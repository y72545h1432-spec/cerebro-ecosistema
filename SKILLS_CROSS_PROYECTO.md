# SKILLS CROSS-PROYECTO — mapa multi-agente detallado

> Conocimiento compartido entre agentes y sesiones de TODOS los proyectos. Resumen en los
> adaptadores `~\CLAUDE.md` y `~\AGENTS.md` §🧰.
> Generado 2026-06-15 por investigación con 4 subagentes. Formalizado 2026-06-16.
> Reconciliado para Claude/Codex el 2026-06-18 tras investigación de skills generales.
>
> Las skills se disparan por su `description` (matching semántico). Este doc deja por
> escrito **qué invocar y cuándo**, para que el acierto no dependa del azar.

---

## 0. Contrato de skills generales

Este archivo es la **fuente de verdad de criterios**, no una carpeta de implementación.

- Las skills se activan por intención/tarea, no por copiar mecánicamente nombres entre runtimes.
- Las skills aplicables se **revisan antes de implementar**; no se empieza a tocar código/procesos nuevos hasta haber decidido si hay skill, proceso o hueco.
- Cada runtime usa los nombres reales disponibles en su entorno: Claude, Codex, plugins o futuras capas.
- Los adaptadores (`CLAUDE.md`, `AGENTS.md` y los de proyecto) enlazan este mapa y solo añaden diferencias locales.
- Una skill externa no se instala por popularidad: primero se revisa, se compara con lo ya existente y se prueba en sandbox cuando aplique.
- Si una capacidad es recurrente, riesgosa o multi-paso, se convierte en skill/proceso; si es puntual, se registra como receta o backlog.

### Dónde viven

| Ubicación | Uso |
|---|---|
| `~\.claude\skills\` | Skills disponibles para Claude Code. |
| `~\.agents\skills\` | Skills locales generales para agentes/Codex cuando están expuestas. |
| `~\.codex\plugins\cache\` | Skills de plugins/sistema de Codex (`superpowers:*`, `openai-docs`, documentos, browser, etc.). |
| `~\.cerebro\` | Mapas, procesos y registros; no es el lugar principal de implementación de skills. |

### Proceso al investigar skills

1. **Revisar antes de implementar:** identificar intención, proyecto y tipo de tarea; abrir la skill/proceso aplicable antes de tocar código o ejecutar cambios.
2. **Descubrir:** inventario local + búsqueda externa si el usuario pidió investigación o la información puede cambiar.
3. **Clasificar:** universal, dominio cross-proyecto, específica de proyecto, receta o backlog.
4. **Comparar:** detectar duplicados y decidir cuál manda por runtime.
5. **Verificar:** leer `SKILL.md`, revisar riesgos, probar si ejecuta código o toca herramientas.
6. **Cablear:** actualizar este mapa, el hub de procesos y solo el adaptador mínimo necesario.
7. **Registrar:** bitácora + `ms.conocimiento(..., tags=["skills"])`.

---

## 1. Universales (sirven a TODO proyecto)

| Capacidad | Runtime/nombre real | Disparador |
|---|---|---|
| Descubrir/cablear skills | `arrancar-area`, `find-skills`, `superpowers:dispatching-parallel-agents` | Proyecto, área o tipo de tarea nuevo. |
| Crear/editar skills | `skill-creator`, `superpowers:writing-skills` | Hueco recurrente sin skill o skill existente insuficiente. |
| Investigación exhaustiva | `investigacion-infinita` (en Claude **y** Codex desde 2026-06-18; en Codex adaptado: subagentes nativos en vez de `general-purpose`) | “Investigación infinita”, “barre X de punta a punta”, mapa + backlog. |
| Planificación | `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans` | Diseño/feature/pipeline no trivial. |
| Implementación fiable | `superpowers:test-driven-development`, `superpowers:systematic-debugging` | Feature/bugfix o cualquier fallo inesperado. |
| Verificación | `superpowers:verification-before-completion`, `verify`, `run`, `.cerebro\cerebro_hechos.py` | Antes de declarar algo listo o afirmar un hecho de entorno. |
| Grafo de código (on-demand) | `.cerebro\cerebro_grafo.py` — `simbolo <X> <ruta>` (def/callers, Python `ast` nativo) · `arquitectura <ruta>` (mapa Graphify on-demand, 36 leng.) | Entrar a un repo grande desconocido (arquitectura) o ubicar dónde se define / quién llama a un símbolo sin barrer a grep. Sin daemon/install. Memoria [[reference-graphify-evaluado]]. |
| Revisión | `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `code-review`, `pr-review-toolkit` | Cierre de trabajo o integración. |
| Instrucciones de agentes | `claude-md-management:claude-md-improver` | Auditar/mejorar `CLAUDE.md`/`AGENTS.md`. |
| Preguntas OpenAI/Codex | `openai-docs` en Codex; `claude-api` como referencia legacy Claude/LLM | Modelos, precios, tool-use, MCP, API, agentes. No responder de memoria. |
| IA aplicada | `ia-aplicada` | Automatización, MCP, IA local, voice agents, asistentes, workflows. |
| GUI/computer-use | `gui-control-seguro` + `computer-use:computer-use` | Mirar pantalla, OCR, clicar, escribir o controlar apps. Protocolo primero, herramienta después. |
| Continuidad | `remember`, `session-report` | Cierre/continuación de sesión, handoff y memoria durable. |
| Artefactos editables | `documents`, `pdf`, `spreadsheets`, `presentations` | Crear/editar/verificar Word, PDF, Excel/CSV o PowerPoint. |

