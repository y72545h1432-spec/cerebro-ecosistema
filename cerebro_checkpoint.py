"""CEREBRO · CHECKPOINT DE CONTINUIDAD (anti-bugs / muerte subita).

Tapa el unico hueco que la infra de continuidad NO cubre: que una sesion muera de golpe
(crash / freeze / SIGKILL) SIN poder ejecutar el cierre manual (`/remember`, `session-report`,
`ms.despedir()`). Los demas mecanismos ya cubren lo suyo y NO se duplican aqui:
memoria durable (cerebro_memoria), latidos/locks con TTL+PID-alive (cerebro_multisesion),
cola de tareas con visibility-timeout (cerebro_tareas_modelo).

Idea: escribir FRECUENTEMENTE (antes de cada accion larga/arriesgada, no solo al cierre) un
checkpoint ATOMICO al slot que ya se auto-carga al abrir, `.remember/remember.md`, con un marcador
`ESTADO: en-curso`. El cierre limpio lo pasa a `ESTADO: cerrado-limpio`. Al abrir, `recuperar()`
ve si el ultimo checkpoint quedo `en-curso` (= muerte sucia) y dispara RECOVERY MODE.

Por que atomico (tmp + os.replace): si el crash ocurre DURANTE la escritura, un write en sitio
dejaria el handoff truncado justo cuando mas se necesita. os.replace es atomico en NTFS:
o ves el checkpoint viejo entero, o el nuevo entero, nunca medio.

Proceso completo: .cerebro/19_RECUPERACION_POST_CRASH.md

Solo stdlib. Reusa el mutex de proceso de cerebro_multisesion (serializa escrituras concurrentes).
NUNCA lanza en el camino de escritura/lectura (degrada): un anti-bugs que crashea es peor que el bug.

API:
    checkpoint(resumen, proximo_paso, *, tarea=None, proyecto=None, archivos=(), sesion=None) -> ruta
    cerrar_limpio(resumen=None) -> bool
    recuperar() -> dict   # {existe, recovery, estado, timestamp, proyecto, tarea, resumen, proximo_paso, archivos, raw}
CLI:
    py cerebro_checkpoint.py checkpoint -r "<resumen>" -n "<proximo paso>" [-t TAREA -p PROYECTO -a f1 -a f2]
    py cerebro_checkpoint.py cerrar-limpio [-r "<resumen>"]
    py cerebro_checkpoint.py recuperar [--aviso]   # --aviso: banner SOLO si hubo muerte sucia
"""
from __future__ import annotations
import argparse
import datetime as _dt
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cerebro_multisesion import _Mutex  # mutex de proceso (serializa el write)

REMEMBER = pathlib.Path.home() / ".remember" / "remember.md"
EN_CURSO = "en-curso"
CERRADO = "cerrado-limpio"

# Mapa cwd-prefijo -> nombre de proyecto (para inferir proyecto desde el cwd del hook).
# Solo el default NEUTRAL (el hub del propio ecosistema) vive en el codigo; los proyectos PERSONALES
# salen de proyectos.local.toml (gitignored) via cerebro_proyectos -> nada personal queda hardcodeado.
_HOME = str(pathlib.Path.home()).lower().replace("/", "\\")
_PROYECTOS = {_HOME + r"\.cerebro": "hub"}
try:
    import cerebro_proyectos as _proy
    _PROYECTOS.update(_proy.mapa_cwd())
except Exception:
    pass


def _ckpt_dir() -> pathlib.Path:
    """Directorio de checkpoints POR-SESION (derivado de REMEMBER en tiempo de llamada,
    para que los tests que reapuntan REMEMBER tambien reapunten aqui)."""
    return REMEMBER.parent / "checkpoints"


def _ckpt_path(sesion: str) -> pathlib.Path:
    safe = "".join(c if (c.isalnum() or c in "-_.") else "_" for c in str(sesion))[:120] or "sin-sesion"
    return _ckpt_dir() / f"{safe}.md"


def _proyecto_de_cwd(cwd: str | None) -> str | None:
    if not cwd:
        return None
    low = str(cwd).replace("/", "\\").lower().rstrip("\\")
    best = None
    for pref, nombre in _PROYECTOS.items():
        if low == pref or low.startswith(pref + "\\"):
            if best is None or len(pref) > best[0]:
                best = (len(pref), nombre)
    return best[1] if best else None


