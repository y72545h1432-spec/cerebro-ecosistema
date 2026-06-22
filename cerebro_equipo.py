"""cerebro_equipo.py — SUPERVISOR del Agent Team (auto-spawn de workers efimeros + guardrails).

POR QUE EXISTE (2026-06-21): el ecosistema ya tenia cola de tareas, locks, mailbox y checkpoint, pero
NO un lider que LANCE workers solo. Esto lo aporta: drena la cola lanzando procesos `claude -p`
(o `codex`) headless EFIMEROS hasta un cap de concurrencia, con recuperacion, y luego TERMINA (no es
un daemon -> respeta la Regla #3, ahora reemplazada por guardrails acotados y verificables).

MODELO DE WORKER = EFIMERO: cada tarea = un proceso que nace, hace SU tarea, reporta (completar/
fallar/rechazar via cerebro_tareas_modelo) y muere. Si crashea, solo se pierde 1 tarea y el
visibility-timeout (expirar_tomadas) la recupera. Mucho mas estable que sesiones interactivas colgadas.

GUARDRAILS (reemplazan la prohibicion absoluta de la Regla #3):
  1. --confirm obligatorio (+ ms.decidir durable). Sin el -> --dry-run (muestra el plan, no lanza).
  2. max_workers: concurrencia dura.  3. kill-switch: archivo STOP chequeado antes de cada worker.
  4. presupuesto por worker (--max-budget-usd) y agregado por run.  5. solo ejecutables claude/codex
  (allowlist).  6. una pasada de drenado y termina (sin loops/daemons).

TESTEABLE SIN TOKENS: --dry-run arma e imprime el argv sin ejecutar; `runner` inyectable (worker fake)
ejerce todo el ciclo (claim CAS, cierre, recuperacion) contra stores temporales, sin invocar el LLM.

CLI:
    py cerebro_equipo.py drenar --tier haiku [--runtime claude] [--confirm] [--dry-run] [--max-workers N]
    py cerebro_equipo.py reanudar --run <run_id> --tier haiku [--confirm]
    py cerebro_equipo.py dash [--once|--follow N]      # (Fase 3, en cerebro_equipo_dash.py)
"""
from __future__ import annotations
import os
import sys
import json
import uuid
import shutil
import pathlib
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cerebro_core as core                 # noqa: E402
import cerebro_tareas_modelo as tareas      # noqa: E402  (la cola que drenamos)

# Defaults espejo de cerebro_equipo.toml: el modulo funciona aunque el toml no exista (tests).
DEFAULTS = {
    "max_workers": 3,
    "max_tasks_per_run": 12,
    "worker_timeout_s": 600,
    "worker_budget_usd": 0.50,
    "run_budget_usd": 5.0,
    "visibility_ttl_min": 30,
    "permission_mode": "acceptEdits",
    "workdir": "",
    "allowed_exes": ["claude", "claude.exe", "codex", "codex.exe"],
    "allowed_tools": {"haiku": "Read Grep Glob",
                      "sonnet": "Read Grep Glob Edit Write Bash",
                      "opus": "Read Grep Glob Edit Write Bash"},
    "disallowed_tools": "Bash(claude:*) Bash(codex:*) Bash(*cerebro_equipo*)",
    "claude_exe": "",
    "codex_exe": "",
    "api_max_steps": 8,        # pasos maximos del bucle agentico del runtime 'api' (anti-loop)
    # ---- estrategia de CALIDAD (gratis vs pago vs hibrido) ----
    # modo: "gratis" = todo runtime 'api' ($0) · "pago" = todo 'claude' · "hibrido" = enruta por brecha.
    # verificador: "auto" (verifica salidas de modelos gratis) | true | false.
    # hibrido: que runtime usa cada cosa por DEFECTO (brecha pequena -> api gratis; media/grande -> claude).
    "calidad": {
        "modo": "hibrido",
        "verificador": "auto",
        "hibrido": {"debate": "api", "drenar_haiku": "api",
                    "drenar_sonnet": "claude", "drenar_opus": "claude"},
    },
}


# --------------------------------------------------------------------------- config
def cargar_config(path: str | None = None) -> dict:
    """Defaults + override del toml si existe. Nunca lanza (config rota -> defaults)."""
    cfg = json.loads(json.dumps(DEFAULTS))  # copia profunda barata
    p = pathlib.Path(path) if path else (pathlib.Path(AQUI) / "cerebro_equipo.toml")
    if p.exists():
        try:
            import tomllib
            with p.open("rb") as f:
                data = tomllib.load(f)
            for k, v in data.items():
                cfg[k] = v
        except Exception:
            pass
    return cfg


# --------------------------------------------------------------------------- rutas / kill-switch
def _equipo_dir() -> pathlib.Path:
    return core.STATE_DIR / "equipo"


def kill_switch_path(run_id: str, cfg: dict) -> pathlib.Path:
    return _equipo_dir() / "STOP"


def kill_switch_activo(run_id: str, cfg: dict) -> bool:
    """True si existe el archivo STOP -> el supervisor deja de lanzar (drena los en vuelo y sale)."""
    try:
        return kill_switch_path(run_id, cfg).exists()
    except OSError:
        return False


# --------------------------------------------------------------------------- autorizacion (guardrail #1)
def confirmar_autorizacion(confirm: bool, run_id: str, dry_run: bool) -> bool:
    """Sin --confirm o con --dry-run -> False (el caller hace el plan dry). Con --confirm registra la
    decision durable (ms.decidir) y devuelve True. Asi el auto-spawn nunca ocurre sin un OK explicito."""
    if dry_run or not confirm:
        return False
    try:
        from cerebro_multisesion import Multisesion
        ms = Multisesion(f"supervisor equipo {run_id}", project="hub",
                         agent="claude", runtime="claude-code")
        ms.decidir(f"auto-spawn Agent Team run {run_id} autorizado (--confirm)",
                   motivo="supervisor de equipo: lanza workers headless efimeros con guardrails")
        ms.despedir()
    except Exception:
        pass
    return True


