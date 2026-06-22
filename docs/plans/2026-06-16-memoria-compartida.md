# Memoria durable compartida — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task. Steps use checkbox (`- [ ]`) syntax. **NO hay git** en el ecosistema → los
> "commit" se reemplazan por checkpoints de verificación + registro en multisesión.

**Goal:** Crear un almacén de memoria durable neutral en `.cerebro/memoria/` que Claude y Codex
(y agentes futuros) leen y escriben por igual, migrando los 102 hechos de Claude, con un helper
común y los adaptadores apuntando a la nueva fuente única.

**Architecture:** Almacén markdown (un hecho por archivo, por área de proyecto) + índice maestro
`MEMORIA.md` reconstruible. Helper `cerebro_memoria.py` (solo stdlib, reusa el mutex/atomic de
`cerebro_multisesion.py`). `~/.claude/.../MEMORY.md` se vuelve hardlink al índice neutral para que
Claude lo siga auto-cargando sin duplicar.

**Tech Stack:** Python 3 stdlib (json/re/pathlib/tempfile/datetime), Windows hardlink (`mklink /H`).

---

## File Structure
- Create: `~\.cerebro\cerebro_memoria.py` — helper API + CLI.
- Create: `~\.cerebro\memoria\` (estructura de carpetas + `MEMORIA.md`).
- Create: `~\.cerebro\_backups\memoria_claude_AAAAMMDD.zip` — backup.
- Create: `~\.cerebro\_migrar_memoria.py` — script de migración de una sola vez (se borra al final).
- Modify (docs): `00_INDICE.md`, `02_PROTOCOLO_OPERATIVO.md`, `06_CONTRATO_NUEVO_AGENTE.md`,
  `09_MAPA_GLOBAL_MEMORIA.md`, `11_PROCESO_MEJORA_ECOSISTEMA.md`, `12_HUB_PROCESOS.md`,
  `03_BITACORA_MULTIAGENTE.md`, `04_CHEQUEOS_SEGURIDAD.md`.
- Modify (adaptadores): `~\CLAUDE.md`, `~\AGENTS.md`.
- Replace: `~\.claude\projects\C--Users-<TU_USUARIO>\memory\MEMORY.md` → hardlink (backup antes).

---

## Task 1: Backup de la memoria de Claude (seguridad primero — regla #8)

**Files:** Create `~\.cerebro\_backups\memoria_claude_AAAAMMDD.zip`

- [ ] **Step 1: Crear el zip de backup**
```powershell
$ts = Get-Date -Format yyyyMMdd
New-Item -ItemType Directory -Force "~\.cerebro\_backups" | Out-Null
Compress-Archive -Path "~\.claude\projects\C--Users-<TU_USUARIO>\memory\*" `
  -DestinationPath "~\.cerebro\_backups\memoria_claude_$ts.zip" -Force
```
- [ ] **Step 2: Verificar el backup**
```powershell
$z = Get-ChildItem "~\.cerebro\_backups\memoria_claude_*.zip" | Select -Last 1
Add-Type -A System.IO.Compression.FileSystem
$n = [IO.Compression.ZipFile]::OpenRead($z.FullName).Entries.Count
"backup: $($z.Name) — $n entradas"
```
Expected: ~102+ entradas (los .md + MEMORY.md). Si <100 → STOP, no continuar.

---

## Task 2: Helper `cerebro_memoria.py`

**Files:** Create `~\.cerebro\cerebro_memoria.py`

