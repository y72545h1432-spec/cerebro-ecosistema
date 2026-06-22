"""Tests del GC de ciclo de vida (causa raiz #1: los dicts no se acotaban).
`_purgar` truncaba las listas (eventos/conocimiento) pero NUNCA eliminaba sesiones
muertas ni purgaba buzon/acks -> sesiones crecio a 537 / multisesion.json ~461KB.
STORE temporal aislado. Correr: py -3 test_cerebro_multisesion_gc.py"""
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import cerebro_multisesion as cm


def _ok(name):
    print(f"  ok  {name}")


def _fresh_ms():
    d = Path(tempfile.mkdtemp(prefix="cm_gc_"))
    cm.ARCHIVO = d / "multisesion.json"
    cm.EVENT_LOG = d / "eventos.jsonl"
    cm.LOCKDIR = d / "_locks"
    return cm.Multisesion("test", project="test", agent="claude", runtime="claude-code")


def _viejo(min_atras):
    return (datetime.now() - timedelta(minutes=min_atras)).isoformat(timespec="seconds")


def _past():
    return (datetime.now() - timedelta(hours=1)).isoformat(timespec="seconds")


def _future():
    return (datetime.now() + timedelta(hours=1)).isoformat(timespec="seconds")


# ---- 1: una sesion muerta y vieja se ELIMINA del dict (no solo viva=False) ----
def test_gc_elimina_sesiones_muertas_viejas():
    ms = _fresh_ms()
    def f(d):
        d["sesiones"]["zombi-vieja"] = {
            "project": "x", "viva": False, "host": "otro-host",
            "ultimo_latido": _viejo(cm.RETENER_MUERTAS_MIN + 60), "tarea": "(muerta)"}
    ms._mutar(f)
    assert "zombi-vieja" not in ms.estado()["sesiones"]
    _ok("gc: elimina sesion muerta mas vieja que la ventana de retencion")


# ---- 2: una sesion muerta RECIENTE se conserva (auditoria) ----
def test_gc_conserva_muertas_recientes():
    ms = _fresh_ms()
    def f(d):
        d["sesiones"]["muerta-reciente"] = {
            "project": "x", "viva": False, "host": "otro-host",
            "ultimo_latido": _viejo(10), "tarea": "(muerta)"}
    ms._mutar(f)
    assert "muerta-reciente" in ms.estado()["sesiones"]
    _ok("gc: conserva sesion muerta dentro de la ventana de retencion")


# ---- 3: la sesion viva actual NUNCA se elimina ----
def test_gc_nunca_elimina_la_viva_actual():
    ms = _fresh_ms()
    ms.latido("trabajando")
    assert ms.id in ms.estado()["sesiones"]
    _ok("gc: la sesion viva actual sobrevive al purgado")


# ---- 4: GC de sesion muerta no deja su lock colgando ----
def test_gc_no_deja_locks_colgando():
    ms = _fresh_ms()
    def f(d):
        d["sesiones"]["zombi-con-lock"] = {
            "project": "x", "viva": False, "host": "otro-host",
            "ultimo_latido": _viejo(cm.RETENER_MUERTAS_MIN + 60)}
        d["locks"]["x:recurso"] = {"sesion": "zombi-con-lock", "desde": _viejo(5),
                                   "project": "x", "recurso": "recurso"}
    ms._mutar(f)
    e = ms.estado()
    assert "zombi-con-lock" not in e["sesiones"]
    assert "x:recurso" not in e["locks"]
    _ok("gc: el lock de una sesion muerta no queda colgando")


# ---- 5: buzon personal huerfano de una sesion GC'd se limpia + listas vacias fuera ----
def test_gc_limpia_buzon_huerfano_y_listas_vacias():
    ms = _fresh_ms()
    def f(d):
        d["sesiones"]["zombi-buzon"] = {
            "project": "x", "viva": False, "host": "otro-host",
            "ultimo_latido": _viejo(cm.RETENER_MUERTAS_MIN + 60)}
        d["buzon"]["zombi-buzon"] = [{"id": "m1", "summary": "nunca leido"}]
        d["buzon"]["lista-vacia"] = []
    ms._mutar(f)
    d = ms._leer()
    cm.Multisesion._purgar(d)
    assert "zombi-buzon" not in d["buzon"]
    assert "lista-vacia" not in d["buzon"]
    _ok("gc: limpia buzon personal de sesion GC'd y descarta listas vacias")


# ---- 6: el GC NO rompe dead_letter (un requires_ack vencido sin ack sigue rescatable) ----
def test_gc_preserva_dead_letters():
    ms = _fresh_ms()
    mid = ms.mensaje_tipo("*", type="handoff", requires_ack=True,
                          summary="handoff caido", expires_at=_past())
    # forzar un purgado completo
    ms.latido()
    assert mid in [m["id"] for m in ms.dead_letter()]
    _ok("gc: preserva dead-letters (no borra requires_ack vencido sin ack del buzon *)")


# ---- 7: acks viejos se purgan; los recientes se conservan ----
def test_gc_purga_acks_viejos():
    ms = _fresh_ms()
    def f(d):
        d["acks"]["msg-viejo"] = [{"ts": _viejo(cm.RETENER_MUERTAS_MIN + 60), "nota": "x"}]
        d["acks"]["msg-nuevo"] = [{"ts": _viejo(5), "nota": "y"}]
    ms._mutar(f)
    d = ms._leer()
    cm.Multisesion._purgar(d)
    assert "msg-viejo" not in d["acks"]
    assert "msg-nuevo" in d["acks"]
    _ok("gc: purga acks mas viejos que la retencion, conserva los recientes")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_multisesion_gc ({len(fns)} casos) ==")
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
