# Indice del Ecosistema Multi-Agente

Entrada neutral para entender el cerebro compartido de `~`.

> 🚀 **Setup de un clon nuevo:** `SETUP.md` (completa lo sensible: claves gratis, rutas; lo no sensible ya viene listo).

> ⚡ **Eficiencia (primordial):** para un dato puntual, `py .cerebro\cerebro_memoria.py buscar "<texto>"`
> PRIMERO (recall por significado); abre el doc dueño solo si el hecho no basta. Hábitos de tokens:
> `TOKENS_HABITOS.md`. Coordinación viva: `cerebro_multisesion.py` (Paso 0/locks/buzón),
> `cerebro_coprog.py` (locks por archivo), `cerebro_tareas_modelo.py` (cola de tareas por modelo),
> `cerebro_grafo.py` (grafo de código on-demand: `simbolo <X> <ruta>` = def/quién-llama · `arquitectura <ruta>` = mapa de repo grande).
> **Salud de coordinación:** `cerebro_salud.py` (read-only) — panel de lo que estaba invisible: locks tomados (marca GLOBAL/STALE), dead-letters vencidos y conflictos de hechos. `--json` para el hub.
> **CLI único:** `py cerebro.py <area> [args]` despacha a TODOS los módulos (tareas/modelo/coord/salud/watch/checkpoint/hechos/memoria/coprog/grafo/skills); base común en `cerebro_core.py`.

