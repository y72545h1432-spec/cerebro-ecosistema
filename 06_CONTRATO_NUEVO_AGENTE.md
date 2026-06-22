# Contrato para Integrar un Nuevo Agente

Objetivo: que cualquier agente futuro pueda entender y trabajar con el ecosistema existente sin romper la coordinacion entre agentes.

## Requisitos minimos
Un agente nuevo debe tener:
- Nombre estable en minusculas: `agent`.
- Runtime/superficie estable: `runtime`.
- Archivo adaptador propio si necesita reglas especiales.
- Capacidad de leer `~\.cerebro\00_INDICE.md`.
- Capacidad de registrar Paso 0 en `cerebro_multisesion.py`.
- Capacidad de leer y emitir mensajes tipados (`mensaje_tipo`), confirmar recepcion (`ack`), reportar progreso (`progreso`) y solicitar cancelacion (`cancelacion`) cuando aplique.
- Capacidad de leer la memoria durable compartida `~\.cerebro\memoria\MEMORIA.md` y de
  escribir hechos con `cerebro_memoria.py` (`recordar`/`buscar`/`reindexar`). NO crear una memoria
  durable paralela: la fuente unica es `.cerebro\memoria\`.

## Identidad
Formato recomendado:
```python
ms = Multisesion(
    "descripcion corta del trabajo",
    project="nombre-proyecto",
    agent="nombre-agente",
    runtime="superficie-o-app"
)
```

Ejemplos:
- `agent="claude"`, `runtime="claude-code"`
- `agent="codex"`, `runtime="codex"`
- `agent="local-qwen"`, `runtime="tu servidor LLM local"`
- `agent="browser-agent"`, `runtime="mcp-browser"`

## Adaptador minimo
Si el agente necesita entrada propia, crear un archivo en `~\` o en el proyecto:

```md
# <AGENTE>.md — Adaptador <agente> del ecosistema multi-agente

> Fuente neutral: `~\.cerebro\00_INDICE.md`.

## Arranque obligatorio
1. Leer `~\.cerebro\00_INDICE.md`.
2. Ejecutar Paso 0 con `agent="<agente>"` y `runtime="<runtime>"`.
3. Leer el adaptador del proyecto y la memoria durable compartida (`.cerebro\memoria\MEMORIA.md`).
4. Respetar locks, confirmaciones y limites de memoria privada.
5. Guardar hechos durables con `cerebro_memoria.py` (no en una memoria propia paralela).
```

## Protocolo de convivencia
1. No asumir propiedad del ecosistema.
2. No copiar nombres de skills/herramientas de otro runtime sin verificar que existan.
3. Usar `project` para dominio de trabajo y `agent` para identidad.
4. Reclamar locks antes de editar archivos compartidos.
5. Usar locks globales para recursos fisicos o servicios compartidos.
6. Usar mensajes tipados para handoffs, bloqueos, solicitudes de revision, progreso y cierre.
7. Confirmar con `ack` los mensajes que tengan `requires_ack=True`.
8. Registrar eventos importantes.
9. Usar `conocimiento()` solo para aprendizajes reutilizables.
10. No mover memorias privadas/historiales/credenciales/caches sin tarea dedicada.

## Mensajeria
- Mensaje a todos: `ms.mensaje("*", "...")`
- Mensaje a proyecto: `ms.mensaje("tu-tienda", "...")`
- Mensaje a agente: `ms.mensaje("agent:codex", "...")`
- Mensaje tipado: `ms.mensaje_tipo("agent:claude", type="handoff", priority="high", requires_ack=True, summary="...", details="...")`
- Confirmacion: `ms.ack("<mensaje_id>", "recibido")`
- Progreso: `ms.progreso("<token>", 50, total=100, message="mitad del trabajo")`
- Cancelacion: `ms.cancelacion("<request_id>", "motivo", para="agent:codex")`

## Checklist de alta
- [ ] Nombre `agent` definido.
- [ ] `runtime` definido.
- [ ] Adaptador creado si hace falta.
- [ ] Entrada agregada a `00_INDICE.md`.
- [ ] Entrada agregada a `ECOSISTEMA_MULTIAGENTE.md`.
- [ ] Entrada agregada a `03_BITACORA_MULTIAGENTE.md`.
- [ ] Prueba de `Multisesion(..., agent=..., runtime=...)` ejecutada.
- [ ] No se tocaron memorias privadas de otros agentes.
