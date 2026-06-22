"""Tests del ranker semantico neutral (cerebro_semantica). Sin red: inyecta un embedder denso falso
para probar la capa densa, y prueba la degradacion (token-coseno) sin backend.
Correr: py -3 test_cerebro_semantica.py"""
import sys
import traceback

import cerebro_semantica as cs


def _ok(name):
    print(f"  ok  {name}")


def _reset():
    cs.register_dense_embedder(None)
    cs._DENSE_TRIED = True   # evita auto-registrar el embedder local real durante el test


# Embedder denso FALSO determinista: vector por presencia de conceptos (sinonimos comparten eje).
_CONImport = {
    "cansancio": 0, "fatiga": 0, "cansad": 0, "agotad": 0, "coste": 0, "control": 0,  # eje 0: fatiga
    "color": 1, "rojo": 1, "azul": 1, "pintura": 1,                                   # eje 1: color
    "gpu": 2, "vram": 2, "tarjeta": 2, "memoria": 2,                                  # eje 2: hardware
}


def _fake_embed(texts):
    vecs = []
    for t in texts:
        v = [0.0, 0.0, 0.0, 0.01]
        low = t.lower()
        for token, eje in _CONImport.items():
            if token in low:
                v[eje] += 1.0
        vecs.append(v)
    return vecs


# ---- 1: capa densa -> sinonimo (sin solape lexico) rankea por ENCIMA de lo irrelevante ----
def test_denso_sinonimo_gana():
    _reset()
    cs.register_dense_embedder(_fake_embed)
    docs = ["el agente acumula coste de control y baja el ritmo",   # fatiga (sin la palabra 'fatiga')
            "elegir el color rojo o azul de la pintura",
            "la GPU tiene poca VRAM en la tarjeta"]
    sc = cs.scores("fatiga", docs)
    assert sc[0] == max(sc), sc
    _ok("denso: 'fatiga' rankea 1º el doc de 'coste de control' (sinonimo, 0 solape lexico)")


# ---- 2: has_dense refleja el registro ----
def test_has_dense():
    _reset()
    assert cs.has_dense() is False
    cs.register_dense_embedder(_fake_embed)
    assert cs.has_dense() is True
    _ok("has_dense: refleja si hay embedder denso")


# ---- 3: sin backend denso -> token-coseno SIEMPRE da una lista (degradacion elegante) ----
def test_degrada_sin_denso():
    _reset()
    docs = ["abrir el menu inicio con la tecla win", "cerrar la ventana activa"]
    sc = cs.scores("tecla win menu", docs)
    assert isinstance(sc, list) and len(sc) == 2 and sc[0] > sc[1], sc
    _ok("degradacion: sin denso, token-coseno ordena por solape lexico (nunca rompe)")


# ---- 4: best() devuelve (indice, score) del mas similar ----
def test_best():
    _reset()
    cs.register_dense_embedder(_fake_embed)
    docs = ["pintura de color azul", "se quedo sin vram la gpu"]
    b = cs.best("tarjeta grafica memoria", docs)
    assert b is not None and b[0] == 1, b
    _ok("best: indice del doc mas similar (hardware->doc de gpu/vram)")


# ---- 5: docs vacios -> [] (no rompe) ----
def test_vacio():
    _reset()
    assert cs.scores("algo", []) == []
    assert cs.best("algo", []) is None
    _ok("vacio: sin docs devuelve [] / None")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_semantica ({len(fns)} casos) ==")
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