### Calidad web general

`web-quality-audit` es el paraguas. Usa subskills cuando el trabajo sea específico:
`accessibility`, `seo`, `performance`, `core-web-vitals`, `best-practices`, `frontend-design`.

### Regla de convivencia Claude/Codex

- Registro operativo: `~\.cerebro\CONVIVENCIA_CLAUDE_CODEX.md`.
- Indice neutral: `~\.cerebro\00_INDICE.md`.
- Fuente neutral: `~\.cerebro\ECOSISTEMA_MULTIAGENTE.md`.
- Regla: ambos usan Paso 0 multisesión y no copian nombres de skills mecánicamente; cada runtime debe usar las skills reales disponibles.

---

## 2. Dominios cross-proyecto

| Dominio | Skills principales | Cuándo |
|---|---|---|
| Diseño/UI | `diseno`, `frontend-design`, `accessibility` | UX, visual design, componentes, revisión estética o a11y. |
| Video/motion | `video-editing`, `produccion-audiovisual`, `hyperframes:*`, `claude-video-vision` | Editar, analizar o producir videos/shorts/motion graphics. |
| Marketing/ecommerce | `marketing-digital`, `ecommerce`, `agencia-ia`, `negocios`, `seo` | Ads, CRO, pricing, oferta, agencia, growth, tienda. |
| Tendencias recientes | `last30days` + búsqueda web | Qué dice internet ahora sobre un tema. |
| Investigación y búsqueda actual | `20_RED_ROLES_IA.md` (`buscador`: Gemini Deep Research, OpenAI Deep Research, Perplexity) + búsqueda web | Comparativas, benchmarks, fuentes primarias, decisiones que dependen de información cambiante. |
| Shopify/Liquid | `liquid-skills:*`, `shopify-plugin:*` si disponible | Temas, secciones, metafields, functions, accesibilidad e-commerce. |
| Recursos IA locales | `ia-aplicada` + `18_RECURSOS_IA_LOCALES.md` | GPU, tu servidor LLM local, Qwen, daemons, batch externo, benchmarks. |

Notas de solape:
- `video-editing` decide criterio/editorial; `video-marca` o `hyperframes:*` ejecutan pipeline/render.
- `diseno` aporta criterio; `frontend-design` aterriza UI en código.
- `gui-control-seguro` gobierna seguridad; `computer-use` o `gui_control\` son herramientas.
- En Codex, preferir la familia HyperFrames de plugin cacheado cuando esté expuesta; en Claude usar la skill local disponible.

---

## 3. Por proyecto (además de las universales)

### tu-tienda (`C:\tu-tienda\`)
- **Propias** (`.claude/skills/`): `tu-tienda-listar-producto`, `tu-tienda-curar-producto`, `tu-tienda-importar-resenas`, `video-marca`.
- **Dominio**: `ecommerce`, `marketing-digital`, `negocios`, `video-editing`, `produccion-audiovisual`, `youtube-growth`, `diseno`, `hyperframes:*`, `shopify-plugin:*`/`liquid-skills:*`, `claude-video-vision`.
- **Infra local**: Mano Derecha, tu servidor LLM local, Qwen, GPU o batch externo → `18_RECURSOS_IA_LOCALES.md` + `C:\tu-tienda\GUIAS\MANO_DERECHA_LOCAL.md`.
- Nota: `superpowers:systematic-debugging`/`TDD`/`verification` mapean a la regla tu-tienda “verificar en vivo con evidencia”.

### tu-proyecto-aprendizaje (`~\tu-proyecto-aprendizaje\`) ⚠️ MODO APRENDIZAJE
- `openai-docs`/`claude-api`, `ia-aplicada`, `tutor-modo-aprendizaje`, `claude-md-management`, `remember`.
- `superpowers:systematic-debugging`/`test-driven-development` **solo sobre código que el usuario YA escribió**.
- Excluir de ejercicios toda skill que rellene `# TODO (tú)` o resuelva el aprendizaje por el usuario.

