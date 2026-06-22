# CAPA C — Revisión cross-model (handoff a Codex)

Recreado de gstack `/codex`. Idea: todos tus revisores son Claude; una 2ª opinión de OTRO modelo
(Codex/GPT) caza cosas que un solo modelo no ve. **Aporta diversidad de modelo, no más del mismo.**

## Realidad de tu entorno (honestidad ante todo)
- **No hay `codex` CLI invocable desde esta sesión.** No puedo llamar a Codex automáticamente.
- Tu Codex es un **runtime separado** (arranca por `AGENTS.md`), coordinado por `.cerebro`.
- Por lo tanto esto es un **handoff**, no un paso automático. Si no hay sesión Codex viva, **dilo** —
  no inventes ni finjas una segunda opinión (tu regla #2: verificar con evidencia; #13 comunicación).

## Protocolo de handoff
1. **Empaqueta** el material para Codex:
   - El diff a revisar (`git diff <base>...HEAD` o rango del PR).
   - Contexto: qué hace el cambio, qué dudas tienes, qué NO mirar (para no repetir tu review Claude).
   - Criterio de salida: "reporta solo bugs reales con línea exacta y confianza ≥ 7/10".
2. **Publica el handoff** por tu canal vivo `.cerebro` (regla #13):
   ```python
   import sys; sys.path.insert(0, r"~\.cerebro")
   from cerebro_multisesion import Multisesion
   ms = Multisesion("review cross-model", project="<proyecto>", agent="claude", runtime="claude-code")
   ms.mensaje_tipo("review", "Codex: revisa este diff <ruta/PR>. Busca lo que un revisor Claude no vería. "
                   "Solo hallazgos con línea exacta + confianza >=7. Contexto: <...>")
   ```
   (o el verbo de handoff/`ack` que uses; observa la respuesta con `cerebro_watch.py --once`.)
3. **Al volver de Codex:** filtra. Acepta solo hallazgos que:
   - citen **archivo:línea exacta**, y
   - tengan confianza ≥ umbral (7/10 por defecto).
   Descarta lo genérico/estilístico sin línea. Marca **pass/fail** del gate.
4. Si Codex no está disponible → registra "2ª opinión cross-model NO realizada (sin sesión Codex)" y sigue;
   no cuentes el review como cross-model si no lo fue.

## Cuándo SÍ vale la pena
- Cambios de alto riesgo (pagos, auth, datos, lógica de negocio crítica de tu-tienda).
- Cuando tu review Claude salió "limpio" pero la intuición dice que algo falta (diversidad de modelo).
No para cada diff trivial — el handoff tiene costo de coordinación.
