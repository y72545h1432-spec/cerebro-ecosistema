# Co-programacion Multi-Agente

Investigacion y protocolo para que Claude, Codex y futuros agentes escriban codigo juntos con mas calidad, menos conflictos y mejor retroalimentacion.

## Objetivo
Permitir que varios agentes colaboren sobre una misma tarea de codigo sin pisarse:
- compartir analisis,
- dividir ownership,
- escribir cambios compatibles,
- revisarse mutuamente,
- verificar con evidencia,
- integrar con trazabilidad.

## Hallazgos de investigacion

### 1. Dos patrones validos: manager e handoffs
OpenAI Agents SDK documenta dos patrones principales:
- **Manager / agents as tools**: un coordinador conserva control y llama especialistas.
- **Handoffs**: agentes pares transfieren control a otro especialista.

Aplicacion local: para codigo complejo, usar un **integrador/coordinador** que divide ownership y recibe patches. Para tareas muy especializadas, usar handoff estructurado con `mensaje_tipo(type="handoff")`.

Fuente: https://openai.github.io/openai-agents-python/agents/

### 2. Handoff con metadata pequeña
Los handoffs funcionan mejor con payload estructurado: motivo, prioridad, resumen y filtros de contexto. No deben arrastrar todo el historial si no hace falta.

Aplicacion local: todo handoff de codigo debe incluir:
- objetivo,
- archivos tocados,
- estado actual,
- pruebas corridas,
- riesgos,
- siguiente accion esperada.

Fuente: https://openai.github.io/openai-agents-python/handoffs/

### 3. Selector de siguiente agente
AutoGen `SelectorGroupChat` usa roles/descripciones y contexto compartido para elegir el siguiente participante. Esto evita rondas fijas cuando la tarea necesita dinamismo.

Aplicacion local: el integrador decide el siguiente agente segun estado:
- arquitecto si falta diseño,
- implementador si hay plan,
- revisor si hay diff,
- tester si hay cambios listos,
- usuario si hay decision irreversible.

Fuente: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html

### 4. Swarm con handoffs locales
AutoGen `Swarm` permite que agentes deleguen segun capacidades y compartan contexto. Advierte que handoffs paralelos pueden causar comportamiento inesperado si no se controla.

Aplicacion local: permitir handoffs, pero no permitir dos agentes escribiendo el mismo recurso sin lock/ownership.

Fuente: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html

### 5. Worktrees reducen interferencia
Git soporta varios working trees para trabajar en mas de una rama a la vez. Esto sirve para separar cambios de agentes cuando una tarea es grande o riesgosa.

Aplicacion local: si varios agentes van a editar codigo en paralelo, preferir worktrees/ramas separadas o ownership por archivo. No mezclar cambios grandes en el mismo working tree sin coordinador.

Fuente: https://git-scm.com/docs/git-worktree

### 6. Merge exige limpieza y cuidado
Git merge incorpora cambios de ramas, pero con conflictos puede detenerse y requerir resolucion. Git desaconseja merges con cambios locales no triviales porque pueden dejar un estado dificil de revertir.

Aplicacion local: antes de integrar patches de varios agentes:
- working tree limpio o cambios claramente inventariados,
- pruebas por patch,
- merge/integracion por un solo integrador,
- rollback claro.

Fuente: https://git-scm.com/docs/git-merge

### 7. Reviews son parte central de calidad
GitHub describe reviews como forma primaria de colaborar: comentar, sugerir mejoras, aprobar o pedir cambios antes de merge.

Aplicacion local: ningun cambio multi-agente importante se considera listo hasta pasar por revisor distinto al implementador cuando sea posible.

Fuente: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews

### 8. Riesgo real de codigo agente sin supervision
SWE-chat (2026) reporta que menos de la mitad del codigo producido por agentes sobrevive en commits y que el codigo escrito por agentes introduce mas vulnerabilidades que el humano. Tambien observa que el flujo colaborativo humano-agente es mas eficiente que el "vibe coding" autonomo.

