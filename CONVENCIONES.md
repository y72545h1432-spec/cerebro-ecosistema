# CONVENCIONES — Reglas y skills del ecosistema (versión pública)

> Versión **genérica** (sin rutas, proyectos ni credenciales del autor) de las reglas de trabajo y el
> catálogo de skills que acompañan a este ecosistema. Pensada para que **cualquiera** pueda adoptarlas.
> Para configurar lo sensible de tu clon: ver [`SETUP.md`](SETUP.md).

---

## ⛔ Reglas de trabajo (aplican a todo proyecto)

### A. Generales (portables a cualquier agente/proyecto)
1. **Confirmar antes de lo irreversible / externo / que gasta dinero.** La autorización en un contexto
   no se extiende al siguiente. Ante una acción destructiva, mira primero el objetivo; si contradice cómo
   te lo describieron o no lo creaste tú, repórtalo en vez de proceder.
2. **Verificar en vivo con evidencia** antes de reportar algo como hecho. Si un test falla, dilo con su
   salida; si saltaste un paso, dilo. "Parece correcto" no es "está hecho".
3. **No relanzar daemons/loops autónomos sin decisión explícita del usuario.** Un orquestador que **drena
   una cola y termina** (no persistente) es aceptable bajo guardrails: confirmación una vez, tope de
   concurrencia, kill-switch, presupuesto y allowlist de ejecutables.
4. **Revisar qué skills/procesos aplican antes de implementar algo nuevo** (proyecto nuevo, área nueva, o
   un tipo de tarea que no se venía haciendo). Cablea las relevantes ANTES de ejecutar.
5. **Skills nuevas: VERIFICAR → UNIFICAR.** Verifica primero que funcionen y sean seguras (recrear nativo
   > copiar código de terceros; no instalar sistemas ajenos sin OK); luego intégralas sin duplicar.
6. **Actualizar la documentación mínima necesaria antes de cerrar** un cambio estructural (reglas, rutas,
   agentes, protocolo).
7. **Priorizar la salud del computador:** estabilidad, temperatura, disco, recursos y la continuidad del
   trabajo del usuario van primero, antes que cualquier tarea pesada o persistente.

### B. Calidad de salida (anti-error, inspiradas en Karpathy)
- **K1 — Pensar antes de codear.** Declara supuestos; si hay varias interpretaciones, preséntalas (no
  elijas en silencio); si hay un enfoque más simple, dilo; si algo no está claro, PARA y pregunta.
- **K2 — Simplicidad primero.** Mínimo código que resuelva el problema; nada especulativo (sin features
  no pedidas, sin abstracciones de un solo uso, sin "flexibilidad" no solicitada).
- **K3 — Cambios quirúrgicos.** Toca solo lo necesario; cada línea cambiada traza directo a la petición.
  No "mejores" lo adyacente, no refactorices lo que no está roto, respeta el estilo existente.
- **K4 — Ejecución por metas verificables.** "Arregla el bug" → "escribe un test que lo reproduzca, luego
  hazlo pasar". Tareas multipaso: plan breve `N. [paso] → verify: [check]`.

### C. Hábitos de tokens (eficiencia)
- **H1** `/clear` al cambiar de proyecto (el historial se re-cobra cada turno).
- **H2** No editar el archivo de arranque (CLAUDE.md/AGENTS.md) a mitad de sesión (invalida el caché de
  prefijo); si toca, en UN bloque.
- **H3** Subagentes solo para barridos multi-archivo; editar 1-2 archivos → inline.
- **H4** `/compact focus on <tarea>` antes de tareas largas; lo crítico al INICIO de cada `SKILL.md`.
- **H5** Leer barato: `limit` al leer, búsquedas con conteo/solo-rutas, recall en memoria antes de re-leer.
- **H6** Bajar de modelo donde la calidad no sufra; research en modelo barato.
- **H7** Respuestas concisas; herramientas MCP en modo *deferred* (carga bajo demanda).

### D. Uso del ecosistema (estas reglas explican las herramientas que SÍ vienen en este repo)
- **E1 — Paso 0 multisesión.** Antes de tocar archivos de un proyecto con posibles sesiones concurrentes,
  registra la sesión, reclama locks y lee el buzón con `cerebro_multisesion.py`.
- **E2 — Comunicación viva segura.** Para handoffs, bloqueos, revisión, progreso o cancelación, usa
  mensajes tipados (`ms.mensaje_tipo`, `ms.ack`, `ms.progreso`, `ms.cancelacion`) y observa con
  `cerebro_watch.py --once`.
- **E3 — Co-programación multi-agente.** Si varios agentes escriben código, usa ownership explícito,
  locks, handoff estructurado, revisión cruzada, pruebas e integración por un responsable único.
- **E4 — Hechos verificables.** Toda afirmación factual sobre el estado del sistema (un test/comando pasa
  o falla, una dep está instalada, un puerto responde) se PRUEBA con `cerebro_hechos.py`, no se afirma en
  texto libre. Así un hecho relativo al entorno nunca se transmite como absoluto.

### E. Mejora continua de skills  ⭐ (proceso de auto-mejora)
- **R16 — Mejora la skill cuando notes que puede mejorar.** Cuando, usando o leyendo una skill, detectes
  un hueco, error, dato desactualizado, caso faltante o un patrón claramente mejor:
  1. **Confirma** que es una mejora real (verifícala, no la asumas — reglas A2/A5).
  2. Aplica un **cambio quirúrgico** al `SKILL.md` (o su `references/`) **sin romper los disparadores** de
     su `description` ni inflar el alcance (K2/K3).
  3. **Regístralo**: una línea de changelog en la skill + nota en memoria/conocimiento con tag `skills`.
  4. Si la skill está espejada en un repo, **re-sincroniza** (`cerebro_sync_repo.py`).
  - Una mejora = un cambio enfocado. Si es grande o cambia el propósito de la skill, **primero propón**.
  - Vive como **regla de criterio** (no hook): requiere juzgar qué es "mejora real".

---

## 🧩 Skills incluidas (`skills/`)

Skills propias del autor, **genericizadas** (los ejemplos citan proyectos a modo ilustrativo; adáptalos).
Se disparan por su `description`. No incluye skills de terceros (instálalas por su cuenta).

| Skill | Para qué |
|---|---|
| `equipo-ingenieria` | Operar como un EQUIPO de ingeniería: retar el scope, gates verificables por fase, segunda opinión cross-model, retro desde git. |
| `investigacion-infinita` | Investigación exhaustiva de un tema hasta saturación semántica, por olas reanudables. |
| `arrancar-area` | Arranque de un proyecto/área nueva: cablear las skills que aplican antes de ejecutar. |
| `gui-control-seguro` | Protocolo seguro para controlar la GUI (ratón/teclado/OCR) con foco verificado + confirmación. |
| `diseno` | Diseño UI/visual. |
| `negocios` | Estrategia y modelos de negocio. |
| `agencia-ia` | Montar/operar una agencia con IA. |
| `ia-aplicada` | IA aplicada (de ML clásico a fine-tuning/LoRA y despliegue). |
| `marketing-digital` | Marketing y paid ads (estructura de campañas, hooks, creative testing, CRO). |
| `ecommerce` | E-commerce / dropshipping (sourcing, PDP, conversión). |
| `youtube-growth` | Crecimiento en YouTube. |
| `produccion-audiovisual` | Producción audiovisual (rodaje, luz, cámara). |
| `video-editing` | Edición/dirección de video (retención, ritmo, cortes, color, sonido). |

> ¿Hueco recurrente sin skill? Créala. ¿Una skill se puede mejorar? Aplica **R16** (arriba).
