"""Tests del supervisor del Agent Team (cerebro_equipo). SIN tokens: worker fake + dry-run.
Todo aislado en temporales (cola, STATE_DIR del kill-switch, multisesion y checkpoint).
Correr: py -3 test_cerebro_equipo.py"""
import sys
import time
import tempfile
import traceback
import threading
from pathlib import Path
from datetime import datetime, timedelta

import cerebro_core as core
import cerebro_tareas_modelo as tm
import cerebro_multisesion as cm
import cerebro_checkpoint as ckpt
import cerebro_salud as salud
import cerebro_modelo as modelo
import cerebro_equipo as eq
import cerebro_equipo_dash as dash
import cerebro_llm as llm


def _ok(name):
    print(f"  ok  {name}")


def _fresh():
    """Aisla TODO el estado que el supervisor toca, en un tmp por caso."""
    d = Path(tempfile.mkdtemp(prefix="equipo_"))
    tm.STORE = d / "tareas.json"                 # la cola
    core.STATE_DIR = d                           # kill-switch vive en <STATE_DIR>/equipo/STOP
    cm.ARCHIVO = d / "multisesion.json"          # ms.decidir de confirmar_autorizacion
    cm.EVENT_LOG = d / "eventos.jsonl"
    cm.LOCKDIR = d / "_locks"
    ckpt.REMEMBER = d / "remember.md"            # checkpoints del run
    salud.STATE = d / "multisesion.json"         # dashboard lee salud
    modelo.STORE = d / "modelos_vivos.json"      # dashboard lee tiers vivos
    return d


def _fake_completa(task, ctx):
    """Worker fake: 'hace' la tarea cerrandola como hecha (sin LLM)."""
    tm.completar(task["id"], nota="fake ok", por=ctx["worker_id"])
    return {"exit_code": 0, "cost": 0.01, "outcome": "hecha"}


# ---- 1: dry-run arma el argv correcto y NO lanza ni reclama ----
def test_dry_run_arma_argv():
    _fresh()
    tm.publicar("t1", "p", modelo="haiku", terminado="ok")
    res = eq.drenar_cola("haiku", "claude", dry_run=True)
    assert res["dry"] is True and res["n"] == 1
    argv = res["plan"][0]["argv"]
    assert "-p" in argv and "json" in argv
    assert argv[argv.index("--model") + 1] == "haiku"
    assert "--max-budget-usd" in argv and "--output-format" in argv
    # no toco la cola: la tarea sigue pendiente
    assert tm._load()["tareas"][res["plan"][0]["task_id"]]["estado"] == "pendiente"
    _ok("dry-run: arma argv (-p/--model/--output-format/--max-budget-usd) y NO reclama tareas")


# ---- 2: sin --confirm el drenado real degrada a dry (guardrail #1) ----
def test_sin_confirm_es_dry():
    _fresh()
    tid = tm.publicar("t", "p", modelo="haiku", terminado="ok")
    res = eq.drenar_cola("haiku", "claude", confirm=False)
    assert res.get("dry") is True
    assert tm._load()["tareas"][tid]["estado"] == "pendiente"   # nada lanzado
    _ok("sin --confirm: degrada a dry-run, no lanza (guardrail de autorizacion)")


# ---- 3: con --confirm y worker fake, drena y cierra las tareas ----
def test_drena_con_fake_runner():
    _fresh()
    for i in range(3):
        tm.publicar(f"t{i}", "p", modelo="haiku", terminado="ok")
    res = eq.drenar_cola("haiku", "claude", confirm=True, runner=_fake_completa)
    assert res["hechas"] == 3, res
    assert all(t["estado"] == "hecha" for t in tm._load()["tareas"].values())
    _ok("drenar (fake): reclama y completa todas las pendientes del tier")


