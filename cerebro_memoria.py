"""CEREBRO · MEMORIA DURABLE COMPARTIDA (multi-agente).

Almacen markdown neutral que TODOS los agentes (claude, codex, futuros) leen y escriben.
Un hecho por archivo en .cerebro/memoria/<area>/<slug>.md; indice maestro MEMORIA.md
reconstruible con reindexar(). Solo stdlib. Reusa el blindaje (mutex de proceso) de
cerebro_multisesion.

conocimiento() de la multisesion = stream EFIMERO de aprendizajes en caliente.
Este almacen = hechos DURABLES curados. Promocion: aprendizaje que vale guardar -> recordar().

API:
    recordar(slug, descripcion, cuerpo, type, project, agente, links=()) -> ruta
    leer(slug) -> dict | None
    olvidar(slug) -> bool
    buscar(texto=None, type=None, project=None, agente=None, n=20) -> list[dict]
    indice() -> str
    reindexar() -> int   # nº de hechos indexados
CLI: py cerebro_memoria.py [reindexar | indice | buscar <texto> | leer <slug>]
"""
from __future__ import annotations
import re, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cerebro_core as core   # base comun: escritura atomica
from cerebro_multisesion import _Mutex   # mutex de proceso (serializa escrituras)
from cerebro_core import write_atomic as _write_text_atomic   # texto atomico (.bak + fsync + replace)

BASE = pathlib.Path(__file__).resolve().parent / "memoria"
INDICE = BASE / "MEMORIA.md"
# "hub" = area neutral siempre presente; el resto sale de proyectos.local.toml (personal, no versionado).
AREAS = ["hub"]
try:
    import cerebro_proyectos as _proy
    AREAS += [n for n in _proy.nombres() if n not in AREAS]
except Exception:
    pass
TIPOS = {"user", "feedback", "project", "reference"}
_FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)


def _area(project: str) -> str:
    p = (project or "hub").strip().lower()
    return p if p in AREAS else "hub"


def _parse(texto: str) -> dict:
    """Devuelve {name, description, type, project, agente_origen, cuerpo, links}."""
    m = _FM.match(texto)
    meta, cuerpo = {}, texto
    if m:
        head, cuerpo = m.group(1), m.group(2)
        cur = meta
        for ln in head.splitlines():
            if not ln.strip():
                continue
            if re.match(r"^\s+\w", ln) and ":" in ln:       # campo anidado (dentro de metadata:)
                k, _, v = ln.strip().partition(":")
                cur[k.strip()] = v.strip()
            elif ln.rstrip().endswith(":") and ":" in ln:    # apertura de bloque (metadata:)
                cur = meta.setdefault(ln.strip()[:-1], {})
            else:
                k, _, v = ln.partition(":")
                meta[k.strip()] = v.strip()
                cur = meta
    md = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
    return {
        "name": meta.get("name", ""),
        "description": meta.get("description", ""),
        "type": md.get("type", meta.get("type", "")),
        "project": md.get("project", meta.get("project", "hub")),
        "agente_origen": md.get("agente_origen", meta.get("agente_origen", "")),
        "cuerpo": cuerpo.strip(),
        "links": re.findall(r"\[\[([^\]]+)\]\]", cuerpo),
    }


def _archivos() -> list:
    return [p for p in BASE.glob("*/*.md") if p.name != "MEMORIA.md"]


# _write_text_atomic = cerebro_core.write_atomic (escribe texto atomico con respaldo .bak; importado arriba).


def _find(slug: str):
    for p in _archivos():
        if p.stem == slug:
            return p
    return None


def recordar(slug, descripcion, cuerpo, type, project, agente, links=()) -> str:
    if type not in TIPOS:
        raise ValueError(f"type invalido: {type} (usa {TIPOS})")
    area = _area(project)
    cuerpo = cuerpo.rstrip()
    for l in links:
        if f"[[{l}]]" not in cuerpo:
            cuerpo += f"\n\n[[{l}]]"
    doc = (f"---\nname: {slug}\ndescription: {descripcion}\nmetadata:\n"
           f"  type: {type}\n  project: {area}\n  agente_origen: {agente}\n---\n\n{cuerpo}\n")
    with _Mutex("memoria"):
        viejo = _find(slug)
        if viejo and viejo.parent.name != area:
            try: viejo.unlink()
            except OSError: pass
        _write_text_atomic(BASE / area / f"{slug}.md", doc)
        _reindexar_nolock()
    return str(BASE / area / f"{slug}.md")


def leer(slug):
    p = _find(slug)
    if not p:
        return None
    d = _parse(p.read_text(encoding="utf-8"))
    d["ruta"] = str(p)
    return d


def olvidar(slug) -> bool:
    with _Mutex("memoria"):
        p = _find(slug)
        if not p:
            return False
        p.unlink()
        _reindexar_nolock()
        return True


