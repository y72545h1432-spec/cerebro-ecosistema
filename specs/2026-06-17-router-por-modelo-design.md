# Spec — Router de tareas por modelo (delegación multimodelo con activador)

> Fecha: 2026-06-17 · Estado: aprobado (diseño) · Autor: sesión Claude/Opus
> Contexto: ecosistema multi-agente en `~` (NO es repo git; durabilidad por archivo + memoria).
> Objetivo de negocio: **ahorrar tokens** ejecutando el trabajo barato en el modelo barato (Haiku −90% vs Opus),
> sin que el usuario tenga que recordar a qué sesión escribir.

## 1. Problema

Hoy el usuario abre varias sesiones de Claude Code con modelos distintos y existe `cerebro_tareas_modelo.py`
(una cola que reparte tareas por *tier*: `haiku`/`sonnet`/`opus`/`any`). Pero faltan tres cosas:

1. **Auto-conocimiento de modelo:** ninguna sesión declara su tier de forma fiable y consultable por otras.
2. **Router/clasificador:** si el usuario le escribe a *cualquier* sesión, esa sesión no tiene un mecanismo
   para decidir a qué tier se delega la tarea.
3. **Activador automático:** las sesiones nuevas no entran solas al "trabajo conjunto" (no se registran ni
   consultan su cola).

Resultado actual: el ahorro depende de que el usuario recuerde manualmente publicar/tomar tareas y a qué
sesión hablarle. Queremos que sea automático e independiente de a qué modelo le escriba.

## 2. Objetivos y no-objetivos

**Objetivos**
- Cada sesión sabe y **declara** su tier al arrancar, con liveness (heartbeat + TTL).
- Cualquier sesión puede **clasificar** una tarea entrante y decir a qué tier se delega.
- Toda sesión nueva entra sola al sistema (activador por hook).
- Reusar `cerebro_tareas_modelo.py` y `_Mutex` de `cerebro_multisesion`; **no** romper ni duplicar infra.

