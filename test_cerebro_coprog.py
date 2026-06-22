"""Tests puros de cerebro_coprog (tablero de co-programacion). Sin estado real: dict inyectado.
Correr: py -3 test_cerebro_coprog.py"""
import sys
import traceback

import cerebro_coprog as cop


def _ok(name):
    print(f"  ok  {name}")


def _fake_state():
    return {
        "sesiones": {
            "claude-tu-proyecto-agente-A": {"tarea": "cablear counterfactual", "viva": True},
            "claude-tu-proyecto-agente-B": {"tarea": "investigar", "viva": True},
        },
        "locks": {
            "tu-proyecto-agente:file:cognition.py": {"recurso": "file:cognition.py", "project": "tu-proyecto-agente",
                                         "sesion": "claude-tu-proyecto-agente-A", "agent": "claude",
                                         "runtime": "claude-code", "desde": "2020-01-01T00:00:00",
                                         "motivo": "wiring"},
            "tu-proyecto-agente:cerebro_item20": {"recurso": "cerebro_item20", "project": "tu-proyecto-agente",
                                      "sesion": "claude-tu-proyecto-agente-A", "agent": "claude",
                                      "runtime": "claude-code", "desde": "2020-01-01T00:00:00"},
            "tu-tienda:file:mano.py": {"recurso": "file:mano.py", "project": "tu-tienda",
                                  "sesion": "tu-tienda-X", "agent": "claude", "runtime": "claude-code",
                                  "desde": "2020-01-01T00:00:00", "motivo": ""},
        },
    }


def test_file_key_normaliza():
    assert cop.file_key("cognition.py") == "file:cognition.py"
    assert cop.file_key("./cognition.py") == "file:cognition.py"
    assert cop.file_key(r"C:\Users\x\tu-proyecto-agente\Cognition.py") == "file:cognition.py"
    _ok("file_key normaliza basename/minusculas (abs, rel y mayusculas colisionan)")


def test_board_solo_archivos():
    filas = cop.board(d=_fake_state())
    archivos = {f["archivo"] for f in filas}
    assert archivos == {"cognition.py", "mano.py"}          # excluye el lock no-file (cerebro_item20)
    _ok("board: lista solo locks file:*, excluye locks no-archivo")


def test_board_filtra_proyecto():
    filas = cop.board(project="tu-proyecto-agente", d=_fake_state())
    assert [f["archivo"] for f in filas] == ["cognition.py"]
    f = filas[0]
    assert f["agent"] == "claude" and f["tarea"] == "cablear counterfactual"
    _ok("board: filtra por proyecto y cruza la tarea de la sesion duena")


def test_who_has():
    d = _fake_state()
    h = cop.who_has("cognition.py", project="tu-proyecto-agente", d=d)
    assert h and h["sesion"] == "claude-tu-proyecto-agente-A"
    assert cop.who_has("arbiter.py", project="tu-proyecto-agente", d=d) is None   # libre
    _ok("who_has: detecta archivo tomado y libre")


def test_edad_calculada():
    filas = cop.board(d=_fake_state())
    assert all(f["edad_min"] > 0 for f in filas)              # 'desde' antiguo -> edad positiva
    _ok("edad_min: se calcula desde 'desde' (positiva para locks antiguos)")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_coprog ({len(fns)} casos) ==")
    for fn in fns:
        try:
            fn()
            ok += 1
        except Exception:
            print("FAIL", fn.__name__)
            traceback.print_exc()
    print(f"\n{ok}/{len(fns)} verde")
    sys.exit(0 if ok == len(fns) else 1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _run()