Aplicacion local: mas agentes no significa mas autonomia ciega. La calidad sube cuando hay:
- revision,
- tests,
- interrupciones/feedback,
- ownership,
- evidencia.

Fuente: https://arxiv.org/abs/2604.20779

### 9. Code review multi-agente mejora con supervisor QA
CodeAgent usa varios agentes para code review y un supervisor QA-Checker para asegurar que las contribuciones respondan a la pregunta inicial.

Aplicacion local: para codigo sensible, usar rol `qa-checker` o `revisor-integrador` que valide que cada comentario/diff responde al objetivo, no solo que "parece mejor".

Fuente: https://arxiv.org/abs/2402.02172

## Modelo local recomendado

### Roles
| Rol | Responsabilidad | Puede editar |
|---|---|---|
| Coordinador/integrador | Divide tarea, asigna ownership, decide merge, cierra evidencia | Si, pero idealmente solo integracion |
| Arquitecto | Diseña enfoque, contratos, riesgos | No por defecto |
| Implementador | Escribe patch en ownership asignado | Si, solo archivos asignados |
| Revisor | Busca bugs, regresiones, seguridad, tests faltantes | No por defecto |
| Tester | Corre pruebas, reproduce, verifica | No por defecto |
| QA-checker | Valida que todo responde al objetivo original | No por defecto |

Regla: un agente puede tener varios roles en tareas pequeñas, pero en cambios importantes revisor y implementador deben separarse.

## Flujo recomendado

### Fase 1 — Intake
1. Paso 0 multisesion.
2. Identificar proyecto y objetivo.
3. Elegir modo:
   - single-agent si es pequeño,
   - pair-review si toca codigo compartido,
   - multi-agent si requiere varias especialidades,
   - worktree fan-out si hay ediciones paralelas grandes.

### Fase 2 — Plan y ownership
1. Coordinador crea lista de archivos/modulos posibles.
2. Revisa estado del repo (`git status` si aplica).
3. Define ownership:
   - agente,
   - archivos/rutas,
   - limites,
   - pruebas esperadas.
4. Registra lock por recurso o archivo compartido:
   - `ms.reclamar("ruta-o-modulo")`
   - hardware/servicios con `scope="global"`.

### Fase 3 — Escritura controlada
1. Cada implementador relee los archivos asignados antes de editar.
2. No toca archivos fuera de ownership sin handoff/ack.
3. Emite progreso con `ms.progreso(...)`.
4. Si se bloquea, manda `mensaje_tipo(type="blocker")`.

### Fase 4 — Revision cruzada
1. Implementador entrega handoff con:
   - diff/resumen,
   - archivos cambiados,
   - pruebas corridas,
   - riesgos,
   - pendiente.
2. Revisor revisa con postura de code review:
   - bugs,
   - regresiones,
   - seguridad,
   - faltan pruebas,
   - complejidad innecesaria.
3. QA-checker valida contra objetivo original.

### Fase 5 — Integracion
1. Integrador aplica cambios en una sola linea de integracion.
2. Resuelve conflictos con contexto, no eligiendo "ours/theirs" a ciegas.
3. Corre pruebas relevantes.
4. Actualiza docs si cambia protocolo/reglas/API.
5. Cierra con evidencia.

## Modos operativos

### Modo A — Pair-review rapido
Para cambios pequeños:
1. Un agente implementa.
2. Otro revisa.
3. El implementador corrige.
4. Se verifica.

### Modo B — Fan-out por ownership
Para cambios medianos:
1. Coordinador divide archivos.
2. Implementadores trabajan en ownership no solapado.
3. Revisor revisa todo.
4. Integrador une.

### Modo C — Worktree por agente
Para cambios grandes/riesgosos:
1. Crear worktree/rama por agente.
2. Cada agente trabaja aislado.
3. Integrador compara diffs.
4. Merge controlado con pruebas.

No crear worktrees sin necesidad: cuestan disco y atencion.

