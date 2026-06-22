"""cerebro_init.py — configura el ecosistema para QUIEN clona el repo (auto-config de proyectos).

Detecta tus proyectos automaticamente (carpetas con CLAUDE.md / AGENTS.md / .git) y los registra en
proyectos.local.toml (el archivo PERSONAL, gitignored). Si no encuentra nada, deja instrucciones para
crear uno a mano. Es IDEMPOTENTE y NO destructivo: nunca pisa proyectos ya registrados; sin --confirm
solo MUESTRA lo que haria (dry-run).

SALUD DEL PC: avisa si un proyecto vive dentro de una carpeta que se sincroniza a la nube
(OneDrive / Dropbox / Google Drive / iCloud) y recomienda sacarlo, porque la sync en caliente puede
bloquear o corromper archivos de trabajo.

USO:
    py cerebro_init.py                 # detecta y MUESTRA lo que registraria (dry-run)
    py cerebro_init.py --confirm       # escribe/actualiza proyectos.local.toml
    py cerebro_init.py --raiz <dir>    # escanea ademas otra carpeta (repetible)
"""
from __future__ import annotations
import pathlib
import sys

import cerebro_proyectos as proy

CONFIG = pathlib.Path(__file__).resolve().parent / "proyectos.local.toml"
EJEMPLO = pathlib.Path(__file__).resolve().parent / "proyectos.example.toml"

# Marcas de proyecto: una carpeta es "proyecto" si contiene alguno de estos.
MARCAS = ("CLAUDE.md", "AGENTS.md", ".git")
# Carpetas que NO son proyectos (ruido del sistema / dependencias).
IGNORAR = {".cerebro", ".claude", ".git", ".cache", ".config", ".vscode", ".idea",
           "node_modules", "__pycache__", ".venv", "venv", "env",
           "appdata", "application data", "windows", "program files", "program files (x86)",
           "programdata", "$recycle.bin", "recovery", "intel", "perflogs",
           "default", "default user", "all users", "public", "saved games",
           "desktop", "downloads", "music", "pictures", "videos", "favorites",
           "contacts", "links", "searches", "3d objects"}
# Segmentos de ruta que indican sincronizacion a la nube (salud del PC).
NUBE = ("onedrive", "dropbox", "google drive", "googledrive", "google_drive", "icloud", "creative cloud")


def _es_nube(ruta: pathlib.Path) -> bool:
    partes = [p.lower() for p in ruta.parts]
    return any(any(n in p for n in NUBE) for p in partes)


def _entrada(d: pathlib.Path) -> str:
    for m in ("CLAUDE.md", "AGENTS.md"):
        if (d / m).exists():
            return m
    return ""


def _que_es(d: pathlib.Path) -> str:
    """Primera linea util del CLAUDE.md/AGENTS.md (titulo) como descripcion, si la hay."""
    for m in ("CLAUDE.md", "AGENTS.md", "README.md"):
        f = d / m
        if not f.exists():
            continue
        try:
            for ln in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                t = ln.strip().lstrip("#").strip()
                if t:
                    return t[:80]
        except OSError:
            pass
    return ""


def _es_proyecto(d: pathlib.Path) -> bool:
    if not d.is_dir() or d.name.lower() in IGNORAR or d.name.startswith("."):
        return False
    return any((d / m).exists() for m in MARCAS)


def _raices(extra: list[pathlib.Path]) -> list[pathlib.Path]:
    """Carpetas cuyos hijos directos se inspeccionan en busca de proyectos."""
    home = pathlib.Path.home()
    cand = [home]
    # raiz del disco del home (p.ej. C:\) para proyectos colgados de la raiz
    cand.append(pathlib.Path(home.anchor) if home.anchor else home)
    # carpetas comunes (incluida la nube: las detectamos para AVISAR, no para recomendar)
    for sub in ("OneDrive", "Documents", "Documentos", "Projects", "Proyectos", "dev", "code", "src"):
        p = home / sub
        if p.exists():
            cand.append(p)
            for hijo in ("Documents", "Documentos"):  # subcarpeta Documentos dentro de la nube, etc.
                if (p / hijo).exists():
                    cand.append(p / hijo)
    cand.extend(extra)
    # dedupe conservando orden
    vistos, out = set(), []
    for c in cand:
        k = str(c).lower()
        if k not in vistos and c.exists():
            vistos.add(k)
            out.append(c)
    return out


