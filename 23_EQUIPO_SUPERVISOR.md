# 23 · AGENT TEAM (supervisor) + consolidación base + CLI único

> Construido 2026-06-21. Equivalente más estable al "Agent Team" de Claude Code, sobre `.cerebro`.
> Estado: Fases 0–3 completas, suite 13/13 verde. Probe real `claude -p` headless verificado (hecho
> `claude-headless-haiku` → ok). Detalle de diseño: `plans/investiga-que-es-agent-twinkling-penguin.md`.

## Qué se añadió

| Archivo | Qué es |
|---|---|
| `cerebro_core.py` | **Base común** (stdlib pura): `write_atomic`/`read_json_tolerant`/`append_jsonl`/`read_jsonl`, `now`/`is_expired`/`age_minutes`, `unfold`/`to_list`, `pid_alive`/`env_fingerprint`/`shell_effective`, y **`FileMutex`** (lock del SO: `msvcrt.locking`/`fcntl.flock`). Fuente ÚNICA: 8 módulos importan de aquí (antes había 4-5 copias). |
| `cerebro.py` | **CLI único**: `py cerebro.py <area> [args]` despacha a cada módulo (estilo `git`). Áreas: tareas, modelo, coord, salud, watch, checkpoint, hechos, memoria, coprog, grafo, skills, equipo. Los `py cerebro_X.py ...` antiguos siguen vivos (compat). |
| `cerebro_equipo.py` | **Supervisor del equipo**: drena la cola lanzando workers `claude -p` (o `codex`) headless EFÍMEROS y **termina** (no daemon). Modo debate por olas. Runtime `api` GRATIS + routing híbrido + verificador. |
| `cerebro_llm.py` | **Cliente LLM gratis** OpenAI-compatible multi-proveedor (Groq/Gemini/OpenRouter) con **fallback** automático. Stdlib pura (`urllib`); claves por entorno (apto repo público). |
| `equipo_worker_contrato.txt` | Plantilla del prompt del worker efímero (Paso 0 cerebro → ejecuta → completar/fallar/rechazar → hallazgos). |
| `cerebro_equipo.toml` | Config de guardrails (caps, budgets, allowlist de exes, tools por tier). |
| `cerebro_equipo_dash.py` | **Dashboard** read-only (no daemon): `--once` / `--follow N` / `--json`. |

## Cómo se usa

```
# 1) (opcional) abre sesiones worker o deja que el supervisor las lance solo.
# 2) DRY-RUN siempre primero (no gasta, no lanza): muestra el argv exacto que correría.
py cerebro.py equipo drenar --tier haiku --dry-run
# 3) Lanzar de verdad (requiere --confirm; registra ms.decidir):
py cerebro.py equipo drenar --tier haiku --confirm --max-workers 3
# 4) Debate por olas (teammates que se rebaten; para por saturación semántica o tope):
py cerebro.py equipo debate --enunciado "¿cómo abordar X?" --max-rondas 4 --workers 3 --confirm
# 5) Panel en vivo (read-only):
py cerebro.py equipo dash --once        # o --follow 10
# 6) Recuperar un run tras un crash (re-entrega tareas colgadas):
py cerebro.py equipo reanudar --run <run_id> --tier haiku --confirm
# KILL-SWITCH: crea el archivo  %LOCALAPPDATA%\cerebro\equipo\STOP  para que deje de lanzar.
```

## 💰 Costo: GRATIS vs PAGO vs HÍBRIDO (elige tu modo)

El equipo puede correr a **costo $0** (modelos gratuitos) o con **Claude** (de pago, máxima calidad), o
mezclar ambos. Se controla con `calidad.modo` en `cerebro_equipo.toml` o al vuelo con `--modo`/`--runtime`.

| Modo | Qué recibes | Costo | Cuándo usarlo |
|---|---|---|---|
| **`gratis`** | TODO con modelos gratis OpenAI-compatible (Groq / Gemini / OpenRouter). Buena calidad en debate, análisis, clasificación, drafts y ediciones simples; **brecha** en lo difícil (refactor multi-archivo, debug sutil, repos grandes). | **$0** | Probar, explorar, tareas masivas, o si no quieres gastar nada. |
| **`pago`** | TODO con Claude (Opus/Sonnet/Haiku). Máxima calidad y fiabilidad agéntica. | tokens (budgets: `worker_budget_usd`, `run_budget_usd`) | Trabajo crítico donde la corrección importa. |
| **`hibrido`** (DEFAULT) | Enruta por **brecha**: lo de brecha pequeña gratis, lo difícil a Claude. Por defecto: **debate** y tareas **`haiku`** → gratis; **`sonnet`/`opus`** → Claude. | mixto (paga solo lo difícil) | El equilibrio recomendado: $0 en lo barato, calidad en lo que cuesta. |

**Verificador (compensa la brecha del gratis sin costo):** `calidad.verificador = "auto"` corre una **2ª pasada
gratis** que critica las salidas de los modelos gratuitos contra el criterio de aceptación; si no cumplen, la
tarea **no se marca `hecha`** (se bloquea para rehacer). Vale `true`/`false` para forzarlo.

