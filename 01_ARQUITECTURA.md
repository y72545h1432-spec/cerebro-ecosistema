# Arquitectura del Ecosistema Multi-Agente

## Capas

### 1. Capa neutral: `.cerebro`
Ruta: `~\.cerebro\`

Responsabilidad:
- Identidad multi-agente.
- Coordinacion multisesion agentica (`agent`/`runtime` por sesion).
- Locks globales y por proyecto.
- Eventos, decisiones, buzon y conocimiento compartido.
- Documentacion neutral que no pertenece a Claude ni a Codex.

No debe guardar:
- Credenciales.
- Tokens.
- Historial privado completo de un runtime.
- Caches pesadas.
- Artefactos temporales que no aporten coordinacion.

### 2. Capa runtime
| Runtime | Ruta privada | Entrada |
|---|---|---|
| Claude Code | `~\.claude\` | `~\CLAUDE.md` |
| Codex | `~\.codex\` | `~\AGENTS.md` |
| Skills personales | `~\.agents\skills\` | Descubiertas por Codex segun `description`. |

Responsabilidad:
- Preferencias y memoria propias de cada runtime.
- Skills/plugins propios.
- Historial, sesiones y caches del runtime.

Regla:
- Ningun runtime debe asumir que sus nombres de skills existen en otro runtime.

### 3. Capa proyecto
Cada proyecto conserva su carpeta y sus reglas duras. Los adaptadores `CLAUDE.md` y `AGENTS.md` son puertas de entrada, no memorias paralelas.

Responsabilidad:
- Estado y reglas especificas del proyecto.
- Planes, comandos, gotchas y restricciones locales.
- Referencias al protocolo neutral cuando haya trabajo concurrente.

### 4. Capa recursos compartidos
Recursos que deben coordinarse con locks globales:
- `gpu`
- `vram`
- `tu servidor LLM local`
- `tu servidor LLM local_config`
- `daemon_config`
- `puerto_1234`

## Flujo de autoridad
1. Usuario.
2. Reglas universales del adaptador runtime (`CLAUDE.md`/`AGENTS.md`).
3. Fuente neutral `.cerebro`.
4. Reglas del proyecto.
5. Memoria privada del runtime.

Si hay conflicto, no se resuelve por antiguedad: se registra en `.cerebro`, se pide confirmacion si afecta seguridad, y se actualiza la fuente neutral.

## Modelo de identidad
- `project`: dominio de trabajo (`tu-tienda`, `tu-proyecto-agente`, `hub`, etc.).
- `agent`: quien actua (`claude`, `codex`, `desconocido`, futuro agente).
- `runtime`: superficie concreta (`claude-code`, `codex`, app futura).
- `sesion`: instancia viva con PID/host/latido.

El ecosistema se coordina cruzando `project + agent + recurso`.

## Integracion de nuevos agentes
El ecosistema es abierto por contrato, no por copia de archivos. Cualquier runtime nuevo debe:
1. Leer `06_CONTRATO_NUEVO_AGENTE.md`.
2. Declarar `agent` y `runtime`.
3. Crear adaptador solo si aporta reglas propias.
4. Reusar `.cerebro` para coordinacion y no crear una segunda multisesion paralela.

## Árbol del ecosistema (mapa canónico) — actualizado 2026-06-19
> Solo el ECOSISTEMA. Se **omiten a propósito** las carpetas de Windows/perfil (Contacts, Cookies,
> NetHood, Start Menu, AppData, Documents, Downloads, OneDrive, Recent, SendTo…) y los dotdirs de
> herramientas (`.ollama`, `.tu servidor LLM local`, `.vscode`, `.cache`, `.config`, `.ssh`…): son **intocables**.
> **[load-bearing]** = referenciado por ruta absoluta (hooks, `sys.path`, routers, dashboards) → NO
> mover sin reescribir rutas + re-test. La memoria privada NO se mueve en reorganizaciones (regla #8).

```
~\                      ← HOME (raíz del ecosistema, cwd de arranque)
├─ CLAUDE.md                         router Claude (auto-carga)               [load-bearing]
├─ AGENTS.md                         router Codex (auto-carga)                [load-bearing]
├─ hub_dashboard.py · hub_status.py  HUB multiproyecto :<PUERTO_HUB> (+ test_hub_*.py) [load-bearing]
│
├─ .cerebro\                         ★ NÚCLEO neutral (coordinación + memoria + docs de proceso)
│  ├─ cerebro_multisesion.py         core multisesión (Paso 0 · locks · buzón · eventos)
│  ├─ cerebro_memoria.py             memoria durable (recordar/buscar/reindexar)
│  ├─ cerebro_hechos.py              hechos verificables (anti-discrepancia, regla #15)
│  ├─ cerebro_coprog.py · cerebro_checkpoint.py · cerebro_modelo.py · cerebro_tareas_modelo.py
│  ├─ cerebro_grafo.py               grafo de código on-demand: `simbolo` / `arquitectura`
│  ├─ cerebro_semantica.py · cerebro_watch.py · dash_theme.py · test_*.py
│  ├─ cerebro_research.py             motor Investigación Infinita (saturación semántica) — globalizado de tu-tienda+tu-proyecto-agente (F6)
│  ├─ cerebro_paths.py                rutas robustas conscientes de OneDrive (is_dehydrated/state_dir/resolve_root) — globalizado de tu-tienda (F6)
│  ├─ cerebro_hardware_gate.py        gate de VRAM antes de actos caros (recurso GLOBAL) — globalizado de tu-proyecto-agente (F6)
│  ├─ 00_INDICE.md … 21_*.md         docs de proceso numerados (abrir SOLO el dueño, vía 00_INDICE)
│  ├─ ECOSISTEMA_MULTIAGENTE.md · SKILLS_CROSS_PROYECTO.md · REGISTRO_SKILLS_EXTERNAS.md · TOKENS_HABITOS.md …
│  ├─ memoria\                       memoria durable (1 hecho/archivo + MEMORIA.md índice)  [NO mover · regla #8]
│  │  └─ hub\ tu-tienda\ tu-proyecto-agente\ tu-proyecto-aprendizaje\ tu-proyecto-web\ tu-proyecto-automatizacion\ tu-proyecto-juegos\
│  ├─ hooks\                         hooks de sesión (skill_dispatch…)
│  ├─ auditorias\ · specs\ · docs\ · PLUGINS_OFICIALES\ · investigacion_ecosistema\ · investigacion_recursos\
│  └─ _backups\                      respaldos internos
│
├─ .claude\                          runtime Claude (config/skills/plugins/sesiones)   [privado]
├─ .codex\                           runtime Codex                                     [privado]
├─ .agents\skills\                   skills personales (Codex las descubre por description)
├─ .remember\                        handoffs (now.md/recent.md/…) ← SessionStart auto-carga
│
├─ ──────── PROYECTOS ────────
├─ tu-proyecto-aprendizaje\          (CLAUDE.md/AGENTS.md → PROGRESO.md)        personal · MODO APRENDIZAJE
├─ tu-proyecto-agente\               (CLAUDE.md/AGENTS.md → DOCUMENTACION.md)   computer-use + LoRA Qwen local
├─ tu-proyecto-automatizacion\ (→ PLAN.md)                               Premiere 2020 + pymiere
├─ tu-proyecto-juegos\         (→ PLAN.md)                               juega Roblox vía visión (gui_control)
│  (tu-proyecto-web vive en tu-proyecto-web\ — réplica Figma "Game Zone")
│
├─ ──────── TOOLING ────────
├─ gui_control\          pantalla/ratón/teclado/OCR + stream MJPEG
├─ open-design\          alternativa local a Claude Design (<VRAM>-limitada)
│
├─ scratch\              ✚ NUEVO (2026-06-19) — cajón de archivos sueltos NO load-bearing
│  ├─ datos-sueltos\     solicitudes_*.xlsx · solicitudes.json · hy.json · finalid.txt
│  ├─ backups\           CLAUDE.md.bak-…
│  └─ skills-fuente\     repos-fuente de skills integradas (nothing-design-skill\ — procedencia/LICENSE)
│
└─ (las 4 carpetas "sin clasificar" se resolvieron 2026-06-19: AniKomos\ [repo vacío] · ansel\ [vacía] ·
   my-project\ [scaffold Vite desechable] → Papelera; nothing-design-skill\ → instalada como skill en
   .claude\skills\nothing-design\ + repo-fuente en scratch\skills-fuente\)

C:\                                  ← (es repo git: backup del ecosistema)
├─ tu-tienda\                 (CLAUDE.md/AGENTS.md → 00_EMPIEZA_AQUI/REINICIO_DE_SESION.md)  tienda Shopify
├─ .remember\            handoff a nivel C (remember.md)
└─ .cerebro\ · .agents\ · .cache\    espejos/estado a nivel C
```

**Qué se ordenó el 2026-06-19** (alcance "árbol documentado + tidy seguro"): se documentó este árbol y se
movieron **8 archivos sueltos huérfanos** del home a `scratch\` (reversible). NO se tocó nada
load-bearing, ni dotdirs de runtime/herramientas, ni carpetas de Windows, ni `memoria\` (regla #8). Las
4 carpetas "sin clasificar" se dejaron en su sitio a la espera de decisión del usuario.