SEM_FLOOR = 0.15   # umbral minimo para incluir un hecho SOLO por semantica (sin solape lexico)


def buscar(texto=None, type=None, project=None, agente=None, n=20, semantico=None) -> list:
    """Recall de hechos. Filtros estructurados (type/project/agente) + recuperacion por `texto`.

    El `texto` se recupera por SIGNIFICADO (cerebro_semantica: denso via tu servidor LLM local -> TF-IDF ->
    token-coseno) cuando hay backend, y es SUPERSET de la busqueda por subcadena de siempre: un hecho
    que CONTIENE el texto SIEMPRE aparece (recall garantizado), y ademas suben los relevantes por
    sinonimo/parafrasis. `semantico`: None=auto (usa semantica si hay backend), False=solo subcadena
    (comportamiento historico), True=fuerza semantica. Resultados ordenados por relevancia (_score)."""
    cands = []
    for p in _archivos():
        d = _parse(p.read_text(encoding="utf-8"))
        if type and d["type"] != type: continue
        if project and d["project"] != _area(project): continue
        if agente and d["agente_origen"] != agente: continue
        d["ruta"] = str(p)
        cands.append(d)
    if not texto:
        return cands[:n]
    t = texto.lower()
    sem = None
    if semantico is not False:
        try:
            import cerebro_semantica
            if semantico is True or cerebro_semantica.has_dense() or _sklearn():
                docs = [f"{d['name']} {d['description']} {d['cuerpo']}" for d in cands]
                sem = cerebro_semantica.scores(texto, docs)
        except Exception:
            sem = None
    scored = []
    for i, d in enumerate(cands):
        hay = t in (d["name"] + d["description"] + d["cuerpo"]).lower()
        s = sem[i] if sem else 0.0
        # Subcadena = +1 (recall garantizado, nunca se pierde). Semantico-solo: solo si pasa el piso.
        if hay:
            score = 1.0 + s
        elif sem is not None and s >= SEM_FLOOR:
            score = s
        else:
            continue
        d2 = dict(d); d2["_score"] = round(score, 4)
        scored.append((score, i, d2))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [d for _, _, d in scored[:n]]


def _sklearn() -> bool:
    try:
        import sklearn  # noqa: F401
        return True
    except Exception:
        return False


def indice() -> str:
    return INDICE.read_text(encoding="utf-8") if INDICE.exists() else ""


def _reindexar_nolock() -> int:
    porarea: dict = {a: [] for a in AREAS}
    total = 0
    for p in _archivos():
        d = _parse(p.read_text(encoding="utf-8"))
        d["_rel"] = f"{p.parent.name}/{p.name}"
        porarea.setdefault(p.parent.name, []).append(d)
        total += 1
    lineas = [
        "# MEMORIA — memoria durable compartida del ecosistema multi-agente",
        "",
        "> Fuente UNICA de hechos durables, compartida por todos los agentes (claude, codex, "
        "futuros). Un hecho por archivo `<area>/<slug>.md` (frontmatter name/description/"
        "metadata.type/project/agente_origen; cuerpo con `[[enlaces]]`). Este MEMORIA.md es el "
        "INDICE: una linea por hecho, NUNCA el contenido. Usa `cerebro_memoria.py` para escribir "
        "(mantiene este indice). conocimiento() de la multisesion = stream efimero; esto = durable.",
        "",
    ]
    for a in AREAS:
        items = sorted(porarea.get(a, []), key=lambda x: (x["type"], x["name"]))
        if not items:
            continue
        lineas.append(f"## {a}")
        for d in items:
            org = f" · {d['agente_origen']}" if d["agente_origen"] else ""
            lineas.append(f"- [{d['name']}]({d['_rel']}) — _{d['type']}{org}_ — {d['description']}")
        lineas.append("")
    _write_text_atomic(INDICE, "\n".join(lineas) + "\n")
    return total


def reindexar() -> int:
    with _Mutex("memoria"):
        return _reindexar_nolock()


def _orfanos() -> list:
    idx = indice()
    return [p.stem for p in _archivos() if f"]({p.parent.name}/{p.name})" not in idx]


if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    cmd = sys.argv[1] if len(sys.argv) > 1 else "indice"
    if cmd == "reindexar":
        print("hechos indexados:", reindexar(), "| orfanos:", _orfanos())
    elif cmd == "indice":
        print(indice())
    elif cmd == "buscar":
        for d in buscar(" ".join(sys.argv[2:])):
            sc = f"{d.get('_score', 0):.3f}"
            print(f"[{sc}] [{d['type']}/{d['project']}] {d['name']} — {d['description']}")
    elif cmd == "leer":
        d = leer(sys.argv[2]); print(d["cuerpo"] if d else "(no existe)")
    else:
        print("uso: cerebro_memoria.py [reindexar|indice|buscar <texto>|leer <slug>]")
