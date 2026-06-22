"""Tests de la mensajeria de tareas por modelo. Usa un STORE temporal (no toca el real).
Correr: py -3 test_cerebro_tareas_modelo.py"""
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import cerebro_tareas_modelo as tm


def _ok(name):
    print(f"  ok  {name}")


def _fresh():
    # dir unico por caso: evita colision de nombres (id(object()) reutiliza direcciones) y
    # aisla el .bak que escribe la io atomica de cerebro_core.
    tm.STORE = Path(tempfile.mkdtemp(prefix="tm_test_")) / "tareas.json"


# ---- 1: publicar exige detalles; routing por modelo (tier + 'any') ----
def test_publicar_y_pendientes():
    _fresh()
    tm.publicar("limpiar imports", "rama mecanica", modelo="haiku",
                terminado="ruff limpio", archivos="x.py", pruebas="ruff x.py")
    tm.publicar("disenar arquitectura", "decision dificil", modelo="opus", terminado="diseno aprobado")
    tm.publicar("tarea general", "para cualquiera", modelo="any", terminado="hecha")
    ph = [t["id"] for t in tm.pendientes("haiku")]
    po = [t["id"] for t in tm.pendientes("opus")]
    # haiku ve las suyas + 'any'; opus ve las suyas + 'any'; ninguna ve la del otro tier
    assert "M001" in ph and "M003" in ph and "M002" not in ph, ph
    assert "M002" in po and "M003" in po and "M001" not in po, po
    _ok("publicar + pendientes: routing por tier de modelo incluye 'any', excluye otros tiers")


# ---- 2: tomar es atomico (un segundo intento falla) ----
def test_tomar_atomico():
    _fresh()
    tid = tm.publicar("t", "p", modelo="haiku", terminado="ok")
    assert tm.tomar(tid, "sesion-haiku-1") is True
    assert tm.tomar(tid, "sesion-haiku-2") is False           # ya tomada
    assert tid not in [t["id"] for t in tm.pendientes("haiku")]  # ya no esta pendiente
    _ok("tomar: reclamo atomico, un segundo tomar falla y sale de pendientes")


# ---- 3: completar cierra y registra; no se puede recompletar ----
def test_completar():
    _fresh()
    tid = tm.publicar("t", "p", modelo="sonnet", terminado="ok")
    tm.tomar(tid, "s1")
    assert tm.completar(tid, "resultado x", por="s1") is True
    assert tm.completar(tid, "otra vez") is False
    _ok("completar: cierra una vez; recompletar devuelve False")


# ---- 4: tablero agrupa activas por modelo, oculta cerradas ----
def test_tablero():
    _fresh()
    a = tm.publicar("a", "p", modelo="haiku", terminado="ok")
    tm.publicar("b", "p", modelo="opus", terminado="ok")
    tm.completar(a, "done")                       # cerrada -> no aparece
    tb = tm.tablero()
    assert "opus" in tb and "haiku" not in tb, tb
    _ok("tablero: agrupa activas por modelo y oculta las cerradas")


# ---- 5: modelo invalido cae a 'any' (degradacion segura) ----
def test_modelo_invalido():
    _fresh()
    tid = tm.publicar("t", "p", modelo="gpt-9000", terminado="ok")
    assert tm._load()["tareas"][tid]["modelo"] == "any"
    assert tid in [t["id"] for t in tm.pendientes("haiku")]   # 'any' la ve cualquiera
    _ok("modelo invalido -> 'any' (lo ve cualquier sesion)")


# ---- 6: estados terminales fallida/rechazada (A2A failed/rejected) no se reabren ----
def test_estados_terminales_fallar_rechazar():
    _fresh()
    a = tm.publicar("a", "p", modelo="haiku", terminado="ok")
    tm.tomar(a, "s1")
    assert tm.fallar(a, "exploto al correr", por="s1") is True
    assert tm._load()["tareas"][a]["estado"] == "fallida"
    assert tm.completar(a, "no") is False                    # terminal: no se reabre
    b = tm.publicar("b", "p", modelo="haiku", terminado="ok")
    assert tm.rechazar(b, "fuera de mi alcance", por="s1") is True
    assert tm._load()["tareas"][b]["estado"] == "rechazada"
    assert b not in [t["id"] for t in tm.pendientes("haiku")]  # ya no pendiente
    _ok("estados terminales: fallar/rechazar cierran y no se reabren; salen de pendientes")


# ---- 7: visibility timeout: 'tomada' colgada (worker muerto) vuelve a 'pendiente' ----
def test_expirar_tomadas_reclama_worker_muerto():
    _fresh()
    a = tm.publicar("a", "p", modelo="haiku", terminado="ok")
    tm.tomar(a, "sesion-muerta")
    futuro = datetime.now() + timedelta(minutes=60)
    reclamadas = tm.expirar_tomadas(ttl_min=30, ahora=futuro)
    assert a in reclamadas
    t = tm._load()["tareas"][a]
    assert t["estado"] == "pendiente" and t["tomada_por"] == ""
    assert a in [x["id"] for x in tm.pendientes("haiku")]      # re-entregable
    _ok("expirar_tomadas: reclama una 'tomada' vencida -> vuelve a pendiente y re-entregable")


# ---- 8: una 'tomada' reciente NO se reclama (worker vivo trabajando) ----
def test_expirar_no_toca_recientes():
    _fresh()
    a = tm.publicar("a", "p", modelo="haiku", terminado="ok")
    tm.tomar(a, "s1")
    assert tm.expirar_tomadas(ttl_min=30) == []               # ahora=now, recien tomada
    assert tm._load()["tareas"][a]["estado"] == "tomada"
    _ok("expirar_tomadas: respeta tareas recien tomadas (no roba trabajo en curso)")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_tareas_modelo ({len(fns)} casos) ==")
    for fn in fns:
        try:
            fn(); ok += 1
        except Exception:
            print("FAIL", fn.__name__); traceback.print_exc()
    print(f"\n{ok}/{len(fns)} verde")
    sys.exit(0 if ok == len(fns) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _run()
