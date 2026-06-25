---
name: escribir-menos-codigo
description: Distilled from the `DietrichGebert/ponytail` skill (MIT) — makes the agent write the least code that fully solves the task ("the best code is the code you never wrote"). Use BEFORE writing or adding any code — implementing a feature, fixing a bug, adding a dependency, scaffolding, or refactoring — to avoid over-engineering, dead abstractions, and unnecessary dependencies that cost tokens, bugs and review time. A 7-rung YAGNI decision ladder + non-negotiable safety floor. Operationalizes "Calidad de Salida §2 (Simplicidad primero)" of CLAUDE.md; complements `superpowers:test-driven-development` and the token habits. NOT a code-golf / cleverness skill, and NOT for prose.
---

# Escribir menos código — destilado de `ponytail` (DietrichGebert, MIT)

> **Lo crítico primero** (la truncación conserva el inicio). Antes de escribir UNA línea, sube la
> escalera y quédate en el peldaño MÁS ALTO que resuelva el problema de verdad. "El mejor código es
> el que nunca escribiste." Es comportamiento (texto-guía), no un plugin: cero RAM/red.
> **Número honesto** (benchmark agéntico del repo, Haiku 4.5, 12 tareas en FastAPI+React real):
> **−54% líneas, −22% tokens, −20% costo, −27% tiempo, 100% seguro.** El "−77%/90%" de los videos
> es la medición *single-shot* vieja que el propio autor retractó. Detalle: `.cerebro\REGISTRO_SKILLS_EXTERNAS.md`.

## La escalera de decisión (7 peldaños — para en el más alto que aplique)
1. **¿Necesita existir?** → si no, NO lo escribas (YAGNI). La feature no pedida, la abstracción de un
   solo uso, el "por si acaso", el manejo de errores para escenarios imposibles: no van.
2. **¿Ya está en el código?** → reúsalo. Busca antes (`Grep`, `cerebro_grafo.py simbolo`, `cerebro_memoria buscar`).
3. **¿Lo resuelve la stdlib?** → úsala antes que una dependencia.
4. **¿Hay una feature NATIVA de la plataforma?** → úsala (ej: `<input type="date">` en vez de instalar
   un date-picker: 404 → 23 líneas). HTML/CSS/SQL/OS nativo antes que una librería.
5. **¿Una dependencia YA instalada lo hace?** → úsala antes de añadir una nueva.
6. **¿Cabe en una línea / una función chica?** → hazlo así.
7. **Fallback:** el mínimo viable que pasa el caso real. Nada especulativo.

## Suelo de seguridad — NO NEGOCIABLE (nunca se recorta por "menos código")
Validación de límites de confianza (input no confiable), manejo de pérdida de datos, seguridad
(authz/secretos/inyección) y **accesibilidad** se mantienen SIEMPRE. "Menos código" es quitar lo
superfluo, no quitar guardas. Si dudas entre una guarda y una línea menos: la guarda gana.

## Regla de oro
**Perezoso con la SOLUCIÓN, nunca con la LECTURA.** Traza el flujo real (lee el código que tocas)
antes de elegir peldaño — la pereza informada elige el peldaño alto; la pereza ciega rompe cosas.
Pregúntate al terminar: *"¿un senior diría que esto está sobre-complicado?"* Si escribiste 200
líneas y caben en 50, reescribe (Calidad de Salida §2).

## Cuándo NO aplica
- No es code-golf: legibilidad > brevedad astuta. Una línea ilegible NO gana a tres claras.
- No toca prosa/docs (usa las skills de escritura).
- En `tu-proyecto-aprendizaje` (modo aprendizaje): guía sobre lo que el usuario YA escribió — **nunca** rellenes `# TODO (tú)`.

## Auto-revisión rápida (mental, antes de cerrar)
- ¿Cada línea nueva traza directo a la petición? (Calidad de Salida §3, cambios quirúrgicos)
- ¿Añadí dep/abstracción/config que nadie pidió? → bórrala.
- ¿Recorté alguna guarda del suelo de seguridad? → repón.

---
<!-- changelog -->
- 2026-06-24 · v1 · Destilada de `DietrichGebert/ponytail` (MIT) a skill nativa (sin plugin/Node). Unifica con CLAUDE.md "Calidad de Salida §2".
