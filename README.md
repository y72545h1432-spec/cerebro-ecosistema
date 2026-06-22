# .cerebro — Ecosistema multi-agente (coordinación + memoria + reglas + skills)

> Un cerebro compartido para trabajar con **varios agentes de IA en paralelo** (Claude Code, Codex y
> futuros) sobre **varios proyectos**, sin que se pisen, sin perder contexto y sin gastar de más.
> Stdlib pura (sin dependencias para el núcleo), portable y **$0** por defecto.

🚀 **¿Recién clonaste? → [`SETUP.md`](SETUP.md)** (configura lo sensible en ~5 min). Lo no sensible ya viene listo.
🗂️ **Mapa completo de documentos → [`00_INDICE.md`](00_INDICE.md)** · Identidad y principios → [`ECOSISTEMA_MULTIAGENTE.md`](ECOSISTEMA_MULTIAGENTE.md).

---

## 1. ¿Para qué sirve?

Una sola persona, muchos proyectos, muchos agentes. El problema: los agentes de IA olvidan el contexto
entre sesiones, se pisan al editar lo mismo, repiten investigación ya hecha y queman tokens. Este
ecosistema resuelve eso con **cuatro piezas compartidas** que viven *fuera* de cualquier runtime:

| Pieza | Qué hace | Entrada |
|---|---|---|
| **Coordinación** | Locks, buzón, eventos y conocimiento entre sesiones en tiempo real (el "Paso 0") | `cerebro_multisesion.py` |
| **Memoria durable** | Un hecho por archivo + índice; recall por significado, no re-derivar | `cerebro_memoria.py` |
| **Adaptadores por runtime** | `CLAUDE.md` / `AGENTS.md` traducen el ecosistema a cada agente | (raíz de cada proyecto) |
| **Reglas y procesos** | Guardarraíles universales + rutinas reutilizables (docs numerados) | `00_INDICE.md` |

Beneficio neto: agentes que **comparten estado y conocimiento**, **no se pisan**, **retoman sin perder
contexto** y **eligen el modelo más barato** que sirva.

---

## 2. Instalación

Requisito: **Python 3.11+** (3.14 recomendado por `tomllib`). El núcleo es stdlib pura; las claves de
LLM son opcionales y gratis.

```bash
git clone <este-repo> .cerebro          # idealmente en ~/.cerebro (FUERA de OneDrive/Dropbox/Drive)
cd .cerebro
cp .env.example .env                     # (Windows: Copy-Item .env.example .env) — pega 1 clave gratis
py cerebro_init.py                        # detecta tus proyectos (dry-run) -> --confirm para guardar
# verificación (todo $0):
for t in test_cerebro_*.py; do py "$t"; done    # PowerShell: Get-ChildItem test_cerebro_*.py | % { py $_.Name }
```

Checklist completo (claves gratis, modo de pago opcional, verificación) en **[`SETUP.md`](SETUP.md)**.
Cómo dar de alta un proyecto propio: **[`ESTRUCTURA_PROYECTOS.md`](ESTRUCTURA_PROYECTOS.md)**.

> 💡 **Salud del PC:** pon el ecosistema y tus proyectos **fuera de carpetas que sincronizan a la nube**
> (OneDrive/Dropbox/Drive). La sync en caliente puede bloquear/corromper locks y estado. `cerebro_init.py` te avisa si detecta uno en la nube.

---

## 3. CLI único

Todo se despacha por un solo comando: `py cerebro.py <área> [args]`

| Área | Para qué |
|---|---|
| `coord` | multisesión: estado / locks / buzón / eventos |
| `memoria` | recordar / buscar / reindexar (memoria durable) |
| `tareas` · `modelo` | cola de tareas y router por modelo (reparte lo barato a tiers gratis) |
| `salud` | panel read-only de coordinación (locks tomados, dead-letters, conflictos) |
| `checkpoint` | recuperación post-crash (checkpoint atómico + RECOVERY al abrir) |
| `hechos` | hechos verificables (prueba comandos y guarda evidencia anti-discrepancia) |
| `grafo` | grafo de código on-demand (`simbolo` / `arquitectura`, vía `ast`, sin daemon) |
| `coprog` | co-programación: ownership y locks por archivo |

---

## 4. Reglas universales (guardarraíles)

Aplican a **todo** proyecto. Las clave (lista completa en el `CLAUDE.md` de cada proyecto):

