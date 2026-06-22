# REGISTRO de skills externas (para encontrarlas fácil en el futuro)

> Catálogo de sistemas/skills de terceros vistos en videos/web, con detalles y dónde
> conseguirlos. **No instalados** salvo que se diga. Antes de instalar cualquiera: es acción
> externa (ejecuta código de terceros) → requiere OK del usuario, y ojo con [[reference_plugins_trimmed]]
> (plugins podados a 19 por RAM). Conocimiento compartido entre proyectos.

---

## ✅ INSTALADAS (verificadas + cableadas)

- **`emil-design-eng`** (skill de Claude) — filosofía de diseño/animación de **Emil Kowalski** (taste, motion,
  easing, micro-interacciones, checklist de review). **Solo texto-guía** (sin bash/red/código → segura, cero RAM).
  679 líneas. **Origen:** repo oficial `github.com/emilkowalski/skills` (sin LICENSE en raíz; procedencia anotada).
  Instalada 2026-06-19 en `~\.claude\skills\emil-design-eng\` con OK del usuario (de los 24 reels).
  **Dispara por description** (UI polish/animación). Complementa `frontend-design` para tu-tienda/tu-proyecto-web.
- **`nothing-design`** (skill de Claude) — sistema de diseño inspirado en la estética Nothing (monocromo,
  tipografía suiza, negros OLED, dot-matrix; dark+light). `v3.0.0`, `allowed-tools: [Read,Write,Edit,Glob,Grep]`
  (sin Bash/red → seguro). **Origen:** repo `nothing-design-skill` que estaba suelto en el home; verificado e
  instalado 2026-06-19 en `~\.claude\skills\nothing-design\` (LICENSE conservada; repo-fuente
  movido a `scratch\skills-fuente\` como procedencia). **Dispara solo** con "Nothing style"/"/nothing-design"
  (no automático). Útil para: tu-proyecto-web, landings/PDP de tu-tienda con estética técnica, dashboards.

---

## GitHub — repositorios de Agent Skills revisados (2026-06-18)

Estado: **investigados, NO instalados**. Mantener como referencias/candidatos; cualquier instalación requiere OK del usuario y pasar por `SKILLS_CROSS_PROYECTO.md` (revisar skills antes de implementar).

| Repo | Qué aporta | Veredicto para el ecosistema |
|---|---|---|
| https://github.com/anthropics/skills | Repositorio público de Anthropic para Agent Skills: ejemplos, spec, template y skills como `claude-api`, `frontend-design`, `mcp-builder`, `webapp-testing`, `docx`, `pdf`, `pptx`, `xlsx`. | **Referencia principal de formato/patrones.** No instalar en bloque; ya tenemos varios equivalentes vía plugins Codex/document skills. Revisar skills concretas si hacen falta. |
| https://github.com/vercel-labs/agent-skills | Colección oficial de Vercel con `react-best-practices`, `web-design-guidelines`, `writing-guidelines`, `vercel-optimize`, `deploy-to-vercel`, `react-view-transitions`, etc. | **Candidatos selectivos.** Útil para React/Next/Vercel y escritura técnica. No instalar sin proyecto que lo necesite. |
| https://github.com/ynulihao/AgentSkillOS | Investigación/prototipo para selección y orquestación de grandes catálogos de skills; enfoque en retrieval, capability tree y DAGs. | **Referencia arquitectónica**, no skill práctica inmediata. Inspiración para gobernanza/selección si el catálogo crece. |
| https://github.com/Huangdingcheng/SkillWiki | Infraestructura/lifecycle para skills con procedencia, gobernanza y evolución. | **Referencia de gobernanza**, útil para el backlog de instalación externa y trazabilidad. |
| https://github.com/skilltester-ai/skilltester | Proyecto de evaluación de utilidad/seguridad de skills. | **Candidato de QA**, revisar si se decide crear proceso formal de pruebas de skills externas. |
| https://github.com/GeniusHTX/SWE-Skills-Bench | Benchmark de skills para software engineering con pruebas por aceptación. | **Referencia de evaluación**, refuerza no instalar skills genéricas sin medir beneficio real. |
| https://github.com/scienceaix/agentskills | Lista curada tipo “awesome” sobre Agent Skills, MCP, tool use, computer use, benchmarks, papers y frameworks. | **Indice de investigación**, útil para futuras olas; no es una skill. |
| https://github.com/wwh0411/MCP-Flow | Pipeline de investigación/training para dominar herramientas MCP reales a escala. | **Referencia MCP**, no skill instalable; útil si se diseña aprendizaje/evals de herramientas. |

Hallazgos:
- `anthropics/skills` y `vercel-labs/agent-skills` son las fuentes más útiles para cosechar patrones concretos.
- `webapp-testing` (Anthropic) puede complementar verificación Playwright si el flujo local queda corto.
- `writing-guidelines` (Vercel) cubre un hueco real ya marcado: escritura técnica/docs.
- `react-best-practices`/`web-design-guidelines` pueden servir para proyectos React/Next, pero se solapan con `frontend-design`, `accessibility`, `performance` y `web-quality-audit`.
- `AgentSkillOS`/`SkillWiki` no se instalan: sirven para diseñar cómo seleccionar, gobernar y evolucionar skills.
- La señal de benchmarks recientes es conservadora: las skills especializadas ayudan; las genéricas o desalineadas pueden no aportar o incluso estorbar.
- La ola extendida converge en 3 familias: **referencias oficiales**, **orquestación/evaluación** y **seguridad de supply chain**.
- Riesgo clave: `SKILL.md` no es solo documentación; también afecta descubrimiento, selección y confianza. Revisar instrucciones + código + permisos + contexto del repo.

### Fuentes de seguridad/evaluación que cambian el criterio
- `Malicious Agent Skills in the Wild` (2026): dataset de skills maliciosas en registries; ataques de robo de datos y secuestro del agente.
- `Under the Hood of SKILL.md` (2026): ataques semánticos contra descubrimiento/selección/gobernanza usando solo texto de `SKILL.md`.
- `SkillSieve` (2026): triage jerárquico para detectar skills maliciosas combinando metadatos, código e instrucciones.
- `MalSkillBench` (2026): benchmark runtime-verificado; muestra que hay que razonar conjuntamente sobre intención, código e instrucciones.
- `Malicious Or Not` (2026): usar contexto completo del repositorio reduce falsos positivos y detecta riesgos como repos abandonados/hijacking.

### Regla de adopción derivada
Para cualquier skill externa de GitHub/marketplace:
1. Revisar `SKILL.md` completo.
2. Revisar scripts, binarios, comandos de instalación, permisos, variables de entorno y dependencias.
3. Revisar señales del repo: dueño, commits recientes, issues, licencia, releases, forks sospechosos, historial de renombres.
4. Comparar contra skills existentes para evitar duplicado.
5. Probar en sandbox o entorno sin secretos si ejecuta código, red, shell, GUI, browser, email, cloud, wallet o filesystem.
6. Registrar veredicto antes de cablear o instalar.

### Ola 3 — skills concretas con señal práctica
| Skill/repo | Señal | Encaje |
|---|---|---|
| `vercel-labs/agent-skills/skills/writing-guidelines` | Skill mínima que delega en una fuente viva de reglas de escritura. | Candidato fuerte para el hueco cross-proyecto “escritura técnica/docs”. Mejor recrear/adaptar nativo que instalar sin revisión. |
| `vercel-labs/agent-skills/skills/react-best-practices` | 70 reglas React/Next con categorías por impacto y estructura de reglas compilables. | Candidato selectivo para proyectos React/Next; se solapa con `frontend-design`, `performance`, `core-web-vitals`, `best-practices`. |
| `vercel-labs/agent-skills/skills/vercel-optimize` | Skill madura orientada a métricas: primero señales de producción, luego investigación acotada. | Referencia fuerte para diseño de skills complejas: métricas primero, gates deterministas, briefs acotados, verificación antes del reporte. |
| `anthropics/skills/skills/webapp-testing` | Playwright local con patrón “reconocimiento → acción” y helper de servidor tratado como caja negra. | Candidato para reforzar verificación frontend y `tu-proyecto-web`; parcialmente cubierto por browser/Playwright local. |

### Ola 3 — infraestructura/estándar
- `agentskills.io` / `anthropics/skills/spec`: mantener como referencia de compatibilidad, no como runtime.
- `Skilldex` (`skillpm`/`spm`): package manager/registry con scoring de conformidad y “skillsets”; referencia para un futuro validador local si el catálogo crece.
- `SkillMOO`, `SkillRevise`, `SkillX`: refuerzan una idea repetida: mejorar/prunar skills con evidencia de ejecución, no acumular instrucciones.
- `Dynamic Malicious Skills` (2026): defensa sugerida por la literatura: montar skills externas como read-only cuando sea posible; no permitir que una skill se modifique dinámicamente durante ejecución.

### Ola 4 — huecos del ecosistema y multimodal GUI
Busqueda dirigida: CI/CD, observabilidad/incidentes, arquitectura/repo audit, docs vivas, GUI/computer-use.

Resultado:
- Para **CI/CD/GitHub Actions** aparecio mas literatura/evidencia que skills listas. Señal: LLMs fallan en YAML CI con errores estructurales; si se crea skill local debe ser verificacion-first: lint/schema, accion exacta, permisos minimos, matrix/cache, rerun de workflow.
- Para **observabilidad/incidentes** no aparecio una skill GitHub madura y especifica comparable a `vercel-optimize`; mantener hueco propio. Patron a copiar: metricas primero, evidencia antes de grep, recomendaciones trazables.
- Para **arquitectura/repo audit** no aparecio una skill externa clara; crear nativa si se vuelve recurrente: inventario de modulos, ownership, limites, deuda y pruebas.
- Para **docs vivas** `writing-guidelines` cubre estilo, pero no cubre la rutina estructural local (DOCUMENTACION/CHANGELOG/COGNITIVE o bitacora/procesos). Mantener hueco local.
- Para **GUI/computer-use** aparecio `VISUALSKILL` como referencia: skills multimodales con texto + figuras/capturas por topico, cargadas bajo demanda. Relevante para `gui-control-seguro`, `tu-proyecto-juegos`, `tu-proyecto-automatizacion` y apps Windows.

Referencia nueva:
- `VISUALSKILL: Multimodal Skills for Computer-Use Agents` (2026). Repo anunciado: `https://github.com/XMHZZ2018/VisualSkills`, pero al revisar estaba como repo 404/no disponible. Mantener como referencia de paper, no como repo instalable.