def _ahora() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _sesion_id(sesion: str | None) -> str:
    if sesion:
        return str(sesion)
    return f"pid-{os.getpid()}"


def _render(estado: str, resumen: str, proximo_paso: str, *, tarea: str | None,
            proyecto: str | None, archivos, sesion: str | None) -> str:
    archivos = [str(a) for a in (archivos or []) if str(a).strip()]
    lineas = [
        f"# HANDOFF / CHECKPOINT - {proyecto or 'general'}",
        "",
        "> Auto-cargado al abrir. Lo escribe cerebro_checkpoint.py (anti-bugs / muerte subita).",
        "> Proceso: .cerebro/19_RECUPERACION_POST_CRASH.md",
        "",
        f"ESTADO: {estado}",
        f"TIMESTAMP: {_ahora()}",
        f"SESION: {_sesion_id(sesion)}",
        f"PROYECTO: {proyecto or ''}",
        f"TAREA: {tarea or ''}",
        "",
        "## Resumen",
        (resumen or "").strip() or "(sin resumen)",
        "",
        "## Proximo paso",
        (proximo_paso or "").strip() or "(sin proximo paso)",
        "",
        "## Archivos tocados",
    ]
    lineas += [f"- {a}" for a in archivos] or ["(ninguno)"]
    lineas.append("")
    return "\n".join(lineas)


