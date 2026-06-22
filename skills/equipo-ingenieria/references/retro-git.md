# CAPA D — Retrospectiva de ingeniería desde git

Recreado de gstack `/retro`. Produce una retro objetiva desde `git log` (no opiniones). Agnóstico al
stack — solo necesita git. Útil para auto-evaluación de un hito/semana y como entregable para clientes.

## Paso 1 — Recolectar (ajusta `--since`)
```bash
SINCE="1 week ago"   # o "2026-06-12", o un tag/rango
# Resumen por archivo (líneas +/- y churn):
git log --since="$SINCE" --numstat --pretty=format:'%H|%an|%ad|%s' --date=short
# Resumen compacto por commit:
git log --since="$SINCE" --shortstat --pretty=format:'%h %an %ad %s' --date=short
# Por autor:
git shortlog --since="$SINCE" -sn
# Hotspots (archivos más tocados):
git log --since="$SINCE" --name-only --pretty=format: | grep -v '^$' | sort | uniq -c | sort -rn | head -15
```

## Paso 2 — Calcular métricas
- **Commits**, **días activos**, **autores**.
- **SLOC lógico** (líneas netas sin blancos/comentarios — aproxima con +/- de `--numstat`, descontando lockfiles/generados).
- **Ratio de tests**: archivos/`líneas` de test vs de producción tocados (grep paths `test`/`spec`/`__tests__`).
- **Hotspots de churn**: los 5-10 archivos más modificados (candidatos a refactor/fragilidad).

## Paso 3 — Redactar la retro
Estructura sugerida:
1. **Tabla resumen**: | Métrica | Esta semana | Δ vs anterior |  (commits, SLOC, ratio tests, hotspots, días).
2. **Por autor** (si aplica multi-agente Claude/Codex): 1 *praise* anclado a un commit concreto + 1 *área de mejora* concreta.
3. **Hotspots y riesgos**: qué archivo concentró el churn y por qué; ¿deuda? ¿falta de tests?
4. **Tendencia**: comparación con la retro previa (mejoró el ratio de tests? bajó el churn?).
5. **Acciones** para el próximo hito (máx 3, accionables).

## Paso 4 — Persistir para comparar
Guarda un snapshot JSON en el proyecto para los deltas de la próxima retro:
```
.context/retros/AAAA-MM-DD.json   # {commits, sloc, test_ratio, hotspots, autores, dias}
```
La próxima vez, lee el snapshot anterior y rellena la columna "Δ vs anterior".

## Notas
- En Windows, los comandos van por Bash/git-bash; si hay presión de RAM (fork errors), corre los `git log`
  de a uno, no encadenados.
- Excluye lockfiles/`dist`/generados del conteo de SLOC para que las métricas no mientan.
- Es solo lectura de git: no toca el repo ni la config global.