Decision:
- Los huecos CI/CD, observabilidad, arquitectura y docs vivas se quedan como **skills nativas a crear cuando se usen**, no como instalaciones externas.
- Agregar posible skill futura: **visual-skill-gui-local**: capturas anotadas + pasos + estados esperados para apps usadas por el ecosistema.

### Ola 5 — dominios tu-tienda/ecosistema y portabilidad cross-runtime
Busqueda dirigida: Shopify/ecommerce, marketing, browser automation, secrets/security, estandar/compilacion.

Resultado:
- No aparecieron repos GitHub de skills externas para Shopify/marketing/secrets con confianza superior a las skills locales ya instaladas (`ecommerce`, `marketing-digital`, `liquid-skills:*`, `best-practices`, hooks de secretos). Mantener dominio tu-tienda con conocimiento propio.
- Las busquedas por browser automation vuelven a `webapp-testing`, Playwright y computer-use; no hay candidato nuevo mejor que lo ya registrado.
- La rama de seguridad vuelve a repetir marketplace/OpenClaw/ClawHub: no instalar skills de marketplace para servicios sensibles (ads, email, wallets, cloud, Shopify) sin sandbox y revision manual.
- Novedad util: **SkCC** (`SkCC: Portable and Secure Skill Compilation for Cross-Framework LLM Agents`). Propone IR tipado + compilacion por framework + analisis de seguridad antes de desplegar. No se adopta como herramienta, pero encaja con nuestro problema real: Claude/Codex tienen nombres, plugins y formatos distintos.

