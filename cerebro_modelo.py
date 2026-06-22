"""cerebro_modelo.py — ROUTER DE TAREAS POR MODELO (auto-conocimiento de tier + clasificador + liveness).

POR QUE EXISTE (2026-06-17): para ahorrar tokens, el usuario abre VARIAS sesiones Claude Code con modelos
distintos y le habla a UNA (la orquestadora). Esta sesion debe (a) saber su propio tier, (b) clasificar la
tarea entrante y (c) repartirla al tier correcto. Este modulo es el cerebro de ese router; la cola fisica
sigue siendo cerebro_tareas_modelo.py (no se duplica). Spec: .cerebro/specs/2026-06-17-router-por-modelo-design.md

Tres responsabilidades:
  - tier_de(model_id)       : mapea un id de modelo a su tier (opus/sonnet/haiku). Desconocido -> opus (seguro).
  - registrar/vivos         : heartbeat por tier (que sesiones-modelo estan vivas ahora; TTL).
  - clasificar              : heuristica que PROPONE un tier + razon (la sesion confirma — diseno hibrido).
  - delegar                 : publica en la cola para un tier y arma el aviso (encolada / abre sesion <tier>).

No duplica infra: escritura atomica con _Mutex de cerebro_multisesion; estado efimero en
%LOCALAPPDATA%/cerebro/modelos_vivos.json (como los locks).

CLI:
    soy <model-id>                       # imprime el tier de ese id (p.ej. claude-opus-4-8 -> opus)
    registrar <tier> [--sesion s]        # marca ese tier como vivo (heartbeat)
    vivos                                # tiers con sesion viva ahora
    clasificar "<titulo>" [-p prop] [--archivo x]   # propone tier + razon
    delegar "<titulo>" -p <prop> --tier <t> --terminado <c> [--archivo x --prueba c] [--prioridad n] [--por s]
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core  # base comun: io atomica, tiempo, normalizacion  # noqa: E402
from cerebro_multisesion import _Mutex  # mutex de proceso (serializa entre sesiones)  # noqa: E402
import cerebro_tareas_modelo as tareas   # la cola fisica por tier  # noqa: E402
from cerebro_core import now as _now, unfold as _fold  # noqa: E402

TIERS = ("haiku", "sonnet", "opus")
TTL_SEG = 900  # 15 min sin heartbeat -> el tier deja de contar como vivo

# Estado junto al resto de coordinacion efimera del cerebro.
STORE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "cerebro" / "modelos_vivos.json"


# _now y _fold (normalizacion sin acentos) viven en cerebro_core (importados arriba).


# --------------------------------------------------------------------------- model id -> tier
def tier_de(model_id: str) -> str:
    """Mapea un id de modelo de Anthropic a su tier. Desconocido/vacio -> 'opus' (default SEGURO:
    nunca degradar trabajo a un tier barato sin certeza del modelo)."""
    m = _fold(model_id)
    if "haiku" in m:
        return "haiku"
    if "sonnet" in m:
        return "sonnet"
    if "opus" in m or "fable" in m:   # fable = tope de gama -> tier opus
        return "opus"
    return "opus"


# --------------------------------------------------------------------------- liveness (heartbeat + TTL)
def _load() -> dict:
    d = core.read_json_tolerant(STORE)
    return d if isinstance(d, dict) else {}


def _save(d: dict) -> None:
    core.write_atomic(STORE, d)


def registrar(tier: str, sesion: str = "") -> None:
    """Marca un tier como vivo AHORA (heartbeat). Idempotente; renueva el timestamp en cada llamada."""
    t = (tier or "").strip().lower()
    if t not in TIERS:
        raise ValueError(f"tier invalido: {tier!r} (usa uno de {TIERS})")
    with _Mutex("modelos_vivos"):
        d = _load()
        d[t] = {"sesion": sesion or "?", "ts": _now()}
        _save(d)


def vivos(ttl_seg: int = TTL_SEG, ahora: datetime | None = None, d: dict | None = None) -> set:
    """Tiers con heartbeat dentro del TTL. ahora/d inyectables para test."""
    d = d if d is not None else _load()
    ref = ahora or datetime.now()
    out = set()
    for tier, info in d.items():
        ts = info.get("ts") if isinstance(info, dict) else None
        if not ts:
            continue
        try:
            edad = (ref - datetime.fromisoformat(ts)).total_seconds()
        except Exception:
            continue
        if 0 <= edad <= ttl_seg:
            out.add(tier)
    return out


# --------------------------------------------------------------------------- clasificador (heuristica)
# Diccionario inicial (afinable con el uso). 'opus' gana sobre 'haiku' si aparecen senales de ambos:
# nunca mandar algo de arquitectura/razonamiento a un tier barato por una palabra mecanica suelta.
_OPUS_KW = ("disen", "arquitect", "depura", "debug", "investig", "analiz", "decid", "refactor",
            "spec", "plan", "razona", "estrateg", "evalua", "compar", "audita", "review",
            "revisa codigo", "brainstorm", "disena", "propon", "porque", "trade-off", "tradeoff")
_HAIKU_KW = ("renombra", "formatea", "mueve", "mover", "lista", "listar", "busca", "buscar",
             "corre test", "correr test", "ejecuta test", "aplica", "regenera", "convierte",
             "convertir", "copia", "ordena", "traduc", "reemplaza", "renderiz", "limpia import",
             "ruff", "lint", "renombrar", "borra", "elimina", "mueve archivo")


def clasificar(titulo: str, proposito: str = "", archivos=None) -> tuple:
    """Propone (tier, razon) por heuristica. La sesion confirma o corrige (diseno hibrido D1)."""
    texto = _fold(" ".join([titulo or "", proposito or "", " ".join(archivos or [])]))
    for kw in _OPUS_KW:
        if kw in texto:
            return "opus", f"senal de razonamiento/diseno: '{kw}'"
    for kw in _HAIKU_KW:
        if kw in texto:
            return "haiku", f"senal mecanica/repetitiva: '{kw}'"
    return "sonnet", "sin senal fuerte -> tier intermedio por defecto"


# --------------------------------------------------------------------------- delegar (clasificar + encolar)
def delegar(titulo: str, proposito: str, tier: str, terminado: str = "", archivos=None,
            pruebas=None, prioridad: int = 0, creada_por: str = "",
            tiers_vivos: set | None = None) -> dict:
    """Publica la tarea en la cola para `tier` y arma el aviso para el usuario. tiers_vivos inyectable."""
    t = (tier or "").strip().lower()
    if t not in TIERS:
        raise ValueError(f"tier invalido: {tier!r} (usa uno de {TIERS})")
    tid = tareas.publicar(titulo, proposito, modelo=t, terminado=terminado, archivos=archivos,
                          pruebas=pruebas, prioridad=prioridad, creada_por=creada_por)
    vv = tiers_vivos if tiers_vivos is not None else vivos()
    worker_vivo = t in vv
    if worker_vivo:
        aviso = f"{tid} encolada para {t}; la tomara tu sesion {t} (viva)."
    else:
        aviso = f"{tid} encolada para {t}; NO hay sesion {t} abierta — abre una sesion {t} para que la tome."
    return {"id": tid, "tier": t, "worker_vivo": worker_vivo, "aviso": aviso}


# --------------------------------------------------------------------------- CLI
def _cli(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "soy":
        if len(argv) < 2:
            print("uso: soy <model-id>", file=sys.stderr); return 2
        print(tier_de(argv[1])); return 0
    if cmd == "vivos":
        vv = sorted(vivos())
        print("VIVOS: " + (", ".join(vv) if vv else "(ninguno)")); return 0
    import argparse
    p = argparse.ArgumentParser(prog="cerebro_modelo")
    sub = p.add_subparsers(dest="cmd")
    pr = sub.add_parser("registrar"); pr.add_argument("tier"); pr.add_argument("--sesion", default="")
    pc = sub.add_parser("clasificar")
    pc.add_argument("titulo"); pc.add_argument("-p", "--proposito", default="")
    pc.add_argument("--archivo", dest="archivos", action="append", default=[])
    pd = sub.add_parser("delegar")
    pd.add_argument("titulo"); pd.add_argument("-p", "--proposito", required=True)
    pd.add_argument("--tier", required=True); pd.add_argument("--terminado", default="")
    pd.add_argument("--archivo", dest="archivos", action="append", default=[])
    pd.add_argument("--prueba", dest="pruebas", action="append", default=[])
    pd.add_argument("--prioridad", type=int, default=0); pd.add_argument("--por", default="?")
    a = p.parse_args(argv)
    if a.cmd == "registrar":
        registrar(a.tier, a.sesion); print(f"OK vivo: {a.tier}"); return 0
    if a.cmd == "clasificar":
        tier, razon = clasificar(a.titulo, a.proposito, a.archivos)
        print(f"{tier}  ({razon})"); return 0
    if a.cmd == "delegar":
        r = delegar(a.titulo, a.proposito, a.tier, a.terminado, a.archivos, a.pruebas, a.prioridad, a.por)
        print(r["aviso"]); return 0
    print(f"comando desconocido: {cmd}", file=sys.stderr); return 2


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(_cli(sys.argv[1:]))