## Mapa de documentos (abre SOLO el que aplique — no leerlos todos)
1. `ECOSISTEMA_MULTIAGENTE.md` — identidad, principios y politica de documentos.
2. `01_ARQUITECTURA.md` — capas del sistema, propiedad de cada carpeta y limites + **ÁRBOL canónico del ecosistema** (mapa de qué vive dónde; actualizado 2026-06-19).
3. `02_PROTOCOLO_OPERATIVO.md` — como entra y trabaja cualquier agente.
4. `SKILLS_CROSS_PROYECTO.md` — mapa de capacidades por proyecto/runtime.
5. `03_BITACORA_MULTIAGENTE.md` — registro humano de cambios estructurales. _(Consulta puntual, NO cargar entero.)_
6. `04_CHEQUEOS_SEGURIDAD.md` — checklist de seguridad y funcionalidad.
7. `05_MIGRACION_PRIVADA_PENDIENTE.md` — tareas diferidas para Claude si alguna vez hay que mover memoria privada, historiales, credenciales o caches.
8. `06_CONTRATO_NUEVO_AGENTE.md` — contrato para que un agente futuro se integre sin romper convivencia.
9. `07_REGLA_ACTUALIZACION_DOCUMENTAL.md` — regla de actualizacion continua para evitar confusion entre sesiones/agentes.
10. `08_REGISTRO_ESTADO_PRIVADO.md` — inventario neutral de memorias privadas, historiales, credenciales y caches.
11. `09_MAPA_GLOBAL_MEMORIA.md` — mapa global de donde vive cada tipo de memoria y como globalizarla sin romper runtimes.
12. `10_PRIORIDAD_SALUD_COMPUTADOR.md` — regla universal para priorizar estabilidad, recursos y seguridad del equipo.
13. `11_PROCESO_MEJORA_ECOSISTEMA.md` — rutina para simplificar actualizacion de documentos, mejorar eficiencia de agentes y reducir gasto de tokens.
14. `12_HUB_PROCESOS.md` — tabla unica para elegir que proceso/documento abrir sin leer todo.
15. `13_COMUNICACION_TIEMPO_REAL.md` — investigacion y propuesta para coordinacion viva entre agentes sin romper seguridad.
16. `14_COPROGRAMACION_MULTIAGENTE.md` — protocolo para que agentes escriban codigo juntos con ownership, revision, pruebas e integracion segura. _(Se abre solo al co-programar; resumen en memoria, enlazar no cargar.)_
17. `15_COORDINACION_CLAUDE_PILOTO.md` — handoff y plan para coordinar Codex/Claude durante mejoras de infraestructura de tu-proyecto-agente.
18. `16_HECHOS_ACTIVADORES_CODEX.md` — disparadores para que Codex actue proactivamente al detectar handoffs, reviews, bloqueos o trabajo conjunto.
19. `17_ROUTER_POR_MODELO.md` — router de tareas por modelo (hablas a Opus y reparte al tier mas barato; activador por hook SessionStart + aviso /clear por PreCompact).
20. `18_RECURSOS_IA_LOCALES.md` — protocolo para GPU/tu servidor LLM local/daemons IA local y batch externo (tu-tienda Mano Derecha, tu-proyecto-agente LoRA, vLLM/Kaggle).
21. `19_RECUPERACION_POST_CRASH.md` — continuidad ante muerte súbita: checkpoint atómico frecuente (`cerebro_checkpoint.py`) + RECOVERY MODE al abrir, sin perder contexto.
22. `20_RED_ROLES_IA.md` — red de roles por IA/modelo: `buscador` (Gemini/OpenAI/Perplexity), arquitecto, implementador, mecanico, verificador y enlace con el router por modelo.
23. 21_PROTOCOLO_COMPROBACION_CALIDAD.md — auditoria integral del ecosistema y proyectos para detectar fallos, riesgos y mejoras con evidencia.
24. `22_OPENCLAW_VIGILANTE.md` — OpenClaw como vigilante read-only always-on (observa git+salud+tareas y avisa por Telegram; modelo local; NO coordina ni modifica). _(Excepción aprobada a la Regla #3.)_

## Adaptadores
| Runtime | Adaptador raiz | Uso |
|---|---|---|
| Claude Code | `~\CLAUDE.md` | Entrada compacta para sesiones Claude. |
| Codex | `~\AGENTS.md` | Entrada compacta para sesiones Codex. |

## Proyectos registrados
Los proyectos son **personales** → viven en `proyectos.local.toml` (gitignored), no en el código.
Auto-config: `py cerebro_init.py` (detecta y propone) · plantilla `proyectos.example.toml` · cómo
estructurar un proyecto (incl. **fuera de OneDrive** por salud del PC): `ESTRUCTURA_PROYECTOS.md`.
`cerebro_memoria` (áreas) y `cerebro_checkpoint` (inferencia por cwd) leen esa config.

| Proyecto | Ruta | Adaptadores actuales |
|---|---|---|
| tu-tienda | `C:\tu-tienda\` | `CLAUDE.md`, `AGENTS.md` |
| tu-proyecto-aprendizaje | `~\tu-proyecto-aprendizaje\` | `CLAUDE.md`, `AGENTS.md` |
| tu-proyecto-agente | `~\tu-proyecto-agente\` | `CLAUDE.md`, `AGENTS.md` |
| tu-proyecto-web | `~\tu-proyecto-web\` | `CLAUDE.md`, `AGENTS.md` |
| tu-proyecto-automatizacion | `~\tu-proyecto-automatizacion\` | `CLAUDE.md`, `AGENTS.md` |
| tu-proyecto-juegos | `~\tu-proyecto-juegos\` | `CLAUDE.md`, `AGENTS.md` |

## Investigación del ecosistema
Lo INVESTIGADO sobre infraestructura compartida (no tu-proyecto-agente) está mapeado en
`investigacion_recursos\INDICE.md` (corpus B = recursos Claude Code + backlog vetado; corpus C =
comunicación multi-agente O18–O26, ya implementada). Es el gemelo del roadmap de tu-proyecto-agente (corpus A,
`tu-proyecto-agente\research\`). Reparto 2-Opus en thread `org-investigacion-2opus`.

## Memoria durable compartida
Los hechos durables de TODOS los agentes viven en `.cerebro\memoria\` (un hecho por archivo + indice
`MEMORIA.md`). Leer/escribir con `cerebro_memoria.py` (`recordar`/`buscar`/`reindexar`). Fuente unica;
no crear memorias paralelas. Detalle en `09_MAPA_GLOBAL_MEMORIA.md` y `11` (O11).

## Regla corta
Ningun agente es el dueño del ecosistema. `.cerebro` coordina; cada runtime adapta.

## Integracion futura
Todo agente nuevo debe seguir `06_CONTRATO_NUEVO_AGENTE.md` antes de tocar proyectos.

## Regla de memoria privada
No mover memorias privadas, historiales, credenciales ni caches durante reorganizaciones generales salvo necesidad concreta, backup y verificacion. Inventario en `08_REGISTRO_ESTADO_PRIVADO.md`; protocolo diferido en `05_MIGRACION_PRIVADA_PENDIENTE.md`.

## Regla de documentacion continua
Todo cambio estructural debe actualizar la documentacion minima necesaria antes de cerrar. Ver `07_REGLA_ACTUALIZACION_DOCUMENTAL.md`.

## Regla de salud del computador
La salud del computador tiene prioridad sobre cualquier tarea. Ver `10_PRIORIDAD_SALUD_COMPUTADOR.md`.

## Proceso de mejora del ecosistema
Cuando el usuario mencione "mejora del ecosistema" u otra optimizacion, aplicar `11_PROCESO_MEJORA_ECOSISTEMA.md`: facilitar actualizacion de documentos, reducir lectura, duplicacion, confusion y gasto de tokens sin perder seguridad ni efectividad.

## Hub de procesos
Si no sabes que rutina aplica, abre `12_HUB_PROCESOS.md` y carga solo el documento dueño del proceso.
