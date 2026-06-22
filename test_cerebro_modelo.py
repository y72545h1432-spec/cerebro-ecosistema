"""Tests del router por modelo. Usa STORE/cola temporales (no toca los reales).
Correr: py -3 test_cerebro_modelo.py"""
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import cerebro_modelo as cm
import cerebro_tareas_modelo as tm


def _ok(name):
    print(f"  ok  {name}")


def _fresh():
    cm.STORE = Path(tempfile.gettempdir()) / f"cm_test_{id(object())}.json"
    if cm.STORE.exists():
        cm.STORE.unlink()
    tm.STORE = Path(tempfile.gettempdir()) / f"cmtm_test_{id(object())}.json"
    if tm.STORE.exists():
        tm.STORE.unlink()


# ---- 1: tier_de mapea por substring; desconocido/fable -> opus (default seguro) ----
def test_tier_de():
    _fresh()
    assert cm.tier_de("claude-opus-4-8") == "opus"
    assert cm.tier_de("claude-sonnet-4-6") == "sonnet"
    assert cm.tier_de("claude-haiku-4-5-20251001") == "haiku"
    assert cm.tier_de("claude-fable-5") == "opus"          # tope de gama -> tier opus
    assert cm.tier_de("gpt-9000") == "opus"                # desconocido -> opus (seguro)
    assert cm.tier_de("") == "opus"
    _ok("tier_de: opus/sonnet/haiku/fable; desconocido y vacio -> opus")


# ---- 2: registrar + vivos respeta TTL (heartbeat viejo no cuenta) ----
def test_registrar_y_vivos_ttl():
    _fresh()
    cm.registrar("haiku", "s-haiku")
    cm.registrar("opus", "s-opus")
    assert cm.vivos() == {"haiku", "opus"}
    # un heartbeat de hace 20 min queda fuera de un TTL de 15 min
    viejo = (datetime.now() - timedelta(minutes=20)).isoformat(timespec="seconds")
    d = {"haiku": {"sesion": "s", "ts": viejo}, "opus": {"sesion": "s", "ts": cm._now()}}
    assert cm.vivos(d=d) == {"opus"}, cm.vivos(d=d)
    _ok("registrar/vivos: heartbeat fresco cuenta; mas viejo que el TTL no")


def test_registrar_tier_invalido():
    _fresh()
    try:
        cm.registrar("gpt")
    except ValueError:
        _ok("registrar: tier invalido lanza ValueError"); return
    raise AssertionError("se esperaba ValueError para tier invalido")


# ---- 3: clasificar — mecanico->haiku, dificil->opus, intermedio->sonnet, opus gana sobre haiku ----
def test_clasificar():
    _fresh()
    assert cm.clasificar("renombrar variables en x.py")[0] == "haiku"
    assert cm.clasificar("disenar la arquitectura del router")[0] == "opus"
    assert cm.clasificar("escribir el correo al cliente")[0] == "sonnet"
    # senal de ambos: arquitectura (opus) + mover (haiku) -> gana opus
    tier, razon = cm.clasificar("refactor de arquitectura y mover archivos")
    assert tier == "opus", (tier, razon)
    assert razon                                           # razon nunca vacia
    _ok("clasificar: mecanico->haiku, dificil->opus, intermedio->sonnet, opus>haiku, con razon")


# ---- 4: delegar publica en la cola con el tier correcto y arma el aviso segun worker vivo ----
def test_delegar_con_worker_vivo():
    _fresh()
    r = cm.delegar("limpiar imports", "rama mecanica", tier="haiku", terminado="ruff limpio",
                   archivos="x.py", pruebas="ruff x.py", tiers_vivos={"haiku"})
    assert r["tier"] == "haiku" and r["worker_vivo"] is True
    assert r["id"] in [t["id"] for t in tm.pendientes("haiku")]   # quedo encolada para haiku
    assert "tomara" in r["aviso"]
    _ok("delegar: con worker vivo publica para el tier y avisa que lo tomara")


def test_delegar_sin_worker_vivo():
    _fresh()
    r = cm.delegar("limpiar imports", "rama mecanica", tier="haiku", terminado="ruff limpio",
                   tiers_vivos=set())
    assert r["worker_vivo"] is False
    assert "abre una sesion haiku" in r["aviso"]
    _ok("delegar: sin worker vivo encola y avisa que abras la sesion del tier")


def test_delegar_tier_invalido():
    _fresh()
    try:
        cm.delegar("t", "p", tier="gpt", tiers_vivos=set())
    except ValueError:
        _ok("delegar: tier invalido lanza ValueError"); return
    raise AssertionError("se esperaba ValueError")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_modelo ({len(fns)} casos) ==")
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
