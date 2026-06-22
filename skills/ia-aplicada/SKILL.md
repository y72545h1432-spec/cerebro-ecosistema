---
name: ia-aplicada
description: Applied AI knowledge distilled from the @ImperiaIA (ES) and @brendanautomation (EN) YouTube channels. Use when the user asks how to apply Claude/AI to daily work or business — Claude Code for non-programmers, saving tokens/limits, Claude Skills (create/download/vet), AI Operating System (MCP servers, business automation: CRM/invoicing/inbox/thumbnails), Claude as personal assistant (dashboard + Telegram bot), automating video editing/SEO/newsletters with Claude Code, AI voice agents (Vapi/Retell/ElevenLabs, prompt engineering, guardrails, testing), n8n vs Claude Code, building websites/apps with AI, private/local AI — or mentions ImperiaIA or Brendan Automation. Complements `video-editing` §10 and `claude-api`.
---

# IA aplicada — destilado de @ImperiaIA (ES) + @brendanautomation (EN)

**Fuentes**: transcripts en `~\tu-tienda\_archivos_trabajo\imperia_ia\` y `_archivos_trabajo\<canal-cliente-2>\` (`<videoid>.txt`); mapas id→título en `_archivos_trabajo\_titles_imperia_ia.txt` y `_titles_<canal-cliente-2>.txt`; notas en `_archivos_trabajo\_skill_notes\<canal-cliente-2>.md`. ImperiaIA = ecosistema Claude para usuarios; Brendan = automatización de negocio con Claude Code + voice agents + n8n. Lee el transcript original para el paso a paso exacto.

## 1 · Claude Code desde cero (sin saber programar) [6tTstj2UZFo]
- Claude Code = **agente** que escribe/gestiona software autónomamente; le hablas en lenguaje natural. Instalación: terminal (comando de la web), app de Claude (pestaña Code), o extensión VS Code.
- Arranque de proyecto: pídele que cree la base él (no montes tú el entorno) → **`/init` obligatorio** (crea `CLAUDE.md` = memoria del proyecto; sin él, re-investiga el código en cada prompt y gasta 5-10× más límite; pedirle mantenerlo al día).
- **4 modos**: default · accept edits · **plan mode (el importante: estudia antes de tocar; aprueba el plan y ejecuta solo; casi nunca se equivoca)** · auto mode (Opus, evalúa seguridad de comandos solo).
- Modelos/esfuerzo: Opus para programar (esfuerzo X-High por defecto, medio para cambios menores); Sonnet siempre en alto (gasta pocos tokens).
- **Gestión de contexto (clave)**: conversaciones CORTAS centradas en UNA tarea → `/clear` al terminar (con `/resume` recuperas); `/context` para ver ocupación; `/compact` con instrucciones antes de acercarte a 200k — **a partir de 200k tokens cada token cuesta el DOBLE** (documentado por Anthropic); `/usage` para ver gasto de sesión/semana.
- Extras: comandos custom (pídeselos en lenguaje natural), `/plugin` + marketplaces de skills, **capturas de pantalla pegadas** para iterar trabajo visual, varios Claude en paralelo.

## 2 · Claude como asistente personal [IPfNbktThco]
- Patrón: **dashboard personal** (nutrición, inbox, tareas, calendario, movimiento) + **bot de Telegram** al que mandas voz/foto/texto y actualiza todo.
- Stack gratis: diseño base en Claude Design → exportar a Claude Code (capa funcional) → **Supabase** (datos) + **Vercel** (hosting, variables de entorno) + BotFather (token Telegram) + API key de Anthropic (Sonnet o incluso Haiku basta; Opus innecesario) + OpenAI/Whisper solo si quieres audios.
- El sistema mejora con el uso: con un mes de datos, Claude analiza patrones (ej. dieta vs gimnasio) y sugiere cambios. Accesible desde el móvil; todo personalizable pidiéndoselo a Claude Code.

## 3 · Claude + herramientas de trabajo (títulos índice, transcripts disponibles/pendientes)
- **Claude × CapCut "modo dios"** [1Ov5UXSKglg] y **Claude conectado a Premiere Pro** [1zGj_bM7GaM]; "Despedí a mi editor por Claude" [iDkJR3YJpeA] → ver también skill `video-editing` §10 (LUTs, SRT counters, motion graphics por código).
- **Claude + Excel** en <10 min [TJ58Ym_ztM8]; **Claude/ChatGPT + PowerPoint** para presentaciones [nRIO2NIxLK8].
- **Webs de +$10,000 con Claude** gratis y sin programar [kuLE6T85A2w]; **Claude Design** guía completa [4A_o4ToVwbE] y alternativa Open Design [lsVXH85jCiM].
- **IA privada/local en tu PC** (sin pagar) [rIskSC0FnwE].
- Planes de Claude: ¿merece la pena pagar? [0GEk7og8tC0]; **ahorrar límites de uso** [XUS3IVickNo]; reviews de modelos (Opus 4.7/4.8, comparativas con ChatGPT) [Y4nz5I837mM, FQCkDbdY2Gk, eGxDavfYLIY, TqnniIRd60Y]; Nano Banana para video (Gemini) [nWXnayjskXI].

## 4 · Ahorro de tokens en Claude Code — 10 hacks de Brendan [qns5Tx1x6Jk]
1. `CLAUDE.md` raíz + anidados por carpeta (contexto gratis en system prompt). 2. `/compact` en sesiones largas. 3. `/clear` al cambiar de tarea. 4. Referencias específicas (ruta+función; lo vago = lee todo el codebase). 5. Ignore file (node_modules/builds/assets). 6. Prompts concisos: qué + dónde exacto + output esperado. 7. **Sub-agentes** para exploración/tests/búsquedas amplias (el detalle no entra al contexto principal). 8. Modelo según tarea (Opus solo razonamiento profundo; Sonnet día a día = el mayor ahorro). 9. Plan mode (evita rondas de "no era eso"). 10. **Hooks** para checks automáticos post-edit.

## 5 · Claude Skills [Sq1hWHxXMC0, iMWC6mdPS5g, n_ByvhyVkP8]
- Skill = markdown con instrucciones de CÓMO hacer una tarea a tu manera; se escribe una vez. Marketplaces: MCP Market, SkillsMP (ej. "landing page anti-AI-slop" transforma webs genéricas).
- **Lo mejor: skills propias desde tu trabajo previo** ("aquí están mis mejores X, crea una skill basada en esto") > cualquier skill pública.
- Las skills no ejecutan MCP/API solas — orquestan herramientas configuradas → ⚠️ **vetar skills de terceros** antes de instalarlas (pueden incluir tool calls indeseados).

## 6 · AI Operating System (negocio entero desde un chat) [-A2kYFrq7fg, Rd_2MRHJLA0]
- Un Claude Code con: **CLAUDE.md maestro** (contexto del negocio) + **MCP servers** (Gmail, Stripe, accounting, Analytics, CRM propio…). Oficiales: claude.ai → Connectors (aparecen en `/mcp`); no oficiales: "instálame el MCP de <app>".
- Reemplaza SaaS: CRM construido con Claude Code [IETh8bEQVV8], invoicing end-to-end (CRM→PDF→draft Gmail), thumbnails que aprenden de tus analytics, monitoreo de inbox. Meta: eliminar toda tarea repetitiva.
- Automatizaciones probadas con Claude Code: **edición de video completa** (Descript para cortes → Claude Code + Remotion + ffmpeg + Whisper → render; ver `video-editing` §10) [G0EH0xdy2-E], SEO [2GNTl6bCYmQ], thumbnails [o9byLiyuheQ], LinkedIn [1q0RmehD8SU], newsletter [Rs58AAIyI68], slide decks [YiwdkM2W8CI], short-form+VEED [6hY0jCy9ujM].

## 7 · AI Voice Agents (pilar Brendan) [jg1j1Rv8SkA, jDPXWMUVUPE + cursos Vapi/Retell/ElevenLabs/LiveKit]
- Stack: Vapi (principal), Retell, ElevenLabs Conversational, LiveKit; integraciones n8n/Make/GHL/Calendar.
- **El prompt ES el producto**: rol (personalidad+objetivo) + script + **guardrails** (no desviarse del objetivo de llamada) + **knowledge base** externa (RAG; sacar info del prompt = menos costo por generación).
- **Ciclo de 8 fases** (diseño→implementación→evaluación→refinamiento→iteración→validación→deploy→mantenimiento): solo 2 son "construir"; el valor = **testear con transcripts reales** e iterar (assistant en 10 min; CONFIABLE = semanas).
- Casos: recepcionistas (dental/HVAC/restaurantes), revival de leads, recordatorios cita/factura, speed-to-lead, e-commerce.

## 8 · n8n vs Claude Code [XmzJhShHMnI, lGLwLOERp6c, eQNkwr82KVo]
- n8n = workflows deterministas con triggers/integraciones visuales (corre solo, 24/7); Claude Code = trabajo ad-hoc inteligente y construir sistemas. Se combinan: Claude Code crea/edita workflows de n8n. (Nota tu-tienda: hay MCP de n8n conectado.)

## 9 · Canales adicionales (biblioteca consultable, carpetas en `_archivos_trabajo\`)
- **@RoboNuggets** (`robonuggets`, 134 — Claude Code avanzado, EN): second brain auto-mejorable con 1 prompt [K2BpNt3UBOQ], 7 skills de uso diario [UpgjdQJShWg], microapps agénticas [N9fRqffXdqQ], /goal para Claude Code/Codex [aEDq1bBynOg], usar Opus mejor que el 99% (del founder de Claude Code) [c1QHHRzmMXE], Claude para small business (admin work) [sys8N0etQfw], **HyperFrames V2 [4E2I_NJkzhI] + skill de ads cinemáticos [t6w-IpKjW1s]** (→ `video-editing`/`video-marca`), Claude+Canva [fT3rsZ22C4A], HTML slides (PowerPoint killer) [t2ELuj2prA0], Claude+GPT-Image-2 para diseño [uuP3lDlKfCI], sistema de diseño 67k installs [tohWF-kb67g].
- **@NexumAI** (`nexum_ai`, 126 — Claude Code ES + automatización de negocio): tutorial completo 2026 [u8Fe_WZ6lWE, 1o-srYjTCug], **reducir tokens 90% — DESTILADO [0MPDOn9YWik]** (leído 2026-06-10; fundamento: cada mensaje relee TODA la conversación → costo compuesto, no lineal; consumos invisibles = CLAUDE.md recargado siempre + MCPs conectados sin uso + adjuntos): (1) modelo por tarea — Opus solo para planear/decisiones, Sonnet polivalente, Haiku formateo (`/model opusplan` = Opus en plan mode, Sonnet en el resto); (2) planear ANTES de implementar (plan en archivo, iterar hasta aprobado); (3) `/clear` entre tareas no relacionadas — el hábito que nadie tiene; (4) 1 prompt encadenado ("primero X, luego Y, luego Z") > 5 prompts separados; (5) medir con `/context` (desglose por categoría) + `/usage`; (6) desconectar MCPs que no usas; (7) CLAUDE.md corto: resumen de CÓMO está ordenado el workspace, no el contenido de cada archivo; (8) **la caché dura 5 min** — pausa >5 min = relectura completa → `/compact` o `/clear` antes de pausar; (9) skills compactadoras de output (ej. "caveman" −65%). las 22 skills que necesitas [dj7uAA2Phqg], skill Remotion para videos [bteoTz-jXd0], agente WhatsApp gratis [uudeznYRulA], marca personal +30k followers en 30 días con Claude Code [HEOaurSDAvQ], **10 reels en minutos con Claude [zgnsMLwdceE]**, automatizaciones por sector: clínicas [IoNXQ7Ars3w], ecommerce [z2SSOZOsQcc], Mercado Libre [nCEicRhF1iM], seguimiento WhatsApp [QumNMa-_8mc], qué aprender antes de automatizar [IpDgG8K8BLI].
- **@centeia-education** (`centeia`, 135 — IA para negocio/productividad, ES): **AEO, el nuevo SEO** (que ChatGPT/Gemini/Perplexity recomienden tu marca) [qSLK72z8AfM], top 5 de 100 Claude Skills [MSA6XcTfmXo], negocio con Claude en 21 días [Kp1IftU5opA], Claude+Notion [UR7_PfAUrPo], NotebookLM avanzado [8X0pYIYdkWU, Fm2My7XEaH8], Claude Routines [8GS4sfC4IC0], Claude+Figma [s9YQJ7N95RM], **videos de producto con Claude+Remotion ("adiós Premiere/AE") [_g5BGHJU9p4]** (→ tu-tienda directo), sin tokens: errores que cometes [HrEsM-y6Hp0].
- **@LucianoMattica** (`luciano_mattica`, 8): dashboard con Claude Code [MIu5XTGU0oU], Claude Code+Vercel Agent Browser [HAh4dyQoVtA], **Claude Code+HyperFrames resuelven la edición de video [FhCyKN0nJnk]**, 3 formas fáciles de automatizar [t7PUaqCQxpQ], negocio desordenado [WXJ_MglLH_k].
- **@juanpe.<empresa-cliente-1>** (`<canal-cliente-1>`, 113 — ecosistema Claude + negocio): Claude Code curso completo ES [qctLhAeIIrA], 10 mejores de 100 skills [qRKbqu1DfKY], Claude Code gratis con OpenRouter [zLZf8wUFL38], DeepSeek+Claude Code 10× más barato [op3kt8sD-Sw], Claude Code+Playwright agentes web [LO8uDHDlyA0], **Claude Code+HyperFrames tutorial [fPXP5QIpB6g]**, CRM €3,000 en 21 min [F9JYnIPLIIM], WhatsApp agent €3,000 [2bBT31ly6G8]. Negocio → skill `agencia-ia`.

## 10 · Más canales (descarga progresiva)
- **@wearenocode** (`wearenocode`, 283): vibe coding apps $109k/mes [GMrX0DaLDos], 7 niveles de dominar la IA [CP7Aj-7jers], Claude Cowork para no-técnicos [Cyyvb-r4zkA], 5 formas de ganar dinero con IA 2026 [0UACvpDYEBk].
- **@bencord** (`bencord`, 109): automatizar cualquier negocio 2026 desde cero [D-gcNGdHYz0], **vibe marketing [U5XdnPy42uE]**, cómo funciona un agent harness [z3KF8OaLCG4], reviews de modelos Claude (Fable 5, Opus 4.8).
- **@MigueBaenaIA** (`migue_baena`, 199): 31 business skills de Claude gratis [urZuDtTePWs], **"usas mal Claude Code: así lo usan los ingenieros de Anthropic" [UlwZ5hDTnQ8]**, apps sin código [3lyc8AA44Ik], Codex explicado [vD_PD2SGYYk], Gemini gems/features.
- **@soyalvaropareja** (`alvaro_pareja`, 54 — Claude para marketers): auditar Meta Ads con Claude Code [43hYND_jgLc], Cowork + plantilla [aR66YkFI94o], Projects vs Skills [3fIG3DTxf8c] → más en skill `marketing-digital`.
- **@claude** (`claude_oficial`, 119 — canal OFICIAL de Anthropic): demos de Fable 5 (Pokémon solo con visión, Factorio, simulaciones, CAD), casos de uso por profesión ("Working Like a Lawyer with Claude") — referencia canónica de capacidades.
- **@FaztTech** (`fazt_tech`, **196 transcripts ✓** 2026-06-10): harness engineering, apps completas con IA, token economy, Zerolang — leer transcript por videoid al usar.
- **@MeticsMediaEspanol** (`metics_media`, **68 ✓**): tutoriales Hostinger/VPS/Hermes, **webs de $10k con Claude Code**.
- **@SantiMunozIA** (`santi_munoz`, 15 parcial): los 2 ⭐ ya destilados en `marketing-digital` §8 (Claude+Google Ads ROAS 6.4× + método setup).
- En cola/parciales (ver `_skills_canales_estado.md`): nateherk (subagents top), MDALatam (reels IA, 9), Platzi, JuanGabrielGomila, la_inteligencia_artificial, AlanDaitch, HolaMundoDev, RingaTech, gustavo-entrala — la tarea de descarga fue RELANZADA 2026-06-10 15:25.

## 11 · FULL-PASS 2026-06-11 — Nate Herk · Santi Muñoz · MDA Latam

### 11a · @NateHerk — Subagentes, rutinas cloud y gestión de contexto [271 videos, 25 leídos]

**Subagentes (arquitectura "jefe + trabajadores") [e18sdZLwP7o]**
- Subagente = sesión Claude independiente con contexto limpio; el orquestador es la sesión principal.
- Patrón económico clave: **Opus orquestador + Haiku trabajadores = 4-10× ahorro**. Haiku lee 300 páginas, devuelve 3 bullets a la sesión Opus.
- Front matter YAML del subagente: `name`, `description` (trigger de invocación — ser preciso evita misfires), `model`, `tools`, `disallowed_tools`. Ubicación: `.claude/agents/` (proyecto) o `~/.claude/agents/` (global).
- Claude solo lee el front matter para decidir si invocar; el body completo se carga solo si se activa → economía de tokens.
- Cuándo NO usar: ediciones de 1 línea, pasos A→B→C secuenciales, tareas que necesitan preguntas interactivas.
- **Dynamic Workflows** [jZgcWCzxh1I]: Claude escribe JS → lanza 40-210+ subagentes en paralelo; se guardan en `.claude/workflows/`. Reservar para auditorías masivas (226+ productos); muy costoso (Nate gastó 50% del plan $200/mes en 30 min).
- → tu-tienda: usar subagentes Haiku para importar reseñas (`ae_reviews_to_judgeme.py`), enriquecer tags (`enrich_search_v2.py`), generar i18n en batch.

**Skill "Grill Me" — interrogatorio antes de construir [c0kaKxM2pHg]**
- Propósito: extraer TODO el conocimiento tácito antes de construir un skill/sistema. Sin este paso: 70% de éxito, 30 iteraciones; con él: 90% desde el primer intento.
- Claude te interroga pregunta a pregunta; tras cada respuesta escribe un checkpoint en `brainstorms/<tema>.md` (decisiones, Q&A log, flags abiertos).
- Prompt base (Matt Pocock): *"Entrevístame sin descanso sobre cada aspecto de este plan hasta llegar a entendimiento común. Recorre cada rama del árbol de decisiones. Para cada pregunta, da tu respuesta recomendada. Haz preguntas de una en una."*
- → tu-tienda: aplicar antes de construir el skill de video ads, flujo de catálogo CJ, onboarding de productos.

**Gestión de contexto — session handoff al 12-15% [_qZvORxGqI0]**
- A partir del 60-70% de la ventana, Claude empieza a olvidar y contradecirse. Compactación automática al 95% = ya tarde.
- Estrategia: al llegar al 12-15% del contexto (>120k tokens en Opus), ejecutar skill de **session handoff** → produce resumen, archivos clave, estado actual, preguntas abiertas → `/clear` → sesión nueva con mínimo necesario.
- `/rewind` tras un error = borra el "historial sucio" del intento fallido del contexto.
- → tu-tienda: crítico para sesiones largas de catálogo y watchers; implementar en `CLAUDE.md` que fuerce handoff antes del 20% de uso.

**Rutinas cloud — 24/7 sin PC encendido [ehg4fhydTgs, xJ5oz63mIec]**
- Rutinas cloud = prompts en infraestructura Anthropic; no necesita PC. Límites: Pro=5/día, **Max ($200/mes)=15/día**, Team=25/día; mínimo 1 hora de intervalo.
- Gotchas críticos: NO tienen `.env` local → secretos van en "Cloud Environment"; Playwright/cookies de browser NO funcionan remotamente; repo clonado se destruye post-ejecución → solo persiste lo pusheado a GitHub.
- Prompt ideal: orden explícito + "si falla, notificar vía Slack con el error" + sin confirmaciones interactivas.
- `/loop` en terminal: máx 7 días; trick — crear 2do cron que ejecute `/clear` cada 5 min para evitar context degradation en bucles largos.
- → tu-tienda: migrar rutinas "winning products" (días 1 y 15) y "organic content" (dom 9am) a rutinas cloud. `/loop` para tareas en sesión (monitoreo de stock, responder comentarios).

**Error handling para watchers en producción [Irk4-DO5qgM]**
- 5 técnicas: (1) **Error Workflow** separado en n8n (trigger de error → notifica Slack/email); (2) **Retry on Failure** en cada nodo; (3) **Modelo fallback** (si principal falla 3×, usar alternativo vía OpenRouter); (4) **Continue on Error** = si 1 item falla de 1000, los 999 restantes no se detienen; (5) **Polling** para APIs async (loop status "processing"→"completed").
- → tu-tienda: retry + continue-on-error en importación por lotes; error workflow que notifique si falla la importación de reseñas.

> Destilado completo: `_archivos_trabajo/_destilados/nate_herk.md`

---

### 11b · @SantiMunozIA — Meta Ads CLI, datos propios→targeting, anuncios en lote [121 videos, 10 leídos]

*(Videos pz6AIlkjWlc y uaMr9HpgJgE ya destilados en `marketing-digital` §8; no se repiten aquí.)*

**Meta Ads CLI — mayo 2026 [Yoq6Rga7QFk]**
- Meta lanzó su propio **Ads CLI** el 1 de mayo 2026: da a un agente IA acceso total al panel Meta (crear campañas, pausar/activar, A/B testing, catálogos, reportes, análisis pixel).
- Game changer: tracking end-to-end — Claude ve pixel + campañas + conversiones al mismo tiempo y cruza información.
- Instalación: Meta Business Suite → Configuración → Usuarios de Sistema → crear System User → app en modo producción (requiere URL política de privacidad).
- → tu-tienda: Claude ya tiene token permanente de Meta (`META_SYSTEM_TOKEN` en `.env`). Casos directos: A/B testing de copies Galaxy/Luna con 5 ángulos, análisis funnel pixel `1561114292244191`, rutina Monday 8am con reporte semanal de campañas.

**Datos propios → targeting → CTR 14% [dcBONQzoohk]**
- Flujo probado: datos del formulario de onboarding (1,000 respuestas) → Claude analiza → genera targeting ideal → Performance Max con $17/día → CTR 14% (vs 3-6% industria); ROAS 640%.
- Costo por lead bajó de 59 MXN a 6 MXN en 4 días (Google aprendiendo). No juzgar campaña antes del día 4.
- → tu-tienda: palanca disponible — datos de Quiz (`/pages/quiz`), perfiles Klaviyo, historial Browse Abandonment → Claude genera targeting → lanza vía Meta API o Performance Max. Vincular canal/landing a la campaña mejora CTR significativamente.

**Generación de anuncios en lote por catálogo [TiuaUyNVPik]**
- Flujo Make.com: Airtable (URL producto) → descargar imagen → GPT-4o-mini analiza imagen → genera prompt para Gemini imagen edit → Gemini edita → subir a Drive → actualizar Airtable con URL.
- Truco: GPT como intermediario que "traduce" la imagen a un prompt — permite procesar cualquier producto sin instrucciones manuales por producto.
- Cambiar temporada = cambiar 1 línea en el GPT ("para Navidad", "para envío gratis").
- Costo: ~$0.40-0.50 por imagen de anuncio. 100 URLs en Airtable → 100 anuncios en 1 clic.
- → tu-tienda: 226+ productos en catálogo → aplicar antes de BFCM 2026. Adaptar: `products_en/*.jpg` → tabla Airtable → flujo Make.com → anuncios Meta listos.

**Análisis de competidores automatizado [T9VV03vS4gU]**
- Stack: n8n + Apify ($5 gratis) para scraping de cualquier red social → Assembly AI / Supadata para transcripciones → GPT-4.1 mini para scoring 0-100 (hook, claridad, valor, engagement) → Airtable con scores.
- Output por post: score 0-100, keywords, sentimiento, idea para video propio, fortalezas/mejoras.
- → tu-tienda: scrapear cuentas de cozy lighting / tu-nicho antes de crear contenido → seleccionar temas ganadores → alimentar pipeline de video Claude.

**Carruseles automatizados con Nano Banana [1Ffz4LIhQMg]**
- Skill `/carrusel` + tema → Claude planifica estructura → genera prompts para Nano Banana Pro (Kie AI) → generación **en paralelo** → Pillow (Python, gratis) compone imagen + texto → guarda localmente.
- Precio: $0.09/imagen (Nano Banana Pro). Carrusel 8 slides = $0.72.
- → tu-tienda: carruseles de productos (comparativas, "5 ideas cozy lighting", tutoriales setup) desde `assets/marketing/products_en/`.

> Destilado completo: `_archivos_trabajo/_destilados/santi_munoz.md`

---

### 11c · @MDALatam — Stack Nano Banana + Higgsfield + Claude para reels, GPT de marca, efectos CapCut [27 leídos]

**Stack de reels cinematográficos [ROQzWOuJsJw, 7FH1CBBX8Jc]**
- Trío principal: **Nano Banana** (imágenes de producto con texto) + **Higgsfield** (video IA con motion, MCP ya conectado) + **Claude** (guion + copy del reel). HeyGen opcional para avatar/voz clonada.
- **Make Reels** (makereels.com): tema → reel completo con guion, imágenes, voz y hashtags en segundos. Adaptable para tu-tienda: "5 razones para llevar el proyector galaxy a tu cuarto."
- Grok: sube 3 imágenes → crea imagen compuesta → convierte a video con movimiento (gratis, inmediato).
- Videos de escenas animadas [MswupCQBMiI]: n8n + GPT-4o-mini (guion 4-6 escenas) + Nano Banana (frame inicial + frame final) + Wan 2.1/BO3 en Kie AI (animación A→B + audio) → ~$2 USD por video de 4 escenas.

**GPT de marca para contenido automatizado [e0-KtuHuFc8]**
- Un GPT personalizado entrenado en el tono + categorías + reglas de la marca genera: carruseles 10 slides + guion de reel + prompts de imagen + hashtags + CTA, todo en segundos.
- Reels más efectivos: **15-20 segundos máximo**. Añadir en el GPT: "no pasar de 20 segundos."
- Prompts negativos: "nunca contenido con imágenes negativas / nunca salir del tono cozy." Positivos: "usa siempre gatillos mentales en portadas."
- Entrenar GPT con transcripciones de creadores de referencia: Rask (u otra gratuita) → PDF → subir como knowledge base.
- → tu-tienda: crear GPT tu-tienda con tono cozy/dreamy/smart-home, categorías (proyectores, lámparas luna, tiras LED), reglas (reels 15-20s, carruseles 10 slides, hashtag EN siempre, CTA a `/pages/quiz`).

**Carrusel controversial que viraliza [FmKz-O3LEcI]**
- Estructura de 9 slides: (1) título negativo/provocador ("Basta de proyectores baratos") → (2) gancho + contexto → (3-7) denunciar errores / construir el hilo → (8) valor real + conclusión → (9) CTA fuerte.
- Métrica sana para cuenta pequeña: 25-30% engagement. Alcance: cuentas chicas deben llegar al 50-60% de seguidores.
- → tu-tienda: "Por qué el proyector barato de Amazon arruina tu cuarto (y qué usar en cambio)."

**Efectos CapCut para productos [AA_gmoxfu0s, f4C1cpQrOQA, Z2dYEvHdRLI, C_P0YR0qS3o, nkQNvTfov5w]**
- **Subtítulos dinámicos** (palabra por palabra): CapCut → Texto → Subtítulos automáticos → activar "subtítulos dinámicos" → editar lote. +20-40% retención.
- **Producto flotante**: foto lugar vacío + foto producto → superposición → eliminar fondo → animación "invertir". Para proyector galaxy "apareciendo" en habitación oscura.
- **Efecto glitch**: copiar clip → superposición → eliminar fondo → dividir cada 5-6 frames → animación "Combo 3". Para hook en primeros 3 segundos.
- **Dispersión de partículas**: Congela frame → convierte a foto → Estilo → Dispersión. Efecto mágico/dreamy para lámpara luna o proyector.
- **Texto con relleno progresivo** (completion bait): texto solo con trazo → copia con relleno → animación "barrido hacia arriba" 1.5s → exportar → superposición con filtro "empalmar". El espectador espera que el texto se complete = retención +.
- **Pauta micro ($5-10) para alcanzar el 100% de seguidores** [FF6cdam-v_4]: Meta Ads → campaña Interacción → público "interactuaron con mi cuenta en 365 días." Especialmente útil en lanzamientos de producto.

> Destilado completo: `_archivos_trabajo/_destilados/mda_latam.md`

---

## 12 · FULL-PASS 2026-06-21 — lote destilados _LOCAL (12 canales)

### 12a · Bencord — FULL-PASS 2026-06-21
*(canal destilado; IA aplicada / Claude / automatización; ref: `_archivos_trabajo/_destilados/bencord_p1..p4_LOCAL.md`)*

**Stack agéntico: Claude Code vs OpenCL vs N8N** [3fJ0aEyWu4c] [MWuasFiCmWs] [QBdqFJj7pqc] [7HlfFHLoYK8]:
- Claude Code: opera en carpetas aisladas, contexto limpio, solo modelos Anthropic (Opus/Sonnet); evolución: 60 min manual → 1 min automatizado; ideal para tareas específicas sin contaminación de contexto. → aplica: hub de automatizaciones tu-tienda (curación, i18n, reviews), manteniendo contexto <48% para evitar degradación del 40%+.
- OpenCL: acceso total al sistema (Mac Mini o VPS 24/7), soporta GPT/Anthropic/modelos locales, costo energético ~$2–$3 USD/mes; mayor riesgo de seguridad; ideal para asistente integrado permanente. → aplica: daemon de operaciones tu-tienda corriendo en segundo plano con skills de soporte/inventario.
- N8N: best para automatizaciones determinísticas (600 ejecuciones/día, webhooks, triggers definidos); instalar en VPS Hostinger es 70% más barato que cloud N8N ($24/mes); Docker Compose + dominio propio (ej. `benjaeselmejor.cloud`) con 100 workflows preinstalados. → aplica: flujos de pedidos, reportes, publicaciones en RRSS desde Google Sheets.

**Routines y skills de Claude Code — automatización sin servidor** [jtvE_ZVWQpo] [9JvIRYLwetU] [dJYauJwcalA]:
- Routines Anthropic: triggers Scheduled / HTTP POST / GitHub Events; límites Pro 5 runs/día, Max 15 runs/día, Enterprise 25 runs/día; mínimo 1 hora entre runs; reemplaza N8N para usuarios no técnicos. → aplica: newsletter semanal tu-tienda, reporte de ventas diario, actualización de colecciones sin servidor local.
- Skills como SOPs digitales: 3–4 skills/semana → agente maneja 90% del negocio en 3 meses; benchmark 30 min manuales ↔ 1 min automatizado; "YouTube Creator" skill reduce planificación de 2 días a <10 min; framework SMART (Skills-MSP-Artifacts-Repetición-Testeo); 87,000+ skills en skillsmp.com. → aplica: skills `tu-tienda-listar-producto`, `tu-tienda-curar-producto`, `tu-tienda-margenes` ya existentes; crear `tu-tienda-ads-meta` y `tu-tienda-ugc-batch`.
- agents.md <200 líneas: archivo central de identidad del agente; mejora con uso; usar estándares abiertos para interoperabilidad 2027. → aplica: mantener `CLAUDE.md` + `agents.md` como base del orquestador tu-tienda.

**Modelos IA — benchmarks y selección por caso de uso** [8HwaET0jxzE] [5mqVPEwN_dQ] [EW38h93vO2g] [k0RmZG87XTU] [qab9pKpPvio]:
- Opus 4.8: +63 puntos vs GPT 5.5 en benchmarks independientes; Fast Mode 2.5x más rápido, 3x menos costo; contexto 1M tokens (degradación >400k); 75% menos fallos en código que Opus 4.7; niveles high/extra de esfuerzo.
- GPT-5 (API): $0.05/1M tokens input, $0.4 output (Nano); GPT-5 Mini supera O3 en benchmarks matemáticos; parámetros `reasoning_effort` (high/low) y `verbosity`; alucinaciones en salud reducidas 15% (a 1.6%).
- Fable 5: 29.3 vs 13.4 GPT en razonamiento alto nivel; $10/1M tokens input, $50 output (doble Opus 4.8); migró 50M líneas de código Stripe en 1 día; dominio ciberseguridad 78% vs GPT 34%.
- Setup híbrido recomendado: Nemotron 3 (NVIDIA, gratis, 85.6 Pinch Bench) para 90% de tareas + modelo premium (Opus/GPT-5) para 10% complejo → ahorro 90% del costo mensual ($500–$2k → $10–$20/mes). → aplica: Qwen3-8B local (Mano Derecha) para cola + Claude Sonnet para decisiones críticas tu-tienda.

**Automatización de leads y CRM con IA** [6IJoZivAQYg] [6I780zheHzU] [D-gcNGdHYz0] [8hqFUQNFPew] [FQZGoSwdS_0]:
- Scorecard Make + Airtable + Fill Out: clasifica leads en "Muy calificado / Medianamente / No califica" via GPT-4o/O3 Mini; variables estructuradas (nombre, urgencia, presupuesto, celular sin '+' ni guiones); notificaciones Slack + WhatsApp Business Cloud; downsell automático para no calificados; plan Pro Make gratuito 3 meses (partner académico).
- Go High Level + Claude Code via MCP: token PIT (hasta 139 permisos); crea contactos, notas, oportunidades, calendarios con lenguaje natural; funnel $10k+; conecta Telegram/Slack/WhatsApp/Discord; ~$97/mes; 30 días gratis.
- Teoría de restricciones (TOC): identifica paso más lento del embudo (ej. 7 leads/hora vs 10 en otras etapas); postventa automatizada (recordatorios cada 30 días para bienestar, cada 5 meses para producto físico); reduce no-show del 30% al 5% con WhatsApp pre-autenticado.
- Agentes Hermes en VPS Docker: token límite <200k (20%) para evitar degradación; prompts <200 líneas mejora precisión 40%; cronjobs para campañas (Black Friday, etc.); gestión CRM 100% desde Telegram. → aplica: scorecard para leads tu-tienda (formulario Fill Out → clasificación GPT → email personalizado → WhatsApp confirmación).

**Generación de contenido y UGC con IA a escala** [PcXe9oej_z4] [wxvI7N7IFQE] [EFY0X7ml6kY] [KVunZDROG2s] [skPqG5OSCWk]:
- UGC con Sora 2: videos 4 seg a $0.10/seg = $0.40/video; 100 videos UGC = $40 total vs $100+/video con influencer; dimensiones 720x1080 (vertical) o 1024x768 (horizontal); flujo Imagen→Resize→Sora 2→Google Drive→MP4→interfaz.
- Pipeline N8N + AirTable: concept board → prompts por escena → NanoBanana/Wave Speed (imágenes) → VO3.1 (video, 8 seg por $0.30 total) → Suno (música, 2 min/canción) → ElevenLabs (voz, Voice ID); checklist cada 15 seg para verificar renders; 100+ videos en 5 min.
- LoRA/Flux Dev: entrena con 12–20 fotos, 100 pasos/imagen (1000 para 10 imágenes); costo ~$0.025–$0.04 por imagen en Replicate; usar ZIP etiquetado "Photo of [Nombre]"; trigger words para contextos específicos. → aplica: entrenar LoRA con productos tu-nicho tu-tienda (15–20 fotos de lámparas/proyectores en contextos cozy) para creativos de Meta Ads.
- Filmora AI: Auto Reframe horizontal→vertical; AI subtítulos; 9 versiones del mismo video para TikTok/Reels en segundos; Text-based editing; batch 1000 shorts programados.

**Meta Ads automatizadas con Claude Code + API Meta** [mfk82SbXgGo] [U5XdnPy42uE] [FyXu6v783Fc]:
- Cloud Code + API Meta: control total sin Meta Ads Manager; retargeting por país con CPA filtrables (ej. EE.UU. $45); copy dinámico por cultura (Chile/España/México); 10+ creativos diarios con NanoBanana; test semanal → elimina 9/10 peores → deja top 1; ROI +40% vs manual, CTR +25%.
- Vibe Framework (Visión-Insumos-Brain-Engine): HigsField + ChatGPT Images 2 genera creativos y landing pages; 3 prompts = 1,000 correos personalizados vs 6 semanas manual; Apollo + Instantly tasa de respuesta 1%→3–4%; costo operativo → $0/mes solo con Cloud Code + APIs.
- Reducción stack: de $1,903 → $500/mes reemplazando suscripciones con Cloud Code + MSPs (1000+ integraciones Google Drive/Slack/Notion); tokens como nuevo modelo de monetización vs suscripciones fijas. → aplica: automatizar Meta Ads tu-tienda US-first por país, copy en inglés con cultural fit, creativos de tu-nicho/bienestar en batch semanal.

**Email outreach y captación de leads B2B/B2C** [GdcEwByOikw] [LuyxtSmYeXU] [aJ8ey_WJ0f8] [zSPvxqSc3kc]:
- Cold email stack: Instantly ($37/mes warmup) + Apify/Apollo (leads por nicho ~$5–$10 por 1k correos); dominios precalentados en marketplace; tasa realista 1–3% respuesta; 50–100 emails/día para no quemar dominio; video Loom 3–5 min = 8x conversión; ROI >$5k por inversión de $1k.
- Menichat + Make + MailerLite: 6,000+ emails en 6 meses; trigger por palabras clave comentario Instagram ("guía") → DM automático → captura email → envío guía PDF → upsell; 10+ variantes de respuesta para simular humano; gratis hasta 1,000 emails MailerLite.
- Research de dolor en Facebook: Apify scraper grupos Facebook ~$0.20/50 posts; GPT-5 clasifica variables dolor/frecuencia/potencial (1–10); reporte semanal automático vía Make + Gmail; 10,000 tokens GPT-5 suficiente para análisis profundo. → aplica: extraer dolores en grupos Facebook de tu-nicho/Wellness US; alimentar copy de ads y descripciones de producto tu-tienda.

**Infraestructura agente: VPS, acceso remoto y seguridad** [Au-igeiNF2c] [M8kOnNLL-3E] [FQZGoSwdS_0] [z3KF8OaLCG4]:
- Mac Mini 24/7: $2–$3 USD/mes energía; `claude remote control` desde celular (Plan Pro/Max requerido); reconexión automática; acceso total a archivos + MCP locales; migración fácil desde OpenCL.
- Framework Soul (Setup-Orchestration-Unify-Liberty): soul.js para personalidad del agente; CloudHub/MolHub para skills (Sonos, Whisper, Slack, Trello); Hardbeat para tareas proactivas horarias; Tailscale para ocultar IP pública (gratis); Browser Control Chrome Extension para scraping sin API.
- Arnés > modelo: modelos cambian cada 3 meses, arnés permanece; contexto <48% (ideal <20%) para evitar pérdida de eficiencia 40%+; memoria en archivos externos (`agents.md`, `progress.json`); roles separados Orquestador (Claude Code) + Implementador (Codex) + Revisor (Cursor); estándares abiertos `agents.md`/HNCMD para interoperabilidad 2027. → aplica: arquitectura tu-tienda ya sigue este patrón; reforzar con `progress.json` para estado de cola y separar roles de curación vs publicación vs reseñas.

### 12b · Ringa Tech — FULL-PASS 2026-06-21
*(canal destilado; IA / machine learning / tutoriales; ref: `_archivos_trabajo/_destilados/ringa_tech_p1..p3_LOCAL.md`)*


**Fundamentos de redes neuronales y funciones de activación** [CU24iC3grq8] [_0wdproot34] [aFZEvQDTSyA] [iX_on3VxZzk]:
- Perceptrón con pesos y umbral simula toma de decisiones; red densa 28×28 alcanza 97.3 % en MNIST con 5 épocas, ~98 % con más. → aplica: clasificar imágenes de productos tu-nicho (detectar tipo de lámpara/termostato) con dataset propio de ≥60 k ejemplos.
- ReLU es la función de activación por defecto en capas ocultas (f(x)=max(0,x), derivada simple, no acotada); Sigmoid solo en salida binaria; GELU en Transformers/BERT/GPT; Swish supera a ReLU en visión; MISH supera a Swish en detección (YOLOv4). → aplica: elegir GELU si usas modelos de lenguaje, ReLU si entrenas CNNs propias para imágenes de producto.
- Backpropagation ajusta >50 k pesos mediante gradiente descendente con optimizador Adam (lr=0.001 por defecto); función de costo MSE para regresión (ej. °C→°F), SparseCategoricalCrossentropy para multiclase. → aplica: predecir consumo energético o precio dinámico con datos históricos de ventas tu-tienda.

**Redes convolucionales (CNNs) y visión artificial** [4sWhhQwHqug] [AwTH_0yW9_I] [DbwKbsCWPSg] [ZyauOVzjg9Q]:
- CNN con 32 núcleos 3×3 (RGB → 3 convoluciones por núcleo = 96 totales) + MaxPooling 2×2 logra >95 % en MNIST; red densa falla a <50 % si imagen cambia posición/tamaño. → aplica: detectar defectos en fotos de productos o categorizar imágenes del catálogo automáticamente.
- Dropout 50 % + aumento de datos (rotación ±30°, zoom 15 %, flip, shift ±15 %) corrige sobreajuste; dataset "perros y gatos" de TensorFlow (~23 k imágenes a 100×100 px, float32/255) con 3 pares Conv+MaxPool (32→64→128 filtros) y capa densa 250 neuronas es la arquitectura base. → aplica: escalar el mismo patrón para clasificar luces, proyectores, difusores.
- Operadores Sobel y Canny detectan bordes; convolución con kernel 3×3 y fórmula Pitágoras (√(H²+V²)) da magnitud; reducción de ruido con algoritmo Canny reduce 40 % el tiempo de procesamiento. → aplica: preprocesar fotos de producto antes de clasificar (limpieza de fondo).

**Transferencia de aprendizaje e inferencia en producción** [9Dur_oUMGG8] [JpE4bYyRADI] [DcRkEZKU7LQ]:
- MobileNet v2 (ImageNet) como base: congelar capas preentrenadas, reemplazar última capa por Dense(N, softmax); redimensionar imágenes a 224×224; split 80/20; exportar a TensorFlow Serving para versionar y escalar, o Flask/FastAPI para one-offs. → aplica: clasificador de categorías tu-nicho en 3 semanas con <500 imágenes por clase.
- Exportar `.h5` → `tensorflowjs_converter` genera `.json` + `.bin`; cargar en JS con `tf.loadLayersModel()` + `async/await`; normalizar con `tf.scalar`; predicción con `model.predict(tensor)`; `ngrok http 8000` para acceso desde móvil sin configuración. → aplica: demo visual de clasificación de productos en el storefront tu-tienda.
- Vectorización NumPy vs. bucle for: 30× más rápido en 20 M elementos; CUDA/cuDNN reduce entrenamiento de semanas a horas; PyTorch+CUDA ideal para modelos de recomendación; Cython/Numba para cálculos críticos sin reescribir todo. → aplica: acelerar batch scoring de productos en GPU local (Qwen/tu servidor LLM local) o GPU cloud.

**LLMs, agentes y arquitecturas de memoria** [IHpLbziFGEQ] [b6G3tN9ESbE] [iTDGQg-g438] [MjK-j7YJ5YI] [7NlYAZzMLeI]:
- LLM (Transformer + autoatención) → SLM (dispositivo/bajo recurso) → LRMS (Chain of Thought, más caro); embeddings en espacio vectorial + bases vectoriales (PineconeDB, Milvus) + RAG = respuestas actualizadas sin reentrenar. → aplica: chatbot de soporte tu-tienda que consulta políticas, FAQs y catálogo vía RAG.
- Pipeline RLHF: preentrenamiento (175 B parámetros, 95 % del costo) → SFT con 13 k pares etiquetados → modelo de recompensas entrenado por humanos → algoritmo Policy Gradient; temperatura 0 = respuesta determinista. → aplica: ajustar modelos de soporte con respuestas reales de clientes tu-tienda para reducir alucinaciones.
- Memoria corta: buffer de 10 mensajes; los 6 más antiguos se resumen con modelo secundario (GROQ); guardado de largo plazo en Supabase/PostgreSQL con función `guardar_memoria()` activada por menciones de preferencias. → aplica: agente de soporte tu-tienda que recuerda historial del cliente entre sesiones.
- Tokens visuales + Deep Encoder (SAM + CLIP + mezcla de expertos, 570 M parámetros activos): compresión 10× con 97 % de precisión; a 20× cae a 60 %; permite manejar 200 k páginas/día con GPU NVIDIA A100; OCR como entrada alternativa a LLMs. → aplica: resumir correos, PDFs de proveedor o fichas de producto sin tokenizer.
- GPT-3.5 cuesta ~$0.002/prompt; GPT-4o razonamiento ~$0.03–$0.10/prompt; LangChain/CrewAI reducen 70 % el código repetitivo; funciones personalizadas (`list_files`, `read_file`) con parámetros claros para tool_call. → aplica: chatbot de soporte en GPT-3.5 + función de consulta de inventario, reservando GPT-4o para decisiones complejas.

**Automatización IA: asistentes de voz, agentes y flujos n8n/N10** [−0tIy8wWtzE] [lnXGlR2TAqc] [wd4voMPEOGg] [PU30VIg0QI4]:
- Stack asistente de voz: Whisper (90 % precisión en entorno controlado) + GPT-3.5-turbo con `function_call=auto` + ElevenLabs TTS (voz Bella reemplazable); Flask como backend; `subprocess` para abrir programas externos. → aplica: asistente "cozy home helper" que añade productos al carrito por voz ("añade lámpara de sal").
- N10 + Ollama en Docker (2 contenedores, volumen `/home/node`): modelos desde Qwen 8B hasta 235B parámetros, cuantizados 4-bit; historial de 10 mensajes; herramientas HTTP para API YouTube (CPM estimado $25 × promedio vistas → presupuesto de patrocinio). → aplica: agente local para analizar canales competidores de tu-nicho y estimar CPM antes de hacer outreach.
- Hostinger KVM2 (2 vCPUs, 8 GB RAM, hasta 10× más barato que Heroku) + Docploy: despliegue con SSL automático, variables de entorno, logs en tiempo real; Gmail trigger → extracción → GPT-5 → etiquetado automático ("Queja", "Pregunta de producto"). → aplica: automatizar clasificación de correos de clientes tu-tienda con costo de infraestructura mínimo.
- Agentes RAG con memoria de largo plazo + base vectorial: personajes simulados (experimento Stanford) lograron 100 % credibilidad vs. humanos; arquitectura de reflexiones recursivas agrupa memorias en "insights" futuros; límite tokens gestionado con BD externa. → aplica: agente de onboarding tu-tienda que recuerda preferencias del cliente y anticipa recomendaciones.

**Algoritmos de optimización y ML no supervisado** [5vwBQ_KoD60] [SGPNhwQYb4M] [ghEDBimjjkc]:
- Algoritmos genéticos: crea N "cerebros" aleatorios, selecciona mejores por KPI (distancia, eficiencia), mezcla genes con mutación; redes neuronales simples + evolución reduce complejidad sin sacrificar resultados. → aplica: optimizar reglas de pricing dinámico para margen ≥25 % neto en tu-tienda (costo CJ + envío + PayPal 5.4 %+$0.30).
- Segmentación de objetos sin librerías: clustering por cercanía (distancia euclidiana <50 px = mismo objeto); bounding box dinámico (x_min/x_max/y_min/y_max); reducción 40 % en tiempo de procesamiento con validación de si el píxel está dentro del rectángulo. → aplica: detección automática de producto en fotos UGC para recorte y fondo limpio.

**Infraestructura, contenedores y seguridad** [9eTVZwMZJsA] [70AduhLh65w] [KEVyWk3e6xI] [ZOim08yd0uc] [xikzrZ0Pz7M]:
- Docker: 2 contenedores Ubuntu+Debian ocupan <50 MB vs. ~300 MB por VM; `node:16-alpine` estándar; Compose para app+DB; ~10 MB RAM por contenedor → 100+ contenedores sin saturar; Kubernetes/Docker Swarm para orquestación; GPU cloud (RTX 5090, H200) rentable por hora en Romot. → aplica: desplegar backend tu-tienda (app + Redis + PostgreSQL) en Hostinger KVM2 con Compose.
- Amazon S3 "denial of wallet": 1 000 solicitudes PUT/GET cuestan $0.02; bucket mal nombrado puede generar $1 300 en minutos; Amazon Shield Advanced cuesta $3 000/mes y no protege 403/404; solución: nombres aleatorios con sufijo fijo (`prod-bucket-abc123`); alertas (no bloqueos) son la única opción nativa. → aplica: nunca usar nombres simples en buckets de assets tu-tienda; configurar alerta de billing a $50.
- Docker ignora UFW/iptables; puerto 27017 (MongoDB) vulnerable por defecto; crear red bridge personalizada (`docker network create mynet`) y desconectar de bridge público; LLMs (Qwen, Gemini) pueden generar scripts de ataque en segundos → escanear puertos con NMAP periódicamente. → aplica: aislar DB de pedidos/inventario tu-tienda en red Docker interna sin exposición externa.
- Phishing: 95 % de ataques apuntan a humanos no a servidores; clonado de sitio + 2FA interceptado en 60 segundos (caso Reddit); FIDO2/llaves físicas son la opción más segura; bcrypt+sal+pimienta para contraseñas; Meta guardó contraseñas en texto plano 2012–2019 → multa 91 M€ GDPR. → aplica: activar FIDO2 en cuentas críticas (Shopify admin, PayPal, CJ); nunca loguear tokens de sesión.
- DDoS: 11.5 Tbps pico 2022 (vs. 3.8 Tbps año anterior, +200 %); botnet Mirai infecta routers/cámaras IoT con credenciales por defecto; Cloudflare soporta 11.5 Tbps; WAF + CDN + rate-limiting + monitoreo en tiempo real son la defensa base. → aplica: poner storefront tu-tienda detrás de Cloudflare Free + WAF; configurar rate-limit en /checkout.

**Producción de contenido con IA y herramientas creativas** [Xkv1rliZxX4] [rM0IDeyD0EA] [YqSSId7xfwU] [aQf9kzb_3ng]:
- Filmora + BO3/nano banana: texto → video en minutos; 1 minuto de contenido = 5–7 shorts con subtítulos y zooms automáticos (80 % precisión); créditos gratuitos reducen costos de edición 70 %; ahorro estimado 15+ horas/mes. → aplica: generar anuncios UGC de productos tu-nicho tu-tienda con prompts tipo "lámpara cozy, ambiente tech, chispa en cabeza".
- Deep fake facial con Colab (Google Drive + GPU gratuita): resolución ideal 320×320 px, imagen con fondo simple y expresión neutra; tiempo de ejecución ~1 min si ya entrenado; resultado indistinguible. → aplica: crear demos de producto con "portavoz" virtual para anuncios US-first sin contratar actores.
- OCR manuscrito: TRCR (Hugging Face) + OpenCV para separar líneas + CUDA para inferencia; TTS con Open Voice (checkpoints `v2_1_es`) o XTTS-V2/Melo-TTS para calidad premium; despliegue con Docker + APIs REST modulares. → aplica: procesar notas internas escritas a mano o formularios de pedido no digitales.
- ChatGPT alcanzó 100 M usuarios en 2 meses (récord histórico); modelos de lenguaje son "aproximadores de funciones" sin conciencia; riesgo de sesgo: IBM AI Fairness 360 + SHAP/LIME para explicabilidad; Bing limitó uso a 5 sesiones diarias para evitar abuso. → aplica: usar IA como herramienta de apoyo en soporte/contenido tu-tienda, no como decisor autónomo; auditar sesgos en recomendaciones de producto cada trimestre.

### 12c · Alan Daitch — FULL-PASS 2026-06-21
*(canal destilado; IA aplicada / negocios con IA; ref: `_archivos_trabajo/_destilados/alan_daitch_p1..p3_LOCAL.md`)*

**Automatización de flujos con N8N + LLMs** [6LMIFlZ27yg] [XO3JIhcXAUw] [bDFY4C2eXBg]:
- N8N como motor de automatización backend: clasifica correos con Gemini 2.5 Flash (prompt: *"Clasifica como spam/no. Solo responde: spam / no"*), elimina spam vía switch node + filtro condicional, crea eventos en Google Calendar API con variable dinámica `now`. → aplica: automatizar bandeja de tu-tienda (pedidos, consultas, devoluciones) sin tocar manualmente.
- N8N local instalable sin costo; usa templates de comunidad + Webhooks para integrar APIs de proveedores CJ, sincronizar inventarios en tiempo real. → aplica: flujo de stock automático entre CJ y Shopify.
- N8N + GPT4O/Gemini + Serp API + imgBB + Facebook Graph: genera posts en español, sube imagen, publica en LinkedIn/Instagram/Twitter en 30s–2min por post; requiere API keys separadas (OpenAI, Google Cloud, Serp, imgBB). → aplica: automatizar contenido orgánico tu-nicho + bienestar diariamente.

**Selección y uso de modelos por tarea** [NNKalnsj_wQ] [PXKCUs2TJJg] [dRSscbmMUMw] [IgFq0aA5iWA]:
- GPT-5 modo *thinking*: recomendaciones, análisis comparativos, estrategias complejas; +40% precisión vs fast según tests. Modo *fast*: consultas técnicas simples. GPT-4O: correos y publicaciones con tono empático. → aplica: usar *thinking* para comparativas de productos tu-nicho, *4O* para emails post-compra.
- Grock resistente a sesgos de memoria en acertijos lógicos; O3 mini high: mayor razonamiento no lineal; 70% de modelos caen en trampas con entradas estándar. → aplica: usar Grock/O3 para análisis de comportamiento de clientes, no confiar en GPT-3.5 para decisiones críticas.
- Shemini: búsqueda profunda hasta 100 fuentes (vs ChatGPT 20–30), genera imágenes editables, modo canvas sin código; Perplexity: tablas comparativas + fuentes verificables en tiempo real, ideal SEO. → aplica: investigar tendencias tu-nicho con Shemini; comparar precios de termostatos/luces LED con Perplexity.

**Prompt engineering y GPTs personalizados** [7ZZ51-IjTAM] [OK1Hs6nrKKk] [XSs8w89Hodg] [7myErpmx6wQ]:
- Estructura de prompt de alto rendimiento: *Contexto + Rol + Acción específica + Formato + Tono + Límite numérico*. Ejemplo: "Redacta plan de marketing para tienda tu-nicho US-first. Actúa como experto en dropshipping. Markdown. Tono profesional. 5 estrategias." → aplica: plantilla fija para todo contenido de tu-tienda.
- Prompts de meta-nivel: (1) *"Haceme preguntas hasta estar al 95% de confianza"* — reduce errores por suposiciones; (2) *"Actúa como experto del 1% que critica mi guion"* — mejora profundidad; (3) *"Actúa como rebelde que reformule mi enunciado"* — ideas disruptivas. → aplica: usar (1) para briefs de producto, (2) para revisar copy de PDP.
- GPT personalizado con archivos de hooks cargados: genera 5 hooks + 5 cierres + 2 enfoques por guion; activa búsqueda por contenido ("microondas" → busca `microondas.txt`); desactivar compartir con OpenAI por privacidad. → aplica: GPT tu-tienda-guionista con base de hooks de tu-nicho + bienestar.
- Proyectos ChatGPT: instrucciones predefinidas por proyecto (guiones, curación, marketing), archivos como DB de hooks, carpetas por categoría — evita repetir contexto en cada chat. → aplica: proyecto "tu-tienda-Marketing" con instrucciones de nicho cozy/US-first.

**Generación de video con IA (Google Flow / BO3 / Runway)** [1wPwaDtvyyA] [QgTUmByGykg] [s6c4n_lqGQs] [k0r4vqjXwyU] [VpNqjc2QuVg]:
- BO3 Fast: 20 créditos/8s (vs Quality 100 créditos); estrategia óptima: 3 generaciones fast + 1 petición final. Upscale gratis al terminar. Prompts en inglés aunque el video sea en español. → aplica: generar 50 videos/mes con prueba gratuita Shemini.google/subscriptions (cancelar antes del 2° mes).
- Google Flow beta: concatena escenas, genera hasta 50 videos con créditos adicionales; Beo 3.1 Fast: 4x menos créditos que Quality; combina fotograma inicial + final sin texto explicativo. → aplica: intros de productos tu-nicho (caja → producto en uso) con narración en español.
- Pipeline de video completo: Nano Banana (imagen 3D) → Clink AI (transición entre frames, velocidad 1.5x) → Runway ML (imitar estilo + audio, alto costo créditos) → BO3 (escena cinematográfica 8s). → aplica: contenido de producto premium para redes con calidad cinematográfica.
- Google Gemini Pro + Flow: 1000 créditos/mes = 50 videos (20 créditos/video); lip sync automático; contenido en formato horizontal para YouTube. → aplica: canal YouTube de tu-tienda con estilo cozy/bienestar consistente.

**Agentes de IA y automatización de tareas autónomas** [V8Wb3aijSdc] [SAHdRuD4A-M] [HL1B_VGehvI] [hJG0aVBFj2s]:
- Distinción clave: LLM (genera texto sin contexto dinámico) < Workflow (pasos predefinidos, reactivo) < Agente (planifica, decide herramientas, itera sin intervención). Framework React: Reasoning → Action → Think — evalúa resultados y corrige en bucle. → aplica: agente que resume ventas + detecta productos sin stock + notifica vía WhatsApp.
- ChatGPT Agent Mode: pedido con criterios implícitos → selección automática → gestión de carrito; cronograma para tareas recurrentes (ej: revisar precios competidores 8 AM); límite 40 consultas/mes en plan $20. → aplica: automatizar comparación semanal de precios en nicho tu-nicho.
- ChatGPT en navegador (extensión): modo agente abre/cierra tabs, extrae precios, completa Google Sheets en tiempo real; reescribe texto seleccionado; 5x más lento que humano pero sin errores graves. → aplica: generar listas de precios comparativas de proveedores CJ vs competidores.

**Generación y edición de imágenes de producto** [4YA-1mpb2H4] [FvpTWTj4S6Q] [dqOXTZVSaiY] [PV339dsmTiQ]:
- Benchmarking de modelos de imagen: 3 iteraciones por modelo (ChatGPT, Gemini Flash, Grock); estructura prompt: *Objeto + Detalles técnicos + Contexto visual*; precisión esperada: 80% en técnicos, 75% en textos dinámicos. Gemini Flash para iteraciones rápidas + Google AI Studio para ajuste final. → aplica: imágenes de producto tu-nicho con contexto de sala cozy en 3 iteraciones.
- Framework por etapas: (1) imagen base → (2) ajustar elementos específicos → (3) estilo/posición → (4) validar. Nano Banana 2: grounding con imágenes reales de internet, elimina marcas de agua con "aumentar calidad". → aplica: fotos de productos en escenas reales (salón, dormitorio) sin shoot físico.
- Prompt engineering de imagen: cambio de ángulo ("camina 50m atrás"), modificación de horario (día→noche, neones), extracción de personajes, 9 poses del mismo objeto con consistencia, edición de texto en imagen ("tío Pepe" → "tío Alan"). → aplica: variantes de foto de producto para A/B testing en Shopify.

**Estrategia de contenido viral y redes sociales** [39kPRsj-WHI] [Jb4Bp-y1DL8] [gfp5jvaAHg4]:
- Herramientas de escalado viral: Opus Clip (clona voz + foto + subtítulos para TikTok en 5 min); Heen (3 videos 20s/mes gratis); publicar en 500–1000 cuentas → si funciona escalar a 5k→20k. Métricas reales: 1.5M visualizaciones con 800 seguidores, 10M impresiones/30 días, 35k nuevos seguidores. → aplica: testar hooks de tu-nicho con Heen antes de escalar.
- Email marketing segmentado: carrito abandonado → descuento 15% → +25% conversiones. A/B testing banners/precios/CTAs → +30% CTR. Táctica "Free Trial" (humidificador de prueba + envío gratis) → 18% conversión. KPIs: ROI >4x, carga <2s, rebote <45%. → aplica: flujo Klaviyo post-carrito abandonado para tu-tienda.
- Contenido híbrido: tu-nicho + bienestar = margen 40–50% (humidificador inteligente + aromaterapia). Keywords SEO: "tu-nicho products near me", "cozy home decor", "wellness gadgets for home". Pricing dinámico: subir precios calefacción en invierno. → aplica: colección "Winter Cozy" con precio dinámico diciembre–febrero.

**Privacidad, sesgos y uso responsable de IA** [Sk5k-Md8KI4] [Xl264Dc1GfQ] [ZoXTVMJE2t8]:
- Configuración de privacidad ChatGPT: desactivar "mejorar el modelo para todos"; chat temporal elimina historial en 30 días; Privacy Portal OpenAI para borrado completo (hasta 30 días de proceso); anonimizar datos antes de enviar (usar IDs en lugar de nombres reales). → aplica: nunca subir catálogo de clientes o datos de pedidos reales a ChatGPT.
- Sesgos críticos a vigilar: confirmación (da respuestas convincentes según cómo preguntas), presuposición (inventa si le pides algo inexistente — ej: 16 patrimonios cuando son 12), anclaje (primer dato influye toda la conversación), exclusión temporal (no conoce eventos post-entrenamiento). → aplica: siempre verificar con fuente externa antes de usar datos de IA en decisiones de catálogo o pricing.

**Herramientas freemium y stack de producción gratuito** [BsXtX_xalAM] [SmXAk-uT25A] [cU4pG4O4xKg]:
- Stack gratuito validado: Claude.ai (guiones largos, español natural, ~30 min/día) · Nano Banana (edición de imagen, precisión media) · Gama.app (presentaciones con branding, créditos gratis) · HeyGen (avatar 3 videos/mes, 720p con watermark) · Google Flow Beo3 (5 intentos/mes, 8s) · Suno.ai (jingles en segundos, reggaetón/cumbia/cualquier género) · Notebook LM (resúmenes + podcast de documentos). → aplica: producir contenido de tu-tienda con $0 combinando estas herramientas por turno.
- Google AI Studio: prototipos de apps web sin código en minutos, Gemini Pro vs Flash según calidad/velocidad, exportar a GitHub → Vercel (servidores Google Cloud $20–$200/mes; preferir GitHub gratuito para MVPs). → aplica: crear app de comparador de productos tu-nicho como MVP en <1 hora.
- Gemini integrado en Google Workspace: Flash para tareas rápidas (reformular títulos, listas), Pro para análisis estructurado (+60% ahorro de tiempo en resúmenes); Canvas genera quizzes/dashboards; Nano Banana genera miniaturas personalizadas desde Docs; automatizar seguimiento de publicaciones en Sheets con columnas fecha/tema/estado/enlace. → aplica: dashboard de contenido tu-tienda en Google Sheets gestionado por Gemini.

### 12d · Claude / Anthropic (oficial) — FULL-PASS 2026-06-21
*(canal destilado; features Claude + Claude Code + prácticas; ref: `_archivos_trabajo/_destilados/claude_oficial_p1..p3_LOCAL.md`)*


**CLAUDE.md / Memoria persistente** [O0FGCxkHM-U] [bjdBVZa66oU]:
- `CLAUDE.md` (o `claw.md`) es la única fuente de verdad que persiste entre sesiones; sin él Claude re-explora en cada turno y pierde eficiencia. Define comandos (`dev`, `test`, `lint`, `format`), preferencias de estilo (indentación 2 esp., exports nombrados, Tailwind), server-actions vs API-routes, y usa `@` para referenciar docs internos. Mantenerlo conciso: solo lo necesario, cero redundancias. `/init` genera un draft basado en el stack detectado. → aplica: tu-tienda ya tiene CLAUDE.md; añadir referencias `@DOCUMENTACION/PROCESO_MARGENES.md`, `@GUIAS/MANO_DERECHA_LOCAL.md` y los scripts clave del índice para que Claude no los redescubra.
- `skills.md` en `.claude/skills/`: codifica estándares de commit, políticas de diseño y formatos de documentación. Se cargan en tiempo real cuando el contexto coincide; no saturan el contexto. → aplica: crear `tu-tienda-commit-format.md` y `tu-tienda-review-pr.md` en `.claude/skills/` para evitar explicar el formato de commit en cada sesión.

**Hooks deterministas** [IkaPHiMDazM]:
- Hooks en `.claude/settings.json` son versionables y proyecto-nivel (consistencia de equipo). Tipos: `post-tool-use` (auto-formatting tras edits — llama Prettier/Black/GoFmt con `$CLAUDE_PROJECT_DIR`), `pre-tool-use` (bloquea operaciones peligrosas: si exit code = 2 → bloqueo + mensaje a Claude; evita `rm -rf`, commits a main). Matchers concretos: `"edit"`, `"multi-edit"`, `"tool-call"`, `"notification"`, `"stop"`. Regla clave: no confíes en prompts para acciones críticas — usa hooks. → aplica: hook `post-tool-use` con matcher `edit` para auto-formatear Python en `scripts/`; hook `pre-tool-use` que bloquee cualquier llamada que contenga `productCreate`/`productSet` (guardarrail #1 de tu-tienda).

**Modos de permisos y bucle agente** [6bs5b4FltCU] [fl1DSmwQKKY]:
- Tres modos: *Default* (pide permiso para edits y comandos), *Auto-accept edits* (edita sin confirmar, pide permiso para comandos), *Plan mode* (solo lectura — explora sin actuar, ideal para mapear antes de ejecutar). Claude Code = LLM + tools + acciones; su context window es la memoria operativa. Si se excede, compacta automáticamente resumiendo. Semantic search decide cuándo invocar tools, no palabras clave. → aplica: usar Plan mode al inicio de tareas de catálogo complejas (vet_catalog_wave, phase2_publish) para revisar el plan antes de que Claude toque archivos.

**Gestión de contexto** [eW3oTyfeWZ0] [kkBFmwkDzdo]:
- `/compact` resume sesiones largas y libera contexto; `/clear` reinicia para proyectos nuevos; `/context` muestra qué ocupa más espacio. Desactiva MCP servers no relevantes (cada servidor MCP añade sus esquemas al contexto en cada turno — impuesto de tokens). Regla MCP: si >10% de la ventana de contexto se usa para definiciones MCP, Claude entra en modo búsqueda-de-herramientas (menos eficiente). Priorizar CLI sobre MCP cuando exista script equivalente. → aplica: confirma CLI-first ya implementado (183 scripts); usar `/compact` tras sesiones largas de curación de catálogo; revisar con `/mcp` qué servidores están activos y desactivar los no usados por sesión.

**Routines / automatización proactiva** [eSP7PLTXNy8] [KLCuxMDZSDg]:
- `routines` en Claude Code: agentes que se lanzan sin intervención humana mediante triggers `cron` (tiempo) o eventos (GitHub issues, PRs, DataDog alerts). Proveen contexto dinámico (GitHub, Slack, Twilio) y permiten `steerability` en tiempo real (interrumpir/guiar). Impacto documentado: +200% en PRs generadas por Claude Code. `/schedule` programa ejecuciones autónomas con triggers cronométricos. Validación post-ejecución siempre antes de mergear. → aplica: routine semanal que revisa stock de productos activos en CJ API y alerta por Slack si hay desabastecimiento; routine post-deploy que corre `screenshot.py` y reporta QA visual.

**Remote Control / multidispositivo** [Ko7_tC1fMMM]:
- `claude remote control`: lanza sesión local, genera URL/QR vinculando móvil al entorno de desarrollo. Ediciones desde móvil se reflejan en el terminal principal y viceversa. Modo Spawn: crear nuevas sesiones remotas desde móvil. Acceso completo a MCP servers, configuraciones y sistema de archivos sin mover infraestructura. Disponible en planes Pro, Max, Team y Enterprise. → aplica: útil para supervisar el daemon Mano Derecha o el dashboard Mission Control (:<PUERTO_TIENDA>) desde móvil sin exponer credenciales.

**Optimización de modelos y costos** [P0uMXS6emHA] [OXJO4LldSnc] [mWvtOHlZM-I]:
- Eval personalizado con dataset de inputs reales: 92% Haiku vs 100% Sonnet/Opus — elegir por resultado exitoso por tarea, no por token. Prompt caching con estrategia "append-only" alcanza 80–90% hit rate (costo Opus baja a 1/10 del listado). Context hygiene: limpiar JSON, usar markdown, simplificar fechas → −65% costo +9% precisión. Adaptive thinking: Sonnet/Opus usan "scratchpad" interno para decidir cuánto pensar. Effort levels ajustables: `low/medium/high/max`; thinking tokens para razonamiento paso a paso; tool-calling tokens para APIs en tiempo real. Diminishing returns en tareas complejas con max effort: medir con evals antes de subir nivel. Refactorizar prompts largos (400 líneas → 15 líneas + skills + 3 tools bash/read/write): eval score pasó 83%→92%. → aplica: usar prompt caching en llamadas recurrentes a Shopify API y CJ API; medir con eval corto antes de escalar a Opus para tareas de curación.

**Workflow Explore → Plan → Code → Commit** [xJQuF02NAK8] [igO8iyca2_g]:
- Secuencia canónica: Explore (leer sin editar en plan mode) → Plan (definir criterios explícitos de "correcto") → Code (implementar) → Commit (sub-agente revisor + mensaje de commit personalizado). Plan mode lee archivos sin editar, facilita investigación. Corregir el plan antes de generar código elimina rework. Guardar soluciones en `.md` para reutilización. Cuellos de botella ya no son codificación sino revisión, seguridad y alineación cross-funcional: shift-left con detección de bugs temprana. "Claudify everything": automatiza tareas repetitivas y comandos, guarda en scripts, usa PRs como fuente de verdad interna. → aplica: aplicar este workflow en cada tarea de theme (`theme_claude_v1`) — Explore en plan mode, Plan con criterios de QA visual, Code, Commit vía `git_snapshot.py`.

### 12e · Gustavo Entrala — FULL-PASS 2026-06-21
*(canal destilado; IA / innovación / productividad; ref: `_archivos_trabajo/_destilados/gustavo_entrala_p1..p4_LOCAL.md`)*

**Agentes IA y automatización operativa** [eYgQWhYjf5Q] [r0Iz-okwOsA] [SzVm56YK9I8]:
- Agente Make + GPT-4 Turbo cuesta ~$1.5 / 10 días de prueba; filtra 100+ CVs en minutos con 95% precisión. → aplica: agente de atención al cliente tu-tienda que responde envíos/precios con datos actualizados de CJ en tiempo real.
- 40-60% de tareas operativas de e-commerce son automatizables; un agente gestiona 150+ tareas/día, reduce tiempo humano 30-40%. → aplica: agente Shopify que monitorea stock CJ, ajusta precios y genera respuestas en <5 segundos.
- Make AI Agents: 3.000+ apps integradas, lógica visual sin caja negra; Salesforce cobra por gestión (modelo escalable). → aplica: orquestar flujo CJ→Shopify→Judge.me sin código adicional.
- Marco de adopción en 3 niveles: copiloto → facilitador → agente especializado 24/7. → aplica: empezar con copiloto de descripciones de producto, escalar a agente de precios autónomo.
- Google: 25% del código escrito con IA → ingresos por empleado de $1.5M a $2M (+33%). BBVA ahorró 2h/semana por profesional. → aplica: justificación interna para invertir en automatización antes que en headcount.

**Prompting y uso táctico de modelos** [fZ7ZeH65PFA] [TWgg2vxYUHw] [W6CzDJvBmXk] [UqKhMMqCo_E]:
- Asignar rol + contexto detallado + formato específico mejora calidad de output; mercado de prompts (Promptbase) a 2-10€/unidad. → aplica: prompt "experto en tu-nicho US" con contexto de nicho cozy/bienestar para descripciones SEO en 6 locales.
- "Por favor" añade 13-20 tokens por consulta; 900M consultas/día con 60% cortesía = ~$250K USD/día de sobrecosto. Estudio Molic: mejora precisión 25%, pero priorizar claridad > cortesía. → aplica: optimizar prompts batch del daemon Mano Derecha eliminando cortesía innecesaria.
- Alucinaciones: 6.4% en documentos legales, 4.3% médico, 3.7% científico. Ventana de contexto gigante reduce alucinación a 0.7%. → aplica: verificar con Perplexity/Grok cualquier dato de proveedor, precio o regulación antes de publicar.
- Kit usuario escéptico: pedir citas literales, pedir "no lo sé", usar búsqueda en tiempo real para datos dinámicos (ventas, tendencias). → aplica: validar con Perplexity tendencias de búsqueda tu-nicho antes de apostar por un producto.
- Notebook LM convierte documentos en cuadernos interactivos; Napkin AI genera visualizaciones desde párrafos; Gemini Deep Research procesa judiciales + artículos + videos. → aplica: analizar transcripts de canales competidores para extraer insights de nicho.

**Modelos de IA y coste de entrenamiento** [66le3H7yI1Q] [MbmmiWrrhfM] [H-zooAmWuK0]:
- DeepSeek R1 entrenado con $5.3M en 2 meses (vs. >$1.000M OpenAI); 3% del coste de O1; empata en 6 de 9 benchmarks Strawberry; app más descargada del mundo en enero 2025. → aplica: usar DeepSeek R1 (gratuito) para tareas de razonamiento y análisis donde no se requiera privacidad de datos tu-tienda.
- Técnicas clave: destilación de modelos (transferir conocimiento de GPT-4 al aprendiz), RLHF, optimización de inferencia por compresión. → aplica: entender qué capacidades de razonamiento paso a paso [MbmmiWrrhfM] aplicar al clasificador de productos on-niche.
- NVIDIA perdió $600B en bolsa en enero 2025 por el anuncio de DeepSeek. Chips H800 a $7K/unidad. Acceso via APIs de Anthropic/OpenAI: OpenAI cobra ~10% del coste de desarrollo. → aplica: APIs token-based son la vía óptima para tu-tienda sin inversión en infraestructura; comparar DeepSeek vs Claude por coste/tarea.
- Chain-of-Thought Prompting mejora precisión en tareas complejas hasta 40%; datos sintéticos reducen costes de entrenamiento 60%. → aplica: usar razonamiento paso a paso en el clasificador de márgenes (precio − CJ − envío − PayPal).
- Suscripción O1 Pro: €2.000-€3.000/mes para acceso premium. Modelos gratuitos (DeepSeek R1, Llama) como alternativa para escalar sin inversión masiva. → aplica: mantener Claude como motor principal + DeepSeek para batch barato en Mano Derecha local.

**Personalización emocional de IA y UX** [IXqnL35Rea0] [nyunLBoAf8M]:
- 93.1% de profesionales de marketing usa IA; 49.2% en asistentes virtuales/chatbots. Hashtag #BringbackGPT4 fue trending 48h: usuarios valoran más colaboración y empatía que pura inteligencia. → aplica: el asistente de tu-tienda debe tener tono cálido/cozy alineado con el nicho bienestar, no frío/corporativo.
- IA del futuro = ecosistema de personalidades (modos sereno/motivador/productivo que el usuario elige). 47.5% usa IA para análisis, pero 49.2% para interacción humana. → aplica: configurar tono del chatbot de tienda según momento del buyer journey (descubrimiento=inspirador, checkout=confianza, postventa=cálido).
- Uso intensivo de IA reduce conectividad cerebral 60% (ondas Z/alfa); 83% de usuarios olvida contenido que la IA escribió por ellos. Framework "Piensa primero, usa después". → aplica: usar IA para edición y optimización de copy, no como motor inicial; mantener criterio editorial humano en textos de marca tu-tienda.
- Incogni elimina datos personales de 123+ plataformas ahorrando 90h de trabajo manual. → aplica: proteger datos del operador de tu-tienda en brokers de datos.

**Integración de IA en e-commerce Shopify** [H-zooAmWuK0] [8Szm56z58EM] [pgldO_y7hzc]:
- APIs de Anthropic/OpenAI para prototipos sin inversir $500M; Shopify permite búsqueda de productos via IA entre tiendas; Morgan Stanley integra GPT en soporte al cliente. → aplica: asistente IA en PDP que responde "¿Este proyector sirve para habitación de 15m²?" con datos reales del producto.
- Make (framework orquestación visual): 2.500 apps preconstruidas, 10K operaciones gratis de entrada. → aplica: conectar CJ Dropshipping API → Shopify → Judge.me → email Klaviyo en un flujo sin código.
- AI Governance: "Two-Person Rule" para decisiones críticas (pagos, infraestructura); "Canary Releases" para implementaciones graduales; "Access Control Minimal" (permisos que expiran). → aplica: cualquier automatización que toque precios o publicación de productos requiere revisión humana antes de escalar; replicar guardarraíles de CLAUDE.md en agentes externos.
- Monitoreo de competencia en tiempo real con agentes: siguen blogs/noticias de marcas (Apple, Xiaomi, Samsung) y generan recomendaciones diarias. → aplica: agente que monitorea precios de proyectores y luces ambientales en Amazon US para ajustar pricing tu-tienda.

**Privacidad, cookies y publicidad first-party** [YSJJ_hDB8Zo] [wVqd_NA5vSg] [9E_cy60xozo]:
- Apple ATT: consentimiento explícito para tracking cross-app; Facebook lo califica de riesgo "nuclear" para sus ingresos. Google elimina cookies; reemplaza con segmentación por grupos de interés (no datos individuales). → aplica: tu-tienda no puede depender de retargeting de terceros; construir lista email propia desde día 1.
- Marcos regulatorios: GDPR, CCPA, ePrivacy obligan a informar uso de datos. Publishers pierden capacidad de medir ROI cross-device. → aplica: migrar a first-party data (email, CRM Klaviyo) + publicidad contextual en Meta/Pinterest segmentada por intereses tu-nicho/cozy.
- Facebook/Meta ARPU Europa: ~€41/usuario anual (2020); si usuario se mantiene 5 años = €240, 10 años = €400. LTV multiplica 6x en empresas como Google o Apple. → aplica: calcular LTV de cliente tu-tienda; un cliente recurrente de bienestar vale €240+ en 5 años; justifica invertir en retención vía email y reseñas.

**Gobernanza y riesgos de IA** [pgldO_y7hzc] [UqKhMMqCo_E] [IbZLGOMRNs0]:
- Criptografía actual (RSA, ECC) vulnerable ante computación cuántica en 2029 según Google; NIST prevé migración completa para 2035. Algoritmo Shor puede descifrar claves Bitcoin en ~9 minutos con hardware suficiente. → aplica: revisar si proveedores de pago (PayPal) tienen roadmap post-cuántico; no almacenar datos sensibles en texto plano.
- 90% de empresas no tiene plan para computación cuántica. Protocolo BB84 (QKD) ya funciona en fibra óptica >150km. → aplica: horizonte 2029 es corto; depender de proveedores (Shopify, PayPal) que tengan equipos de seguridad activos.
- "Harvest Now, Decrypt Later": actores maliciosos guardan datos cifrados hoy para descifrarlos cuando la computación cuántica madure. → aplica: no transmitir datos de clientes sin cifrado robusto aunque parezcan poco sensibles ahora.

**Modelos de negocio y estrategia de plataforma** [aWF6NLPwacA] [pGnbawFxlNI] [mgOjeKT1HSs]:
- Círculo virtuoso Amazon (Gene Collings): selección amplia → precios bajos → experiencia → tráfico → más proveedores → precios más bajos. Prime como "moat" con costo upfront (€30+) que fideliza. → aplica: tu-tienda no puede replicar Prime, pero sí construir moat con curaduría experta tu-nicho + reseñas verificadas + respuesta rápida.
- Amazon Principio 1: "Obsesión por el cliente" incluso si pierde dinero a corto plazo (AWS). Principio de "2 pizzas": equipos pequeños = agilidad. "Nota de prensa como herramienta de validación" antes de desarrollar. → aplica: antes de añadir categoría nueva (ej. masajes eléctricos), escribir la "nota de prensa" del producto ideal para validar si tiene mercado.
- Perplexity: de $520M a $14.000M en 3 años; 22M usuarios mensuales; 780M preguntas/mes (+20% mensual). Metodología: lanzar → medir → descartar si no se usa → repetir. No planifica más de 3 meses. → aplica: iterar catálogo tu-tienda en ciclos cortos (4-6 semanas); si un producto no convierte en 30 días, reemplazar sin piedad.

### 12f · RoboNuggets — FULL-PASS 2026-06-21
*(canal destilado; herramientas IA / automatización / agentes / no-code; ref: `_archivos_trabajo/_destilados/robonuggets_p1..p5_LOCAL.md`)*

**Agentes multi-paso y orquestación (Claude Code)** [2rhZOisVXZM] [mWUs98XrjIQ]:
- Ultra Code lanza dinámics workflows donde Claude actúa como orchestrator delegando a sub-agentes paralelos (ej.: 9 agentes para auditar 3 sitios en paralelo; 96 agentes para bug-hunt); consumo: 4–6% cuota semanal por análisis complejo. → aplica: auditar SEO técnico + keyword gap de tu-tienda vs. competidores en minutos con un solo prompt.
- Framework "3C": Modelo (Opus/Haiku/Sonnet) + Arnés (Claude Code/Anti-gravity) + Contexto (workspace+datos); priorizar configuración del contexto para no reconfigurar al cambiar de modelo. → aplica: centralizar contexto de tu-tienda (catálogo, márgenes, reglas) para reutilizarlo en cualquier arnés.
- Claude Code aumentó 50% límites semanales (hasta 13/07) + 100% en sesión de 5h; Codex tiene 86M instalaciones vs. 7M de Claude Code — migrar entre arneses es sencillo por usar texto/código como base. → aplica: aprovechar el pico de cuota para automatizaciones intensivas de lanzamiento de colecciones.

**Control de permisos y seguridad de agentes** [9BIy_h4L-MY]:
- Modo Automático (Anthropic): clasificador Sonnet 4.6 evalúa riesgos en tiempo real; bloquea comandos destructivos (`rm -rf`) sin intervención humana; disponible solo en planes de equipo. → aplica: activar para tareas de inventario/precios sin supervisión constante.
- Retransmisión de Permiso (v2.1.81+): el agente notifica vía Telegram cuando necesita aprobación sin detener la operación; 3 capas en `settings.json` (bloqueo, entorno auto, anulación). → aplica: aprobar desde móvil actualizaciones de catálogo CJ o emails de Klaviyo mientras se está fuera.
- Regla: comandos destructivos siempre requieren aprobación explícita aunque el clasificador los considere seguros; configurable por reglas de anulación. → aplica: bloquear borrados masivos de productos y cambios de precios sin confirmación.

**Automatización de contenido visual/video con N8N** [9cPhU_VfYeM] [CIYv59aJIv8] [rhKw-MUFb2E]:
- N8N orquesta pipelines completos: nodos Set Value + HTTP Request + Wait (60s/capítulo) generan video de 2h dividido en 10 capítulos × 24 segmentos de 30s; costo ~$2.25 total (~$0.02/imagen con KAI/Crema). → aplica: generar videos de producto tu-nicho / ambiente cozy con narración + fondo sonoro automatizados.
- N8N + File.ai (Flux Pro): 13 escenas × 5s = video de 65s; costo ~$3/video vs. $50/mes en tools premium; margen del 88% si se venden a $25; en TikTok ~$0.5 CPM → 50k vistas = $25. Batch interval: 2000ms entre prompts para evitar spam. → aplica: producir reels de tu-tienda con escenas de bienestar/tu-nicho a escala, sin editor humano.
- Nano Banana Pro (Google): 4K sin pixelación, $0.12/imagen vs. $0.02 base (6× más caro) pero sin errores de ortografía; integración cambiando el body del HTTP Request en N8N; soporta transparencia de fondo vía servicio de eliminación automático. → aplica: generar wall art / creativos de producto en 4K para listings de Etsy o ads de Meta.
- FFmpeg concatena clips en N8N: 13 clips × 5s = video final; wait nodes: 180s para sonidos, 600s para video final; Google Sheets marca ítems como "hechos" para tracking. → aplica: pipeline de contenido orgánico TikTok/Instagram semanal sin intervención manual.

**Generación masiva de anuncios sin costo** [BQID-wELOlo]:
- N8N + Nano Banana (Google, gratuito) genera 25+ anuncios/imágenes a $0: trigger Telegram → análisis imagen OpenAI → instrucciones IA → exporta a Box (10 GB gratis) o Telegram; lotes de 3s entre solicitudes para evitar bloqueos en Open Router. → aplica: crear 25+ variantes de anuncios para productos tu-nicho / bienestar sin presupuesto de diseño.
- Control de calidad: salida estructurada + analizador OpenAI verifica que cada anuncio cumpla especificaciones; nombres únicos por fila evitan duplicados; eliminar marca agua N8N añadiendo campo atribución. → aplica: validar que copies y creativos de tu-tienda sean on-brand antes de publicar en Meta/TikTok.

**Memoria local y búsqueda semántica (QMD + OpenClaw)** [JVqbQkb4oaU] [LfvKkrVSO-U]:
- QMD (Query My Documents) descarga ~2 GB de modelos desde Hugging Face (gratis); indexa Markdown cada 5 min; 3 estrategias: BM25 + semántica + clasificación por relevancia; da atribución exacta de archivo y línea; reduce uso de tokens evitando sobrecarga de memoria. → aplica: indexar destilados + KBs de tu-tienda para que Mano Derecha recupere contexto con precisión sin gastar tokens de Claude.
- OpenClaw (Mac/Win/Raspberry Pi) vs. Nemo Claw (solo Linux + Nvidia Cloud, alfa): OpenClaw con OAuth (ChatGPT Plus $20/mes) controla costos; Nemo Claw impone costos variables por Nvidia. → aplica: usar OpenClaw en máquina secundaria con OAuth para tareas de agente sin riesgo de costos inesperados.

**Generación automatizada de reportes y presentaciones** [RBcc_ezfh1s] [7sInxhTDA7U]:
- Markdown + Marp + Cloud Code: CSV de Facebook Ads → diapositivas profesionales con HTML/CSS (iconos SVG, gráficos animados, botones); exporta a PDF/PowerPoint sin herramientas externas; programación periódica para reportes semanales automáticos. → aplica: generar reportes de ventas tu-tienda y dashboards de campañas listos para revisar cada lunes sin trabajo manual.
- NotebookLM integrado con Claude Code via skill: genera diapositivas, resúmenes de video, podcasts e infografías desde fuentes YouTube/docs/web; cron local para investigación diaria automatizada. → aplica: resumir trends de tu-nicho / bienestar semanalmente y convertirlos en briefs de producto o contenido.

**Productividad con atajos de prompts (ChatGPT / Chrome)** [Hkrjh4vdWmA] [uoQaGqpYYoE]:
- Auto Prompting: atajos en perfil ChatGPT (P3 = paráfrasis 3 opciones, L = respuesta larga, S = resumen, T = tabla); combinables (P10S = 10 opciones en una frase); reduce esfuerzo de escritura >70%; funciona en web y móvil. → aplica: acelerar la generación de títulos, metas SEO y descripciones de producto para los listings de tu-tienda.
- Atajos Chrome: motores de búsqueda personalizados con `%s` como placeholder (C = ChatGPT, P = Perplexity, B = Bing); ahorro de 10–20 min/día en tareas repetitivas de investigación. → aplica: investigar precios de competidores, tendencias de nicho y keywords desde la barra del navegador sin pasos intermedios.

**Monetización de voz clonada (11 Labs)** [Y5ztamh_410]:
- Clonar voz requiere mínimo 30 min de audio (ideal 3h); etiquetado SEO (acento, género, estilo, uso educativo) mejora visibilidad en biblioteca; revisión tarda 1–2 días; Stripe se conecta al activar compartir; período de aviso recomendado: 30 días para migración de usuarios. → aplica: crear narraciones de tu-tienda (unboxing, tutoriales tu-nicho) con voz clonada propia para contenido escalable sin grabar cada vez.

### 12g · Imperia IA — FULL-PASS 2026-06-21
*(canal destilado; IA aplicada / agentes / automatización; ref: `_archivos_trabajo/_destilados/imperia_ia_p1_LOCAL.md`)*

**Selección de plan / modelo Claude** [0GEk7og8tC0]:
- Pro (20 €/mes) = acceso Opus + Chat; suficiente para decisiones y copy. Max (100–200 €/mes ×5 o ×20) = Opus + Claude Code; necesario para desarrollo intensivo o si el límite se alcanza en <3 s. API = solo esporádico, coste impredecible para uso recurrente. → aplica: tu-tienda usa Claude Code (Max); escalar si el límite aparece a diario en sesiones de curación/scripts.
- tu servidor LLM local + modelos abiertos (Qwen, Llama) en local: requiere 24 GB RAM, ~1 año por detrás de cloud, pero privacidad total. → aplica: Mano Derecha ya corre Qwen3-8B local; no mezclar datos de pedidos reales con cloud sin revisar GDPR/CCPA.
- Riesgo GDPR: uso de datos sensibles en cloud → multa hasta 4 % facturación anual. → aplica: nunca subir PII de clientes (emails, pedidos) a prompts de Claude.

**Comparativa de modelos (GPT 5.5 vs Opus 4.7 / precios futuros)** [eGxDavfYLIY] [GkOgdVVYVKE]:
- GPT 5.5: 70 % más eficiente en tokens → coste real menor a pesar de precio nominal más alto; alucinaciones 86 % cuando no sabe; superior en interacción con apps (clics, formularios) y generación de imágenes pixel-a-pixel. → aplica: usar GPT 5.5 para banners/creativos de producto y automatizaciones de UI.
- Opus 4.7: alucinaciones 36 %; lidera en programación compleja y proyectos grandes. → aplica: mantener Opus en scripts críticos de tu-tienda (phase2_publish, vet_catalog_wave).
- DeepSeek V4 Pro: descuento 75 % permanente (input $0.14 / output $0.87), 30× más barato que Opus; rendimiento aceptable con caché activada para tareas repetitivas. → aplica: evaluar DeepSeek para batch de i18n masivo o enriquecimiento SEO donde la precisión no sea crítica.
- Opus 4.8 / Sonet 4.8 filtrados: lanzamiento estimado finales junio 2026; menos alucinaciones, mayor eficiencia. → aplica: migrar Claude Code a 4.8 en cuanto esté disponible en Max.

**Claude Code — uso avanzado y gestión de tokens** [6tTstj2UZFo]:
- Contexto óptimo: mantener conversaciones <100 k tokens; costo dobla a partir de 200 k tokens (documentado Anthropic). Comandos `/clear` y `/resume` para optimizar sesiones largas. `/usage` para monitorear gasto por sesión. → aplica: en sesiones de curación de catálogo, hacer `/clear` entre bloques de productos para no acumular contexto inútil.
- Modo planificación: el agente genera un plan aprobable antes de actuar → ideal para cambios de tema o publicación masiva. Modo automático solo con Opus 4.7+. → aplica: usar modo planificación antes de correr `phase2_publish.py` sobre lotes grandes.
- Input por captura de pantalla (`Cmd+Shift+4`) para ajustes de diseño precisos; referenciar archivos con `@nombre_archivo`; revertir con `Escape×2` para no perder tokens. → aplica: QA visual del tema con `screenshot.py` + captura → prompt de corrección en Claude Code.
- `barra worktree` para proyectos en paralelo sin conflictos (similar a git branches). → aplica: separar rama de tema v2 de la edición de scripts sin bloquear el trabajo del daemon.

**Automatización de producción de video con IA** [1Ov5UXSKglg] [1zGj_bM7GaM]:
- Claude Code + Hyperframes: genera animaciones premium desde prompts; crea archivos SRT para contadores/texto dinámico integrables en CapCut. Esquema 80/20: IA hace el 80 %, ajuste creativo manual el 20 %. → aplica: producción de Shorts de tu-tienda (iluminación, aromaterapia) sin rodar: prompt → animación → SRT → CapCut.
- MCP (Machine Control Protocol) conecta Claude Code con Premiere Pro: automatiza eliminación de silencios en clips de 9 min, sincronización de audio, renderizado final con un prompt. Modo multiagente: 4–5 instancias Claude en paralelo según tokens disponibles. → aplica: si el volumen de video escala, conectar Premiere vía MCP para edición batch de product demos.
- Librería de componentes animados (mapas, contadores, efectos): crear una vez, reciclar en futuros vídeos. Open Design como base visual gratuita y reutilizable. → aplica: construir librería de assets tu-tienda (logo animado, lower thirds cozy) para consistencia de marca.

**Generación de video con Gemini OVNI** [nWXnayjskXI]:
- Clips de 10 s ultra realistas; sincronización audiovisual (labios, sonido, física). Precios: 8 €/mes ≈ 2–3 clips; 20 €/mes ≈ 5–6 clips; 100 €/mes ≈ 15–20 clips. Supera a Sora en coherencia y edición en tiempo real. Avatares personalizados con VPN (no disponible en Europa sin VPN). → aplica: generar anuncios de producto tu-nicho (ej.: proyector de estrellas en habitación cozy) con prompt + imagen de referencia del catálogo CJ; más rentable que producción en estudio.
- Framework: "Prompt + Audio/Imagen/Vídeo" = clip generado reutilizable como fuente de otro clip (coherencia en serie). → aplica: crear serie de clips de ambientación tu-tienda para Pinterest/TikTok con un solo asset base.

**Dashboard personal + integraciones no-code** [IPfNbktThco]:
- Stack gratuito: Claude Code + Supabase (BD) + Vercel (hosting) + Gmail + Google Calendar + OpenAI/Anthropic para transcripción de audio → bot Telegram que agenda reuniones o registra datos con foto/audio. Setup en 2 h usando Claude Design → exportar a Claude Code para backend. → aplica: construir dashboard de tu-tienda con ventas Shopify + stock CJ + KPIs de Pinterest en plan gratuito; bot Telegram para consultas rápidas de estado de tienda desde móvil.
- Variables de entorno en Vercel (API keys Shopify, Supabase, Anthropic): configuración paso a paso, sin código adicional. Código abierto → personalizable. → aplica: exponer `dashboard_server.py` en Vercel como alternativa al localhost:<PUERTO_TIENDA> para acceso remoto.

**Herramientas de diseño y presentaciones** [nRIO2NIxLK8] [lsVXH85jCiM] [kuLE6T85A2w]:
- Open Design (gratuito, open source): alternativa a Claude Design sin límites semanales; importa ZIPs de Claude Design; integra API key propia (Gemini, DeepSeek, Llama) para evitar dependencia única; deploy local para privacidad. → aplica: crear creativos de colecciones tu-tienda (iluminación, bienestar) sin consumir cuota de Claude Design.
- Gamma / Kimi Slides: presentaciones en 2–5 min desde prompt; créditos gratuitos para prueba. Plugin ChatGPT para PowerPoint: edición directa sobre plantillas + sincronización desde Excel. → aplica: generar pitch deck de tu-tienda o reportes de KPIs mensuales en minutos desde hoja de cálculo.
- Claude Code + GPT Images 2 + Next.js → web premium en 30 min; deploy en Vercel (plan gratuito + dominio). → aplica: landing page de colección hero (ej.: "Smart Lighting") con diseño de marca y vídeo integrado, sin agencia.

**Claude en Excel / análisis financiero** [TJ58Ym_ztM8]:
- Extensión nativa (Chrome Web Store / Office Add-ins): analiza datos, genera fórmulas, gráficos, escenarios ("¿qué pasa si subo precio 10 %?"), audita referencias rotas/divisiones por cero. Exporta a PowerPoint/Word/Outlook. Modelos: Opus (análisis complejo) o Sonet (urgente). → aplica: modelar márgenes netos tu-tienda (precio − costo CJ − envío − PayPal 5.4 %+$0.30) directamente en Excel con Claude; simular escenarios de descuento para campañas US sin salir de la hoja.

### 12h · Luciano Mattica — FULL-PASS 2026-06-21
*(canal destilado; IA aplicada / negocios con IA; ref: `_archivos_trabajo/_destilados/luciano_mattica_p1_LOCAL.md`)*

**Prototipado sin equipo técnico** [-rA2aO-FJdM]:
- Prompt de 62 líneas en ChatGPT + Cloud Design → prototipo funcional con botones, métricas y vistas en ~10 min, sin diseñador ni Figma. → aplica: crear apps de bienestar (hábitos, meditación) o configuradores de tu-nicho para tu-tienda sin contratar desarrolladores.
- Exportación en ZIP/PDF/PowerPoint/Canva/HTML; Cloud Code + API conecta backend automático sin programación. → aplica: exportar como HTML e integrar con scripts existentes de tu-tienda para demos o landing pages de producto.
- Reducción del 25% en tokens vs. Opus 4.7; duplicar prototipo como plantilla reutilizable para múltiples proyectos. → aplica: mantener costo bajo al iterar creativos o prototipos de páginas cozy/bienestar.

**Producción audiovisual automatizada** [FhCyKN0nJnk]:
- Cloud Code + API Whisper (OpenAI) para transcribir videos y generar planes de edición en "plan mode" con timing exacto, animaciones y motion graphics → reducción del 60%+ en tiempo de producción. → aplica: automatizar subtítulos + animaciones para promos tu-nicho/cozy de tu-tienda sin edición manual.
- Segmentación modular por secciones: corregir solo la parte específica sin recalcular todo el proyecto. → aplica: actualizar clips de producto o tutoriales de aromaterapia/masaje de forma puntual.
- Renderización final a 4K como paso de cierre; límite de 2500 palabras/mes en Gladio → batch editing para maximizar uso del API. → aplica: priorizar videos de mayor impacto (hero, UGC) dentro del límite mensual.

**Testing y automatización web** [HAh4dyQoVtA]:
- Asient Browser es 5.7× más eficiente que Playwright (evita screenshots innecesarios) → conversaciones más largas, menos interrupciones. → aplica: automatizar QA del checkout multi-paso de tu-tienda (Shopify + PayPal) con Cloud Code sin coste de Playwright.
- Monitoreo de precios y cambios de sitio web de competencia sin API; ejecución en sandbox Versel (nube), no requiere computadora encendida. → aplica: rastrear precios de competidores de iluminación/tu-nicho en EE.UU. de forma continua.
- Login automático en plataformas, descarga de reportes y completado de formularios (CJ, Meta Ads, Judge.me). → aplica: acelerar flujos repetitivos de curación y reseñas en tu-tienda.

**Dashboard operativo personalizado** [WXJ_MglLH_k]:
- Cloud Code genera dashboard con filtros de facturación por periodos (30/60/90 días), clientes recurrentes vs. únicos, panel de tareas multiusuario y banco de ideas centralizado. → aplica: unificar métricas de ventas Shopify, tareas de curación y contenido en un solo panel para tu-tienda.
- Tokenización: APF Token (Instagram) + Meta Access Token + Telegram Bot Token + Chat ID para notificaciones automáticas 5 min antes de tareas críticas. → aplica: alertas de publicación de productos, fechas de anuncios y cobros sin revisar manualmente.
- Integración en tiempo real con Instagram y Meta Ads: mejor adset, creativo, impresiones, clicks visibles en el dashboard. → aplica: tomar decisiones de pausa/escala de anuncios de tu-tienda desde un solo lugar.

**CLAs vs. MCPs — optimización de tokens** [hYhEU2xyBYQ]:
- CLAs (Command Line APIs en Go) usan 1800 tokens donde MCP usa 98k (ejemplo Airbnb) → 35× más eficiente; sin servidor, sin round trips. → aplica: reemplazar MCPs de Shopify/CJ por CLAs para reducir impuesto de contexto en sesiones largas.
- Printing Press: >50 CLAs preconstruidos + CLA Factory (describe en lenguaje natural → Cloud Code genera y compila en Go). Acceso a servicios sin API pública: TikTok Shops, ESPN, Craigslist. → aplica: construir CLA para TikTok Shops y automatizar workflows de tu-tienda (resumen → Discord).
- Prioridad recomendada: CLA > API > MCP; usar `slash context` en Cloud Code para auditar qué MCPs consumen tokens innecesariamente. → aplica: auditar los 19 plugins actuales de tu-tienda y sustituir los más pesados.

**Automatización programada (loops y rutinas)** [t7PUaqCQxpQ]:
- Loop en Cloud Code: intervalos definidos (ej. cada 30–45 min), autoexpira en 7 días, usa Chrome headless. → aplica: monitoreo de precios de competencia o métricas de anuncios de tu-tienda sin sesión abierta.
- Cloud Routines + Desktop Schedule Task: integración con Cloud Code, sin sesión, pero mínimo 1 hora de intervalo. → aplica: reportes horarios de stock CJ o métricas de Pinterest.
- Modal/Trigger.D: serverless avanzado con scripts TS de larga duración y auto-retrials; solo para devs. → aplica: reservar para integraciones complejas si tu-tienda escala a equipo técnico.

**Generación de imágenes para e-commerce** [yPP8_SjxWjI]:
- ChatGPT 4o Image vs. Nano Banana: +35% consistencia (+200 puntos en pruebas), formato vertical nativo (ideal para banners), sin marca de agua, texto manuscrito realista sin errores. → aplica: generar hero sections, banners cozy y UGC selfies de productos tu-nicho sin contratar fotógrafo.
- Casos prácticos validados: hero section con marca automática, fotos de comida ultra-realistas, logos en estilos 3D/metal/glass/fluffy, carruseles de hasta 4 imágenes desde un solo prompt. → aplica: crear variantes de creativos para Meta Ads e Instagram de tu-tienda directamente desde descripciones básicas.
- Límite: máximo 5 imágenes seguidas sin espera de 4 min (vs. Nano Banana sin restricciones). → aplica: planificar sesiones de generación en batches de 5 para mantener fluidez.

### 12i · Centeia — FULL-PASS 2026-06-21
*(canal destilado; IA aplicada + marketing con IA; ref: `_archivos_trabajo/_destilados/centeia_p1..p5_LOCAL.md`)*


**Automatización de marketing y contenido** [29mNkLLGnPo] [UjMh80cy4Pw] [VBUk2NAxA-M] [cnmb6y0sgmc]:
- Make.com + ChatGPT + DALL·E 3 generan publicaciones simultáneas para 7-15 redes sociales; 1h manual → 5x más rápido con automatización. → aplica: crear flujo Make que genere posts tu-nicho/cozy para Instagram (cuadrado) y LinkedIn (16:9) desde un solo input de producto.
- Pipeline completo sin código: Whisper (transcripción audio) → ChatGPT (guion) → ElevenLabs V2 (voz clonada) → Sora/Hey (vídeo IA) → Google Drive (almacenamiento) + Telegram/WhatsApp (distribución); delay 240 s entre pasos para evitar errores de generación. → aplica: convertir demos de producto o podcasts de bienestar en Reels/Shorts sin producción manual.
- Make.com automatiza captura de leads (Google Maps + Serapi), gestión de correos (Gmail → borradores HTML en 15 min/día vs 3h), clasificación de facturas por mes y publicación en redes desde formularios con Dali 3. → aplica: capturar correos de proveedores CJ y clasificarlos automáticamente; publicar nuevos productos con imagen generada.
- Agentes GPT dedicados por canal con lógica específica (LinkedIn = profesional, TikTok = viral); artículos blog generados en Markdown convertidos automáticamente a HTML para Shopify. → aplica: pipeline de contenido SEO que sube directamente al blog de tu-tienda en Shopify.

**Creación de vídeo con IA** [8tTbMmZN-og] [Hz_cmG5vPnU] [tPcgRi1k-bE] [lHO4pAy86JA] [tgajoyKzbVE]:
- Pica Effects (modelos Turbo / 1.5): efectos *squish/crush/melted/explode* sobre imagen de producto → vídeo 1-2 min en lugar de 10+ h de edición; reducción de coste de producción 90%; Pica FX 1.5 elimina fragmentos sin presentador, integra audio generado → 70% menos tiempo de edición. → aplica: crear demos animadas de luces LED, termostatos o humidificadores con un solo prompt en inglés.
- Highfield centraliza todos los modelos (Clean 3.0, Sora, BO3, etc.) por ~25 €/mes vs 20 €/modelo individual; flujo: prompts multishot de 15 s divididos en escenas de 3 s → agente GPT "Clean 3.0 Prompt Generator" → Motion Control para transformar caras/cuerpos; tiempo total ~15 min por proyecto. → aplica: producir vídeos de producto tu-nicho en 720p/1080p con narrativa cinematográfica sin equipo de vídeo.
- BO3 (Google) + FreePic: acceso sin VPN ni pago de 24 $/mes; generación en 3-4 min; prompts en formato Jason (estructura JSON con estilo, cámara, duración, ambiente) vía ChatGPT para evitar que la IA "invente" elementos no solicitados; audio generado automáticamente en 16:9. → aplica: demostraciones técnicas de productos cozy con narrativa ASMR y precisión de escena.
- Sora (plan Plus $20/mes, HD 720p): Recut + Remix para sustituir elementos; Blend para fusionar vídeos; Loop para contenido reutilizable; plan premium +$200/mes para 1080p + 20 s y 5 vídeos simultáneos. → aplica: crear loops de ambiente cozy para stories o anuncios de retargeting.

**Generación de imagen con IA** [HHc8xYvJg6o] [UiaxMgTSHmg] [Axg0ks1PvCg]:
- Ideogram 2.0: mejor que DALL·E o Midjourney para realismo; prompt negativo para eliminar elementos no deseados; ratio 9:16 para social, 16:9 para producto; paleta automática; formato JPG 70% / PNG 100% para tienda; genera hasta 5 diseños de un mismo producto en segundos. → aplica: imágenes de productos tu-nicho con fondos cozy, diferentes ambientes y etiquetas de marca sin diseñador.
- GPT Image 2.0 lidera en texto legible, infografías, miniaturas YouTube y páginas web de e-commerce (tarjetas con nombre, precio, 2 beneficios, etiqueta de color); Nano Banana 2 supera a Pro en calidad cinematográfica y renders 3D realistas (2.5 créditos vs 2) en formato 16:9 2K. → aplica: generar miniaturas comparativas de productos, storyboards de 8 viñetas y anuncios en múltiples formatos desde un mismo brief.
- Grok 4 disponible gratis en x.com/i/grok: genera imágenes fotorrealistas, cinematográficas y anime; soporta edición en tiempo real con referencia visual; benchmark 95.7% de precisión. → aplica: creativos de ads US-first con estilo fotorrealista sin coste de licencia de modelo.

**Chatbots, agentes y automatización de soporte** [SZPFU59u9T4] [iUYp2YitVq8] [nFF6g0BrOjs] [28EenIr14Rc] [LDzXdnaPFv4]:
- Nubion AI: 2 bots por $29/mes (vs competidores >$50 por 1 bot); modelos GPT-3.5 Turbo / GPT-4 Mini; entrenamiento con PDF/DOCX hasta 100 MB; 50+ preguntas predefinidas; integración WhatsApp + web embeddable + Telegram + Calendly en 30 s de setup; reducción de tickets + aumento de conversiones. → aplica: chatbot tu-tienda entrenado con fichas de producto tu-nicho y FAQ, activo 24/7 en el storefront y WhatsApp.
- Agentes de llamada automatizadas (BAPI + Make.com + ElevenLabs): latencia reducida de 1700 ms → 575 ms con modelo V2 Flash; flujo: nombre → fecha ISO 8601 → confirmación → router de disponibilidad; facturación real de 3.500 €/mes vendiendo automatizaciones de reservas; coste IA vs salario humano: 3.500 vs 1.200 €/mes con ROI en 5-6 meses; llamadas masivas con ofertas = +20% facturación anual. → aplica: automatizar seguimiento post-venta y recordatorios de pedido en tu-tienda sin contratar soporte adicional.
- Agentes IA autónomos vía Make.com con subagentes (5-20): cada uno ejecuta tareas específicas (correos, facturas, eventos Google Calendar, inventario); inputs en lenguaje natural ("mañana a las 11"); tokens limitados a 100k por llamada; activación on demand para evitar sobrecarga. → aplica: sistema de 5-10 escenarios que gestionen pedidos CJ, notificaciones de stock y respuestas a clientes sin intervención manual.
- Configuración WhatsApp Business + Nubion AI vía Meta for Developers: permisos clave = WhatsApp Business Manage Events + Messaging; token sin caducidad; endpoints activos solo "messages" + "subscriptions". → aplica: canal de soporte omnicanal para tu-tienda con respuesta automática a preguntas de producto.

**Prompting, modelos y uso eficiente de IA** [4UvfAHDqDJ8] [CH2apFzkBug] [HrEsM-y6Hp0] [8RlgawxSBCc] [ZC5vKDwfFZ4] [QL Cp Re-u4GE]:
- Método Aspect (7 elementos): Acción + Pasos + Persona/Rol + Ejemplos + Contexto + Restricciones + Plantilla; mínimo 15-20 palabras por prompt; metaprompting = pedir a la IA que genere las preguntas de contexto necesarias antes de ejecutar. → aplica: estructurar prompts de descripciones de producto tu-tienda con rol "experto en tu-nicho US-first", restricción "sin tecnicismos", plantilla con beneficios + CTA.
- Temperatura 0 para emails formales/deterministas; temperatura 2 para ideas y creatividad; modelos por tarea: Sonnet 4.6 para resúmenes/análisis diarios, Opus 4.7 para estrategia compleja/código; archivos en Markdown reducen consumo de tokens hasta 50% vs PDF/Word; proyectos fijos con instrucciones evitan pérdida de contexto. → aplica: proyecto Claude "Analista tu-tienda" con instrucciones fijas de tono cozy + restricciones de marca para generar todo el contenido de marketing desde una sola sesión.
- GPT-5.5 responde en ~30 s con código funcional y landing en React + TypeScript; Claude Opus 4.7 tarda ~5 min pero supera en análisis contextual y simulaciones interactivas; GPT-5.5 es más eficiente en coste por resultado para prototipos y automatización. → aplica: usar GPT-5.5 para generar scripts de automatización y landing pages de producto; Claude para estrategias de catálogo y análisis de competencia.
- Forzar razonador con "Tómate tu tiempo y piensa paso a paso"; controlar longitud con "conciso en 50 palabras" o "documento extenso"; bloquear razonamiento interno con criterios predefinidos antes de la respuesta final; combinar búsqueda web + modelos razonadores para datos reales (ej: precio Meta subió 15% → análisis de factores). → aplica: prompts de estrategia de marketing tu-tienda con criterios: "Claridad, US-first, margen ≥25%, tono cozy".

**Herramientas de automatización no-code** [fd3JlBMY3rE] [7AgN1jSVukQ] [M41QsYnKSqk] [8GS4sfC4IC0]:
- Comparativa de costes: Zapier 170 €/mes (10k ops, 8.500 apps) vs Make.com 10 €/mes (10k ops, 2.000 apps) vs N8N 24 €/mes (2.500 ejecuciones, 1.040 apps); Make.com = opción preferida para Shopify + CRM; N8N = mejor para agentes IA personalizados y control técnico. → aplica: Make.com como plataforma principal de tu-tienda para flujos de contenido, facturas y seguimiento; N8N para agentes avanzados si se necesita personalización.
- Rutinas Cloud (Claude): automatización serverless 100% en la nube incluso con PC apagada; trigger horario (ej: domingo 18h) o vía API; conectores Gmail, Notion, Google Calendar, Slack sin configuración de nodos; planes Pro (5 rutinas/día) / Max (15) / Enterprise (25); frecuencia mínima 1h entre ejecuciones; prompts como SOP (paso a paso + tono + error handling). → aplica: newsletter semanal de novedades tu-nicho generada automáticamente cada lunes con contenido curado de Perplexity + redacción Claude.
- Stack de herramientas clave por función: N8N/Make.com (automatizar) + ChatGPT+Gamma (contenido y presentaciones) + 11Labs+Runway Gen4 (vídeo) + Cursor (código sin saber programar) + Copilot M365 (integración total en Office). → aplica: usar Gamma para presentaciones de producto tu-tienda para inversores/proveedores; Cursor para scripts de Shopify a medida.

**Marketing con IA: contenido, AEO y captación** [qSLK72z8AfM] [ZGGiWxOLSAM] [29mNkLLGnPo] [wznmfx4vpEE] [s9YQJ7N95RM]:
- AEO (Answer Engine Optimization): crear páginas que respondan preguntas directas como "¿Qué son los mejores humidificadores inteligentes para dormir?" o "¿Cómo optimizar energía en casa inteligente?"; incluir FAQ específicas para IA, comparativas de productos, transparencia de precios; analizar cómo aparece la marca en Gemini/Perplexity con prompts como "¿Qué marcas recomiendas para tu-nicho?". → aplica: crear sección de preguntas de SEO+AEO en el blog tu-tienda con 20+ prompts del ICP estadounidense sobre bienestar y domótica.
- Extracción de leads en Instagram vía hashtags específicos (#tu-nicho, #CozyLiving, #WellnessTech) + campañas de email con variables dinámicas ("Hola [Nombre], soluciones para tu hogar inteligente") + seguimiento automatizado de 5-10 correos con valor incremental; descuento 30% como incentivo de conversión. → aplica: secuencia automatizada de cold outreach para compradores de tu-nicho en EE.UU. con Calendly integrado.
- Embudo Meta Ads generado con Claude + Figma: 5 puntos de dolor → 15 anuncios (3 por punto) + landing con vídeo UGC + CTA de llamada → cierre; tiempo manual 3 días → minutos con prompt estructurado. → aplica: construir el funnel de adquisición de tu-tienda con Claude exportando a Figma usando el plugin "Fix Jump" para e-commerce + IA.
- Contenido viral con Gemini: análisis de tendencias (5 temas más relevantes en automatización), canvas interactivo de ROI (158 h/semana perdidas sin automatizar = ahorro del 70%), copywriter personalizado basado en patrones de escritura propios, listas de publicación automatizadas para 4 días de LinkedIn. → aplica: calendario de contenido de tu-tienda generado semanalmente por Gemini con ganchos específicos para bienestar + tu-nicho.

**Avatares IA y creación de contenido con voz clonada** [3S3XwoytT6g] [-tsWk69Xb2M] [qPg9aHg3P_Q] [fea8YyS3Eco]:
- HEEEN (plataforma de avatares): hasta 100 avatares por persona; plan gratuito (3/mes) / Premium $29/mes (ilimitado); grabación de 2-5 min con cámara fija + fondo estático + sonido ambiente; 3 modos de creación: script, grabación en vivo, audio previo; reduce costes de producción 80% vs vídeo tradicional. → aplica: grabar una vez con el fundador y generar múltiples tutoriales de instalación y demos de producto tu-nicho en español e inglés.
- Clonación de voz ElevenLabs: 30 min de audio = +45% precisión vs 2 min (instant cloning); plan Pro $22/mes → transcripción de archivos hasta 1 GB + voz multilingüe + edición de fondo sonoro; speech-to-text convierte contenido existente en texto SEO-friendly. → aplica: convertir vídeos de proveedores o demos en guiones editados, generar narración de marca consistente para todos los vídeos tu-tienda.
- Modelos de negocio con avatares: faceless content + AdSense/afiliados; formación corporativa e-learning (10k-30k €/proyecto); UGC para marcas (packs 30 vídeos TikTok a 2k-5k €); agencia de avatares = setup + retainer (5 clientes @ 2k €/mes = 10k €/mes); automatización post-producción con Make/Zapier para subida automática desde plantillas. → aplica: generar UGC de tu-tienda con avatares para TikTok/Instagram y vender ese servicio a marcas de bienestar complementarias.

**Estrategia operativa: niveles de uso IA y validación de negocio** [xeHcy7yLLD0] [5F477ngsxhc] [MeGwg5TObA0] [11FUMqV5LkY]:
- 3 niveles críticos de uso: nivel 1 = chatbot reactivo (99% de usuarios); nivel 2 = IA completa procesos (analiza → resume → redacta → sugiere siguiente paso); nivel 3 = orquestación de agentes especializados (investigación + análisis + redacción + revisión coordinados). Ventaja competitiva en nivel 2-3. → aplica: llevar tu-tienda de nivel 1 (consultas aisladas a Claude) a nivel 2 (proceso de publicación de producto 100% asistido) y planificar nivel 3 para gestión de catálogo.
- 7 errores a evitar al implementar IA en negocio: (1) empezar sin problema medible; (2) confundir demo con negocio; (3) saltar a agentes autónomos sin dominar workflows; (4) diversificar sin foco; (5) creer que la IA se adopta sola; (6) datos sucios (datos sucios = decisiones malas); (7) usar IA como atajo sin proceso. → aplica: antes de automatizar un nuevo flujo en tu-tienda, definir métrica clara (ej: reducir tiempo de respuesta al cliente del 40%) y limpiar datos de CJ primero.
- Framework de automatización por niveles: (1) tarea puntual con IA; (2) guardar proceso para repetirlo; (3) proceso repetible documentado; (4) conectar con herramientas internas; (5) automatizar parcialmente → +20% eficiencia en marketing al usar IA con datos reales de comentarios de clientes. → aplica: documentar cada proceso de publicación tu-tienda como SOP en Notion antes de automatizarlo con Claude/Make.
- ROI primero en proyectos IA: no hablar de IA como "moda" sino de "30% menos tiempo de respuesta al cliente", "reducción Z% costes", "aumento Y leads"; implementación iterativa (fase 1: implementar, fase 2: feedback, fase 3: ajuste, fase 4: medir); sistemas críticos que no se pueden apagar = chatbot de atención al cliente + automatización de leads. → aplica: medir y reportar mensualmente el ahorro de tiempo de tu-tienda con IA para justificar la inversión en herramientas y escalar.

### 12j · Álvaro Pareja — FULL-PASS 2026-06-21
*(canal destilado; Claude para marketers / IA aplicada; ref: `_archivos_trabajo/_destilados/alvaro_pareja_p1..p2_LOCAL.md`)*

**Claude / Skills de Claude para marketing** [3fIG3DTxf8c] [P5cbRgqZ114] [JLQ6cKo-JvY]:
- Proyectos + Skills en Claude = 10x productividad: un anuncio dentro de un proyecto con brief del cliente incluye diferenciación competitiva vs. copy genérico; tasa de conversión 3x mayor con contexto específico. → aplica: crear proyecto tu-tienda con productos tu-nicho, público US, voz cozy/bienestar; cargar en cada sesión.
- Claude Opus 4.6 supera a GPT en marketing y campañas complejas: genera 50 líneas de copy en una llamada, reduce costos por cliente un 35%; versión pro ($20/mes) da acceso a CWork (agente web) para investigación de competencia en tiempo real. → aplica: usar Claude para redactar PDPs, emails Klaviyo y copy Meta con proyecto precargado.
- Skills reutilizables (MetaAds Analyser, Competitive Ad Extractor, Copywriting Skill, Ad Creative Skill, Elite Research Assistant): MetaAds Analyser diagnostica campañas en <30 segundos (breakdown effect, learning phase, audience fatigue); Competitive Ad Extractor genera battle map de anuncios rivales; Ad Creative Skill genera 3 versiones con ángulos miedo/deseo y cumplimiento regulatorio. → aplica: auditar campañas tu-tienda semanalmente con MetaAds Analyser; analizar competidores de iluminación LED con Competitive Ad Extractor.
- Cowork (agente autónomo Claude Pro): automatiza Daily Briefing a las 7am (Google Calendar → prioridades), genera landing pages en HTML directamente, crea secuencias de email con framework PAS (Problema-Agitación-Solución) y estructura bienvenida → problema → solución diferenciada → prueba social → cierre. → aplica: automatizar redacción de campañas Klaviyo para tu-tienda con conectores Google Drive + Canva.

**Creativos e imágenes con IA** [5Rkzb1ov3Rg] [JxCensnyfOM] [iJbudK8_H3E] [FkghvJw3yU0] [5781EjrhSjk] [-Jf0IXjWyvI]:
- Nano Banana + BO3/Clink AI: genera imágenes en segundos (reemplaza fondos, logos, productos), convierte a animaciones de 5–10s con efectos lluvia/nieve; prompt clave: "sustituye [producto] por [nuevo], estilo comercial, iluminación natural". Sin Photoshop ni diseño técnico. → aplica: crear creativos de lámparas ambientales con fondo cozy (sala, dormitorio) animados para Meta/TikTok.
- ChatGPT Plus ($20/mes): genera hasta 10 imágenes/día con estilo 3D/Pixar, UGC con personas reales (mujer 40 años, perfil objetivo US), recrear estilo de marcas referentes (IKEA, Fanta) subiendo imagen de referencia + producto. → aplica: producir variantes A/B de banners para Shopify y creativos Meta sin sesión de estudio ($100+ por sesión vs $20/mes).
- Framework FAB (Feature-Action-Benefit) en prompts de imagen: "Crea 3 versiones en vertical/cuadrado/horizontal para Instagram, Facebook y Pinterest"; "Adapta a gustos culturales de Brasil, Francia y España"; "Mantén personaje X con misma apariencia en todas las imágenes". → aplica: generar set de creativos multiformato por cada producto hero tu-tienda.
- Google Flow (BO3) + Google Bard: vídeo comercial en 5 minutos a partir de imagen real + prompt: *"commercial-style video in Spanish, smooth camera movement, close-up of the dish, natural lighting, 16:9 format"*; 50 vídeos/mes con cuenta pro gratuita (1000 créditos ≈ $20 USD). → aplica: producir vídeos de producto tu-nicho para Reels/Shorts sin equipo externo.
- Pomeli (beta gratuita): Business DNA en 5 minutos (tono, colores, tagline), fotoshoots con IA en 2–3 min; flujo recomendado: Pomeli para ideas → Canva/BO3 para edición → publicación manual. Descarga inmediata (las sesiones se borran). → aplica: generar ideas de campaña y primeras imágenes sin presupuesto de diseño.

**Estructura de campañas Meta Ads / algoritmo Andrómeda** [2ZHPHbwRN2c] [E8S0whDGB00] [P4E5qoBvSt0] [cy_Mve46ctA] [Entd1sZs3ig] [c0CtWwHB4-U]:
- Andrómeda (algoritmo Meta 2025): señales de filtrado = distribución desigual de presupuesto (1 anuncio gasta $2, otros <$0.10), impresiones <300/día, CPMs >$5, CTR <2%. Requiere creativos completamente diferentes (no variaciones mínimas de color/texto): videos, testimonios, demos, UGC, fundador, nosotros-vs-ellos. → aplica: lanzar 10–15 creativos por conjunto en campañas tu-tienda; rotar cada 15 días los de bajo rendimiento.
- Estructura consolidada: 1–2 conjuntos de anuncios con 10–15 creativos (no múltiples conjuntos con 1–3 anuncios cada uno). CBO para distribución automática del presupuesto. Auditoría de Opportunity Score: si <70, crear nuevos creativos con estrategias distintas. → aplica: consolidar campañas fragmentadas de tu-tienda en estructura 1 conjunto / 10+ creativos.
- Desactivar TODAS las mejoras Advantage Plus manualmente (13 opciones en 2025): retoques visuales, traducción, animación, música, contenido multimedia flexible. "Optimizar texto por persona" se reactiva automáticamente (Meta lo considera "esencial"); duplicar anuncios ya configurados para no repetir proceso. → aplica: auditar cada anuncio activo tu-tienda y desactivar mejoras antes de escalar.
- Escalado vertical: +20% de presupuesto cada 3 días (método conservador, no afecta fase de aprendizaje). Detener cuando costo por conversión sube o ROI cae por debajo de 2.5. No dejar anuncios en stand-by sin haber alcanzado 3,000 personas. Escalado horizontal (duplicar campaña) solo con datos sólidos y segmentación adicional por género/edad. → aplica: escalar campañas ganadoras tu-tienda en incrementos de 20% con ventana de análisis de 3/7/14/30 días.
- Geografía amplia reduce CPA: campaña nacional México genera mensajes a $5 pesos vs. local a $21 pesos (4x más caro). ABO con 3 conjuntos + 15 anuncios da más control sobre distribución. → aplica: en campañas US-first de tu-tienda, usar targeting abierto nacional antes de segmentar por ciudad/estado.

**Atribución y métricas** [SkN9Or3li3s] [10UiQYXlTJw] [a21QeyQ5i4U] [PMTAQEDLNdM]:
- Atribución incremental vs. estándar: modelo estándar atribuye 100% de ventas a anuncios; incremental calcula solo ventas directas por publicidad (típicamente 60–70% menos: ej. 21k → 8k). Recomendación: usar estándar para optimización, pero añadir columna incremental para análisis real del impacto. → aplica: crear columna personalizada en Ads Manager tu-tienda para medir ventas incrementales y ajustar presupuesto hacia anuncios con mayor impacto real.
- Desglose de público (Meta): público activo = visitantes web + interacciones sin compra; clientes actuales = listas de compradores + eventos de compra (Pixel, 180 días). En retargeting: si >50% es público nuevo → error de configuración. En prospección: si >70% son nuevos → correcto. Desactivar "usar como sugerencia" en Advantage Plus para evitar que Meta mezcle públicos. → aplica: configurar segmentos de público tu-tienda con Pixel Shopify + lista de clientes CJ.
- Métricas de vídeo AIDA (5 métricas clave): Hook Rate >25% (reproducciones 3s/impresiones), Retención 75% del vídeo >2%, CTR >1%, Conversión >2.5% (compras) / >20% (leads), Tiempo de reproducción 3–5s mínimo. Crear métricas personalizadas en Ads Manager. → aplica: añadir estas 5 métricas como columnas en Ads Manager para todos los vídeos de tu-tienda.
- Reglas de monitoreo: revisar campañas cada 3 días (si presupuesto >$500/día, 2 veces/día); CTR <1% = anuncio muerto; >2% = alto rendimiento. Subir presupuesto máximo 20%/día; si costos crecen al subir, detener. Publicidad es subasta: más inversión = más caro (no hay economía de escala). → aplica: establecer calendario semanal de revisión de campañas tu-tienda con umbrales fijos de corte.

**Segmentación y psicología del consumidor** [sdRkoCX3X_Y] [yrw-g8dA2as] [c6OW_zn_0EM] [Bc3TSMmegQQ] [osP1XIyXYN8]:
- Pirámide de consciencia (Eugene Schwartz): 3% decisión inmediata, 17% búsqueda de información, 20% conscientes del problema, 60% inconscientes. Presupuesto ideal: 50%+ en fríos (memes, contenido educativo), 30–40% tibios (testimonios, UGC), 20% calientes (descuentos, urgencia). No competir por el 3% con descuentos; el mercado está saturado. → aplica: fríos tu-tienda = "¿Por qué no duermes bien?" + contenido sobre ambiente luminoso; tibios = UGC de lámparas en uso; calientes = "Últimas unidades".
- Psicología de compra (Nelson Consumer Neuroscience): 95% de decisiones son subconscientes. Framework de 5 mitos: (1) Aversión a la pérdida > razones racionales; (2) Repetición inconsciente > creatividad disruptiva; (3) Emoción primero, razón después; (4) Anclaje psicológico de precios (mostrar precio alto primero); (5) Prueba social > campaña publicitaria. → aplica: en PDPs tu-tienda usar "Si no tienes iluminación ambiental, tu sueño se ve afectado" + testimonios reales + precio tachado alto antes del precio real.
- Meta vs. Google por intención: Google para intención alta (busca activamente); Meta para intención baja/visual (compra por impulso o deseo). tu-nicho + bienestar = intención baja → priorizar Meta. Usar Google solo para servicios urgentes (instalación, soporte técnico). → aplica: 80%+ del presupuesto publicitario tu-tienda en Meta; Google Ads solo para keywords de soporte/instalación.
- KPIs de campaña de conversión ($500/día): CTR >1.5%, CPC <$5, tasa conversión >2%, CPA <$150, ROAS ≥2x. Primeros 7 días: validar audiencia + creativo + oferta; ajustar presupuesto +20%/día hacia conjuntos ganadores. Remarketing = 10–20% del presupuesto (carritos abandonados). → aplica: usar estos umbrales como criterios de corte/escala en campañas tu-tienda US-first.

**Herramientas de automatización y espionaje competitivo** [7rqicBCPq6w] [43hYND_jgLc] [-nuDDAjUmy4] [aR66YkFI94o] [BsCkIDjkT-I]:
- Atria ($159/mes): automatiza investigación de competencia, genera 4 versiones de anuncio desde URL rival, usa Canva templates sin costo adicional. Rentable solo si facturación >$10k/mes; versión gratuita 7 días para validar ROI. Riesgo: textos genéricos → editar siempre para sonar auténtico. → aplica: usar periodo de prueba de Atria para analizar competidores de iluminación LED smart en Meta Library.
- Winning Hunter: espionaje competitivo + generación de anuncios; sube URL de producto → genera copy + landing page automáticamente. Ideal para e-commerce. → aplica: subir productos tu-tienda a Winning Hunter para generar variantes de copy y comparar con anuncios de competidores en el mismo nicho.
- Claude Code + Antigravity: dashboard personalizado de MetaAds sin código (npm install + npm run), conectado vía tokens de MetaAds API. Muestra CTR, CPM, alcance vs. periodo anterior (ej: +34% CTR), alertas automatizadas por campaña sin resultados. Chatbot integrado para consultas: "¿qué hacer con frecuencia alta de 6?" → aplica: montar dashboard local tu-tienda para seguimiento semanal de campañas sin entrar manualmente a Ads Manager.
- AI Creative / Opus Clip / Napkin AI: AI Creative genera paquetes completos (texto + audiencia + creativos) en minutos desde URL de tienda, cobra por descarga (7 días prueba, 10 descargas gratis); Opus Clip recorta vídeos largos en shorts/reels virales, ahorra 10h → 1h; Napkin AI genera gráficos desde texto (velocidad 10x). → aplica: Opus Clip para reutilizar vídeos de productos tu-tienda en múltiples formatos; Napkin AI para infografías de características tu-nicho.

**Infraestructura publicitaria Meta (Business Manager / Pixel / seguridad)** [23oLj5TYk8E] [DskjSnODZf0] [Je0ValCM2nE] [RR4ugzB05Vc] [0mOVCp2WA7E]:
- Business Manager obligatorio antes de lanzar campañas: conectar Facebook + Instagram + WhatsApp en un solo BM; usar Business ID (no correo) para dar acceso a socios/agencias; acceso parcial a colaboradores (contenido, mensajes, anuncios, estadísticas, pero NO control total ni acceso financiero). Zona horaria y divisa se fijan al crear y NO cambian. → aplica: verificar que tu-tienda tenga BM con dominio verificado, pixel activo y roles definidos antes de escalar presupuesto.
- Pixel + API de Conversiones en Shopify: instalar vía "Conjunto de datos y píxeles" con categoría bienestar (evitar compartir info prohibida); verificar con extensión Metapixel Helper en Chrome; la integración Shopify-Meta configura automáticamente eventos (carrito, compra). Publicar tráfico de prueba y confirmar estado "Activo" en administrador de eventos. → aplica: verificar estado del Pixel tu-tienda + API de Conversiones antes de cada campaña nueva.
- Seguridad de cuenta: autenticación 2 pasos (Google Authenticator) para todos los colaboradores; tarjeta de crédito con saldo suficiente (evitar virtuales o CVV dinámico); no cambiar dispositivo/ubicación abruptamente (Meta detecta patrones sospechosos); verificar identidad en BM (dominio, página, 2FA). Revisar periódicamente business.facebook.com/businessupporthome. → aplica: checklist de seguridad trimestral para cuenta tu-tienda Meta.
- Business Suite (gestión contenido) vs. Business Manager (gestión activos): Suite = programación de posts, estadísticas, mensajes; Manager = píxeles, anuncios, colaboradores, seguridad. Horarios óptimos Instagram sugeridos por Meta: 12h, 15h, 19h. Facebook: 17–18h. → aplica: programar contenido orgánico tu-tienda en Suite usando horarios pico; gestionar pixel y colaboradores solo desde Manager.

# FULLPASS — Nate Herk (~254 videos, p1–p8)
> skill: ia-aplicada | canal: automatización IA, n8n, agentes, Claude | fecha: 2026-06-21


## 1. ARQUITECTURA MULTI-AGENTE Y ORQUESTACIÓN

- **Patrón orquestador→subagentes** [0iUNOmeU7O4]: agente central distribuye a 4 especializados (contactos/contenido/calendario/email); cada uno con su modelo, instrucciones y herramientas propias
- **Enjambre en un solo flujo** [vpyllOeLhs4]: v1.103 de n8n permite todos los agentes en el mismo canvas (sin subflujos), memoria compartida por session-ID, modelos mixtos GPT4.1Mini/Flash/Antropico según rol
- **Padre→hijo con JSON estructurado** [vwlx-e8UYC8]: flujo padre envía JSON al hijo; hijo devuelve solo output limpio; `ver ejecución de sub` para trazabilidad; completión automática de parámetros vacíos
- **Paralelización vs secuencial** [qNW9KaLe1nY]: 4 elementos en 22s (paralelo) vs 51s (secuencial); subflujo con "ejecutar una vez por elemento" + "no esperar finalización"; límite API = cuello de botella
- **Paperclip / agencia autónoma** [HJ-dwefABss]: 7 agentes + 5 tareas, archivos `agent.json`/`heartbeat.json`/`soul.json`/`tools.json`, `$budget` por agente, 48 agentes QA; patrón "empresa IA sin humanos"
- **Advisor/Executor** [1EPsUXSManU]: Haiku como advisor + Opus como executor = 12% más barato, precisión BrowseComp sube 19.7%→41.2%; aplica en tu-tienda para presupuestación de tareas repetitivas
- **Encadenamiento de prompts** [nSQnJoqK4DQ]: esquema→evaluación→escritura usando 20/flash→Mini→CLA3.5; Evaluator-Optimizer: bucle infinito hasta calidad deseada; paralelización (emoción+intención+sesgo simultáneos)
- **DeepSeek R1 como planificador** [tjaD65OCoE8]: R1 (api.deepseek.com/v1) no admite function-calling directo → usarlo solo como planificador chain-of-thought; V3 como agente de herramientas; 98% menos tokens que alternativas
- **→ aplica:** orquestador tu-tienda → subagentes: (1) atención cliente Shopify, (2) email marketing, (3) inventario+pedidos, (4) contenido tu-nicho; session-ID por cliente para memoria compartida

---

## 2. RAG Y BASES VECTORIALES

- **Pipeline RAG completo con Supabase** [cCD303XsUjI]: 1000 chars/chunk, 200 overlap, session-based memory en PostgreSQL; flujo Google Drive→extracción texto→Supabase→agente
- **Pinecone vs Supabase** [wEXrbtqNIqI]: Supabase ideal para proyectos medianos con metadatos relacionales; Pinecone para escala masiva; `text-embedding-3-small` como default; tabla `chat_history` automática
- **Pinecone Assistant** [QojPKL96Dx4]: 1,277 tokens vs 30k para vector store tradicional; $0.05/hora; `include_highlights=true`; umbral >0.4 para filtrado; 5¢/h activo
- **Agentic RAG vs SQL** [BhGaGFH0jR4]: SQL para datos tabulares, vectores para no estructurado; plantilla "Cole Mean" en Supabase; decisión: ¿dato exacto o semántico?
- **Metadatos como clave de precisión** [lnm0PMi-4mE]: metadatos (título+URL+timestamp) en cada chunk; vectorizar solo texto segmentado no todo el contenido; filtro dinámico por URL para eliminar vectores obsoletos; Apify+Supabase+n8n
- **Reranking Cohere** [xWhX61651H8]: `rerank v3.5` filtra 20 vectores → selecciona top 3 (puntuaciones 86/74/73); límite Supabase aumentar a 20 (default 4); umbral post-reranking >0.7; pipeline 2 agentes: uno decide filtro, otro busca
- **RAG con voz** [Je4EAscnKK0]: ElevenLabs+n8n+Pinecone como "Voice RAG"; temperatura 0.8–1.2; Gemini 1.5 Flash como base para velocidad; webhooks dinámicos con parámetros destinatario+contenido
- **→ aplica:** tu-tienda RAG: catálogo Shopify (SKU+descripción+precio) → Supabase vector con metadatos {categoría, colección, precio_rango}; agente responde "¿tienen humidificadores <$50?" con reranking Cohere; elimina chunks al discontinuar producto

---

## 3. GENERACIÓN DE CONTENIDO UGC Y VIDEO

- **Stack completo UGC** [AYsg5gAMWyo]: Google Sheets→V3.1 imagen ($0.02)+video ($0.30)→Sora 2 ($0.015/s vs $0.10/s OpenAI); formato 9:16; Key.ai como gateway
- **Pipeline Flux+Cling+11Labs+Createmate** [BcfjIBd49C8]: Flux Pro $0.06/img → Cling video → 11Labs audio → Createmate $2/pub → Botato 9 redes; $76/mes total; Google Sheets como cola
- **HeyGen Avatar 5** [EbJu9T30nfI]: 30min audio para clonar voz + Remotion + FFmpeg; $4/min vs $35-75/hr freelance; API HeyGen: endpoints `/avatar` y `/voice`, polling status hasta "completo"
- **JSON to Video** [lF2bvXoV-Zg]: Google Sheets → JSON estructura (intro/cierre/texto_N/imagen_N) → JSON-to-Video API; polling 10s hasta "hecho"; 600s gratis; Flux Pro 20 créditos/video; publicación YouTube automática
- **Video ranking lists automatizado** [lF2bvXoV-Zg]: agentes separados (intro/cierre vs clasificación); 11Labs conexión preconfigurada; columna "estado de creación" con filtro "pendiente" evita duplicados
- **Higgsfield + Claude Code** [xn6Z5PYyAIE]: CLI `higgsfield install/auth/agent install`; 617 líneas `advertisingmasterclass.md`; 100+ variantes creativas (curiosidad/contraparte/interrupción/pregunta/estadística); imagen referencia fija = coherencia de anuncio
- **Landing page animada desde video** [q0TgUtj6vIs]: Kling 3.0 stop-motion WebP 100+ frames → FFmpeg → HTML/CSS/JS; NanoBanana+Key.ai para imágenes 16:9 sin sombras; GitHub+Vercel CI/CD; $5-10k por sitio
- **→ aplica:** tu-tienda contenido: producto tu-nicho → Flux Pro imagen → Cling video 8s ASMR → 11Labs voz bienestar → Botato publica en TikTok/Instagram/Pinterest/YouTube; Google Sheets como cola con estado "pendiente/publicado"

---

## 4. CLAUDE CODE COMO SISTEMA OPERATIVO

- **Rutinas y crons** [BlNJFa3Btm8]: tareas programadas 6AM/8:30AM/noon/3PM/weekly; auto-reparación de flujos; log por tarea; loops=por sesión, cron=persistente [OUyfxhFtGCo]
- **Claude.md como multiplicador** [tXtCK66fPj8]: contexto operativo (no documentación); permisos dinámicos para Git/carpetas; 85 comandos disponibles; `/plan`, `/compact`, `/context`, `/cost`, `/ultra-review`; `{slash}insights` = 1500 msgs/30 días
- **WAT framework** [tDGiWn0flK8][saggDHHnmtQ]: Workflows (Markdown SOP) + Agent (Claude) + Tools (Python scripts); `secrets.md` para credenciales; flujo auto-reparable tras error con ciclo mejora continua; VSCode+Claude Code extension
- **GWS CLI** [Wu67lLD8bB0]: bash commands para Gmail/Drive/Docs/Sheets/Calendar/Slides; OAuth2; email prioritization; Slides con brand; útil sin acceso a interfaz gráfica
- **Claude Code + n8n auto-repair** [uUEa6V-FLB8]: flujo error n8n → HTTP request → Claude Code; Enro para túneles seguros; corrige JSON inválido, sintaxis, arrays; integra ClickUp para notificaciones; limitación: no resuelve credenciales caducadas
- **Skills/habilidades** [zKBPwDpBfhs]: skill.md ≤500 líneas; YAML/Markdown; 3 niveles de contexto; skill-creator plugin `/plugins`; 30s para lanzar 4 agentes paralelos; WAT + SOP = receta reutilizable
- **Klouse como asistente ejecutivo** [rlJovzVhlIo]: VPS Hostinger KVM2 (2vCPU/8GB) + Cloudbot; `soul.md`+`user.md`; cuentas dedicadas; flujos diarios automáticos YouTube/Twitter 7AM; $50/mes (~$200 con plan Max); ~$223 en 3 días con Opus 4.5
- **→ aplica:** tu-tienda Claude Code: rutina 6AM = revisar órdenes Shopify + analizar stock; 8:30AM = email summary clientes; noon = generar contenido redes; skill `tu-tienda-product-content` con brand guidelines + tone bienestar

---

## 5. AUTOMATIZACIÓN EMAIL, CRM Y LEADS

- **Clasificador Gmail 4 categorías** [HN0oWxbF2bM][x1tam0Fhymc]: GPT-4o etiqueta cliente/finanzas/alta-prioridad/promo; etiquetas preconfiguradas con colores; 10 correos/s, 95% precisión; <15min configuración; acciones diferenciadas por etiqueta
- **Agente email con memoria** [6DLZK7XDOGo]: LLM + buffer 5 msgs + Gmail tool + Google Sheets contacts; subflujo Gmail con filtros fecha dinámicos + Google Contacts query [Q4iEslmyMyM]
- **Human-in-the-loop sales email** [FcAAlOw6KZ8]: AirTable trigger → Claude 3.5 Sonnet → Telegram feedback → Gmail send; 23% más rápido, +142% conversión; bucket approve/reject con comentarios
- **Human-in-the-loop X/Twitter** [CdnR-fNVPKI]: Tavily+GPT41 → Telegram approval gate → iterative revision loop; no publica sin aprobación humana
- **Onboarding automatizado** [Wpwbm3zCymk]: form → GPT-40 email personalizado → Google Sheets + Slack; 15-20min ahorrados/cliente; genera hoja de ruta PDF con ReportLab+matplotlib
- **Lead qualification** [fz1RduhHeks]: Google Sheets + OpenAI criterios (decision-maker + ≤45 empleados); `JSON.parse()`; flujo paralelo mensaje personalizado; espera 1-15min post-form [fWtXJswvUcA]
- **VAPPY voice lead qualification** [BO-jFbN4p8Y]: form→normalizar teléfono→llamada saliente→polling→Google Sheets; GPT 4.1 como modelo voz; validación nombre/email/teléfono; MCP backend sin IA para reducir latencia [y-cq_Qo4zVo]
- **Post-reunión → propuesta** [KGXFkUlBHxw]: Fireflies transcripción → polling espera resumen → Google Sheets → Slack confirm → agente genera propuesta → Gamma API para slides; `meeting_id` como ID sincronización
- **→ aplica:** tu-tienda email stack: Gmail trigger → GPT-4o clasifica (soporte/pedido/proveedor/spam) → para soporte: agente con RAG catálogo responde borrador → Telegram aprobación → envía; lead tu-nicho: form → espera 5min → email personalizado con producto recomendado

---

## 6. SCRAPING Y EXTRACCIÓN DE DATOS

- **Firecrawl** [3Pim6uCASSE][4efAzBiTeVo][Ee9WtEEd300]: extract/crawl/map/search API; wildcard crawl; curl→n8n; 1700 job listings→200 CSV; 500 créditos gratis; código `herk10`; site: operator para filtrar dominios
- **Apify** [gZ_RLC25gCw][lnm0PMi-4mE]: 4500+ actores; Google Maps 50 resultados/19s; TikTok hashtag 25 videos; transcripciones YouTube con timestamps; código `30NateHerk` = 30% descuento
- **Google Maps email scraper** [NzMNuuS5JbI]: 97 queries → 814 emails; regex filtering; espera 6s entre requests; try/catch para errores 429
- **Twitter/X API** [lEo7IAgj0UY]: $0.15/1000 tweets; paginación con cursor dinámico; 3 pasadas = 58 tweets; exporta ID/URL/contenido/likes/retweets/replies/views/fecha a Google Sheets; `$count` y `$cursor` como variables JSON
- **Playwright + Claude** [J-6pnl5DQg8]: QA automation 12 preguntas multi-página; sesión persistente con perfil de navegador; detección visual por color de iconos; headless/headed según caso; loop: ejecutar→detectar→corregir→probar
- **LinkedIn scraping** [R36bpNPPIMs]: Google Search `site:linkedin.com/in/ (puesto) (industria) (ubicación)`; encabezado `User-Agent: Mozilla/5.0`; parseo HTML con `querySelectorAll('a')`; paginación `inicio=10`
- **→ aplica:** tu-tienda scraping: Apify actors para TikTok trending #tu-nicho + #Wellness → análisis con GPT-4o → ideas contenido; Firecrawl competidores Amazon/Shopify → precios → ajuste automático en Google Sheets

---

## 7. MCP, CONECTORES Y SEGURIDAD

- **n8n MCP nativo v1.88** [VTEg8uJ4yxo]: activador MCP + cliente MCP; 10 custom tools; webhook URL producción; community nodes v1.94+ (Tavily/11Labs oficiales)
- **Claude Code + MCP + n8n skills** [B6k_vAjndMo]: 1100 nodos, 99% precisión, 2700+ templates; newsletter automation; MCP como capa de extensión para herramientas externas
- **Servidor MCP arquitectura** [m0YrxLnFPzQ]: MCP traduce entrada LLM → parámetros API REST; esquemas dinámicos por herramienta; Fir Crawl Extract + Airtable + Perplexity como herramientas MCP; plataforma híbrida con múltiples servidores
- **Vappy + NADN MCP backend** [y-cq_Qo4zVo]: 7 flujos en MCP (búsqueda cliente/CRM/disponibilidad/eventos/actualización); sin IA en backend = menor latencia; Bearer token en header; transferencia de llamadas con "Handoff"
- **Seguridad en n8n** [oWdJMJp2HgM]: nodos nativos: jailbreak detection (umbral 0-1), PII detection (98% precisión), NSFW filter, keyword blocking, URL filtering (HTTPS/ftp), text sanitization antes de LLM; expresiones regex personalizadas
- **Webhook security** [xxARTGo_Oqg]: HTTPS + firmas de tokens; límites de velocidad; cliente genera su propia clave API; canal seguro para transferencia (Slack/ClickUp/link uso único); cliente = dueño de credenciales
- **Contexto de ingeniería** [wq001sxDTWw]: 6 componentes: entrada usuario + sistema + memoria + RAG + herramientas + salida estructurada; memoria corta = ventana 3 interacciones + session-ID; memoria larga = gráfico usuario persistente entre sesiones
- **→ aplica:** tu-tienda MCP: Claude Code ↔ MCP server n8n; herramientas: `buscar_pedido`, `actualizar_inventario`, `enviar_email_cliente`, `publicar_producto`; sanitizar PII antes de enviar a LLM (datos tarjetas, emails clientes)

---

## 8. PUBLICACIÓN MULTI-RED Y GESTIÓN CONTENIDO

- **Botato/Blot 9 redes** [QovlUE_VlWQ][RvuPRX-b7Lc]: YouTube/Instagram/TikTok/X/LinkedIn/Facebook/Threads/Pinterest/BlueSky; Google Sheets trigger; nodos nativos; header `blot-api-key`; rotación contenido (7 activos max); $76/mes total
- **Newsletter multi-agente** [HUdm3NXwk-w]: 5 nodos (experto+planificador+researchers+editor+título); Tavily+Claude 3.5; HTML output; 6 secciones; boletín semanal [pxzo2lXhWJE]: Tavi x2 + NIDAN + Gmail; disparador domingo 00:00; Split Out por tema
- **Publicación multi-plataforma desde Sheets** [u2Tuu02r7QI]: tema+audiencia → 3 posts (LinkedIn profesional / X corto / blog estructurado); Tavily API para RAG en tiempo real; disparador automático al agregar fila
- **LinkedIn automation** [ACkHpQQnfxQ]: Tavily + OpenAI DALL-E $0.17/img; Createmate para publicación; posts automatizados con imágenes
- **Campaña automática con Google V3** [RvuPRX-b7Lc]: 3-10 veces/día; 7 objetos en Sheets como base de ideas; agente ideas genera nuevos objetos+pie; V3 Cling 2.1; $6/video 8s; audio ASMR $0.75/s; 35k+ views/día
- **Contenido diario con Apify+HeyGen** [llm60n03x3c]: noticias diarias via Apify → guión dinámico → HeyGen avatar video; polling 30s inicial → 5s loop; producción x20 vs manual
- **→ aplica:** tu-tienda publicación: Google Sheets con productos tu-nicho destacados → agente genera copy por red → Botato publica en 9 redes; newsletter semanal bienestar: Tavily busca tendencias → Claude redacta HTML → Gmail envía domingo 8AM

---

## 9. SELF-HOSTING, MODELOS Y OPTIMIZACIÓN COSTOS

- **Self-hosting n8n** [6ZB0zADNaqk]: VPS $6/mes vs $25 cloud; Docker Compose; backup automático; código Hostinger `NateHerk` = 10% descuento; Cloudflare tunnels para HTTPS público [cZQPDLgPtNg]
- **Ollama local LLMs** [DcEMf2K6cPQ]: Docker+Ollama; Llama 3.2 / DeepSeek / Qwen; ≥14B parámetros para agentes; sin costo API; latencia local
- **OpenRouter gateway** [A0OwvNOLNlw]: clave API única para DeepSeek/Gemini/Sonnet/GPT-4; DeepSeek R1: $2.19/M tokens salida (vs $60 OpenAI O1 = 96.4% ahorro); O2k_qwZA8HU: Qwen 3.5 9B via Ollama, 64k contexto, $10=1000 req/día
- **Cache estratégico** [6cEQEba0i2A]: TTL 5min API vs 1h web; 10% reducción costos; handoff de sesión sin perder cache; Superpowers plugin 9% reducción costo, 14% menos tokens [4XqVR6xI6Kw]
- **CLI vs MCP token overhead** [49V-5Ock8LU]: CLI vs MCP = 18k tokens/mensaje menos; `/clear` entre tareas; group instructions; status line; optimizar context %
- **Tablas de datos n8n** [QCjMBOEhpLE]: 2 rows = 11ms vs 1600ms Google Sheets; 20 rows = 97ms vs 1700ms; usar para datos de alta frecuencia de consulta
- **Key.ai como router modelos** [GY-kAiZGLOw]: GPT Image 2 ($0.06 fijo) vs NanoBanana 2 ($0.04-0.09); modelos de imagen/video/voz desde un punto; Sora 2 a $0.015/s
- **Modelos comparativa** [WX4rp-vP3zo]: GPT 5.5 vs Opus 4.7: 82.7 vs 69.4 Terminal Bench; 50% más rápido; $<3 vs ~$5/run; Fable 5 [dYrrEKXtttk]: $10/M input/$50/M output; gratis hasta junio 22; más rápido que Opus 4.8+GPT5.5
- **→ aplica:** tu-tienda infra: n8n self-hosted VPS Hostinger $6/mes; Cloudflare tunnel → dominio `tu-tienda-automation.com`; OpenRouter para todos los LLMs; cache 1h para prompts de catálogo que no cambian; tablas n8n para session-state en lugar de Sheets

---

## 10. EVALUACIÓN, OBSERVABILIDAD Y ERRORES

- **AI evaluation framework** [-zFd1nPn6U0]: 5-750 muestras test; Google Sheets tracking (entrada esperada/respuesta real/puntuación); 90%→59% accuracy decay = señal reentrenamiento; variar una variable por prueba para aislar impacto
- **Observabilidad LLM** [vVdS-ZEFf50]: "devolver pasos inmediatos" para capturar intermedios; JavaScript limpia JSON; Google Sheets registra timestamp/flujo/entrada/salida/acciones/costo total; rama error vs éxito separadas
- **Tablas de datos como logger** [lcNN3X9gXls]: campos timestamp+flujo+entrada/salida+tokens+acciones; menús desplegables para modelos (evita errores manuales); sincronización diaria Google Sheets → tabla n8n; registrador errores con nodo+mensaje+flujo
- **Error handling n8n** [Ctr89Q2Nei8]: `continue on error`; operadores `?` vs `|`; child agent para validación/retry; flujo de error nativo → notificación email/SMS; activador nativo de errores para workflows
- **n8n tips productividad** [zMy5yoA-ub8]: fijar datos con `P`; simular datos con lápiz; desactivar nodo con `D`; notas adhesivas `Shift+S`; renombrar `F2`; historial versiones; `Tab` para nuevo nodo; `{{now.format("YYYY-MM-DD")}}`; variables `{{flow.id}}`
- **Migración flujos n8n** [t1PTmpas0bg]: API n8n + Google Sheets; estado "procesar/procesado"; exportar JSON completo (nodos+conexiones+params); dos API keys (origen+destino); sin transferencia credenciales/usuarios
- **→ aplica:** tu-tienda observabilidad: cada agente registra en Google Sheets {sesión, producto_consultado, respuesta, tokens, costo, resultado}; alerta Telegram si tasa error >5% en 1h; test semanal 50 muestras con preguntas reales de clientes

---

## 11. MODELOS DE NEGOCIO Y VENTAS DE AUTOMATIZACIÓN

- **Pricing por valor** [8C6iCpJ9HPo][wIcw0T9NhZM]: $1200 para 2h automation que reemplaza 10h/semana; fórmula: (horas_ahorradas × tarifa_hora × semanas) × 10-40% = precio; contratos recurrentes $1.5k-15k/mes; pago por hitos no por horas
- **Ladder consulting** [Pi-m8R068r4]: $50-99/hr → $500-2500 audit → $2.5k-10k proyecto → $3k-10k/mes retainer; LRP framework: Escuchar+Repetir+Empujar; oferta zero-risk: no pago hasta resultados [XB2xmX3USUI]
- **BUILD + SCAN frameworks** [Q46OLxFshAQ]: demo 60s; ahorro $140k/año como anchor; diagnóstico + cuantificar horas perdidas + propuesta; evitar "sofisticación trap" (5 proveedores sin necesidad)
- **Agencia vs producto** [VzOYty0siaM]: B2C YouTube+community+courses=$231k/mes; B2B $5k-50k/proyecto; valuation 5-10x revenue [$6M→$30M] [8ktcSaSTvxk]
- **→ aplica:** tu-tienda servicios: ofrecer setup agente email tu-tienda a otras tiendas Shopify tu-nicho ($2.5k setup + $500/mes mantenimiento); caso de estudio: "automatizó clasificación 300 emails/día, ahorra 15h/semana"

### 12l · MDA Latam (pase completo _LOCAL) — FULL-PASS 2026-06-21
*(canal destilado ~183 videos; Nano Banana + Higgsfield + Claude reels + CapCut; supera §11c parcial; ref: `_archivos_trabajo/_destilados/mda_latam_p1..p6_LOCAL.md`)*


**Generación visual IA para producto (Higgsfield / Gemini / Grok / Ideogram)**

[rCScGlJiY3k] · [PHT3K7z93YQ] · [vaBODH5zEE8] · [ZnQKdhUhNeI] · [jciWZL_lPJU]:
- Gemini + Yemini para composiciones de producto en contextos realistas: prompt *"colócalo en un dormitorio"* o *"crea imagen de este humidificador en sala cozy"* → genera escenas de decoración para listings y reels sin fotografía propia. → aplica: banners de producto tu-tienda (proyectores, lámparas, aromaterapia) en ambientes cozy-US.
- Ideogram + prompts detallados para logos e imágenes de marca: *"Logo para tu-tienda, estilo moderno, tonos cálidos, tu-nicho cozy, minimalista"*; copiar prompt entre plataformas para variantes rápidas. → aplica: creativos de anuncio y thumbnails sin diseñador.
- Grok (herramienta Grock): genera video, imagen, audio y animaciones en minutos desde texto; ejemplo citado "mujer abrazando lobo desde carro" en 30 s. → aplica: vídeo-anuncio de ambiente cozy para Meta/TikTok en <4 h con 2 personas.
- Extensión IPRM en Chrome: genera prompts hiperdetallados automáticamente (ej. "fotografía hiperdetallada de producto en sala iluminada con luz cálida"). → aplica: mejorar calidad de imágenes IA de tu-tienda en una pasada.
- Luca / Lucas AI: logo + guía de marca + kit redes sociales en minutos, costo cero hasta satisfacción; entrega tarjetas, formatos redes y web. → aplica: identidad visual de tu-tienda sin presupuesto de diseño.
- DALL·E 4.0 (GPT premium): imágenes 3D y estilo Disney integrado. → aplica: creativos de temporada (Halloween, Navidad cozy) para tu-tienda.

**Producción de reels y video con CapCut (efectos, transiciones, subtítulos)**

[0hn8R3v3WMQ] · [KRf5qIky2QQ] · [NJgVZw4aNIE] · [WXo55dEtrqE] · [jBBm6TSkI9A] · [jHFae0KAVEY] · [ocp6kfnphfc] · [SyXdICBOBQ8] · [sdcrZWhXc6o] · [turI-LqWWVc] · [pWnrZtZUGmk] · [plMn6nqurtc] · [zIPG6wbA6FQ] · [XcOmayUgR44]:
- Timelapse + superposición CapCut: graba clip 30 min de fondo sin persona → superpone clip activo corto → máscara horizontal para difuminar línea de horizonte → velocidad 2x/3x en clip principal. → aplica: mostrar setup de tu-nicho o cuarto cozy "armándose" en 15 s.
- Efecto "congelación/detener el tiempo": dos clips (objeto + acción) → alinear objeto debajo del video principal → máscara + dividir → congelar fotograma clave → revertir fragmento siguiente. → aplica: destacar funcionalidad de termostato o lámpara en mid-air.
- Efecto levitación mágica CapCut: croma key (tela verde o cartulina) opacidad 70 → 100%; sincronizar movimiento exacto entre clips; ajustar intensidad y sombras cromáticas; subir velocidad del último fragmento. → aplica: producto "flotando" para reels de producto tu-tienda.
- Clones automáticos (efecto velocidad automática): estilo "marco congelado" → clonar figura con efecto dispersión de partículas → trípode obligatorio → aumenta retención visual +30% (dato TikTok). → aplica: apertura de reel de producto con efecto wow.
- Efecto clones con keyframe: duplicar video → eliminar fondo → 3 capas superpuestas → keyframe capas 2 y 3 moviéndose izq/der en 5 cuadros → fade in/out 0.5 s. → aplica: mostrar variantes de color de producto simultáneamente.
- Subtítulos dinámicos automáticos CapCut: importar → subtítulos automáticos → personalizar fuente/color/sombra/animación → "Aplicar a subtítulos automáticos" para aplicar globalmente → audio claro para precisión. → aplica: subtitular tutoriales de producto tu-tienda en español e inglés para US.
- Efecto "sacar objetos" (superposición PNG + timing): recortar fondo con Remove.bg o Figma → superponer PNG sincronizado → ajustar "king frame" al ritmo del movimiento → storytelling visual para lanzamientos. → aplica: mostrar catálogo de iluminación saliendo de caja.
- Transición de cruce: dos clips (caminar hacia cámara + cruce) → recortar clip 1 antes del paso → velocidad al final del 1 y principio del 2 → empalme fluido sin efectos complejos. → aplica: transición de "antes/después" de ambiente cozy.
- Efecto "volar" con keyframe: grabar salto + fondo vacío → eliminar fondo del clip salto → keyframe timeline → sincronizar sobre clip vacío. → aplica: "transición mágica" para debut de producto nuevo.
- Transición de texto dinámica: grabar 10 s caminando → exportar con texto → nuevo proyecto → superponer sin título → máscara + girar 90° → mover línea al ritmo de caminada. → aplica: intro de reel educativo sobre tu-nicho.
- Croma key "hombre invisible": tela croma + iluminación uniforme → saturación verde 30–50% → herramienta Croma Key + ajuste de intensidad → fondo neutro/blanco para destacar producto. → aplica: efecto donde la mano sujeta el producto sin cuerpo visible.
- Croma key con cartulina verde: dos videos (influencer + cartulina) → misma duración → silenciar audio → intensidad croma ~40% → efecto "malla" → ratio 16:9 HD. → aplica: mostrar producto tu-nicho en manos con fondo reemplazado por escena cozy.

**GPTs personalizados y prompt engineering para contenido de marca**

[fyb82UFKAlg] · [xqcpCq9oPkg] · [vaBODH5zEE8] · [wPng0VG1hDk] · [rXqYaYSMMu0] · [jy3Jeq0ox7M]:
- Crear GPT privado entrenado con base de conocimiento (hasta 20 archivos / 512 MB): instrucciones precisas de rol, tono, formato (Reels → Hook + mensaje rápido + CTA; Carrusel → 10 slides storytelling + CTA); desactivar internet y DALL·E para respuestas solo desde el corpus. → aplica: GPT de marca tu-tienda que genera descripciones de producto, reels scripts y emails en tono cozy-US.
- Framework de prompts: Contexto + Tarea + Instrucción + Clarificación + Refinamiento → tasa de éxito sube de 25% a 90% (dato canal). Ejemplo tu-tienda: *"Eres experto en dropshipping tu-nicho US. Crea descripción SEO de 150 palabras para humidificador aromático, tono cozy, sin jerga técnica."*
- Role Prompting: *"Eres un experto en investigación de mercados para bienestar doméstico"* → mejora precisión del output; complementar con mapa de empatía (¿qué ve, escucha, siente el prospecto?). → aplica: generar buyer personas US para tu-tienda.
- GPT por formato específico (un GPT por formato): Reels, Carrusel, Stories → mayor precisión y menor "drift"; afinamiento crítico: "esto sí / esto no" por iteración diaria.
- Predis: integra ChatGPT + Canva + Hotsite → crea posts, carousels, reels y programa publicaciones en redes; Escríbelo: 30 artículos SEO/mes automáticos + plugin WordPress. → aplica: publicación automatizada del contenido tu-tienda en redes.
- Extensión IPRM (Chrome) para prompts optimizados de imagen. Poe: acceso a múltiples LLMs en un solo pago mensual para asistentes personalizados.

**Automatización de contenido: Heyen / Nano Banana / HeyGen / Notebook**

[33rZ7x2DDRo] · [LC57VzZkUWQ] · [j2NEQAkge0Y] · [ilg3EwVeLsc] · [bSO9F2GWT_0] · [Y2m40hM0AoI] · [cPS3cyZ3WTc]:
- Heyen (Heyer): grabar 2 minutos de voz + cara + gestos → generar 100 h de contenido de video automatizado para YouTube, Instagram, TikTok, Hotmart sin grabar. → aplica: crear biblioteca de tutoriales de producto tu-tienda (instalación de smart plug, uso de proyector) sin cámara recurrente.
- Notebook / Google NotebookLM: subir PDF (plan de negocios, catálogo) → genera resúmenes, mapas mentales, infografías, presentaciones, podcasts en minutos. → aplica: convertir el catálogo tu-tienda o brief de temporada en contenido multiformat para redes.
- HeyGen + Learning Studio: convertir curso/guion en videocurso profesional en 1 clic; Wonder Dynamics: películas IA sin cámara profesional → 100 h de contenido visual único. → aplica: serie educativa "tu-nicho en 5 pasos" para YouTube tu-tienda.
- Rask: traduce videos a cualquier idioma → expansión global. → aplica: subtitular reels en inglés para audiencia US sin grabar de nuevo.
- Framework "1 minuto–2 minutos": crear curso + convertir en video = modelo escalable; $13k–$135k en YouTube + $568k en Hotmart (cifras reales del canal). → aplica: monetizar el conocimiento tu-tienda sobre tu-nicho como infoproducto paralelo.
- Suno: canciones personalizadas con letra y tema definidos → branding musical. ElevenLabs: clonar voz (plan $5/mes–$100 empresarial) → agente de voz que atiende y vende 24/7 en múltiples idiomas con script denso (precios, FAQ, objeciones). → aplica: asistente de voz tu-tienda para llamadas de soporte automatizadas.

**Agentes IA y automatización de ventas/WhatsApp**

[Kf9dlB_K29o] · [NOrKE4jjd70] · [GUonKYViOP0] · [0-tqM3_YpJ4] · [calqAPxgc2g] · [LFT9eXWEhsE] · [jzOD2X2qf_s] · [RoogERM6Huo] · [W5fpNyJEd28]:
- ElevenLabs + script denso: entrena al agente con todos los mensajes posibles (precios, promos, objeciones, FAQ) → simulación de conversación natural en llamadas → no es chatbot sino asistente de llamada. → aplica: agente de voz tu-tienda que responde consultas de producto tu-nicho en inglés 24/7.
- ManyChat (partner oficial Meta): automatiza comentarios Instagram (3 variantes de respuesta), reacciones a historias (emoji → secuencia automática), redirección a YouTube/email/WhatsApp desde un solo flujo. Activar: Configuración > Privacidad > Mensajes > activar envío a terceros. → aplica: publicar reel tu-tienda con CTA "comenta COZY" → envío automático de link de producto.
- Mini Chat (Telegram): bot con bienvenida personalizada + imagen + video + difusión masiva simultánea → fidelización y promociones a todos los usuarios. → aplica: canal Telegram de tu-tienda para notificaciones de drops y descuentos.
- WhatsApp Business API vs App: API permite envío masivo ilimitado + cuenta verificada (chulito verde) + plantillas preaprobadas + ventanas de 24 h; costo por conversación, no por mensaje; número dedicado nuevo. Plataformas: Twilio, Semia, Gashop, Watty.io, Guati. → aplica: canal oficial tu-tienda US con automatización de post-compra y recuperación de carrito.
- CRM multicanal (Clientengo / plataformas de chat): centraliza WhatsApp, Instagram DM, Telegram, Facebook en un dashboard; pipelines por canal; etiquetas Caliente/Tibio/Frío; asignación automática de leads; métricas tiempo de respuesta y tasa de conversión. → aplica: gestión de leads tu-tienda desde un solo panel.
- Disparadores conversacionales: palabras clave ("quiero algo") activan flujos → reduce tiempo de atención 65%; temporizadores de 3–4 s entre mensajes para naturalidad; validación de email automática en flujo. → aplica: flujo tu-tienda donde "smart light" activa catálogo + precio + CTA pago.
- N8N + Make: 44 workflows en 3 días de formación; automatiza tareas 24/7 (landing pages, logos, imágenes, publicaciones, análisis de competencia, emails). → aplica: workflow que al recibir lead → crea tarea en CRM → envía secuencia WhatsApp → notifica a Shopify.

**Estrategia de contenido en redes sociales (parrilla, formatos, scheduling)**

[SMpx_yHLOck] · [Y4w4D-ycV8I] · [n1aFIq9e134] · [LhAYmXM5kf8] · [e-gEFrfKNVg] · [u7Xc2faK5PY] · [tAj5vBP0xMM] · [YyQlgq1uSaA]:
- Framework "Categorías x Día": Lunes Inspiración (20–25% engagement) | Martes Educativo (30–40% retención) | Miércoles Comercial (10–15%) | Jueves Informativo (25–30%) | Viernes Entretenimiento/Meme (15–20%). Mix recomendado: 40% educativo, 30% informativo, 20% comercial, 10% entretenimiento.
- Ciclo semanal de producción: Lunes → tendencias Google Trends + AnswerThePublic + hashtags; Martes → textos y guiones con CTA; Miércoles → grabación/video 15 s de valor; Jueves → gráficos Canva (vertical 9:16); Viernes → edición con transiciones + música; Sábado → scheduling Buffer/Later en horarios 9–12 AM y 6–8 PM. → aplica: lanzar 7 días de contenido tu-tienda en una sola jornada.
- ChatGPT + Canva batch: tabla 2 columnas (Tip + Emoticono) → Canva conecta automáticamente → 10 publicaciones listas en 1 minuto. → aplica: serie "tu-nicho Tip del Día" para Instagram tu-tienda.
- Formatos por plataforma: Instagram Reels 1 min 1080×1920 / Stories 15 s / Carrusel ≤10 imágenes; YouTube Shorts 15–60 s para viralización; TikTok video ≤60 s + historia + audio; LinkedIn PDF/video consumo horizontal. Carrusel 3240×1080 en Canva (3 columnas de 1080 px) → Image Splitter para separar. → aplica: adaptar cada pieza tu-tienda a cada formato en un solo flujo de producción.
- Content pillars tu-tienda: 3–5 temas fijos (#tu-nicho #CozyLife #WellnessLiving #DropshippingTips) → micro-momentos (<15 s) + CTA claro + regla 80/20 (el 20% de posts genera el 80% del engagement → identificar con Instagram Insights).
- Obsequios digitales como lead magnet: PDFs "top 5", guías descargables → +40% de retención; activar con palabra clave en DM (ManyChat). → aplica: "Guía gratuita: 5 gadgets tu-nicho para dormir mejor" para captar emails tu-tienda.

**Ads pagados: Meta / TikTok / Google (campañas, segmentación, métricas)**

[DYnlF7P5GGQ] · [7UtLfqJgSQI] · [bFsJsH14o-4] · [gBzlFEn1w2U] · [kgzJXLGbRfs] · [aUnNY1i2Mss] · [lrWi8NR8qEE] · [weZygjJ5-xE] · [c3Fdp6PrCrQ] · [EVV1GMvNYD8]:
- Estructura de campaña Meta: 1 campaña → conjuntos segmentados por interés (tu-nicho, wellness, cozy living) + comportamiento → 3–5 variantes de anuncio por conjunto; presupuesto diario $5–$10 inicial (PMV), escalar en 14 días; rotación inteligente para evitar saturación; desactivar conjuntos con ROI <1.5×.
- Carousel Ads: +30% ROI vs. estático; mostrar múltiples productos en un anuncio; Video Ads <15 s para captar atención rápida. Retargeting: 20–30% del presupuesto para usuarios que vieron producto sin comprar (10× más probabilidad de conversión). Lookalike Audiences de compradores: +25–40% de leads.
- LeadInFrost ($99/mes): captura seguidores de competidores en Instagram/Facebook → exporta como "público personalizado" en Ads Manager → +20–30% de conversión vs. segmentación genérica; combinar con intereses (ej.: "tu-nicho" + seguidores de @competidor). → aplica: audiencias tu-tienda desde competidores de home automation US.
- TikTok sin estar en EE.UU.: usar TikTok for Business (no app principal) → Pixel + GA4 para tracking → presupuesto mínimo $20 → segmentar por intereses + interacciones con hashtags + dispositivos → opción "Automática" para que TikTok optimice; integración directa con Shopify por SKU.
- Google Ads Smart Bidding "Target CPA" / "Maximize Conversion Value" → remarketing listas dinámicas de carrito abandonado (+20–35% conversión); extensiones de llamada directa (+30–45% conversión móvil); long-tail keywords "tu-nicho products near me"; campañas display + búsqueda combo (+30% leads).
- Anuncios Meta: objetivo "Visitas a página de destino" → IA de Meta identifica usuarios potenciales; excluir usuarios que ya interactuaron; ubicaciones manuales: solo "Historias" y "Superposición de Ríos"; presupuesto inicial $5 para probar → escalar con datos. KPIs target: CTR >2%, CPC <$0.50, CVR >4%, ROAS >3×.
- Framework de optimización: 7 días prueba → ajuste diario → 14 días escalamiento. A/B testing: mínimo 3 variantes por campaña (copy, imagen, CTA); "Compra ahora" vs "Descubre tu hogar inteligente".

**SEO, analytics y conversión (GA4, Shopify, UX)**

[HEBL2ti_RdY] · [cEIdmPLFQvM] · [II5M3n0oh50] · [YbVEJP0BqoA] · [1jDhxWwwcEk] · [K1s8FfXPjZ0] · [qyHIJhV6hOA]:
- GA4 en Shopify: custom events ("click en botón de compra", "view_item", "carrito abandonado") + user properties para segmentar; conversion funnels "visita → filtro → carrito → pago"; predictive metrics para anticipar demanda; A/B testing integrado. → aplica: medir qué productos tu-tienda generan más add-to-cart sin compra para priorizar remarketing.
- SEO on-page: título + meta descripción = "snipe" de Google; PageSpeed Insights + Test My Site para velocidad móvil (<1.5 s target); AMP para móvil (+tráfico); keywords long-tail "tu-nicho for bedroom", "cozy living room gadgets US"; Google My Business para presencia local; content marketing framework 4 semanas: Texto → Infografía → Video → Podcast.
- UX / navegación tienda: menú ≤3 clics a pago; carrito visible en tiempo real; hero section con CTA + video corto; product page 3–5 imágenes + video + reseñas + FAQ; checkout 1–2 pasos (68% abandono de carrito según Shopify stats); tiempo de decisión del usuario <3 segundos → diseño limpio + CTA visible desde el primer segundo.
- Framework RFM (Recency, Frequency, Monetary) para segmentar clientes → email marketing 70% comunicación de valor + 30% promoción; cadenas progresivas con datos incrementales; personalización por producto comprado (luz LED → emails sobre iluminación cozy). → aplica: segmentar base tu-tienda por categoría (iluminación, aromaterapia, proyectores) para cross-sell.
- Shopify Flow: automatizar pedidos, facturas y seguimiento sin intervención; SMS/WhatsApp para notificaciones automáticas post-compra; dropshipping KPIs: tiempo de entrega <48 h, costo logístico <15% del precio de venta, conversión landing page 15%.

**Producción audiovisual IA: Sora / Lovable / Farbase / Wonder Dynamics**

[7rJDkYEcVdg] · [Bdxl8WKlEGE] · [FnEqfnxW7sE] · [pj47PU2SpEI] · [rOvyapArtl4] · [j2NEQAkge0Y] · [snI-J9dmTMY]:
- Sora (acceso con BPN/VPN US): generación de video IA avanzada; acceder cambiando país en App Store a EE.UU. o usando Surfshark/Shark. → aplica: clips de ambiente cozy tu-nicho para anuncios tu-tienda sin grabar.
- Lovable + Shopify: landing pages en 10 min con lenguaje natural ("quiero un video en la parte derecha", "cambia colores a negro y naranja"); conecta con Shopify en 2 clics (claim) sin cambiar DNS; chat IA flotante personalizable; planes desde $25/mes; multi-dispositivo en diseño. → aplica: landing page de producto tu-tienda para campaña de temporada en <1 h.
- Farbase (Firebase + IA): crear apps con lenguaje natural ("créame una app para diagnóstico de bienestar") → botón "autogenerar" conecta a API Google/ChatGPT; herramienta Stitch para apps con paletas visuales y edición en tiempo real. → aplica: app de quiz "¿Qué tan smart es tu hogar?" como lead magnet para tu-tienda.
- Comerciales en 4 horas con 2 personas usando IA: proceso → guion IA → imágenes/video IA → narración ElevenLabs → edición → publicar. Costo vs. agencia tradicional: 10× más barato. → aplica: tu-tienda puede producir 5–7 creativos semanales con este flujo.
- Wonder Dynamics: películas IA sin cámara profesional → 100 h de contenido visual único. Landing Sites AI: landing page rápida con IA. Gama.app: presentaciones profesionales sin PowerPoint (ahorra 3–5 h/proyecto). → aplica: material educativo y pitch tu-tienda para inversores o partners.
- Plan de contenido 7 días integrado (canal [snI-J9dmTMY]): Día 1 Estrategia 360 + IA; Día 2 SEO y distribución; Día 3 Marketing de video e IA; Día 4 Automatización y WhatsApp; Día 5 YouTube y autoridad; Día 6 Pauta y redes sociales; Día 7 Resumen y automatización. → aplica: estructura de sprint de contenido tu-tienda mensual.

**Agentes IA avanzados: Operator / Gemini / Claude / GPT-mode agente**

[PD_cTMKJyyI] · [YeRfGw1estA] · [nmv3aRqHRZo] · [wPng0VG1hDk] · [T28iylMqY1Q] · [p2EmawgFQRU]:
- Operator (ChatGPT modo agente, solo US/VPN): analiza 50 publicaciones de Instagram de competidores → identifica temas con alta interacción → genera tweets/posts → puede publicar automáticamente; captura leads por voz y envía datos a Google Drive en tiempo real; busca precios de tickets, productos, opciones en real-time. → aplica: análisis de competidores tu-tienda en tu-nicho US + generación automática de contenido.
- Gemini 1.5 Pro: resultados detallados en investigación (precios, duración, requisitos); multimodal (texto, audio, imagen, video como entrada/salida); LoRA + fine-tuning para adaptar a tienda específica; 1M tokens de contexto. → aplica: análisis de mercado US + generación de descripciones de producto tu-tienda en inglés.
- Vectorización de productos: embeddings 36 dimensiones (ajuste, estilo, durabilidad, tendencia) + redes neuronales → recomendaciones personalizadas; chatbots entrenados con corpus propio (500k palabras) como experto interno 24/7. → aplica: recomendador de productos tu-tienda "también te puede gustar" basado en comportamiento.
- Cloud / Claude: ventana de contexto >200,000 tokens (vs. GPT 256k tokens, Gemini 1M); español usa hasta 3× más tokens que inglés → procesar en inglés para mayor eficiencia. Habilidades personalizadas (mejor en marketing, copywriting, diseño Canva) + Notebook para investigación + extracción de contenido. → aplica: asistente interno tu-tienda entrenado con catálogo + guías + políticas.
- Amazon Bedrock: modelos personalizados para análisis de clientes, automatización de ventas, inventario predictivo. → aplica: análisis de demanda por categoría tu-tienda para optimizar catálogo.

**Branding de producto, copy y posicionamiento US-first**

[3IJhaaSd0_o] · [H9eO5ZrDyAg] · [MQFRYUvOQFI] · [HjzalGIBdZ8] · [ydXDm5bZs98] · [TRd7T_14wfg] · [ACyCF8XlgF8]:
- Copywriting específico vs. genérico: "ahorra hasta 30% en electricidad con esta luz LED" >> "mejora tu hogar"; 500 mensajes/día en 1974 → >5,000 hoy → solo se recuerdan 54 → mensaje debe ser memorable y resolver un problema concreto. Framework 9 premarcos: dolor emocional/mental/físico, necesidad diaria, deseo específico.
- AIDA para reels y anuncios: Atención (hook 3 s) → Interés (dato/beneficio) → Deseo (prueba social/demo) → Acción (CTA claro). 4P + BAP: Promesa + Panorama + Prueba + Impulso; Antes + Después + Ahora. → aplica: estructura de cada reel de producto tu-tienda.
- Posicionamiento emocional US-first: pilar emocional ("más tiempo libre, menos estrés") + pilar técnico (Shopify, datos, automatización) + pilar identitario ("tu-nicho que se siente como hogar"). Keywords SEO: "tu-nicho USA", "cozy living", "home automation US", "wellness tech". → aplica: hero copy de tu-tienda.
- Pricing premium value: $49–$89 por productos de calidad; evitar competir solo por precio → usar alianzas estratégicas (descuento en servicios complementarios como aromaterapia + dispositivo) para aumentar valor percibido sin bajar margen.
- Segmentación por "momentos de vida" no generaciones: 70% de usuarios se informan por momentos vitales; TikTok para jóvenes en transición; Google para decisores de hogar; Instagram para aspiracionales. → aplica: adaptar canal tu-tienda según el momento de compra (nuevo hogar, regalo, renovación).
- Email marketing personalizado por producto comprado: usuario compró luz LED → secuencia sobre iluminación cozy → cross-sell aromaterapia → ratio 70% valor + 30% promo; 1 correo bien segmentado > 10 correos genéricos.

**Diseño visual en Canva y herramientas gráficas sin costo**

[6oUJDLIfdEg] · [eHT1ojz7SyI] · [YjcldTRA-F8] · [BKRgUZMR0dA] · [YCaLd6nsWzQ]:
- Diseño 3D en Canva (versión gratuita): 3 recursos (screenshot + imagen señalando abajo + fondo) → recortar sin dorso → subir 1080×1350 → técnica "copia + mover" para capas visuales → "mover a fondo" para profundidad 3D. → aplica: posts de producto tu-tienda con efecto de profundidad visual.
- Carrusel panorámico: tamaño 3240×1080 (3 columnas de 1080 px) → "Mostrar reglas y guías" → "Imagen Splitter" para separar en 3 imágenes individuales. → aplica: carrusel coherente tu-tienda que se ve continuo en el perfil de Instagram.
- Camba (Canva) Pro + Remus Background Remover: eliminar fondo automáticamente → sombra brillante + efecto brillante → borde 15 px → transparencia 100%. → aplica: imágenes de producto tu-tienda con borde luminoso para destacar en feed.
- Adobe Express: miles de plantillas para stories, reels, carousels → reduce tiempo de creación 60%+; formatos pre-configurados para cada red social. → aplica: producción rápida de creativos de campaña tu-tienda en temporada.
- Contenido SEO 2025 en Canva: keywords "tu-nicho essentials", "cozy wellness products" → elementos gráficos personalizados con rol "Campaña de Marketing" → estructura 3C (Concepto + Contexto + Conclusión) para retención. → aplica: posts educativos tu-tienda con keywords integradas visualmente.

## Reglas de oro
1. Si puedes explicar la idea en castellano, puedes construirla con Claude Code.
2. Plan mode primero; aprueba y deja ejecutar.
3. `CLAUDE.md` al día = 5-10× menos gasto.
4. Conversación corta + `/clear` > megaconversación.
5. Modelo según tarea: Opus=código complejo, Sonnet=día a día, Haiku=bots/baratos.
6. Para trabajo visual, itera con capturas de pantalla.
7. Session handoff al 12-15% de contexto en sesiones largas (no esperar al 95%).
8. Subagentes Haiku para lectura masiva; Opus orquestador = 4-10× ahorro.
9. Rutinas cloud para 24/7; `/loop` para tareas en sesión.
10. Grill Me antes de construir cualquier skill importante.

> Nota: el canal tiene ~19+ videos; algunos transcripts pueden faltar localmente (descarga incremental). Si falta un id, descargarlo: `yt-dlp --skip-download --write-auto-subs --sub-langs "es.*,en.*" <url>`.
