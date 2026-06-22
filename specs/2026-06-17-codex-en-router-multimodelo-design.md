# Spec — Codex como worker del router multimodelo (destino explícito ruteado por capacidad)

> Fecha: 2026-06-17 · Estado: aprobado (diseño) · Autor: sesión Claude/Opus
> Contexto: ecosistema multi-agente en `~` (NO es repo git; durabilidad por archivo + memoria).
> Extiende: `2026-06-17-router-por-modelo-design.md` (el router por tier ya existente).
> Objetivo de negocio: **ahorrar tokens de Claude** sumando a Codex (OpenAI, bolsa de costo separada) como
> ejecutor par; el trabajo que va a Codex NO consume presupuesto de Claude.

## 1. Problema

El router por modelo (`cerebro_modelo.py` + `cerebro_tareas_modelo.py`) reparte tareas entre tiers de Claude
(`haiku`/`sonnet`/`opus`/`any`). Codex **ya participa del cerebro compartido** (memoria, mensajes, locks,
multisesión vía `AGENTS.md`), pero **NO es un destino de la cola de tareas por modelo**: no se le puede
`publicar`/`delegar` una tarea ni declararse worker vivo del router.

Codex es un runtime de coding agéntico completo (refactor multi-archivo, computer-use, browser, repl, code
review) y **par a Opus en razonamiento**, con **costo en bolsa separada** (suscripción OpenAI). Desaprovecharlo
como destino del router deja sobre la mesa el mayor ahorro posible de tokens Claude.

## 2. Objetivos y no-objetivos

**Objetivos**
- `codex` es un **destino válido** de la cola (`publicar`/`pendientes`/`tablero`/`delegar --tier codex`).
- `codex` es un **worker vivo declarable** (`registrar codex`, aparece en `vivos`).
- Se le puede asignar **cualquier** tarea (equivalente-Opus o mecánica): **sin tope de complejidad**.
- El ruteo a Codex es **explícito** (decisión del orquestador/usuario), guiado por un **perfil de capacidades**
  para no malgastarlo.
- Codex entra solo al sistema al arrancar (activación vía `AGENTS.md`, su adaptador auto-cargado).
- Reusar la infra existente; **no** duplicar ni romper el router por tier.

