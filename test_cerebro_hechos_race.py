"""Test de la RACE de escritura de cerebro_hechos (_append protegido con FileMutex, fix 2026-06-21).

Reproduce la condicion REAL del incidente: N procesos concurrentes anexando al MISMO hechos.jsonl.
Sin el mutex de proceso, dos appends pueden interleaver -> linea JSON corrupta (rompe la deteccion de
conflictos) o lineas perdidas. Con el mutex, las N*M lineas quedan integras y parseables.

Aislado via LOCALAPPDATA temporal: redirige core.STATE_DIR -> hechos.jsonl + el dir de _locks del
mutex, sin tocar el estado real. Correr: py -3 test_cerebro_hechos_race.py"""
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

CEREBRO = os.path.dirname(os.path.abspath(__file__))
N_PROC = 6
M_EACH = 30

# Cada worker (proceso aparte) anexa M lineas al MISMO hechos.jsonl via _append (la funcion que el
# fix protegio con FileMutex). Directo a _append: aisla la serializacion de escritura, sin el O(n^2)
# de la deteccion de conflictos (que es lectura y no toca la race).
_WORKER = (
    "import sys; sys.path.insert(0, r'{cer}'); "
    "import cerebro_hechos as h; "
    "[h._append(h.HECHOS, {{'w': {wid}, 'i': i}}) for i in range({m})]"
)


def test_append_concurrente_no_corrompe():
    tmp = Path(tempfile.mkdtemp(prefix="hechos_race_"))
    env = dict(os.environ)
    env["LOCALAPPDATA"] = str(tmp)   # redirige hechos.jsonl + _locks del mutex a un sandbox

    procs = []
    for w in range(N_PROC):
        code = _WORKER.format(cer=CEREBRO, wid=w, m=M_EACH)
        procs.append(subprocess.Popen([sys.executable, "-c", code], env=env,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.PIPE))
    errs = []
    for p in procs:
        _, e = p.communicate(timeout=180)
        if p.returncode != 0:
            errs.append((e or b"").decode("utf-8", "replace"))
    assert not errs, "algun worker fallo:\n" + "\n".join(errs)

    hechos = tmp / "cerebro" / "hechos.jsonl"
    lines = [ln for ln in hechos.read_text(encoding="utf-8").splitlines() if ln.strip()]
    # cada linea debe ser JSON valido (sin interleaving) y deben estar TODAS (sin perdidas)
    for ln in lines:
        json.loads(ln)   # lanza si una linea quedo corrupta -> el test falla
    assert len(lines) == N_PROC * M_EACH, f"esperaba {N_PROC * M_EACH} hechos integros, hay {len(lines)}"
    print(f"  ok  _append concurrente: {len(lines)} lineas integras de {N_PROC} procesos "
          f"(sin corrupcion ni perdida; el FileMutex serializo las escrituras)")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("== test_cerebro_hechos_race (1 caso) ==")
    test_append_concurrente_no_corrompe()
    print("\n1/1 verde")