def _escribir_atomico(texto: str, destino: pathlib.Path | None = None) -> pathlib.Path:
    """Escribe `texto` a `destino` (REMEMBER por defecto) de forma atomica
    (tmp en el mismo dir + os.replace). Nunca lanza."""
    destino = destino or REMEMBER
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with _Mutex("checkpoint"):
            fd, tmp = tempfile.mkstemp(dir=str(destino.parent), prefix=".remember-", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(texto)
                    fh.flush()
                    os.fsync(fh.fileno())  # durabilidad: el contenido esta en disco antes del replace
                os.replace(tmp, destino)  # atomico en NTFS
            finally:
                if os.path.exists(tmp):
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass
    except Exception as e:  # noqa: BLE001 - el anti-bugs jamas debe tumbar la sesion
        sys.stderr.write(f"[checkpoint] no se pudo escribir: {e}\n")
    return destino


def checkpoint(resumen: str, proximo_paso: str, *, tarea: str | None = None,
               proyecto: str | None = None, archivos=(), sesion: str | None = None) -> pathlib.Path:
    """Escribe un checkpoint `en-curso`. Llamar antes de cada accion larga/arriesgada."""
    return _escribir_atomico(_render(EN_CURSO, resumen, proximo_paso, tarea=tarea,
                                     proyecto=proyecto, archivos=archivos, sesion=sesion))


def cerrar_limpio(resumen: str | None = None, *, sesion: str | None = None) -> bool:
    """Marca un checkpoint como `cerrado-limpio`. Conserva el resto del handoff.

    Si `sesion` se da, cierra el checkpoint POR-SESION de esa sesion (sin pisar a otras sesiones
    concurrentes). Tambien refresca REMEMBER para el auto-load legible. Sin `sesion`, opera sobre
    REMEMBER (comportamiento clasico). Nunca lanza -> devuelve False si falla.
    """
    if sesion:
        path = _ckpt_path(sesion)
        try:
            prev = _parse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            prev = {}
        nuevo_resumen = resumen if resumen is not None else prev.get("resumen", "")
        texto = _render(
            CERRADO, nuevo_resumen, prev.get("proximo_paso", ""),
            tarea=prev.get("tarea") or None, proyecto=prev.get("proyecto") or None,
            archivos=prev.get("archivos", ()), sesion=sesion,
        )
        _escribir_atomico(texto, path)   # cierra SOLO su archivo por-sesion
        _escribir_atomico(texto)         # remember.md legible
        try:
            return _parse(path.read_text(encoding="utf-8")).get("estado") == CERRADO
        except (OSError, UnicodeDecodeError):
            return False

    prev = recuperar()
    nuevo_resumen = resumen if resumen is not None else prev.get("resumen", "")
    texto = _render(
        CERRADO, nuevo_resumen, prev.get("proximo_paso", ""),
        tarea=prev.get("tarea") or None, proyecto=prev.get("proyecto") or None,
        archivos=prev.get("archivos", ()), sesion=None,
    )
    _escribir_atomico(texto)
    return recuperar().get("estado") == CERRADO


def _parse(texto: str) -> dict:
    """Extrae los campos del checkpoint de forma tolerante (lineas `CLAVE: valor` + secciones `## x`)."""
    campos = {"estado": "", "timestamp": "", "proyecto": "", "tarea": "", "sesion": "",
              "resumen": "", "proximo_paso": "", "archivos": []}
    seccion = None
    buf_resumen, buf_prox, archivos = [], [], []
    for ln in texto.splitlines():
        s = ln.strip()
        low = s.lower()
        if low.startswith("estado:"):
            campos["estado"] = s.split(":", 1)[1].strip().lower()
        elif low.startswith("timestamp:"):
            campos["timestamp"] = s.split(":", 1)[1].strip()
        elif low.startswith("sesion:"):
            campos["sesion"] = s.split(":", 1)[1].strip()
        elif low.startswith("proyecto:"):
            campos["proyecto"] = s.split(":", 1)[1].strip()
        elif low.startswith("tarea:"):
            campos["tarea"] = s.split(":", 1)[1].strip()
        elif low.startswith("## resumen"):
            seccion = "resumen"
        elif low.startswith("## proximo"):
            seccion = "prox"
        elif low.startswith("## archivos"):
            seccion = "arch"
        elif s.startswith("## "):
            seccion = None
        elif seccion == "resumen" and s and not s.startswith(">") and not s.startswith("#"):
            buf_resumen.append(s)
        elif seccion == "prox" and s and not s.startswith(">") and not s.startswith("#"):
            buf_prox.append(s)
        elif seccion == "arch" and s.startswith("- "):
            v = s[2:].strip()
            if v and v != "(ninguno)":
                archivos.append(v)
    campos["resumen"] = " ".join(b for b in buf_resumen if b != "(sin resumen)")
    campos["proximo_paso"] = " ".join(b for b in buf_prox if b != "(sin proximo paso)")
    campos["archivos"] = archivos
    return campos


def recuperar() -> dict:
    """Lee el ultimo checkpoint. `recovery=True` si quedo `en-curso` (= muerte sucia). Nunca lanza."""
    out = {"existe": False, "recovery": False, "estado": "", "timestamp": "", "sesion": "",
           "proyecto": "", "tarea": "", "resumen": "", "proximo_paso": "", "archivos": [], "raw": ""}
    try:
        raw = REMEMBER.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return out
    if not raw.strip():
        return out
    out["raw"] = raw
    out.update(_parse(raw))
    out["existe"] = bool(out["estado"]) or bool(out["resumen"])
    out["recovery"] = out["estado"] == EN_CURSO
    return out


# ───────────────────────── auto-checkpoint (sin disciplina) ─────────────────────────

def _texto_de_contenido(contenido) -> str:
    """Aplana el `message.content` de un evento de transcript a texto plano (solo bloques `text`)."""
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for b in contenido:
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
                partes.append(str(b["text"]))
        return " ".join(partes)
    return ""


def _es_prompt_humano(texto: str) -> bool:
    """Filtra prompts reales del usuario (no wrappers de comandos locales ni resúmenes de reanudación)."""
    t = texto.strip()
    if not t:
        return False
    descartar = ("<local-command", "<command-name>", "<command-message>", "<command-args>",
                 "this session is being continued", "caveat: the messages below")
    low = t.lower()
    return not any(d in low for d in descartar)


def _leer_transcript(path: str | None, *, limite_eventos: int = 60):
    """Devuelve (ultimo_prompt_humano, ultimo_texto_asistente) leyendo el tail del .jsonl. Nunca lanza."""
    ultimo_user, ultimo_asis = "", ""
    if not path:
        return ultimo_user, ultimo_asis
    try:
        import json as _json
        p = pathlib.Path(path)
        lineas = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, UnicodeDecodeError):
        return ultimo_user, ultimo_asis
    for ln in lineas[-limite_eventos:]:
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = _json.loads(ln)
        except ValueError:
            continue
        msg = o.get("message") or {}
        role = msg.get("role") or o.get("type")
        txt = _texto_de_contenido(msg.get("content"))
        if not txt.strip():
            continue
        if role == "assistant":
            ultimo_asis = txt
        elif role == "user" and _es_prompt_humano(txt):
            ultimo_user = txt
    return ultimo_user.strip(), ultimo_asis.strip()