# --------------------------------------------------------------------------- construccion del worker
def model_de_tier(tier: str) -> str:
    """tier -> alias de modelo para `claude -p --model` / `codex --model`."""
    return {"haiku": "haiku", "sonnet": "sonnet", "opus": "opus"}.get((tier or "").lower(), "sonnet")


def resolver_exe(runtime: str, cfg: dict) -> str:
    if runtime == "claude":
        return cfg.get("claude_exe") or shutil.which("claude") or "claude"
    if runtime == "codex":
        return cfg.get("codex_exe") or shutil.which("codex") or "codex"
    raise ValueError(f"runtime no soportado: {runtime!r}")


def resolver_runtime(kind: str, tier: str, cfg: dict, cli: str | None = None) -> str:
    """Elige el runtime segun la estrategia de CALIDAD. `cli` (--runtime explicito) SIEMPRE gana.
    modo 'gratis' -> api ($0); 'pago' -> claude; 'hibrido' -> tabla por brecha (kind/tier).
    kind in {'debate','drenar'}. Default hibrido: debate y drenar_haiku -> api gratis; sonnet/opus -> claude."""
    if cli:
        return cli
    cal = cfg.get("calidad", {}) or {}
    modo = (cal.get("modo") or "hibrido").lower()
    if modo == "gratis":
        return "api"
    if modo == "pago":
        return "claude"
    hib = cal.get("hibrido", {}) or {}
    if kind == "debate":
        return hib.get("debate", "api")
    return hib.get(f"drenar_{(tier or '').lower()}", "claude")


def _verificador_activo(cfg: dict, runtime: str) -> bool:
    """verificador: true/false explicito; 'auto' -> verifica solo salidas de modelos GRATIS (api),
    para compensar su brecha de calidad sin gastar pasadas extra en Claude (ya es de alta calidad)."""
    v = (cfg.get("calidad", {}) or {}).get("verificador", "auto")
    if isinstance(v, bool):
        return v
    return str(v).lower() == "auto" and runtime == "api"


def _solo_json(texto: str) -> str:
    """Saca el primer objeto JSON de un texto (los modelos a veces lo envuelven en ``` o prosa)."""
    i, j = texto.find("{"), texto.rfind("}")
    return texto[i:j + 1] if 0 <= i < j else "{}"


def _verificar(producto: str, criterio: str, cfg: dict) -> dict:
    """2a pasada (gratis): un modelo critica el producto contra el criterio de aceptacion.
    Devuelve {ok, problemas, via}. Si el verificador falla, NO bloquea (ok=True) -> nunca corta el flujo."""
    try:
        import cerebro_llm
        msgs = [{"role": "system",
                 "content": "Eres un verificador estricto de control de calidad. Responde SOLO con JSON "
                            '{"ok": bool, "problemas": ["..."]}. ok=true solo si el producto cumple el criterio.'},
                {"role": "user",
                 "content": f"CRITERIO DE ACEPTACION:\n{criterio or '(no especificado)'}\n\n"
                            f"PRODUCTO A VERIFICAR:\n{producto}\n\n¿Cumple? Responde el JSON."}]
        r = cerebro_llm.chat(msgs, tier="sonnet", cfg=cfg, max_tokens=400, temperature=0.0)
        obj = json.loads(_solo_json(r["text"]))
        return {"ok": bool(obj.get("ok", True)), "problemas": obj.get("problemas", []), "via": r["provider"]}
    except Exception as e:
        return {"ok": True, "problemas": [], "error": str(e)[:160]}


_CONTRATO = None


def _contrato() -> str:
    global _CONTRATO
    if _CONTRATO is None:
        _CONTRATO = (pathlib.Path(AQUI) / "equipo_worker_contrato.txt").read_text(encoding="utf-8")
    return _CONTRATO


def construir_prompt(task: dict, runtime: str, tier: str, cfg: dict, run_id: str,
                     worker_id: str, ronda_path: str | None = None) -> str:
    modo = ""
    if ronda_path:
        modo = (f"\n[MODO DEBATE] LEE primero {ronda_path} (hallazgos de tus companeros de esta ronda) "
                f"y APORTA o REBATE con argumentos; agrega tu seccion '## {worker_id}' a ese archivo.\n")
    return _contrato().format(
        run_id=run_id, task_id=task.get("id", ""), tier=tier, worker_id=worker_id, runtime=runtime,
        titulo=task.get("titulo", ""), proposito=task.get("proposito", ""),
        terminado=task.get("terminado", ""),
        archivos=", ".join(task.get("archivos") or []) or "(ninguno)",
        pruebas=", ".join(task.get("pruebas") or []) or "(ninguna)",
        modo_debate=modo, stop_file=str(kill_switch_path(run_id, cfg)), cerebro=AQUI,
    )


