# Arranque de una sesión BARATA (Haiku/Sonnet) — 5 pasos

Para una sesión de modelo barato dedicada a trabajo mecánico/verificable (ahorro de tokens).

1. **Paso 0** (coordinación): `import sys; sys.path.insert(0, r"~\.cerebro")` →
   `from cerebro_multisesion import Multisesion; ms = Multisesion("trabajo mecanico", project="<proj>", agent="claude", runtime="claude-code")`.
2. **Ver mi cola** (por modelo): `py -3 ~\.cerebro\cerebro_tareas_modelo.py pendientes haiku`
   (o `sonnet`). Incluye las dirigidas a tu tier + las `any`.
3. **Tomar UNA** (atómico): `... cerebro_tareas_modelo.py tomar <id> --por <tu-sesion>`. Cada tarea trae
   `--archivo`/`--prueba`/`--terminado`: hazla exactamente hasta ese criterio.
4. **Antes de editar un `.py`:** `py -3 ...\cerebro_coprog.py board <proj>` + `cop.claim_all(ms, ...)`;
   si está tomado, NO edites. Corre la `--prueba` declarada antes de cerrar.
5. **Cerrar:** `... cerebro_tareas_modelo.py completar <id> -n "resultado + prueba verde"`. Si te quedas
   sin tareas, `tablero` para ver el resto o avisa por el buzón.

Hábitos de tokens (aplican igual): `.cerebro\TOKENS_HABITOS.md`. No re-leas docs enteros: `cerebro_memoria.py buscar`.
