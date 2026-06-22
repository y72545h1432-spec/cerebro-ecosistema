# Regla Universal: Priorizar la Salud del Computador

## Regla principal
La salud, estabilidad y seguridad del computador tienen prioridad sobre cualquier tarea, automatizacion, entrenamiento, render, scraping, daemon, instalacion o experimento.

## Implica
- No saturar CPU, GPU, VRAM, RAM, disco o red sin necesidad real.
- No lanzar procesos largos, daemons, loops autonomos, entrenamientos, renders o descargas masivas sin confirmacion explicita.
- No usar la GPU/tu servidor LLM local sin reclamar lock global (`gpu`, `vram`, `tu servidor LLM local`) y revisar si otro proyecto la necesita.
- No llenar discos con caches, datasets, videos, modelos o backups redundantes.
- No instalar dependencias pesadas ni modificar PATH/servicios/seguridad sin confirmar.
- No forzar procesos si hay signos de temperatura alta, memoria baja, disco lleno, errores del sistema o lentitud fuerte.
- No limpiar ni borrar caches/historiales como reflejo automatico; diagnosticar primero, respaldar si aplica, y confirmar si es destructivo.

## Senales de alerta
- Disco del sistema con poco espacio libre.
- Ventiladores altos o equipo caliente.
- GPU/VRAM ocupada por otro proceso.
- tu servidor LLM local activo con modelo cargado.
- Premiere/DaVinci/editores abiertos con proyecto real.
- Procesos Python/Node/ffmpeg largos sin registro.
- Descargas/modelos/datasets grandes en curso.

## Protocolo antes de tareas pesadas
1. Revisar si la tarea necesita recursos altos.
2. Reclamar lock global si toca GPU/tu servidor LLM local/daemon/puertos.
3. Comprobar espacio y procesos relevantes cuando el riesgo sea real.
4. Explicar al usuario el costo/riesgo si hace falta.
5. Ejecutar de forma acotada, con timeout y salida verificable.
6. Registrar en `.cerebro` si afecta recursos compartidos.

## Recursos IA locales
Si la tarea toca GPU, tu servidor LLM local, Qwen, daemons de IA local, vLLM/Kaggle/Colab o una cola offline de inferencia, abrir tambien `18_RECURSOS_IA_LOCALES.md`. Ese documento decide si conviene local, batch externo, benchmark o no tocar.

## Regla de parada
Si una tarea amenaza estabilidad, datos, temperatura, disco, bateria, rendimiento o continuidad de trabajo del usuario, el agente debe parar, registrar el motivo y pedir confirmacion antes de continuar.