def _prune_viejos(dias: int = 7) -> None:
    """Borra checkpoints POR-SESION ya `cerrado-limpio` y mas viejos que `dias`, para que no se
    acumulen sin limite (muchas sesiones multi-modelo). Nunca toca `en-curso`. Nunca lanza."""
    try:
        d = _ckpt_dir()
        if not d.exists():
            return
        limite = _dt.datetime.now() - _dt.timedelta(days=dias)
        for f in d.glob("*.md"):
            try:
                if _dt.datetime.fromtimestamp(f.stat().st_mtime) >= limite:
                    continue
                if _parse(f.read_text(encoding="utf-8")).get("estado") == CERRADO:
                    f.unlink()
            except OSError:
                continue
    except Exception:  # noqa: BLE001
        pass


def auto_desde_payload(payload: dict) -> pathlib.Path | None:
    """Escribe un checkpoint `en-curso` POR-SESION a partir del JSON de un hook de Claude Code.

    payload (lo que Claude Code pasa por stdin): session_id, transcript_path, cwd, prompt, ...
    Captura el estado REAL leyendo el transcript -> no depende de que Claude redacte nada.
    Nunca lanza (un anti-bugs que crashea es peor que el bug)."""
    try:
        if not isinstance(payload, dict):
            return None
        sesion = str(payload.get("session_id") or "").strip()
        if not sesion and payload.get("transcript_path"):
            # en Claude Code el transcript se llama <session_id>.jsonl -> derivar de ahi
            sesion = pathlib.Path(str(payload["transcript_path"])).stem.strip()
        if not sesion:
            return None
        proyecto = _proyecto_de_cwd(payload.get("cwd"))
        prompt = (payload.get("prompt") or "").strip()
        ult_user, ult_asis = _leer_transcript(payload.get("transcript_path"))
        prompt_efectivo = ult_user or (prompt if _es_prompt_humano(prompt) else "")
        resumen = ult_asis or "(auto) sesion activa sin texto de asistente aun"
        proximo = f"(auto) ultimo pedido del usuario: {prompt_efectivo}" if prompt_efectivo \
            else "(auto) continuar la tarea en curso"
        texto = _render(EN_CURSO, resumen, proximo, tarea=None, proyecto=proyecto,
                        archivos=(), sesion=sesion)
        _escribir_atomico(texto, _ckpt_path(sesion))   # por-sesion (decision de recovery)
        _escribir_atomico(texto)                        # remember.md legible (compat auto-load)
        _prune_viejos()                                 # evita acumulacion de cerrados viejos
        return _ckpt_path(sesion)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[checkpoint] auto degradado: {e}\n")
        return None