**No-objetivos (YAGNI)**
- NO meter `codex` en la heurística automática del clasificador (decisión del usuario: solo explícito).
- NO auto-lanzar sesiones/daemons de Codex (regla universal #3). Si no hay worker codex vivo → avisar.
- NO tocar `~/.codex/hooks.json` (gateado por `trusted_hash`); la activación por hook queda como mejora opcional.
- NO mover memoria privada (regla #8).
- NO crear dashboard nuevo.

## 3. Decisiones de diseño (confirmadas con el usuario 2026-06-17)

| # | Decisión | Elección |
|---|----------|----------|
| D1 | ¿Rol de Codex en el router? | **Destino explícito sin tope de complejidad**: cualquier tarea, ruteada por capacidad. |
| D2 | ¿Codex en la heurística `clasificar()`? | **No.** El clasificador nunca propone `codex` (solo orden explícita). |
| D3 | ¿`codex` es un "tier"? | **No.** Se separa `TIERS` (escalera de costo Claude, lo único auto-proponible) de `WORKERS` (destinos/liveness reales, que incluye `codex`). |
| D4 | ¿Cómo se activa Codex como worker? | **(a) `AGENTS.md` raíz** (auto-cargado, sin re-trust). (b) hook `session_start` queda anotada como mejora opcional. |
| D5 | ¿Liveness de Codex? | Tier fijo `codex` (no derivado de model-id; Codex se identifica por runtime). |

## 4. Diseño

### 4.1 `cerebro_tareas_modelo.py` (cola física)
- `MODELOS = ("haiku", "sonnet", "opus", "codex", "any")` — añadir `"codex"`.
- Efecto automático (sin más cambios): `publicar --modelo codex`, `pendientes codex` (devuelve codex + `any`),
  `tablero` muestra columna `[codex]`, `_norm_modelo` acepta codex. El orden de impresión recorre `MODELOS`.

### 4.2 `cerebro_modelo.py` (cerebro del router)
- Mantener `TIERS = ("haiku", "sonnet", "opus")` — **solo** lo que `clasificar()` puede proponer.
- Introducir `WORKERS = TIERS + ("codex",)`.
- `registrar(tier)` y `vivos()` validan/operan sobre `WORKERS` (permite `registrar codex`, `codex` en `vivos`).
- `delegar(..., tier)` valida `tier in WORKERS` (permite `delegar --tier codex` con **cualquier** tarea).
- `clasificar()` **intacto** (su loop solo conoce `_OPUS_KW`/`_HAIKU_KW`/`sonnet`; nunca devuelve codex). ✓ D2
- `tier_de()` **intacto** (mapea ids de Anthropic; codex no tiene model-id Anthropic → irrelevante).
- El aviso de `delegar` para codex sin sesión viva reutiliza el texto existente:
  "abre una sesión codex para que la tome".

### 4.3 Activación de Codex (`AGENTS.md` raíz)
Añadir un bloque worker (espejo del `worker_instruccion.txt` de Claude) con **tier fijo `codex`**:
- Al arrancar (si va a trabajar en tareas repartibles): `cerebro_modelo.py registrar codex` +
  `cerebro_tareas_modelo.py pendientes codex` (toma con `tomar <id> --por <sesion>`).
- **Codex NO se auto-asigna**: solo toma lo dirigido explícitamente a `codex` (o `any`).
- Codex también puede **delegar** trabajo de tiers Claude de vuelta a la cola (`delegar --tier <t>`).
- No auto-lanzar daemons (regla #3).

### 4.4 Perfil de capacidades de Codex (guía de ruteo — documentado en `AGENTS.md` + `17_…md` + `worker_instruccion.txt`)
- **Dale preferentemente:** coding agéntico end-to-end, refactor multi-archivo, implementar contra un spec,
  iterar tests, code review, automatización browser/computer-use, tareas largas autónomas bien especificadas.
  Razonamiento **par a Opus**.
- **No lo malgastes en:** renombrar/mover un archivo o one-liner trivial → eso es `haiku` (más barato).
- **Ventaja transversal:** su costo NO sale del presupuesto Claude → ante empate de capacidad, descargar a
  Codex ahorra tokens de Claude.

### 4.5 `worker_instruccion.txt` (lo ve la sesión Opus orquestadora)
Añadir: `codex` es destino válido para **cualquier** tarea; para mandarle algo:
`cerebro_modelo.py delegar "<titulo>" --tier codex -p "<prop>" --terminado "<criterio>"` + resumen
"dale preferentemente / no lo malgastes" del §4.4.

## 5. Flujo de datos

```
Usuario → sesión Opus (orquestadora)
   │  decide explícitamente: "esto a Codex"
   ▼
cerebro_modelo.delegar(titulo, --tier codex, …)
   │  valida codex ∈ WORKERS ✓
   ▼
cerebro_tareas_modelo.publicar(modelo="codex")  → cola %LOCALAPPDATA%/cerebro/tareas_modelo.json
   │  aviso: "Mxxx encolada para codex; (viva|abre una sesión codex)"
   ▼
sesión Codex (AGENTS.md la activó) → pendientes codex → tomar Mxxx → ejecuta → completar Mxxx
```

## 6. Manejo de errores / casos borde
- `delegar --tier codex` sin sesión codex viva → encola + avisa "abre una sesión codex" (no ejecuta en Claude). ✓ regla #3
- `clasificar` con texto que casualmente diga "codex" → sigue devolviendo opus/sonnet/haiku (codex no está en KW). ✓ D2
- `registrar` con tier inválido → `ValueError` (ahora `codex` es válido; otros siguen fallando).
- Compatibilidad: tareas existentes en la cola no se ven afectadas (solo se amplía el conjunto válido).

## 7. Pruebas
- `test_cerebro_modelo.py`: (a) `delegar --tier codex` OK y encola con modelo codex; (b) `registrar codex` válido y
  aparece en `vivos`; (c) `clasificar` **nunca** devuelve codex (incluido un caso con la palabra "codex" en el texto);
  (d) `tier_de` sigue mapeando ids Anthropic igual.
- `test_cerebro_tareas_modelo.py`: (a) `publicar --modelo codex` normaliza a codex; (b) `pendientes("codex")`
  devuelve codex + any y excluye haiku/opus puros; (c) `tablero` agrupa la columna codex.

## 8. Docs a actualizar (regla #9, mínimo)
- `17_ROUTER_POR_MODELO.md`: codex como destino explícito + perfil de capacidad.
- `AGENTS.md` raíz: bloque worker codex (§4.3) + perfil (§4.4).
- `worker_instruccion.txt`: línea de destino codex (§4.5).
- `CLAUDE.md`: mención de codex como destino — **en un bloque único al CIERRE de sesión** (hábito de tokens #2:
  no editar el archivo auto-cargado a mitad de sesión; avisar al usuario).
- `CONVIVENCIA_CLAUDE_CODEX.md` / `00_INDICE.md`: enlace si procede.

## 9. Mejora opcional anotada (no en este alcance)
Hook `session_start` en `~/.codex/hooks.json` que inyecte un `worker_instruccion_codex.txt` (simetría total con
el SessionStart de Claude). Implica re-trust del `trusted_hash` en Codex → se decide aparte.
