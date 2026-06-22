#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cerebro_skills_audit.py — Linter de descriptions de skills. Backlog II_SKILLS #1.
Read-only: NO modifica skills. Marca anti-patrones de autoria/triggering:
  - description ausente / fuera de rango (<200 infra-dispara, >1536 excede limite)
  - sin trigger imperativo explicito (Use when / Usa cuando / Use al... / Dispara...)
  - clusters near-duplicate sin 'NOT FOR' (señal de posible colision de disparo)
Uso: py cerebro_skills_audit.py [--root DIR]
"""
import argparse
import os
import re

DEF_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "skills")
# Trigger imperativo al inicio de una description bien escrita (ES/EN, con o sin acento).
TRIG = re.compile(
    r"\b(use|usa|[uú]sa(la|lo)|dispara(la|lo)|when the user|cuando el usuario|when asked)\b",
    re.I)
# Clusters near-duplicate conocidos (deberian llevar NOT FOR cruzado).
CLUSTERS = {
    "video": {"video-editing", "produccion-audiovisual", "video-marca", "youtube-growth"},
    "negocio": {"marketing-digital", "negocios", "ecommerce", "agencia-ia"},
}


def desc_de(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"(?ms)^description:\s*(?:>-?\s*)?(.+?)(?=^\w[\w-]*:|^---)", t)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=DEF_ROOT)
    a = ap.parse_args()
    en_cluster = {s: c for c, ss in CLUSTERS.items() for s in ss}
    print(f"{'skill':<26}{'len':>5}{'trig':>6}{'NOTFOR':>8}  notas")
    print("-" * 74)
    problemas = 0
    for d in sorted(os.listdir(a.root)):
        p = os.path.join(a.root, d, "SKILL.md")
        if not os.path.isfile(p):
            continue
        desc = desc_de(p)
        L = len(desc)
        trig = bool(TRIG.search(desc))
        nf = "NOT FOR" in desc
        notas = []
        if not desc:
            notas.append("SIN description")
        else:
            if L < 200:
                notas.append("corta(infra-dispara?)")
            if L > 1536:
                notas.append("EXCEDE 1536")
            if not trig:
                notas.append("sin trigger imperativo")
            if d in en_cluster and not nf:
                notas.append(f"cluster '{en_cluster[d]}' sin NOT FOR")
        if notas:
            problemas += 1
        print(f"{d:<26}{L:>5}{'si' if trig else 'NO':>6}{'si' if nf else '-':>8}  "
              f"{', '.join(notas)}")
    print(f"\n{problemas} skill(s) con notas. (linter de autoria/triggering — regla #1)")


if __name__ == "__main__":
    main()
