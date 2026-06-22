#!/usr/bin/env python3
"""cerebro_grafo.py - router de grafo de codigo on-demand (lo mejor de dos mundos).

Dos verbos, cada herramienta en su fortaleza, sin daemon / sin tocar CLAUDE.md / sin install:

  arquitectura <ruta> [--keep]   Mapa de un repo grande desconocido (god nodes, comunidades,
                                 ciclos de import). Por dentro: Graphify (uvx, telemetria off);
                                 imprime GRAPH_REPORT.md y BORRA graphify-out/ (incluido el
                                 graph.html inutil) salvo --keep. 36 lenguajes.

  simbolo <nombre> <ruta>        Donde se define / quien llama / a que llama. 100% Python `ast`
                                 nativo (stdlib): sin Node, sin daemon, sin terceros. SOLO .py.

Veredicto y porque de este diseno: memoria [[reference-graphify-evaluado]].
"""
from __future__ import annotations

import argparse
import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# simbolo  -  consulta nativa con ast (sin terceros)
# --------------------------------------------------------------------------- #


def _call_name(func: ast.AST) -> str | None:
    """Nombre invocado en un nodo Call: foo() -> 'foo', obj.foo() -> 'foo'."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


class _Scanner(ast.NodeVisitor):
    """Recorre un AST acumulando definiciones, llamadores y llamadas-internas del objetivo."""

    def __init__(self, target: str, rel: str):
        self.target = target
        self.rel = rel
        self.scope: list[tuple[str, str, int]] = []  # pila (kind, name, lineno)
        self.defs: list[tuple[str, int, str, str]] = []      # rel, line, kind, cualificado
        self.callers: list[tuple[str, int, str]] = []        # rel, line, contexto
        self.calls_made: set[str] = set()                    # nombres llamados dentro del target

    def _enter(self, node, kind: str):
        if node.name == self.target:
            qual = ".".join(s[1] for s in self.scope + [(kind, node.name, node.lineno)])
            self.defs.append((self.rel, node.lineno, kind, qual))
        self.scope.append((kind, node.name, node.lineno))
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = lambda self, n: self._enter(n, "def")          # noqa: E731
    visit_AsyncFunctionDef = lambda self, n: self._enter(n, "async def")  # noqa: E731
    visit_ClassDef = lambda self, n: self._enter(n, "class")           # noqa: E731

    def visit_Call(self, node: ast.Call):
        name = _call_name(node.func)
        if name == self.target:
            ctx = self.scope[-1][1] if self.scope else "<modulo>"
            self.callers.append((self.rel, node.lineno, ctx))
        # llamadas hechas DENTRO del cuerpo del target (mini blast-radius hacia afuera)
        if name and any(k != "class" and n == self.target for k, n, _ in self.scope):
            self.calls_made.add(name)
        self.generic_visit(node)


def simbolo(nombre: str, ruta: str) -> int:
    base = Path(ruta).resolve()
    if not base.exists():
        print(f"[error] ruta no existe: {base}", file=sys.stderr)
        return 2
    pys = [base] if base.is_file() else sorted(base.rglob("*.py"))
    defs, callers, calls_made = [], [], set()
    leidos = 0
    for py in pys:
        try:
            src = py.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(py))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        leidos += 1
        rel = os.path.relpath(py, base) if base.is_dir() else py.name
        sc = _Scanner(nombre, rel)
        sc.visit(tree)
        defs += sc.defs
        callers += sc.callers
        calls_made |= sc.calls_made

    print(f"SIMBOLO: {nombre}   ({leidos} archivos .py escaneados bajo {base})")
    print(f"\n== Definiciones ({len(defs)}) ==")
    if defs:
        for rel, line, kind, qual in defs:
            print(f"  {rel}:{line}  {kind} {qual}")
    else:
        print("  (ninguna - simbolo no definido aqui, o es importado de fuera / no-Python)")
    print(f"\n== Quien llama a `{nombre}` ({len(callers)}) ==")
    if callers:
        for rel, line, ctx in sorted(callers):
            print(f"  {rel}:{line}  dentro de {ctx}")
    else:
        print("  (sin llamadores en este arbol)")
    if calls_made:
        print(f"\n== `{nombre}` llama a (dentro de su cuerpo) ==")
        print("  " + ", ".join(sorted(calls_made)))
    return 0


# --------------------------------------------------------------------------- #
# arquitectura  -  delega en Graphify on-demand, limpia detras
# --------------------------------------------------------------------------- #


def arquitectura(ruta: str, keep: bool = False) -> int:
    base = Path(ruta).resolve()
    if not base.is_dir():
        print(f"[error] ruta no es carpeta: {base}", file=sys.stderr)
        return 2
    if shutil.which("uvx") is None:
        print("[error] falta `uvx` (instala uv) - necesario para Graphify on-demand", file=sys.stderr)
        return 3

    env = dict(os.environ, DO_NOT_TRACK="1", GRAPHIFY_TELEMETRY="0")
    out = base / "graphify-out"
    preexistente = out.exists()  # no pisar/borrar un graphify-out que el usuario ya tuviera
    try:
        print(f"[arquitectura] indexando {base} con Graphify (puede tardar ~segundos)...", file=sys.stderr)
        r = subprocess.run(
            ["uvx", "--from", "graphifyy", "graphify", "update", "."],
            cwd=str(base), env=env, capture_output=True, text=True,
        )
        report = out / "GRAPH_REPORT.md"
        if not report.exists():
            print("[error] Graphify no genero GRAPH_REPORT.md", file=sys.stderr)
            sys.stderr.write(r.stdout + r.stderr)
            return 1
        print(report.read_text(encoding="utf-8"))
        if keep:
            print(f"\n[grafo conservado en {out}]  (graph.json / graph.html ahi)", file=sys.stderr)
        return 0
    finally:
        # esconder la basura SIEMPRE (incl. graph.html 227KB), pase lo que pase con el print
        if not keep and not preexistente:
            shutil.rmtree(out, ignore_errors=True)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # Windows: consola cp1252 revienta con Unicode (flechas)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    p = argparse.ArgumentParser(prog="cerebro_grafo", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("arquitectura", help="mapa de arquitectura (Graphify on-demand, 36 lenguajes)")
    pa.add_argument("ruta")
    pa.add_argument("--keep", action="store_true", help="no borrar graphify-out (conserva graph.json/html)")

    ps = sub.add_parser("simbolo", help="donde se define / quien llama (Python ast nativo, solo .py)")
    ps.add_argument("nombre")
    ps.add_argument("ruta")

    a = p.parse_args(argv)
    if a.cmd == "arquitectura":
        return arquitectura(a.ruta, a.keep)
    return simbolo(a.nombre, a.ruta)


if __name__ == "__main__":
    raise SystemExit(main())
