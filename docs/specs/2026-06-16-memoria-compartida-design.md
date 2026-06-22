# Spec — Memoria durable compartida + coordinación para agentes (ecosistema multi-agente)

> Fecha: 2026-06-16 · Estado: APROBADO (diseño) · Proceso: `11_PROCESO_MEJORA_ECOSISTEMA.md` (O11)
> Autor de la sesión: claude/claude-code · Afecta a: TODOS los agentes (claude, codex, futuros)

## 1. Problema

La **coordinación** entre sesiones/agentes ya es fuerte (`cerebro_multisesion.py`: locks,
sesiones con liveness, eventos, decisiones, buzón, `conocimiento()` compartido). El hueco real es
la **memoria durable**, que está fragmentada y NO se comparte entre agentes:

- Claude: **102 hechos curados** en `~/.claude/projects/C--Users-<TU_USUARIO>/memory/` (un hecho por
  archivo, auto-cargados en su contexto) → **invisibles para Codex**.
- Codex: lo suyo en `.codex/` → invisible para Claude.
- `.cerebro` tiene `conocimiento()` (≈58 notas) — compartido pero **efímero** (tope 300, en
  `%LOCALAPPDATA%`, no es markdown curado ni versionado).
- **No existe** un almacén durable neutral compartido.

## 2. Objetivo y decisiones tomadas