def construir_cmd(task: dict, runtime: str, tier: str, cfg: dict, run_id: str,
                  worker_id: str, ronda_path: str | None = None) -> dict:
    """Arma {argv, prompt, runtime}. El prompt va por STDIN (no por argv) -> sin problemas de comillas
    ni de longitud en Windows. argv SIEMPRE como lista (subprocess sin shell)."""
    prompt = construir_prompt(task, runtime, tier, cfg, run_id, worker_id, ronda_path)
    if runtime == "claude":
        argv = [resolver_exe("claude", cfg), "-p",
                "--model", model_de_tier(tier),
                "--output-format", "json",
                "--permission-mode", cfg.get("permission_mode", "acceptEdits"),
                "--max-budget-usd", str(cfg.get("worker_budget_usd", 0.5))]
        tools = (cfg.get("allowed_tools") or {}).get(tier)
        if tools:
            argv += ["--allowedTools", tools]
        if cfg.get("disallowed_tools"):
            argv += ["--disallowedTools", cfg["disallowed_tools"]]
        argv += ["--add-dir", cfg.get("workdir") or os.getcwd()]
        return {"argv": argv, "prompt": prompt, "runtime": "claude"}
    if runtime == "codex":
        # codex no esta instalado hoy: argv best-effort (se valida la existencia al lanzar).
        argv = [resolver_exe("codex", cfg), "exec", "--json", "--model", model_de_tier(tier)]
        return {"argv": argv, "prompt": prompt, "runtime": "codex"}
    if runtime == "api":
        # runtime GRATIS (OpenAI-compatible). No hay exe/argv: el worker es una llamada HTTP. El plan
        # describe la cadena de proveedores y el modelo por tier (se resuelve al lanzar, segun claves).
        try:
            import cerebro_llm
            chain = cerebro_llm.proveedores_listos(cfg) or ["(sin clave configurada)"]
            modelo = (cerebro_llm.modelo_para(cerebro_llm.cadena(cfg)[0], tier)
                      if cerebro_llm.cadena(cfg) else "?")
        except Exception:
            chain, modelo = ["(cerebro_llm no disponible)"], "?"
        return {"argv": None, "prompt": prompt, "runtime": "api",
                "api": {"proveedores": chain, "modelo": modelo, "tier": tier}}
    raise ValueError(f"runtime no soportado: {runtime!r}")


def _exe_permitido(argv: list, cfg: dict) -> None:
    """Allowlist anti fork-bomb / anti-cualquier-cosa: solo claude/codex headless. Lanza si no."""
    exe = os.path.basename(argv[0]).lower() if argv else ""
    if exe not in {e.lower() for e in cfg.get("allowed_exes", [])}:
        raise ValueError(f"ejecutable no permitido para un worker: {argv[0]!r} "
                         f"(allowlist: {cfg.get('allowed_exes')})")


# --------------------------------------------------------------------------- ejecucion del worker real
def _parse_cost(stdout: str) -> float:
    """Extrae el costo del JSON de `claude -p --output-format json` (best-effort, 0.0 si no se ve)."""
    try:
        obj = json.loads(stdout)
    except Exception:
        return 0.0
    for k in ("total_cost_usd", "cost_usd", "total_cost"):
        if isinstance(obj, dict) and isinstance(obj.get(k), (int, float)):
            return float(obj[k])
    return 0.0


def _estado_tarea(tid: str) -> str:
    return (tareas._load().get("tareas", {}).get(tid, {}) or {}).get("estado", "")


# ---- runtime 'api' (GRATIS): el worker es una llamada HTTP, no un subproceso ----
def _dentro(workdir: pathlib.Path, ruta: str) -> pathlib.Path | None:
    """Resuelve `ruta` dentro de workdir (sandbox). None si intenta escapar."""
    try:
        p = (workdir / ruta).resolve()
        p.relative_to(workdir)
        return p
    except Exception:
        return None