### Modo D — Debate de diseño antes de editar
Para arquitectura/API:
1. Arquitecto propone.
2. Revisor desafia riesgos.
3. Tester propone criterios verificables.
4. Solo despues se edita.

## Contrato de handoff de codigo

Usar `ms.mensaje_tipo(..., type="handoff", requires_ack=True)` con:

```text
summary: objetivo en una linea
details:
  - archivos tocados:
  - cambios:
  - pruebas:
  - riesgos:
  - siguiente accion esperada:
evidence:
  - comandos
  - rutas
  - outputs relevantes
```

**Mejor (O26): usa la primitiva `ms.handoff(...)`** que FUERZA el contrato y rechaza un handoff incompleto —
la ambiguedad de especificacion en el traspaso es la causa #1 empirica de fallo multi-agente (~79%, MAST):
```python
ms.handoff("agent:codex",
    goal="...",            # OBLIGATORIO: el para-que (intent)
    next_step="...",       # OBLIGATORIO: siguiente accion
    acceptance="...",      # OBLIGATORIO: criterio de HECHO verificable (se prueba, no se declara)
    done="...", findings="archivos/cambios/riesgos", open_questions="...", constraints="...")
# requires_ack=True implicito. El receptor hace ack confirmando ENTENDIMIENTO (closed-loop), no solo recibo.
```
Detalle del porque y fuentes: O26 en `11_PROCESO_MEJORA_ECOSISTEMA.md` + `13_COMUNICACION_TIEMPO_REAL.md`.

## Protocolo de ARCHIVOS (`cerebro_coprog`) — OBLIGATORIO antes de editar código compartido

> Nació de un choque real (2026-06-17): dos sesiones editaban `cognition.py` sin lock; una tuvo que
> ADIVINAR por mtimes qué tocaba la otra. Esta es la regla para que no se repita. Lo usan IGUAL Claude y Codex.

**Antes de tocar CUALQUIER archivo de código de un proyecto con sesiones concurrentes:**

1. **Mira el tablero** (read-only, sin crear sesión, cuándo quieras):
   `py -3 ~\.cerebro\cerebro_coprog.py board <proyecto>`  → quién edita qué AHORA.
2. **Reclama el/los archivo(s)** desde tu sesión viva (el lock vive mientras tu sesión late):
   ```python
   import sys; sys.path.insert(0, r"~\.cerebro")
   import cerebro_coprog as cop
   from cerebro_multisesion import Multisesion
   ms = Multisesion("editar X", project="tu-proyecto-agente", agent="claude", runtime="claude-code")
   if cop.claim_all(ms, "cognition.py", "arbiter.py"):   # TODOS o NINGUNO
       ... editar ...
       cop.release(ms, "cognition.py", "arbiter.py")      # liberar al terminar
   else:
       ... NO editar: coordinar por ms.mensaje_tipo(type="blocker"/"handoff") y reintentar ...
   ```
3. **Si está tomado → NO edites.** Manda `mensaje_tipo(type="blocker"/"handoff", requires_ack=True)` y
   espera ack o a que se libere (o toma OTRO archivo/ítem disjunto mientras tanto).
4. **Ediciones largas:** `ms.latido()` periódico renueva tus locks (TTL 30 min). **Libera al terminar.**

`file:<archivo>` se normaliza por basename en minúsculas (abs/rel/mayúsculas colisionan). El tablero
descarta locks de sesiones muertas (PID muerto / sin latido >15 min) y locks viejos (>30 min) solos.

### ⚠️ El lock por runtime: quién lo SOSTIENE de verdad (descubierto 2026-06-17, ola T015)

El lock vive atado a un **proceso de sesión vivo con heartbeat**. Eso cambia quién está realmente
protegido según el runtime que edita — confundirlo da una **falsa sensación de seguridad**:

| Runtime | Cómo edita | ¿El lock protege? | Guard EFECTIVO |
|---|---|---|---|
| **Worker** (Codex / Haiku / Sonnet de sesión larga) | Su proceso de sesión sigue vivo mientras edita | **Sí** — `claim_all` retiene el lock durante toda la edición | `cerebro_coprog` (úsalo tal cual arriba) |
| **Claude Code como orquestador** | Llama `py -c` (proceso EFÍMERO) y edita con la herramienta Edit en **otro turno** | **No** — `claim_all(ms,...)` devuelve `True` pero el lock se LIBERA cuando ese `py -c` retorna, ANTES de que corra Edit | (1) chequeo **"file modified since read"** de Edit + (2) **sondear el board y re-leer fresco** antes de cada edición |

**Por qué:** el patrón `claim → editar → release` de arriba asume que claim y edición ocurren en el
**mismo proceso**. Claude Code nunca edita dentro de un `py -c`; edita con Edit en turnos posteriores →
el lock ya se evaporó. Por eso el guard real de Claude-Code es la **concurrencia optimista** de Edit
(Edit aborta si el archivo cambió desde tu última lectura → bloquea pisar una escritura en vuelo),
reforzada con un `board` previo. Verificado: choque en `config.py` con Codex/spacing — el punto de
contención típico es `config.py` (todas las lanes le añaden su flag). Memoria: [[coprog-locks-efimeros-claude]].

**Regla operativa para Claude-Code-orquestador:** antes de cada Edit a un archivo caliente →
`board <proyecto>` (read-only) → **Read fresco** del archivo → Edit. Si Edit aborta con "modified since
read", NO reintentes a ciegas: re-lee, confirma qué cambió (otro agente aterrizó), e integra.

**OMITE la ceremonia `claim_all`/`release` (O16, ahorro de tokens):** para Claude-Code es un **no-op**
(el lock muere al terminar el `py -c`, antes del Edit) → ejecutar esos bloques `py -c` gasta turnos y
tokens sin proteger nada. El `board`-poll ya **ve** el lock vivo de un worker (Codex/Haiku/Sonnet) si lo
hay, y el guard de Edit cubre la carrera. Reserva `claim_all`/`release` para los **workers** (proceso de
sesión vivo, que sí lo sostiene). Claude-Code: `board` → `Read` → `Edit`, y basta.

## Reglas duras
- **ANTES de editar un archivo de código compartido: reclámalo con `cop.claim_all(ms, ...)` (o `ms.reclamar("file:<archivo>")`). Si está tomado, NO lo edites — coordina por buzón. Revisa el tablero con `cerebro_coprog.py board`.**
- Nunca dos agentes editan el mismo archivo al mismo tiempo sin lock y coordinador.
- No se integra codigo sin pruebas o razon explicita de por que no se pudieron correr.
- No se acepta "vibe coding" autonomo para cambios sensibles.
- No se resuelven conflictos eligiendo un lado sin entender ambos.
- No se mezclan refactors no pedidos con bugfixes multi-agente.
- No se dejan locks vivos al cerrar.
- No se usan servidores/daemons/worktrees persistentes sin justificacion.

## Optimizacion de tokens
- Cada agente recibe solo su paquete de contexto: objetivo, ownership, archivos asignados y contrato esperado.
- El integrador conserva el mapa global; implementadores no deben leer todo el proyecto si no hace falta.
- Los handoffs deben ser breves y estructurados.
- La memoria durable guarda reglas aprendidas, no logs completos.

## Herramienta de co-programación: `cerebro_coprog.py` (PARCIALMENTE HECHA, 2026-06-17)

Creada tras el choque en `cognition.py`. Implementado (con `test_cerebro_coprog.py`, 5/5):
- ✅ **tablero read-only** de ownership de archivos (`board`/`check` CLI),
- ✅ **reclamo/liberación por archivo** (`claim`/`claim_all`/`release`/`who_has`) sobre la API de locks existente,
- ✅ normalización `file:<basename>` y cruce con la tarea de cada sesión.

Pendiente (para cuando se pida / haga falta, NO antes — YAGNI):
- plantilla de handoff de código autogenerada,
- marcado review/QA/integración,
- reporte final de la sesión de co-programación.