# ---- 4: kill-switch (STOP) impide lanzar ----
def test_kill_switch_no_lanza():
    d = _fresh()
    tid = tm.publicar("t", "p", modelo="haiku", terminado="ok")
    stop = d / "equipo" / "STOP"
    stop.parent.mkdir(parents=True, exist_ok=True)
    stop.write_text("stop", encoding="utf-8")
    res = eq.drenar_cola("haiku", "claude", confirm=True, runner=_fake_completa)
    assert res.get("stopped") is True
    assert tm._load()["tareas"][tid]["estado"] == "pendiente"
    _ok("kill-switch: con STOP no lanza nada (drena los en vuelo y sale)")


# ---- 5: max_workers acota la concurrencia ----
def test_max_workers_respeta():
    _fresh()
    for i in range(6):
        tm.publicar(f"t{i}", "p", modelo="haiku", terminado="ok")
    activos = {"now": 0, "peak": 0, "lock": threading.Lock()}

    def runner_lento(task, ctx):
        with activos["lock"]:
            activos["now"] += 1
            activos["peak"] = max(activos["peak"], activos["now"])
        time.sleep(0.05)
        with activos["lock"]:
            activos["now"] -= 1
        tm.completar(task["id"], por=ctx["worker_id"])
        return {"exit_code": 0, "cost": 0.0, "outcome": "hecha"}

    cfg = eq.cargar_config(); cfg["max_workers"] = 2
    eq.drenar_cola("haiku", "claude", cfg=cfg, confirm=True, runner=runner_lento)
    assert activos["peak"] <= 2, activos["peak"]
    _ok("max_workers: la concurrencia nunca supera el cap configurado")


# ---- 6: allowlist rechaza ejecutables que no sean claude/codex ----
def test_allowlist_rechaza_exe():
    cfg = eq.cargar_config()
    try:
        eq._exe_permitido(["python.exe", "-c", "x"], cfg)
        assert False, "deberia rechazar python como worker"
    except ValueError:
        pass
    eq._exe_permitido(["C:\\x\\claude.exe", "-p"], cfg)   # claude SI permitido (no lanza)
    _ok("allowlist: rechaza exe ajeno (anti fork-bomb); acepta claude/codex")


# ---- 7: recuperacion — reanudar reclama 'tomada' colgada y la re-drena ----
def test_reanudar_recupera_colgada():
    _fresh()
    tid = tm.publicar("t", "p", modelo="haiku", terminado="ok")
    tm.tomar(tid, "worker-muerto")               # simula worker que la tomo y murio sin cerrar
    res = eq.reanudar("R-test", tier="haiku", confirm=True, runner=_fake_completa, ttl_min=0)
    assert tid in res["reclamadas_al_reanudar"]
    assert tm._load()["tareas"][tid]["estado"] == "hecha"
    _ok("reanudar: expira la 'tomada' colgada del worker muerto y la completa al re-drenar")


# ---- 8: presupuesto agregado del run detiene nuevos lanzamientos ----
def test_budget_detiene():
    _fresh()
    for i in range(3):
        tm.publicar(f"t{i}", "p", modelo="haiku", terminado="ok")
    cfg = eq.cargar_config(); cfg["max_workers"] = 1; cfg["run_budget_usd"] = 0.005

    def runner_caro(task, ctx):
        tm.completar(task["id"], por=ctx["worker_id"])
        return {"exit_code": 0, "cost": 0.01, "outcome": "hecha"}

    res = eq.drenar_cola("haiku", "claude", cfg=cfg, confirm=True, runner=runner_caro)
    skipped = [r for r in res["resultados"] if r.get("outcome") == "skipped_budget"]
    assert skipped, res["resultados"]
    _ok("budget: tras superar el presupuesto del run, los siguientes workers se saltan")


# ---- 9: model_de_tier mapea los tiers conocidos ----
def test_model_de_tier():
    assert eq.model_de_tier("haiku") == "haiku"
    assert eq.model_de_tier("opus") == "opus"
    assert eq.model_de_tier("desconocido") == "sonnet"
    _ok("model_de_tier: haiku/sonnet/opus; desconocido -> sonnet")