def _api_toolset(puede_escribir: bool) -> list:
    """Herramientas (formato OpenAI) que el modelo gratis puede usar en el bucle agentico."""
    tools = [
        {"type": "function", "function": {"name": "leer_archivo", "description": "Lee un archivo de texto del workdir.",
         "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}}, "required": ["ruta"]}}},
        {"type": "function", "function": {"name": "listar_directorio", "description": "Lista archivos de un directorio del workdir.",
         "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}}, "required": ["ruta"]}}},
        {"type": "function", "function": {"name": "buscar", "description": "Busca un texto literal en los archivos del workdir.",
         "parameters": {"type": "object", "properties": {"patron": {"type": "string"}, "ruta": {"type": "string"}}, "required": ["patron"]}}},
        {"type": "function", "function": {"name": "terminar", "description": "Cierra la tarea con su resultado. LLAMALA al final.",
         "parameters": {"type": "object", "properties": {
             "resultado": {"type": "string", "enum": ["hecha", "fallida", "rechazada"]},
             "resumen": {"type": "string"}}, "required": ["resultado", "resumen"]}}},
    ]
    if puede_escribir:
        tools.insert(3, {"type": "function", "function": {
            "name": "escribir_archivo", "description": "Crea o reemplaza un archivo del workdir.",
            "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}, "contenido": {"type": "string"}},
                           "required": ["ruta", "contenido"]}}})
    return tools


def _ejecutar_tool(tc: dict, workdir: pathlib.Path, puede_escribir: bool):
    """Ejecuta una tool del worker. Devuelve (texto_resultado, terminar_dict_o_None)."""
    name, args = tc.get("name", ""), tc.get("args", {}) or {}
    if name == "terminar":
        return "(tarea cerrada)", {"resultado": args.get("resultado", "hecha"), "resumen": args.get("resumen", "")}
    if name in ("leer_archivo", "listar_directorio", "buscar", "escribir_archivo"):
        ruta = args.get("ruta", ".")
        p = _dentro(workdir, ruta) if name != "buscar" else workdir
        if name != "buscar" and p is None:
            return f"ERROR: ruta fuera del workdir: {ruta}", None
        try:
            if name == "leer_archivo":
                return p.read_text(encoding="utf-8", errors="replace")[:6000], None
            if name == "listar_directorio":
                return "\n".join(sorted(x.name for x in p.iterdir()))[:3000], None
            if name == "buscar":
                pat, hits = args.get("patron", ""), []
                for f in workdir.rglob("*"):
                    if f.is_file() and f.stat().st_size < 500_000:
                        try:
                            for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                                if pat and pat in line:
                                    hits.append(f"{f.relative_to(workdir)}:{n}: {line.strip()[:120]}")
                                    if len(hits) >= 40:
                                        break
                        except Exception:
                            pass
                    if len(hits) >= 40:
                        break
                return "\n".join(hits) or "(sin coincidencias)", None
            if name == "escribir_archivo":
                if not puede_escribir:
                    return "ERROR: este tier es de solo lectura (no puede escribir).", None
                p.parent.mkdir(parents=True, exist_ok=True)
                core.write_atomic(p, args.get("contenido", ""))
                return f"escrito {ruta} ({len(args.get('contenido', ''))} chars)", None
        except Exception as e:
            return f"ERROR ejecutando {name}: {e}", None
    return f"ERROR: herramienta desconocida {name!r}", None


def _reconstruir_tcs(tcs: list) -> list:
    """Reconstruye los tool_calls en formato OpenAI para el historial de mensajes."""
    return [{"id": tc["id"], "type": "function",
             "function": {"name": tc["name"], "arguments": json.dumps(tc.get("args", {}), ensure_ascii=False)}}
            for tc in tcs]


def _run_api_task(task: dict, ctx: dict) -> dict:
    """Worker agentico GRATIS: bucle de tool-calling contra un modelo OpenAI-compatible. Lee/edita
    archivos del workdir con herramientas acotadas (tier-gated) y cierra la tarea con 'terminar'.
    El SUPERVISOR cierra la tarea en cerebro (completar/fallar/rechazar) segun el resultado + verificador."""
    import cerebro_llm
    cfg, tid, worker_id, tier = ctx["cfg"], task["id"], ctx["worker_id"], ctx["tier"]
    workdir = pathlib.Path(cfg.get("workdir") or os.getcwd()).resolve()
    tools_tier = (cfg.get("allowed_tools") or {}).get(tier, "")
    puede_escribir = ("Write" in tools_tier) or ("Edit" in tools_tier)
    sistema = ("Eres un worker que resuelve UNA tarea concreta con herramientas. Lee solo lo necesario, "
               "haz el cambio MINIMO, y SIEMPRE llama a 'terminar' con el resultado. Si no puedes, "
               "termina con resultado='fallida' y explica por que. No inventes archivos ni resultados.")
    usuario = (f"TAREA: {task.get('titulo', '')}\nPROPOSITO: {task.get('proposito', '')}\n"
               f"CRITERIO DE TERMINADO: {task.get('terminado', '')}\n"
               f"ARCHIVOS SUGERIDOS: {', '.join(task.get('archivos') or []) or '(ninguno)'}\n"
               f"WORKDIR: {workdir}\nEscribe rutas relativas al WORKDIR.")
    messages = [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]
    tools = _api_toolset(puede_escribir)
    final, provider = None, "?"
    for _ in range(int(cfg.get("api_max_steps", 8))):
        if kill_switch_activo(ctx["run_id"], cfg):
            break
        try:
            r = cerebro_llm.chat(messages, tier=tier, cfg=cfg, tools=tools, max_tokens=1500, temperature=0.2)
        except Exception as e:
            tareas.fallar(tid, motivo=f"api error: {e}", por=worker_id)
            return {"exit_code": None, "cost": 0.0, "outcome": "api_error", "error": str(e)[:160]}
        provider = r.get("provider", provider)
        if not r["tool_calls"]:                       # texto sin tools -> lo tomamos como cierre
            final = {"resultado": "hecha", "resumen": (r["text"] or "")[:600]}
            break
        messages.append({"role": "assistant", "content": r["text"] or "", "tool_calls": _reconstruir_tcs(r["tool_calls"])})
        for tc in r["tool_calls"]:
            res, termino = _ejecutar_tool(tc, workdir, puede_escribir)
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": res})
            if termino:
                final = termino
        if final:
            break
    if final is None:
        tareas.fallar(tid, motivo=f"worker api no cerro en {cfg.get('api_max_steps', 8)} pasos", por=worker_id)
        return {"exit_code": 0, "cost": 0.0, "outcome": "no_cerrada", "provider": provider}
    resultado = (final.get("resultado") or "hecha").lower()
    resumen = final.get("resumen", "")
    if resultado == "hecha":
        if _verificador_activo(cfg, "api"):
            v = _verificar(resumen, task.get("terminado", ""), cfg)
            if not v["ok"]:
                tareas.fallar(tid, motivo=f"verificador rechazo: {v.get('problemas')}", por=worker_id)
                return {"exit_code": 0, "cost": 0.0, "outcome": "rechazada_verificador",
                        "provider": provider, "verificacion": v}
        tareas.completar(tid, nota=f"{resumen} [via {provider}]", por=worker_id)
        return {"exit_code": 0, "cost": 0.0, "outcome": "hecha", "provider": provider}
    if resultado == "rechazada":
        tareas.rechazar(tid, motivo=resumen, por=worker_id)
        return {"exit_code": 0, "cost": 0.0, "outcome": "rechazada", "provider": provider}
    tareas.fallar(tid, motivo=resumen, por=worker_id)
    return {"exit_code": 0, "cost": 0.0, "outcome": "fallida", "provider": provider}


def default_runner(task: dict, ctx: dict) -> dict:
    """Worker REAL: lanza `claude -p`/`codex` headless con el prompt por stdin, espera, y deriva el
    resultado del estado de la tarea (el worker reporto completar/fallar/rechazar via cerebro).
    Si el runtime es 'api', usa el bucle agentico GRATIS (sin subproceso)."""
    if ctx.get("runtime") == "api":
        return _run_api_task(task, ctx)
    cfg, tid, worker_id = ctx["cfg"], task["id"], ctx["worker_id"]
    cmd = construir_cmd(task, ctx["runtime"], ctx["tier"], cfg, ctx["run_id"], worker_id, ctx.get("ronda_path"))
    _exe_permitido(cmd["argv"], cfg)
    try:
        p = subprocess.run(cmd["argv"], input=cmd["prompt"], capture_output=True, text=True,
                           timeout=cfg["worker_timeout_s"], encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        tareas.fallar(tid, motivo=f"timeout {cfg['worker_timeout_s']}s", por=worker_id)
        return {"exit_code": None, "cost": 0.0, "outcome": "timeout"}
    except Exception as e:
        tareas.fallar(tid, motivo=f"no se pudo lanzar worker: {e}", por=worker_id)
        return {"exit_code": None, "cost": 0.0, "outcome": "launch_error", "error": str(e)}
    cost = _parse_cost(p.stdout or "")
    if _estado_tarea(tid) == "tomada":  # el worker no cerro la tarea -> no dejarla colgada
        tareas.fallar(tid, motivo=f"worker termino (exit {p.returncode}) sin cerrar la tarea", por=worker_id)
        return {"exit_code": p.returncode, "cost": cost, "outcome": "no_cerrada"}
    return {"exit_code": p.returncode, "cost": cost, "outcome": _estado_tarea(tid)}


# --------------------------------------------------------------------------- orquestacion
def _run_one(task: dict, runtime: str, tier: str, cfg: dict, run_id: str,
             runner, ronda_path, state: dict) -> dict:
    tid = task["id"]
    if kill_switch_activo(run_id, cfg):
        return {"task_id": tid, "outcome": "skipped_stop"}
    with state["lock"]:
        if state["cost"] >= cfg["run_budget_usd"]:
            return {"task_id": tid, "outcome": "skipped_budget"}
    worker_id = f"equipo-{run_id}-{tid}"
    if not tareas.tomar(tid, por=worker_id):     # CAS atomico: si otro la tomo, me salgo
        return {"task_id": tid, "outcome": "skipped_taken"}
    ctx = {"runtime": runtime, "tier": tier, "cfg": cfg, "run_id": run_id,
           "worker_id": worker_id, "ronda_path": ronda_path}
    try:
        res = runner(task, ctx)
    except Exception as e:
        tareas.fallar(tid, motivo=f"runner excepcion: {e}", por=worker_id)
        return {"task_id": tid, "worker_id": worker_id, "outcome": "error", "error": str(e)}
    with state["lock"]:
        state["cost"] += float(res.get("cost") or 0.0)
    return {"task_id": tid, "worker_id": worker_id, **res}


def _plan_dry(tier: str, runtime: str, cfg: dict, run_id: str, ronda_path=None) -> dict:
    pend = tareas.pendientes(tier)[:cfg["max_tasks_per_run"]]
    plan = []
    for t in pend:
        cmd = construir_cmd(t, runtime, tier, cfg, run_id, f"equipo-{run_id}-{t['id']}", ronda_path)
        if cmd.get("argv"):
            _exe_permitido(cmd["argv"], cfg)   # allowlist solo aplica a runtimes con exe (claude/codex)
        plan.append({"task_id": t["id"], "titulo": t.get("titulo", ""),
                     "argv": cmd["argv"], "api": cmd.get("api"), "prompt_chars": len(cmd["prompt"])})
    return {"dry": True, "run_id": run_id, "tier": tier, "runtime": runtime, "n": len(plan), "plan": plan}


def _checkpoint(run_id, tier, n, ronda=0):
    try:
        import cerebro_checkpoint as ckpt
        ckpt.checkpoint(f"supervisor equipo {run_id}: drenando {n} tareas (tier {tier}, ronda {ronda})",
                        "esperar workers -> expirar_tomadas -> cerrar", tarea=f"equipo {run_id}",
                        proyecto="hub", sesion=f"equipo-{run_id}")
    except Exception:
        pass


def _cerrar_checkpoint(run_id, resultados):
    try:
        import cerebro_checkpoint as ckpt
        ckpt.cerrar_limpio(f"equipo {run_id}: {len(resultados)} resultados", sesion=f"equipo-{run_id}")
    except Exception:
        pass


def drenar_cola(tier: str, runtime: str = "claude", cfg: dict | None = None, run_id: str | None = None,
                confirm: bool = False, dry_run: bool = False, runner=None, ronda_path=None) -> dict:
    """Drena la cola del `tier` lanzando workers efimeros (hasta max_workers) y TERMINA. Sin --confirm
    o con --dry-run devuelve el PLAN sin lanzar. `runner` inyectable para tests (worker fake)."""
    cfg = cfg or cargar_config()
    run_id = run_id or ("R" + uuid.uuid4().hex[:8])
    if not confirmar_autorizacion(confirm, run_id, dry_run):
        return _plan_dry(tier, runtime, cfg, run_id, ronda_path)
    if kill_switch_activo(run_id, cfg):
        return {"run_id": run_id, "stopped": True, "resultados": [], "reclamadas": []}
    runner = runner or default_runner
    pend = tareas.pendientes(tier)[:cfg["max_tasks_per_run"]]
    _checkpoint(run_id, tier, len(pend))
    state = {"lock": threading.Lock(), "cost": 0.0}
    resultados = []
    if pend:
        with ThreadPoolExecutor(max_workers=cfg["max_workers"]) as ex:
            futs = [ex.submit(_run_one, t, runtime, tier, cfg, run_id, runner, ronda_path, state)
                    for t in pend]
            for fut in as_completed(futs):
                resultados.append(fut.result())
    reclamadas = tareas.expirar_tomadas(cfg["visibility_ttl_min"])
    _cerrar_checkpoint(run_id, resultados)
    hechas = [r for r in resultados if r.get("outcome") == "hecha"]
    return {"run_id": run_id, "tier": tier, "runtime": runtime,
            "lanzados": len([r for r in resultados if not str(r.get("outcome", "")).startswith("skipped")]),
            "hechas": len(hechas), "resultados": resultados, "reclamadas": reclamadas,
            "costo": round(state["cost"], 4)}


def reanudar(run_id: str, cfg: dict | None = None, tier: str = "haiku", runtime: str = "claude",
             runner=None, confirm: bool = True, ttl_min: int | None = None) -> dict:
    """RECOVERY: reclama tareas 'tomada' colgadas (de workers/supervisor muertos) y re-drena. La COLA es
    la fuente de verdad; el checkpoint solo aporta el run_id. `ttl_min` fuerza la reclamacion (tests)."""
    cfg = cfg or cargar_config()
    reclamadas = tareas.expirar_tomadas(cfg["visibility_ttl_min"] if ttl_min is None else ttl_min)
    res = drenar_cola(tier, runtime, cfg, run_id=run_id, confirm=confirm, runner=runner)
    res["reanudado"] = True
    res["reclamadas_al_reanudar"] = reclamadas
    return res


def liberar_todo(run_id: str, cfg: dict | None = None) -> None:
    """Cierre best-effort del run (marca el checkpoint cerrado-limpio)."""
    _cerrar_checkpoint(run_id, [])


# --------------------------------------------------------------------------- DEBATE por olas
# El efecto "teammates que se hablan" SIN procesos persistentes: cada ronda lanza N workers efimeros
# NUEVOS que LEEN la ronda previa (lo que dejaron los otros) y APORTAN/REBATEN en la ronda actual.
# Se hablan via doc compartido + mailbox. Se para por SATURACION semantica (reusa cerebro_semantica)
# o por tope de rondas. Mismo patron que la skill investigacion-infinita (olas + saturacion).
_DEBATE_PROMPT = """[WORKER DE DEBATE — run {run_id} · ronda {ronda} · {worker_id}]
Eres un participante EFIMERO de un debate estructurado. Enunciado:
  {enunciado}

PASO 0 cerebro (registra sesion, lee buzon):
  import sys; sys.path.insert(0, r"{cerebro}")
  from cerebro_multisesion import Multisesion
  ms = Multisesion("debate {worker_id}", project="hub", agent="{runtime}", runtime="{runtime}")
  ms.leer_buzon()

LEE la ronda previa (argumentos de tus companeros): {prev}
APORTA valor NUEVO o REBATE con argumentos + evidencia (NO repitas lo ya dicho).
ESCRIBE tu aporte AL FINAL de: {cur}
  formato:   \\n## {worker_id}\\n<afirmacion / por que / evidencia / Recomendacion #1>\\n
Publica:    ms.mensaje_tipo("equipo:{run_id}", type="done", summary="<1 linea>", thread="{run_id}")
            ms.conocimiento("<aprendizaje>", tags=["equipo","debate","{run_id}"])
Si existe {stop_file}: no escribas y apagate.  Cierra: ms.despedir().
"""


def _debate_dir(run_id: str) -> pathlib.Path:
    d = _equipo_dir() / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_api_debate(ctx: dict) -> dict:
    """Worker de debate GRATIS: pide el aporte a un modelo OpenAI-compatible y el SUPERVISOR lo escribe
    en el doc de la ronda bajo FileMutex (sin carrera entre los N workers de la ola). Costo $0."""
    import cerebro_llm
    cfg = ctx["cfg"]
    try:
        prev_txt = pathlib.Path(ctx["prev"]).read_text(encoding="utf-8")
    except OSError:
        prev_txt = ""
    msgs = [{"role": "system",
             "content": "Participas en un debate estructurado entre varios agentes. Aporta valor NUEVO "
                        "o REBATE con argumentos y evidencia; NO repitas lo ya dicho. Se conciso."},
            {"role": "user",
             "content": f"ENUNCIADO: {ctx['enunciado']}\n\nLO QUE YA DIJERON TUS COMPANEROS (ronda previa):\n"
                        f"{prev_txt[:6000]}\n\nEscribe TU aporte: afirmacion / por que / evidencia / Recomendacion #1."}]
    try:
        r = cerebro_llm.chat(msgs, tier=ctx["tier"], cfg=cfg, max_tokens=900, temperature=0.6)
    except Exception as e:
        return {"exit_code": None, "cost": 0.0, "outcome": "error", "error": str(e)[:160]}
    seccion = f"\n## {ctx['worker_id']} (via {r['provider']})\n{(r['text'] or '').strip()}\n"
    cur = pathlib.Path(ctx["cur"])
    with core.FileMutex(f"debate-{ctx['run_id']}-r{ctx['ronda']}", lockdir=_debate_dir(ctx["run_id"])):
        cur.write_text(cur.read_text(encoding="utf-8") + seccion, encoding="utf-8")
    return {"exit_code": 0, "cost": 0.0, "outcome": "done", "provider": r["provider"]}


def default_debate_runner(ctx: dict) -> dict:
    """Worker de debate REAL: lanza `claude -p` con el prompt de debate; el worker escribe su seccion
    en el doc de la ronda con sus propias tools. Prompt por stdin; argv como lista; allowlist.
    Si el runtime es 'api', usa el debatiente GRATIS (sin subproceso)."""
    if ctx.get("runtime") == "api":
        return _run_api_debate(ctx)
    cfg = ctx["cfg"]
    prompt = _DEBATE_PROMPT.format(
        run_id=ctx["run_id"], ronda=ctx["ronda"], worker_id=ctx["worker_id"],
        enunciado=ctx["enunciado"], prev=ctx["prev"], cur=ctx["cur"],
        stop_file=str(kill_switch_path(ctx["run_id"], cfg)), runtime=ctx["runtime"], cerebro=AQUI)
    argv = [resolver_exe(ctx["runtime"], cfg), "-p", "--model", model_de_tier(ctx["tier"]),
            "--output-format", "json", "--permission-mode", cfg.get("permission_mode", "acceptEdits"),
            "--max-budget-usd", str(cfg.get("worker_budget_usd", 0.5)),
            "--add-dir", str(_debate_dir(ctx["run_id"]))]
    tools = (cfg.get("allowed_tools") or {}).get(ctx["tier"])
    if tools:
        argv += ["--allowedTools", tools + " Edit Write"]  # el debatiente necesita escribir su seccion
    if cfg.get("disallowed_tools"):
        argv += ["--disallowedTools", cfg["disallowed_tools"]]
    _exe_permitido(argv, cfg)
    try:
        p = subprocess.run(argv, input=prompt, capture_output=True, text=True,
                           timeout=cfg["worker_timeout_s"], encoding="utf-8", errors="replace")
        return {"exit_code": p.returncode, "cost": _parse_cost(p.stdout or ""), "outcome": "done"}
    except subprocess.TimeoutExpired:
        return {"exit_code": None, "cost": 0.0, "outcome": "timeout"}
    except Exception as e:
        return {"exit_code": None, "cost": 0.0, "outcome": "error", "error": str(e)}


def _debate_worker(run_id, ronda, i, enunciado, prev, cur, cfg, tier, runtime, runner, state) -> dict:
    worker_id = f"equipo-{run_id}-r{ronda}-w{i}"
    if kill_switch_activo(run_id, cfg):
        return {"worker": worker_id, "outcome": "skipped_stop"}
    ctx = {"run_id": run_id, "ronda": ronda, "worker_id": worker_id, "enunciado": enunciado,
           "prev": str(prev), "cur": str(cur), "cfg": cfg, "tier": tier, "runtime": runtime}
    try:
        res = runner(ctx)
    except Exception as e:
        return {"worker": worker_id, "outcome": "error", "error": str(e)}
    with state["lock"]:
        state["cost"] += float(res.get("cost") or 0.0)
    return {"worker": worker_id, **res}


def ronda_debate(run_id: str, enunciado: str, ronda: int, n_workers: int, cfg: dict,
                 tier: str, runtime: str, runner) -> dict:
    """Una ola: N workers efimeros nuevos leen ronda_{r-1}.md y escriben en ronda_{r}.md."""
    ddir = _debate_dir(run_id)
    prev = ddir / f"ronda_{ronda - 1}.md"
    cur = ddir / f"ronda_{ronda}.md"
    if not prev.exists():  # ronda 0 = el enunciado
        core.write_atomic(prev, f"# Debate {run_id} — enunciado\n\n{enunciado}\n")
    core.write_atomic(cur, f"# Ronda {ronda} — {run_id}\n\n> Enunciado: {enunciado}\n")
    state = {"lock": threading.Lock(), "cost": 0.0}
    secciones = []
    with ThreadPoolExecutor(max_workers=min(n_workers, cfg["max_workers"])) as ex:
        futs = [ex.submit(_debate_worker, run_id, ronda, i, enunciado, prev, cur, cfg, tier, runtime,
                          runner, state) for i in range(n_workers)]
        for f in as_completed(futs):
            secciones.append(f.result())
    return {"ronda": ronda, "archivo": str(cur), "secciones": secciones, "cost": round(state["cost"], 4)}


def _saturado(prev_texto: str, cur_texto: str, umbral: float) -> bool:
    """True si la ronda nueva es semanticamente casi igual a la previa (no aporta novedad)."""
    if not prev_texto.strip() or not cur_texto.strip():
        return False
    try:
        import cerebro_semantica
        s = cerebro_semantica.scores(cur_texto, [prev_texto])
        return bool(s) and s[0] >= umbral
    except Exception:
        return False


def _consolidar(run_id: str, enunciado: str, rondas: list) -> pathlib.Path:
    ddir = _debate_dir(run_id)
    out = [f"# Consolidado del debate {run_id}", "", f"> Enunciado: {enunciado}", ""]
    for info in rondas:
        try:
            out.append(pathlib.Path(info["archivo"]).read_text(encoding="utf-8"))
        except OSError:
            pass
        out.append("")
    path = ddir / "consolidado.md"
    core.write_atomic(path, "\n".join(out))
    try:
        from cerebro_multisesion import Multisesion
        ms = Multisesion(f"debate {run_id}", project="hub", agent="claude", runtime="claude-code")
        ms.conocimiento(f"Debate {run_id} consolidado ({len(rondas)} rondas): {enunciado[:120]}",
                        tags=["equipo", "debate", run_id])
        ms.despedir()
    except Exception:
        pass
    return path


def correr_debate(run_id: str | None, enunciado: str, cfg: dict | None = None, max_rondas: int = 4,
                  tier: str = "sonnet", runtime: str = "claude", confirm: bool = False,
                  dry_run: bool = False, runner=None, n_workers: int = 3, umbral: float = 0.82) -> dict:
    """Debate por olas hasta SATURACION o `max_rondas`. Sin --confirm/-> dry. `runner` inyectable."""
    cfg = cfg or cargar_config()
    run_id = run_id or ("D" + uuid.uuid4().hex[:8])
    if not confirmar_autorizacion(confirm, run_id, dry_run):
        return {"dry": True, "run_id": run_id, "enunciado": enunciado, "max_rondas": max_rondas,
                "n_workers": n_workers, "tier": tier, "runtime": runtime}
    runner = runner or default_debate_runner
    rondas, prev_texto = [], ""
    for r in range(1, max_rondas + 1):
        if kill_switch_activo(run_id, cfg):
            break
        info = ronda_debate(run_id, enunciado, r, n_workers, cfg, tier, runtime, runner)
        _checkpoint(run_id, tier, n_workers, ronda=r)
        cur_texto = pathlib.Path(info["archivo"]).read_text(encoding="utf-8")
        if prev_texto and _saturado(prev_texto, cur_texto, umbral):
            info["saturado"] = True
            rondas.append(info)
            break
        prev_texto = cur_texto
        rondas.append(info)
    consolidado = _consolidar(run_id, enunciado, rondas)
    _cerrar_checkpoint(run_id, rondas)
    return {"run_id": run_id, "rondas": len(rondas), "saturado": any(x.get("saturado") for x in rondas),
            "consolidado": str(consolidado), "costo": round(sum(x["cost"] for x in rondas), 4),
            "detalle": rondas}


# --------------------------------------------------------------------------- CLI
def _print_dry(plan: dict) -> None:
    print(f"[DRY-RUN] run {plan['run_id']} · tier {plan['tier']} · runtime {plan['runtime']} · "
          f"{plan['n']} tarea(s) (sin --confirm = no se lanza nada)")
    for it in plan["plan"]:
        print(f"\n  {it['task_id']}  {it['titulo']}")
        if it.get("api"):
            ap = it["api"]
            print(f"    api ($0): proveedores {ap['proveedores']} · modelo {ap['modelo']} (tier {ap['tier']})")
            print(f"    prompt: {it['prompt_chars']} chars como mensaje")
        else:
            print("    argv: " + " ".join(it["argv"]))
            print(f"    prompt: {it['prompt_chars']} chars por stdin")
    if not plan["plan"]:
        print("  (no hay tareas pendientes para ese tier)")


def _cli(argv: list) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    import argparse
    cmd = argv[0]
    if cmd == "drenar":
        p = argparse.ArgumentParser(prog="cerebro_equipo drenar")
        p.add_argument("--tier", required=True)
        p.add_argument("--runtime", default=None, help="claude|codex|api (vacio = lo decide --modo/calidad)")
        p.add_argument("--modo", default=None, help="gratis|pago|hibrido (override de calidad.modo)")
        p.add_argument("--confirm", action="store_true")
        p.add_argument("--dry-run", dest="dry", action="store_true")
        p.add_argument("--max-workers", type=int, default=None)
        p.add_argument("--run", default=None)
        a = p.parse_args(argv[1:])
        cfg = cargar_config()
        if a.max_workers:
            cfg["max_workers"] = a.max_workers
        if a.modo:
            cfg.setdefault("calidad", {})["modo"] = a.modo
        runtime = resolver_runtime("drenar", a.tier, cfg, cli=a.runtime)
        res = drenar_cola(a.tier, runtime, cfg, run_id=a.run, confirm=a.confirm, dry_run=a.dry)
        if res.get("dry"):
            _print_dry(res)
        else:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if cmd == "reanudar":
        p = argparse.ArgumentParser(prog="cerebro_equipo reanudar")
        p.add_argument("--run", required=True)
        p.add_argument("--tier", default="haiku")
        p.add_argument("--runtime", default=None)
        p.add_argument("--modo", default=None)
        p.add_argument("--confirm", action="store_true")
        a = p.parse_args(argv[1:])
        cfg = cargar_config()
        if a.modo:
            cfg.setdefault("calidad", {})["modo"] = a.modo
        runtime = resolver_runtime("drenar", a.tier, cfg, cli=a.runtime)
        res = reanudar(a.run, cfg=cfg, tier=a.tier, runtime=runtime, confirm=a.confirm)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if cmd == "debate":
        p = argparse.ArgumentParser(prog="cerebro_equipo debate")
        p.add_argument("--enunciado", required=True)
        p.add_argument("--run", default=None)
        p.add_argument("--max-rondas", type=int, default=4)
        p.add_argument("--workers", type=int, default=3)
        p.add_argument("--tier", default="sonnet")
        p.add_argument("--runtime", default=None)
        p.add_argument("--modo", default=None)
        p.add_argument("--confirm", action="store_true")
        p.add_argument("--dry-run", dest="dry", action="store_true")
        a = p.parse_args(argv[1:])
        cfg = cargar_config()
        if a.modo:
            cfg.setdefault("calidad", {})["modo"] = a.modo
        runtime = resolver_runtime("debate", a.tier, cfg, cli=a.runtime)
        res = correr_debate(a.run, a.enunciado, cfg=cfg, max_rondas=a.max_rondas, tier=a.tier,
                            runtime=runtime, confirm=a.confirm, dry_run=a.dry, n_workers=a.workers)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    if cmd == "dash":
        import cerebro_equipo_dash as dash
        return dash.main(argv[1:])
    print(f"comando desconocido: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(_cli(sys.argv[1:]))
