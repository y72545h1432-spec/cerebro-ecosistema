"""cerebro.py — CLI UNICO del ecosistema (un solo punto de entrada que despacha a los demas).

POR QUE EXISTE (2026-06-21): habia 17 puntos de entrada CLI separados (`py cerebro_X.py ...`). Este
dispatcher unifica todo bajo `py cerebro.py <area> [args...]`, al estilo de `git` que delega en
`git-<sub>`. NO reimplementa logica: reenvia al modulo correcto como subproceso, conservando su
comportamiento, encoding y codigo de salida EXACTOS. Los `py cerebro_X.py ...` antiguos siguen
funcionando (compatibilidad; deprecacion suave).

Uso:
    py cerebro.py                      # lista las areas
    py cerebro.py <area> --help        # ayuda del area (la del modulo)
    py cerebro.py tareas pendientes haiku
    py cerebro.py coord                # estado de la multisesion
    py cerebro.py salud --json
    py cerebro.py equipo drenar --tier haiku --confirm    # (Fase 2-3)
"""
from __future__ import annotations
import os
import sys
import subprocess

AQUI = os.path.dirname(os.path.abspath(__file__))

# area -> (modulo, descripcion corta). El modulo se invoca como `py <modulo> <resto-de-args>`.
AREAS = {
    "tareas":     ("cerebro_tareas_modelo.py", "cola de tareas por modelo (publicar/pendientes/tomar/...)"),
    "modelo":     ("cerebro_modelo.py",        "router por tier (soy/vivos/registrar/clasificar/delegar)"),
    "coord":      ("cerebro_multisesion.py",   "estado de coordinacion multi-agente (sesiones/locks/buzon)"),
    "salud":      ("cerebro_salud.py",         "telemetria read-only (locks stale, dead-letters, conflictos)"),
    "watch":      ("cerebro_watch.py",         "watcher de eventos (--once / --follow --seconds N)"),
    "checkpoint": ("cerebro_checkpoint.py",    "checkpoint anti-crash (checkpoint/cerrar-limpio/recuperar)"),
    "hechos":     ("cerebro_hechos.py",        "hechos verificables (probe/verificar/conflictos/...)"),
    "memoria":    ("cerebro_memoria.py",       "memoria durable (recordar/leer/buscar/indice/reindexar)"),
    "coprog":     ("cerebro_coprog.py",        "co-programacion: tablero de locks de archivo (board/check)"),
    "grafo":      ("cerebro_grafo.py",         "grafo de codigo on-demand (simbolo/arquitectura)"),
    "equipo":     ("cerebro_equipo.py",        "supervisor del Agent Team (drenar/debate/reanudar/dash)"),
}

# sub-areas de 'skills' -> modulo. `py cerebro.py skills <sub> [args]`.
SKILLS = {
    "audit":    "cerebro_skills_audit.py",
    "diff":     "cerebro_skills_diff.py",
    "sync":     "cerebro_skills_sync.py",
    "dispatch": "cerebro_skill_dispatch.py",
}


def _correr(modulo: str, args: list[str]) -> int:
    """Reenvia al modulo como subproceso, heredando stdin/stdout/stderr y devolviendo su exit code."""
    ruta = os.path.join(AQUI, modulo)
    if not os.path.exists(ruta):
        print(f"cerebro: '{modulo}' aun no existe (proximamente).", file=sys.stderr)
        return 3
    # Lista de args (sin shell): sin riesgo de inyeccion ni de re-cotizado de comillas en Windows.
    return subprocess.run([sys.executable, ruta, *args]).returncode


def _uso() -> None:
    print("cerebro — CLI unico del ecosistema multi-agente\n")
    print("uso: py cerebro.py <area> [args...]\n")
    print("AREAS:")
    for a, (_mod, desc) in AREAS.items():
        print(f"  {a:<11} {desc}")
    print(f"  {'skills':<11} auditoria/sincronizacion de skills ({'/'.join(SKILLS)})")
    print("\nayuda de un area:  py cerebro.py <area> --help")


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        _uso()
        return 0
    area, resto = argv[0], argv[1:]
    if area == "skills":
        if not resto or resto[0] in ("-h", "--help", "help"):
            print("uso: py cerebro.py skills <sub> [args]   subs: " + ", ".join(SKILLS))
            return 0
        sub, sargs = resto[0], resto[1:]
        if sub not in SKILLS:
            print(f"cerebro: sub de skills desconocido: {sub!r} (usa {', '.join(SKILLS)})", file=sys.stderr)
            return 2
        return _correr(SKILLS[sub], sargs)
    if area not in AREAS:
        print(f"cerebro: area desconocida: {area!r}\n", file=sys.stderr)
        _uso()
        return 2
    return _correr(AREAS[area][0], resto)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main(sys.argv[1:]))
