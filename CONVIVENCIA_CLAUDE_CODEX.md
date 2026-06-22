# Convivencia Claude/Codex

Registro creado el 2026-06-16 para que Claude Code y Codex trabajen sobre el mismo cerebro sin pisarse.

Este archivo queda como puente especifico entre dos runtimes. La fuente neutral del ecosistema es `~\.cerebro\ECOSISTEMA_MULTIAGENTE.md`.

## Alcance
- `.cerebro` es la capa compartida de coordinacion: estado, locks, eventos, decisiones, buzon y conocimiento cross-proyecto.
- Claude mantiene su memoria operativa en `~\.claude\`.
- Codex mantiene su memoria operativa en `~\.codex\`.
- Los hubs raiz son espejos operativos: `~\CLAUDE.md` para Claude y `~\AGENTS.md` para Codex.

## Reglas de convivencia
1. Antes de tocar archivos de un proyecto, ambos agentes deben hacer Paso 0 multisesion via `~\.cerebro\cerebro_multisesion.py`.
2. Para recursos compartidos, usar locks globales: `gpu`, `vram`, `tu servidor LLM local`, `tu servidor LLM local_config`, `daemon_config`, `puerto_1234`.
3. Los cambios estructurales se documentan en el hub correspondiente y, si afectan a ambos agentes, tambien aqui o en `SKILLS_CROSS_PROYECTO.md`.
4. No copiar mecanicamente nombres de skills entre agentes. Usar el nombre real disponible en cada runtime.
5. `.cerebro` no reemplaza la memoria privada de cada agente; solo guarda coordinacion y conocimiento que deba ser visible para todos.

## Registro
- 2026-06-16: Codex entro al ecosistema y dejo evento/conocimiento en `.cerebro` con tags `codex`, `coordinacion`, `agents`.
- 2026-06-16: El ecosistema deja de definirse como "de Claude" y pasa a identidad multi-agente. `CLAUDE.md` y `AGENTS.md` quedan como adaptadores, no como fuente unica de verdad.
