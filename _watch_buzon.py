"""Vigía nocturno: espera a que OTRA sesión deje mensajes/conocimiento nuevos y SALE (exit 0).

Lee multisesion.json en SOLO LECTURA (no consume mensajes). Hace baseline de los ids de mensajes a
agent:claude / '*' / proyectos y de la conocimiento; al detectar algo NUEVO, lo imprime y termina
(el harness me re-invoca). Heartbeat: sale igual tras ~8h por si no llega nada.
Uso: py -3 _watch_buzon.py  (en background)
"""
import json
import os
import time
from pathlib import Path

JSON = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "cerebro" / "multisesion.json"
WATCH_BOXES = ("agent:claude", "tu-proyecto-agente")          # mensajes DIRIGIDOS a mí o a tu-proyecto-agente
WATCH_TAGS = {"investigacion", "implementar", "para-claude"}  # solo deliverables de investigación
INTERVAL = 120          # s entre chequeos (cache-friendly, no urgente de noche)
MAX_ITERS = 240         # ~8h de heartbeat


def snapshot():
    try:
        d = json.loads(JSON.read_text(encoding="utf-8"))
    except Exception:
        return set(), set()
    msg_ids = set()
    for box in WATCH_BOXES:
        for m in d.get("buzon", {}).get(box, []):
            msg_ids.add(m.get("id") or f"{m.get('ts')}|{m.get('de')}")
    # conocimiento SOLO si tiene un tag relevante (filtra ruido de coordinación tipo Codex)
    con_ids = {f"{c.get('ts')}|{c.get('sesion')}|{c.get('nota','')[:40]}"
               for c in d.get("conocimiento", []) if WATCH_TAGS & set(c.get("tags", []))}
    return msg_ids, con_ids


def detail(new_msgs, new_cons):
    try:
        d = json.loads(JSON.read_text(encoding="utf-8"))
    except Exception:
        return
    for box in WATCH_BOXES:
        for m in d.get("buzon", {}).get(box, []):
            mid = m.get("id") or f"{m.get('ts')}|{m.get('de')}"
            if mid in new_msgs:
                print(f"[MSG->{box}] {m.get('agent')}/{m.get('project')}: {m.get('texto') or m.get('summary')}")
    for c in d.get("conocimiento", []):
        cid = f"{c.get('ts')}|{c.get('sesion')}|{c.get('nota','')[:40]}"
        if cid in new_cons:
            print(f"[CONOC {c.get('tags')}] {c.get('agent')}/{c.get('project')}: {c.get('nota')}")


def main():
    base_msgs, base_cons = snapshot()
    print(f"vigia activo: {len(base_msgs)} msgs base, {len(base_cons)} conoc base. Esperando novedades...")
    for _ in range(MAX_ITERS):
        time.sleep(INTERVAL)
        msgs, cons = snapshot()
        new_msgs, new_cons = msgs - base_msgs, cons - base_cons
        if new_msgs or new_cons:
            print(f"=== NOVEDAD: {len(new_msgs)} mensajes, {len(new_cons)} conocimiento nuevos ===")
            detail(new_msgs, new_cons)
            return
    print("=== heartbeat: 8h sin novedades, salgo (re-evaluar) ===")


if __name__ == "__main__":
    main()
