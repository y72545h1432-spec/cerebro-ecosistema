#!/usr/bin/env python3
"""cerebro_salud.py — TELEMETRIA de lo que YA existe pero estaba INVISIBLE.

Causa raiz #4 de la investigacion infinita del ecosistema (saturacion L3, 2026-06-18,
`investigacion_ecosistema/BACKLOG.md` P1.2): dead-letters, locks globales, conflictos de
hechos y sesiones-zombi viven en disco pero NADA los muestra -> se acumulan en silencio.

Esto es un panel READ-ONLY (no muta estado) de un solo comando:
    py -3 cerebro_salud.py            # panel humano
    py -3 cerebro_salud.py --json     # JSON (para hub_dashboard / otro panel)

Fuentes: %LOCALAPPDATA%/cerebro/multisesion.json (locks/buzon/sesiones) + cerebro_hechos.py.
Espejo READ-ONLY de la logica de Multisesion.dead_letter (no la muta ni la marca).
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core  # base comun: lectura tolerante + edad en minutos

try:  # consola Windows cp1252 -> evita UnicodeEncodeError/mojibake (convencion del ecosistema)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STATE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "cerebro" / "multisesion.json"
LOCK_TTL_MIN = 30  # espejo de cerebro_multisesion: locks viejos caducan a ~30 min
AQUI = Path(__file__).resolve().parent


def _leer() -> dict:
    return core.read_json_tolerant(STATE) or {}


def _edad_min(iso, now):
    return core.age_minutes(iso, now)


def locks(d: dict, now: datetime) -> list:
    """Locks tomados, marcados GLOBAL (`*:`) y STALE (holder no vivo / edad > TTL).
    Un lock STALE global = el riesgo real de la refutacion L3 (zombi de batch reteniendo GPU)."""
    out = []
    ses = d.get("sesiones", {})
    for k, v in (d.get("locks") or {}).items():
        if not isinstance(v, dict):
            continue
        sid = v.get("sesion")
        s = ses.get(sid, {}) if isinstance(ses, dict) else {}
        viva = bool(s.get("viva"))
        edad = _edad_min(v.get("desde") or v.get("ts") or s.get("ultimo_latido"), now)
        es_global = str(k).startswith("*:")
        stale = (not viva) or (edad is not None and edad > LOCK_TTL_MIN)
        out.append({"key": k, "sesion": sid, "global": es_global, "holder_vivo": viva,
                    "edad_min": round(edad, 1) if edad is not None else None, "stale": stale})
    return out


def dead_letters(d: dict, now: datetime) -> list:
    """Espejo read-only de Multisesion.dead_letter: mensajes requires_ack cuyo expires_at
    vencio sin ack -> handoffs/blockers caidos en silencio (cola at-least-once)."""
    acks = d.get("acks", {})
    out, vistos = [], set()
    for destino, msgs in (d.get("buzon") or {}).items():
        for m in msgs or []:
            if not m.get("requires_ack"):
                continue
            exp = m.get("expires_at")
            if not exp:
                continue
            try:
                if datetime.fromisoformat(exp) > now:
                    continue
            except Exception:
                continue
            mid = m.get("id")
            if mid in vistos or acks.get(mid):
                continue
            vistos.add(mid)
            out.append({"id": mid, "de": m.get("de"), "destino": destino,
                        "tipo": m.get("type"), "texto": (m.get("texto") or "")[:80], "expiro": exp})
    return out


def conflictos() -> str:
    try:
        r = subprocess.run([sys.executable, str(AQUI / "cerebro_hechos.py"), "conflictos"],
                           capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr or "").strip()
    except Exception as e:
        return f"(no se pudo consultar conflictos: {e})"


def recolectar() -> dict:
    now = datetime.now()
    d = _leer()
    ses = d.get("sesiones", {})
    vivas = sum(1 for s in ses.values() if isinstance(s, dict) and s.get("viva"))
    return {"estado": str(STATE), "sesiones_total": len(ses), "sesiones_vivas": vivas,
            "locks": locks(d, now), "dead_letters": dead_letters(d, now)}


def main() -> int:
    data = recolectar()
    if "--json" in sys.argv:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    lk, dl = data["locks"], data["dead_letters"]
    stale = [l for l in lk if l["stale"]]
    print("CEREBRO · SALUD DE COORDINACION (read-only)")
    print(f"  estado:   {data['estado']}")
    print(f"  sesiones: {data['sesiones_total']} total / {data['sesiones_vivas']} vivas")
    print()
    print(f"LOCKS ({len(lk)}; STALE/zombi: {len(stale)}):")
    if not lk:
        print("  (ninguno tomado)")
    for l in lk:
        tag = "GLOBAL" if l["global"] else "proj  "
        warn = "  <-- STALE/zombi (recurso retenido; revisar GPU/tu servidor LLM local)" if l["stale"] else ""
        print(f"  [{tag}] {l['key']} · holder={l['sesion']} vivo={l['holder_vivo']} edad={l['edad_min']}min{warn}")
    print()
    print(f"DEAD-LETTERS vigentes ({len(dl)}):")
    if not dl:
        print("  (ninguno)")
    for m in dl:
        print(f"  {m['id']} [{m['tipo']}] de={m['de']} -> {m['destino']} | {m['texto']} (expiro {m['expiro']})")
    print()
    print("CONFLICTOS de hechos (cerebro_hechos.py conflictos):")
    print("  " + conflictos().replace("\n", "\n  "))
    # exit 1 si hay algo que requiere atencion (util para hooks/monitor)
    return 1 if (stale or dl) else 0


if __name__ == "__main__":
    raise SystemExit(main())