# ---- 10: saturacion semantica detecta rondas que no aportan novedad ----
def test_saturado_detecta_similar():
    a = "la respuesta es 42 por simetria y elegancia matematica en el modelo"
    assert eq._saturado(a, a, 0.6) is True                       # identico -> saturado
    assert eq._saturado(a, "receta de pasta italiana con tomate", 0.6) is False
    _ok("_saturado: identico -> True; tema distinto -> False")


# ---- 11: debate por olas corre, escribe rondas y consolida ----
def _fake_debate(ctx):
    cur = Path(ctx["cur"])
    cur.write_text(cur.read_text(encoding="utf-8") +
                   f"\n## {ctx['worker_id']}\nAporte: la respuesta es 42 por simetria.\n",
                   encoding="utf-8")
    return {"cost": 0.0, "outcome": "done"}


def test_debate_corre_y_consolida():
    _fresh()
    res = eq.correr_debate("Dtest", "cual es la respuesta y por que?", max_rondas=4, n_workers=2,
                           confirm=True, runner=_fake_debate, umbral=0.6)
    assert res["rondas"] >= 1 and res["rondas"] <= 4
    cons = Path(res["consolidado"])
    assert cons.exists() and "## equipo-Dtest" in cons.read_text(encoding="utf-8")
    # con aportes identicos entre rondas debe saturar antes del tope
    assert res["saturado"] is True
    _ok("debate: corre olas, escribe rondas, consolida y SATURA con aportes repetidos")


# ---- 12: debate sin --confirm degrada a dry (guardrail) ----
def test_debate_sin_confirm_dry():
    _fresh()
    res = eq.correr_debate("Dx", "enunciado", confirm=False)
    assert res.get("dry") is True
    _ok("debate: sin --confirm degrada a dry-run")


# ---- 13: dashboard recolecta snapshot read-only ----
def test_dash_recolecta():
    d = _fresh()
    tm.publicar("t", "p", modelo="haiku", terminado="ok")
    snap = dash.recolectar()
    for k in ("cola_activas", "tiers_vivos", "stop", "locks", "dead_letters"):
        assert k in snap, k
    assert snap["stop"] is False
    # con STOP presente, lo refleja y el exit code pide atencion
    (d / "equipo").mkdir(parents=True, exist_ok=True)
    (d / "equipo" / "STOP").write_text("x", encoding="utf-8")
    assert dash.recolectar()["stop"] is True
    assert dash._exit_code(dash.recolectar()) == 1
    _ok("dashboard: snapshot read-only (cola/tiers/stop); refleja STOP y exit code de atencion")


# ---- 14: resolver_runtime aplica la estrategia de calidad (gratis/pago/hibrido + override) ----
def test_resolver_runtime():
    cfg = eq.cargar_config()
    # hibrido (default): debate y haiku -> api gratis; sonnet/opus -> claude
    assert eq.resolver_runtime("debate", "sonnet", cfg) == "api"
    assert eq.resolver_runtime("drenar", "haiku", cfg) == "api"
    assert eq.resolver_runtime("drenar", "sonnet", cfg) == "claude"
    assert eq.resolver_runtime("drenar", "opus", cfg) == "claude"
    # --runtime explicito SIEMPRE gana
    assert eq.resolver_runtime("drenar", "opus", cfg, cli="api") == "api"
    # modo gratis / pago fuerzan todo
    cfg["calidad"]["modo"] = "gratis"
    assert eq.resolver_runtime("drenar", "opus", cfg) == "api"
    cfg["calidad"]["modo"] = "pago"
    assert eq.resolver_runtime("debate", "haiku", cfg) == "claude"
    _ok("resolver_runtime: hibrido enruta por brecha; gratis/pago fuerzan; --runtime gana")


# ---- 15: drenar con runtime api en dry-run muestra proveedores y NO lanza ----
def test_drenar_api_dry():
    _fresh()
    tm.publicar("t-api", "p", modelo="haiku", terminado="ok")
    res = eq.drenar_cola("haiku", "api", dry_run=True)
    assert res["dry"] is True and res["runtime"] == "api"
    it = res["plan"][0]
    assert it["argv"] is None and it["api"] is not None and "proveedores" in it["api"]
    _ok("drenar api (dry): plan sin argv, describe proveedores/modelo, no lanza")


