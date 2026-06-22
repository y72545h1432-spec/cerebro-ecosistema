"""CEREBRO · MULTISESION AGENTICA (multi-agente + multiproyecto)

Coordinacion + conocimiento entre sesiones concurrentes de CUALQUIER agente
(Claude Code, Codex, futuros runtimes) y CUALQUIER proyecto (tu-tienda, tu-proyecto-aprendizaje,
tu-proyecto-agente, ...). Vive FUERA de tu-tienda y FUERA de cualquier runtime para que todos los
agentes/proyectos compartan estado.

Autocontenido: solo stdlib (json/os/time/socket/ctypes/tempfile/uuid/datetime).
No depende de tu-tienda. Cualquier proyecto puede:
    import sys; sys.path.insert(0, r"~\\.cerebro")
    from cerebro_multisesion import Multisesion
    ms = Multisesion("descripción", project="tu-proyecto-agente", agent="codex")

API (compatible con la multisesion vieja de tu-tienda + extensiones):
    ms.reclamar(recurso, motivo="", scope="project")  -> bool   (scope="global" = entre proyectos)
    ms.reclamar_o_esperar(recurso, ...)               -> bool
    ms.liberar(recurso, scope="project")
    ms.latido(tarea=None)            # renueva sesión + mis locks
    ms.evento(detalle)
    ms.decidir(decision, motivo="")  # acuerdo durable (no deshacer sin reemplazar)
    ms.mensaje(para, texto) / ms.leer_buzon()
    ms.conocimiento(nota, tags=())   # APRENDIZAJE compartido entre TODOS los proyectos
    ms.leer_conocimiento(project=None, tag=None, n=20)
    ms.estado(project=None)          # None = todos los proyectos; "<p>" = solo ese
    ms.despedir()

BLINDAJE (mejoras sobre la versión tu-tienda):
  · Mutex de proceso (lockfile O_EXCL + pid-liveness) alrededor de CADA mutación →
    elimina el lost-update race del read-modify-write (antes solo había replace atómico).
  · pid_alive(): una sesión cuyo PID murió se marca muerta al instante (no espera el TTL).
  · Backup .bak antes de cada replace + recuperación si el JSON se corrompe.
  · Recursos de hardware (GPU/tu servidor LLM local) son GLOBALES aunque pidas scope project →
    tu-tienda y tu-proyecto-agente NO pisan la VRAM a la vez.
  · Esquema versionado con migración suave.
"""
from __future__ import annotations
import os, time, uuid, socket, pathlib, subprocess, shutil
from datetime import datetime

import cerebro_core as core  # base comun: io atomica, tiempo, pid, mutex (fuente unica)
from cerebro_core import (  # alias: conserva los nombres internos para no tocar los call-sites
    STATE_DIR, now as _ahora, is_expired as _vencido, pid_alive,
    write_atomic as _write_atomic, read_json_tolerant as _read_tolerante,
    append_jsonl as _core_append_jsonl, FileMutex,
)

SCHEMA = 5
# Estado compartido fuera de OneDrive y fuera de tu-tienda (STATE_DIR viene de cerebro_core).
ARCHIVO = STATE_DIR / "multisesion.json"
LOCKDIR = STATE_DIR / "_locks"
EVENT_LOG = STATE_DIR / "eventos.jsonl"

TTL_LOCK_MIN = 30          # un lock sin renovar muere a los 30 min
LATIDO_MUERTO_MIN = 15     # sesión sin latido en 15 min = muerta
RETENER_MUERTAS_MIN = 180  # sesiones muertas: 3h de gracia para auditoría, luego GC (causa raíz #1).
                           # El dict 'sesiones' es coordinación EN VIVO (la muerte se declara a los 15 min);
                           # el histórico durable vive en .remember/. 3h acota el estado ~15× sin perder
                           # ventana de auditoría reciente.
MAX_EVENTOS = 160
MAX_CONOCIMIENTO = 300
MAX_EVENT_LOG_BYTES = 2_000_000