- **Compartir todo entre agentes SALVO secretos** (credenciales, tokens, historiales privados,
  cachés NUNCA se globalizan — reglas #8 / `01_ARQUITECTURA` / `09_MAPA_GLOBAL_MEMORIA`).
- **Todo bien organizado para agentes presentes y futuros** → una **fuente única** estructurada,
  no un parche.
- Enfoque elegido: **almacén durable neutral en `.cerebro/memoria/`** que Claude y Codex leen y
  escriben por igual, con un helper común y los adaptadores apuntando a él.

## 3. Arquitectura

### 3.1 Estructura del almacén `.cerebro/memoria/`
```
.cerebro/memoria/
  MEMORIA.md              # índice maestro: 1 línea por hecho, agrupado por área (NUNCA contenido)
  hub/                    # universal: usuario, feedback transversal, referencias cross-proyecto
  tu-tienda/ tu-proyecto-agente/ tu-proyecto-aprendizaje/ tu-proyecto-web/ tu-proyecto-automatizacion/ tu-proyecto-juegos/
    <slug>.md             # un hecho por archivo
```
Frontmatter (neutral, extiende el formato actual de Claude):
```yaml
---
name: <slug>
description: <una línea — para decidir relevancia al recordar>
metadata:
  type: user | feedback | project | reference
  project: hub | tu-tienda | tu-proyecto-agente | tu-proyecto-aprendizaje | tu-proyecto-web | tu-proyecto-automatizacion | tu-proyecto-juegos
  agente_origen: claude | codex
---
cuerpo con enlaces [[otro-slug]]
```
Principio de no-confusión (`09`): **una fuente principal por hecho**; si se necesita en varios
sitios, se enlaza/resume, no se duplica.

### 3.2 Qué se migra y qué NO
- **Se migra:** los 102 hechos (`project_*`, `feedback_*`, `reference_*`) → clasificados por área,
  con `project`/`agente_origen: claude`, preservando contenido y `[[links]]`.
- **Fuera:** credenciales/tokens/caches; `.remember/` sigue siendo diario privado de Claude
  (puede alimentar memoria, no es el almacén). Punteros a secretos (p. ej. "token en `.env`") SÍ
  se conservan: son punteros, no secretos.
- **tu-proyecto-automatizacion:** su `memoria/` granular viajera (USB) **se queda en el proyecto**; en el
  neutral va solo el hecho durable de alto nivel + puntero. Sin duplicar.

### 3.3 Helper `cerebro_memoria.py` (solo stdlib, estilo `cerebro_multisesion.py`)
Misma API para todos los agentes:
- `recordar(slug, descripcion, cuerpo, type, project, agente, links=())` — escribe el `.md` **y**
  actualiza el índice de forma atómica (mutex de proceso reutilizado del patrón de multisesión).
- `buscar(texto=None, type=None, project=None, agente=None, n=20)` · `leer(slug)` · `olvidar(slug)`
  · `indice()` · `reindexar()` (reconstruye `MEMORIA.md` desde archivos; sana huérfanos/drift).
- CLI: `py cerebro_memoria.py buscar "tu-tienda pricing"` · `py cerebro_memoria.py reindexar`.
- Escritura atómica + backup `.bak` (mismo blindaje que multisesión).

### 3.4 Stub redirector de Claude
- `~/.claude/.../memory/MEMORY.md` → **hardlink** al `MEMORIA.md` neutral (ambos en C:). Claude
  auto-carga el índice neutral, siempre actual, cero duplicación. `reindexar()` recrea el link si
  se rompe. **Fallback:** stub de texto con redirección + `CLAUDE.md` obliga a leer el índice
  neutral al iniciar.
- `CLAUDE.md` raíz: "memoria durable = `.cerebro/memoria/` vía `cerebro_memoria.py`" (las
  instrucciones de usuario sobrescriben el comportamiento por defecto del runtime).

### 3.5 Coordinación (existentes y futuros)
- **División clara:** `conocimiento()` = stream efímero de aprendizajes en caliente;
  `.cerebro/memoria/` = hechos durables curados. Promoción: aprendizaje que vale guardar →
  `recordar()`.
- Docs a actualizar (mínimas, regla `07`): `06_CONTRATO_NUEVO_AGENTE` (un agente nuevo lee
  `MEMORIA.md`, usa `cerebro_memoria.py`, coordina con `cerebro_multisesion.py`), `09_MAPA`
  (fuente primaria nueva), `00_INDICE`, `02_PROTOCOLO`, `11` (optimización **O11**), `12_HUB`
  (fila "Memoria durable compartida"), adaptadores `CLAUDE.md`/`AGENTS.md`. `mensaje()` en buzón de
  `codex`.

## 4. Plan de migración (con backup — regla #8)
1. **Backup**: zip de `~/.claude/.../memory/` → `.cerebro/_backups/memoria_claude_AAAAMMDD.zip`;
   originales se conservan hasta verificar.
2. Construir estructura `.cerebro/memoria/` + `cerebro_memoria.py`.
3. Migrar 102 (clasificar por área, añadir metadata, preservar `[[links]]`, escanear secretos).
4. `reindexar()` → verificar **102 → N hechos, 0 huérfanos** por conteo.
5. `MEMORY.md` → hardlink al índice neutral (backup del original antes).
6. Actualizar docs/adaptadores + bitácora `03` + checklist `04`.
7. Registrar (`ms.evento`/`ms.conocimiento`) + buzón a codex.

## 5. Verificación
- Autotest de `cerebro_memoria.py`: `reindexar()` idempotente; `buscar()` encuentra un hecho
  conocido; `recordar()/olvidar()` round-trip; **0 huérfanos** tras reindex.
- Conteo migrado == origen (menos lo excluido a propósito).
- `MEMORY.md` resuelve al índice neutral (auto-load de Claude intacto).
- Codex: verificar legibilidad de la ruta + `AGENTS.md` actualizado (no se puede correr Codex aquí).

## 6. Riesgos / Rollback
- **Rollback:** restaurar desde el zip de backup. NO se borran los originales de `~/.claude` hasta
  que el usuario confirme que el sistema nuevo funciona en una sesión real.
- Hardlink frágil ante renombrados → `reindexar()` lo recrea; fallback a stub de texto.

## 7. Fuera de alcance (YAGNI)
- Base de datos / embeddings para búsqueda semántica (basta léxica).
- Tocar el PC del trabajo (separado; va por USB).
- Mover credenciales/cachés/historiales privados.