# ---- 16: worker api agentico cierra la tarea via 'terminar' (chat fake, 0 red) ----
def test_api_task_termina():
    _fresh()
    cfg = eq.cargar_config(); cfg["calidad"]["verificador"] = False  # aisla el cierre
    tid = tm.publicar("suma", "p", modelo="haiku", terminado="ok")
    orig = llm.chat
    llm.chat = lambda messages, tier="sonnet", cfg=None, tools=None, **k: {
        "ok": True, "text": "", "provider": "groq", "model": "m", "cost": 0.0, "intentos": [],
        "finish_reason": "tool_calls",
        "tool_calls": [{"id": "c1", "name": "terminar",
                        "args": {"resultado": "hecha", "resumen": "tarea resuelta"}}]}
    try:
        res = eq.drenar_cola("haiku", "api", cfg=cfg, confirm=True)
    finally:
        llm.chat = orig
    assert res["hechas"] == 1, res
    assert tm._load()["tareas"][tid]["estado"] == "hecha"
    _ok("api task: el bucle agentico llama 'terminar' -> el supervisor completa la tarea ($0)")


# ---- 17: verificador rechaza una salida pobre -> la tarea NO queda 'hecha' ----
def test_api_task_verificador_rechaza():
    _fresh()
    cfg = eq.cargar_config()
    cfg["calidad"]["verificador"] = True  # fuerza la 2a pasada
    tid = tm.publicar("dudosa", "p", modelo="haiku", terminado="debe compilar")

    def fake(messages, tier="sonnet", cfg=None, tools=None, **k):
        if tools:   # bucle de la tarea -> cierra como hecha
            return {"ok": True, "text": "", "provider": "groq", "model": "m", "cost": 0.0, "intentos": [],
                    "finish_reason": "tool_calls",
                    "tool_calls": [{"id": "c1", "name": "terminar",
                                    "args": {"resultado": "hecha", "resumen": "supuestamente listo"}}]}
        # verificador (sin tools) -> dice que NO cumple
        return {"ok": True, "text": '{"ok": false, "problemas": ["no compila"]}', "provider": "groq",
                "model": "m", "cost": 0.0, "intentos": [], "finish_reason": "stop", "tool_calls": []}

    orig = llm.chat
    llm.chat = fake
    try:
        res = eq.drenar_cola("haiku", "api", cfg=cfg, confirm=True)
    finally:
        llm.chat = orig
    estado = tm._load()["tareas"][tid]["estado"]
    assert estado != "hecha", estado   # el verificador la bloqueo
    assert any(r.get("outcome") == "rechazada_verificador" for r in res["resultados"]), res["resultados"]
    _ok("verificador: una salida que no cumple el criterio NO se marca hecha (se bloquea, $0)")


# ---- 18: debate con runtime api escribe la seccion via supervisor (sin carrera) ----
def test_api_debate_escribe():
    _fresh()
    orig = llm.chat
    llm.chat = lambda messages, tier="sonnet", cfg=None, tools=None, **k: {
        "ok": True, "text": "la respuesta es 42 por simetria", "provider": "gemini", "model": "m",
        "cost": 0.0, "intentos": [], "finish_reason": "stop", "tool_calls": []}
    try:
        res = eq.correr_debate("Dapi", "cual es la respuesta?", max_rondas=2, n_workers=2,
                               runtime="api", confirm=True, umbral=0.6)
    finally:
        llm.chat = orig
    cons = Path(res["consolidado"]).read_text(encoding="utf-8")
    assert "(via gemini)" in cons and "## equipo-Dapi" in cons
    _ok("api debate: el supervisor escribe la seccion del worker gratis en el doc de la ronda ($0)")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_equipo ({len(fns)} casos) ==")
    for fn in fns:
        try:
            fn(); ok += 1
        except Exception:
            print("FAIL", fn.__name__); traceback.print_exc()
    print(f"\n{ok}/{len(fns)} verde")
    sys.exit(0 if ok == len(fns) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _run()
