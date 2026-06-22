# SETUP — Configuración inicial del ecosistema

> **Para la sesión (IA o persona) que abre este repo recién clonado.**
> El repo trae configurado todo lo **NO sensible** (código, tests, docs, defaults, plantillas).
> Aquí completas lo **SENSIBLE** (claves, rutas de tu máquina, memoria privada), que **nunca** vive en el repo.
>
> 🔐 **Regla de oro para una IA que ejecute este setup:** los secretos los provee el HUMANO. Nunca
> inventes, adivines ni hardcodees una clave; nunca la subas a git. Si falta un dato sensible, **pídeselo
> al usuario** y para hasta tenerlo.

---

## ✅ Lo que YA viene configurado (no toques, es público y portable)
- **Código y tests**: `cerebro_*.py` + `test_cerebro_*.py` (stdlib pura).
- **CLI único**: `py cerebro.py <area> [args]` (tareas/modelo/coord/salud/watch/checkpoint/hechos/memoria/coprog/grafo/skills).
- **Plantillas**: `.env.example`, `.gitignore` (ya protege secretos y memoria).
- **Convenciones de trabajo**: `CONVENCIONES.md` (reglas generales + calidad + hábitos + auto-mejora de skills R16).
- **Skills propias** (genericizadas) en `skills/` — se disparan por su `description`; índice en `CONVENCIONES.md`.
- **Código portable**: las rutas se derivan de `Path(__file__)` / `Path.home()` — funciona desde cualquier usuario/ruta sin editar nada.
- **Auto-config de proyectos**: `cerebro_init.py` (detecta tus proyectos) + `proyectos.example.toml` (plantilla) + guía `ESTRUCTURA_PROYECTOS.md`.

## 🔧 Lo SENSIBLE que debes completar (checklist)

### 1. Claves de los proveedores gratis ($0) — al menos una
- [ ] Copia la plantilla:  `cp .env.example .env`  (en Windows: `Copy-Item .env.example .env`)
- [ ] Consigue **al menos una** clave gratis (sin tarjeta) y pégala en `.env`:
  - Groq → https://console.groq.com
  - Google Gemini → https://aistudio.google.com/apikey
  - OpenRouter → https://openrouter.ai/keys
- [ ] Carga el `.env` en tu shell (ver comandos dentro de `.env.example`).
- [ ] Verifica:  `py -c "import cerebro_llm; print(cerebro_llm.proveedores_listos())"`  → debe listar tu(s) proveedor(es).
> ⚠️ `.env` está en `.gitignore`: **no se sube**. Solo `.env.example` (sin claves) se versiona.

### 2. (Opcional) Modo de PAGO con Claude — máxima calidad
- [ ] Instala el CLI `claude` y autentícate (suscripción o API).  Verifica: `claude --version`.
- [ ] Sin esto, usa solo modo gratis: `--modo gratis` (todo $0). Con Claude disponible, el híbrido manda lo difícil a Claude.

### 3. Tus proyectos (auto-config, fácil)
- [ ] Detéctalos y regístralos:  `py cerebro_init.py`  (dry-run, muestra qué haría) → `py cerebro_init.py --confirm` (guarda).
- [ ] O a mano: copia `proyectos.example.toml` → `proyectos.local.toml` y añade tus proyectos (gitignored).
- [ ] **Salud del PC:** pon los proyectos **fuera de OneDrive/Dropbox/Drive** (la sync en caliente corrompe/bloquea archivos). `cerebro_init.py` te avisa si detecta uno en la nube. Detalle: `ESTRUCTURA_PROYECTOS.md`.
- [ ] No hace falta tocar rutas del código: es portable (`Path(__file__)`/`Path.home()`). El estado efímero se crea solo en `%LOCALAPPDATA%\cerebro\`.

### 4. Memoria y estado privados (empiezan vacíos — es lo correcto)
- [ ] La carpeta `memoria/` **no viene en el repo** (es personal). Se crea sola al primer `cerebro_memoria.py recordar ...`.
- [ ] Lo mismo con backups, handoffs (`.remember/`) e investigación de proyectos: son privados y quedan fuera por diseño.

### 5. Verificación final (todo $0)
- [ ] Suite completa en verde:
  - bash: `for t in test_cerebro_*.py; do py "$t"; done`
  - PowerShell: `Get-ChildItem test_cerebro_*.py | ForEach-Object { py $_.Name }`

---

## 🚫 Qué NO subir nunca (lo aplica `.gitignore` + `cerebro_sync_repo.py`)
Claves/`.env`, `memoria/`, `estado/`/`state/`, `_backups/`, `.remember/`, locks/buzones/eventos, `*.bak`,
imágenes de dashboards, e investigación específica de tus proyectos. Si añades algo sensible nuevo,
agrégalo a `.gitignore` **y** a la lista `EXCLUDE_*` de `cerebro_sync_repo.py`.

## 🔄 Mantener una copia pública en sync (solo si mantienes un ecosistema privado propio)
El repo público se genera desde un ecosistema privado con `cerebro_sync_repo.py`, que **no se publica**
(lleva la denylist con datos personales del autor; es herramienta del mantenedor, no del repo). Si tú
mantienes tu propio espejo, ese script: espeja `.cerebro` excluyendo lo privado, **genericiza** todo el
texto (rutas/usuario/proyectos/secretos → placeholders) y deja `proyectos.local.toml` fuera. Tras cada
cambio en el original, se vuelve a correr y la copia queda limpia (scan de datos personales = 0).