Decision:
- Para tu-tienda, priorizar skills locales y memoria propia antes que skills externas de ecommerce/marketing.
- Agregar hueco futuro: **skill-portability-cross-runtime** para adaptar/revisar una skill entre Claude, Codex, `.agents` y plugins sin copiar nombres mecanicamente.
- La busqueda por dominios sensibles queda saturada: mas riesgo que beneficio externo.

---

## ECC — "Everything Claude Code" (Affaan Mustafa)
- **Fuente:** video YouTube `BR6HknO4DAs` (canal *revolutia*, 2026-06-12) → repo real.
- **Repo:** https://github.com/affaan-m/ecc · autor https://github.com/affaan-m
- **Qué es:** "agent harness performance optimization system". ~119-270+ skills, ~28-67 subagentes,
  ~60-92 slash commands. MIT. Multiplataforma: Claude Code, Cursor, Codex, OpenCode, Gemini.
  Nació de ganar un hackathon de Anthropic (sep-2025). >100K stars.
- **Instalación (NO ejecutada):** `/plugin install ecc@ecc` (marketplace) · o manual
  `./install.sh --profile full`. Web/selector de perfiles: "ECC Tools" (`ecc-install --profile core`,
  perfil core = 8 items). ⚠️ Instala **hooks que interceptan tool-calls** (bloquea `git --no-verify`,
  detecta secretos en prompts, protege `.eslintrc`/`biome.json`/`.ruff.toml`, AgentShield "1282 tests, 102 rules").
- **Veredicto:** **NO instalar el set completo** (choca con plugins podados/RAM + ejecuta código
  de terceros). Sí cosechar **ideas** y, si alguna sirve, recrearla nativa. Decisión de instalar = del usuario.

