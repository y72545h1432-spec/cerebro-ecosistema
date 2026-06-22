---
name: equipo-ingenieria
description: Playbook para operar como un EQUIPO de ingenieros (no un solo coder) al planear, construir, revisar, shippear o hacer retrospectiva de un proyecto. Úsalo cuando el usuario pida "rigor de equipo", retar el alcance/scope de un plan antes de codear, gates verificables por fase, una segunda opinión cross-model (Codex), o una retrospectiva de ingeniería desde git. Complementa (NO reemplaza) superpowers, feature-dev y pr-review-toolkit. Destilado de garrytan/gstack y addyosmani/agent-skills (verificados 2026-06-19, no instalados). NOT FOR la revisión de código en sí (usa pr-review-toolkit/code-review), debugging (systematic-debugging), ni a11y/CWV/perf (ya tienes accessibility/core-web-vitals/performance/web-quality-audit).
---

# Equipo de ingeniería (capas alrededor del código)

Tu stack ya cubre el núcleo: **plan** (`superpowers:writing-plans`, `feature-dev:code-architect`),
**build** (`superpowers:test-driven-development`, `subagent-driven-development`), **review**
(`pr-review-toolkit` 6 ángulos, `code-review`, `security-review`), **debug** (`systematic-debugging`),
**verify** (`verification-before-completion`). Esta skill añade las CUATRO capas que ese stack NO tiene,
en el momento correcto. Aplica solo la sección que corresponde — no recorras todo de corrido.

> Origen: ideas verificadas de `garrytan/gstack` (16k★) y `addyosmani/agent-skills`. Recreadas
> nativas (markdown puro, sin bash de terceros, sin tocar config global). Detalle por capa en `references/`.

---

## CAPA A — Reto de scope/producto ANTES de codear  → `references/reto-scope.md`
**Cuándo:** justo después de escribir un plan (output de `writing-plans`) y ANTES de tocar código.
**Por qué:** tu stack diseña *cómo* construir bien, pero nadie reta *qué* y *cuánto*. Aquí decides si el
plan resuelve el problema correcto y con qué ambición.
**Qué haces (resumen — detalle en la reference):**
1. **Forcing questions de producto** (6): ¿demanda real o hipotética? ¿qué pasa si NO lo hacemos? ¿wedge
   mínimo que alguien querría esta semana? ¿el usuario es específico? ¿lo observaste o lo asumes? ¿future-fit?
2. **Reta la premisa**, no solo el diseño. Mapea **estado actual → este plan → ideal a 12 meses**.
3. Ofrece **2-3 enfoques** (mínimo-viable vs arquitectura-ideal vs reducción) con `AskUserQuestion`.
4. Elige un **modo**: Expansión-10x / Selectiva / Hold-rigor / Reducción-ruthless. Declara el modo y por qué.
> Pura guía, portable a Python/Shopify/cualquier proyecto.

## CAPA B — Gates verificables por fase + anti-racionalización  → `references/gates-y-anti-racionalizacion.md`
**Cuándo:** al cerrar cada fase (spec / build / review / ship). Refuerza `verification-before-completion`
volviéndolo **concreto y con evidencia** (no "parece bien").
**Qué haces:** antes de declarar una fase "hecha", pega el bloque de checkboxes de esa fase (en la reference)
y rellénalo con EVIDENCIA real (output de tests, build OK, diff acotado). Reglas duras heredadas:
- **"Tests son prueba — 'parece correcto' no es hecho".** Para bugs: test que reproduce y FALLA antes del fix.
- **Nunca `git add -A`** — staging selectivo, cada commit traza a la petición (tu regla #3 Calidad de Salida).
- **No avanzas de fase** hasta validar la actual.
- Consulta la **tabla anti-racionalización** (excusa → realidad) para no caer en el atajo del agente.

## CAPA C — Revisión cross-model (handoff a Codex)  → `references/cross-model-codex.md`
**Cuándo:** tras un review interno fuerte, cuando quieras diversidad de MODELO (todos tus revisores son Claude).
**Realidad de tu entorno:** no hay `codex` CLI invocable desde aquí. Así que NO es automático: se hace por
**handoff a una sesión Codex** vía tu buzón `.cerebro` (`ms.mensaje_tipo(...)` / handoff estructurado).
**Qué haces (detalle en la reference):** empaqueta el diff + contexto + "qué dudas tienes", publícalo como
handoff de review a Codex, y al volver: solo aceptas hallazgos que **citen línea exacta** y con confianza ≥ umbral.
Gate pass/fail. Si no hay sesión Codex viva, dilo — no finjas la 2ª opinión.

## CAPA D — Retrospectiva de ingeniería desde git  → `references/retro-git.md`
**Cuándo:** al cerrar una semana/hito, o como entregable para un cliente.
**Qué haces:** corres los comandos `git log` de la reference y produces: tabla resumen (commits, SLOC lógico,
ratio de tests, hotspots de churn, días activos), praise anclado a commits + 1 área de mejora, y **deltas vs la
retro anterior** (guardas snapshot en `.context/retros/AAAA-MM-DD.json` del proyecto). Solo git, agnóstico al stack.

---

## Lo que esta skill NO hace (ya lo tienes — no dupliques)
- Revisión de código por ángulos → `pr-review-toolkit`, `code-review`. · Seguridad → `security-review`.
- Debugging → `systematic-debugging`. · Simplificar → `code-simplifier`/`simplify`.
- a11y / Core Web Vitals / performance del storefront → `accessibility`, `core-web-vitals`, `performance`, `web-quality-audit`.
- Memoria/learnings → `remember`, `claude-md-management`.

## Integración con tu flujo
`brainstorming` → `writing-plans` → **[CAPA A: reto-scope]** → `TDD`/`subagent-driven-development`
→ **[CAPA B: gates por fase]** → `pr-review-toolkit` → **[CAPA C: cross-model si aplica]** →
`commit-push-pr` (+ gates de ship de CAPA B) → **[CAPA D: retro al cerrar hito]**.
