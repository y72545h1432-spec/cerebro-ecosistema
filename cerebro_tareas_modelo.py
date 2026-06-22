"""cerebro_tareas_modelo.py — MENSAJERIA DE TAREAS POR MODELO (multimodelo, ahorro de tokens).

POR QUE EXISTE (2026-06-17): para ahorrar, el usuario abre VARIAS sesiones Claude Code con modelos
distintos (p.ej. una Haiku para lo mecanico, una Opus para lo dificil). Esto es la cola que reparte el
trabajo POR MODELO: la sesion cara (Opus) PUBLICA tareas mecanicas dirigidas a `haiku`; la sesion barata
las TOMA y ejecuta. Routing por TIER DE MODELO, no por id de sesion (eso ya lo hace cerebro_multisesion).

Disciplina (igual que el arbol de tareas de tu-proyecto-agente): toda tarea lleva TODOS sus detalles — `proposito`
y `terminado` SIEMPRE; `archivos`+`pruebas` si toca codigo. `publicar` AVISA si faltan.

No duplica infra: escritura atomica con el _Mutex de cerebro_multisesion; difusion best-effort por
conocimiento(). Estado en %LOCALAPPDATA%/cerebro/tareas_modelo.json (coordinacion efimera, como locks).

CLI:
    publicar "<titulo>" -p "<proposito>" --modelo haiku --terminado "<criterio>" [--archivo x --prueba c]
    pendientes [modelo]          # tareas pendientes dirigidas a ese modelo (o 'any'); sin arg = todas
    tomar <id> --por <sesion>    # reclamo atomico (solo si esta pendiente)
    completar <id> [-n nota]
    cancelar <id> [-m motivo]
    fallar <id> [-m motivo]      # cierre terminal: lo intento y fallo (A2A failed)
    rechazar <id> [-m motivo]    # cierre terminal: declina por alcance/permisos (A2A rejected)
    expirar [ttl_min]            # visibility timeout: 'tomada' colgada -> vuelve a pendiente (def 30)
    tablero                      # quien debe hacer que, agrupado por modelo
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core  # base comun: io atomica, tiempo, normalizacion  # noqa: E402
from cerebro_multisesion import _Mutex  # mutex de proceso (serializa entre sesiones)  # noqa: E402
from cerebro_core import now as _now, to_list as _as_list  # noqa: E402

MODELOS = ("haiku", "sonnet", "opus", "any")
# Estados de tarea (alineados con el lifecycle A2A: working/completed/failed/rejected/canceled).
ESTADOS = ("pendiente", "tomada", "hecha", "cancelada", "fallida", "rechazada")
TERMINALES = ("hecha", "cancelada", "fallida", "rechazada")

# Estado junto al resto de coordinacion efimera del cerebro.
STORE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "cerebro" / "tareas_modelo.json"


# _now (timestamp) y _as_list (coercion str/lista) viven en cerebro_core (importados arriba).


def _load() -> dict:
    d = core.read_json_tolerant(STORE)
    return d if isinstance(d, dict) else {"seq": 0, "tareas": {}}


def _save(d: dict) -> None:
    core.write_atomic(STORE, d)


def _norm_modelo(modelo: str) -> str:
    m = (modelo or "any").strip().lower()
    return m if m in MODELOS else "any"


def publicar(titulo: str, proposito: str, modelo: str = "any", terminado: str = "",
             archivos=None, pruebas=None, prioridad: int = 0, creada_por: str = "") -> str:
    """Encola una tarea dirigida a un TIER de modelo. Devuelve su id. Avisa si faltan detalles."""
    with _Mutex("tareas_modelo"):
        d = _load()
        d["seq"] += 1
        tid = f"M{d['seq']:03d}"
        t = {"id": tid, "titulo": titulo, "proposito": proposito or "",
             "modelo": _norm_modelo(modelo), "terminado": terminado or "",
             "archivos": _as_list(archivos), "pruebas": _as_list(pruebas),
             "prioridad": int(prioridad), "estado": "pendiente",
             "creada_por": creada_por or "?", "tomada_por": "",
             "ts_creada": _now(), "ts_tomada": "", "ts_hecha": "",
             "nota": "", "bitacora": []}
        d["tareas"][tid] = t
        _save(d)
    _avisar_detalles(t)
    return tid


def _avisar_detalles(t: dict) -> None:
    faltan = []
    if not (t.get("proposito") or "").strip():
        faltan.append("-p/--proposito")
    if not (t.get("terminado") or "").strip():
        faltan.append("--terminado")
    if t.get("archivos") and not t.get("pruebas"):
        faltan.append("--prueba (declaraste archivos pero ninguna prueba)")
    if faltan:
        print(f"AVISO {t['id']}: faltan detalles -> " + "; ".join(faltan), file=sys.stderr)


def pendientes(modelo: str | None = None, d: dict | None = None) -> list:
    """Tareas PENDIENTES que una sesion de `modelo` debe atender: las dirigidas a ese tier MAS las
    'any'. Sin `modelo` -> todas las pendientes. d inyectable (testeable). Orden: prioridad desc."""
    d = d if d is not None else _load()
    m = _norm_modelo(modelo) if modelo else None
    out = []
    for t in d.get("tareas", {}).values():
        if t.get("estado") != "pendiente":
            continue
        if m and t.get("modelo") not in (m, "any"):
            continue
        out.append(t)
    return sorted(out, key=lambda t: (-int(t.get("prioridad", 0)), t.get("ts_creada", "")))


def tomar(tid: str, por: str) -> bool:
    """Reclamo ATOMICO: solo si la tarea sigue 'pendiente'. Devuelve False si ya estaba tomada/hecha."""
    with _Mutex("tareas_modelo"):
        d = _load()
        t = d.get("tareas", {}).get(tid)
        if not t or t["estado"] != "pendiente":
            return False
        t["estado"] = "tomada"
        t["tomada_por"] = por or "?"
        t["ts_tomada"] = _now()
        t["bitacora"].append({"ts": _now(), "texto": f"[tomada] {por}"})
        _save(d)
        return True


def completar(tid: str, nota: str = "", por: str | None = None) -> bool:
    return _cerrar(tid, "hecha", nota, por)


def cancelar(tid: str, motivo: str = "", por: str | None = None) -> bool:
    return _cerrar(tid, "cancelada", motivo, por)


def fallar(tid: str, motivo: str = "", por: str | None = None) -> bool:
    """Cierre terminal 'fallida' (A2A failed): el worker LO INTENTO y no lo logro. Lleva evidencia/motivo."""
    return _cerrar(tid, "fallida", motivo, por)


def rechazar(tid: str, motivo: str = "", por: str | None = None) -> bool:
    """Cierre terminal 'rechazada' (A2A rejected): el worker DECLINA (fuera de alcance/permisos/ownership)."""
    return _cerrar(tid, "rechazada", motivo, por)


def expirar_tomadas(ttl_min: int = 30, ahora: datetime | None = None) -> list:
    """Visibility timeout: una tarea 'tomada' cuyo worker murio/desaparecio queda colgada para siempre.
    Reclama las 'tomada' cuyo `ts_tomada` es mas viejo que `ttl_min` -> vuelven a 'pendiente'
    (re-entregables a otra sesion). Devuelve los ids reclamados. `ahora` inyectable (testeable)."""
    ahora = ahora or datetime.now()
    reclamadas: list = []
    with _Mutex("tareas_modelo"):
        d = _load()
        for t in d.get("tareas", {}).values():
            if t.get("estado") != "tomada":
                continue
            ts = t.get("ts_tomada")
            if not ts:
                continue
            try:
                if (ahora - datetime.fromisoformat(ts)).total_seconds() <= ttl_min * 60:
                    continue
            except Exception:
                continue
            quien = t.get("tomada_por", "")
            t["estado"] = "pendiente"
            t["tomada_por"] = ""
            t["ts_tomada"] = ""
            t["bitacora"].append({"ts": _now(),
                                  "texto": f"[reclamada-ttl] worker {quien} sin cerrar > {ttl_min}min"})
            reclamadas.append(t["id"])
        if reclamadas:
            _save(d)
    return reclamadas


def _cerrar(tid: str, estado: str, nota: str, por: str | None) -> bool:
    with _Mutex("tareas_modelo"):
        d = _load()
        t = d.get("tareas", {}).get(tid)
        if not t or t["estado"] in TERMINALES:
            return False
        t["estado"] = estado
        t["nota"] = nota or t.get("nota", "")
        t["ts_hecha"] = _now()
        if por:
            t["tomada_por"] = t["tomada_por"] or por
        t["bitacora"].append({"ts": _now(), "texto": f"[{estado}] {nota}"})
        _save(d)
        return True


def tablero(d: dict | None = None) -> dict:
    """Vista read-only agrupada por modelo: {modelo: [tareas activas (pendiente/tomada)]}."""
    d = d if d is not None else _load()
    out: dict = {m: [] for m in MODELOS}
    for t in d.get("tareas", {}).values():
        if t.get("estado") in ("pendiente", "tomada"):
            out.setdefault(t.get("modelo", "any"), []).append(t)
    for m in out:
        out[m].sort(key=lambda t: (-int(t.get("prioridad", 0)), t.get("ts_creada", "")))
    return {m: v for m, v in out.items() if v}


# ---------------- CLI ----------------
def _print_tablero() -> None:
    tb = tablero()
    print("TABLERO DE TAREAS POR MODELO (activas)")
    if not tb:
        print("  (sin tareas activas)")
        return
    for m in MODELOS:
        if m not in tb:
            continue
        print(f"  [{m}]")
        for t in tb[m]:
            est = "PEND" if t["estado"] == "pendiente" else "TOMADA"
            quien = f" por {t['tomada_por']}" if t["estado"] == "tomada" else ""
            print(f"    {t['id']} [{est}{quien}] {t['titulo']} | {t['proposito'][:60]}")


def _print_pendientes(modelo: str | None) -> None:
    ps = pendientes(modelo)
    foco = f" para {modelo}" if modelo else ""
    print(f"PENDIENTES{foco}: {len(ps)}")
    for t in ps:
        files = (" | archivos: " + ",".join(t["archivos"])) if t["archivos"] else ""
        print(f"  {t['id']} ({t['modelo']}) {t['titulo']} -> {t['terminado'][:50]}{files}")


def _cli(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "tablero":
        _print_tablero(); return 0
    if cmd == "pendientes":
        _print_pendientes(argv[1] if len(argv) > 1 else None); return 0
    if cmd == "expirar":
        ttl = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else 30
        r = expirar_tomadas(ttl)
        print(f"reclamadas (>{ttl}min sin cerrar): {len(r)} {r}"); return 0
    import argparse
    p = argparse.ArgumentParser(prog="cerebro_tareas_modelo")
    sub = p.add_subparsers(dest="cmd")
    pp = sub.add_parser("publicar")
    pp.add_argument("titulo")
    pp.add_argument("-p", "--proposito", required=True)
    pp.add_argument("--modelo", default="any")
    pp.add_argument("--terminado", default="")
    pp.add_argument("--archivo", dest="archivos", action="append", default=[])
    pp.add_argument("--prueba", dest="pruebas", action="append", default=[])
    pp.add_argument("--prioridad", type=int, default=0)
    pp.add_argument("--por", default="?")
    for name in ("tomar", "completar", "cancelar", "fallar", "rechazar"):
        q = sub.add_parser(name)
        q.add_argument("tid")
        q.add_argument("--por", default=None)
        q.add_argument("-n", "--nota", default="")
        q.add_argument("-m", "--motivo", default="")
    a = p.parse_args(argv)
    if a.cmd == "publicar":
        tid = publicar(a.titulo, a.proposito, a.modelo, a.terminado, a.archivos, a.pruebas,
                       a.prioridad, a.por)
        print(tid); return 0
    if a.cmd == "tomar":
        print("OK" if tomar(a.tid, a.por or "?") else "NO (ya tomada/inexistente)")
        return 0
    if a.cmd == "completar":
        print("OK" if completar(a.tid, a.nota, a.por) else "NO")
        return 0
    if a.cmd == "cancelar":
        print("OK" if cancelar(a.tid, a.motivo, a.por) else "NO")
        return 0
    if a.cmd == "fallar":
        print("OK" if fallar(a.tid, a.motivo, a.por) else "NO")
        return 0
    if a.cmd == "rechazar":
        print("OK" if rechazar(a.tid, a.motivo, a.por) else "NO")
        return 0
    print(f"comando desconocido: {cmd}"); return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(_cli(sys.argv[1:]))