def escanear(current_session: str | None = None) -> list[dict]:
    """Escanea los checkpoints POR-SESION y devuelve los que quedaron en MUERTE SUCIA:
    `en-curso` y de una sesion distinta a la actual. Asimetria a proposito: preferimos un
    banner de mas (informativo) a perder trabajo en silencio. Nunca lanza."""
    dirty = []
    try:
        d = _ckpt_dir()
        if not d.exists():
            return dirty
        for f in sorted(d.glob("*.md")):
            try:
                campos = _parse(f.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            ses = campos.get("sesion") or f.stem
            if campos.get("estado") != EN_CURSO:
                continue
            if current_session and ses == current_session:
                continue  # reanudacion normal de la propia sesion, no es muerte
            campos["sesion"] = ses
            campos["archivo"] = str(f)
            dirty.append(campos)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[checkpoint] escaneo degradado: {e}\n")
    dirty.sort(key=lambda c: c.get("timestamp", ""), reverse=True)
    return dirty


def _banner(rec: dict) -> str:
    barra = "=" * 64
    return "\n".join([
        barra,
        "  !! RECOVERY MODE - la sesion anterior murio SIN cerrar limpio.",
        f"  Ultimo checkpoint: {rec.get('timestamp','?')}  proyecto: {rec.get('proyecto') or '?'}",
        f"  Tarea: {rec.get('tarea') or '(sin tarea)'}",
        f"  Resumen: {(rec.get('resumen') or '')[:200]}",
        f"  Proximo paso: {(rec.get('proximo_paso') or '')[:200]}",
        "  -> Cruza con tareas huerfanas (cerebro_tareas_modelo.expirar) y locks de PID",
        "     muerto (ms.estado). NO asumas que el contexto esta integro. Confirma con el usuario.",
        "  Detalle del protocolo: .cerebro/19_RECUPERACION_POST_CRASH.md",
        barra,
    ])


def _banner_multi(dirty: list[dict]) -> str:
    barra = "=" * 64
    lineas = [barra, f"  !! RECOVERY MODE - {len(dirty)} sesion(es) murieron SIN cerrar limpio."]
    for i, rec in enumerate(dirty, 1):
        lineas += [
            f"  [{i}] sesion {rec.get('sesion','?')}  {rec.get('timestamp','?')}  "
            f"proyecto: {rec.get('proyecto') or '?'}",
            f"      Estaba: {(rec.get('resumen') or '')[:180]}",
            f"      Proximo: {(rec.get('proximo_paso') or '')[:180]}",
        ]
    lineas += [
        "  -> Puede haber sesiones VIVAS concurrentes aqui: confirma con el usuario antes de retomar.",
        "     Cruza con tareas huerfanas (cerebro_tareas_modelo.expirar) y locks de PID muerto (ms.estado).",
        "  Detalle del protocolo: .cerebro/19_RECUPERACION_POST_CRASH.md",
        barra,
    ]
    return "\n".join(lineas)


def _payload_stdin() -> dict:
    """Lee el JSON que Claude Code pasa por stdin a los hooks. {} si no hay/no es JSON. Nunca lanza."""
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        data = sys.stdin.read()
        if not data.strip():
            return {}
        import json as _json
        obj = _json.loads(data)
        return obj if isinstance(obj, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _cli(argv=None) -> int:
    p = argparse.ArgumentParser(description="Checkpoint de continuidad anti-bugs (muerte subita).")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("checkpoint", help="escribe un checkpoint en-curso")
    c.add_argument("-r", "--resumen", required=True)
    c.add_argument("-n", "--proximo", required=True)
    c.add_argument("-t", "--tarea", default=None)
    c.add_argument("-p", "--proyecto", default=None)
    c.add_argument("-a", "--archivo", action="append", default=[])
    c.add_argument("-s", "--sesion", default=None)

    sub.add_parser("auto", help="auto-checkpoint desde el JSON del hook por stdin (sin disciplina)")

    cl = sub.add_parser("cerrar-limpio", help="marca el checkpoint como cerrado-limpio")
    cl.add_argument("-r", "--resumen", default=None)
    cl.add_argument("-s", "--sesion", default=None, help="cierra el checkpoint de esa sesion (per-sesion)")

    r = sub.add_parser("recuperar", help="lee el checkpoint; --aviso = banner solo si hubo muerte sucia")
    r.add_argument("--aviso", action="store_true")
    r.add_argument("-s", "--sesion", default=None, help="sesion actual (se excluye del escaneo)")

    args = p.parse_args(argv)
    if args.cmd == "checkpoint":
        ruta = checkpoint(args.resumen, args.proximo, tarea=args.tarea, proyecto=args.proyecto,
                          archivos=args.archivo, sesion=args.sesion)
        print(f"[checkpoint] en-curso -> {ruta}")
        return 0
    if args.cmd == "auto":
        ruta = auto_desde_payload(_payload_stdin())
        # a stderr: el stdout de UserPromptSubmit se inyecta al contexto -> debe quedar VACIO
        if ruta:
            sys.stderr.write(f"[checkpoint] auto en-curso -> {ruta}\n")
        return 0  # nunca falla el hook
    if args.cmd == "cerrar-limpio":
        # el hook SessionEnd tambien recibe session_id por stdin; preferimos --sesion, luego stdin
        sesion = args.sesion or (_payload_stdin().get("session_id") or None)
        ok = cerrar_limpio(args.resumen, sesion=sesion)
        print(f"[checkpoint] cerrado-limpio: {ok}")
        return 0 if ok else 1
    if args.cmd == "recuperar":
        if args.aviso:
            actual = args.sesion or (_payload_stdin().get("session_id") or None)
            dirty = escanear(current_session=actual)
            if dirty:
                print(_banner_multi(dirty))
            else:
                # fallback al slot legacy unico (compat: checkpoints sin per-sesion)
                rec = recuperar()
                if rec["recovery"]:
                    print(_banner(rec))
            # silencio si todo cerrado limpio: el hook SessionStart no debe ensuciar
            return 0
        print(recuperar())
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())
