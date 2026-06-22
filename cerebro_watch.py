r"""Watcher local opcional del cerebro multi-agente.

Solo lectura. No ejecuta acciones, no abre red y no queda como daemon salvo que
quien lo lance lo mantenga corriendo. Lee el log append-only eventos.jsonl.

Uso:
    python -X utf8 ~\.cerebro\cerebro_watch.py --once
    python -X utf8 ~\.cerebro\cerebro_watch.py --follow --seconds 60
"""
from __future__ import annotations
import argparse, json, os, pathlib, time, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core  # base comun (STATE_DIR)

STATE_DIR = core.STATE_DIR
EVENT_LOG = STATE_DIR / "eventos.jsonl"


def _read_lines(path: pathlib.Path, offset: int = 0) -> tuple[int, list[dict]]:
    if not path.exists():
        return offset, []
    items = []
    with path.open("r", encoding="utf-8") as f:
        f.seek(offset)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except ValueError:
                continue
        return f.tell(), items


def _format(e: dict) -> str:
    msg = e.get("summary") or e.get("detalle") or ""
    meta = []
    if e.get("message_type"):
        meta.append(e["message_type"])
    if e.get("priority") and e["priority"] != "normal":
        meta.append(e["priority"])
    if e.get("requires_ack"):
        meta.append("ack")
    suffix = f" [{' '.join(meta)}]" if meta else ""
    return f"{e.get('ts','?')} ({e.get('agent','?')}/{e.get('project','?')}) {e.get('type','event')}{suffix}: {msg}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Watcher local de eventos del cerebro multi-agente.")
    ap.add_argument("--once", action="store_true", help="Imprime eventos recientes y termina.")
    ap.add_argument("--follow", action="store_true", help="Sigue leyendo eventos nuevos.")
    ap.add_argument("--seconds", type=int, default=60, help="Duracion maxima en modo follow.")
    ap.add_argument("--interval", type=float, default=2.0, help="Intervalo de lectura en segundos.")
    ap.add_argument("--last", type=int, default=30, help="Cantidad de eventos recientes en --once.")
    ap.add_argument("--agent", default="", help="Filtrar por agente.")
    ap.add_argument("--project", default="", help="Filtrar por proyecto.")
    ap.add_argument("--type", default="", help="Filtrar por tipo de evento.")
    args = ap.parse_args()

    if args.interval < 1:
        args.interval = 1
    if not args.once and not args.follow:
        args.once = True

    offset, items = _read_lines(EVENT_LOG, 0)

    def keep(e: dict) -> bool:
        if args.agent and e.get("agent") != args.agent:
            return False
        if args.project and e.get("project") != args.project:
            return False
        if args.type and e.get("type") != args.type:
            return False
        return True

    if args.once:
        for e in [x for x in items if keep(x)][-args.last:]:
            print(_format(e))
        return 0

    for e in [x for x in items if keep(x)][-args.last:]:
        print(_format(e))
    end = time.time() + max(1, args.seconds)
    while time.time() < end:
        time.sleep(args.interval)
        if EVENT_LOG.exists() and EVENT_LOG.stat().st_size < offset:
            offset = 0
        offset, new_items = _read_lines(EVENT_LOG, offset)
        for e in new_items:
            if keep(e):
                print(_format(e), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