# Recursos que SON de hardware/infra compartida entre proyectos → siempre globales.
GLOBAL_RESOURCES = {"gpu", "vram", "tu servidor LLM local", "tu servidor LLM local_config", "daemon_config", "puerto_1234"}
# Subconjunto que es CARGA de GPU real → al reclamarlos sondeamos el hardware (los *_config y el
# puerto no consumen VRAM, no se sondean). Convierte la regla de prosa "revisar si otro proyecto
# necesita la GPU" (10_PRIORIDAD_SALUD_COMPUTADOR.md) en un chequeo ejecutable (causa raíz #3).
HW_PROBE_RES = {"gpu", "vram", "tu servidor LLM local"}
MESSAGE_TYPES = {
    "notice", "task_request", "handoff", "progress", "blocker", "review_request",
    "decision_request", "done", "cancel"
}
PRIORITIES = {"low", "normal", "high", "urgent"}

_AQUI = pathlib.Path(__file__).resolve().parent   # raiz del ecosistema (portable)
_PROTOCOLO = {
    "que_es": "Estado compartido en tiempo real entre agentes y proyectos.",
    "documentacion": str(_AQUI / "00_INDICE.md"),
    "fuente_neutral": str(_AQUI / "ECOSISTEMA_MULTIAGENTE.md"),
    "regla_1": "Regístrate al arrancar con 'project' y 'agent'; di en 'tarea' qué haces; renueva latido en trabajos largos.",
    "regla_2": "Reclama el recurso ANTES de tocarlo. Si está tomado, NO lo toques. Hardware (GPU/tu servidor LLM local) es global entre proyectos.",
    "regla_3": "Registra eventos de lo relevante que completes; usa conocimiento() para aprendizajes que sirvan a OTROS proyectos.",
    "regla_4": "Antes de editar archivos compartidos (handoff/colas): reclamar, RELEER, editar, liberar.",
    "regla_5": "Locks viejos (>30 min) y sesiones sin latido (>15 min) o con PID muerto expiran solos.",
    "regla_6": "DECISIONES vigentes son durables: no las deshagas sin registrar una nueva que la reemplace.",
    "regla_7": "Revisa tu BUZÓN al arrancar; deja mensaje() cuando algo afecte a otra sesión/proyecto.",
}


def _detectar_agente(agent: str | None = None) -> str:
    """Nombre estable del agente/runtime humano-legible.

    Se mantiene opcional para no romper shims existentes. Preferir pasar
    agent="codex" / agent="claude" cuando el runtime lo sepa.
    """
    if agent:
        return str(agent).strip().lower() or "desconocido"
    for env in ("CEREBRO_AGENT", "AGENT_NAME", "CODEX_AGENT", "CLAUDE_AGENT"):
        val = os.environ.get(env)
        if val:
            return val.strip().lower()
    # Heuristica conservadora: no asumir Claude si no se sabe.
    return "desconocido"


def _detectar_runtime(runtime: str | None = None, agent: str | None = None) -> str:
    if runtime:
        return str(runtime).strip().lower() or "desconocido"
    env = os.environ.get("CEREBRO_RUNTIME") or os.environ.get("AGENT_RUNTIME")
    if env:
        return env.strip().lower()
    if agent in {"codex", "claude", "claude-code"}:
        return agent
    return "desconocido"


# _ahora (now), _vencido (is_expired), pid_alive, _write_atomic, _read_tolerante viven en
# cerebro_core (importados arriba como alias). Aqui solo quedan los que dependen de constantes/estado
# de ESTE modulo (rotacion del event-log, LOCKDIR parcheable por los tests).
def _append_jsonl(path: pathlib.Path, item: dict) -> None:
    """Append-only log liviano para watchers/dashboards (rota a .jsonl.bak por tamano).
    Delega en cerebro_core.append_jsonl pasando el limite de rotacion de ESTE modulo."""
    _core_append_jsonl(path, item, max_bytes=MAX_EVENT_LOG_BYTES)


def _Mutex(name: str = "multisesion") -> FileMutex:
    """Mutex de proceso del cerebro. Factoria sobre cerebro_core.FileMutex que usa el LOCKDIR del
    MODULO, resuelto en TIEMPO DE LLAMADA -> los tests que reapuntan cm.LOCKDIR siguen aislados, y
    los modulos que hacen `from cerebro_multisesion import _Mutex` lo siguen usando como `with _Mutex():`."""
    return FileMutex(name, lockdir=LOCKDIR)


