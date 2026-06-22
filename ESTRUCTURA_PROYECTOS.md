# Cómo estructurar un proyecto en el ecosistema

Guía para añadir un proyecto propio al ecosistema multi-agente. Lo del ecosistema (coordinación,
memoria, checkpoint, equipo) ya viene hecho; esto es solo **lo personal de cada proyecto**. Para
integrar un *agente/runtime* nuevo (no un proyecto), ver `06_CONTRATO_NUEVO_AGENTE.md`.

> Atajo: `py cerebro_init.py` detecta tus carpetas de proyecto y propone registrarlas;
> `--confirm` las guarda en `proyectos.local.toml`. Esta guía es el "a mano / qué significa".

---

## 1. Dónde vive (SALUD DEL PC: fuera de la nube)
- Pon el proyecto en una ruta local **fuera de carpetas que se sincronizan a la nube**
  (OneDrive, Dropbox, Google Drive, iCloud). La sync en caliente puede **bloquear o corromper**
  archivos de trabajo (locks, `node_modules`, `.git`, estado) → fallos difíciles de depurar.
- Recomendado: `~/<proyecto>` (p.ej. `C:\Users\<tu>\miapp`) o cualquier disco local no sincronizado.
- El ecosistema mismo (`.cerebro`, `.remember`, estado en `%LOCALAPPDATA%`) ya está fuera de la nube.

## 2. Registrarlo (lo personal va a config, no al código)
Los proyectos son **personales** → no se hardcodean. Viven en `proyectos.local.toml` (gitignored).
- Auto: `py cerebro_init.py --confirm`.
- A mano: copia `proyectos.example.toml` → `proyectos.local.toml` y añade un bloque:
  ```toml
  [[proyecto]]
  nombre  = "miapp"          # minúsculas; = área de memoria + inferencia por cwd
  ruta    = "~/miapp"        # admite ~ y rutas absolutas (/ o \)
  que_es  = "qué es en una línea"
  entrada = "CLAUDE.md"      # archivo de entrada (CLAUDE.md o AGENTS.md)
  ```
Al registrarlo, `cerebro_memoria` le da un **área de memoria** propia y `cerebro_checkpoint`
**infiere el proyecto** desde el `cwd` automáticamente.

## 3. Adaptador de entrada por runtime
Crea en la raíz del proyecto el adaptador del runtime que uses (mínimo viable):
```md
# CLAUDE.md — <proyecto>

> Vive en `~/<proyecto>` (fuera de la nube). Hub raíz: `..\CLAUDE.md`.
> Fuente neutral del ecosistema: `~/.cerebro/00_INDICE.md`.

## Qué es
<una o dos líneas>

## Arranque
1. Paso 0 multisesión con `project="<proyecto>"` antes de tocar archivos.
2. Leer la memoria durable compartida (`~/.cerebro/memoria/MEMORIA.md`) — buscar antes de re-derivar.
```
- Para Codex u otros, replica como `AGENTS.md` delegando en `CLAUDE.md` (ver `06_CONTRATO_NUEVO_AGENTE.md`).
- Mantén el adaptador **conciso**: enlaza al ecosistema, no copies sus reglas.

## 4. Paso 0 (coordinación) antes de tocar archivos
Siempre, en cualquier runtime:
```python
import sys; sys.path.insert(0, str(__import__("pathlib").Path.home() / ".cerebro"))
from cerebro_multisesion import Multisesion
ms = Multisesion("qué haces", project="<proyecto>", agent="claude", runtime="claude-code")
ms.estado(); ms.reclamar("<recurso>"); ms.leer_buzon(); ms.despedir()
```
Recursos físicos compartidos (GPU, un servicio local) → `ms.reclamar("<x>", scope="global")`.

## 5. Memoria por proyecto
- Hechos durables del proyecto → `cerebro_memoria.py recordar` con `project="<proyecto>"`
  (van a su área; el índice `MEMORIA.md` es común). **No** crees una memoria paralela.
- Aprendizajes en caliente reutilizables → `ms.conocimiento("...", tags=[...])`.
- Lo en-curso al cerrar → handoff (`.remember/remember.md`) + cola/árbol de tareas; al abrir, léelo.

## 6. Checklist de alta de proyecto
- [ ] Carpeta del proyecto **fuera de OneDrive/Dropbox/Drive**.
- [ ] Registrado en `proyectos.local.toml` (vía `cerebro_init.py` o a mano).
- [ ] Adaptador `CLAUDE.md` (y `AGENTS.md` si usas Codex) en la raíz.
- [ ] Paso 0 probado: `Multisesion(..., project="<proyecto>")` corre sin error.
- [ ] `cerebro_memoria.py buscar --project <proyecto>` responde (área creada al primer `recordar`).
- [ ] Nada personal/secreto hardcodeado en el código (usa `.env` gitignored + config local).
