# ⚡ HÁBITOS DE TOKENS (primordiales) — ahorro de gasto en TODA sesión

> Síntesis verificada (2026-06-17, 3 investigaciones contra docs oficiales de Anthropic/Claude Code).
> Estos hábitos son **primordiales**: aplican a toda sesión de cualquier agente. **Regla de aviso:**
> cada vez que el asistente vaya a ACTUAR en contra de uno de estos hábitos, debe AVISAR al usuario
> ANTES y dejar que el usuario lo aplique (el usuario controla `/clear`, `/compact`, `/model`, etc.).
> Detalle de por qué cada uno: memoria [[tokens-sintesis-reduccion]]. Operacionaliza la regla #11.

## Los 3 monederos (no confundir)
- **$ de la sesión Claude Code** (lo que más importa día a día).
- **$ del maestro Claude de tu-proyecto-agente** (solo con `--teach`).
- **Cómputo local** del Qwen de tu-proyecto-agente (no cuesta $, cuesta GPU/tiempo).

## HÁBITOS PRIMORDIALES (sesión Claude Code · coste de aplicar = CERO)
1. **`/clear` al cambiar de proyecto** (tu-tienda↔tu-proyecto-agente↔tu-proyecto-aprendizaje↔…). El historial se re-cobra en cada
   turno; el router `CLAUDE.md` se re-inyecta solo. → ahorro #1 en sesiones largas.
2. **No editar `CLAUDE.md`/`AGENTS.md` a mitad de sesión** salvo necesidad: invalida el caché de prefijo
   (write 1.25× de todo lo que sigue). Si hay que tocarlos, hacerlo en UN bloque al inicio/fin.
3. **Subagentes solo para barridos multi-archivo.** Arrancan en frío (~3.700 tok de overhead, sin
   heredar tu caché). Regla: ahorra si `(lectura inline − resumen devuelto) > ~3.700`. Edición de 1-2
   archivos que ya ubicas → inline. Para read-only, preferir Explore/Plan (se saltan CLAUDE.md).
4. **`/compact focus on <tarea>`** antes de tareas largas (no esperar al auto). Instrucciones críticas
   al INICIO de cada `SKILL.md` (la truncación conserva el inicio). → **Protocolo de compactación** abajo.
5. **Leer barato:** Read con `offset/limit`, Grep con `count`/`files_with_matches` (+`glob`/`type`),
   y `cerebro_memoria.py buscar` en vez de re-leer docs/memoria enteros. NO re-leer un archivo recién
   editado (Edit/Write ya falla si no aplicó).
6. **Bajar de modelo donde la calidad no sufra** (Sonnet −40%, Haiku −90% vs Opus) y **subagentes de
   research en modelo barato** (devuelven poco resumen). Ver multimodelo abajo.
7. **MCP en modo deferred** (NO `ENABLE_TOOL_SEARCH=false`): hay cientos de tools = decenas de miles de
   tok si se cargan upfront.
8. **`disable-model-invocation: true`** en skills de efecto (commit/deploy/publicar): salen del índice
   de arranque, cuestan cero hasta invocarlas con `/`.
9. **Respuestas concisas** (el output es el token más caro, 5× el input, y nunca se cachea).

## Protocolo de compactación automática (auto-compact nativo + aviso enfocado) — elegido 2026-06-18
> Por qué NO por reloj: la compactación se dispara por **llenado de contexto** o **frontera de lote**, NUNCA
> por minutos. Compactar pronto tira caché caliente (TTL ~5 min, se re-cobra todo) → más caro, lo contrario
> del objetivo. **Límite técnico:** el asistente NO puede ejecutar `/compact`/`/clear` (son comandos del
> cliente, no tools). Por eso el protocolo combina lo automático nativo + un aviso de un toque.

**Dos capas:**
1. **Red de seguridad = auto-compact nativo de Claude Code** (manos libres, sin keystroke). Se activa una
   vez en `/config` (lo hace el usuario; no mutar config global en caliente). Cubre el caso "me pasé del
   límite sin darme cuenta". Resumen genérico (sin focus).
2. **Foco fino = aviso enfocado del asistente** (un toque del usuario). El asistente emite el comando exacto
   listo para correr en estos **disparadores**:
   - **Frontera de lote:** terminé un grupo coherente de tareas (p.ej. un trío de módulos del backlog) y voy
     a cambiar de área/tema.
   - **Contexto alto:** noto el historial largo (muchos tool-outputs/ciclos) aunque no se haya cerrado lote.
   - **Cambio de proyecto:** ahí el aviso es **`/clear`** (más barato que `/compact`), no compactar.

**Formato fijo del aviso** (siempre el comando ya redactado con el `focus` correcto, para que el usuario solo
presione enter):
> ⚠️ Tokens — frontera de lote / contexto alto. Recomiendo: `/compact focus on <tarea-en-curso concreta>`
> (o `/clear` si vas a cambiar de proyecto). Lo controlas tú.

