# Protocolo Operativo Multi-Agente

## Entrada de cualquier agente
1. Leer el adaptador del runtime actual:
   - Claude Code: `~\CLAUDE.md`
   - Codex: `~\AGENTS.md`
2. Leer `~\.cerebro\00_INDICE.md`.
3. Si no es obvio que rutina aplica, consultar `12_HUB_PROCESOS.md`.
4. Elegir paquete de contexto minimo segun `11_PROCESO_MEJORA_ECOSISTEMA.md`.
5. Identificar proyecto y archivo de entrada local.
6. Ejecutar Paso 0 multisesion antes de editar.

## Paso 0
```python
import sys; sys.path.insert(0, r"~\.cerebro")
from cerebro_multisesion import Multisesion

ms = Multisesion("descripcion corta", project="nombre-proyecto", agent="codex", runtime="codex")
ms.estado()
ms.reclamar("recurso-o-tarea")
ms.leer_buzon()
ms.evento("inicio trabajo")
```

Si el runtime es Claude Code, usar `agent="claude"` y `runtime="claude-code"`. Si es otro agente, usar un identificador estable en minusculas.
Para integrar agentes nuevos, seguir `06_CONTRATO_NUEVO_AGENTE.md`.

## Durante el trabajo
- Registrar avances relevantes con `ms.evento(...)`.
- Registrar aprendizajes reutilizables con `ms.conocimiento(..., tags=[...])` (stream EFIMERO).
- Guardar HECHOS DURABLES (los que sirven a sesiones/agentes futuros) en la memoria compartida con
  `cerebro_memoria.recordar(...)`; buscarlos con `cerebro_memoria.buscar(...)`. Leer
  `.cerebro\memoria\MEMORIA.md` al arrancar.
- Usar locks globales para recursos compartidos.
- Usar mensajes por agente con `ms.mensaje("agent:codex", "...")` o `ms.mensaje("agent:claude", "...")` cuando el aviso no sea de un proyecto concreto.
- Para coordinacion viva, preferir `ms.mensaje_tipo(...)` con `type`, `priority`, `requires_ack`, `summary`,
  `details` y `evidence`. Si recibes un mensaje que requiere confirmacion, responder con `ms.ack(id, nota)`.
- Para progreso largo, usar `ms.progreso(progress_token, progress, total, message)` con frecuencia moderada.
- Para pedir que otra sesion pare una operacion, usar `ms.cancelacion(request_id, reason, para)`; no asumas que la
  cancelacion ocurrio hasta recibir ack o evento de cierre.
- Para observar actividad sin releer todo, usar `cerebro_watch.py --once`; `--follow` solo con duracion maxima.
- Priorizar la salud del computador: revisar recursos/locks antes de tareas pesadas y parar si hay riesgo. Ver `10_PRIORIDAD_SALUD_COMPUTADOR.md`.
- No tocar credenciales, historiales o caches salvo orden explicita.
- No relanzar daemons, loops autonomos ni acciones GUI sin confirmacion.

## Cierre
1. Verificar con comandos o inspeccion real.
2. Actualizar la documentacion minima necesaria segun `07_REGLA_ACTUALIZACION_DOCUMENTAL.md`.
3. Si fue una optimizacion del ecosistema, actualizar `11_PROCESO_MEJORA_ECOSISTEMA.md`.
4. Registrar resumen en `03_BITACORA_MULTIAGENTE.md` si el cambio fue estructural.
5. Registrar cierre con `ms.evento(...)` y liberar via `ms.despedir()`.
6. Informar al usuario que se verifico y que queda pendiente si algo no pudo comprobarse.

## Politica de cambios documentales
- Cambios neutrales o cross-runtime: `.cerebro`.
- Cambios Claude-only: `CLAUDE.md` o `.claude`.
- Cambios Codex-only: `AGENTS.md` o `.codex`.
- Cambios de proyecto: adaptador del proyecto y su memoria/plan local.
