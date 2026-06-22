# CAPA A — Reto de scope/producto antes de codear

Recreado de gstack `/plan-ceo-review` + `/office-hours`. Se aplica sobre un plan YA escrito
(output de `superpowers:writing-plans`), ANTES de tocar código. Pura guía conversacional.

## Paso 1 — Forcing questions de producto (la cara "office-hours")
Antes de validar el *cómo*, reta el *qué*. Hazte (y si aplica, al usuario) estas 6:
1. **Demanda real vs hipotética** — ¿alguien pidió esto, o lo asumimos? ¿Evidencia concreta?
2. **Costo de no hacerlo** — si NO construimos esto, ¿qué se rompe o se pierde? ¿Dolor real o teórico?
3. **Wedge mínimo** — ¿cuál es la versión más pequeña que alguien querría usar/pagar ESTA semana?
4. **Especificidad del usuario** — ¿para quién exactamente? Un "todos" es una señal de alarma.
5. **Observado vs supuesto** — ¿esto lo viste pasar, o lo estás infiriendo?
6. **Future-fit** — ¿nos acerca al objetivo a 12 meses, o es un desvío que habrá que deshacer?

Si 2+ respuestas son débiles → el plan probablemente resuelve el problema equivocado. Dilo antes de codear.

## Paso 2 — Reta la premisa (la cara "CEO-review")
- No critiques solo el diseño técnico; **cuestiona si el problema es el correcto**.
- Mapea explícitamente: **estado actual → lo que este plan deja → ideal a 12 meses**. ¿El plan acerca al ideal?
- Nombra el supuesto más frágil del plan y qué pasaría si es falso.

## Paso 3 — Ofrece 2-3 enfoques (no elijas en silencio — tu regla #1 Calidad de Salida)
Presenta con `AskUserQuestion`, p.ej.:
- **Mínimo viable** — lo más chico que valida la hipótesis (rápido, deuda controlada).
- **Arquitectura ideal** — bien hecho de raíz (más lento, menos retrabajo).
- **Reducción** — recortar el plan a su núcleo, posponer el resto.
Da una **recomendación** (no un catálogo neutro), con el trade-off de cada uno.

## Paso 4 — Declara el MODO y por qué
Elige uno explícitamente y anótalo en el plan:
| Modo | Cuándo | Efecto |
|---|---|---|
| **Expansión-10x** | apuesta estratégica, ventana de oportunidad | piensa en grande, acepta más scope |
| **Selectiva** | crecer solo donde el ROI es claro | añade 1-2 cosas de alto valor, corta el resto |
| **Hold-rigor** | el plan está bien dimensionado | no toques scope, sube el listón de calidad |
| **Reducción-ruthless** | scope inflado, plazos/recursos ajustados | corta a lo esencial, pospón lo demás |

**Salida de la capa A:** un plan con premisa retada, modo declarado y enfoque elegido por el usuario.
NO empieces a codear hasta cerrar esto.
