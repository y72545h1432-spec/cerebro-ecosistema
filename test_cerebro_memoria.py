"""Tests de cerebro_memoria (memoria durable compartida). BASE/INDICE temporales aislados.
Antes no existian (hueco de cobertura detectado en la auditoria 2026-06-21).
Correr: py -3 test_cerebro_memoria.py"""
import sys
import tempfile
import traceback
from pathlib import Path

import cerebro_memoria as mem


def _ok(name):
    print(f"  ok  {name}")


def _fresh():
    d = Path(tempfile.mkdtemp(prefix="mem_"))
    mem.BASE = d
    mem.INDICE = d / "MEMORIA.md"


def test_recordar_y_leer():
    _fresh()
    ruta = mem.recordar("slug-x", "una desc", "cuerpo del hecho", "project", "tu-proyecto-agente", "claude")
    assert Path(ruta).exists()
    d = mem.leer("slug-x")
    assert d and d["name"] == "slug-x" and d["description"] == "una desc"
    assert d["type"] == "project" and d["cuerpo"] == "cuerpo del hecho"
    _ok("recordar + leer: roundtrip de frontmatter (name/desc/type) y cuerpo")


def test_type_invalido_lanza():
    _fresh()
    try:
        mem.recordar("s", "d", "c", "no-existe", "hub", "claude")
        assert False, "deberia lanzar ValueError"
    except ValueError:
        pass
    _ok("recordar: type invalido -> ValueError")


def test_area_invalida_cae_a_hub():
    _fresh()
    mem.recordar("s2", "d", "c", "user", "proyecto-inexistente", "claude")
    assert mem.leer("s2")["project"] == "hub"
    _ok("recordar: project fuera de AREAS -> 'hub' (degradacion segura)")


def test_buscar_subcadena():
    _fresh()
    mem.recordar("a1", "sobre gpus", "entrenamiento lora en gpu", "reference", "tu-proyecto-agente", "claude")
    mem.recordar("a2", "sobre tienda", "dropshipping cozy", "reference", "tu-tienda", "claude")
    ids = [d["name"] for d in mem.buscar("dropshipping", semantico=False)]
    assert "a2" in ids and "a1" not in ids, ids
    _ok("buscar: subcadena recupera el hecho correcto (recall garantizado)")


def test_buscar_filtros():
    _fresh()
    mem.recordar("p1", "d", "c", "project", "tu-proyecto-agente", "claude")
    mem.recordar("n1", "d", "c", "project", "tu-tienda", "claude")
    ids = [d["name"] for d in mem.buscar(type="project", project="tu-proyecto-agente")]
    assert ids == ["p1"], ids
    _ok("buscar: filtros estructurados type/project aislan el hecho")


def test_reindexar_e_indice():
    _fresh()
    mem.recordar("z1", "desc z", "cuerpo", "feedback", "hub", "codex")
    assert mem.reindexar() == 1
    idx = mem.indice()
    assert "z1" in idx and "desc z" in idx
    _ok("reindexar + indice: cuenta hechos y los lista en MEMORIA.md")


def test_olvidar():
    _fresh()
    mem.recordar("borrame", "d", "c", "user", "hub", "claude")
    assert mem.olvidar("borrame") is True
    assert mem.leer("borrame") is None
    assert mem.olvidar("borrame") is False
    _ok("olvidar: borra el hecho; segundo olvidar -> False")


def test_recordar_actualiza_no_duplica():
    _fresh()
    mem.recordar("dup", "v1", "cuerpo1", "user", "hub", "claude")
    mem.recordar("dup", "v2", "cuerpo2", "user", "hub", "claude")
    d = mem.leer("dup")
    assert d["description"] == "v2" and d["cuerpo"] == "cuerpo2"
    # un solo archivo para el slug (no duplicado)
    assert len([p for p in mem._archivos() if p.stem == "dup"]) == 1
    _ok("recordar: re-grabar el mismo slug ACTUALIZA en sitio (no duplica)")


def test_consolidar_detecta_near_dup():
    _fresh()
    mem.recordar("router-tareas-por-modelo", "cola por modelo", "publica tareas a un modelo concreto", "reference", "hub", "claude")
    mem.recordar("reference-tareas-por-modelo", "cola por modelo", "publica tareas a un modelo concreto", "reference", "hub", "claude")
    mem.recordar("algo-distinto", "otra cosa", "dropshipping cozy tu-nicho", "reference", "hub", "claude")
    pares = mem.consolidar(umbral=0.80)
    slugs = {tuple(sorted((a, b))) for _, _, a, b, _, _ in pares}
    assert ("reference-tareas-por-modelo", "router-tareas-por-modelo") in slugs, pares
    assert all("algo-distinto" not in (a, b) for _, _, a, b, _, _ in pares), pares
    _ok("consolidar: detecta el near-duplicado (name-drift) y excluye el hecho distinto")


def test_fusionar_conserva_y_borra():
    _fresh()
    mem.recordar("keep", "desc", "cuerpo A", "reference", "hub", "claude")
    mem.recordar("drop", "desc", "cuerpo B unico", "reference", "hub", "claude")
    assert mem.fusionar("keep", "drop") is True
    k = mem.leer("keep")
    assert k and "cuerpo A" in k["cuerpo"] and "cuerpo B unico" in k["cuerpo"]
    assert mem.leer("drop") is None
    assert mem.fusionar("keep", "noexiste") is False
    _ok("fusionar: anexa el cuerpo del drop al keep, borra el drop; par inexistente -> False")


def test_sugerir_slug():
    _fresh()
    assert mem._sugerir_slug("Feedback usuario 2026: NO poner logo!") == "feedback-usuario-2026-no-poner-logo"
    assert mem._sugerir_slug("") == "nota"
    _ok("_sugerir_slug: normaliza a kebab-case y degrada a 'nota' si vacío")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_memoria ({len(fns)} casos) ==")
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
