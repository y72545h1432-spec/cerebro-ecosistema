# 17 · Router de tareas por modelo (delegación multimodelo)

> Mecanismo para **ahorrar tokens**: le hablas a UNA sesión (la orquestadora) y ella reparte el trabajo al
> modelo más barato capaz de hacerlo. Spec: `.cerebro/specs/2026-06-17-router-por-modelo-design.md`.
> Cola física: `cerebro_tareas_modelo.py`. Cerebro del router: `cerebro_modelo.py`. Activador: hook SessionStart.
> Capa superior de roles por capacidad: `.cerebro/20_RED_ROLES_IA.md` (incluye rol `buscador` para
> investigacion actual con Gemini Deep Research, OpenAI Deep Research y Perplexity).

## Qué es
Tres piezas encima de la cola por tier que ya existía:
1. **Auto-conocimiento de modelo** — cada sesión sabe su tier (de su propio model-id) y se **registra** viva.
2. **Clasificador** — cualquier sesión propone a qué tier va una tarea (`clasificar`) y la confirma (híbrido).
3. **Activador** — un hook `SessionStart` inyecta la instrucción worker en TODA sesión nueva (texto en
   `.cerebro/worker_instruccion.txt`); la sesión se registra y consulta su cola sola.

## Cómo se usa (CLI de `cerebro_modelo.py`)
```
py .cerebro\cerebro_modelo.py soy claude-opus-4-8        # -> opus  (mapea model-id a tier)
py .cerebro\cerebro_modelo.py registrar <tu-tier>        # heartbeat: marca tu tier vivo (TTL 15 min)
py .cerebro\cerebro_modelo.py vivos                      # tiers con sesión viva ahora
py .cerebro\cerebro_modelo.py clasificar "<titulo>" -p "<prop>"   # propone tier + razón
py .cerebro\cerebro_modelo.py delegar "<titulo>" --tier <t> -p "<prop>" --terminado "<c>" [--archivo x --prueba c]
```
La cola se atiende con `cerebro_tareas_modelo.py`: `pendientes <tier>`, `tomar <id> --por <s>`, `completar <id>`.

## Las 3 decisiones de diseño
- **D1 (clasificación híbrida):** `clasificar` propone por heurística (palabras clave); la sesión confirma/corrige.
- **D2 (sin worker vivo):** si delegas a un tier sin sesión abierta, se **encola y se avisa** ("abre una sesión X"); no se ejecuta en el tier caro ni se auto-lanza nada (regla universal #3).
- **D3 (activador):** hook `SessionStart` inyecta la instrucción; la sesión se registra sola.

## Mapa model-id → tier
`claude-opus-*` y `claude-fable-*` → **opus** · `claude-sonnet-*` → **sonnet** · `claude-haiku-*` → **haiku** ·
desconocido/vacío → **opus** (default seguro: nunca degradar trabajo a un tier barato sin certeza).

## Relacion con la red de roles IA
Este router decide **tier local**. La red de roles decide **capacidad**:
`buscador` para fuentes actuales, `arquitecto` para diseno, `implementador` para codigo/docs,
`mecanico` para tareas baratas y `verificador` para cierre. Si la tarea contiene investigacion actual,
benchmarks, precios, normativa o fuentes externas, primero aplicar `20_RED_ROLES_IA.md`; solo delegar
al tier local cuando el trabajo ya sea implementable o verificable dentro del workspace.

## Cómo abrir las sesiones
Ver el doc de Escritorio `COMO_ABRIR_SESIONES_MULTIMODELO.md` (a quién le hablas y cuántas sesiones abrir).

## Tests
`py .cerebro\test_cerebro_modelo.py` (7 casos) · `py .cerebro\test_cerebro_tareas_modelo.py` (5 casos).

## Pendiente al cierre de sesión (no hacer a mitad — hábito #2 de tokens)
Enlazar este doc desde `CLAUDE.md` (sección multimodelo) y desde `00_INDICE.md`.
