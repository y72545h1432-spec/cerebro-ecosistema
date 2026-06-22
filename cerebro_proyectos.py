"""CEREBRO · PROYECTOS (config local — lo PERSONAL fuera del codigo).

Los proyectos de cada persona son PERSONALES: no se hardcodean ni se publican. Viven en
<.cerebro>/proyectos.local.toml (gitignored). El repo trae proyectos.example.toml como plantilla,
y cerebro_init.py puede autogenerarlo detectando los proyectos de quien clona.

Si no hay config -> listas vacias (el ecosistema funciona, solo sin proyectos registrados): el
codigo del ecosistema NUNCA depende de un proyecto concreto del autor.

Formato (TOML, requiere Python 3.11+ para leerse; sin el, degrada a vacio con aviso):
    [[proyecto]]
    nombre  = "miapp"            # identificador corto en minusculas (= area de memoria)
    ruta    = "~/miapp"          # admite ~ y rutas absolutas (/ o \\)
    que_es  = "descripcion corta"
    entrada = "CLAUDE.md"        # archivo de entrada (opcional)

API:
    cargar(config=None) -> list[dict]   # [{nombre, ruta, ruta_abs, que_es, entrada}, ...]
    nombres(config=None) -> list[str]   # nombres de proyecto (para AREAS de memoria)
    mapa_cwd(config=None) -> dict       # {ruta_abs_normalizada: nombre} para inferir por cwd
"""
from __future__ import annotations
import pathlib
import sys

CONFIG = pathlib.Path(__file__).resolve().parent / "proyectos.local.toml"


def _expand(ruta: str) -> str:
    return str(pathlib.Path(ruta.strip()).expanduser())


def _norm(ruta_abs: str) -> str:
    """Normaliza una ruta para comparar contra cwd (minusculas, backslash, sin barra final)."""
    return ruta_abs.replace("/", "\\").lower().rstrip("\\")


def cargar(config: pathlib.Path | None = None) -> list[dict]:
    cfg = config or CONFIG
    if not cfg.exists():
        return []
    try:
        import tomllib
    except ImportError:
        # No silencioso: avisa por que no se cargaron los proyectos (Python < 3.11).
        print("[cerebro_proyectos] proyectos.local.toml existe pero falta tomllib (Python 3.11+); "
              "proyectos no cargados.", file=sys.stderr)
        return []
    try:
        data = tomllib.loads(cfg.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[cerebro_proyectos] proyectos.local.toml ilegible ({e}); proyectos no cargados.",
              file=sys.stderr)
        return []
    out = []
    for p in data.get("proyecto", []):
        nombre = str(p.get("nombre", "")).strip().lower()
        if not nombre:
            continue
        ruta = str(p.get("ruta", "")).strip()
        out.append({
            "nombre": nombre,
            "ruta": ruta,
            "ruta_abs": _expand(ruta) if ruta else "",
            "que_es": str(p.get("que_es", "")).strip(),
            "entrada": str(p.get("entrada", "")).strip(),
        })
    return out


def nombres(config: pathlib.Path | None = None) -> list[str]:
    return [p["nombre"] for p in cargar(config)]


def mapa_cwd(config: pathlib.Path | None = None) -> dict:
    m = {}
    for p in cargar(config):
        if p["ruta_abs"]:
            m[_norm(p["ruta_abs"])] = p["nombre"]
    return m


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ps = cargar()
    if not ps:
        print("Sin proyectos. Copia proyectos.example.toml -> proyectos.local.toml "
              "o corre: py cerebro_init.py --confirm")
    for p in ps:
        print(f"  {p['nombre']:<24} {p['ruta_abs'] or '(sin ruta)'}  — {p['que_es']}")
