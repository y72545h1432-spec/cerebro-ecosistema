#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cerebro_skills_sync.py — Copia una skill de un runtime a otro aplicando sustitucion
direccional de tokens de runtime. Backlog II_SKILLS #25. NO daemon (se lanza a mano).

Mantiene el invariante de sincronizacion (ver cerebro_skills_diff.py #23): el catalogo de
Claude (~/.claude/skills) y Codex (~/.agents/skills) deben converger salvo skills scoped a
proyecto a proposito. Solo sustituye tokens INEQUIVOCOS de runtime (rutas/adaptador), NO el
nombre 'Claude'/'Codex' en prosa (eso puede requerir adaptacion humana -> se avisa).

Uso:
  py cerebro_skills_sync.py <slug> --dir claude2codex|codex2claude [--dry]
"""
import argparse
import os
import shutil

HOME = os.path.expanduser("~")
ROOT_CLAUDE = os.path.join(HOME, ".claude", "skills")
ROOT_AGENTS = os.path.join(HOME, ".agents", "skills")

# Sustituciones INEQUIVOCAS por direccion (token -> token). Solo rutas y adaptador.
SUBS = {
    "claude2codex": [("CLAUDE.md", "AGENTS.md"), (".claude", ".agents")],
    "codex2claude": [("AGENTS.md", "CLAUDE.md"), (".agents", ".claude")],
}
# Tokens en prosa que pueden necesitar adaptacion HUMANA (no se tocan; se reporta su presencia).
AVISAR = {
    "claude2codex": ["general-purpose", "Claude Code", "Task tool"],
    "codex2claude": ["AGENTS.md", "Codex"],
}
TEXTO = {".md", ".txt", ".py"}


def sync(slug, direction, dry):
    src_root, dst_root = (ROOT_CLAUDE, ROOT_AGENTS) if direction == "claude2codex" else (ROOT_AGENTS, ROOT_CLAUDE)
    src = os.path.join(src_root, slug)
    dst = os.path.join(dst_root, slug)
    if not os.path.isdir(src):
        print(f"  ! no existe origen: {src}"); return
    if os.path.isdir(dst):
        print(f"  ! destino YA existe (no sobreescribo): {dst}"); return
    subs = SUBS[direction]
    avisos = set()
    archivos = []
    for dirpath, _dirs, files in os.walk(src):
        for fn in files:
            sp = os.path.join(dirpath, fn)
            rel = os.path.relpath(sp, src)
            dp = os.path.join(dst, rel)
            ext = os.path.splitext(fn)[1].lower()
            archivos.append((sp, dp, ext))
            if ext in TEXTO:
                txt = open(sp, encoding="utf-8", errors="replace").read()
                for tok in AVISAR[direction]:
                    if tok in txt:
                        avisos.add(f"{rel}: contiene '{tok}'")
    print(f"  {slug}: {len(archivos)} archivo(s) {src_root.split(os.sep)[-2]}->{dst_root.split(os.sep)[-2]}"
          f"{' [DRY]' if dry else ''}")
    if not dry:
        for sp, dp, ext in archivos:
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            if ext in TEXTO:
                txt = open(sp, encoding="utf-8", errors="replace").read()
                for a, b in subs:
                    txt = txt.replace(a, b)
                open(dp, "w", encoding="utf-8", newline="\n").write(txt)
            else:
                shutil.copy2(sp, dp)
    for a in sorted(avisos):
        print(f"      ⚠ adaptacion humana posible -> {a}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--dir", required=True, choices=list(SUBS))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    sync(a.slug, a.dir, a.dry)


if __name__ == "__main__":
    main()