def _lock_key(project: str, recurso: str, scope: str) -> str:
    if scope == "global" or recurso in GLOBAL_RESOURCES:
        return f"*:{recurso}"
    return f"{project}:{recurso}"


def gpu_estado(timeout: float = 2.0) -> dict | None:
    """Probe REAL del hardware GPU vía nvidia-smi (best-effort). Convierte la regla de prosa
    "antes de tocar la GPU, revisar si otro proyecto la necesita" en evidencia ejecutable: al
    reclamar un lock global de hardware adjuntamos VRAM/temp/util como prueba (no solo confianza
    en que se reclamó). Devuelve None si no hay nvidia-smi (host sin GPU / driver ausente) o si
    falla → el lock sigue siendo advisory y NUNCA se bloquea por esto."""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    try:
        r = subprocess.run(
            [exe, "--query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0 or not (r.stdout or "").strip():
            return None
        used, total, temp, util = [p.strip() for p in r.stdout.strip().splitlines()[0].split(",")]
        return {"vram_used_mb": int(used), "vram_total_mb": int(total),
                "gpu_temp_c": int(temp), "gpu_util_pct": int(util)}
    except Exception:
        return None


class Multisesion:
    def __init__(self, descripcion: str, project: str = "general", sesion_id: str | None = None,
                 agent: str | None = None, runtime: str | None = None) -> None:
        self.project = project
        self.agent = _detectar_agente(agent)
        self.runtime = _detectar_runtime(runtime, self.agent)
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        prefix = f"{self.agent}-{project}" if self.agent != "desconocido" else project
        self.id = sesion_id or f"{prefix}-{datetime.now():%m%d_%H%M}_{uuid.uuid4().hex[:5]}"
        self._mutar(lambda d: d["sesiones"].__setitem__(self.id, {
            "project": project, "agent": self.agent, "runtime": self.runtime,
            "descripcion": descripcion, "inicio": _ahora(),
            "pid": os.getpid(), "host": socket.gethostname(),
            "ultimo_latido": _ahora(), "tarea": "arrancando", "viva": True}))
        self.evento(f"sesión registrada [{self.agent}/{project}]: {descripcion}")

    # ---------- núcleo ----------
    @staticmethod
    def _vacio() -> dict:
        return {"_schema": SCHEMA, "_protocolo": _PROTOCOLO, "sesiones": {}, "locks": {},
                "eventos": [], "decisiones": [], "buzon": {}, "conocimiento": [],
                "agentes": {}, "acks": {}}

    def _leer(self) -> dict:
        d = _read_tolerante(ARCHIVO)
        if not isinstance(d, dict):
            return self._vacio()
        base = self._vacio()
        base.update(d)
        for k in ("sesiones", "locks", "buzon", "agentes", "acks"):
            base[k] = d.get(k, {}) or {}
        for k in ("eventos", "decisiones", "conocimiento"):
            base[k] = d.get(k, []) or []
        return base

    def _mutar(self, fn) -> dict:
        with _Mutex():                       # serializa entre procesos (blindaje)
            d = self._leer()
            d["_schema"] = SCHEMA
            d["_protocolo"] = _PROTOCOLO
            d.setdefault("agentes", {})
            self._purgar(d)
            self._registrar_agente(d)
            fn(d)
            _write_atomic(ARCHIVO, d)
            return d

    def _registrar_agente(self, d: dict) -> None:
        info = d.setdefault("agentes", {}).setdefault(self.agent, {
            "agent": self.agent, "runtime": self.runtime, "primera_vez": _ahora(),
            "sesiones": 0})
        info["runtime"] = self.runtime
        info["ultimo_visto"] = _ahora()
        info["host"] = socket.gethostname()
        info["sesiones"] = len([s for s in d.get("sesiones", {}).values()
                                if s.get("agent") == self.agent])

    @staticmethod
    def _purgar(d: dict) -> None:
        for sid, s in d["sesiones"].items():
            s.setdefault("agent", "claude" if sid.startswith("tu-tienda-") else "desconocido")
            s.setdefault("runtime", s.get("agent", "desconocido"))
            if s.get("viva"):
                pid = s.get("pid")
                muerta = _vencido(s.get("ultimo_latido", ""), LATIDO_MUERTO_MIN)
                # PID muerto del MISMO host = sesión caída; otro host no se juzga por PID local.
                if pid and s.get("host") == socket.gethostname() and not pid_alive(pid):
                    muerta = True
                if muerta:
                    s["viva"] = False
                    s["tarea"] = f"(muerta; última: {s.get('tarea')})"
        d["locks"] = {r: l for r, l in d["locks"].items()
                      if not _vencido(l.get("desde", ""), TTL_LOCK_MIN)
                      and d["sesiones"].get(l.get("sesion"), {}).get("viva", False)}
        # GC de ciclo de vida (causa raíz #1: las LISTAS se truncaban, los DICTS no -> 537 sesiones).
        # Va DESPUÉS del filtro de locks (que ya descartó los de sesiones no vivas) para no dejar
        # locks colgando. Las decisiones NO se tocan: son durables (regla #6, se reemplazan, no se purgan).
        muertas_gc = {sid for sid, s in d["sesiones"].items()
                      if not s.get("viva") and _vencido(s.get("ultimo_latido", ""), RETENER_MUERTAS_MIN)}
        if muertas_gc:
            d["sesiones"] = {sid: s for sid, s in d["sesiones"].items() if sid not in muertas_gc}
            for sid in muertas_gc:          # su buzón personal nunca se leerá -> huérfano para siempre
                d["buzon"].pop(sid, None)
        d["buzon"] = {k: v for k, v in d["buzon"].items() if v}   # listas vacías (se acumulan al popear)
        d["acks"] = {mid: items for mid, items in d["acks"].items()
                     if items and not _vencido(items[-1].get("ts", ""), RETENER_MUERTAS_MIN)}
        d["eventos"] = d["eventos"][-MAX_EVENTOS:]
        d["conocimiento"] = d["conocimiento"][-MAX_CONOCIMIENTO:]

    # ---------- API ----------
    def latido(self, tarea: str | None = None) -> None:
        def f(d):
            s = d["sesiones"].setdefault(self.id, {"project": self.project})
            s["agent"] = self.agent
            s["runtime"] = self.runtime
            s["ultimo_latido"] = _ahora()
            s["viva"] = True
            s.setdefault("pid", os.getpid())
            s.setdefault("host", socket.gethostname())
            if tarea:
                s["tarea"] = tarea
            for l in d["locks"].values():
                if l.get("sesion") == self.id:
                    l["desde"] = _ahora()
        self._mutar(f)

    def reclamar(self, recurso: str, motivo: str = "", scope: str = "project") -> bool:
        key = _lock_key(self.project, recurso, scope)
        # Lock-GPU como chequeo ejecutable: si es carga de GPU global, sondeamos el hardware ANTES
        # de mutar (el subprocess nvidia-smi NO debe correr dentro del mutex de proceso) y guardamos
        # la evidencia en el lock. Advisory: no condiciona la concesión (tu servidor LLM local reside siempre).
        hw = gpu_estado() if key.startswith("*:") and recurso in HW_PROBE_RES else None
        res = {"ok": False}
        def f(d):
            l = d["locks"].get(key)
            if l and l["sesion"] != self.id:
                return  # tomado por otra sesión viva
            lock = {"sesion": self.id, "project": self.project,
                    "agent": self.agent, "runtime": self.runtime,
                    "desde": _ahora(), "motivo": motivo, "recurso": recurso}
            if hw:
                lock["hw"] = hw
            d["locks"][key] = lock
            res["ok"] = True
        self._mutar(f)
        if res["ok"]:
            self.latido(f"trabajando en {recurso}" + (f" ({motivo})" if motivo else ""))
            if hw:
                self._log_event("gpu_probe",
                                f"reclamar {recurso}: VRAM {hw['vram_used_mb']}/{hw['vram_total_mb']}MB "
                                f"{hw['gpu_temp_c']}C util {hw['gpu_util_pct']}%",
                                {"recurso": recurso, **hw})
        return res["ok"]

    def reclamar_o_esperar(self, recurso: str, motivo: str = "", max_min: int = 10,
                           scope: str = "project") -> bool:
        fin = time.time() + max_min * 60
        while time.time() < fin:
            if self.reclamar(recurso, motivo, scope):
                return True
            time.sleep(30)
        return False

    def liberar(self, recurso: str, scope: str = "project") -> None:
        key = _lock_key(self.project, recurso, scope)
        def f(d):
            if d["locks"].get(key, {}).get("sesion") == self.id:
                d["locks"].pop(key, None)
        self._mutar(f)

    def decidir(self, decision: str, motivo: str = "") -> None:
        item = {"ts": _ahora(), "project": self.project, "agent": self.agent,
                "runtime": self.runtime, "sesion": self.id,
                "decision": decision, "motivo": motivo}
        self._mutar(lambda d: d["decisiones"].append(item))
        self._log_event("decision", decision, {"motivo": motivo})

    def conocimiento(self, nota: str, tags=()) -> None:
        """Aprendizaje COMPARTIDO entre todos los agentes/proyectos."""
        item = {"ts": _ahora(), "project": self.project, "agent": self.agent,
                "runtime": self.runtime, "sesion": self.id,
                "nota": nota, "tags": list(tags)}
        self._mutar(lambda d: d["conocimiento"].append(item))
        self._log_event("conocimiento", nota, {"tags": list(tags)})

    def leer_conocimiento(self, project: str | None = None, tag: str | None = None,
                          agent: str | None = None, n: int = 20) -> list:
        d = self._leer()
        items = d.get("conocimiento", [])
        if project:
            items = [c for c in items if c.get("project") == project]
        if agent:
            items = [c for c in items if c.get("agent") == agent]
        if tag:
            items = [c for c in items if tag in c.get("tags", [])]
        return items[-n:]

    def mensaje(self, para: str, texto: str) -> str:
        """Mensaje legacy: conserva la API vieja y lo registra como notice normal."""
        return self.mensaje_tipo(para, texto=texto, type="notice", priority="normal")

    def mensaje_tipo(self, para: str, texto: str | None = None, type: str = "notice",
                     priority: str = "normal", requires_ack: bool = False,
                     resource: str = "", expires_at: str = "", summary: str = "",
                     details: str = "", evidence=None, thread: str = "",
                     progress_token: str = "") -> str:
        """Mensaje estructurado para coordinacion viva. No ejecuta acciones."""
        msg_type = type if type in MESSAGE_TYPES else "notice"
        prio = priority if priority in PRIORITIES else "normal"
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        body = {
            "id": msg_id, "ts": _ahora(), "de": self.id, "project": self.project,
            "agent": self.agent, "runtime": self.runtime, "para": para,
            "type": msg_type, "priority": prio, "requires_ack": bool(requires_ack),
            "resource": resource, "expires_at": expires_at,
            "summary": summary or (texto or "")[:140], "details": details,
            "evidence": evidence or [], "thread": thread, "progress_token": progress_token,
            "texto": texto or summary or details,
        }
        self._mutar(lambda d: d["buzon"].setdefault(para, []).append(body))
        self._log_event("mensaje", body["summary"], {
            "id": msg_id, "para": para, "message_type": msg_type,
            "priority": prio, "requires_ack": bool(requires_ack),
            "thread": thread, "progress_token": progress_token,
        })
        return msg_id

    def leer_buzon(self, type: str | None = None, priority: str | None = None,
                   requires_ack: bool | None = None) -> list:
        res = []
        now = datetime.now()

        def vigente(m):
            exp = m.get("expires_at")
            if not exp:
                return True
            try:
                return datetime.fromisoformat(exp) > now
            except Exception:
                return True

        def match(m):
            if not vigente(m):
                return False
            if type and m.get("type", "notice") != type:
                return False
            if priority and m.get("priority", "normal") != priority:
                return False
            if requires_ack is not None and bool(m.get("requires_ack")) != bool(requires_ack):
                return False
            return True

        def f(d):
            personal = d["buzon"].pop(self.id, [])
            candidatos = []
            candidatos.extend(personal)
            candidatos.extend(d["buzon"].get("*", []))
            candidatos.extend(d["buzon"].get(self.project, []))   # buzón por proyecto
            candidatos.extend(d["buzon"].get(f"agent:{self.agent}", []))  # buzón por agente/runtime
            vistos = set()
            for m in candidatos:
                mid = m.get("id") or f"legacy_{m.get('ts','')}_{m.get('de','')}"
                if mid in vistos:
                    continue
                vistos.add(mid)
                if match(m):
                    res.append(m)
        self._mutar(f)
        return res

    def ack(self, mensaje_id: str, nota: str = "") -> None:
        item = {"ts": _ahora(), "agent": self.agent, "runtime": self.runtime,
                "project": self.project, "sesion": self.id, "nota": nota}
        self._mutar(lambda d: d["acks"].setdefault(mensaje_id, []).append(item))
        self._log_event("ack", f"ack {mensaje_id}", {"mensaje_id": mensaje_id, "nota": nota})

    def dead_letter(self, ahora: datetime | None = None) -> list:
        """Mensajes `requires_ack` que VENCIERON sin ack: handoffs/blockers caidos.
        `leer_buzon` los oculta (vigente()=False) -> se perderian en silencio. Esto los rescata
        para inspeccion humana/agente (patron dead-letter de colas at-least-once). Read-only:
        NO muta el buzon ni los marca. Cada item lleva `_destino` (a quien iban dirigidos)."""
        now = ahora or datetime.now()
        d = self._leer()
        acks = d.get("acks", {})
        out, vistos = [], set()
        for destino, msgs in d.get("buzon", {}).items():
            for m in msgs or []:
                if not m.get("requires_ack"):
                    continue
                exp = m.get("expires_at")
                if not exp:
                    continue                       # sin caducidad -> sigue en el buzon, no es perdida
                try:
                    if datetime.fromisoformat(exp) > now:
                        continue                   # aun vigente
                except Exception:
                    continue
                mid = m.get("id")
                if mid in vistos or acks.get(mid):
                    continue                       # ya visto o ya atendido a tiempo
                vistos.add(mid)
                out.append({**m, "_destino": destino})
        return out

    def progreso(self, progress_token: str, progress: float, total: float | None = None,
                 message: str = "", para: str = "*") -> str:
        details = message or f"progreso {progress}" + (f"/{total}" if total else "")
        return self.mensaje_tipo(
            para, type="progress", priority="normal", summary=details, details=details,
            progress_token=progress_token, evidence=[{"progress": progress, "total": total}]
        )

    def cancelacion(self, request_id: str, reason: str = "", para: str = "*") -> str:
        """Solicita cancelar una operacion. Es una notificacion; no ejecuta acciones."""
        return self.mensaje_tipo(
            para, type="cancel", priority="high", requires_ack=True,
            summary=f"cancelar {request_id}", details=reason,
            evidence=[{"request_id": request_id, "reason": reason}]
        )

    def handoff(self, para: str, goal: str, next_step: str, acceptance: str,
                done: str = "", findings: str = "", open_questions: str = "",
                constraints: str = "", thread: str = "", expires_at: str = "",
                priority: str = "high") -> str:
        """Contrato de handoff estructurado (O26). La causa #1 empirica de fallo multi-agente
        (~79%, taxonomia MAST) es la AMBIGÜEDAD de especificacion en el traspaso, no el consenso.
        Esto hace del handoff COMPLETO el camino de menor resistencia: empaqueta intent + estado
        + criterio de aceptacion como objeto estructurado (no historial crudo) y EXIGE los minimos
        anti-ambiguedad. `requires_ack=True` espera un ack closed-loop que confirme ENTENDIMIENTO
        (no solo recepcion). Verificar lo `acceptance` con evidencia (regla #2 / cerebro_hechos)."""
        faltan = [n for n, v in (("goal", goal), ("next_step", next_step),
                                 ("acceptance", acceptance)) if not (v or "").strip()]
        if faltan:
            raise ValueError(f"handoff incompleto: faltan {', '.join(faltan)} "
                             f"(intent / siguiente accion / criterio de aceptacion son obligatorios)")
        paquete = {"goal": goal, "done": done, "findings": findings,
                   "open_questions": open_questions, "constraints": constraints,
                   "next_step": next_step, "acceptance": acceptance}
        detalle = "\n".join(f"{k}: {v}" for k, v in paquete.items() if v)
        return self.mensaje_tipo(
            para, type="handoff", priority=priority, requires_ack=True,
            summary=f"handoff: {goal}"[:140], details=detalle,
            evidence=[{"handoff": paquete}], thread=thread, expires_at=expires_at,
        )

    def evento(self, detalle: str) -> None:
        item = {"ts": _ahora(), "project": self.project, "agent": self.agent,
                "runtime": self.runtime, "sesion": self.id, "detalle": detalle}
        self._mutar(lambda d: d["eventos"].append(item))
        self._log_event("evento", detalle)

    def despedir(self) -> None:
        def f(d):
            s = d["sesiones"].get(self.id, {})
            s["viva"] = False
            s["fin"] = _ahora()
            s["tarea"] = "sesión cerrada"
            d["locks"] = {r: l for r, l in d["locks"].items() if l["sesion"] != self.id}
        self._mutar(f)
        self.evento("sesión despedida")

    def estado(self, project: str | None = None, agent: str | None = None) -> dict:
        d = self._leer()
        self._purgar(d)
        if project or agent:
            d = dict(d)
            if project:
                d["sesiones"] = {k: v for k, v in d["sesiones"].items() if v.get("project") == project}
                d["locks"] = {k: v for k, v in d["locks"].items() if v.get("project") == project or k.startswith("*:")}
                d["eventos"] = [e for e in d["eventos"] if e.get("project") in (project, None)]
            if agent:
                d["sesiones"] = {k: v for k, v in d["sesiones"].items() if v.get("agent") == agent}
                d["locks"] = {k: v for k, v in d["locks"].items() if v.get("agent") == agent or k.startswith("*:")}
                d["eventos"] = [e for e in d["eventos"] if e.get("agent") in (agent, None)]
        return d

    def _log_event(self, type: str, summary: str, extra: dict | None = None) -> None:
        item = {"ts": _ahora(), "project": self.project, "agent": self.agent,
                "runtime": self.runtime, "sesion": self.id, "type": type,
                "summary": summary}
        if extra:
            item.update(extra)
        try:
            _append_jsonl(EVENT_LOG, item)
        except OSError:
            pass


def _solo_lectura() -> dict:
    ms = Multisesion.__new__(Multisesion)
    d = ms._leer()
    Multisesion._purgar(d)
    return d


def _print_estado(d: dict, foco: str | None = None) -> None:
    print(f"CEREBRO · MULTISESION AGENTICA (schema {d.get('_schema')})" + (f" — foco: {foco}" if foco else " — todos los proyectos/agentes"))
    print("AGENTES:", {k: {"runtime": v.get("runtime"), "ultimo_visto": v.get("ultimo_visto")} for k, v in d.get("agentes", {}).items()} or "(ninguno)")
    print("SESIONES:")
    for sid, s in d["sesiones"].items():
        if foco and s.get("project") != foco:
            continue
        marca = "🟢" if s.get("viva") else "⚫"
        print(f"  {marca} [{s.get('agent','?')}/{s.get('project','?')}] {sid}: {s.get('descripcion','')} | {s.get('tarea')} | {s.get('ultimo_latido')}")
    print("LOCKS:", {r: f"{l['sesion']} ({l.get('motivo','')})" for r, l in d["locks"].items()} or "(ninguno)")
    print("DECISIONES VIGENTES (últimas 10):")
    for dec in d.get("decisiones", [])[-10:]:
        print(f"  [{dec['ts']}] ({dec.get('agent','?')}/{dec.get('project','?')}) {dec['decision']}")
    print("CONOCIMIENTO COMPARTIDO (últimos 8):")
    for c in d.get("conocimiento", [])[-8:]:
        tg = f" #{'/'.join(c.get('tags', []))}" if c.get("tags") else ""
        print(f"  [{c['ts']}] ({c.get('agent','?')}/{c.get('project','?')}) {c['nota']}{tg}")
    print("ÚLTIMOS EVENTOS (12):")
    for e in d["eventos"][-12:]:
        print(f"  [{e['ts']}] ({e.get('agent','?')}/{e.get('project','?')}) {e['detalle']}")


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    foco = sys.argv[1] if len(sys.argv) > 1 else None
    _print_estado(_solo_lectura(), foco)
