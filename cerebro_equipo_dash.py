"""cerebro_equipo_dash.py — DASHBOARD en vivo del Agent Team (READ-ONLY, NO daemon).

Compone lo que ya existe en una sola vista: salud de coordinacion (locks stale, dead-letters,
sesiones) + cola de tareas por tier + tiers vivos + estado del kill-switch. No muta nada.

NO es daemon: `--follow N` re-imprime N veces (default 30) con un intervalo y SALE (respeta Regla #3).
    py cerebro_equipo_dash.py --once
    py cerebro_equipo_dash.py --follow 5 --interval 2
    py cerebro_equipo_dash.py --json
"""
from __future__ import annotations
import os
import sys
import json
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cerebro_core as core           # noqa: E402
import cerebro_salud as salud         # noqa: E402
import cerebro_tareas_modelo as tareas  # noqa: E402
import cerebro_modelo as modelo       # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _stop_activo() -> bool:
    try:
        return (core.STATE_DIR / "equipo" / "STOP").exists()
    except OSError:
        return False


def recolectar() -> dict:
    """Snapshot read-only del estado del equipo (compone salud + cola + tiers vivos)."""
    base = salud.recolectar()                       # sesiones/locks/dead_letters (ya read-only)
    tb = tareas.tablero()                           # {tier: [tareas activas]}
    cont = {m: len(ts) for m, ts in tb.items()}
    try:
        vivos = sorted(modelo.vivos())
    except Exception:
        vivos = []
    stale = [l for l in base.get("locks", []) if l.get("stale")]
    return {
        "sesiones_total": base.get("sesiones_total", 0),
        "sesiones_vivas": base.get("sesiones_vivas", 0),
        "tiers_vivos": vivos,
        "cola_activas": cont,
        "locks": base.get("locks", []),
        "locks_stale": len(stale),
        "dead_letters": base.get("dead_letters", []),
        "stop": _stop_activo(),
    }


def _print(d: dict) -> None:
    print("CEREBRO · AGENT TEAM — DASHBOARD (read-only)")
    print(f"  sesiones: {d['sesiones_total']} total / {d['sesiones_vivas']} vivas"
          f"   ·   tiers vivos: {', '.join(d['tiers_vivos']) or '(ninguno)'}"
          f"   ·   STOP: {'SI' if d['stop'] else 'no'}")
    print(f"  cola activas por tier: {d['cola_activas'] or '(vacia)'}")
    print(f"  locks: {len(d['locks'])} (STALE/zombi: {d['locks_stale']})   ·   "
          f"dead-letters: {len(d['dead_letters'])}")
    for l in d["locks"]:
        if l.get("stale"):
            print(f"    ⚠ STALE {l['key']} · holder={l['sesion']} vivo={l['holder_vivo']}")
    for m in d["dead_letters"]:
        print(f"    ⚠ dead-letter {m.get('id')} [{m.get('tipo')}] -> {m.get('destino')}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Dashboard read-only del Agent Team (no daemon).")
    ap.add_argument("--once", action="store_true", help="imprime un snapshot y sale (default)")
    ap.add_argument("--follow", nargs="?", type=int, const=30, default=None,
                    help="re-imprime N veces (default 30) y SALE; no es daemon")
    ap.add_argument("--interval", type=float, default=2.0, help="segundos entre refrescos en --follow")
    ap.add_argument("--json", action="store_true", help="snapshot en JSON (para hub/hooks)")
    a = ap.parse_args(argv)

    if a.json:
        print(json.dumps(recolectar(), ensure_ascii=False, indent=2))
        return _exit_code(recolectar())

    if a.follow:
        n = max(1, a.follow)
        interval = max(0.5, a.interval)
        for i in range(n):
            d = recolectar()
            print(f"\n--- refresco {i + 1}/{n} ---")
            _print(d)
            if i < n - 1:
                time.sleep(interval)
        return _exit_code(recolectar())

    d = recolectar()
    _print(d)
    return _exit_code(d)


def _exit_code(d: dict) -> int:
    """1 si hay algo que atender (lock stale, dead-letter o STOP activo); 0 si todo en orden."""
    return 1 if (d.get("locks_stale") or d.get("dead_letters") or d.get("stop")) else 0


if __name__ == "__main__":
    raise SystemExit(main())
