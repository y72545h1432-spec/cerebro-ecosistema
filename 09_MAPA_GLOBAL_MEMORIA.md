# Mapa Global de Memoria

Mapa neutral para que cualquier agente sepa donde buscar memoria sin asumir que todo vive en Claude.

## Fuentes por tipo

| Necesidad | Fuente primaria | Fuente secundaria | Nota |
|---|---|---|---|
| **Hechos durables (cualquier agente)** | `.cerebro\memoria\MEMORIA.md` + `<area>\<slug>.md` (via `cerebro_memoria.py`) | `.cerebro\_backups\memoria_claude_*.zip` | **Fuente UNICA compartida** (claude/codex/futuros). Escribir SIEMPRE con el helper (mantiene el indice). |
| Reglas multi-agente | `.cerebro\00_INDICE.md` | `.cerebro\ECOSISTEMA_MULTIAGENTE.md` | Siempre empezar aqui. |
| Estado vivo/locks | `%LOCALAPPDATA%\cerebro\multisesion.json` via `cerebro_multisesion.py` | `.cerebro\README.md` | No editar JSON a mano. |
| Reglas Claude | `~\CLAUDE.md` | `CLAUDE.md` del proyecto | Adaptador Claude. |
| Reglas Codex | `~\AGENTS.md` | `AGENTS.md` del proyecto | Adaptador Codex. |
| Feedback / estado durable / referencias | `.cerebro\memoria\<area>\` (migrado el 2026-06-16) | `.claude\...\memory\MEMORY.md.pre-neutral.bak` | Los 102 hechos de Claude se migraron al almacen neutral compartido. |
| (legado) `~/.claude/.../memory/MEMORY.md` | **redirige** al indice neutral | — | Ya es un stub: la memoria real vive en `.cerebro\memoria\`. |
| Memoria viajera tu-proyecto-automatizacion | `D:\tu-proyecto-automatizacion\02_MEMORIA_COMPARTIDA.md` y `D:\tu-proyecto-automatizacion\memoria\` cuando la USB este conectada | `~\tu-proyecto-automatizacion\02_MEMORIA_COMPARTIDA.md` y `memoria\` | Sincronizada localmente el 2026-06-16 con backup previo. |
| Referencias tecnicas | `.claude\projects\C--Users-<TU_USUARIO>\memory\reference_*.md` | `.cerebro\SKILLS_CROSS_PROYECTO.md` | Hacer neutral lo que sea cross-agent. |
| Diario reciente | `.remember\now.md`, `.remember\recent.md`, `today-*.md` | multisesion eventos/conocimiento | No copiar logs completos. |
| Credenciales | runtime privado (`.claude`, `.codex`) | ninguna | No abrir, no documentar contenido. |
| Caches | runtime privado | ninguna | No migrar; limpiar solo con autorizacion. |

## Protocolo para globalizar una memoria
1. Identificar si la memoria es:
   - regla universal,
   - regla de proyecto,
   - preferencia del usuario,
   - referencia tecnica,
   - secreto/cache/historial privado.
2. Si es secreto/cache/historial privado: no globalizar contenido.
3. Si aplica a varios agentes: resumir en `.cerebro` y enlazar fuente.
4. Si aplica a un runtime: actualizar su adaptador.
5. Si aplica a un proyecto: actualizar adaptador/documento local.
6. Registrar el cambio en `03_BITACORA_MULTIAGENTE.md` y `ms.conocimiento(...)`.

## Principio de no confusion
Una memoria debe tener una fuente principal. Si se necesita en varios sitios, enlazarla o resumirla, no duplicarla literalmente.
