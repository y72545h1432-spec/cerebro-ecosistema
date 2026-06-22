---
name: gui-control-seguro
description: Use cuando haya que CONTROLAR la GUI de Windows (mover/clicar ratón, escribir teclado, leer pantalla por OCR, ver la pantalla en vivo) vía ~\gui_control\ — en tu-proyecto-agente (computer-use), tu-tienda (acciones de navegador/escritorio) o cualquier tarea que pida "clica", "escribe en la ventana", "mira la pantalla", "automatiza esta app". Inyectar input en el escritorio en vivo es PELIGROSO: esta skill impone el protocolo seguro (foco verificado + usuario mirando + confirmación). Dispárala antes de cualquier acción de ratón/teclado real.
---

# gui-control-seguro — manejar la GUI sin disparos en el pie

Toolkit: **`~\gui_control\`** (`gui.py` ratón/teclado/OCR, `stream.py` MJPEG en
vivo, `winput.py` SendInput). Doc viva: `gui_control/README.md`. Sin deps nuevas.

## ⛔ Por qué hay que ir con cuidado (lección aprendida a las malas)
Las pulsaciones/clics globales van a la ventana **CON FOCO**. Si la terminal de Claude está
enfocada, "escribir" cae **en el propio prompt de Claude y se envía solo**; un modificador
pegado dispara atajos (abrió pestañas, inició Game Bar). Notepad Win11 es una sola ventana con
pestañas → `notepad.exe` agrega pestaña a los archivos REALES del usuario. Por eso el input
real es **acción irreversible/externa** → regla universal #1 + #4 del hub.

## Protocolo OBLIGATORIO antes de inyectar input
1. **Usuario mirando el stream.** Lanza `python gui_control/stream.py` y confirma que el usuario
   lo está viendo (a menudo desde el móvil). Sin observación → no inyectes.
2. **Fija la ventana objetivo.** `python gui_control/gui.py target "<Título>"` → se auto-activa
   en cada comando (mata el robo de foco de la terminal).
3. **Re-verifica el foco ANTES de cada chunk.** Comprueba `GetForegroundWindow` / usa el
   `activate` de `gui.py`; nunca asumas que el foco sigue donde lo dejaste.
4. **Confirma con el usuario** la acción concreta antes de ejecutarla (qué se clica/escribe).
5. **`type` > `paste`** si el foco es dudoso; para texto Unicode/combos Win usa `winput.py`
   (SendInput; pyautogui falla con la tecla Win en Win10/11). Suelta modificadores al terminar
   (`release_modifiers()`).

## Capacidades (para no cazar coordenadas a mano)
- **Clic por OCR:** `gui.py clicktext "texto"` / `find "texto"` (winocr, sin Tesseract).
- **Esperar y clicar cuando aparezca:** `gui.py waittext "texto" [timeout] [--click]` (automatiza
  sin adivinar tiempos).
- **Rejilla de coords:** `gui.py grid` · **capturas:** `shot` / `shot-region X Y W H` (zoom texto chico).
- **Salud:** `gui.py doctor` (¿OCR ok?) · stream `/healthz` (RAM/cursor/fps) — útil con RAM al
  límite (`feedback_recursos_pc`).
- **Control desde el móvil:** `stream.py` v5 (tap=clic, swipe=scroll, barra de teclas). En red
  compartida usa `--token`.

## Verificación
Tras cada acción, **mira el stream / haz `shot`** y confirma el efecto real antes de seguir
(regla "verificar en vivo con evidencia"). En tu-proyecto-agente, reporta **cada intento paso a paso**
(`feedback_piloto_informar_intentos`).

> Detalle y backlog en `gui_control/README.md §SEGURIDAD`. Relacionado:
> `reference_gui_control_tooling`, `feedback_acciones_estrictas`, `project_piloto_agente`.
> Si mejoras los scripts, anótalo en el changelog del README (`feedback_actualizar_skills`).
