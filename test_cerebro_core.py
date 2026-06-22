"""Tests de cerebro_core (base comun). Estado en dirs temporales aislados.
Correr: py -3 test_cerebro_core.py"""
import sys
import os
import tempfile
import traceback
from pathlib import Path
from datetime import datetime, timedelta

import cerebro_core as core


def _ok(name):
    print(f"  ok  {name}")


def _tmp(suffix=".json"):
    return Path(tempfile.mkdtemp(prefix="core_")) / f"x{suffix}"


# ---- tiempo ----
def test_now_iso_segundos():
    s = core.now()
    # parseable y sin microsegundos
    datetime.fromisoformat(s)
    assert "." not in s, s
    _ok("now: ISO 8601 con segundos, sin microsegundos")


def test_is_expired():
    viejo = (datetime.now() - timedelta(minutes=40)).isoformat(timespec="seconds")
    nuevo = (datetime.now() - timedelta(minutes=5)).isoformat(timespec="seconds")
    assert core.is_expired(viejo, 30) is True
    assert core.is_expired(nuevo, 30) is False
    assert core.is_expired("no-es-fecha", 30) is True   # invalido -> vencido
    _ok("is_expired: vencido/vigente segun umbral; invalido -> vencido")


def test_age_minutes():
    hace10 = (datetime.now() - timedelta(minutes=10)).isoformat(timespec="seconds")
    edad = core.age_minutes(hace10)
    assert 9.0 <= edad <= 11.0, edad
    assert core.age_minutes("basura") is None
    _ok("age_minutes: edad correcta; invalido -> None")


# ---- normalizacion ----
def test_unfold():
    assert core.unfold("Diseñar ARQUITECTURA") == "disenar arquitectura"
    assert core.unfold(None) == ""
    _ok("unfold: minusculas sin acentos; None -> ''")


def test_to_list():
    assert core.to_list("a, b ,c") == ["a", "b", "c"]
    assert core.to_list(["x", "y,z"]) == ["x", "y", "z"]
    assert core.to_list(None) == []
    _ok("to_list: coacciona str/lista, separa comas, descarta vacios")


# ---- sistema ----
def test_pid_alive():
    import os
    assert core.pid_alive(os.getpid()) is True       # yo estoy vivo
    assert core.pid_alive(None) is False
    assert core.pid_alive(0) is False
    _ok("pid_alive: True para mi pid; False para None/0")


def test_env_fingerprint():
    fp = core.env_fingerprint()
    for k in ("host", "cwd", "python", "py_version", "os", "shell"):
        assert k in fp and fp[k], (k, fp)
    _ok("env_fingerprint: incluye host/cwd/python/py_version/os/shell")


# ---- IO atomica ----
def test_write_read_json_roundtrip():
    p = _tmp()
    core.write_atomic(p, {"a": 1, "ñ": "áé"})
    assert core.read_json_tolerant(p) == {"a": 1, "ñ": "áé"}
    _ok("write_atomic + read_json_tolerant: roundtrip JSON con unicode")


def test_write_atomic_crea_bak_y_recupera():
    p = _tmp()
    core.write_atomic(p, {"v": 1})
    core.write_atomic(p, {"v": 2})                 # mueve el viejo a .bak
    assert p.with_suffix(".bak").exists()
    # corrompo el principal -> el fallback lee el .bak
    p.write_text("{ corrupto", encoding="utf-8")
    assert core.read_json_tolerant(p) == {"v": 1}
    _ok("write_atomic: respaldo .bak; read_json_tolerant cae al .bak si el principal se corrompe")


def test_read_json_tolerant_inexistente():
    p = _tmp()
    assert core.read_json_tolerant(p) is None
    _ok("read_json_tolerant: None si no existe ni hay .bak")


def test_write_atomic_texto():
    p = _tmp(".md")
    core.write_atomic(p, "# hola\nlínea")
    assert p.read_text(encoding="utf-8") == "# hola\nlínea"
    _ok("write_atomic: escribe texto plano cuando data es str")


def test_append_read_jsonl():
    p = _tmp(".jsonl")
    core.append_jsonl(p, {"i": 1})
    core.append_jsonl(p, {"i": 2})
    assert [x["i"] for x in core.read_jsonl(p)] == [1, 2]
    _ok("append_jsonl + read_jsonl: orden preservado")


def test_read_jsonl_tolera_basura():
    p = _tmp(".jsonl")
    p.write_text('{"i":1}\n\nno-json\n{"i":2}\n', encoding="utf-8")
    assert [x["i"] for x in core.read_jsonl(p)] == [1, 2]
    assert core.read_jsonl(_tmp(".jsonl")) == []     # inexistente -> []
    _ok("read_jsonl: salta lineas vacias/mal formadas; inexistente -> []")


def test_append_jsonl_rota_por_tamano():
    p = _tmp(".jsonl")
    core.append_jsonl(p, {"i": 1})
    core.append_jsonl(p, {"i": 2}, max_bytes=1)       # ya supera 1 byte -> rota antes de escribir
    assert p.with_suffix(".jsonl.bak").exists()
    assert [x["i"] for x in core.read_jsonl(p)] == [2]
    _ok("append_jsonl: rota a .jsonl.bak cuando supera max_bytes")


# ---- mutex ----
def test_filemutex_adquiere_y_reutiliza():
    d = Path(tempfile.mkdtemp(prefix="mtx_"))
    with core.FileMutex("t", lockdir=d) as m:
        assert m._locked is True                       # tengo el lock del SO
    with core.FileMutex("t", lockdir=d) as m2:         # liberado al salir -> re-adquirible
        assert m2._locked is True
    _ok("FileMutex: adquiere el lock del SO y lo libera al salir (re-adquirible)")


def _otro_handle_puede_lockear(path: Path) -> bool:
    """Intenta tomar el lock del SO desde OTRO handle (no bloqueante). True si lo consiguio."""
    fh = open(path, "a+", encoding="utf-8"); fh.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                return True
            except OSError:
                return False
        import fcntl
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            return True
        except OSError:
            return False
    finally:
        fh.close()


def test_filemutex_excluye_concurrente():
    d = Path(tempfile.mkdtemp(prefix="mtx_"))
    lf = d / "mutex_t.lock"
    with core.FileMutex("t", lockdir=d):
        assert _otro_handle_puede_lockear(lf) is False   # tomado -> nadie mas entra
    assert _otro_handle_puede_lockear(lf) is True        # liberado -> ya se puede
    _ok("FileMutex: exclusion real del SO (otro handle no entra mientras esta tomado; si tras liberar)")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_core ({len(fns)} casos) ==")
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