El `<focus>` lo decide el asistente con lo que sabe necesario para seguir: la tarea/área activa + el próximo
paso, NO el historial ya cerrado. Tras el compact, el asistente continúa el trabajo sin re-derivar (handoff +
memoria + árbol de tareas son la continuidad — ver sección de continuidad abajo).

## Palancas de API (mecánica verificada)
- **Prompt caching** (palanca #1): lectura 0.1×, escritura 1.25× (5min)/2× (1h); break-even tras 1 sola
  lectura; orden `tools→system→messages`; cambiar de modelo o de tools invalida todo.
- **Batch API**: −50% input+output, <1h, para trabajo no interactivo (se apila con caching, TTL 1h).
- **Precios in/out MTok:** Opus 4.8 $5/$25 · Sonnet 4.6 $3/$15 · Haiku 4.5 $1/$5.

## Eficiencia de docs del ecosistema (aplicado 2026-06-17)
- **B2:** `00_INDICE.md` ya no es "lectura obligatoria por orden" → "Mapa: abre solo el que aplique".
- **B1:** regla `buscar` el hecho ANTES de abrir el doc dueño (usa el recall semántico).
- **B4:** `14_COPROGRAMACION`/`03_BITACORA` marcados consulta-no-carga (resumen en memoria; enlazar).

## tu-proyecto-agente (cola/roadmap — toca $ del maestro + cómputo local)
- **A1** caché del system+tools del maestro (`engine_claude.py`), **A2** poda de PNG por turno, **A3**
  `text_summary(goal=...)` + bajar `limit`, **A6** registrar embedder denso (gated por modelo de
  embeddings en tu servidor LLM local — ver pendiente). Validar con UN episodio antes de recolección masiva.

## Multimodelo (varias sesiones, una por modelo) + mensajería de tareas por modelo
Para ahorrar, el usuario puede abrir **varias sesiones Claude Code con modelos distintos** (p.ej. una
Haiku para lo mecánico, una Opus para lo difícil) y repartir el trabajo por **`cerebro_tareas_modelo.py`**:
una cola de tareas DIRIGIDAS A UN MODELO. La sesión cara (Opus) publica tareas mecánicas para `haiku`;
la sesión barata las toma y ejecuta. Uso:
```
py -3 .cerebro\cerebro_tareas_modelo.py publicar "titulo" -p "proposito" --modelo haiku \
    --terminado "criterio" [--archivo x.py --prueba "cmd"]
py -3 .cerebro\cerebro_tareas_modelo.py pendientes haiku     # lo que esta sesion (Haiku) debe tomar
py -3 .cerebro\cerebro_tareas_modelo.py tomar <id> --por sesion-haiku
py -3 .cerebro\cerebro_tareas_modelo.py completar <id> -n "resultado"
py -3 .cerebro\cerebro_tareas_modelo.py tablero                # quien tiene que hacer que, por modelo
```
Toda tarea lleva TODOS sus detalles (propósito + terminado siempre; archivo + prueba si toca código),
igual que el árbol de tareas de tu-proyecto-agente.

## Continuidad de sesión (perder la MENOR cantidad de contexto al cerrar/abrir)
El objetivo: que reabrir NO obligue a re-derivar ni re-leer todo. La pérdida se minimiza porque el
estado vive en capas DURABLES, no en el historial del chat:
- **Al CERRAR una sesión:**
  1. `session-report` / `remember` → escribir el **handoff** en `~\.remember\remember.md`
     (el hook `SessionStart` lo auto-carga al abrir): qué estaba en curso, decisiones tomadas, **el
     próximo paso concreto**, y los punteros (no pegar contenido — enlazar).
  2. Promover lo que vale a **memoria durable** (`cerebro_memoria.recordar`) — sobrevive a cualquier sesión.
     Para no olvidar qué promover, `py .cerebro\cerebro_memoria.py cosechar [proyecto]` lista el stream
     efímero `conocimiento()` como candidatos durables (con slug sugerido; NO graba — eliges tú).
  3. Dejar lo EN-CURSO en el **árbol de tareas** (tu-proyecto-agente `tareas/`) o en la **cola por modelo**; `latido`/
     `despedir` de la multisesión y `conocimiento()` cierran el estado de coordinación.
- **Al ABRIR otra sesión:**
  1. Leer el **handoff** (`.remember/remember.md`, auto-cargado) + `00_INDICE.md` (mapa, no todo).
  2. `cerebro_memoria.py buscar "<tema>"` para traer el hecho exacto en vez de re-leer documentos.
  3. `ms.estado()` / `ARBOL.md` / `cerebro_tareas_modelo tablero` para ver dónde quedó cada hilo.
- **Regla:** el handoff y la memoria son la fuente de continuidad; el historial del chat es desechable
  (por eso `/clear` entre proyectos es barato). Enlazar, no pegar (truco 16).
