"""cerebro_coprog.py — co-programacion sin choques: TABLERO de "quien edita que" + helpers de
reclamo de ARCHIVOS sobre la API de locks que ya existe en cerebro_multisesion.

POR QUE EXISTE (2026-06-17): dos sesiones (p.ej. dos Claude, o Claude+Codex) editaban el mismo
archivo de codigo (cognition.py) sin reclamar lock -> una tenia que ADIVINAR por mtimes que tocaba la
otra. Esto formaliza la regla y la hace de UN comando: antes de editar un archivo de codigo compartido,
reclama `file:<archivo>`; si esta tomado, NO edites: coordina por buzon y espera. Y cualquiera puede ver
el tablero de ownership en vivo.

NO duplica infra: usa Multisesion.reclamar/liberar (TTL 30min, latido que renueva, reaper de muertos).
Es una capa fina + un CLI read-only. La usan IGUAL Claude y Codex.

USO COMO LIBRERIA (dentro de tu sesion viva, con tu `ms`):
    import sys; sys.path.insert(0, r"~\\.cerebro")
    import cerebro_coprog as cop
    from cerebro_multisesion import Multisesion
    ms = Multisesion("editar espina", project="tu-proyecto-agente", agent="claude", runtime="claude-code")
    if cop.claim_all(ms, "cognition.py", "arbiter.py"):   # reclama AMBOS o ninguno
        ... editar ...
        cop.release(ms, "cognition.py", "arbiter.py")
    else:
        ... NO editar: coordinar por ms.mensaje_tipo(type="blocker"/"handoff") y reintentar ...
    # en ediciones largas: ms.latido() periodico renueva tus locks de archivo.

USO COMO CLI (read-only, sin crear sesion; cualquiera, cuando sea):
    py -3 cerebro_coprog.py board                 # quien edita que (todos los proyectos)
    py -3 cerebro_coprog.py board tu-proyecto-agente          # solo un proyecto
    py -3 cerebro_coprog.py check tu-proyecto-agente cognition.py arbiter.py   # ¿libres? (exit 0=si, 1=tomado)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cerebro_multisesion import TTL_LOCK_MIN, _solo_lectura  # noqa: E402

FILE_PREFIX = "file:"


def file_key(path: str) -> str:
    """Clave canonica del lock de un archivo: `file:<basename en minusculas>`.
    Normaliza para que 'cognition.py', './cognition.py' y 'C:\\...\\cognition.py' colisionen."""
    return FILE_PREFIX + os.path.basename(str(path)).strip().lower()


def _edad_min(desde: str) -> float:
    try:
        return round((datetime.now() - datetime.fromisoformat(desde)).total_seconds() / 60.0, 1)
    except Exception:
        return -1.0


# ---------- lectura (read-only; no necesita sesion) ----------
def board(project: str | None = None, d: dict | None = None) -> list[dict]:
    """Tablero de ownership de ARCHIVOS: lista de locks `file:*` vigentes con quien, agente,
    runtime, edad en minutos, motivo y la tarea actual de esa sesion. d inyectable (testeable)."""
    d = d if d is not None else _solo_lectura()
    sesiones = d.get("sesiones", {})
    filas = []
    for l in d.get("locks", {}).values():
        rec = l.get("recurso", "")
        if not rec.startswith(FILE_PREFIX):
            continue
        if project and l.get("project") != project and not str(rec).startswith("*:"):
            continue
        sid = l.get("sesion", "")
        filas.append({
            "archivo": rec[len(FILE_PREFIX):],
            "recurso": rec,
            "project": l.get("project", "?"),
            "sesion": sid,
            "agent": l.get("agent", "?"),
            "runtime": l.get("runtime", "?"),
            "edad_min": _edad_min(l.get("desde", "")),
            "ttl_min": TTL_LOCK_MIN,
            "motivo": l.get("motivo", ""),
            "tarea": sesiones.get(sid, {}).get("tarea", ""),
        })
    return sorted(filas, key=lambda f: f["archivo"])


def who_has(path: str, project: str | None = None, d: dict | None = None) -> dict | None:
    """Quien tiene reclamado un archivo (o None si esta libre). d inyectable (testeable)."""
    fk = file_key(path)
    for fila in board(project=project, d=d):
        if fila["recurso"] == fk:
            return fila
    return None


# ---------- escritura (requiere una sesion VIVA `ms`; el lock vive mientras ella late) ----------
def claim(ms, *paths: str, motivo: str = "") -> dict:
    """Reclama `file:<archivo>` para cada path con TU sesion. Devuelve {archivo: bool}.
    El lock se mantiene mientras tu sesion late (ms.latido); se libera con release() o al morir."""
    out = {}
    for p in paths:
        out[os.path.basename(str(p))] = bool(ms.reclamar(file_key(p), motivo=motivo))
    return out


def claim_all(ms, *paths: str, motivo: str = "") -> bool:
    """Reclama TODOS los archivos o NINGUNO (all-or-nothing): si alguno esta tomado por otra sesion,
    suelta los que si consiguio y devuelve False (para que NO edites un set a medias)."""
    got = []
    for p in paths:
        if ms.reclamar(file_key(p), motivo=motivo):
            got.append(p)
        else:
            for g in got:
                ms.liberar(file_key(g))
            return False
    return True


def release(ms, *paths: str) -> None:
    """Libera tus locks de archivo (al terminar de editar)."""
    for p in paths:
        ms.liberar(file_key(p))


# ---------- CLI read-only ----------
def _print_board(project: str | None = None) -> None:
    # ASCII puro a proposito: una herramienta de coordinacion NO debe crashear al imprimir en
    # consolas cp1252 (Windows). Sin emojis ni guiones largos.
    filas = board(project)
    foco = f" - {project}" if project else " - todos los proyectos"
    print(f"TABLERO CO-PROGRAMACION (archivos en edicion ahora){foco}")
    if not filas:
        print("  (nadie tiene archivos reclamados)")
        return
    for f in filas:
        viejo = " [OJO: por expirar]" if 0 <= f["ttl_min"] - f["edad_min"] <= 5 else ""
        print(f"  [EDIT] {f['archivo']:<22} {f['agent']}/{f['project']} [{f['sesion']}] "
              f"hace {f['edad_min']}min/{f['ttl_min']}{viejo} | {f['tarea']}")


def _cli(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "board":
        _print_board(argv[1] if len(argv) > 1 else None)
        return 0
    if cmd == "check":
        if len(argv) < 3:
            print("uso: check <project> <archivo> [archivo...]")
            return 2
        project, files = argv[1], argv[2:]
        tomado = False
        for f in files:
            h = who_has(f, project=project)
            if h:
                print(f"  [TOMADO] {f}: por {h['agent']} [{h['sesion']}] hace {h['edad_min']}min | {h['tarea']}")
                tomado = True
            else:
                print(f"  [LIBRE]  {f}: libre")
        return 1 if tomado else 0
    print(f"comando desconocido: {cmd}\n{__doc__}")
    return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(_cli(sys.argv[1:]))
