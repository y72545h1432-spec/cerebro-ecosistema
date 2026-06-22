# Ecosistema Multi-Agente

Fuente neutral del cerebro compartido de `~`.

Este ecosistema no pertenece a un agente especifico. Claude Code, Codex y futuros agentes son runtimes que entran por adaptadores propios y coordinan trabajo mediante `.cerebro`.

## Principio
- `.cerebro` es la capa comun: coordinacion, locks, eventos, decisiones, buzon y conocimiento compartido.
- Cada agente conserva su memoria privada en su runtime: `.claude`, `.codex`, `.agents` u otro directorio equivalente.
- Los archivos de entrada (`CLAUDE.md`, `AGENTS.md`, etc.) son adaptadores. No deben convertirse en fuentes divergentes de verdad.
- La fuente neutral para convivencia y coordinacion entre agentes vive aqui.

## Adaptadores actuales
| Agente/runtime | Entrada | Memoria/config privada | Rol |
|---|---|---|---|
| Claude Code | `~\CLAUDE.md` | `~\.claude\` | Adaptador Claude del ecosistema multi-agente. |
| Codex | `~\AGENTS.md` | `~\.codex\` y skills en `~\.agents\skills\` | Adaptador Codex del ecosistema multi-agente. |

Para integrar otro agente, seguir `~\.cerebro\06_CONTRATO_NUEVO_AGENTE.md`.

## Protocolo obligatorio
1. Leer el adaptador del runtime actual (`CLAUDE.md`, `AGENTS.md` o equivalente).
2. Antes de tocar proyectos, ejecutar Paso 0 multisesion agentico con `~\.cerebro\cerebro_multisesion.py`, pasando `agent`/`runtime` cuando el agente lo sepa.
3. Reclamar locks por proyecto para tareas de escritura y locks globales para recursos compartidos (`gpu`, `vram`, `tu servidor LLM local`, `tu servidor LLM local_config`, `daemon_config`, `puerto_1234`).
4. Registrar cambios estructurales con `ms.evento(...)` y aprendizajes reutilizables con `ms.conocimiento(...)`.
5. Si el cambio afecta a mas de un agente, actualizar este documento o `SKILLS_CROSS_PROYECTO.md`, y enlazar desde los adaptadores necesarios.
6. Confirmar antes de acciones irreversibles, externas, con costo, GUI o daemons autonomos.

## Politica de documentos
- `ECOSISTEMA_MULTIAGENTE.md`: identidad neutral y protocolo compartido.
- `00_INDICE.md`: entrada ordenada a toda la documentacion del ecosistema.
- `01_ARQUITECTURA.md`: capas, ownership y limites.
- `02_PROTOCOLO_OPERATIVO.md`: procedimiento comun de entrada, trabajo y cierre.
- `03_BITACORA_MULTIAGENTE.md`: bitacora humana de cambios estructurales.
- `04_CHEQUEOS_SEGURIDAD.md`: checklist de seguridad y funcionalidad.
- `05_MIGRACION_PRIVADA_PENDIENTE.md`: tareas diferidas si hay que mover memorias privadas, historiales, credenciales o caches.
- `06_CONTRATO_NUEVO_AGENTE.md`: contrato de alta para futuros agentes/runtimes.
- `07_REGLA_ACTUALIZACION_DOCUMENTAL.md`: regla de actualizacion continua para evitar confusion.
- `08_REGISTRO_ESTADO_PRIVADO.md`: inventario neutral de estado privado por runtime.
- `09_MAPA_GLOBAL_MEMORIA.md`: mapa global para encontrar/globalizar memoria sin romper owners.
- `10_PRIORIDAD_SALUD_COMPUTADOR.md`: regla universal de estabilidad y cuidado del equipo.
- `11_PROCESO_MEJORA_ECOSISTEMA.md`: proceso permanente para simplificar actualizacion de documentos, mejorar eficiencia de agentes y reducir gasto de tokens.
- `12_HUB_PROCESOS.md`: selector corto de procesos para elegir que documento dueño abrir.
- `CONVIVENCIA_CLAUDE_CODEX.md`: puente especifico Claude/Codex y registro historico de la integracion inicial.
- `SKILLS_CROSS_PROYECTO.md`: mapa de capacidades por runtime/proyecto y huecos recurrentes.
- `CLAUDE.md`: instrucciones compactas para Claude Code.
- `AGENTS.md`: instrucciones compactas para Codex.

## Politica de memoria privada
- La migracion multi-agente puede mover memorias privadas, historiales, credenciales o caches solo si hay necesidad concreta, backup, rollback y verificacion runtime.
- En esta fase final no se movieron fisicamente porque las rutas son contratos vivos de Claude/Codex/remember.
- Se globalizo el acceso mediante inventario neutral (`08_REGISTRO_ESTADO_PRIVADO.md`) y mapa de memoria (`09_MAPA_GLOBAL_MEMORIA.md`).
- Si en el futuro fuera necesario moverlos, debe hacerse como tarea separada siguiendo `05_MIGRACION_PRIVADA_PENDIENTE.md`.

## Politica de actualizacion documental
- Todo cambio estructural debe actualizar la documentacion minima afectada antes de cerrar sesion.
- La fuente neutral se actualiza antes que los adaptadores si el cambio afecta a mas de un agente.
- Detalle operativo: `~\.cerebro\07_REGLA_ACTUALIZACION_DOCUMENTAL.md`.

## Politica de salud del computador
- La estabilidad del equipo tiene prioridad sobre cualquier objetivo del agente.
- Tareas pesadas o persistentes requieren criterio, locks, limites y confirmacion cuando corresponda.
- Detalle operativo: `~\.cerebro\10_PRIORIDAD_SALUD_COMPUTADOR.md`.

## Politica de eficiencia y tokens
- Los agentes deben cargar solo el paquete de contexto necesario.
- Los adaptadores deben ser cortos y enlazar al detalle.
- Las optimizaciones nuevas del ecosistema se agregan al proceso permanente.
- Si hay duda sobre que rutina aplicar, consultar `12_HUB_PROCESOS.md` antes de abrir documentos largos.
- Detalle operativo: `~\.cerebro\11_PROCESO_MEJORA_ECOSISTEMA.md`.

## Registro de cambios estructurales
- 2026-06-16: Codex migra la identidad documental de "ecosistema de Claude" a ecosistema multi-agente. Se conserva compatibilidad con `CLAUDE.md` y se registra todo en `.cerebro`.
- 2026-06-16: `cerebro_multisesion.py` sube a multisesion agentica schema 4: sesiones, locks, eventos, decisiones y conocimiento registran `agent`/`runtime`; el shim tu-tienda queda compatible y ya no centraliza identidad Claude.
- 2026-06-16: Se agrega contrato de alta para nuevos agentes, con identidad `agent/runtime`, adaptador minimo, mensajeria y checklist.
- 2026-06-16: Se agrega regla de actualizacion documental continua para evitar confusion entre sesiones/agentes.
- 2026-06-16: Se autoriza evaluar movimiento de estado privado; se decide no mover fisicamente por seguridad runtime y se crea inventario/mapa neutral de memoria.
- 2026-06-16: Se agrega regla universal de priorizar la salud del computador.
- 2026-06-16: Se agrega proceso permanente de mejora del ecosistema para simplificar docs, aumentar eficiencia y reducir tokens.
- 2026-06-16: Se aclara que la facilidad de actualizacion se refiere especificamente a documentos y se agrega O9: un solo punto de edicion por tema.
- 2026-06-16: Se agrega hub de procesos para centralizar rutinas y reducir carga de contexto.
