#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cerebro_skill_dispatch.py — Metrica de DISPARO de skills (precision/recall/F1).
Backlog II_SKILLS #13 (la metrica base de la que dependen routing, poda y desambiguacion).

Modelo de datos: un .jsonl append-only en %LOCALAPPDATA%\\cerebro\\skill_dispatch_log.jsonl.
Cada linea es un evento:
  {"ts","skill","tarea","correcta":true|false|null,"tipo":"disparo"|"falso_negativo"}

- "disparo": una skill SE invoco. El hook PreToolUse lo registra con correcta=null (pendiente
  de anotar). Despues anotas a mano si fue correcta (true) o un falso positivo (false).
- "falso_negativo": una skill DEBIO dispararse y no lo hizo. No hay hook que lo capture
  (un no-evento no se observa); se anota a mano al cerrar sesion. Cuenta para el recall.

F1 por skill: TP=disparo&correcta, FP=disparo&!correcta, FN=falso_negativo.
  precision=TP/(TP+FP)  recall=TP/(TP+FN)  F1=2PR/(P+R). <0.7 => reescribir description.

CLI:
  py cerebro_skill_dispatch.py log <skill> --tarea "..." [--correcta true|false]
  py cerebro_skill_dispatch.py miss <skill> --tarea "..."     # falso negativo
  py cerebro_skill_dispatch.py anotar <n> true|false          # fija 'correcta' de la linea n
  py cerebro_skill_dispatch.py pendientes                     # disparos sin anotar
  py cerebro_skill_dispatch.py f1 [--min 0]                   # reporte P/R/F1 por skill
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict

_BASE = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
LOG = os.path.join(_BASE, "cerebro", "skill_dispatch_log.jsonl")


def _ensure():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)


def _append(ev):
    _ensure()
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def _leer():
    if not os.path.isfile(LOG):
        return []
    out = []
    with open(LOG, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
    return out


def log_disparo(skill, tarea="", correcta=None):
    """Llamable por el hook. Registra que una skill se invoco."""
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "skill": skill,
             "tarea": tarea[:200], "correcta": correcta, "tipo": "disparo"})


def cmd_log(a):
    correcta = {"true": True, "false": False}.get((a.correcta or "").lower(), None)
    log_disparo(a.skill, a.tarea or "", correcta)
    print(f"[log] disparo {a.skill} correcta={correcta}")


def cmd_miss(a):
    _append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "skill": a.skill,
             "tarea": (a.tarea or "")[:200], "correcta": False, "tipo": "falso_negativo"})
    print(f"[log] falso_negativo {a.skill}")


def cmd_anotar(a):
    evs = _leer()
    pend = [i for i, e in enumerate(evs) if e.get("tipo") == "disparo" and e.get("correcta") is None]
    if a.n < 0 or a.n >= len(pend):
        print(f"indice fuera de rango (hay {len(pend)} pendientes)"); return
    idx = pend[a.n]
    evs[idx]["correcta"] = (a.valor.lower() == "true")
    with open(LOG, "w", encoding="utf-8") as f:
        for e in evs:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"[anotado] {evs[idx]['skill']} -> correcta={evs[idx]['correcta']}")


def cmd_pendientes(_a):
    pend = [e for e in _leer() if e.get("tipo") == "disparo" and e.get("correcta") is None]
    if not pend:
        print("(sin disparos pendientes de anotar)"); return
    for i, e in enumerate(pend):
        print(f"  [{i}] {e['ts']} {e['skill']:<26} {e.get('tarea','')[:50]}")
    print(f"\nAnota con: py cerebro_skill_dispatch.py anotar <i> true|false")


def cmd_f1(a):
    evs = _leer()
    if not evs:
        print("Log vacio. Aun no hay disparos registrados.\n"
              f"(esperado en {LOG})"); return
    tp = defaultdict(int); fp = defaultdict(int); fn = defaultdict(int); pend = defaultdict(int)
    for e in evs:
        sk = e["skill"]
        if e.get("tipo") == "falso_negativo":
            fn[sk] += 1
        elif e.get("correcta") is True:
            tp[sk] += 1
        elif e.get("correcta") is False:
            fp[sk] += 1
        else:
            pend[sk] += 1
    skills = sorted(set(tp) | set(fp) | set(fn) | set(pend))
    print(f"{'skill':<28}{'TP':>4}{'FP':>4}{'FN':>4}{'pend':>6}{'prec':>7}{'rec':>7}{'F1':>7}  flag")
    print("-" * 78)
    for sk in skills:
        t, f_, n = tp[sk], fp[sk], fn[sk]
        prec = t / (t + f_) if (t + f_) else 0.0
        rec = t / (t + n) if (t + n) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        if a.min and (t + f_ + n) < a.min:
            continue
        flag = "  <- reescribir description" if (t + f_ + n) >= 5 and f1 < 0.7 else ""
        print(f"{sk:<28}{t:>4}{f_:>4}{n:>4}{pend[sk]:>6}{prec:>7.2f}{rec:>7.2f}{f1:>7.2f}{flag}")
    total_pend = sum(pend.values())
    if total_pend:
        print(f"\n{total_pend} disparos PENDIENTES de anotar (no cuentan aun). "
              f"`pendientes` para verlos.")
    print(f"\nMuestra util a partir de >=5 eventos/skill. Log: {LOG}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("log"); p.add_argument("skill"); p.add_argument("--tarea"); p.add_argument("--correcta"); p.set_defaults(fn=cmd_log)
    p = sub.add_parser("miss"); p.add_argument("skill"); p.add_argument("--tarea"); p.set_defaults(fn=cmd_miss)
    p = sub.add_parser("anotar"); p.add_argument("n", type=int); p.add_argument("valor"); p.set_defaults(fn=cmd_anotar)
    p = sub.add_parser("pendientes"); p.set_defaults(fn=cmd_pendientes)
    p = sub.add_parser("f1"); p.add_argument("--min", type=int, default=0); p.set_defaults(fn=cmd_f1)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
