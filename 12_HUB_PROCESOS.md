# Hub de Procesos del Ecosistema

Entrada unica para saber que proceso aplicar sin abrir toda la documentacion.

## Regla
Antes de abrir documentos largos, identifica el proceso aplicable aqui y abre solo el documento dueño.

## Procesos activos

| Proceso | Cuándo se usa | Documento dueño | Salida esperada |
|---|---|---|---|
| Entrada al ecosistema | Cualquier agente inicia trabajo en el cerebro | `00_INDICE.md` | Ruta minima de lectura. |
| Arquitectura/ownership | Hay duda sobre capas, rutas, owners o limites | `01_ARQUITECTURA.md` | Entender donde vive cada cosa. |
| Operacion multi-agente | Un agente va a trabajar, reclamar locks, registrar eventos o cerrar sesion | `02_PROTOCOLO_OPERATIVO.md` | Paso 0 y cierre correcto. |
| Bitacora estructural | Se hizo un cambio estructural | `03_BITACORA_MULTIAGENTE.md` | Registro humano auditable. |
| Chequeos de seguridad | Antes de declarar cambios estructurales como listos | `04_CHEQUEOS_SEGURIDAD.md` | Evidencia de verificacion. |
| Migracion privada | Hay que mover memoria privada, historial, credenciales o caches | `05_MIGRACION_PRIVADA_PENDIENTE.md` | Plan con backup, rollback y verificacion. |
| Nuevo agente | Se integra otro agente/runtime | `06_CONTRATO_NUEVO_AGENTE.md` | Alta con `agent/runtime` y adaptador. |
| Actualizacion documental | Cambia una regla, ruta, proceso o adaptador | `07_REGLA_ACTUALIZACION_DOCUMENTAL.md` | Documentacion minima actualizada. |
| Estado privado | Hay que ubicar memoria, historiales, credenciales o caches | `08_REGISTRO_ESTADO_PRIVADO.md` | Inventario sin exponer secretos. |
| Memoria global | Hay que saber donde vive una memoria o como globalizarla | `09_MAPA_GLOBAL_MEMORIA.md` | Fuente principal y forma segura de enlazar/resumir. |
| Salud del computador | Tarea pesada, persistente o riesgosa para recursos | `10_PRIORIDAD_SALUD_COMPUTADOR.md` | Decision segura sobre recursos. |
| Mejora del ecosistema | Usuario pide optimizar docs, eficiencia, tokens o agregar optimizacion | `11_PROCESO_MEJORA_ECOSISTEMA.md` | Nueva optimizacion integrada. |
| Skills generales / capacidades | Proyecto nuevo, area nueva, tipo de tarea nuevo, o investigar/instalar/crear skills | `SKILLS_CROSS_PROYECTO.md` | Skill invocada/cableada, hueco registrado o skill creada/verificada. |
| Memoria durable compartida | Guardar/buscar un hecho durable que sirva a varios agentes/sesiones | `cerebro_memoria.py` (+ `09_MAPA_GLOBAL_MEMORIA.md`, `11` O11) | Hecho indexado en `.cerebro\memoria\` sin huerfanos. |
| Comunicacion en tiempo real | Mejorar coordinacion viva entre agentes, handoffs, avisos, watchers o bus local | `13_COMUNICACION_TIEMPO_REAL.md` | Propuesta/MVP seguro para mensajeria viva. |
| Coordinacion Claude tu-proyecto-agente | Claude va a trabajar en infraestructura de tu-proyecto-agente y Codex debe coordinarse | `15_COORDINACION_CLAUDE_PILOTO.md` | Handoff, fuentes, y plan seguro de comunicacion. |
| Co-programacion multi-agente | Varios agentes van a escribir/revisar/integrar el mismo codigo o tarea de codigo | `14_COPROGRAMACION_MULTIAGENTE.md` | Ownership, roles, handoffs, revision y merge seguro. |
| Hechos activadores Codex | Codex debe actuar proactivamente al detectar handoff, review, blocker o aviso de Claude | `16_HECHOS_ACTIVADORES_CODEX.md` | Accion segura sin esperar nueva instruccion del usuario. |
| Recursos IA locales/batch | Tocar GPU, tu servidor LLM local, Qwen, daemons IA local, vLLM/Kaggle/Colab o acelerar colas offline | `18_RECURSOS_IA_LOCALES.md` | Decision segura: local, batch externo, benchmark o no tocar. |
| Recuperacion post-crash | Sesion larga/arriesgada, o al abrir tras un cierre sucio (crash/freeze/kill) | `19_RECUPERACION_POST_CRASH.md` (+ `cerebro_checkpoint.py`) | Checkpoint atomico frecuente + RECOVERY MODE sin perder contexto. |
| Comprobacion de calidad | Usuario pide revisar el ecosistema/proyectos, buscar fallos, riesgos o mejoras, o hacer auditoria integral | 21_PROTOCOLO_COMPROBACION_CALIDAD.md | Informe guardado con evidencias, severidad, recomendaciones y cierre verificable. |
| Hub de procesos | Hay demasiados procesos/documentos y se necesita elegir rapido | `12_HUB_PROCESOS.md` | Documento dueño correcto sin leer todo. |

## Proceso minimo para agentes
1. Leer adaptador runtime (`CLAUDE.md`, `AGENTS.md` u otro).
2. Leer `00_INDICE.md`.
3. Consultar este hub si no es obvio que proceso aplica.
4. Abrir solo el documento dueño.
5. Ejecutar y registrar.

## Como agregar un proceso nuevo
1. Crear documento dueño con nombre numerado si es proceso cross-agent.
2. Añadir una fila en `Procesos activos`.
3. Enlazarlo desde `00_INDICE.md`.
4. Registrar en `03_BITACORA_MULTIAGENTE.md`.
5. Si afecta cierre/verificacion, actualizar `04_CHEQUEOS_SEGURIDAD.md`.

## Optimizacion de tokens
- Este documento debe mantenerse corto.
- No pegar instrucciones completas de cada proceso aqui.
- Cada fila debe responder: "cuándo", "dónde" y "qué produce".