**No-objetivos (YAGNI)**
- NO auto-lanzar sesiones/daemons (regla universal #3). Si no hay worker del tier → avisar.
- NO modificar el core `cerebro_multisesion.py` (el tier vive en un store propio pequeño).
- NO inferir el modelo desde el hook (el hook no lo conoce de forma garantizada); la sesión se auto-declara.
- NO un dashboard nuevo (se puede añadir después si hace falta).

## 3. Decisiones de diseño (confirmadas con el usuario 2026-06-17)

| # | Decisión | Elección |
|---|----------|----------|
| D1 | ¿Quién clasifica la tarea? | **Híbrido**: la heurística `clasificar()` propone tier + razón; la sesión confirma/corrige. |
| D2 | ¿Tarea para otro tier sin worker vivo? | **Encolar y avisar** ("abre una sesión `<tier>`"); no ejecutar en el tier caro. |
| D3 | ¿Activador en sesiones nuevas? | **SessionStart hook** inyecta la instrucción; la sesión se **registra sola**. |

## 4. Arquitectura

Tres unidades, cada una con un propósito claro:

### 4.1 `cerebro_modelo.py` (módulo nuevo)
Cerebro del router. Funciones puras + estado atómico. Depende solo de la stdlib + `_Mutex` de
`cerebro_multisesion`. Estado en `%LOCALAPPDATA%\cerebro\modelos_vivos.json` (efímero, como locks).

API (Python + CLI espejo):
- `tier_de(model_id: str) -> str` — mapea un id de modelo a tier. `MAPA`:
  - `claude-opus-*`, `claude-fable-*` → `opus`
  - `claude-sonnet-*` → `sonnet`
  - `claude-haiku-*` → `haiku`
  - desconocido / vacío → `opus` (**default seguro**: nunca degradar a un tier barato por error).
- `registrar(tier: str, sesion: str = "") -> None` — escribe `{tier: {sesion, ts}}` (heartbeat). Atómico.
- `vivos(ttl_seg: int = 900, ahora=None, d=None) -> set[str]` — tiers con heartbeat dentro del TTL.
  `ahora`/`d` inyectables para test.
- `clasificar(titulo, proposito="", archivos=None) -> tuple[str, str]` — heurística por palabras clave;
  devuelve `(tier_propuesto, razon)`. Reglas (orden de prioridad):
  - **opus** si el texto sugiere diseño/arquitectura/debug/razonamiento/redacción difícil
    (p.ej.: diseñar, arquitect, depurar, debug, investiga, analiza, decide, refactor grande, spec, plan).
  - **haiku** si sugiere trabajo mecánico/repetitivo
    (p.ej.: renombrar, formatear, mover, listar, buscar, correr test, aplicar edit conocido, regenerar,
    convertir, copiar, ordenar, traducir literal).
  - **sonnet** en cualquier otro caso (intermedio / por defecto del clasificador).
  - La razón es una frase corta citando la señal encontrada (para que la sesión decida con criterio).
- `delegar(titulo, proposito, tier, terminado="", archivos=None, pruebas=None, prioridad=0, creada_por="")
  -> dict` — publica en `cerebro_tareas_modelo.publicar(...)` con `tier`, luego consulta `vivos()` y
  devuelve `{"id": tid, "tier": tier, "worker_vivo": bool, "aviso": str}`. El `aviso` es el texto que la
  sesión muestra al usuario (encolada + si debe abrir una sesión del tier).

CLI (espejo, igual estilo que `cerebro_tareas_modelo.py`):
```
py cerebro_modelo.py soy <model-id>          # imprime el tier de ese id
py cerebro_modelo.py registrar <tier> [--sesion s]
py cerebro_modelo.py vivos                    # tiers vivos ahora
py cerebro_modelo.py clasificar "<titulo>" [-p "<proposito>"] [--archivo x]
py cerebro_modelo.py delegar "<titulo>" -p "<prop>" --tier <t> --terminado "<c>" [--archivo x --prueba c]
```

### 4.2 Activador — SessionStart hook (en `~\.claude\settings.json`)
Se añade un hook `SessionStart` que imprime (additionalContext) un bloque corto de instrucción para la
sesión. El hook NO conoce el modelo; solo ordena a la sesión auto-declararse. Texto inyectado (resumen):

> Eres worker del sistema multi-modelo (ahorro de tokens). Tu **tier** = tu propio model-id
> (`opus`/`sonnet`/`haiku`). Al arrancar: (1) `py .cerebro\cerebro_modelo.py registrar <tu-tier>`;
> (2) revisa tu cola `py .cerebro\cerebro_tareas_modelo.py pendientes <tu-tier>`. Cuando el usuario te dé
> una tarea: clasifícala (`clasificar` + tu criterio); si el tier resultante ≠ el tuyo → `delegar` y **NO**
> la ejecutes (muéstrale el aviso); si coincide → hazla. No auto-lances sesiones.

Implementación: hook tipo `command`. En Windows el comando imprime el texto (PowerShell `Write-Output` de
un here-string, o un `.py`/`.txt` que se cat-ea). Debe convivir con el hook `SessionStart` de `remember`
(añadir, no reemplazar).

### 4.3 Doc `.cerebro\17_ROUTER_POR_MODELO.md` (nuevo)
Explica el mecanismo (qué es, cómo se usa, las 3 decisiones, ejemplos de CLI) para que sea descubrible y
mantenible. Se enlaza desde `00_INDICE.md` y desde `TOKENS_HABITOS.md` (sección multimodelo).
**El enlace en `CLAUDE.md` se difiere al cierre de sesión** (hábito #2: no editar `CLAUDE.md` a mitad de
sesión — invalida el caché de prefijo).

## 5. Flujo de datos

```
Sesión NUEVA arranca
  └─ SessionStart hook inyecta instrucción worker
       └─ sesión lee su model-id (de su propio contexto) → tier_de() → registrar(tier)
       └─ pendientes(tier): ¿hay trabajo encolado para mí? → si sí, tomar → ejecutar → completar

Usuario escribe una tarea a la sesión S (tier T_s)
  └─ clasificar(tarea) → (T_t, razón)   [heurística]
  └─ sesión confirma/corrige T_t        [criterio]
  └─ si T_t == T_s → la ejecuta ahora
  └─ si T_t != T_s → delegar(...):
        publicar en cola para T_t
        vivos(): ¿hay sesión T_t viva?
          sí → aviso "M0xx encolada; la tomará tu sesión <T_t>"
          no → aviso "M0xx encolada para <T_t>; abre una sesión <T_t>"
```

## 6. Manejo de errores y seguridad
- **Escritura atómica** con `_Mutex("modelos_vivos")` (serializa entre sesiones concurrentes).
- **Store corrupto/ausente** → tratar como vacío (igual que `cerebro_tareas_modelo._load`).
- **model-id desconocido** → tier `opus` (no degradar trabajo a un tier barato sin certeza).
- **Sin worker vivo** → avisar, **nunca** auto-lanzar (regla universal #3).
- **TTL** evita workers fantasma: un tier sin heartbeat reciente no cuenta como vivo.

## 7. Estrategia de pruebas
Tests unitarios (mismo estilo de testeo por inyección que `cerebro_tareas_modelo.py`):
- `tier_de`: opus/sonnet/haiku/fable/desconocido/vacío → tier esperado.
- `vivos`: con `ahora`/`d` inyectados — dentro y fuera del TTL; varios tiers.
- `clasificar`: casos mecánicos→haiku, difíciles→opus, intermedios→sonnet, + que devuelve razón no vacía.
- `delegar`: con cola inyectada/temporal — publica con el tier correcto y arma el `aviso` según `worker_vivo`.
Prueba de humo de CLI: `soy claude-opus-4-8` → `opus`; `registrar haiku` + `vivos` → contiene `haiku`.

## 8. Unidades y dependencias (resumen de aislamiento)
- `cerebro_modelo.py` — depende de: stdlib, `cerebro_multisesion._Mutex`, `cerebro_tareas_modelo.publicar`.
  Lo usan: las sesiones (vía CLI) y el hook (indirectamente, vía la instrucción).
- hook SessionStart — depende de: nada de código propio; solo emite texto. Lo usa: el harness al abrir sesión.
- doc 15 — sin dependencias; referencia a los dos anteriores.

## 9. Riesgos / abiertos
- La calidad de `clasificar` es heurística; por eso es **híbrida** (la sesión corrige). Se puede afinar el
  diccionario de palabras clave con el uso (no bloquea el MVP).
- Si el usuario usa `/model` para cambiar de modelo a mitad de sesión, el tier declarado queda viejo; mitigar
  re-declarando al detectar el cambio (mejora futura; el heartbeat con TTL limita el daño).
