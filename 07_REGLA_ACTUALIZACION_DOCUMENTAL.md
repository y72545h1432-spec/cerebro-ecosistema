# Regla de Actualizacion Documental Continua

Objetivo: evitar confusion entre agentes, sesiones y proyectos manteniendo actualizados solo los documentos necesarios.

## Regla principal
Todo agente que haga un cambio estructural debe actualizar la documentacion minima afectada antes de cerrar la sesion.

## Que cuenta como cambio estructural
- Nuevo agente/runtime.
- Nuevo proyecto.
- Nueva regla universal.
- Cambio en multisesion, locks, recursos globales o protocolo operativo.
- Cambio en adaptadores `CLAUDE.md`, `AGENTS.md` u otro runtime.
- Nuevo skill/herramienta cross-proyecto.
- Cambio en rutas, comandos de arranque, dashboards o servicios compartidos.
- Decision que puede confundir a una sesion futura si no queda escrita.

## Donde escribir
| Cambio | Documento obligatorio |
|---|---|
| Identidad/protocolo multi-agente | `ECOSISTEMA_MULTIAGENTE.md` |
| Orden de lectura o mapa documental | `00_INDICE.md` |
| Capas, ownership, rutas, recursos | `01_ARQUITECTURA.md` |
| Procedimiento de trabajo | `02_PROTOCOLO_OPERATIVO.md` |
| Registro humano de cambios | `03_BITACORA_MULTIAGENTE.md` |
| Seguridad/validacion | `04_CHEQUEOS_SEGURIDAD.md` |
| Memoria privada o caches a migrar despues | `05_MIGRACION_PRIVADA_PENDIENTE.md` |
| Nuevo agente/runtime | `06_CONTRATO_NUEVO_AGENTE.md` + indice |
| Skills/capacidades cross-proyecto | `SKILLS_CROSS_PROYECTO.md` |
| Reglas runtime Claude | `CLAUDE.md` |
| Reglas runtime Codex | `AGENTS.md` |
| Reglas locales de proyecto | `CLAUDE.md`/`AGENTS.md` del proyecto |

## Como escribir
- Enlazar, no pegar.
- Actualizar la fuente neutral primero si el cambio afecta a mas de un agente.
- Mantener adaptadores cortos; deben apuntar al documento neutral.
- Registrar fecha y motivo en `03_BITACORA_MULTIAGENTE.md`.
- Si no estas seguro de donde va, registrar en bitacora y mencionar el documento candidato.

## Que no hacer
- No duplicar bloques largos entre `CLAUDE.md` y `AGENTS.md`.
- No convertir un adaptador de runtime en fuente unica de verdad.
- No esconder decisiones importantes solo en memoria privada.
- No mover credenciales, historiales o caches para "ordenar"; documentar en `05_MIGRACION_PRIVADA_PENDIENTE.md`.

## Cierre obligatorio
Antes de responder "listo", el agente debe comprobar:
1. La documentacion minima afectada fue actualizada.
2. La bitacora registra el cambio si fue estructural.
3. `.cerebro` recibio evento/conocimiento si afecta a otros agentes.
4. No quedan instrucciones contradictorias entre fuente neutral y adaptadores.
5. Si el cambio fue una optimizacion del ecosistema, quedo incorporado en `11_PROCESO_MEJORA_ECOSISTEMA.md`.