1. **Confirmar antes de lo irreversible / externo / que gasta dinero.** La autorización en un contexto no se extiende al siguiente.
2. **Verificar en vivo con evidencia** antes de reportar algo como hecho (ver `cerebro_hechos.py`, regla #15).
3. **Nada de daemons/loops autónomos** sin decisión explícita del usuario.
4. **Acciones GUI** solo con foco verificado + usuario mirando + confirmación (`gui-control-seguro`).
5. **Paso 0 multisesión** antes de tocar archivos de un proyecto con posibles sesiones concurrentes.
6. **Revisar skills antes de implementar** algo de un tipo nuevo (lanza subagentes que busquen skills aplicables).
7. **Skills nuevas: verificar → unificar** (que funcionen y sean seguras; integrarlas sin duplicar).
8–16. Privacidad de memoria, documentación continua, **salud del PC primero**, mejora del ecosistema,
   comunicación viva segura, co-programación, hechos verificables, mejora continua de skills.

Calidad de salida (inspirada en Karpathy): **pensar antes de codear · simplicidad primero (nada
especulativo) · cambios quirúrgicos · ejecución por metas verificables.**

---

## 5. Procesos (abre solo el que aplique)

Documentos numerados, cada uno dueño de una rutina. No leerlos todos — el índice [`12_HUB_PROCESOS.md`](12_HUB_PROCESOS.md)
te manda al correcto. Los más usados:

- [`02_PROTOCOLO_OPERATIVO.md`](02_PROTOCOLO_OPERATIVO.md) — cómo entra y trabaja un agente.
- [`06_CONTRATO_NUEVO_AGENTE.md`](06_CONTRATO_NUEVO_AGENTE.md) — integrar un agente/runtime nuevo.
- [`09_MAPA_GLOBAL_MEMORIA.md`](09_MAPA_GLOBAL_MEMORIA.md) — dónde vive cada tipo de memoria.
- [`13_COMUNICACION_TIEMPO_REAL.md`](13_COMUNICACION_TIEMPO_REAL.md) — handoffs/bloqueos/progreso entre agentes.
- [`14_COPROGRAMACION_MULTIAGENTE.md`](14_COPROGRAMACION_MULTIAGENTE.md) — varios agentes escribiendo código junto.
- [`17_ROUTER_POR_MODELO.md`](17_ROUTER_POR_MODELO.md) — repartir tareas al tier más barato.
- [`19_RECUPERACION_POST_CRASH.md`](19_RECUPERACION_POST_CRASH.md) — continuidad ante muerte súbita.
- [`10_PRIORIDAD_SALUD_COMPUTADOR.md`](10_PRIORIDAD_SALUD_COMPUTADOR.md) — estabilidad/recursos primero.

---

## 6. Skills

Capacidades reutilizables que se disparan por su `description`. Mapa "qué invocar y cuándo":
[`SKILLS_CROSS_PROYECTO.md`](SKILLS_CROSS_PROYECTO.md) · convenciones y auto-mejora (R16):
[`CONVENCIONES.md`](CONVENCIONES.md). Incluidas en `skills/` (genericizadas):

- **De proceso/ingeniería:** `equipo-ingenieria` (operar como un equipo: reto de scope, gates por fase,
  cross-model, retro desde git), `investigacion-infinita` (investigar un tema hasta saturación
  semántica, con olas reanudables — su motor es `cerebro_research.py`), `gui-control-seguro` (input al
  escritorio con protocolo seguro), `arrancar-area`, `diseno`.
- **De dominio (destiladas de cientos de transcripts):** `marketing-digital`, `ia-aplicada`, `ecommerce`,
  `negocios`, `agencia-ia`, `video-editing`, `produccion-audiovisual`, `youtube-growth`.

Complementan (no reemplazan) las skills universales del runtime (planificación, TDD, debugging,
revisión, verificación).

---

## 7. Arquitectura y robustez

- **Base común** `cerebro_core.py` (stdlib): escritura atómica con respaldo `.bak`, JSONL append-only,
  `pid_alive`, mutex de proceso por **lock del SO** (sin TTL/race). Fuente única de esas utilidades.
- **Rutas robustas** `cerebro_paths.py`: detección de placeholders OneDrive, materialización, `state_dir`
  siempre local, resolutor de raíz de proyecto tolerante a carpetas movidas / nube deshidratada.
- **Gate de hardware** `cerebro_hardware_gate.py`: go/no-go de VRAM antes de actos caros (recurso global).
- **Memoria semántica** `cerebro_semantica.py`: recall por significado con degradación elegante
  (densos → TF-IDF sklearn → coseno stdlib): funciona sin GPU ni dependencias.
- Estado efímero en `%LOCALAPPDATA%\cerebro\` (locks/eventos/buzón) — local, nunca en la nube.

Árbol canónico completo: [`01_ARQUITECTURA.md`](01_ARQUITECTURA.md).

---

## 8. Privacidad — qué NO se sube

Este repo es la copia **pública y genérica**. **Cero datos personales** (gate verificado = 0). Quedan
fuera por diseño (`.gitignore` + el sincronizador): `memoria/`, estado/locks/buzón, `.env` y secretos,
`proyectos.local.toml` (tus proyectos reales), backups, imágenes de dashboards e investigación específica
de proyectos. Si añades algo sensible, agrégalo al `.gitignore`. Lo personal vive solo en tu copia local.

---

## 9. Tests

Stdlib puro, sin pytest. Cada módulo trae su `test_cerebro_*.py` (runner propio que imprime `N/N verde`):

```bash
for t in test_cerebro_*.py; do py "$t"; done      # todas las suites en verde
```

---

> Ningún agente es dueño del ecosistema: `.cerebro` coordina; cada runtime adapta.
