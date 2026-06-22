"""Tests de cerebro_hechos (capa anti-discrepancias). Aislado: redirige el almacen a un tmp y NO
avisa por Multisesion. Ejecutar: python test_cerebro_hechos.py
"""
import sys, tempfile, pathlib

import cerebro_hechos as H


def _ok(name):
    print(f"  ok  {name}")


def _aislar():
    """Redirige los JSONL del modulo a un directorio temporal limpio por test."""
    d = pathlib.Path(tempfile.mkdtemp(prefix="hechos_test_"))
    H.HECHOS = d / "hechos.jsonl"
    H.RESOLUCIONES = d / "resueltos.jsonl"


def _set_env(host="PC", py="3.12.0", venv="", python="C:/py/python.exe"):
    H.env_fingerprint = lambda: {"host": host, "cwd": "x", "python": python,
                                 "py_version": py, "venv": venv, "os": "win"}


def test_probe_ok():
    _aislar()
    res = H.probe("t/ok", [sys.executable, "-c", "pass"], agent="claude", avisar=False)
    assert res["hecho"]["status"] == "ok" and res["hecho"]["exit_code"] == 0, res
    assert res["conflicto"] is None
    _ok("probe de comando exit 0 -> status ok, sin conflicto (ground truth)")


def test_probe_fail_captura_salida():
    _aislar()
    res = H.probe("t/fail", [sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"],
                  agent="claude", avisar=False)
    assert res["hecho"]["status"] == "fail" and res["hecho"]["exit_code"] == 3, res
    assert "boom" in res["hecho"]["output"], res["hecho"]["output"]
    _ok("probe de comando que falla -> status fail + evidencia (exit + salida) capturada")


def test_conflicto_entorno_ambas_ciertas():
    _aislar()
    _set_env(py="3.14.0", venv="")                         # entorno A (sistema, sin deps)
    H.afirmar("tu-proyecto-agente/import:agent.py", "fail", "ImportError pyautogui", agent="codex", avisar=False)
    _set_env(py="3.12.0", venv="C:/tu-proyecto-agente/.venv")          # entorno B (venv con deps)
    res = H.afirmar("tu-proyecto-agente/import:agent.py", "ok", "import agent OK", agent="claude", avisar=False)
    c = res["conflicto"]
    assert c is not None and c["tipo"] == "entorno", c
    assert "AMBAS" in c["explicacion"].upper() or "entorno" in c["explicacion"].lower()
    _ok("conflicto entre ENTORNOS distintos -> etiqueta 'entorno' (no es absoluto; ambas pueden ser ciertas)")


def test_contradiccion_mismo_entorno():
    _aislar()
    _set_env(py="3.12.0", venv="C:/v")                     # MISMO entorno en ambas afirmaciones
    H.afirmar("tu-proyecto-agente/test:x", "ok", "pasa", agent="codex", avisar=False)
    res = H.afirmar("tu-proyecto-agente/test:x", "fail", "no pasa", agent="claude", avisar=False)
    c = res["conflicto"]
    assert c is not None and c["tipo"] == "contradiccion", c
    _ok("conflicto en el MISMO entorno -> 'contradiccion' real (hay que reproducir y resolver)")


def test_no_conflicto_mismo_status():
    _aislar()
    _set_env(py="3.12.0")
    H.afirmar("t/s", "ok", "a", agent="codex", avisar=False)
    res = H.afirmar("t/s", "ok", "b", agent="claude", avisar=False)
    assert res["conflicto"] is None, res
    _ok("dos hechos con el MISMO status -> no hay discrepancia")


def test_resolver_silencia_conflicto():
    _aislar()
    _set_env(py="3.12.0")
    H.afirmar("t/c", "ok", "a", agent="codex", avisar=False)
    _set_env(py="3.14.0")
    H.afirmar("t/c", "fail", "b", agent="claude", avisar=False)
    assert any(c["subject"] == "t/c" for c in H.conflictos()), "deberia haber conflicto antes de resolver"
    H.resolver("t/c", "alineado: usar el venv con deps", agent="claude")
    assert not any(c["subject"] == "t/c" for c in H.conflictos()), "resolver debe silenciar la discrepancia"
    _ok("resolver(subject) silencia la discrepancia (deja de alertar, con nota de provenance)")


def test_verificar_recorre_comando_del_probe():
    _aislar()
    _set_env(py="3.12.0")
    H.probe("t/v", [sys.executable, "-c", "pass"], agent="codex", avisar=False)
    # otra sesion/agente RE-VERIFICA: re-corre el MISMO comando en su entorno en vez de confiar
    res = H.verificar("t/v", agent="claude")
    assert res is not None and res["hecho"]["status"] == "ok", res
    assert res["hecho"]["claim"].startswith("re-verificacion"), res["hecho"]["claim"]
    _ok("verificar() re-corre el comando del probe EN TU entorno (confirmar/refutar, no confiar)")


def test_conflictos_lista_y_tipos():
    _aislar()
    _set_env(py="3.12.0", venv="A")
    H.afirmar("s1", "ok", "x", agent="codex", avisar=False)
    _set_env(py="3.12.0", venv="A")
    H.afirmar("s1", "fail", "y", agent="claude", avisar=False)   # mismo entorno -> contradiccion
    cs = H.conflictos()
    assert len(cs) == 1 and cs[0]["tipo"] == "contradiccion", cs
    _ok("conflictos() agrega las discrepancias abiertas con su tipo")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"== test_cerebro_hechos ({len(fns)} casos) ==")
    for fn in fns:
        fn()
    print("TODOS OK")
