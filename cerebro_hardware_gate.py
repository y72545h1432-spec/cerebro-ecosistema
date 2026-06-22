"""cerebro_hardware_gate.py — Gate de prerequisitos de hardware (VRAM) antes de actos caros (módulo PURO).

GLOBALIZADO (2026-06-22, F6): nació en `tu-proyecto-agente/bootstrap/hardware.py` pero es infra del ECOSISTEMA, no
de un proyecto: la <GPU> (<VRAM>) es un recurso GLOBAL que comparten tu-proyecto-agente (entrenar LoRA) y tu-tienda
(daemon Qwen). El go/no-go interoceptivo de VRAM sirve la regla #10 del hub (salud del computador):
abortar limpio con mensaje claro > un OOM que tumba la sesión del usuario. tu-proyecto-agente conserva un
`bootstrap/hardware.py` que es un SHIM fino reexportando de este módulo.

Mecanismo (neuro, regla #4 de tu-proyecto-agente): gating homeostático / interocepción. El hipotálamo + ínsula
monitorean reservas internas y FRENAN la iniciación de acciones costosas cuando las reservas son bajas;
la VRAM es la 'reserva metabólica' del agente.

Módulo PURO: el lector de nvidia-smi se INYECTA (`smi_runner` -> str). Default: subprocess a nvidia-smi.
`check_prerequisites` NUNCA lanza: si no puede leer la GPU degrada a `GateResult(ok=False, reason=...)`,
porque un gate que crashea sería peor que el OOM que intenta evitar. Umbral configurable (no fijo).
"""
import subprocess
from dataclasses import dataclass

DEFAULT_MIN_FREE_MB = 5500  # ~5.5GB libres (<GPU> <VRAM>; regla del proyecto)

_QUERY = ["nvidia-smi", "--query-gpu=name,memory.free,memory.total",
          "--format=csv,noheader,nounits"]


@dataclass(frozen=True)
class GPUInfo:
    """Una GPU vista por nvidia-smi: nombre + VRAM libre/total en MB."""
    name: str
    free_mb: int
    total_mb: int


@dataclass(frozen=True)
class GateResult:
    """Veredicto del gate: ok (se puede proceder?) + reason (por que)."""
    ok: bool
    reason: str


def parse_nvidia_smi(text):
    """Parsea la salida CSV (noheader, nounits) de nvidia-smi. Lineas malformadas se ignoran."""
    gpus = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            continue
        name, free, total = parts
        try:
            gpus.append(GPUInfo(name=name, free_mb=int(free), total_mb=int(total)))
        except ValueError:
            continue  # campos no numericos: descartar la linea
    return gpus


def _default_smi_runner():
    """Lee nvidia-smi via subprocess (la I/O real; aislada para poder inyectar un fake en tests)."""
    return subprocess.run(_QUERY, capture_output=True, text=True, check=True).stdout


def check_prerequisites(min_free_mb=DEFAULT_MIN_FREE_MB, *, smi_runner=None):
    """Gate: True si alguna GPU tiene >= min_free_mb libres. Nunca lanza (degrada a no-ok con razon)."""
    runner = smi_runner or _default_smi_runner
    try:
        text = runner()
    except Exception as e:
        return GateResult(False, f"no se pudo leer nvidia-smi ({type(e).__name__}: {e})")

    gpus = parse_nvidia_smi(text)
    if not gpus:
        return GateResult(False, "ninguna GPU detectada por nvidia-smi")

    best = max(gpus, key=lambda g: g.free_mb)
    if best.free_mb >= min_free_mb:
        return GateResult(True, f"{best.name}: {best.free_mb}MB libres >= {min_free_mb}MB requeridos")
    return GateResult(False, f"VRAM insuficiente: {best.name} tiene {best.free_mb}MB libres < {min_free_mb}MB requeridos")


if __name__ == "__main__":
    r = check_prerequisites()
    print(f"VRAM gate -> ok={r.ok}  {r.reason}")
