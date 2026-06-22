# Bitacora Multi-Agente

Registro humano de cambios estructurales del ecosistema.

## 2026-06-18 — Investigación infinita tu-proyecto-juegos

Autor runtime: Codex.

Motivo:
- El usuario pidio una investigacion infinita sobre el proyecto `tu-proyecto-juegos` y registrarla como lo hacen las sesiones de Claude.

Metodo:
- Se revisaron skills antes de implementar: `arrancar-area`, `gui-control-seguro`, mapa cross-proyecto y hub de procesos.
- Se hizo Paso 0 multisesion en project=`tu-proyecto-juegos` y lock `investigacion-infinita-tu-proyecto-juegos`.
- Se reviso el estado local (`CLAUDE.md`, `AGENTS.md`, `PLAN.md`, `ESTADO_PARTIDA.md`, `gui_control`, memoria durable).
- Se consultaron fuentes actuales sobre Roblox, Grow a Garden y agentes GUI/juegos.

Cambios:
- Se creo `~\tu-proyecto-juegos\INVESTIGACION_INFINITA.md`.
- Se creo registro tipo Claude en `.cerebro\investigacion_recursos\II_JUGAR_ROBLOX\` con `INDICE.md`, `GRAFO.md`, `BACKLOG.md` y `FUENTES.md`.
- Se enlazo la investigacion desde `tu-proyecto-juegos\AGENTS.md`, `CLAUDE.md`, `ESTADO_PARTIDA.md` y `SKILLS_CROSS_PROYECTO.md`.

Decision vigente:
- El proyecto esta listo para una ola empirica, no para mas caminata a ciegas.
- Antes de intentar $1M: mapear landmarks, usar acciones atomicas, registrar estado y completar un ciclo plantar/cosechar/vender verificado.
- Hueco prioritario: skill/proceso `roblox-turn-loop`.
- 2026-06-18 18:02: se agregaron olas 2-4: contrato formal de turno, modo prueba controlado y log semantico/replay de turnos. Estado sigue abierto, no saturado; falta ola empirica con Roblox abierto.

## 2026-06-18 — Investigación infinita tu-tienda Mano Derecha (ola 2)

Autor runtime: Codex.

Motivo:
- El usuario pidio iniciar investigacion infinita para tu-tienda Mano Derecha.

Cambios:
- Se extendio `C:\tu-tienda\DOCUMENTACION\INVESTIGACION_ACELERAR_MANO_DERECHA_2026-06-18.md` con estado vivo, ETA, ramas saturadas y backlog accionable.
- Se creo `C:\tu-tienda\GUIAS\MANO_DERECHA_BATCH_EXTERNO.md` como runbook de exportar/procesar/fusionar batch externo.
- Se enlazo el runbook desde `GUIAS\INDICE.md`, `CLAUDE.md`, `AGENTS.md`, `GUIAS\MANO_DERECHA_LOCAL.md` y `.cerebro\18_RECURSOS_IA_LOCALES.md`.

Decision vigente:
- El daemon local esta vivo y estable; no subir paralelismo local.
- Siguiente accion optima: cerrar batch externo con validador pre-merge y prueba pequena antes de miles de tareas.

## 2026-06-18 — Investigación de skills generales + contrato cross-runtime

Autor runtime: Codex.

Motivo:
- El usuario pidio una investigacion infinita de skills generales siguiendo el proceso de skills del ecosistema.

Metodo:
- Se aplico `arrancar-area` + `find-skills` y se hizo fan-out con 3 subagentes: inventario local, ecosistema externo e integracion documental.
- Se revisaron skills locales de `.claude\skills`, `.agents\skills` y skills de plugins Codex en `.codex\plugins\cache`.
- Se consulto investigacion externa sobre agent skills para evitar instalar por popularidad sin verificacion.

Cambios:
- Se reestructuro `SKILLS_CROSS_PROYECTO.md` como fuente de verdad con contrato cross-runtime, ubicacion real de skills, proceso de descubrimiento y backlog.
- Se agrego el proceso "Skills generales / capacidades" al `12_HUB_PROCESOS.md`.
- Se aclararon en `AGENTS.md` y `CLAUDE.md` las diferencias entre nombres reales por runtime y criterio comun.
- Se enlazo `C:\tu-tienda\AGENTS.md` al bloque tu-tienda del mapa central para que Codex no duplique catalogos.
- Se agrego una ola GitHub al `REGISTRO_SKILLS_EXTERNAS.md`: `anthropics/skills`, `vercel-labs/agent-skills`, `AgentSkillOS`, `SkillWiki`, `skilltester` y `SWE-Skills-Bench`.
- Se amplio la investigacion infinita con ola de saturacion: `scienceaix/agentskills`, `MCP-Flow`, riesgos OpenClaw/ClawHub y papers de seguridad/evaluacion de skills.
- Se agrego ola 3: candidatas concretas `writing-guidelines`, `react-best-practices`, `vercel-optimize`, `webapp-testing`; y referencias de estandar/validacion `Skilldex`, `SkillMOO`, `SkillRevise`, `SkillX`.
- Se agrego ola 4: busqueda por huecos CI/CD, observabilidad, arquitectura, docs vivas y GUI. No aparecieron skills externas maduras para los tres primeros; se registro `VISUALSKILL` como referencia multimodal GUI no instalable por repo 404.
- Se agrego ola 5: busqueda por dominios sensibles tu-tienda/ecosistema (Shopify/ecommerce, marketing, browser, secrets) y portabilidad. Sin candidatos externos superiores; se registro `SkCC` como referencia para adaptacion cross-runtime.

Decision vigente:
- No instalar skills externas todavia.
- Prioridad alta: adaptar `investigacion-infinita` a `.agents\skills` para Codex y definir gobernanza de instalacion externa.
- Regla aclarada por el usuario: las skills se revisan antes de la implementacion.
- Cualquier skill externa debe revisarse como supply chain: `SKILL.md`, scripts, permisos, dependencias y contexto del repositorio.
- Dominios con credenciales/acciones externas (Shopify, ads, email, cloud, browser, secrets) quedan bloqueados para instalaciones externas hasta sandbox + revision manual + OK del usuario.

## 2026-06-18 — Recursos IA locales/batch (O27) + integración Mano Derecha

Autor runtime: Codex.

Motivo:
- El usuario pidio integrar la investigacion de aceleracion de tu-tienda Mano Derecha en la configuracion del ecosistema para que funcione de forma simple, conjunta y segura.

Cambios:
- Se creo `18_RECURSOS_IA_LOCALES.md` como documento dueño para GPU/tu servidor LLM local/Qwen/daemons IA local/batch externo.
- Se enlazo desde `00_INDICE.md`, `12_HUB_PROCESOS.md`, `10_PRIORIDAD_SALUD_COMPUTADOR.md` y O27 en `11_PROCESO_MEJORA_ECOSISTEMA.md`.
- Se enlazo tu-tienda Mano Derecha desde `C:\tu-tienda\CLAUDE.md`, `C:\tu-tienda\AGENTS.md`, `GUIAS\MANO_DERECHA_LOCAL.md` y `DOCUMENTACION\INDICE.md`.
- Se actualizo el adaptador raiz Codex `~\AGENTS.md` para tratar tu servidor LLM local/GPU como recurso compartido con documento dueño.

Decision vigente:
- No subir paralelismo local de Mano Derecha en <GPU> <VRAM>.
- Aceleracion local segura: experimento `max_tokens` adaptativo.
- Aceleracion fuerte: export/import de batch externo con vLLM/Kaggle/Colab/RunPod.

## 2026-06-18 — Investigacion-saturacion (ola 5) + O26 contrato de handoff

Autor runtime: Claude (Opus).

Motivo:
- El usuario pidio una investigacion "infinita" hasta saturacion (ramas → sub-ramas → otros enfoques hasta
  que se repitan) sobre comunicacion multi-agente y activadores.

Metodo: arbol de ramas en temporal, 4 olas / 13 busquedas paralelas, parando por SATURACION (ramas repiten).

Hallazgo: tras O18-O25 la teoria de coordinacion/consenso esta saturada. La unica veta nueva, convergente
desde 5 disciplinas independientes (taxonomia MAST/NeurIPS25, CSCW/common-ground, durable-execution,
OpenAI Agents-SDK, CRM/mission-command): el fallo #1 empirico (~79%) es la AMBIGÜEDAD DE ESPECIFICACION en
el handoff + el hueco de verificacion — no el consenso. Lo demas valido O18-O25, repitio, o es N/A/diferido
(firma JWT = N/A como Sybil; principal-agent/scheming = N/A mismo-usuario; OTel GenAI = aun experimental).

Alcance aplicado (O26):
- Codigo: `ms.handoff(para, goal, next_step, acceptance, done=, findings=, open_questions=, constraints=)` en
  `cerebro_multisesion.py` — empaqueta el contrato en `evidence`, fuerza `requires_ack=True`, RECHAZA con
  `ValueError` si falta goal/next_step/acceptance (structured-I/O enforced). TDD: `test_cerebro_comunicacion.py`
  6/6 (3 casos nuevos). Suite tareas 8/8 sin regresiones.
- Docs: O26 en `11`; contrato + closed-loop ack en `13`; primitiva en el contrato de handoff de `14`;
  checklist "Calidad de handoff" en `04`.
- Memoria: [[contrato-handoff-anti-ambiguedad]]. Temporal de investigacion eliminado al cerrar.

## 2026-06-16 — Migracion a ecosistema multi-agente

Autor runtime: Codex.

Motivo:
- El usuario pidio que el sistema dejara de ser un ecosistema de Claude y pasara a ser un ecosistema multi-agentico.
- Se requirio documentar todo con rigurosidad y evitar problemas con sesiones de Claude.

Alcance aplicado:
- Se creo fuente neutral multi-agente en `.cerebro`.
- Se conservaron `CLAUDE.md` y `AGENTS.md` como adaptadores de runtime.
- Se crearon adaptadores `AGENTS.md` minimos en proyectos que solo tenian `CLAUDE.md`.
- Se añadieron avisos breves en `CLAUDE.md` de proyectos para que Claude detecte convivencia con Codex.
- Se registro el trabajo en multisesion con tags `multiagente`, `migracion`, `seguridad`, `docs`.

Archivos creados:
- `~\.cerebro\00_INDICE.md`
- `~\.cerebro\01_ARQUITECTURA.md`
- `~\.cerebro\02_PROTOCOLO_OPERATIVO.md`
- `~\.cerebro\03_BITACORA_MULTIAGENTE.md`
- `~\.cerebro\04_CHEQUEOS_SEGURIDAD.md`
- `~\.cerebro\05_MIGRACION_PRIVADA_PENDIENTE.md`
- `~\.cerebro\06_CONTRATO_NUEVO_AGENTE.md`
- `~\.cerebro\07_REGLA_ACTUALIZACION_DOCUMENTAL.md`
- `~\.cerebro\08_REGISTRO_ESTADO_PRIVADO.md`
- `~\.cerebro\09_MAPA_GLOBAL_MEMORIA.md`
- `~\.cerebro\10_PRIORIDAD_SALUD_COMPUTADOR.md`
- `~\.cerebro\11_PROCESO_MEJORA_ECOSISTEMA.md`
- `~\.cerebro\12_HUB_PROCESOS.md`
- `~\.cerebro\ECOSISTEMA_MULTIAGENTE.md`
- `C:\tu-tienda\AGENTS.md`
- `~\tu-proyecto-aprendizaje\AGENTS.md`
- `~\tu-proyecto-agente\AGENTS.md`
- `~\tu-proyecto-automatizacion\AGENTS.md`
- `~\tu-proyecto-juegos\AGENTS.md`
- `~\tu-proyecto-web\AGENTS.md`

Archivos modificados:
- `~\CLAUDE.md`
- `~\AGENTS.md`
- `~\.cerebro\README.md`
- `~\.cerebro\SKILLS_CROSS_PROYECTO.md`
- `~\.cerebro\CONVIVENCIA_CLAUDE_CODEX.md`
- `C:\tu-tienda\CLAUDE.md`
- `~\tu-proyecto-aprendizaje\CLAUDE.md`
- `~\tu-proyecto-agente\CLAUDE.md`
- `~\tu-proyecto-automatizacion\CLAUDE.md`
- `~\tu-proyecto-juegos\CLAUDE.md`
- `~\tu-proyecto-web\CLAUDE.md`

Limites respetados:
- No se borraron archivos.
- No se movieron memorias privadas.
- No se editaron credenciales.
- No se limpiaron caches.
- No se lanzaron daemons ni acciones GUI.
- Las posibles migraciones de memoria privada/historiales/credenciales/caches quedaron diferidas y documentadas para una sesion dedicada de Claude si el usuario lo confirma.

## 2026-06-16 — Multisesion agentica

Autor runtime: Codex.

Motivo:
- El usuario pidio optimizar la multisesion para que se convierta en multisesion agentica y globalizar lo centralizado en Claude.

Cambios:
- `cerebro_multisesion.py` paso de "multisesion compartida entre sesiones Claude Code" a "multisesion agentica".
- Schema subio de 3 a 4.
- Sesiones, locks, eventos, decisiones, mensajes y conocimiento ahora registran `agent` y `runtime`.
- `estado()` puede filtrar por `project` y por `agent`.
- `leer_conocimiento()` puede filtrar por `agent`.
- El buzon puede recibir mensajes por agente (`agent:codex`, `agent:claude`).
- `C:\tu-tienda\scripts\multisesion.py` sigue siendo shim compatible, pero ya no impone identidad Claude.

Compatibilidad:
- Las llamadas antiguas `Multisesion("...", project="x")` siguen funcionando.
- Las sesiones viejas sin `agent` se migran suavemente con defaults durante purga/lectura.

## 2026-06-16 — Contrato para agentes futuros

Motivo:
- El usuario aclaro que el ecosistema debe ser versatil para todos los agentes futuros y facil de entender para trabajar con lo existente.

Cambios:
- Se creo `06_CONTRATO_NUEVO_AGENTE.md`.
- Se enlazo desde indice, fuente neutral, arquitectura y protocolo operativo.
- Se estandarizo el alta de agentes por `agent/runtime`, adaptador minimo, locks, mensajeria y checklist.

## 2026-06-16 — Regla de actualizacion documental continua

Motivo:
- El usuario pidio dejar una regla documentada de actualizacion constante de documentos necesarios para evitar confusion.

Cambios:
- Se creo `07_REGLA_ACTUALIZACION_DOCUMENTAL.md`.
- Se enlazo desde indice, fuente neutral y protocolo operativo.
- Se definio que todo cambio estructural debe actualizar la documentacion minima afectada antes de cerrar sesion.

## 2026-06-16 — Inventario de estado privado y globalizacion segura

Motivo:
- El usuario autorizo mover memorias privadas, historiales, credenciales y caches si era necesario para terminar el ecosistema.

Decision:
- No se movieron fisicamente porque `.claude`, `.codex` y `.remember` son rutas vivas de runtime y moverlas puede romper sesiones/autenticacion/plugins/historial.
- Se globalizo el acceso mediante documentacion neutral, sin copiar secretos ni logs completos.

Cambios:
- Se creo `08_REGISTRO_ESTADO_PRIVADO.md`.
- Se creo `09_MAPA_GLOBAL_MEMORIA.md`.
- Se actualizo `05_MIGRACION_PRIVADA_PENDIENTE.md` para reflejar que el movimiento esta permitido solo con necesidad concreta, backup y verificacion.

Seguridad:
- No se abrieron credenciales.
- No se movieron rutas privadas.
- No se borraron caches.
- No se copiaron historiales completos.

## 2026-06-16 — Incorporacion de memoria USB tu-proyecto-automatizacion

Motivo:
- El usuario indico que la memoria USB conectada contenia informacion necesaria.

Origen:
- USB `D:` etiqueta `DEISON`.
- Carpeta relevante: `D:\tu-proyecto-automatizacion`.

Acciones:
- Se inventario la USB sin modificarla.
- Se leyeron `CLAUDE.md`, `02_MEMORIA_COMPARTIDA.md`, `memoria\MEMORIA.md`, `memoria\_PENDIENTE_SYNC.md` y `PLAN.md`.
- Se detecto que `02_MEMORIA_COMPARTIDA.md`, `memoria\MEMORIA.md` y `CLAUDE.md` diferian de la copia local; `PLAN.md` coincidia.
- Se respaldo memoria local en `~\tu-proyecto-automatizacion\_sync_backups\usb_20260616_224912`.
- Se sincronizaron desde USB hacia local:
  - `02_MEMORIA_COMPARTIDA.md`
  - todo `memoria\*`
- No se sobrescribio `CLAUDE.md` local para no perder la adaptacion multi-agente.

Verificacion:
- Hash USB/local de `02_MEMORIA_COMPARTIDA.md` coincide.
- Hash USB/local de `memoria\MEMORIA.md` coincide.
- `_PENDIENTE_SYNC.md` en USB esta vacio.

Aprendizaje clave incorporado:
- Fase 1 pymiere ya funciona en vivo en PC del trabajo.
- JUDICIALES terminada y parqueada.
- INCAUTACION MADERA quedo para que el usuario la termine a mano.
- Nuevas reglas editoriales: b-roll ~3 planos por tramo de VO, bookend estatico con video operativo, cintillas durante toda la nota con Barrido, V5 manual, audio por clip a picos <= -6, crossfades segun ritmo de habla, verificar VO correcta antes de montar.

## 2026-06-16 — Regla salud del computador

Motivo:
- El usuario pidio una regla explicita: priorizar la salud del computador.

Cambios:
- Se creo `10_PRIORIDAD_SALUD_COMPUTADOR.md`.
- Se enlazo desde indice, fuente neutral, protocolo operativo y adaptadores raiz.
- Se establecio que estabilidad, temperatura, recursos, disco y continuidad del trabajo del usuario tienen prioridad sobre cualquier tarea.

## 2026-06-16 — Proceso de mejora del ecosistema

Motivo:
- El usuario pidio una forma de simplificar actualizacion documental y optimizar estructura para eficiencia de IAs y reduccion de tokens.

Cambios:
- Se creo `11_PROCESO_MEJORA_ECOSISTEMA.md`.
- Se definieron paquetes de contexto por situacion.
- Se establecieron optimizaciones activas O1-O8.
- Se enlazo el proceso desde indice, fuente neutral y protocolo operativo.
- Se definio que nuevas optimizaciones se agregan al mismo proceso cuando el usuario lo pida.

Actualizacion posterior:
- El usuario aclaro que "facilidad de actualizacion" se refiere a los documentos.
- Se ajusto `11_PROCESO_MEJORA_ECOSISTEMA.md`.
- Se agrego O9: un solo punto de edicion por tema.

## 2026-06-16 — Hub de procesos del ecosistema

Motivo:
- El usuario pidio ejecutar el proceso de mejora del ecosistema e integrar todos los procesos como este en el cerebro hub.

Cambios:
- Se creo `12_HUB_PROCESOS.md`.
- Se centralizaron los procesos activos en una tabla corta: disparador, documento dueño y salida esperada.
- Se agrego O10 al proceso de mejora del ecosistema.
- Se enlazo desde indice, fuente neutral y protocolo operativo.

Beneficio:
- Los agentes pueden elegir que documento abrir sin cargar toda la documentacion.
- Reduce duplicacion y gasto de tokens.

## 2026-06-16 — Memoria durable compartida (O11)

Autor runtime: Claude (claude-code).

Motivo:
- El usuario pidio optimizar el ecosistema por completo para que los agentes/sesiones se coordinen
  excelentemente y TODOS los recuerdos se compartan. Decision: compartir todo salvo secretos;
  dejar todo bien organizado para agentes presentes y futuros (fuente unica).

Cambios:
- Se creo el almacen durable neutral `.cerebro\memoria\` (un hecho por archivo, por area de proyecto)
  + indice `MEMORIA.md` reconstruible.
- Se creo el helper `cerebro_memoria.py` (solo stdlib, reusa el mutex de `cerebro_multisesion`):
  `recordar`/`leer`/`olvidar`/`buscar`/`indice`/`reindexar` + CLI. API igual para todos los agentes.
- Se migraron 101 hechos curados de Claude (`~/.claude/.../memory/*.md`) al almacen neutral,
  clasificados por area (tu-tienda 82, hub 10, tu-proyecto-agente 5, tu-proyecto-web/tu-proyecto-aprendizaje/tu-proyecto-automatizacion/
  tu-proyecto-juegos 1 c/u). 0 huerfanos. Escaneo de secretos: 0 sospechosos.
- `~/.claude/.../memory/MEMORY.md` se reemplazo por un STUB que redirige al indice neutral
  (backup `MEMORY.md.pre-neutral.bak`). NO se uso hardlink: es incompatible con la escritura atomica
  de `reindexar()` (os.replace crea inodo nuevo).
- Se actualizaron adaptadores (`CLAUDE.md`, `AGENTS.md`) y docs neutrales (`00`, `02`, `06`, `09`,
  `11` O11, `12`). Aviso dejado en buzon `agent:codex`.

Backup / rollback:
- `.cerebro\_backups\memoria_claude_20260616.zip` (102 entradas) + originales de `~/.claude` intactos
  (no se borran hasta que el usuario confirme el sistema nuevo en una sesion real).

Limites respetados:
- No se movieron credenciales/cachés; `.remember` sigue siendo diario privado de Claude.
- La memoria viajera de tu-proyecto-automatizacion (USB) se queda en el proyecto; en el neutral solo el
  hecho de alto nivel.
# 2026-06-16 — Investigacion de comunicacion en tiempo real
- Codex investiga patrones para que agentes se coordinen/comuniquen en vivo.
- Se crea `13_COMUNICACION_TIEMPO_REAL.md` como documento dueño de la propuesta.
- Se registra `O12` en el proceso de mejora: mensajes tipados, ack, eventos append-only y watcher local opcional antes de SSE/MCP.
- Se enlaza el proceso desde `00_INDICE.md` y `12_HUB_PROCESOS.md`.

# 2026-06-16 — MVP comunicacion viva implementado
- `cerebro_multisesion.py` sube a schema 5 con `mensaje_tipo`, filtros en `leer_buzon`, `ack`, `progreso` y `eventos.jsonl`.
- Se agrega `cerebro_watch.py` como watcher local opcional de solo lectura.
- Se agrega `cancelacion` como notificacion segura inspirada en MCP: solicita parar/liberar recursos, no ejecuta acciones por si sola.
- Se actualizan `13_COMUNICACION_TIEMPO_REAL.md`, `02_PROTOCOLO_OPERATIVO.md`, `06_CONTRATO_NUEVO_AGENTE.md`, `04_CHEQUEOS_SEGURIDAD.md` y `11_PROCESO_MEJORA_ECOSISTEMA.md`.
- No se inicia ningun servidor persistente; SSE/MCP queda fase 2 bajo confirmacion.

# 2026-06-17 — Investigacion co-programacion multi-agente
- Codex investiga como permitir que varios agentes escriban codigo juntos con mayor calidad.
- Se crea `14_COPROGRAMACION_MULTIAGENTE.md` como documento dueño.
- Se registra `O13` en el proceso de mejora: roles, ownership, handoffs, revision cruzada, QA-checker, pruebas e integracion por responsable unico.
- Se enlaza desde `00_INDICE.md`, `12_HUB_PROCESOS.md` y `04_CHEQUEOS_SEGURIDAD.md`.

# 2026-06-17 — Coordinacion Claude/Codex para tu-proyecto-agente
- Codex envia handoff tipado a `agent:claude` sobre la proxima mejora de infraestructura de tu-proyecto-agente.
- Se crea `15_COORDINACION_CLAUDE_PILOTO.md` con via local inmediata y hallazgos sobre Claude Code Channels/MCP/hooks/worktrees.
- Recomendacion: usar `.cerebro` ahora; Channels/MCP local solo como fase 2 bajo confirmacion.

# 2026-06-17 — Hechos activadores para Codex
- Se crea `16_HECHOS_ACTIVADORES_CODEX.md`.
- Objetivo: que Codex actue proactivamente dentro de una sesion abierta cuando detecte handoffs, reviews, blockers o avisos de trabajo conjunto.
- Limite: no despierta Codex desde cero, no arranca daemons y no autoriza acciones externas/GUI/GPU/destructivas sin confirmacion o lock.

# 2026-06-17 — Guard de colision por runtime (O15/O16)
- Autor runtime: Claude (Opus). Origen: ola T015 de tu-proyecto-agente (choque real en `config.py` con Codex/spacing).
- Hallazgo: el lock de `cerebro_coprog` solo protege a un agente cuyo PROCESO de sesion sigue vivo (workers Codex/Haiku/Sonnet). Claude-Code lo reclama en un `py -c` efimero que lo libera al retornar, antes de editar con Edit -> el lock no protege.
- `O15` (la regla): guard efectivo de Claude-Code = `board`-poll + Read fresco + concurrencia optimista de Edit ("modified since read"). Tabla "El lock por runtime" en `14_COPROGRAMACION_MULTIAGENTE.md`. Memoria `coprog-locks-efimeros-claude`.
- `O16` (la accion/token): Claude-Code OMITE la ceremonia `claim_all`/`release` (no-op que gasta turnos/tokens); la reserva para los workers. Solo `board` -> Read -> Edit.
- Docs tocados: `14_COPROGRAMACION_MULTIAGENTE.md` (dueño), `11_PROCESO_MEJORA_ECOSISTEMA.md` (O15+O16), `04_CHEQUEOS_SEGURIDAD.md` (linea de lock ahora runtime-aware).
- Memoria nueva `reference`: `entorno-bash-roto-usar-powershell` (el tool Bash tiene PATH roto en esta maquina; usar PowerShell/tools dedicados).

# 2026-06-18 — Adaptadores delgados contra context rot (O17, guiado por docs oficiales)
- Autor runtime: Claude (Opus). Origen: ronda "mejora ecosistema guiada por internet" + item aprobado por el usuario.
- Fundamento (Anthropic): CLAUDE.md inflado -> Claude IGNORA instrucciones reales; "context rot" baja el recall a mayor nº de tokens; el adaptador se carga en CADA sesion de CADA proyecto. Litmus por linea: "¿quitar esto causaria un error? Si no, cortalo." Lo a-veces-relevante/duplicado -> skills (on-demand) o doc dueño enlazado.
- Aplicado: `~\CLAUDE.md` -21,7% (14543->11394 chars). PRESERVADO intacto: 15 reglas universales, habitos de tokens, Paso 0, tabla de proyectos, guard `# TODO (tu)` de tu-proyecto-aprendizaje. COMPRIMIDO/movido a doc enlazado: explicacion del ecosistema, prosa de infraestructura, tabla de skills por proyecto (vive en `SKILLS_CROSS_PROYECTO.md`).
- Revertible: backup `~\CLAUDE.md.bak-20260617-235818` (tratar el adaptador como codigo).
- O17 en `11_PROCESO_MEJORA_ECOSISTEMA.md` con fuentes. Memoria `adaptadores-delgados-litmus`.
- Pendiente analogo (NO hecho, requiere su sesion): aplicar el mismo litmus a `AGENTS.md` (Codex).

# 2026-06-18 — Cache-safe prefix + helper-que-destila (O18/O19, guiado por docs oficiales)
- Autor runtime: Claude (Opus). Origen: ronda "mejora ecosistema con investigacion web exhaustiva".
- Investigacion (4 ejes: context engineering, agent skills, prompt caching, memoria multi-agente). Hallazgo: los habitos y O17 ya cubren context-rot/compaction/subagentes/MCP-deferred; quedaban DOS huecos accionables y respaldados por docs oficiales.
- `O18` — el prefijo siempre-cacheado (system + `CLAUDE.md`/`AGENTS.md` + tool-defs) debe ser byte-identico turno a turno (cache-write +25%, cache-read 10%, paga a ~3 lecturas/TTL 5min). Lo dinamico (fecha/hora/estado) va al TURNO DE USUARIO via hooks (diseño ya correcto: `UserPromptSubmit`/`SessionStart`), nunca al adaptador. Generaliza el habito #2 con su porque economico.
- `O19` — programmatic tool calling: preferir UNA llamada `py helper` que devuelva el resultado destilado sobre N tool-calls que vuelcan salida cruda. Codifica lo que ya hacen `cerebro_memoria.buscar`/`board`/`cerebro_hechos`. Extiende el habito #5.
- Docs tocados: `11_PROCESO_MEJORA_ECOSISTEMA.md` (O18+O19 con fuentes). Memoria nueva `cache-prefijo-estatico-y-helper-destila` enlazada a `tokens-sintesis-reduccion`.
- NO se toco ningun adaptador ni hook (ambas optimizaciones VALIDAN el diseño actual; son guards forward). Sin cambios de seguridad.

# 2026-06-18 — Fiabilidad de entrega: dead-letter + estados terminales + idempotencia (O20/O21/O22)
- Autor runtime: Claude (Opus). Origen: ronda "comunicacion multi-agente + activadores de sesiones, investigacion web profunda". Alcance elegido por el usuario: documentar guards + implementar codigo con tests (TDD).
- Investigacion (A2A v1.0/MCP/ACP bajo Linux Foundation AAIF; lifecycle de tareas A2A; colas at-least-once: idempotencia/visibility-timeout/DLQ; hooks Claude Code). Conclusion: la capa de comunicacion ya es A2A-shaped (mensajes tipados+locks+eventos.jsonl); faltaban piezas de FIABILIDAD DE ENTREGA, no un protocolo nuevo ni servidores.
- Verificado en codigo ANTES de afirmar gaps: `leer_buzon` YA filtra `expires_at` y `tomar` YA es atomico; los gaps reales eran perdida silenciosa de `requires_ack` vencidos, falta de estados terminales/visibility-timeout, y no-idempotencia de activadores.
- `O20` — `ms.dead_letter()` en `cerebro_multisesion.py` (read-only): rescata `requires_ack` vencidos-sin-ack. Test `test_cerebro_comunicacion.py` (3/3, TDD red->green).
- `O21` — `cerebro_tareas_modelo.py`: estados terminales `fallida`/`rechazada` (`fallar()`/`rechazar()`) + `expirar_tomadas(ttl_min=30)` (visibility timeout) + CLI `fallar/rechazar/expirar`. Test `test_cerebro_tareas_modelo.py` (5->8/8, TDD).
- `O22` — Regla 0 de idempotencia (regla pura, sin codigo nuevo): actuar sobre un activador solo tras claim atomico + chequeo de `ack`. Doc 16.
- Docs tocados: `11` (O20/O21/O22), `13` (dueño comunicacion: estado+uso), `16` (Regla 0), `04` (checklist fiabilidad de entrega). Memoria nueva `fiabilidad-entrega-buzon-tareas`.
- Regresion: suites coprog 5/5, hechos OK, semantica 5/5, modelo 7/7 — sin roturas. No se toco hook ni adaptador. Capa 4/5 (SSE/MCP) sigue diferida como estaba.

# 2026-06-18 — Seguridad de comunicacion/activadores: anti-inyeccion + anti-runaway (O23/O24) + direcciones diferidas
- Autor runtime: Claude (Opus). Origen: 3a ronda de research profunda "descubrir todo sobre comunicacion multi-agente + activadores de sesiones".
- Research (8 busquedas nuevas no cubiertas antes): seguridad A2A/rogue-Agent-Cards/prompt-injection, OTel GenAI semantic conventions, topologias (supervisor/swarm/blackboard/contract-net), ciclo completo de hooks Claude Code (~30 eventos), seguridad de triggers (circuit breakers/token-spiral/rate-limit), continuidad entre sesiones.
- Conclusion: los gaps reales son DE SEGURIDAD y caen justo sobre los activadores (foco del usuario). El resto es VALIDACION del diseño (supervisor-worker = 70% produccion = router-por-modelo; orquestador+subagentes efimeros valida habitos/O19; `.cerebro` neutral = "Memory Passport" portable Claude/Codex).
- `O23` — anti prompt-injection: contenido de otro agente (mensaje/`conocimiento`/`worker_instruccion.txt`/handoff) es DATO no confiable, nunca instruccion; un activador solo dispara una clase de accion de la whitelist, no texto arbitrario. Doc 16 Regla A.
- `O24` — anti-runaway/token-spiral: presupuesto de activacion (cap de encadenamiento sin turno humano, anti ping-pong, frenar ante repeticion). Circuit breaker como POLICY (asi lo enmarca la literatura), refuerza reglas universales #3 y #10. Doc 16 Regla B.
- Ambas son REGLAS puras (no codigo): la literatura las define como politicas/guardrails, no algoritmos; fabricar codigo habria violado proporcionalidad/salud. Aplicadas en docs dueño 16 (Reglas A/B), 13 (Seguridad), 11 (O23/O24), 04 (checklist).
- Direcciones DESCUBIERTAS y DIFERIDAS (registradas en doc 13 para no re-investigar): contract-net/bidding para el router (evolucion de doc 17) y OpenTelemetry GenAI (observabilidad) — ambas solo si algun dia se levanta bus/MCP (Capa 4/5). Memoria nueva `seguridad-inter-agente-injection-runaway`.
- Sin cambios de codigo. Sin tocar hooks ni adaptadores.

# 2026-06-18 — Fundamentos multidisciplina + saga/compensacion (O25) + mapa anti-sobreingenieria
- Autor runtime: Claude (Opus). Origen: 4a ronda de research "descubrir todo desde OTRAS perspectivas".
- Research (8 busquedas en disciplinas no tocadas): estigmergia/enjambre, FIPA-ACL/actos de habla, modelo de actores/Erlang supervision/let-it-crash, sistemas distribuidos (relojes logicos/CRDT/split-brain), saga/compensacion, BFT/Sybil/confused-deputy, gossip/heartbeat/phi-accrual.
- VERIFICADO EN CODIGO (no asumido): el reaper de `_purgar`/estado marca sesion muerta por latido (15min) Y por `pid_alive` del mismo host (lineas ~281-289), poda locks de no-vivas (290-292) y capa `eventos`/`conocimiento` (293-294); `_Mutex` reclama lock de PID muerto (195) y cede tras spin (203). => las lentes de estigmergia/actores/heartbeat resultaron VALIDACIONES ya implementadas (mejor que patrones de cluster: pid_alive local = verdad-terreno), NO gaps. Mi hipotesis de "conocimiento sin decaer" y "sesiones vivas fantasma" era FALSA.
- Unico gap real: `O25` saga/compensacion — una tarea delegada multi-paso con efectos debe definir su accion de COMPENSACION explicita y testeable (no rollback automatico); el integrador unico la ejecuta al `fallar()`. Regla pura. Doc 14 (olas) + 13 (lifecycle) + O25 + checklist 04.
- Mayor valor de la ronda: mapa de "mecanismos famosos deliberadamente NO adoptados" (relojes vectoriales, gossip/phi-accrual, BFT/quorum, FIPA completo, anti-Sybil pesado) con su PORQUE (single-host, usuario unico, pid_alive autoritativo) — para que ningun agente futuro los sobre-ingenierize. Mas "Fundamentos teoricos (por que esta construido asi)". Ambos en doc 13.
- Memoria nueva `fundamentos-coordinacion-y-no-sobreingenieria`. Sin codigo, sin tocar hooks/adaptadores.


# 2026-06-18 - Protocolo de comprobacion de calidad del ecosistema
- Autor runtime: Codex. Origen: usuario pide un protocolo para revisar cada proyecto y el ecosistema general buscando fallos y mejoras, dejando todo guardado en documento.
- Creado documento dueño 21_PROTOCOLO_COMPROBACION_CALIDAD.md: auditoria por fases para .cerebro, adaptadores, proyectos registrados, infra compartida, memoria, skills, seguridad, salud del PC y calidad especifica por proyecto.
- Enlazado desde 00_INDICE.md y 12_HUB_PROCESOS.md; agregado al checklist 04_CHEQUEOS_SEGURIDAD.md.
- Criterio: toda auditoria debe producir informe en .cerebro\auditorias\YYYY-MM-DD_calidad_ecosistema.md con evidencias, severidad, impacto, recomendacion y cierre verificable.
