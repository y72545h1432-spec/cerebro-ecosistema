"""Tests de cerebro_paths (rutas robustas + conscientes de OneDrive). No simula la nube real (requiere
atributos de archivo OneDrive), pero cubre el camino normal + el resolutor robusto con tempdirs.
Correr: py -3 test_cerebro_paths.py"""
import os
import sys
import tempfile
import traceback

import cerebro_paths as cp


def _ok(name):
    print(f"  ok  {name}")


def test_is_dehydrated_archivo_normal_es_false():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "x.txt")
        open(f, "w").write("hola")
        assert cp.is_dehydrated(f) is False
        assert cp.is_dehydrated(os.path.join(d, "no-existe")) is False
    _ok("is_dehydrated: archivo normal / inexistente -> False")


def test_materialized():
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "x.txt")
        open(f, "w").write("hola")
        assert cp.materialized(f) is True
        assert cp.materialized(os.path.join(d, "no-existe")) is False
    _ok("materialized: archivo legible True / inexistente False")


def test_state_dir_es_local_y_existe():
    sd = cp.state_dir("cerebro_test_paths_selftest")
    assert sd.exists() and sd.is_dir()
    la = os.environ.get("LOCALAPPDATA")
    if la:
        assert str(sd).lower().startswith(la.lower())  # SIEMPRE local, nunca OneDrive
    try:
        sd.rmdir()
    except OSError:
        pass
    _ok("state_dir: bajo LOCALAPPDATA y creado")


def _crear_raiz(base, marker, sentinel):
    root = os.path.join(base, "PROY")
    os.makedirs(os.path.join(root, marker), exist_ok=True)
    sp = os.path.join(root, sentinel)
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    open(sp, "w", encoding="utf-8").write("centinela")
    return root


def test_resolve_root_por_known_y_pointer():
    marker, sentinel = "MARK", os.path.join("MARK", "centinela.md")
    with tempfile.TemporaryDirectory() as d:
        root = _crear_raiz(d, marker, sentinel)
        # encuentra por 'known'
        got = cp.resolve_root(marker, sentinel, known=[root], update_pointer=False)
        assert got is not None and str(got).lower() == os.path.realpath(root).lower()
        # y reescribe el puntero cuando se le da
        pointer = os.path.join(d, "ptr.txt")
        cp.resolve_root(marker, sentinel, known=[root], pointer=pointer)
        assert open(pointer, encoding="utf-8").read().strip().lower() == os.path.realpath(root).lower()
        # ahora resuelve SOLO por el puntero (sin known)
        got2 = cp.resolve_root(marker, sentinel, pointer=pointer, update_pointer=False)
        assert got2 is not None
    _ok("resolve_root: por known + escribe/lee puntero")


def test_resolve_root_por_env():
    marker, sentinel = "MARK", os.path.join("MARK", "centinela.md")
    with tempfile.TemporaryDirectory() as d:
        root = _crear_raiz(d, marker, sentinel)
        os.environ["CEREBRO_TEST_ROOT"] = root
        try:
            got = cp.resolve_root(marker, sentinel, env_var="CEREBRO_TEST_ROOT", update_pointer=False)
            assert got is not None
        finally:
            del os.environ["CEREBRO_TEST_ROOT"]
    _ok("resolve_root: por variable de entorno")


def test_resolve_root_no_encontrada_devuelve_none():
    with tempfile.TemporaryDirectory() as d:
        got = cp.resolve_root("NOPE", os.path.join("NOPE", "x.md"), known=[d], update_pointer=False)
        assert got is None
    _ok("resolve_root: ninguna candidata valida -> None")


def test_resolve_root_sentinela_faltante_no_valida():
    marker = "MARK"
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, "PROY")
        os.makedirs(os.path.join(root, marker), exist_ok=True)  # marker sí, centinela NO
        got = cp.resolve_root(marker, os.path.join(marker, "falta.md"), known=[root], update_pointer=False)
        assert got is None
    _ok("resolve_root: marker sin centinela materializado -> None")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_paths ({len(fns)} casos) ==")
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
