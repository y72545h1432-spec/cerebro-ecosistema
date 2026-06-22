"""Tests del VRAM gate globalizado (cerebro_hardware_gate). Módulo PURO: el lector de nvidia-smi se
inyecta, nunca toca la GPU real. Correr: py -3 test_cerebro_hardware_gate.py"""
import sys
import traceback

import cerebro_hardware_gate as hw

SMI_UNA = "NVIDIA GeForce <GPU> Laptop GPU, 5800, 6144\n"
SMI_DOS = ("NVIDIA GeForce <GPU> Laptop GPU, 1200, 6144\n"
           "NVIDIA RTX A6000, 40000, 49140\n")


def _ok(name):
    print(f"  ok  {name}")


def test_parse_una():
    g = hw.parse_nvidia_smi(SMI_UNA)
    assert len(g) == 1 and "4050" in g[0].name and g[0].free_mb == 5800 and g[0].total_mb == 6144
    _ok("parse_nvidia_smi: una GPU")


def test_parse_varias():
    g = hw.parse_nvidia_smi(SMI_DOS)
    assert len(g) == 2 and g[1].free_mb == 40000
    _ok("parse_nvidia_smi: varias GPUs")


def test_parse_tolerante():
    g = hw.parse_nvidia_smi("  NVIDIA X ,  500 , 6144  \n\n")
    assert len(g) == 1 and g[0].free_mb == 500 and g[0].name == "NVIDIA X"
    _ok("parse_nvidia_smi: tolera espacios y lineas vacias")


def test_parse_malformada():
    g = hw.parse_nvidia_smi("NVIDIA X, 500, 6144\nbasura sin comas\nNVIDIA Y, 600, 6144\n")
    assert len(g) == 2
    _ok("parse_nvidia_smi: ignora lineas malformadas")


def test_gateresult():
    r = hw.GateResult(ok=True, reason="suficiente")
    assert r.ok is True and r.reason == "suficiente"
    _ok("GateResult: campos ok/reason")


def test_check_ok():
    assert hw.check_prerequisites(min_free_mb=5500, smi_runner=lambda: SMI_UNA).ok is True
    _ok("check_prerequisites: ok con VRAM suficiente")


def test_check_insuficiente():
    r = hw.check_prerequisites(min_free_mb=5500, smi_runner=lambda: "NVIDIA X, 1200, 6144\n")
    assert r.ok is False and "1200" in r.reason and "5500" in r.reason
    _ok("check_prerequisites: falla con VRAM insuficiente (razon clara)")


def test_check_mejor_gpu():
    r = hw.check_prerequisites(min_free_mb=5500, smi_runner=lambda: SMI_DOS)
    assert r.ok is True and "40000" in r.reason
    _ok("check_prerequisites: elige la GPU con mas VRAM libre")


def test_check_smi_falla():
    def boom():
        raise FileNotFoundError("nvidia-smi no encontrado")
    r = hw.check_prerequisites(min_free_mb=5500, smi_runner=boom)
    assert r.ok is False and "nvidia-smi" in r.reason.lower()
    _ok("check_prerequisites: smi que lanza -> no-ok limpio")


def test_check_sin_gpu():
    r = hw.check_prerequisites(min_free_mb=5500, smi_runner=lambda: "\n  \n")
    assert r.ok is False and "gpu" in r.reason.lower()
    _ok("check_prerequisites: sin GPU detectada -> no-ok")


def test_umbral_configurable():
    smi = lambda: "NVIDIA X, 3000, 6144\n"
    assert hw.check_prerequisites(min_free_mb=2000, smi_runner=smi).ok is True
    assert hw.check_prerequisites(min_free_mb=4000, smi_runner=smi).ok is False
    _ok("check_prerequisites: umbral configurable")


def test_default_umbral():
    assert 5000 <= hw.DEFAULT_MIN_FREE_MB <= 6000
    assert hw.check_prerequisites(smi_runner=lambda: SMI_UNA).ok is True
    _ok("check_prerequisites: usa DEFAULT_MIN_FREE_MB (~5.5GB)")


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    print(f"== test_cerebro_hardware_gate ({len(fns)} casos) ==")
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
