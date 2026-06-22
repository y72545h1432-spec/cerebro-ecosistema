"""Tests del motor de Investigación Infinita globalizado (cerebro_research). Sin red ni GPU:
inyecta una sim_fn determinista. Correr: py -3 test_cerebro_research.py"""
import json
import os
import sys
import tempfile
import traceback

import cerebro_research as cr


def _ok(name):
    print(f"  ok  {name}")


def _sim_fn_falsa(a, b):
    # determinista: 1.0 si comparten la primera palabra, si no 0.0
    return 1.0 if a.split()[:1] == b.split()[:1] else 0.0


def test_enfoque_actual_y_rotacion_circular():
    inv = cr.Investigacion("tu-proyecto-agente")
    assert inv.enfoque_actual() == cr.ENFOQUES_DEFAULT[0]
    assert inv.rotar_enfoque() == cr.ENFOQUES_DEFAULT[1]
    for _ in range(len(cr.ENFOQUES_DEFAULT) - 1):
        inv.rotar_enfoque()
    assert inv.enfoque_actual() == cr.ENFOQUES_DEFAULT[0]
    _ok("enfoque actual + rotación circular")


def test_agregar_enfoque_sin_duplicar():
    inv = cr.Investigacion("tu-proyecto-agente")
    n = len(inv.enfoques)
    inv.agregar_enfoque("toma-de-decisiones")
    inv.agregar_enfoque("toma-de-decisiones")
    assert inv.enfoques[-1] == "toma-de-decisiones"
    assert len(inv.enfoques) == n + 1
    _ok("agregar enfoque en caliente sin duplicar")


def test_es_repetido_usa_sim_fn_y_umbral():
    inv = cr.Investigacion("tu-proyecto-agente", umbral=0.78, sim_fn=_sim_fn_falsa)
    assert inv.es_repetido("percepcion OCR de la pantalla") is False
    inv.nodos.append({"titulo": "percepcion", "resumen": "lectura OCR"})
    assert inv.es_repetido("percepcion del entorno via texto") is True
    assert inv.es_repetido("training de LoRA en Qwen") is False
    _ok("es_repetido usa sim_fn + umbral")


def test_es_repetido_sin_sim_fn_es_falso_seguro():
    inv = cr.Investigacion("tu-proyecto-agente", sim_fn=None)
    inv.nodos.append({"titulo": "x", "resumen": "y"})
    assert inv.es_repetido("cualquier cosa") is False
    _ok("sin sim_fn -> es_repetido False seguro")


def test_agregar_nodo_nuevo_y_repetido():
    inv = cr.Investigacion("tu-proyecto-agente", k=3, m=2, sim_fn=_sim_fn_falsa)
    nodo = inv.agregar_nodo(1, None, "percepcion", "lectura OCR", fuentes=["doi:x"])
    assert nodo is not None and nodo["id"] == "N1" and nodo["estado"] == "nuevo"
    assert nodo["enfoque"] == cr.ENFOQUES_DEFAULT[0] and inv.rep_L1 == 0
    rep = inv.agregar_nodo(1, None, "percepcion", "otra vez")
    assert rep is None and inv.rep_L1 == 1
    _ok("agregar_nodo nuevo devuelve nodo / repetido devuelve None + suma contador")


def test_saturacion_rama_y_tema():
    inv = cr.Investigacion("tu-proyecto-agente", k=3, m=2, sim_fn=_sim_fn_falsa)
    inv.nueva_rama()
    inv.agregar_nodo(2, "N0", "alpha", "base")
    assert inv.rama_saturada() is False
    for _ in range(3):
        inv.agregar_nodo(2, "N0", "alpha", "repe")
    assert inv.rama_saturada() is True

    inv2 = cr.Investigacion("tu-proyecto-agente", m=2, sim_fn=_sim_fn_falsa)
    inv2.agregar_nodo(1, None, "beta", "base")
    inv2.agregar_nodo(1, None, "beta", "repe")
    assert inv2.tema_saturado() is False
    inv2.agregar_nodo(1, None, "beta", "repe2")
    assert inv2.tema_saturado() is True
    _ok("rama_saturada tras k / tema_saturado tras m")


def test_guardar_y_cargar_round_trip():
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, "estado.json")
        inv = cr.Investigacion("tu-proyecto-agente", umbral=0.8, k=4, m=3, sim_fn=_sim_fn_falsa)
        inv.agregar_nodo(1, None, "percepcion", "OCR", fuentes=["s1"], recomendacion="rec1")
        inv.rotar_enfoque()
        inv.rep_L1 = 1
        inv.ola = 2
        inv.guardar(ruta)
        datos = json.loads(open(ruta, encoding="utf-8").read())
        assert datos["tema"] == "tu-proyecto-agente" and datos["ola"] == 2
        rec = cr.Investigacion.cargar(ruta, sim_fn=_sim_fn_falsa)
        assert rec.tema == "tu-proyecto-agente" and rec.umbral == 0.8 and rec.k == 4 and rec.m == 3
        assert rec.idx_enfoque == 1 and rec.rep_L1 == 1 and rec.ola == 2
        assert len(rec.nodos) == 1 and rec.nodos[0]["recomendacion"] == "rec1"
        assert rec.sim_fn is _sim_fn_falsa
        assert rec.es_repetido("percepcion otra vez") is True
    _ok("guardar/cargar round-trip + reanudación no re-investiga vistos")


def test_render_grafo_estructura_y_saturacion():
    inv = cr.Investigacion("tu-proyecto-agente", sim_fn=_sim_fn_falsa)
    r1 = inv.agregar_nodo(1, None, "percepcion", "lectura del entorno",
                          fuentes=["src1"], recomendacion="usar OCR snap")
    inv.nueva_rama()
    inv.agregar_nodo(2, r1["id"], "subpercepcion", "OCR por regiones", recomendacion="cachear")
    md = inv.render_grafo()
    for frag in ("# Investigación Infinita — tu-proyecto-agente", "percepcion", "## ", "subpercepcion",
                 "usar OCR snap", "src1"):
        assert frag in md, f"falta en el grafo: {frag!r}"

    inv2 = cr.Investigacion("tu-proyecto-agente", m=1, sim_fn=_sim_fn_falsa)
    inv2.agregar_nodo(1, None, "beta", "base")
    inv2.agregar_nodo(1, None, "beta", "repe")
    assert "SATURADO" in inv2.render_grafo()
    _ok("render_grafo estructura + marca SATURADO")


def test_sim_semantica_contrato():
    """sim_semantica real (usa cerebro_semantica con degradación stdlib). Float en [0,1]."""
    try:
        s = cr.sim_semantica("percepcion ocr pantalla", "percepcion ocr pantalla")
    except Exception as e:  # pragma: no cover
        print(f"  SKIP sim_semantica (cerebro_semantica no disponible: {e})")
        return
    assert 0.0 <= s <= 1.0 and s >= 0.5
    _ok("sim_semantica contrato [0,1] + idéntico >= 0.5")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_research ({len(fns)} casos) ==")
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