### Skills vistas en pantalla (frame 0:16 del video) y mapeo a lo que YA tenemos
| Skill ECC | Qué hace | ¿Ya cubierto aquí? |
|---|---|---|
| Security Review / Security Scan | OWASP top-10, secrets, inyección, checklist | ✅ `security-review` + `pr-review-toolkit:silent-failure-hunter` |
| Claude API | Patrones Messages API, streaming, tool-use, Agent SDK | ✅ `claude-api` |
| Prompt Optimizer | Mejor calidad / menor coste / más rápido | ✅ parcial: `skill-creator` (optimización de description) |
| Continuous Agent Loop / Autonomous Loops | Quality gates, evals, DAGs autónomos | ✅ parcial: `loop`, `schedule`, `superpowers:executing-plans` |
| Agent Harness Construction / Agentic Engineering / AI-First Engineering | Diseñar action spaces, decomposición, model routing | ⚠️ conceptual; relevante a **tu-proyecto-agente** (maestro→estudiante) — recrear si hace falta |
| Cost-Aware LLM Pipeline | Routing por complejidad, budget, prompt caching | ⚠️ parcial `ia-aplicada` (ahorro tokens); útil para tu-tienda daemon + tu-proyecto-agente |
| Foundation Models On-Device | Correr modelos en local | ⚠️ relevante a **tu-proyecto-agente** (Qwen local) + tu servidor LLM local; recrear si hace falta |
| Blueprint | Convertir ideas en mapas de construcción multi-sesión | ✅ parecido: `superpowers:writing-plans` + Plan agent |
| Content Hash Cache | Cache por hash SHA-256 para procesado caro | ❌ no cubierto (nicho; candidato futuro si hay pipeline pesado) |
| Django Security / Spring Boot Security | Seguridad por framework | ❌ no aplica (sin proyectos Django/Spring) |

### Subagentes / commands ECC (del README) y mapeo
- `planner` / `/plan` → ✅ Plan agent + `feature-dev:code-architect`
- `code-reviewer` + reviewers por lenguaje (`typescript/python/go/java-reviewer`) → ✅ `code-review`, `pr-review-toolkit`
- `security-reviewer` / `/security-scan` (AgentShield) → ✅ `security-review` (su AgentShield es su tool propia)
- `architect` → ✅ `feature-dev:code-architect`
- `build-error-resolver` / `/build-fix` → ✅ `superpowers:systematic-debugging`
- `tdd-workflow` → ✅ `superpowers:test-driven-development`
- `e2e-testing` (Playwright) / `verification-loop` → ✅ `verify` + `superpowers:verification-before-completion` (Playwright ya lo usa tu-proyecto-web)
- `frontend-patterns` → ✅ `frontend-design`; `backend-patterns` → parcial `code-architect`
- **memoria entre sesiones / "instincts" (aprende de errores pasados)** → ✅ ya tenemos `remember` + sistema de memoria + `.cerebro/conocimiento()` + `hookify` (capturar errores como reglas)

