"""CEREBRO · HECHOS VERIFICABLES (capa anti-discrepancias de conocimiento entre agentes)

Problema que resuelve (incidente 2026-06-17): un agente afirmo "los imports fallan" como un HECHO
ABSOLUTO cuando en realidad era RELATIVO A SU ENTORNO (un interprete sin las deps). El otro agente,
en otro interprete, veia lo contrario. El mensaje se creyo en vez de verificarse; nadie detecto el
conflicto. Resultado: conocimiento divergente entre sesiones.

Idea (alineada con la literatura multi-agente: provenance + verificacion externa + deteccion de
conflictos en vez de propagarlos en silencio — TrustTrack arXiv:2507.22077; blackboard arXiv:2510.01285):
  Una afirmacion sobre el estado del sistema NO se "cuenta": se PRUEBA.
    1. PROVENANCE  — cada hecho guarda el comando exacto, su codigo de salida y su salida (evidencia).
    2. ENTORNO     — cada hecho guarda su HUELLA (interprete, version, venv, host, cwd). La mayoria de
                     las "discrepancias" son hechos RELATIVOS AL ENTORNO dichos como absolutos.
    3. GROUND TRUTH— `probe()` EJECUTA el comando y deriva el hecho del resultado real (no del decir).
    4. CONFLICTO   — al registrar, se comparan los hechos recientes del MISMO subject; si difieren se
                     ALERTA y se ETIQUETA: "entorno" (ambas ciertas, distinto entorno) vs "contradiccion"
                     (mismo entorno, hecho real divergente -> hay que resolver). Nunca se propaga callado.
    5. RE-VERIFICAR— `verificar()` re-corre el comando del hecho EN TU entorno: confirmas o refutas en
                     vez de confiar. Es la prueba reproducible compartida.

Autocontenido: solo stdlib. Almacen propio (hechos.jsonl) -> NO toca multisesion.json ni su nucleo.
Lo usan por igual Claude y Codex (CLI + API). Avisa por el buzon de Multisesion si esta disponible
(best-effort: si no, el hecho queda igualmente registrado y `conflictos()` lo detecta).

CLI:
    py cerebro_hechos.py probe <subject> -- <comando...>     # ejecuta y registra el hecho (ground truth)
    py cerebro_hechos.py afirmar <subject> <ok|fail|info> "<claim>" [--cmd "..."]   # manual (peor: sin prueba)
    py cerebro_hechos.py verificar <subject>                 # re-corre el ultimo probe EN TU entorno
    py cerebro_hechos.py conflictos                          # discrepancias abiertas (con su tipo)
    py cerebro_hechos.py ver <subject>                       # historial de un subject
    py cerebro_hechos.py lista [n]                           # ultimos hechos
"""
from __future__ import annotations
import os, sys, uuid, subprocess, pathlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core  # base comun: io jsonl/tiempo/env/mutex  # noqa: E402
from cerebro_core import now as _ahora, env_fingerprint, FileMutex, read_jsonl as _leer  # noqa: E402

STATE_DIR = core.STATE_DIR
HECHOS = STATE_DIR / "hechos.jsonl"
RESOLUCIONES = STATE_DIR / "hechos_resueltos.jsonl"

VENTANA_MIN = 180          # un hecho cuenta como "vigente" para detectar conflictos durante 3h
MAX_OUTPUT = 1500          # truncado de la evidencia de salida
PROBE_TIMEOUT = 120        # s por comando de prueba
STATUS = {"ok", "fail", "info"}


def _vigente(iso: str, minutos: int) -> bool:
    """Inverso de core.is_expired: True si el hecho aun cuenta como reciente (<= minutos)."""
    return not core.is_expired(iso, minutos)


# _ahora (timestamp) y env_fingerprint (huella de entorno, incl. shell efectivo) viven en cerebro_core.


# Dimensiones que definen "el mismo entorno" al comparar hechos. SUPUESTO MONO-HOST explícito
# (causa raíz #6): `host` está incluido, así que dos hosts NUNCA se cruzan como contradicción; pero
# el resto de la capa (locks/TTL) sí asume un único host con un único reloj de pared — ver
# 13_COMUNICACION_TIEMPO_REAL.md §Supuestos de entorno.
_ENV_DIMS = ("host", "python", "py_version", "venv", "shell")


