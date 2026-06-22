# 19 · Recuperación post-crash (continuidad ante muerte súbita)

> Tapa el único hueco que la infra de continuidad NO cubría: que una sesión muera de golpe
> (crash / freeze / SIGKILL) **sin** poder ejecutar el cierre manual (`/remember`, `session-report`,
> `ms.despedir()`). Helper: `.cerebro\cerebro_checkpoint.py`. Memoria: [[proceso_recuperacion_post_crash]].

## Por qué existe
Mecanismos ya presentes y qué cubren (NO se duplican):
- **memoria durable** (`cerebro_memoria.py`) — hechos curados que valen para siempre.
- **latidos/locks con TTL + PID-alive** (`cerebro_multisesion.py`) — liveness y exclusión; un lock de PID
  muerto expira solo.
- **cola de tareas con visibility-timeout** (`cerebro_tareas_modelo.py`) — una tarea de worker muerto
  vuelve a `pendiente` con `expirar()`.
- **hook `PreCompact`** — aviso de compactación.

El hueco: ninguno preserva el **contexto en-curso** ("qué estaba haciendo y cuál era el próximo paso")
si la sesión muere **antes** de poder cerrar. El handoff de `.remember\remember.md` "se auto-carga al
abrir", pero hoy solo se escribe en el cierre manual → si hay crash, queda vacío.

## La solución: checkpoint atómico frecuente — AUTOMÁTICO y POR-SESIÓN
`cerebro_checkpoint.py` escribe un handoff **atómico** (tmp + `os.replace`, nunca truncado) con un
marcador de estado:
- `ESTADO: en-curso` — lo deja `checkpoint(...)` (manual) o el **auto-checkpoint** (hooks). Si la
  sesión muere aquí, al abrir se detecta.
- `ESTADO: cerrado-limpio` — lo deja `cerrar_limpio()` (cierre normal o hook `SessionEnd`).

### Dos correcciones clave (incidente 2026-06-18: tu-proyecto-agente B2 murió y el handoff apuntaba al sitio equivocado)
1. **Auto-checkpoint sin disciplina (no depende del hábito).** Los hooks `UserPromptSubmit` y `Stop`
   llaman `cerebro_checkpoint.py auto`, que lee el JSON del hook por stdin (`session_id`,
   `transcript_path`, `cwd`) y **extrae del transcript** el último prompt del usuario + el último
   texto del asistente. Así el breadcrumb refleja "qué se estaba haciendo de verdad" **aunque
   Claude nunca llame `checkpoint()`** — que es justo lo que falla en runs autónomos largos.
2. **Checkpoints POR-SESIÓN (`.remember\checkpoints\<session_id>.md`).** El slot único
   `.remember\remember.md` hacía que un `cerrado-limpio` viejo (sesión A) **enmascarara** la muerte
   sucia de una sesión B posterior, y que sesiones concurrentes se pisaran. Ahora cada sesión tiene
   su archivo; `recuperar`/`escanear` lo decide por-sesión. `remember.md` se conserva solo como
   "último handoff legible" para el auto-load del `SessionStart`.

**El hábito sigue ayudando, pero ya no es la única red.** Un freeze/SIGKILL NO dispara `SessionEnd`;
por eso el auto-checkpoint (que corre en CADA prompt y CADA fin de turno) deja siempre un "último
punto bueno" fresco sin que nadie tenga que acordarse de checkpointear.

## Las 3 fases y qué las cubre

| Fase | Mecanismo | Acción |
|---|---|---|
| **Mid-session (auto)** | hooks `UserPromptSubmit` + `Stop` → `auto` | Escribe `en-curso` por-sesión en CADA prompt y CADA fin de turno, leyendo el transcript. **Sin disciplina.** |
| **Mid-session (manual)** | `checkpoint(...)` + `ms.latido()` | Opcional: refina el breadcrumb antes de una acción larga/arriesgada; el latido sigue siendo el liveness. |
| **Cierre** | `cerrar_limpio(sesion=…)` / hook `SessionEnd` | Estampa `cerrado-limpio` **solo en el archivo de su sesión**. |
| **Apertura** | `escanear(current_session)` / hook `SessionStart` | Cualquier checkpoint `en-curso` de OTRA sesión → **RECOVERY MODE** (no lo enmascara un cierre limpio ajeno). |

### Cuándo checkpointear (regla práctica: "antes de la acción, no después")
- Antes de una tanda larga de edición de varios archivos.
- Antes de algo irreversible / externo / que gasta (regla universal #1).
- Al cambiar de subtarea.

```python
import sys; sys.path.insert(0, r"~\.cerebro")
import cerebro_checkpoint as cp
cp.checkpoint("hecho hasta aquí", "próximo paso concreto", tarea="T123", proyecto="tu-proyecto-agente",
              archivos=["bootstrap/bootstrap.py"])
# ... al cerrar normal:
cp.cerrar_limpio("sesión cerrada, todo verde")
```

### RECOVERY MODE al abrir
Si `recuperar()["recovery"]` es `True` (último checkpoint quedó `en-curso`):
1. Leer el checkpoint (resumen + próximo paso + archivos).
2. Cruzar con **tareas huérfanas** (`cerebro_tareas_modelo.expirar()`) y **locks de PID muerto**
   (`ms.estado()`), que el sistema ya recicla solos.
3. **Avisar al usuario**: "la sesión anterior murió sin cerrar". NO asumir que el contexto está íntegro
   (la sesión pudo morir a mitad de una escritura no-atómica fuera de este helper).
4. Ofrecer **retomar** desde el próximo paso o **descartar**.

El banner lo imprime automáticamente el hook `SessionStart` (`recuperar --aviso`), que **calla** si el
cierre fue limpio o no hay checkpoint.

## Wiring (hooks en `.claude\settings.json`)
- `UserPromptSubmit` (2ª cmd, junto a "Hora local") → `py ...\cerebro_checkpoint.py auto` — auto-checkpoint
  por prompt. **Escribe a stderr** (el stdout de UserPromptSubmit se inyecta al contexto → debe quedar vacío).
- `Stop` → `py ...\cerebro_checkpoint.py auto` — auto-checkpoint al terminar cada turno del asistente.
- `SessionEnd` → `py ...\cerebro_checkpoint.py cerrar-limpio` (lee `session_id` por stdin → cierra su archivo).
- `SessionStart` (2º hook, junto al de `worker_instruccion.txt`) → `py ...\cerebro_checkpoint.py recuperar --aviso`
  (lee `session_id` por stdin para excluirse del escaneo).
- **stdin:** Claude Code pasa el JSON del evento por stdin; el `py` nativo lo hereda dentro de
  `powershell -Command` (NO usar `$input`, que falló en pruebas). `py` lo lee con `_payload_stdin()`.

## Verificación
- `py .cerebro\test_cerebro_checkpoint.py` (ciclo en-curso→recovery, cerrar-limpio→no-recovery, atomicidad).
- Simular crash: `checkpoint(...)` y NO cerrar → abrir sesión nueva → debe salir el banner. Tras
  `cerrar-limpio` → no sale.