def detectar(extra: list[pathlib.Path]) -> list[dict]:
    hallados: dict[str, dict] = {}
    cerebro = pathlib.Path(__file__).resolve().parent
    for raiz in _raices(extra):
        try:
            hijos = sorted(raiz.iterdir())
        except OSError:
            continue
        for d in hijos:
            try:
                if not _es_proyecto(d):
                    continue
            except OSError:
                continue
            if d.resolve() == cerebro:        # el propio hub no es un proyecto
                continue
            clave = str(d.resolve()).lower()
            if clave in hallados:
                continue
            hallados[clave] = {
                "nombre": d.name.lower(),
                "ruta_abs": str(d.resolve()),
                "que_es": _que_es(d),
                "entrada": _entrada(d),
                "nube": _es_nube(d.resolve()),
            }
    return list(hallados.values())


def _ruta_toml(ruta_abs: str) -> str:
    """Ruta para el TOML: ~ si cuelga del home; forward-slash para no escapar backslashes."""
    home = str(pathlib.Path.home())
    r = ruta_abs
    if r.lower().startswith(home.lower()):
        r = "~" + r[len(home):]
    return r.replace("\\", "/")


def _serializar(proyectos: list[dict]) -> str:
    lineas = ["# proyectos.local.toml — TUS proyectos (PERSONAL, NO se versiona; esta en .gitignore).",
              "# Generado/actualizado por cerebro_init.py. Editable a mano.", ""]
    for p in proyectos:
        lineas.append("[[proyecto]]")
        lineas.append(f'nombre  = "{p["nombre"]}"')
        lineas.append(f'ruta    = "{_ruta_toml(p.get("ruta_abs") or p.get("ruta", ""))}"')
        lineas.append(f'que_es  = "{(p.get("que_es", "") or "").replace(chr(34), chr(39))}"')
        lineas.append(f'entrada = "{p.get("entrada", "")}"')
        lineas.append("")
    return "\n".join(lineas)


def main(argv: list) -> int:
    confirm = "--confirm" in argv
    extra = []
    it = iter(argv)
    for a in it:
        if a == "--raiz":
            try:
                extra.append(pathlib.Path(next(it)).expanduser())
            except StopIteration:
                break

    existentes = proy.cargar()
    nombres_ex = {p["nombre"] for p in existentes}
    rutas_ex = {proy._norm(p["ruta_abs"]) for p in existentes if p["ruta_abs"]}

    detectados = detectar(extra)
    nuevos = [d for d in detectados
              if d["nombre"] not in nombres_ex and proy._norm(d["ruta_abs"]) not in rutas_ex]

    print(f"Proyectos ya registrados: {len(existentes)}")
    print(f"Detectados en disco: {len(detectados)}  ·  NUEVOS a registrar: {len(nuevos)}")
    if not detectados and not existentes:
        print("\nNo encontre proyectos. Para crear uno:")
        print(f"  1) copia {EJEMPLO.name} -> {CONFIG.name} y edita tus proyectos a mano, o")
        print("  2) crea una carpeta de proyecto con un CLAUDE.md (o AGENTS.md) y vuelve a correr esto.")
        print("  Estructura recomendada: ESTRUCTURA_PROYECTOS.md")
        return 0

    nube = [d for d in nuevos if d["nube"]]
    for d in nuevos:
        flag = "  ⚠ EN LA NUBE (recomiendo sacarlo de OneDrive/Dropbox)" if d["nube"] else ""
        print(f"  + {d['nombre']:<22} {_ruta_toml(d['ruta_abs'])}{flag}")
    if nube:
        print("\n⚠ SALUD DEL PC: los marcados viven en una carpeta que se sincroniza a la nube. "
              "La sync en caliente puede bloquear/corromper archivos de trabajo; muevelos fuera "
              "(p.ej. a ~/<proyecto>) antes de trabajarlos en serio.")

    if not nuevos:
        print("\nNada nuevo que registrar (idempotente).")
        return 0
    if not confirm:
        print("\n[DRY-RUN] No escribi nada. Re-corre con --confirm para guardar en proyectos.local.toml.")
        return 0

    proy_final = existentes + nuevos
    CONFIG.write_text(_serializar(proy_final), encoding="utf-8")
    print(f"\nOK: {len(nuevos)} proyecto(s) anadidos -> {CONFIG.name} (total {len(proy_final)}).")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main(sys.argv[1:]))