def _env_key(env: dict) -> tuple:
    """Identidad de un entorno para comparar hechos: si difiere, dos resultados distintos pueden ser
    AMBOS ciertos (cada uno en su entorno). Incluye el `shell` efectivo (P2.3)."""
    return tuple(env.get(dim, "") for dim in _ENV_DIMS)


def _append(path: pathlib.Path, item: dict) -> None:
    """Append-only con MUTEX de proceso (fix race 2026-06-21): dos agentes escribiendo el mismo
    .jsonl a la vez podian interleaver lineas -> linea corrupta que rompe la deteccion de conflictos.
    El FileMutex serializa la escritura entre procesos. La lectura (_leer = cerebro_core.read_jsonl,
    importado arriba) tolera lineas mal formadas, asi que las lecturas siguen sin lock."""
    with FileMutex("hechos"):
        core.append_jsonl(path, item)


def _avisar_buzon(hecho: dict, conflicto: dict | None) -> None:
    """Best-effort: si Multisesion esta disponible, publica el hecho/conflicto en el buzon comun."""
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
        from cerebro_multisesion import Multisesion
        ms = Multisesion("hechos verificables", project=hecho.get("project", "general"),
                         agent=hecho.get("agent", "desconocido"), runtime=hecho.get("runtime"))
        if conflicto:
            # Closed-loop por código: el blocker requires_ack lleva expires_at = ventana de vigencia
            # del conflicto. Sin él, leer_buzon lo mostraba PARA SIEMPRE (causa raíz #3: best-effort
            # sin respaldo). Con caducidad, o se ackea a tiempo o cae a dead_letter (lo rescata
            # cerebro_salud.py) — nunca un requires_ack inmortal en el buzón.
            vence = (datetime.now() + timedelta(minutes=VENTANA_MIN)).isoformat(timespec="seconds")
            ms.mensaje_tipo(
                "*", type="blocker", priority="high", requires_ack=True,
                summary=f"DISCREPANCIA [{conflicto['tipo']}] en {hecho['subject']}",
                details=conflicto["explicacion"], expires_at=vence,
                evidence=[conflicto], resource=hecho["subject"])
        ms.despedir()
    except Exception:
        pass   # el hecho ya quedo registrado; el aviso es un extra, no debe romper nada


def _hecho_nuevo(subject: str, claim: str, status: str, command: str, exit_code,
                 output: str, kind: str, agent: str, runtime: str | None,
                 project: str, sesion: str) -> dict:
    return {
        "id": f"hecho_{uuid.uuid4().hex[:12]}", "ts": _ahora(),
        "subject": subject.strip(), "claim": claim, "status": status, "kind": kind,
        "command": command, "exit_code": exit_code, "output": (output or "")[:MAX_OUTPUT],
        "env": env_fingerprint(), "agent": agent, "runtime": runtime or agent,
        "project": project, "sesion": sesion,
    }


def _detectar_conflicto(nuevo: dict, ventana_min: int = VENTANA_MIN) -> dict | None:
    """Compara el hecho nuevo contra los recientes del MISMO subject. Devuelve el conflicto mas
    relevante o None. Etiqueta 'entorno' (distinto entorno -> ambas pueden ser ciertas) o
    'contradiccion' (mismo entorno, status divergente -> hecho real en disputa)."""
    resueltos = {r.get("subject") for r in _leer(RESOLUCIONES)
                 if _vigente(r.get("ts", ""), ventana_min)}
    if nuevo["subject"] in resueltos:
        return None
    previos = [h for h in _leer(HECHOS)
               if h["subject"] == nuevo["subject"] and h["id"] != nuevo["id"]
               and _vigente(h.get("ts", ""), ventana_min)]
    choques = [h for h in previos if h.get("status") != nuevo.get("status")]
    if not choques:
        return None
    # Prioriza el choque del MISMO entorno (contradiccion real) sobre el de otro entorno.
    mismo_env = [h for h in choques if _env_key(h["env"]) == _env_key(nuevo["env"])]
    otro = choques[-1]
    if mismo_env:
        prev, tipo = mismo_env[-1], "contradiccion"
        explic = (f"MISMO entorno, status divergente: {nuevo['agent']} dice '{nuevo['status']}' "
                  f"y {prev['agent']} dijo '{prev['status']}' para '{nuevo['subject']}'. "
                  f"Es una contradiccion real -> reproducir y resolver (no confiar en ninguna a ciegas).")
    else:
        prev, tipo = otro, "entorno"
        explic = (f"Distinto entorno: {nuevo['agent']} ({nuevo['env'].get('py_version')}, "
                  f"venv={nuevo['env'].get('venv') or 'system'}) dice '{nuevo['status']}'; "
                  f"{prev['agent']} ({prev['env'].get('py_version')}, venv={prev['env'].get('venv') or 'system'}) "
                  f"dijo '{prev['status']}'. PROBABLEMENTE AMBAS CIERTAS en su entorno: NO es absoluto. "
                  f"Para alinear: cada agente corre el mismo comando o iguala el entorno.")
    return {"tipo": tipo, "subject": nuevo["subject"], "explicacion": explic,
            "nuevo": {"id": nuevo["id"], "agent": nuevo["agent"], "status": nuevo["status"],
                      "env": nuevo["env"], "command": nuevo["command"]},
            "previo": {"id": prev["id"], "agent": prev["agent"], "status": prev["status"],
                       "env": prev["env"], "command": prev.get("command", "")}}