### Hooks de seguridad estilo ECC — ✅ IMPLEMENTADOS (2026-06-15) vía `hookify`, sin instalar ECC
Cosechado de ECC y recreado nativo (regla #7: verificar → unificar). Archivos en
`~\.claude\` **y** `C:\tu-tienda\.claude\` (cubren hub y tu-tienda, que se lanzan por separado):
- **`hookify.block-git-no-verify.local.md`** (bash, **block**): bloquea `--no-verify` (no saltarse git hooks). *Verificado en vivo: bloqueó un comando de prueba que contenía la cadena.*
- **`hookify.warn-secrets-in-files.local.md`** (file, warn): detecta claves privadas / AWS / `sk-ant-` / `ghp_` / Slack / `api_key=...` antes de escribirlos. *Verificado: 6/6 positivos, 0 falsos positivos. Gotcha corregido: `(?i)` debe ir al INICIO del patrón (Python 3.12 lo exige).*
- **`hookify.protect-linter-config.local.md`** (file, warn): avisa al editar configs de linter/formato (no "callar" errores en vez de arreglarlos).
- **`hookify.block-git-no-gpg-sign.local.md`** (bash, **block**): bloquea `--no-gpg-sign` / `commit.gpgsign=false` (no saltarse la firma). *Verificado: 3/3 positivos, 0 falsos positivos.*
→ Gestionar con `/hookify:list` · `/hookify:configure`. NO se instaló el set ECC completo.

> Si en el futuro se decide instalar ECC o cosechar una skill concreta, esta tabla dice qué
> aporta de nuevo vs. lo que ya hay. Relacionado: [[reference_plugins_trimmed]],
> [[reference_skills_cross_proyecto]], [[feedback_actualizar_skills]].

---

## OpenCode (SST) — agente de coding en terminal · YA INSTALADO (v1.17.7, npm)
- **Fuente:** opencode.ai/docs · repo `github.com/anomalyco/opencode` (antes `sst/opencode`). Investigación exhaustiva 2026-06-17 (4 subagentes, ver `ms.conocimiento` tag `opencode`).
- **Estado local:** instalado vía npm (`~/AppData/Roaming/npm/opencode`), config `~/.config/opencode/` **virgen** (solo `$schema`); SDK de plugins `@opencode-ai/plugin@1.17.7` + `@opencode-ai/sdk` ya en `node_modules`. Sin providers/auth/agentes/commands aún.
- **Qué es:** agente de coding agéntico, cliente-servidor, **agnóstico de modelo** (75+ providers vía Models.dev, incl. local Ollama/tu servidor LLM local). Lee `CLAUDE.md`/`AGENTS.md` nativo. TUI/CLI/web/SDK. Modos Plan/Build, subagentes (General/Explore/Scout + custom en `.opencode/agent/*.md`), permisos finos (allow/ask/deny + `doom_loop`), MCP (stdio+remoto), plugins.
- **Automatización (clave):** (1) `opencode run "..." --format json --dangerously-skip-permissions` headless, lee stdin, NDJSON, exit 0/1 — ⚠️ bug flush `step_finish` (#26855), leer hasta EOF + watchdog; (2) `opencode serve` (HTTP :4096, OpenAPI + SSE; `session.idle`=terminó) → **la vía más robusta**; (3) SDK `@opencode-ai/sdk` + plugins (`tool.execute.before/after`, `permission.ask`, `session.idle`, `shell.env` con `$` de Bun, tools custom).
- **Encaje ecosistema:** candidato a **3er runtime de `.cerebro`** (`agent="opencode"`, contrato `06_CONTRATO_NUEVO_AGENTE.md`). Vía: plugin-puente fino que vía `$`(Bun)→CLIs Python hace Paso 0 (`Multisesion`+`reclamar`), enforca `cerebro_coprog.claim_all` antes de tocar `.py` (deniega por `permission.ask`), y expone `tareas.py`/buzón como tools. Python = fuente de verdad.
- **LÍMITE HONESTO (<VRAM> VRAM):** en OpenCode cada acción es tool-call → cuello de botella = disciplina de tool-calling del modelo, no su IQ. A <VRAM> realista solo `Qwen2.5-Coder-7B Q4 @~16K ctx` y **solo con GPU libre** (lock global `gpu`/`tu servidor LLM local`); el bueno para OpenCode (Qwen3-Coder-30B) pide ~18GB, NO cabe. API tokens=$0 con local, pero GPU/luz/tiempo no. → **obrero de tareas mecánicas verificables, no investigador/arquitecto**.
- **Verificar antes de cablear (regla #7):** ¿plugins corren bajo Bun o Node en este Windows? · dirs `agent/`/`command/` ¿singular o plural? · ¿soporta archivo de instrucciones distinto a `AGENTS.md` (que hoy es de Codex)? Type defs en `node_modules/@opencode-ai/plugin/dist/*.d.ts` son la verdad para 1.17.7.
- **Decisión pendiente del usuario:** integrarlo como runtime (construir plugin-puente + AGENTS.md propio + alta en `00_INDICE.md`/`ECOSISTEMA_MULTIAGENTE.md`) vs. usarlo solo manual/ad-hoc. NO cablear sin OK.

---

## Tres repos "tendencia Claude Code" (reel FB) — investigados 2026-06-18
> Origen: reel de Facebook (creador "Jose", `<email>`) que recomienda 3 repos para Claude Code. Investigados a fondo con 3 subagentes. Memoria: [[reference-codegraph-evaluado]]. ⚠️ Cualquier instalación choca con [[reference_plugins_trimmed]] (RAM: solo 19 plugins activos por agotamiento).

### A. CodeGraph (`github.com/colbymchenry/codegraph`) — **PROBADO en vivo, NO cableado**
- **Qué es:** MCP local — grafo de código (tree-sitter → SQLite/FTS5) para que el agente consulte en vez de barrer con grep/Read. MIT, ~51k stars, autor Colby McHenry. Expone `query`/`explore`/`node`/`callers`/`impact` como **comandos CLI** (usable SIN el MCP).
- **Claim reel "−94% tokens" = HYPE.** README real (mediana, 7 repos): **~47% menos tokens · ~58% menos tool-calls · ~16% más barato**; en repos chicos da break-even.
- **Prueba local 2026-06-18** (10 módulos `cerebro_*.py` en sandbox temp): indexó 298 nodos/641 aristas en 827 ms; `explore` devuelve símbolos + fuente con nº de línea + blast radius + aviso de tests faltantes en 1 llamada. **Funciona en Windows + Node v24** (backend `node:sqlite` nativo).
- **RIESGOS confirmados en vivo:** (1) 🔴 **daemon fantasma en Windows** (#692/#723) — quedó bloqueando el `.db`, `uninit` se colgó, hubo que matar procesos node a mano + `rmdir`. (2) 🟡 **telemetría ON por defecto** → apagar con `DO_NOT_TRACK=1` / `CODEGRAPH_TELEMETRY=0` / `codegraph telemetry off`. (3) ⚠️ **Node ≤ 24** (v25 lo rompe).
- **Cómo usarlo si se decide (sin instalar global):** `npx --yes @colbymchenry/codegraph@latest <init|query|explore> ...` con telemetría off. **NO `codegraph install`** (cablea MCP + daemon inestable + invalida caché de prefijo, hábito #2). Matar daemon al terminar: `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | ? CommandLine -match codegraph | % { Stop-Process -Id $_.ProcessId -Force }`.
- **Alternativa nativa (parqueada):** núcleo simple (AST Python → SQLite FTS5 + 3 queries) replicable en `.cerebro` sin terceros/telemetría/daemon. MVP ~½ jornada. Solo si el indexado se vuelve permanente y el daemon molesta.

### B. Multica / `multica-ai/andrej-karpathy-skills` — **principios ADOPTADOS en CLAUDE.md**
- **El repo de skills** es un único `CLAUDE.md` (sin código), inspirado (no oficial) en un post de Andrej Karpathy. Autor: Jiayuan "JY" Zhang (`forrestchang`, @jiayuan_jy). ⚠️ 178k stars en un archivo único = **inflados** (la plataforma real tiene 37k); sin archivo LICENSE pese a decir "MIT".
- **4 principios → ya cableados** en `CLAUDE.md` raíz, sección "✂️ CALIDAD DE SALIDA": Pensar antes de codear · Simplicidad primero · Cambios quirúrgicos · Ejecución por metas verificables. (Mayor ROI: Cambios quirúrgicos + Simplicidad.)
- **La plataforma Multica** (`multica-ai/multica`): orquesta agentes como compañeros (asignas issue → agente programa → reporta bloqueos → actualiza PR). Go+Next.js+**Postgres17/pgvector**, self-host Docker. Licencia **Apache modificada (source-available, NO OSI**, cláusula anti-SaaS). **Veredicto: OVERKILL** para single-dev Windows (fricción Postgres+Docker+daemon). NO adoptar; el valor estaba en el CLAUDE.md.

### C. Claude Code Plugins Directory (`anthropics/claude-plugins-official`) — **CATÁLOGO para el futuro**
- Marketplace **oficial de Anthropic** (Apache-2.0, riesgo bajo). **Ya viene precargado** en Claude Code (`/plugin` → Discover). Si falta: `/plugin marketplace add anthropics/claude-plugins-official`. Instalar: `/plugin install <nombre>@claude-plugins-official` + `/reload-plugins`.
- ⚠️ **NO instalar en bloque** — chocan con [[reference_plugins_trimmed]] (RAM). Antes de cada uno, mirar **Context cost** en `/plugin`. **Los `*-lsp` se podaron a propósito por RAM → backlog, no instalar salvo necesidad puntual por proyecto.**

**Catálogo interno (`/plugins`, 36 — mantenidos por Anthropic). Marcado: ✅=ya tengo · 🆕=candidato futuro · 🐏=RAM (LSP, evitar):**

| Plugin | Qué hace | Estado |
|---|---|---|
| code-review, code-simplifier, commit-commands, feature-dev, frontend-design, hookify, pr-review-toolkit, claude-md-management, skill-creator, remember, session-report, learning-output-style, explanatory-output-style | (varios) | ✅ ya en mis 19 |
| **security-guidance** | Audita cada edit de Claude buscando vulnerabilidades y lo obliga a corregir en la misma sesión | 🆕 **top candidato** (skills, RAM baja; refuerza regla #7) |
| **plugin-dev** | Toolkit (7 skills) para crear plugins de Claude Code propios | 🆕 empaquetar skills cross-proyecto (regla #6/#7) |
| **agent-sdk-dev** | Kit del Claude Agent SDK | 🆕 útil para tu-proyecto-agente |
| **mcp-server-dev** | Construir servidores MCP | 🆕 exponer `.cerebro` como MCP |
| **claude-code-setup** | Analiza un codebase y sugiere hooks/skills/MCP/subagentes | 🆕 al abrir proyecto nuevo (regla #6) |
| **code-modernization** | Workflow para legacy (COBOL/Java viejo/monolitos) | 🆕 nicho (refactors grandes) |
| **ralph-loop** | Bucles iterativos auto-referenciales ("Ralph Wiggum") | 🆕 con cuidado (regla #3 loops) |
| **mcp-tunnels** | Conectar a MCP privado por túnel de Anthropic | 🆕 nicho |
| **math-olympiad** | Mates de competición con verificación adversarial | 🆕 nicho |
| **playground** | Playgrounds HTML interactivos con preview en vivo | 🆕 nicho |
| **cwc-makers**, **example-plugin** | Onboarding Cardputer / plantilla de referencia | nicho/ejemplo |
| **pyright-lsp** (Python) | Diagnósticos de tipos en vivo. Requiere `npm i -g pyright` | 🐏 backlog (RAM; activar por proyecto si hace falta: tu-proyecto-aprendizaje/tu-proyecto-agente/.cerebro) |
| **typescript-lsp** (TS/JS) | LSP TypeScript. Requiere `typescript-language-server` | 🐏 backlog (tu-tienda/tu-proyecto-web) |
| **clangd-lsp**, **csharp-lsp**, **gopls-lsp**, **jdtls-lsp**, **kotlin-lsp**, **lua-lsp**, **php-lsp**, **rust-analyzer-lsp**, **swift-lsp** | LSP por lenguaje (binario propio en PATH) | 🐏 backlog — lenguajes que NO uso, no instalar |

> Si en el futuro hace falta uno: `/plugin install <nombre>@claude-plugins-official` + `/reload-plugins`, mirando Context cost. Para los 🐏 LSP, instalar primero el language-server en PATH y activarlos **por proyecto** (regla #10 RAM).

---

## Graphify (otro grafo de código) — **PROBADO en vivo 2026-06-19, NO cableado** 🆕 nicho
> Pedido por el usuario ("¿te serviría? quiero integrarla, si hay algo mejor dime"). Comparado de frente con CodeGraph (sección A arriba). Memoria: [[reference-graphify-evaluado]].
- **Qué es:** grafo de código para asistentes IA. `github.com/safishamsi/graphify` (MIT, **YC S26**, creado abr-2026 → muy joven, 365 issues abiertos). **Python puro** (PyPI `graphifyy` doble-y, CLI `graphify`): tree-sitter + NetworkX/Leiden. Corre efímero con `uvx --from graphifyy graphify ...` (sin instalar global). Consultable: `query`/`affected`/`explain`/`path`; build `update <path>` (solo-código, sin LLM).
- **Claims "49x/71.5x/500x menos tokens" = HYPE** (blogs SEO, no benchmarks). Medido aquí: net-negativo en repos chicos.
- **Prueba local 2026-06-19** (13 módulos `cerebro_*.py`, sandbox, `DO_NOT_TRACK=1`): 263 nodos/501 aristas/13 comunidades en **~24.103 ms** (vs CodeGraph 298/641 en 827 ms → **~29× más lento**; el coste es clustering Leiden + `graph.html` 227 KB inútil para agente). **`GRAPH_REPORT.md` (5.9 KB)** = su valor real: god nodes, comunidades, ciclos de import, puentes (mapa de arquitectura que CodeGraph no da). **Query puntual FALLÓ**: `affected "reclamar"` = "no unique match", `query` matcheó nodo equivocado → para navegación de símbolos grep/CodeGraph ganan.
- **Ventaja confirmada sobre CodeGraph:** 🟢 sin daemon, **0 procesos colgados** (no reproduce el `.db` lock #692/#723); 🟢 telemetría off respetada (reporte "0 tokens" = puro código); 🟢 Python (sin atadura Node ≤24).
- **Decisión:** **NO daily driver, NO `install`** (cablea hook PreToolUse + edita CLAUDE.md = viola hábito #2). Guardar **on-demand para UN nicho**: mapa de arquitectura al entrar a un repo grande desconocido → `uvx --from graphifyy graphify update .` (DO_NOT_TRACK=1) + leer `graphify-out/GRAPH_REPORT.md` + borrar `graphify-out/` al terminar.

---

## Lote de 24 reels "Claude Videos" (revisado 2026-06-19) — growth-marketing, casi todo ya cubierto
> Carpeta `Desktop\Claude Videos\` (transcrito con Whisper local). Análisis completo: `Desktop\Claude Videos\_ANALISIS_VIDEOS.md`. Todos del molde "comenta X y te lo paso por DM". **Ninguno instalado.**

**Ya cubierto / ya evaluado (no hacer nada):** Graphify, CodeGraph, Multica/Karpathy, claude-plugins-official, Superpowers, Frontend Design, Code Review, Security Review, Context7, Code Simplifier, Anthropic Official skills (PDF/Excel/Word), "archivo anti-tokens" (= Calidad de Salida), Context Engineering, Live Artifacts.

**Candidatos NUEVOS (requieren OK del usuario):**
| Item | Qué es | Veredicto |
|---|---|---|
| **OpenRouter free** (settings.json `ANTHROPIC_BASE_URL`/`AUTH_TOKEN`/`MODEL: openrouter/free`) | Apuntar Claude Code a modelos gratis | 🟡 decisión: privacidad (código a 3º) + calidad << Opus. $0. |
| **NVIDIA build.nvidia.com** | API key gratis, Kimi/Minimax/GLM/DeepSeek/Llama en nube NVIDIA | 🟡 mismo patrón que OpenRouter |
| **Sequential Thinking MCP** | Razonamiento paso a paso | 🟡 oficial, bajo riesgo, requiere añadir a settings |
| **Firecrawl / Perplexity MCP** | Scraping anti-bot / búsqueda IA | 🟡 se solapa con apify/WebSearch/Chrome |
| **Skills diseño: Emil Kowalski (motion) / Impeccable / Taste** | Movimiento + "buen gusto" anti-genérico | 🟡 se solapa con frontend-design; motion/taste podría complementar |
| **MCPs diseño: 21st.dev Magic / Stitch / Pencil / Draw.io** | UI/pantallas/diagramas desde texto | 🟡 terceros; útil tu-tienda/tu-proyecto-web |
| **n8n MCP** | Claude arma flujos n8n | 🟡 relevante para ia-aplicada/agencia-ia |
| **G-Stack / Addy Osmani / "Matt"-Berserk / itmpl** | Equipos multi-agente plan→build→QA→deploy | 🟡 se solapa con feature-dev + pr-review-toolkit |

**Descartado (🔴):** agregador "todos los modelos premium gratis" (v19, sketchy/ToS), ClaudeMem (tu `.cerebro` es superior), AntiGravity 400+ skills / Everything Claude Code (bulk → rompe [[reference_plugins_trimmed]]), LightRAG (cubierto por cerebro_grafo), claims "94%/70x menos tokens" (hype medido).

**APLICADO 2026-06-19 (el usuario eligió 4 de los 🟡):**
- ✅ **emil-design-eng** skill instalada (ver sección INSTALADAS arriba).
- ❌ **OpenRouter free** → **DESCARTADO por el usuario 2026-06-19** (sandbox `scratch\openrouter-test\` borrado).
  Nota verificada para el futuro: el config correcto era `ANTHROPIC_BASE_URL=https://openrouter.ai/api` + `ANTHROPIC_AUTH_TOKEN`
  + `ANTHROPIC_API_KEY=""` + mapeo `ANTHROPIC_DEFAULT_*_MODEL` (el `ANTHROPIC_MODEL: openrouter/free` del video era FALSO).
  Razón del descarte: calidad << Opus + código a un 3º; no vale para el trabajo fino.
- ✅ **Sequential Thinking MCP + n8n MCP** (`czlonkowski/n8n-mcp` v2.59.1, `@modelcontextprotocol/server-sequential-thinking`):
  en sandbox de proyecto `scratch\mcp-test\.mcp.json` (NO global → respeta RAM/regla #10). n8n es el pesado (base de nodos).
  Promover a user-scope con `claude mcp add -s user ...` si resultan útiles (comandos en `scratch\mcp-test\LEEME.md`).

**INVESTIGADO + DESTILADO → skill nativa `equipo-ingenieria` (2026-06-19):** A pedido del usuario ("skills de un equipo de
IAs como equipo de ingenieros para mejorar revisiones y hechura"). Dos agentes leyeron el contenido real de:
- **`garrytan/gstack`** (16k★, Garry Tan/YC): NO instalar (corre bash, escribe `~/.gstack`+`~/.claude`, install `./setup`,
  ~70% solapa). Ideas rescatadas: `/plan-ceo-review`+`/office-hours` (reto de scope), `/retro` (retro desde git),
  `/ship` con gates, `/codex` (review cross-model). Atado a web-JS/Apple lo demás.
- **`addyosmani/agent-skills`** (Addy Osmani): NO instalar entero. Diferenciador real = **exit-criteria por fase**
  (checkboxes con evidencia) + tablas anti-racionalización + `web-performance-auditor`. a11y/CWV ya cubiertos por
  skills locales (`accessibility`/`core-web-vitals`/`performance`/`web-quality-audit`) → no duplicar.
- **Matt Pocock** (caveman/grill-me/handoff): no traído (grill-me ≈ brainstorming; handoff ≈ tu `.cerebro`).
- **Resultado:** skill nativa `~\.claude\skills\equipo-ingenieria\` (SKILL.md + 4 references:
  reto-scope / gates-y-anti-racionalizacion / cross-model-codex / retro-git). Markdown puro, sin tocar config global,
  complementa superpowers/feature-dev/pr-review-toolkit sin duplicar. Cross-model = handoff a Codex vía `.cerebro` (no hay codex CLI).