- [ ] **Step 1: Escribir el helper completo**
```python
"""CEREBRO · MEMORIA DURABLE COMPARTIDA (multi-agente).

Almacen markdown neutral que TODOS los agentes (claude, codex, futuros) leen y escriben.
Un hecho por archivo en .cerebro/memoria/<area>/<slug>.md; indice maestro MEMORIA.md
reconstruible con reindexar(). Solo stdlib. Reusa el blindaje de cerebro_multisesion.

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
import os, re, sys, tempfile, pathlib
from datetime import datetime

sys.path.insert(0, r"~\.cerebro")
from cerebro_multisesion import _Mutex   # mutex de proceso (serializa escrituras)

BASE = pathlib.Path(r"~\.cerebro\memoria")
INDICE = BASE / "MEMORIA.md"
AREAS = ["hub", "tu-tienda", "tu-proyecto-agente", "tu-proyecto-aprendizaje", "tu-proyecto-web",
         "tu-proyecto-automatizacion", "tu-proyecto-juegos"]
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
            if re.match(r"^\s+\w", ln) and ":" in ln:      # campo anidado (metadata:)
                k, _, v = ln.strip().partition(":")
                cur[k.strip()] = v.strip()
            elif ln.rstrip().endswith(":") and ":" in ln:  # apertura de bloque (metadata:)
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


def _archivos() -> list[pathlib.Path]:
    return [p for p in BASE.glob("*/*.md") if p.name != "MEMORIA.md"]


def _write_text_atomic(path: pathlib.Path, texto: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            path.replace(path.with_suffix(".bak"))
        except OSError:
            pass
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try: os.remove(tmp)
            except OSError: pass


def _find(slug: str) -> pathlib.Path | None:
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


def leer(slug) -> dict | None:
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


def buscar(texto=None, type=None, project=None, agente=None, n=20) -> list:
    out = []
    t = (texto or "").lower()
    for p in _archivos():
        d = _parse(p.read_text(encoding="utf-8"))
        if type and d["type"] != type: continue
        if project and d["project"] != _area(project): continue
        if agente and d["agente_origen"] != agente: continue
        if t and t not in (d["name"] + d["description"] + d["cuerpo"]).lower(): continue
        d["ruta"] = str(p)
        out.append(d)
    return out[:n]


def indice() -> str:
    return INDICE.read_text(encoding="utf-8") if INDICE.exists() else ""


def _reindexar_nolock() -> int:
    porarea: dict[str, list[dict]] = {a: [] for a in AREAS}
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
            print(f"[{d['type']}/{d['project']}] {d['name']} — {d['description']}")
    elif cmd == "leer":
        d = leer(sys.argv[2]); print(d["cuerpo"] if d else "(no existe)")
    else:
        print("uso: cerebro_memoria.py [reindexar|indice|buscar <texto>|leer <slug>]")
```

- [ ] **Step 2: Crear la estructura de carpetas**
```bash
for a in hub tu-tienda tu-proyecto-agente tu-proyecto-aprendizaje tu-proyecto-web tu-proyecto-automatizacion tu-proyecto-juegos; do
  mkdir -p "/c/Users/<TU_USUARIO>/.cerebro/memoria/$a"
done
ls /c/Users/<TU_USUARIO>/.cerebro/memoria/
```

- [ ] **Step 3: Autotest del helper (round-trip + reindex idempotente)**
```bash
cd /c/Users/<TU_USUARIO>/.cerebro && py -3 -c "
import cerebro_memoria as m
m.recordar('autotest-zzz','prueba de round-trip','Cuerpo de prueba con [[deps-opcionales]].','reference','hub','claude')
assert m.leer('autotest-zzz')['description']=='prueba de round-trip'
assert any(d['name']=='autotest-zzz' for d in m.buscar('round-trip'))
n1=m.reindexar(); n2=m.reindexar(); assert n1==n2, 'reindex no idempotente'
assert m.olvidar('autotest-zzz') and m.leer('autotest-zzz') is None
assert not m._orfanos(), 'hay orfanos'
print('AUTOTEST OK · hechos:',n2)
"
```
Expected: `AUTOTEST OK` y 0 orfanos.

---

## Task 3: Migrar los 102 hechos de Claude

**Files:** Create `~\.cerebro\_migrar_memoria.py` (se borra al final)

