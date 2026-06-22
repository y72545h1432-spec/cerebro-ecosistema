---
name: investigacion-infinita
description: >-
  Proceso preestablecido de investigación EXHAUSTIVA de un tema hasta saturación. Úsalo siempre
  que el usuario pida "investigación infinita", "investiga todo sobre X", "barre X de punta a punta",
  "investiga hasta que no quede nada", "ramas y sub-ramas", "investigación exhaustiva/profunda hasta
  agotar", o quiera mapear por completo un área (estado del arte + huecos + backlog accionable).
  Recorre ramas → sub-ramas desde varios enfoques, PARA por repetición semántica (no por agotar un
  temario), avanza en olas con checkpoint reanudable, y respeta el ecosistema (memoria, tareas, locks,
  salud del PC). No es para preguntas puntuales de una sola respuesta.
---

# Investigación Infinita

Investigar un tema **hasta saturación**: no termina por cubrir un temario fijo, sino cuando dejan de
aparecer ramas/sub-ramas nuevas (convergencia, como la saturación teórica cualitativa). "Infinita" =
**finita pero abierta**.

## Cuándo NO usarla
Preguntas de una sola respuesta, lookups puntuales, o tareas con alcance cerrado. Esto es para barrer
un **área entera** y dejar mapa + backlog.

## Lo que produce (doble objetivo)
1. **Mapa de conocimiento**: `GRAFO.md` (árbol navegable de ramas/sub-ramas con resumen+fuentes+
   enfoque+Recomendación #1) + un hecho durable por nodo en la memoria compartida.
2. **Backlog accionable**: cada *Recomendación #1* → ítem priorizado para implementar.

## El motor (ya implementado y testeado)

Implementación de referencia en `~\tu-proyecto-agente\research\INVESTIGACION_INFINITA\`:
- `investigacion_infinita.py` — máquina de estado: dedup semántico, contadores de saturación,
  rotación de enfoques, persistencia, render del mapa.
- `runner.py` — orquestación por olas con checkpoint. **No corre solo** (regla #3: nada autónomo).
- `DISENO.md` / `PLAN.md` — diseño y plan completos.

Para investigar **otro tema** (no tu-proyecto-agente): copia esos dos `.py` al dir del tema (o apunta
`runner.RUTA_ESTADO`/`RUTA_GRAFO` al dir del tema). El motor es genérico, sin lógica de tu-proyecto-agente.

## Algoritmo (bucles de saturación anidados)

Niveles: **L0** tema · **L1** ramas · **L2** sub-ramas (L3+ recursivo si una sub-rama lo pide).
**Enfoques** = lentes rotatorias, ampliables en caliente. Semilla: neurociencia · SOTA-computer-use ·
training/LoRA · tokens/eficiencia · infra-opensource · datos/datasets · seguridad/robustez · percepción/UX.

```
para cada ENFOQUE E (rotando):
    generar ramas(L1) del tema vistas desde E
    para cada rama NUEVA (no repetida):  inv.nueva_rama()
        para cada ENFOQUE E' (rotando):
            generar sub-ramas(L2) desde E'; investigar las NUEVAS
            si inv.rama_saturada():  romper bucle interno   # K sub-ramas repetidas seguidas
    si inv.tema_saturado():  FIN                              # M ramas repetidas seguidas
```

"Repetida" la decide la similitud semántica (`sim_fn`, default `cerebro_semantica`) contra un umbral.
La **diversidad** la da rotar enfoques; la **parada** la da la repetición real. Defaults: `UMBRAL=0.78`,
`K=3`, `M=2` (configurables en el constructor).

## Cómo correr UNA ola (el orquestador eres tú, ola por ola)

```python
import sys; sys.path.insert(0, r"~\tu-proyecto-agente\research\INVESTIGACION_INFINITA")
import runner
inv = runner.cargar_o_crear("tu-proyecto-agente")          # crea o reanuda desde estado.json
pendientes = runner.proximos_a_investigar(inv, n=3)   # hasta 3 nodos NUEVOS a profundizar
```

1. **Despacha ≤3 agentes `general-purpose` en paralelo** (modelo barato — hábito de tokens #6;
   subagentes justificados aquí por ser barrido multi-fuente, hábito #3), uno por nodo pendiente.
   Cada agente entrega, anclado a "**¿cómo afecta esto al TEMA?**": mecanismo/SOTA + **fuentes
   citadas** + **mapeo a módulo concreto del TEMA** + **Recomendación #1** + riesgos. Nodos sin mapeo
   al tema se descartan (anti-deriva de alcance).
2. **Registra resultados**: por cada sub-rama nueva `inv.agregar_nodo(nivel, padre_id, titulo,
   resumen, fuentes=[...], recomendacion="...")` (devuelve `None` si salió repetida → cuenta para
   saturación). Marca los nodos profundizados con `estado="investigado"`.
3. `inv.ola += 1` y `runner.checkpoint(inv)` → reescribe `estado.json` + `GRAFO.md`.
4. **Persiste lo durable**: cada hallazgo a memoria compartida con
   `cerebro_memoria.recordar(slug=f"<tema>-ii-...", ...)`. Cada *Recomendación #1* → backlog/árbol de tareas.
5. **Para** cuando `inv.tema_saturado()` o al llegar al **tope de olas aprobado** por el usuario.

## Cableado obligatorio al ecosistema (reglas del hub `~\CLAUDE.md`)
- **Paso 0 multisesión** + `ms.reclamar("investigacion")` antes de tocar archivos.
- **Registrar tarea** en el árbol del proyecto (`tareas.py … --proposito --terminado`).
- **No daemons/loops autónomos** (#3): avanza ola por ola; el usuario controla cuándo seguir.
- **Salud del PC** (#10): olas de ≤3 agentes, espaciadas; no chocar con GPU/daemon Qwen.
- **Avisar antes de gastar** (#1) y antes de `/clear`.
- **Saturación = parada real**: no inventes "ya terminé"; deja que los contadores K/M lo digan.

## Calibración
Si satura demasiado pronto → sube `UMBRAL` o `K`/`M`. Si nunca satura → bájalos. Revisa `estado.json`
y los contadores `rep_L1`/`rep_L2`. Resúmenes de nodo estructurados (qué/por qué/ángulo) mejoran el
discriminado de la similitud.
