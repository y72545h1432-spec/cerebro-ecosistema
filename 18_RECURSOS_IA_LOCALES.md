# Recursos IA Locales y Batch

Documento dueño para decidir cómo usar GPU, tu servidor LLM local, daemons de IA local y lotes externos sin romper la salud del computador ni duplicar trabajo entre proyectos.

## Cuándo abrirlo
- Vas a tocar tu servidor LLM local, Qwen, vLLM, llama.cpp, Kaggle/Colab/RunPod o una cola de inferencia.
- Un proyecto quiere acelerar un daemon local como tu-tienda Mano Derecha.
- Hay conflicto entre tu-tienda y tu-proyecto-agente por GPU/VRAM.
- Una tarea podría saturar RAM, VRAM, CPU, disco o un puerto local.

## Regla corta
La GPU/tu servidor LLM local es un recurso global. Antes de cambiar modelos, paralelismo, servidor, batch externo o daemon:
1. Ejecuta Paso 0 multisesión.
2. Reclama `gpu` y/o `tu servidor LLM local` con `scope="global"`.
3. Lee `10_PRIORIDAD_SALUD_COMPUTADOR.md`.
4. Haz un benchmark pequeño antes de cambiar la cola real.
5. Registra resultado y decisión en multisesión.

## Matriz de decisión

| Necesidad | Ruta preferida | No hacer |
|---|---|---|
| Mantener trabajo continuo barato | tu servidor LLM local + daemon actual | Subir paralelismo sin medir VRAM |
| Terminar miles de tareas rápido | Exportar batch externo a vLLM/Kaggle/Colab/RunPod | Forzar dos daemons locales |
| Optimizar local con bajo riesgo | `max_tokens` adaptativo + medición por tarea | Cambiar calidad de toda la cola de golpe |
| Comparar backend local | Benchmark llama.cpp server vs tu servidor LLM local con muestra fija | Migrar backend sin A/B |
| tu-proyecto-agente necesita entrenar LoRA | Pausar/time-share tu-tienda Mano Derecha o usar GPU externa | Entrenar y destilar a la vez en <VRAM> |

## Protocolo para acelerar una cola local
1. Baseline: número de pendientes, duración p50/p90, errores, VRAM usada.
2. Clasifica el cuello:
   - VRAM casi llena: no subir paralelismo local.
   - Output largo: probar `max_tokens` adaptativo.
   - Cola offline grande: preparar export/import batch externo.
   - Errores 400/timeouts: revisar tamaño de prompts y servidor.
3. Haz experimento acotado:
   - 30-100 tareas como muestra.
   - No modificar la cola real salvo backup.
   - Medir duración, errores, longitud de salida y criterio de calidad.
4. Promueve solo si hay mejora clara y rollback simple.

## tu-tienda Mano Derecha
Documento específico:
- `C:\tu-tienda\GUIAS\MANO_DERECHA_LOCAL.md`
- `C:\tu-tienda\GUIAS\MANO_DERECHA_BATCH_EXTERNO.md`
- `C:\tu-tienda\DOCUMENTACION\INVESTIGACION_ACELERAR_MANO_DERECHA_2026-06-18.md`

Decisión vigente 2026-06-18:
- No subir `--parallel` en la <GPU> <VRAM>: Qwen3-8B ya ocupa ~5 GB VRAM.
- Mejor primera ruta local: experimento `max_tokens` adaptativo.
- Mejor ruta para acelerar fuerte: batch externo con vLLM y posterior importación.

## Checklist de seguridad
- [ ] Lock global `gpu`/`tu servidor LLM local` reclamado si se toca el recurso.
- [ ] No hay otro proyecto usando VRAM.
- [ ] Baseline guardado antes del cambio.
- [ ] Experimento limitado y reversible.
- [ ] Daemons persistentes solo con autorización o regla existente.
- [ ] Resultado verificado con evidencia fresca.
