# CAPA B — Gates verificables por fase + anti-racionalización

Recreado de addyosmani/agent-skills (su diferenciador: "exit criteria, not more prompt lore").
Vuelve `verification-before-completion` CONCRETO: no avanzas de fase sin pegar EVIDENCIA, no juicio subjetivo.

## Regla madre
**No avanzas a la siguiente fase hasta validar la actual.** Cada checkbox se marca con evidencia
pegada (output de comando, ruta, número), no con "ya está".

## Gates por fase

### Spec / Plan
- [ ] El problema y el usuario están definidos (no "todos").
- [ ] Criterios de aceptación verificables escritos (qué prueba que está hecho).
- [ ] Leíste el código relevante ANTES de escribir la spec (no asumiste la estructura).
- [ ] Capa A (reto-scope) cerrada: modo declarado.

### Build (por tarea)
- [ ] Para bugs: test que reproduce y **FALLA antes** del fix (Red→Green).
- [ ] Suite completa corre sin regresiones — pega el resumen del runner.
- [ ] Build/compilación OK — pega la última línea.
- [ ] **Staging selectivo, nunca `git add -A`** — cada commit traza a la petición.
- [ ] Cero cambios "de paso" no pedidos (tu regla #3 Calidad de Salida).

### Review (antes de merge)
- [ ] Todos los hallazgos Críticos resueltos (no "se ve bien").
- [ ] `pr-review-toolkit` / `code-review` pasado; security-review si toca datos/auth/red.
- [ ] **Historia de verificación documentada**: qué cambió, cómo se verificó, qué se probó.

### Ship (mejora a `commit-push-pr`)
- [ ] Tests verdes (no se pushea en rojo).
- [ ] **Hubo un review reciente** (< N días) — si no, revisar antes de shippear.
- [ ] Commits **bisectables** ordenados (infra → modelos → controladores → docs/changelog al final).
- [ ] Diff acotado: cada línea traza a la tarea.
- [ ] (Shopify-Liquid: omite VERSION semver; valida el theme con tu skill de liquid/web-quality-audit.)

## Tabla anti-racionalización (excusa del agente → realidad)
| Excusa | Realidad |
|---|---|
| "El código generado por IA probablemente está bien" | El código de IA necesita MÁS escrutinio, no menos. |
| "Parece correcto / debería funcionar" | "Parece" no es "probado". Corre el test. |
| "Es un cambio pequeño, no hace falta test" | Los cambios pequeños rompen cosas grandes. Test o no-hecho. |
| "Refactorizo de paso mientras estoy aquí" | Cambio quirúrgico: solo lo pedido. Lo demás se menciona, no se toca. |
| "`git add -A` es más rápido" | Staging selectivo o un commit incluye basura no relacionada. |
| "Lo documento después" | Después = nunca. La historia de verificación va ahora. |

**Salida de la capa B:** fase cerrada solo cuando su bloque de checkboxes está marcado CON evidencia.