def _registrar(hecho: dict, avisar: bool = True) -> dict:
    _append(HECHOS, hecho)
    conflicto = _detectar_conflicto(hecho)
    if avisar:
        _avisar_buzon(hecho, conflicto)
    return {"hecho": hecho, "conflicto": conflicto}


def probe(subject: str, command, *, agent: str = "desconocido", runtime: str | None = None,
          project: str = "general", sesion: str = "", claim: str = "", avisar: bool = True,
          timeout: int = PROBE_TIMEOUT) -> dict:
    """GROUND TRUTH: ejecuta `command`, deriva el hecho del resultado real (exit 0 -> ok, si no fail),
    lo registra con su evidencia + huella de entorno y detecta conflictos. `command` puede ser str
    (shell) o lista (argv)."""
    shell = isinstance(command, str)
    try:
        r = subprocess.run(command, shell=shell, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        exit_code = r.returncode
        output = (r.stdout or "") + (("\n[stderr]\n" + r.stderr) if r.stderr else "")
        status = "ok" if exit_code == 0 else "fail"
    except subprocess.TimeoutExpired:
        exit_code, output, status = None, f"(timeout {timeout}s)", "fail"
    except Exception as e:
        exit_code, output, status = None, f"(no se pudo ejecutar: {e})", "fail"
    # Guarda el comando TAL CUAL (lista o str): asi `verificar` lo re-corre identico, sin re-cotizar
    # (re-unir una lista ya partida por el shell y re-pasarla al shell rompe el quoting -> falsos fail).
    hecho = _hecho_nuevo(subject, claim or f"probe {status}", status, command, exit_code,
                         output, "probe", agent, runtime, project, sesion)
    return _registrar(hecho, avisar=avisar)


def afirmar(subject: str, status: str, claim: str, *, command: str = "", agent: str = "desconocido",
            runtime: str | None = None, project: str = "general", sesion: str = "",
            avisar: bool = True) -> dict:
    """Afirmacion MANUAL (sin ejecutar): provenance mas debil que probe. Igual lleva huella de entorno
    y dispara deteccion de conflictos. Usar solo cuando no hay comando reproducible."""
    status = status if status in STATUS else "info"
    hecho = _hecho_nuevo(subject, claim, status, command, None, "", "manual",
                         agent, runtime, project, sesion)
    return _registrar(hecho, avisar=avisar)


def verificar(subject: str, *, agent: str = "desconocido", runtime: str | None = None,
              project: str = "general", sesion: str = "") -> dict | None:
    """Re-corre el comando del ultimo PROBE de `subject` EN TU entorno y registra el resultado fresco.
    Asi confirmas/refutas en vez de confiar. Devuelve {hecho, conflicto} o None si no hay probe previo."""
    probes = [h for h in _leer(HECHOS) if h["subject"] == subject and h.get("kind") == "probe"
              and h.get("command")]
    if not probes:
        return None
    cmd = probes[-1]["command"]
    return probe(subject, cmd, agent=agent, runtime=runtime, project=project, sesion=sesion,
                 claim=f"re-verificacion de {subject}")


def resolver(subject: str, nota: str, *, agent: str = "desconocido", project: str = "general") -> None:
    """Marca la discrepancia de `subject` como resuelta (deja de alertar). Deja la nota de provenance."""
    _append(RESOLUCIONES, {"ts": _ahora(), "subject": subject, "nota": nota,
                           "agent": agent, "project": project})


def conflictos(ventana_min: int = VENTANA_MIN) -> list[dict]:
    """Subjects con >=2 hechos recientes de status distinto, sin resolver. Cada uno etiquetado por tipo."""
    resueltos = {r.get("subject") for r in _leer(RESOLUCIONES) if _vigente(r.get("ts", ""), ventana_min)}
    recientes = [h for h in _leer(HECHOS) if _vigente(h.get("ts", ""), ventana_min)]
    por_subject: dict[str, list] = {}
    for h in recientes:
        por_subject.setdefault(h["subject"], []).append(h)
    out = []
    for subj, hs in por_subject.items():
        if subj in resueltos:
            continue
        statuses = {h.get("status") for h in hs}
        if len(statuses) < 2:
            continue
        c = _detectar_conflicto(hs[-1], ventana_min)
        if c:
            out.append(c)
    return out


def historial(subject: str, n: int = 20) -> list[dict]:
    return [h for h in _leer(HECHOS) if h["subject"] == subject][-n:]


# ---------------- CLI ----------------
def _agent_env() -> dict:
    return {"agent": os.environ.get("CEREBRO_AGENT", "desconocido"),
            "runtime": os.environ.get("CEREBRO_RUNTIME")}


def _main(argv: list[str]) -> int:
    if not argv:
        print(__doc__); return 0
    cmd = argv[0]
    ae = _agent_env()
    if cmd == "probe":
        if "--" not in argv:
            print("uso: probe <subject> -- <comando...>"); return 2
        i = argv.index("--")
        subject = " ".join(argv[1:i]).strip()
        comando = argv[i + 1:]            # lista ya partida por el shell -> shell=False, sin re-cotizar
        res = probe(subject, comando, **ae)
        _print_res(res); return 0
    if cmd == "afirmar":
        if len(argv) < 4:
            print('uso: afirmar <subject> <ok|fail|info> "<claim>" [--cmd "..."]'); return 2
        subject, status, claim = argv[1], argv[2], argv[3]
        command = ""
        if "--cmd" in argv:
            command = argv[argv.index("--cmd") + 1]
        res = afirmar(subject, status, claim, command=command, **ae)
        _print_res(res); return 0
    if cmd == "verificar":
        res = verificar(argv[1], **ae) if len(argv) > 1 else None
        if res is None:
            print("(no hay probe previo para ese subject)"); return 1
        _print_res(res); return 0
    if cmd == "conflictos":
        cs = conflictos()
        if not cs:
            print("(sin discrepancias abiertas)"); return 0
        for c in cs:
            print(f"[{c['tipo'].upper()}] {c['subject']}\n    {c['explicacion']}")
        return 0
    if cmd == "ver":
        for h in historial(argv[1]) if len(argv) > 1 else []:
            print(f"  [{h['ts']}] {h['agent']}/{h['env'].get('py_version')} "
                  f"venv={h['env'].get('venv') or 'system'} -> {h['status']} | {h['claim']}")
        return 0
    if cmd == "lista":
        n = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 20
        for h in _leer(HECHOS)[-n:]:
            print(f"  [{h['ts']}] ({h['agent']}/{h['project']}) {h['subject']} -> {h['status']}")
        return 0
    print(f"comando desconocido: {cmd}"); return 2


def _print_res(res: dict) -> None:
    h = res["hecho"]
    print(f"hecho registrado: {h['subject']} -> {h['status']} (exit={h['exit_code']}) "
          f"[{h['agent']}/{h['env'].get('py_version')}, venv={h['env'].get('venv') or 'system'}]")
    if res["conflicto"]:
        c = res["conflicto"]
        print(f"\n  ⚠ DISCREPANCIA [{c['tipo'].upper()}]: {c['explicacion']}")
    else:
        print("  (sin conflicto con hechos recientes)")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(_main(sys.argv[1:]))
