#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cerebro_skills_diff.py — Detecta DRIFT entre las skills de Claude (~/.claude/skills)
y las de Codex (~/.agents/skills). Backlog II_SKILLS #23.

Las 3 divergencias ESPERADAS (cosmeticas/de runtime) se normalizan antes de comparar, para
que el reporte muestre solo el drift REAL (instrucciones que cambiaron de fondo). No daemon:
se lanza a mano. No escribe nada salvo el reporte si se pasa --out.

Uso:
  py cerebro_skills_diff.py                 # reporte a stdout
  py cerebro_skills_diff.py --out informe.md
  py cerebro_skills_diff.py --raw           # diff SIN normalizar (incluye lo cosmetico)
"""
import argparse
import difflib
import os
import re

HOME = os.path.expanduser("~")
ROOT_CLAUDE = os.path.join(HOME, ".claude", "skills")
ROOT_AGENTS = os.path.join(HOME, ".agents", "skills")
ALLOW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills_drift_allow.txt")


def allow_listadas():
    """Slugs cuyo drift Claude<->Codex es intencional (adaptacion de runtime)."""
    if not os.path.isfile(ALLOW):
        return set()
    out = set()
    for ln in open(ALLOW, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#"):
            out.add(ln)
    return out

# Sustituciones de runtime ESPERADAS (Claude <-> Codex). Se neutralizan a un token comun
# para no contar como drift lo que es solo adaptacion de runtime. Case-INSENSITIVE: queremos
# ignorar TODA mencion del runtime (claude-api, claude.ai, @claude, .claude/agents...) y dejar
# solo el drift de instrucciones de fondo. Orden importa (los mas especificos primero).
NEUTRALIZA = [
    (r"CLAUDE\.md", "<ADAPTER>"),
    (r"AGENTS\.md", "<ADAPTER>"),
    (r"\.claude\b", "<DOTRT>"),
    (r"\.agents\b", "<DOTRT>"),
    (r"\.Codex\b", "<DOTRT>"),
    (r"Claude Code", "<RUNTIME>"),
    (r"\bCodex\b", "<RUNTIME>"),
    (r"\bClaude\b", "<RUNTIME>"),  # IGNORECASE -> tambien claude-api, claude.ai, @claude
]
_RX = [(re.compile(p, re.IGNORECASE), r) for p, r in NEUTRALIZA]


def skills_en(root):
    """slug -> ruta de SKILL.md, para cada subcarpeta con SKILL.md."""
    out = {}
    if not os.path.isdir(root):
        return out
    for nombre in sorted(os.listdir(root)):
        sk = os.path.join(root, nombre, "SKILL.md")
        if os.path.isfile(sk):
            out[nombre] = sk
    return out


def normaliza(texto):
    for rx, rep in _RX:
        texto = rx.sub(rep, texto)
    return texto


def leer(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def comparar(raw=False):
    c = skills_en(ROOT_CLAUDE)
    a = skills_en(ROOT_AGENTS)
    solo_c = sorted(set(c) - set(a))
    solo_a = sorted(set(a) - set(c))
    comunes = sorted(set(c) & set(a))

    allow = allow_listadas()
    drift_real, solo_cosmetico, drift_intencional = [], [], []
    for slug in comunes:
        tc, ta = leer(c[slug]), leer(a[slug])
        if tc == ta:
            continue  # identicas
        # Si tras neutralizar runtime siguen difiriendo -> drift REAL
        nc, na = normaliza(tc), normaliza(ta)
        if (nc == na) and not raw:
            solo_cosmetico.append(slug)
        elif slug in allow and not raw:
            drift_intencional.append(slug)
        else:
            base = na if not raw else ta
            top = nc if not raw else tc
            difflines = list(difflib.unified_diff(
                base.splitlines(), top.splitlines(),
                fromfile=f"agents/{slug}", tofile=f"claude/{slug}", lineterm="", n=1))
            drift_real.append((slug, difflines))
    return solo_c, solo_a, comunes, drift_real, solo_cosmetico, drift_intencional


def render(solo_c, solo_a, comunes, drift_real, solo_cosmetico, drift_intencional, raw):
    L = []
    L.append("# Drift de skills Claude (~/.claude/skills) vs Codex (~/.agents/skills)")
    L.append("")
    L.append(f"- Comunes: **{len(comunes)}** · solo-Claude: **{len(solo_c)}** · solo-Codex: **{len(solo_a)}**")
    L.append(f"- Con DRIFT real (mas alla de runtime): **{len(drift_real)}** · solo cosmetico: "
             f"**{len(solo_cosmetico)}** · drift intencional (allow-list): **{len(drift_intencional)}**")
    L.append("")
    if drift_intencional:
        L.append("## Drift INTENCIONAL (allow-listed — adaptacion de runtime, OK)")
        L.append(", ".join(f"`{s}`" for s in drift_intencional))
        L.append("")
    if solo_c:
        L.append("## Solo en Claude (faltan en Codex)")
        L.append(", ".join(f"`{s}`" for s in solo_c))
        L.append("")
    if solo_a:
        L.append("## Solo en Codex (faltan en Claude)")
        L.append(", ".join(f"`{s}`" for s in solo_a))
        L.append("")
    if solo_cosmetico:
        L.append("## Difieren SOLO en runtime (cosmetico, OK)")
        L.append(", ".join(f"`{s}`" for s in solo_cosmetico))
        L.append("")
    L.append("## DRIFT REAL (revisar — instrucciones de fondo divergen)" if not raw
             else "## DIFF crudo (incluye runtime)")
    if not drift_real:
        L.append("_(ninguno)_")
    for slug, dl in drift_real:
        L.append(f"### `{slug}`")
        L.append("```diff")
        L.extend(dl[:60])  # acota
        if len(dl) > 60:
            L.append(f"... (+{len(dl) - 60} lineas)")
        L.append("```")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--raw", action="store_true")
    args = ap.parse_args()
    res = comparar(raw=args.raw)
    txt = render(*res, raw=args.raw)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"reporte -> {args.out}")
    else:
        print(txt)


if __name__ == "__main__":
    main()
