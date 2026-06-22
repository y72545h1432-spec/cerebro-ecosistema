---
name: arrancar-area
description: Use al EMPEZAR algo nuevo en cualquier proyecto del cerebro (~) — un proyecto nuevo, un área de conocimiento nueva, o una tarea de un tipo que no se venía haciendo (p.ej. "voy a empezar a hacer X", "nuevo proyecto", "primera vez que toco Y", "quiero meterme en Z"). Lanza subagentes que descubren qué skills/plugins aplican, las cablea en el CLAUDE.md correspondiente y registra el hallazgo. Operacionaliza la REGLA UNIVERSAL #6 del hub. Úsala incluso si el usuario no menciona "skills" — el disparador es la novedad del trabajo, no la palabra.
---

# arrancar-area — descubrir y cablear skills antes de empezar algo nuevo

## Por qué existe
En Claude Code una skill se dispara por su `description` (matching semántico), no por
estar instalada. Si al abrir un área nueva no se mira qué skills hay, el modelo trabaja
"a ciegas" y reinventa lo que una skill ya resuelve. Esta skill convierte ese reflejo en
un paso explícito: **investigar con subagentes → cablear → registrar**, para que el
acierto deje de depender del azar. Es el cumplimiento operativo de la **regla universal #6**.

## Cuándo dispararla
- Se crea/abre un **proyecto nuevo** (aún sin `CLAUDE.md` o sin sección de skills).
- Se abre un **área de conocimiento nueva** dentro de un proyecto existente (p.ej. tu-tienda
  empieza con email marketing, o tu-proyecto-web añade animación 3D).
- Se empieza una **tarea de un tipo que no se venía haciendo** (primera vez que se entrena
  un modelo, se hace regresión visual, se escribe un scraper, etc.).
- NO hace falta que el usuario diga "skills": el disparador es la **novedad** del trabajo.

Si el área ya está cableada en su `CLAUDE.md` y nada es nuevo, **no** la uses — es ruido.

## Procedimiento

### 1. Encuadrar
Identifica: ¿qué proyecto?, ¿qué es lo nuevo exactamente?, ¿qué stack/herramientas implica?
Mira el `CLAUDE.md` del proyecto y el mapa `~\.cerebro\SKILLS_CROSS_PROYECTO.md`
por si ya está cubierto.

### 2. Investigar con subagentes (el corazón de la skill)
Usa `superpowers:dispatching-parallel-agents` para el fan-out. Lanza **1–3 subagentes
`general-purpose` en paralelo** (uno por sub-dominio si el área es ancha; uno basta si es
estrecha). Cada subagente arranca en frío → dale TODO el contexto:
- la lista de skills disponibles (las del `available_skills` de la sesión + las globales
  en `~\.claude\skills\` + las del proyecto),
- el `CLAUDE.md`/memoria del proyecto y el stack,
- la pregunta: *"¿qué skills ya instaladas sirven a ESTA área y con qué disparador? ¿qué
  huecos recurrentes no cubre ninguna?"*

Pídele a cada uno una salida estructurada: (a) skills aplicables + disparador, (b) huecos.

### 3. Sintetizar y cablear
- Cruza los informes. Decide qué skills aplican.
- **Cablea** en el `CLAUDE.md` del proyecto un bloque "Skills útiles aquí" (skill →
  disparador). Si el `CLAUDE.md` no existe, créalo mínimo (qué es, stack, comandos, skills).
- Respeta las reglas duras del proyecto al cablear (p.ej. modo aprendizaje en tu-proyecto-aprendizaje:
  no recomendar skills que generen la solución de los ejercicios).
- Si una skill es claramente **cross-proyecto**, añádela también al mapa del hub.

### 4. Cubrir huecos (solo los reales)
Si hay un hueco **recurrente** sin skill, créala con `skill-creator`. No inventes skills
especulativas: si es de una sola vez, hazlo y ya. Si dudas, anótalo en el backlog del
mapa en vez de construirlo.

### 5. Registrar
- Añade/actualiza la fila del área en `~\.cerebro\SKILLS_CROSS_PROYECTO.md`.
- Registra el aprendizaje: `ms.conocimiento("cableadas skills para <área>", tags=["skills"])`
  (vía el `Multisesion` del hub).

## Regla de oro
Enlazar, no pegar (truco 16). El `CLAUDE.md` queda conciso: la skill + su disparador, y el
detalle vive en el mapa de `.cerebro`. El objetivo no es documentar por documentar, sino
que la **próxima** sesión que toque esa área sepa de inmediato qué invocar.
