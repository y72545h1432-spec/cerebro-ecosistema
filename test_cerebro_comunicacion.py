"""Tests de fiabilidad de entrega del buzon (O20 dead-letter). STORE temporal aislado.
Correr: py -3 test_cerebro_comunicacion.py"""
import sys
import tempfile
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import cerebro_multisesion as cm


def _ok(name):
    print(f"  ok  {name}")


def _fresh_ms():
    d = Path(tempfile.mkdtemp(prefix="cm_test_"))
    cm.ARCHIVO = d / "multisesion.json"
    cm.EVENT_LOG = d / "eventos.jsonl"
    cm.LOCKDIR = d / "_locks"
    return cm.Multisesion("test", project="test", agent="claude", runtime="claude-code")


def _past():
    return (datetime.now() - timedelta(hours=1)).isoformat(timespec="seconds")


def _future():
    return (datetime.now() + timedelta(hours=1)).isoformat(timespec="seconds")


# ---- 1: un requires_ack que vencio SIN ack se rescata (no se pierde en silencio) ----
def test_dead_letter_rescata_vencido_sin_ack():
    ms = _fresh_ms()
    mid = ms.mensaje_tipo("*", type="handoff", priority="high", requires_ack=True,
                          summary="handoff caido", expires_at=_past())
    assert mid not in [m["id"] for m in ms.leer_buzon()]      # leer_buzon lo oculta (vencido)
    assert mid in [m["id"] for m in ms.dead_letter()]          # dead_letter SI lo rescata
    _ok("dead_letter: rescata requires_ack vencido sin ack (handoff caido)")


# ---- 2: si fue ackeado a tiempo, NO es dead-letter ----
def test_dead_letter_excluye_ackeados():
    ms = _fresh_ms()
    mid = ms.mensaje_tipo("*", type="blocker", requires_ack=True,
                          summary="x", expires_at=_past())
    ms.ack(mid, "atendido")
    assert mid not in [m["id"] for m in ms.dead_letter()]
    _ok("dead_letter: excluye mensajes ya ackeados")


# ---- 3: ignora vigentes y los que no exigen ack (no son perdidas) ----
def test_dead_letter_ignora_vigentes_y_sin_requires_ack():
    ms = _fresh_ms()
    vigente = ms.mensaje_tipo("*", requires_ack=True, summary="vigente", expires_at=_future())
    sin_ack = ms.mensaje_tipo("*", requires_ack=False, summary="aviso", expires_at=_past())
    dl = [m["id"] for m in ms.dead_letter()]
    assert vigente not in dl and sin_ack not in dl
    _ok("dead_letter: ignora vigentes y los que no exigen ack")


# ---- 4: handoff() empaqueta el contrato estructurado (O26 anti spec-ambiguity) ----
def test_handoff_empaqueta_contrato_estructurado():
    ms = _fresh_ms()
    mid = ms.handoff("*", goal="migrar X a Y", next_step="correr tests de Y",
                     acceptance="suite Y verde 0 regresiones", done="diseno listo",
                     findings="Y usa schema 5", open_questions="¿tocar Z?",
                     constraints="no tocar A")
    msgs = ms.leer_buzon(type="handoff")
    m = next(x for x in msgs if x["id"] == mid)
    assert m["requires_ack"] is True                       # closed-loop: exige confirmacion
    h = m["evidence"][0]["handoff"]                         # paquete estructurado, no prosa cruda
    assert h["goal"] == "migrar X a Y"
    assert h["acceptance"] == "suite Y verde 0 regresiones"
    assert h["next_step"] == "correr tests de Y"
    _ok("handoff: empaqueta goal/next_step/acceptance + estado en evidence estructurado")


# ---- 5: handoff() RECHAZA un handoff incompleto (la causa #1 de fallo) ----
def test_handoff_exige_minimos_anti_ambiguedad():
    ms = _fresh_ms()
    for faltante in ("goal", "next_step", "acceptance"):
        kw = {"goal": "g", "next_step": "n", "acceptance": "a"}
        kw[faltante] = "   "                               # vacio/whitespace
        try:
            ms.handoff("*", **kw)
            raise AssertionError(f"deberia rechazar handoff sin {faltante}")
        except ValueError:
            pass
    _ok("handoff: rechaza handoff sin goal/next_step/acceptance (no pasa ambiguedad)")


# ---- 6: el receptor recupera el paquete intacto (round-trip) ----
def test_handoff_round_trip_receptor():
    ms = _fresh_ms()
    ms.handoff(f"agent:{ms.agent}", goal="g", next_step="n", acceptance="a",
               findings="hallazgo clave")
    recibido = ms.leer_buzon(type="handoff")[0]
    assert recibido["evidence"][0]["handoff"]["findings"] == "hallazgo clave"
    _ok("handoff: el receptor recupera el paquete estructurado intacto")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_comunicacion ({len(fns)} casos) ==")
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
