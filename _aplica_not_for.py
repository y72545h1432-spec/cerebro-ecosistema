# -*- coding: utf-8 -*-
"""One-off idempotente: agrega ' NOT FOR: ...' a la linea description de skills near-duplicate.
Backlog II_SKILLS #18. Inyecta un token negativo que baja el score para el intent ajeno, sin
tocar el cuerpo. Idempotente (no re-agrega si ya hay 'NOT FOR:'). Solo skills ~/.claude/skills."""
import os
import re

import sys
ROOT = (sys.argv[1] if len(sys.argv) > 1
        else os.path.join(os.path.expanduser("~"), ".claude", "skills"))

# slug -> clausula NOT FOR (<=2 hermanas mas confundidas), en el idioma de la description.
EXCL = {
    "video-editing":
        "NOT FOR shooting/lighting/camera craft (use produccion-audiovisual) nor tu-tienda-branded video (use video-marca).",
    "produccion-audiovisual":
        "NOT FOR editing/montage/retention craft (use video-editing) nor channel strategy (use youtube-growth).",
    "video-marca":
        "NOT FOR generic non-tu-tienda editing (use video-editing) nor on-set filming craft (use produccion-audiovisual).",
    "youtube-growth":
        "NOT FOR editing/assembling the video itself (use video-editing) nor on-set filming (use produccion-audiovisual).",
    "marketing-digital":
        "NOT FOR business models/entrepreneurship (use negocios) nor selling AI-agency services (use agencia-ia).",
    "negocios":
        "NOT FOR operational ads/marketing (use marketing-digital) nor dropshipping/Shopify (use ecommerce).",
    "ecommerce":
        "NOT FOR general marketing creatives/ads (use marketing-digital) nor broad business models (use negocios).",
    "agencia-ia":
        "NOT FOR your own operational marketing (use marketing-digital) nor general business models (use negocios).",
}

LIMITE = 1536  # limite practico de description


def main():
    for slug, clausula in EXCL.items():
        path = os.path.join(ROOT, slug, "SKILL.md")
        if not os.path.isfile(path):
            print(f"  ! falta {slug}"); continue
        txt = open(path, encoding="utf-8").read()
        m = re.search(r"^(description:\s*)(.+)$", txt, re.M)
        if not m:
            print(f"  ! sin description {slug}"); continue
        desc = m.group(2)
        if "NOT FOR" in desc:
            print(f"  = {slug} (ya tiene NOT FOR)"); continue
        nueva = desc.rstrip()
        if not nueva.endswith("."):
            nueva += "."
        nueva = f"{nueva} {clausula}"
        if len(nueva) > LIMITE:
            print(f"  ! {slug} excederia {LIMITE} ({len(nueva)}) -> NO modificado"); continue
        txt2 = txt[:m.start(2)] + nueva + txt[m.end(2):]
        open(path, "w", encoding="utf-8", newline="\n").write(txt2)
        print(f"  + {slug} (+{len(clausula)} chars, total desc={len(nueva)})")


if __name__ == "__main__":
    main()