### tu-proyecto-agente (`~\tu-proyecto-agente\`)
- `openai-docs`/`claude-api`, `ia-aplicada`, `superpowers:*`, `claude-md-management`, `remember`, `verify`/`run`, `claude-video-vision`.
- `investigacion-infinita` para barrer áreas de tu-proyecto-agente de punta a punta; motor histórico en `research/INVESTIGACION_INFINITA/`.

### tu-proyecto-web (`~\tu-proyecto-web\`)
- `frontend-design`, `diseno`, Figma MCP + `/figma-use`/`figma-generate-design`, `run`/`verify`, `superpowers:brainstorming`, `code-review`.
- Evitar over-trigger de `hyperframes:*` por “animaciones”: aquí son CSS + IntersectionObserver salvo petición explícita de video.

### tu-proyecto-automatizacion (`~\tu-proyecto-automatizacion\`)
- `video-editing`, `produccion-audiovisual`, `gui-control-seguro`, `computer-use`, `superpowers:systematic-debugging`, `verification-before-completion`.
- Hueco: skill dedicada para Premiere 2020 + `pymiere` + flujo de notas.

### tu-proyecto-juegos (`~\tu-proyecto-juegos\`)
- `gui-control-seguro`, `computer-use`, `claude-video-vision`, `superpowers:systematic-debugging`, `verification-before-completion`, `run`/`verify`.
- Investigación infinita: `~\tu-proyecto-juegos\INVESTIGACION_INFINITA.md` + `.cerebro\investigacion_recursos\II_JUGAR_ROBLOX\`.
- Hueco: skill dedicada `roblox-turn-loop` para juegos lentos/por turnos con input externo + vision, mapeo, verificacion y recovery.

---

## 4. Skills nuevas creadas

- **`investigacion-infinita`** (Claude: `~\.claude\skills\` · Codex: `~\.agents\skills\` desde 2026-06-18) — cross-proyecto, ahora en **ambos** runtimes. La copia Codex está adaptada (subagentes nativos en vez de `general-purpose`); su drift es intencional y está en `skills_drift_allow.txt`. Sync con `cerebro_skills_sync.py`, control con `cerebro_skills_diff.py`.
- **`arrancar-area`** (`~\.claude\skills\arrancar-area\` y `~\.agents\skills\arrancar-area\`) — operacionaliza la regla universal #6.
- **`tutor-modo-aprendizaje`** (Claude: **scoped a `tu-proyecto-aprendizaje\.claude\skills\`** desde 2026-06-18; Codex: `~\.agents\skills\`) — tu-proyecto-aprendizaje: tutor socrático, pistas escalonadas, nunca rellena `# TODO (tú)`. *(Movida del home global: solo carga dentro de tu-proyecto-aprendizaje — backlog II_SKILLS #24.)*
- **`gui-control-seguro`** (`.claude\skills\` y `.agents\skills\`) — protocolo seguro de control GUI.
- **`tu-tienda-margenes`** (`C:\tu-tienda\.claude\skills\`) — margen neto real antes de precio/ads.
- **`tu-tienda-i18n`** (`C:\tu-tienda\.claude\skills\`) — traducir 6 locales + custom-liquid hardcodeado + gotcha nbsp.

---

## 5. Backlog de huecos (candidatos a skill)

| Prioridad | Área | Hueco | Tipo sugerido |
|---|---|---|---|
| Alta | cross | Adaptar `investigacion-infinita` a `.agents\skills` para Codex. | skill |
| Alta | cross | Gobernanza de instalación de skills externas: revisar, comparar, probar, registrar. | proceso/skill |
| Alta | cross | Gate de seguridad para skills externas: revisar `SKILL.md` + código + permisos + contexto del repo antes de ejecutar. | skill/proceso |
| Media | cross | Escritura técnica/docs: guías, READMEs, changelogs, ADRs. | skill |
| Media | cross | CI/CD y GitHub Actions: diagnosis, pipelines, checks. | skill |
| Media | cross | Observabilidad/incidentes: logs, métricas, tracing, Sentry si el proyecto lo usa. | skill |
| Media | cross | Auditoría de arquitectura/repos: mapas, ownership, deuda, límites. | skill |
| Media | cross | Validación local de skills: formato, description específica, frontmatter, permisos, scripts, read-only externo. | herramienta/skill |
| Media | cross | `visual-skill-gui-local`: skills multimodales con capturas/figuras para apps GUI recurrentes. | skill |
| Media | cross | `skill-portability-cross-runtime`: adaptar skills entre Claude, Codex, `.agents` y plugins sin copiar nombres mecanicamente. | proceso/skill |
| Media | cross | Hechos verificables con `.cerebro\cerebro_hechos.py`. | skill operativa |
| Media | cross | Actualización documental mínima según `07_REGLA_ACTUALIZACION_DOCUMENTAL.md`. | skill/hook |
| Media | tu-proyecto-agente | Entrenamiento LoRA/QLoRA (Qwen2.5-3B, trl/torch, Kaggle, lock GPU global). | skill |
| Media | tu-proyecto-agente | Docs vivas 3-archivos (`DOCUMENTACION` + `CHANGELOG` + `COGNITIVE`). | skill/hook |
| Media | tu-tienda | `tu-tienda-ads-launch` con checklist + gate de autorización + pixel/cuenta/tarjeta IDs. | receta |
| Media | tu-tienda | `tu-tienda-multisesion / Paso-0` para locks, buzón y recursos globales. | skill/hook |
| Media | tu-proyecto-web | Regresión visual: dev server → shots 1440/390 → diff vs Figma → reporte. | skill |
| Media | tu-proyecto-automatizacion | Premiere 2020 + `pymiere` + flujo de notas. | skill |
| Media | tu-proyecto-juegos | `roblox-turn-loop`: juego lento/por turnos con vision + GUI segura + mapa + recovery. | skill |
| Baja | tu-tienda | catálogo-vetting/winners, CAPI server-side, Klaviyo flows. | recetas |

---

## 6. Registro de investigación externa

Conclusión de 2026-06-18: no instalar skills externas todavía. La literatura, repositorios GitHub y ecosistemas recientes apuntan a que las skills ayudan cuando son enfocadas y verificadas, pero la disponibilidad de una skill no garantiza mejora. Por eso el ecosistema mantiene el filtro: descubrir → comparar → verificar → unificar → cablear.

Registro detallado de repositorios externos: `~\.cerebro\REGISTRO_SKILLS_EXTERNAS.md`.

Repos GitHub revisados:
- `anthropics/skills`: referencia principal de formato, spec, template y patrones; no instalar en bloque.
- `vercel-labs/agent-skills`: candidatos selectivos para React/Next/Vercel, web design y escritura técnica.
- `ynulihao/AgentSkillOS`, `Huangdingcheng/SkillWiki` y `scienceaix/agentskills`: referencias de arquitectura/gobernanza/investigación, no skills operativas inmediatas.
- `skilltester-ai/skilltester` y `GeniusHTX/SWE-Skills-Bench`: referencias para evaluar utilidad/seguridad antes de adoptar skills externas.
- `wwh0411/MCP-Flow`: referencia para aprendizaje/evaluación de herramientas MCP a escala.
- `vercel-labs/agent-skills` candidatos concretos: `writing-guidelines`, `react-best-practices`, `vercel-optimize`.
- `anthropics/skills` candidato concreto: `webapp-testing`.
- `Skilldex`/`SkillMOO`/`SkillRevise`/`SkillX`: referencias para validar, podar y mejorar skills con evidencia.
- `VISUALSKILL`: referencia multimodal para computer-use; repo anunciado no disponible al revisar, por ahora no instalable.
- `SkCC`: referencia para compilacion/adaptacion segura cross-framework; relevante a convivencia Claude/Codex.

Riesgo dominante de la ola extendida: supply chain semántica. En skills externas, `SKILL.md` puede manipular descubrimiento/selección y los scripts pueden ejecutar acciones reales; revisar instrucciones, código, permisos y contexto del repositorio antes de cualquier implementación.

Saturacion por huecos: CI/CD, observabilidad, arquitectura y docs vivas no arrojaron una skill externa madura. Mantenerlos como skills nativas futuras, diseñadas desde evidencia local.
Saturacion por dominios sensibles: Shopify/ecommerce, marketing, browser automation y secrets/security no arrojaron mejores candidatos externos que las skills/procesos locales; no traer skills de marketplace para servicios con credenciales sin sandbox y revision manual.

---

## Skills nativas propias añadidas

- **`equipo-ingenieria`** (universal, todos los proyectos de código) — playbook de "equipo de ingenieros" que añade
  las 4 capas que superpowers/feature-dev/pr-review-toolkit NO tienen: **A** reto de scope/producto antes de codear
  (post-`writing-plans`), **B** gates verificables por fase + anti-racionalización, **C** review cross-model (handoff a
  Codex vía `.cerebro`), **D** retrospectiva de ingeniería desde git. Destilada de `garrytan/gstack`+`addyosmani/agent-skills`
  (verificados, NO instalados — ver `REGISTRO_SKILLS_EXTERNAS.md`). Dispara por description. **NOT FOR** review de código en sí
  (pr-review-toolkit), debugging (systematic-debugging), a11y/CWV/perf (accessibility/core-web-vitals/performance/web-quality-audit).
  Pendiente menor: añadir su línea al mapa de `~/.claude/CLAUDE.md` en un cierre de sesión (no editar a mitad — hábito #2).