- [ ] **Step 1: Escribir el migrador**
```python
"""Migracion de una sola vez: ~/.claude/.../memory/*.md -> .cerebro/memoria/<area>/.
Clasifica por prefijo de nombre y tokens de proyecto; preserva contenido y [[links]];
añade project + agente_origen=claude; escanea secretos literales. NO borra el origen."""
import re, sys, pathlib
sys.path.insert(0, r"~\.cerebro")
import cerebro_memoria as m

SRC = pathlib.Path(r"~\.claude\projects\C--Users-<TU_USUARIO>\memory")
TOK = [("tu-tienda","tu-tienda"),("tu-proyecto-agente","tu-proyecto-agente"),("aprender","tu-proyecto-aprendizaje"),("roblox","tu-proyecto-juegos"),
       ("noticias","tu-proyecto-automatizacion"),("juego","tu-proyecto-web"),("juegos","tu-proyecto-web"),
       ("pagina","tu-proyecto-web")]
SECRETO = re.compile(r"(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN|password\s*=\s*\S|token\s*[:=]\s*[A-Za-z0-9]{20,})", re.I)

def tipo_de(nombre):
    for pre in ("feedback","project","reference","user"):
        if nombre.startswith(pre):
            return pre
    return "reference"

def area_de(nombre):
    n = nombre.lower()
    for tok, area in TOK:
        if tok in n:
            return area
    return "hub"

def main():
    hechos = sospechosos = 0
    for p in sorted(SRC.glob("*.md")):
        if p.name == "MEMORIA.md" or p.name == "MEMORY.md":
            continue
        raw = p.read_text(encoding="utf-8")
        d = m._parse(raw)
        slug = d["name"] or p.stem
        desc = d["description"] or (d["cuerpo"][:120].replace(chr(10)," ") if d["cuerpo"] else slug)
        cuerpo = d["cuerpo"] or raw.strip()
        tipo = d["type"] if d["type"] in m.TIPOS else tipo_de(p.stem)
        area = d["project"] if d["project"] in m.AREAS else area_de(p.stem)
        if SECRETO.search(cuerpo):
            print("  ⚠ POSIBLE SECRETO, revisar a mano (NO migrado):", p.name); sospechosos += 1; continue
        m.recordar(slug, desc, cuerpo, tipo, area, "claude")
        hechos += 1
    print(f"migrados: {hechos} | sospechosos saltados: {sospechosos} | total indice: {m.reindexar()}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Correr el migrador**
```bash
cd /c/Users/<TU_USUARIO>/.cerebro && py -3 _migrar_memoria.py
```
Expected: `migrados: ~100+`. Anotar cualquier "POSIBLE SECRETO" para revisar a mano.

- [ ] **Step 3: Verificar conteo y 0 huérfanos**
```bash
cd /c/Users/<TU_USUARIO>/.cerebro && py -3 -c "
import cerebro_memoria as m
print('hechos:', m.reindexar(), '| orfanos:', m._orfanos())
from collections import Counter
print('por area:', Counter(p.parent.name for p in m._archivos()))
"
```
Expected: hechos ≈ 100+, orfanos `[]`. Si origen=102 y migrados+sospechosos ≠ 101 (102−MEMORY.md) → revisar.

---

## Task 4: Redirigir `MEMORY.md` de Claude al índice neutral (hardlink)

**Files:** Replace `~\.claude\projects\C--Users-<TU_USUARIO>\memory\MEMORY.md`

- [ ] **Step 1: Backup del MEMORY.md original**
```powershell
$d = "~\.claude\projects\C--Users-<TU_USUARIO>\memory"
Copy-Item "$d\MEMORY.md" "$d\MEMORY.md.pre-neutral.bak" -Force
```
- [ ] **Step 2: Crear el hardlink (con fallback a stub)**
```powershell
$d = "~\.claude\projects\C--Users-<TU_USUARIO>\memory"
$idx = "~\.cerebro\memoria\MEMORIA.md"
Remove-Item "$d\MEMORY.md" -Force
cmd /c mklink /H "$d\MEMORY.md" "$idx"
if (-not (Test-Path "$d\MEMORY.md")) {
  # Fallback: stub de texto que redirige
  Set-Content "$d\MEMORY.md" "# MEMORIA MOVIDA`n`nLa memoria durable ahora vive en `~\.cerebro\memoria\MEMORIA.md` (compartida con todos los agentes). LÉELA al iniciar. Escribe con `cerebro_memoria.py`." -Encoding utf8
}
```
- [ ] **Step 3: Verificar que MEMORY.md resuelve al índice neutral**
```powershell
$d = "~\.claude\projects\C--Users-<TU_USUARIO>\memory"
$a = (Get-FileHash "$d\MEMORY.md").Hash
$b = (Get-FileHash "~\.cerebro\memoria\MEMORIA.md").Hash
"MEMORY.md == indice neutral (hardlink): $($a -eq $b)"
```
Expected: `True` (hardlink) o, si fallback, el stub con la redirección.

---

## Task 5: Actualizar docs neutrales y adaptadores (regla #07, mínimo suficiente)

**Files:** Modify `09_MAPA_GLOBAL_MEMORIA.md`, `06_CONTRATO_NUEVO_AGENTE.md`, `00_INDICE.md`,
`02_PROTOCOLO_OPERATIVO.md`, `11_PROCESO_MEJORA_ECOSISTEMA.md`, `12_HUB_PROCESOS.md`,
`~\CLAUDE.md`, `~\AGENTS.md`.

- [ ] **Step 1: `09_MAPA` — nueva fuente primaria.** Añadir fila: "Memoria durable compartida →
  `.cerebro\memoria\MEMORIA.md` (vía `cerebro_memoria.py`)" como fuente primaria de hechos durables;
  marcar `~/.claude/.../memory` como redirigida (hardlink).
- [ ] **Step 2: `11` — optimización O11.** Añadir "### O11 — Memoria durable compartida" (fuente
  única neutral + helper; `conocimiento()` efímero vs memoria durable).
- [ ] **Step 3: `12_HUB` — fila nueva.** "Memoria durable compartida | guardar/buscar un hecho que
  sirva a varios agentes | `cerebro_memoria.py` (+ `09_MAPA`) | hecho indexado sin huérfanos".
- [ ] **Step 4: `06_CONTRATO_NUEVO_AGENTE`.** Un agente nuevo: lee `memoria/MEMORIA.md`, usa
  `cerebro_memoria.py` para recordar/buscar, coordina con `cerebro_multisesion.py`.
- [ ] **Step 5: `00_INDICE` + `02_PROTOCOLO`.** Enlace corto al almacén y al helper en la ruta de
  lectura y en "Durante el trabajo".
- [ ] **Step 6: `CLAUDE.md` (raíz) + `AGENTS.md`.** Sección de memoria: "memoria durable =
  `.cerebro\memoria\` vía `cerebro_memoria.py`; `~/.claude MEMORY.md` redirige al índice neutral".
- [ ] **Step 7: Verificar enlaces.** `grep -l "cerebro_memoria" .cerebro/*.md ~/CLAUDE.md ~/AGENTS.md`
  → todos los documentos objetivo lo mencionan.

---

## Task 6: Registro, aviso a Codex y cierre

- [ ] **Step 1: Mensaje en el buzón de Codex + evento + conocimiento + bitácora**
```bash
cd /c/Users/<TU_USUARIO>/.cerebro && py -3 -c "
import sys; sys.path.insert(0,r'~\.cerebro')
from cerebro_multisesion import Multisesion
ms=Multisesion('memoria compartida neutral', project='hub', agent='claude', runtime='claude-code')
ms.mensaje('agent:codex','MEMORIA DURABLE COMPARTIDA: usa cerebro_memoria.py (recordar/buscar/reindexar). Fuente unica .cerebro/memoria/MEMORIA.md. Ver 09_MAPA y 06_CONTRATO.')
ms.conocimiento('Memoria durable compartida operativa en .cerebro/memoria/ via cerebro_memoria.py; 102 hechos de Claude migrados; MEMORY.md redirige al indice neutral.', tags=['memoria','ecosistema','O11'])
ms.evento('Implementada memoria durable compartida (almacen neutral + helper + migracion + redireccion MEMORY.md).')
print('registrado')
"
```
- [ ] **Step 2: Añadir entrada en `03_BITACORA_MULTIAGENTE.md`** (cambio estructural, fecha + qué + por qué).
- [ ] **Step 3: Actualizar `04_CHEQUEOS_SEGURIDAD.md`** (chequeo: "memoria durable sin huérfanos vía
  `cerebro_memoria.py reindexar`; sin secretos literales migrados").
- [ ] **Step 4: Borrar el migrador de un solo uso**
```bash
rm /c/Users/<TU_USUARIO>/.cerebro/_migrar_memoria.py && echo "migrador borrado"
```

---

## Verificación final (gate de cierre)
- [ ] `py cerebro_memoria.py reindexar` → 0 huérfanos.
- [ ] `MEMORY.md` resuelve al índice neutral (hash igual) o stub con redirección.
- [ ] `buscar("pricing")` y `buscar("estabilizador")` devuelven hechos conocidos.
- [ ] Backup zip presente en `_backups/`; originales de `~/.claude` intactos (no borrados).
- [ ] Docs objetivo mencionan `cerebro_memoria`.
- [ ] Buzón de codex tiene el aviso.

## Self-Review (cobertura del spec)
- Estructura `.cerebro/memoria/` por área → Task 2.2. ✓
- Migración 102 + exclusión de secretos → Task 3. ✓
- Helper API → Task 2.1. ✓
- Stub/hardlink redirector → Task 4. ✓
- Coordinación futuros agentes (docs 06/09/00/02/11/12 + adaptadores) → Task 5. ✓
- Backup/rollback (regla #8) → Task 1; originales intactos hasta confirmar. ✓
- Verificación (autotest, conteo, huérfanos) → Task 2.3, 3.3, final. ✓
- Aviso a Codex + bitácora + checklist → Task 6. ✓