# 22 · OpenClaw — Vigilante del ecosistema (read-only, always-on)

> Agente externo always-on que **observa y avisa** sobre todos los proyectos. NO coordina ni modifica:
> es un **consumidor read-only** del ecosistema. Instalado y autorizado por el usuario 2026-06-20.

## Qué es
[OpenClaw](https://openclaw.ai) (open-source, Node) corre como Gateway local persistente, se conecta a
mensajería (Telegram) y ejecuta shell. Aquí cumple un único rol: **vigilante** del ecosistema.
- No es parte de `cerebro_multisesion` (no toma locks, no aparece en el tablero del router).
- Solo **lee**: `git status` de los repos + `cerebro_salud.py --json` + `cerebro_tareas_modelo.py` + `.remember\now.md`.
- Resume con el **modelo local** y avisa por **Telegram**.

## Excepción aprobada a la Regla Universal #3
La regla "no relanzar daemons/loops autónomos sin decisión explícita del usuario" se respeta: el usuario
**autorizó explícitamente** este daemon always-on el 2026-06-20 (modelo local, solo-lectura, Telegram, digest 9:00).

## Diseño (decisión por evidencia, 2026-06-20)
En pruebas, usar el **modelo local como AGENTE** (bucle de tool-calling) resultó frágil: la <GPU> (<VRAM>)
solo aloja **un modelo a la vez** y el daemon de tu-tienda mantiene `qwen3-8b` ocupado → las cargas se cancelaban
("Operation canceled") y el 3B devolvía tool-calls vacíos. **Conclusión:** el vigilante NO pelea por la GPU.
- **Digest diario = cron de COMANDO (sin LLM, sin GPU):** corre `recolecta.py` y manda su salida (ya formateada,
  con fecha y "Atención hoy" calculada en Python) directo a Telegram. 100% confiable. Es el backbone.
- **Chat bot (preguntas ad-hoc) = `claude-cli/claude-opus-4-8` + leer-archivo (ACTIVADO 2026-06-21):**
  Se probó el modelo local como agente y NO sirve en esta caja: <VRAM> no alojan el 3B junto al `qwen3-8b` de tu-tienda
  (carga "Operation canceled"), y el 8B desborda su contexto de 8k con el system prompt. Solución:
  - **Modelo del chat = `claude-cli/claude-opus-4-8`** (sin GPU, contexto grande, tool-calling sólido; usa la
    suscripción de Claude — ya NO es 100% local solo para el chat). Revertir: `openclaw models set local/qwen2.5-3b-instruct`.
  - **exec TOTALMENTE bloqueado:** el exec del agente corre vía shell (no allowlisteado) → no puede ejecutar NADA.
    Por eso el bot **no corre** el recolector: **LEE** `workspace\ESTADO_ECOSISTEMA.md` (herramienta read, permitida)
    y responde. Máximo fail-closed: el bot no puede ejecutar ni modificar nada.
  - **Refresco del estado:** `recolecta.py --out workspace\ESTADO_ECOSISTEMA.md` (lanzador `vigilante-refresh.cmd`).
    El lanzador `vigilante-chat.cmd` refresca y abre `openclaw chat`. Opcional: agendar el refresh con el
    Programador de tareas de Windows (sin daemon de Node).

## Configuración (en `~\.openclaw\`)
- **Config:** `openclaw.json` (helpers no-interactivos: `openclaw config get/set/patch/validate`).
- **Modelo (solo para conversacional):** provider genérico `local` → `http://127.0.0.1:<PUERTO_LLM>/v1`,
  modelo por defecto `local/qwen2.5-3b-instruct` (entra completo en <VRAM>; caliente <1s). Se renombró de
  `tu servidor LLM local` a `local` para evitar el sondeo nativo `/api/v1` que expiraba. **Cero costo de API.**
- **Ciudadano-GPU:** el vigilante no fija modelos cargados; descarga lo que cargue para no robar VRAM a tu-tienda/tu-proyecto-agente.
- **Candado read-only (capas):**
  1. `tools.deny = ["write","edit"]` (sin herramientas de escritura de archivos).
  2. **exec-policy** `security=allowlist`, `ask=on-miss`, `ask-fallback=deny` → en cron desatendido, todo lo
     no allowlisteado se **deniega** (fail-closed). Allowlist: solo `git`, `py`, `python`
     (`approvals allowlist`, archivo `exec-approvals.json`).
  3. Instrucciones: override read-only al inicio de `workspace\AGENTS.md` + skill `cerebro-vigilante`.
  4. (Pendiente) **allowlist de Telegram** al `chat_id` del usuario, para que solo él pueda darle órdenes.
- **Recolector:** `skills\cerebro-vigilante\recolecta.py` — genera el digest read-only (git + salud + tareas + handoff).
- **Skill:** `skills\cerebro-vigilante\SKILL.md` — para el modo conversacional (corre el recolector y formatea).
- **Cron (digest diario):** comando que corre el recolector y lo envía a Telegram (sin LLM):
  `openclaw cron add "0 9 * * *" --name "Vigilante diario" --command-argv '["C:\\...\\py.exe","~\\.openclaw\\skills\\cerebro-vigilante\\recolecta.py"]' --announce --channel telegram --to "<chat_id>"`.
  Jobs en SQLite del Gateway.
- **Always-on:** el Gateway debe estar siempre vivo (corre el cron). Instalar daemon: `openclaw setup --install-daemon`
  (Windows: Scheduled Task, fallback a item de inicio de usuario).

## Operación
- **Always-on:** `openclaw gateway run` (o daemon vía Scheduled Task: `openclaw setup --install-daemon`).
- **Bajo demanda:** el usuario escribe al bot de Telegram; responde con la skill.
- **Estado:** `openclaw gateway status`, `openclaw status`, `openclaw doctor`.
- **Logs:** `~\AppData\Local\Temp\openclaw\openclaw-<fecha>.log`.

## Límite claro
Si se le pide commitear/pushear/editar: **se niega** (es solo-lectura). Esos cambios los hace el usuario o
una sesión de Claude Code/Codex. Futuros agentes: este vigilante NO debe convertirse en escritor sin una
nueva decisión explícita del usuario y actualizar este doc.