### Setup del modo gratis (30 s, sin tarjeta)
1. `cp .env.example .env` y pega **al menos una** clave gratis:
   - Groq → https://console.groq.com  ·  Gemini → https://aistudio.google.com/apikey  ·  OpenRouter → https://openrouter.ai/keys
2. Carga el `.env` en tu shell (ver comandos dentro de `.env.example`).
3. Listo. Con varias claves hay **fallback automático** (si una agota su cuota del día, usa la siguiente).

### Overrides al vuelo
```
py cerebro.py equipo drenar --tier haiku --modo gratis --confirm     # fuerza TODO gratis
py cerebro.py equipo drenar --tier opus  --runtime api --confirm     # esta tarea, gratis
py cerebro.py equipo drenar --tier haiku --runtime claude --confirm  # esta tarea, Claude
py cerebro.py equipo debate --enunciado "..." --modo pago --confirm  # debate con Claude
```
> Las claves NUNCA viven en el repo (van en `.env`, ignorado por git). Config de modelos/presets: sección
> `[calidad]` y `[api]` de `cerebro_equipo.toml`. Cliente multi-proveedor: `cerebro_llm.py`.

## Modelo de worker = EFÍMERO (por qué es más estable que el Agent Team nativo)
Cada tarea = un proceso que nace, hace SU tarea, reporta (`completar`/`fallar`/`rechazar` en
`cerebro_tareas_modelo`) y muere. Sin sesiones interactivas colgadas, sin tmux, sin `/resume` frágil.
Si un worker crashea, solo se pierde 1 tarea y el **visibility-timeout** (`expirar_tomadas`) la
recupera. El debate "teammates que se hablan" se logra por OLAS: cada ronda lanza workers NUEVOS que
leen `ronda_{r-1}.md` (lo que dejaron los otros) y aportan/rebaten en `ronda_{r}.md` — mismo patrón
de saturación que `investigacion-infinita`, sin procesos persistentes.

## Reusa lo que ya existía (no reinventa)
Cola/claim CAS/visibility-timeout (`cerebro_tareas_modelo`), locks/mailbox/`pid_alive`
(`cerebro_multisesion`), router por tier (`cerebro_modelo`), checkpoint anti-crash
(`cerebro_checkpoint`), telemetría (`cerebro_salud`), saturación semántica (`cerebro_semantica`).

## Regla Universal #3 — reencuadre (guardrails en vez de prohibición absoluta)
La #3 ("no relanzar daemons/loops autónomos sin decisión explícita") **se respeta**: el supervisor
lo lanza el usuario u Opus **tras `--confirm` una vez** (registra `ms.decidir`), **drena y termina**
(no es daemon). El auto-spawn queda ACOTADO por guardrails verificables:
1. `--confirm` obligatorio (sin él → `--dry-run`, no lanza).  2. `max_workers` (concurrencia dura).
3. **kill-switch** `…\cerebro\equipo\STOP` (chequeado antes de cada worker).  4. presupuesto por worker
(`--max-budget-usd`) y agregado por run.  5. **allowlist** de ejecutables (solo claude/codex) +
`--disallowedTools` anti fork-bomb.  6. una pasada de drenado (sin loops).
(Precedente: #22 OpenClaw, también excepción acotada a la #3.)

## ⚠️ Seguridad de permisos (léelo antes de `--confirm`)
- **`permission_mode = acceptEdits`** (default): los workers `claude -p` **auto-aceptan ediciones** de
  archivos dentro de `--add-dir` (default: el cwd). Es autonomía headless intencional, pero potente.
- **Gating por tier**: `haiku` = SOLO lectura (Read/Grep/Glob); `sonnet`/`opus` añaden **Edit/Write/Bash**
  → esos workers pueden escribir y correr comandos sin preguntar. Empieza por `haiku` (análisis) o por
  ediciones mecánicas de bajo riesgo con el repo en git **LIMPIO** (revertible).
- **Siempre `--dry-run` primero** (muestra el argv/plan, no lanza) y arranca en **`--modo gratis`** ($0).
  Sube a `sonnet`/`opus` o `--modo pago` solo cuando confíes en la tarea. Kill-switch: crea
  `%LOCALAPPDATA%\cerebro\equipo\STOP`. El runtime gratis sandboxea los archivos al workdir (`_dentro`).
- **Verifica tu CLI**: `--max-budget-usd` / `--permission-mode` / `--add-dir` / `--disallowedTools` dependen
  de la versión de `claude` instalada; haz un smoke-test real en `pago` antes de confiar en el presupuesto.

## Consolidación (Fase 0) — correctness
- `FileMutex` ahora usa **lock del SO**: elimina el TOCTOU del lockfile O_EXCL hecho a mano y los
  locks rancios (el SO libera al morir el proceso). Mejora a TODO el ecosistema.
- `cerebro_hechos._append` quedó **protegido por mutex** (antes: append sin lock → líneas corruptas
  bajo concurrencia). Test: `test_cerebro_hechos_race.py` (180/180 con 6 procesos).

## Tests
`test_cerebro_core.py`, `test_cerebro_memoria.py`, `test_cerebro_hechos_race.py`,
`test_cerebro_equipo.py` (13 casos: dry-run/guardrails/recuperación/debate/dashboard, todo con worker
FAKE → 0 tokens). Suite completa: `for t in test_cerebro_*.py; do py $t; done`.
