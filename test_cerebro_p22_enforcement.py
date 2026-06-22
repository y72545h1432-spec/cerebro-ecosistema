"""P2.2/P2.3 (causa raíz #3 enforcement-por-código + #6 supuestos de entorno) — un caso por regla.

Aísla el estado compartido apuntando LOCALAPPDATA a un tmpdir ANTES de importar los módulos
(ambos fijan STATE_DIR = %LOCALAPPDATA%/cerebro en import). Así NO toca multisesion.json real.

  P2.2-A · lock-GPU   : reclamar() de hardware global adjunta evidencia nvidia-smi + evento.
  P2.2-B · closed-loop: el blocker requires_ack de un conflicto lleva expires_at (no inmortal).
  P2.3-C · shell-env  : el shell efectivo entra en la huella → divergencia entre shells se
                        etiqueta ENTORNO (ambas ciertas), no CONTRADICCIÓN espuria (mono-shell).

Run:  py .cerebro\test_cerebro_p22_enforcement.py
"""
import os, sys, json, tempfile, pathlib
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8")           # consolas cp1252 (Windows)
except Exception:
    pass

_TMP = tempfile.mkdtemp(prefix="cerebro_p22_")
os.environ["LOCALAPPDATA"] = _TMP                      # ANTES de importar
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import cerebro_multisesion as cm
import cerebro_hechos as ch

EVENT_LOG = pathlib.Path(_TMP) / "cerebro" / "eventos.jsonl"


def _eventos():
    if not EVENT_LOG.exists():
        return []
    return [json.loads(l) for l in EVENT_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_gpu_estado_helper():
    """gpu_estado() devuelve dict con las 4 claves si hay nvidia-smi, o None sin romper."""
    est = cm.gpu_estado()
    if est is None:
        print("  [skip-detalle] sin nvidia-smi en este host: gpu_estado()->None (advisory OK)")
        return None
    assert set(est) == {"vram_used_mb", "vram_total_mb", "gpu_temp_c", "gpu_util_pct"}, est
    assert all(isinstance(v, int) for v in est.values()), est
    print(f"  gpu_estado() = {est}")
    return est


def test_reclamar_global_adjunta_evidencia(hay_gpu):
    """reclamar('gpu', global) → el lock lleva 'hw' + se loguea evento gpu_probe (si hay GPU)."""
    ms = cm.Multisesion("test p22 gpu", project="test", agent="claude")
    ok = ms.reclamar("gpu", scope="global")
    assert ok, "no se concedió el lock gpu global"
    d = cm._solo_lectura() if hasattr(cm, "_solo_lectura") else json.loads(cm.ARCHIVO.read_text("utf-8"))
    lock = d["locks"].get("*:gpu")
    assert lock is not None, "lock *:gpu no quedó registrado"
    if hay_gpu:
        assert "hw" in lock, f"el lock global no llevó evidencia hw: {lock}"
        assert lock["hw"]["vram_total_mb"] > 0, lock["hw"]
        evs = [e for e in _eventos() if e.get("type") == "gpu_probe"]
        assert evs, "no se registró evento gpu_probe"
        print(f"  lock *:gpu lleva hw={lock['hw']} + evento gpu_probe OK")
    ms.liberar("gpu", scope="global")
    ms.despedir()


def test_lock_proyecto_no_sondea():
    """Un lock por-proyecto (no hardware) NO debe sondear ni llevar 'hw' (sin coste nvidia-smi)."""
    ms = cm.Multisesion("test p22 proj", project="test", agent="claude")
    assert ms.reclamar("curacion")
    d = json.loads(cm.ARCHIVO.read_text("utf-8"))
    lock = d["locks"].get("test:curacion")
    assert lock is not None and "hw" not in lock, f"lock de proyecto no debe sondear GPU: {lock}"
    print("  lock de proyecto 'curacion' sin sondeo GPU OK")
    ms.liberar("curacion")
    ms.despedir()


def test_blocker_lleva_expires_at():
    """Un conflicto de hechos publica un blocker requires_ack CON expires_at (no inmortal)."""
    subj = "p22-conflicto-demo"
    # dos afirmaciones MISMO entorno, status divergente → contradicción → blocker al buzón "*"
    ch.afirmar(subj, "ok", "demo ok", agent="claude", project="test")
    ch.afirmar(subj, "fail", "demo fail", agent="codex", project="test")
    ms = cm.Multisesion("lector buzon", project="test", agent="lector")
    blockers = [m for m in ms.leer_buzon(type="blocker") if subj in m.get("resource", "")]
    assert blockers, "no se publicó blocker para el conflicto"
    b = blockers[0]
    assert b.get("expires_at"), f"el blocker no lleva expires_at (sería inmortal): {b}"
    venc = datetime.fromisoformat(b["expires_at"])
    assert venc > datetime.now(), "expires_at ya vencido al crearse"
    print(f"  blocker lleva expires_at={b['expires_at']} OK")
    ms.despedir()


def test_blocker_vencido_cae_a_dead_letter():
    """Un blocker requires_ack vencido y sin ack es rescatado por dead_letter() (closed-loop)."""
    ms = cm.Multisesion("emisor", project="test", agent="claude")
    pasado = (datetime.now() - timedelta(minutes=1)).isoformat(timespec="seconds")
    mid = ms.mensaje_tipo("*", type="blocker", priority="high", requires_ack=True,
                          summary="blocker vencido demo", expires_at=pasado, resource="p22-dead")
    dl = ms.dead_letter()
    assert any(m.get("id") == mid for m in dl), "el blocker vencido sin ack no apareció en dead_letter()"
    print("  blocker vencido sin ack → aparece en dead_letter() OK")
    ms.despedir()


def _hecho_env(subj, status, agent, shell):
    """Hecho con env CRAFTeado: mismo host/python/venv, distinto shell (para probar la dimensión)."""
    env = {"host": "H1", "python": "py", "py_version": "3.14", "venv": "", "shell": shell}
    return {"id": f"h_{agent}_{status}", "ts": ch._ahora(), "subject": subj, "claim": "",
            "status": status, "kind": "probe", "command": "cmd", "exit_code": 0, "output": "",
            "env": env, "agent": agent, "runtime": agent, "project": "test", "sesion": ""}


def test_shell_en_env_key():
    """_env_key incluye el shell → dos entornos iguales salvo shell son DISTINTOS (P2.3)."""
    a = {"host": "H", "python": "py", "py_version": "3.14", "venv": "", "shell": "cmd.exe"}
    b = {**a, "shell": "/bin/bash"}
    assert ch._env_key(a) != ch._env_key(b), "el shell no entra en _env_key"
    assert ch._env_key(a) == ch._env_key({**a}), "_env_key no es estable"
    assert "shell" in ch.env_fingerprint(), "env_fingerprint no captura el shell"
    print(f"  _env_key distingue shell; fingerprint.shell={ch.env_fingerprint()['shell']!r} OK")


def test_divergencia_entre_shells_es_entorno_no_contradiccion():
    """Mismo host/python, status divergente PERO distinto shell → tipo 'entorno' (no 'contradiccion')."""
    subj = "p23-shell-demo"
    h_ok = _hecho_env(subj, "ok", "claude", "cmd.exe")
    h_fail = _hecho_env(subj, "fail", "codex", "/bin/bash")
    ch._append(ch.HECHOS, h_ok)
    ch._append(ch.HECHOS, h_fail)
    c = ch._detectar_conflicto(h_fail)
    assert c is not None and c["tipo"] == "entorno", \
        f"divergencia entre shells debió ser 'entorno', fue: {c and c['tipo']}"
    print("  divergencia ok/fail entre shells distintos → 'entorno' (ambas ciertas) OK")
    # Control: MISMO shell con status divergente SÍ debe ser contradicción real.
    subj2 = "p23-mismo-shell-demo"
    ch._append(ch.HECHOS, _hecho_env(subj2, "ok", "claude", "cmd.exe"))
    h2 = _hecho_env(subj2, "fail", "codex", "cmd.exe")
    ch._append(ch.HECHOS, h2)
    c2 = ch._detectar_conflicto(h2)
    assert c2 is not None and c2["tipo"] == "contradiccion", \
        f"mismo shell divergente debió ser 'contradiccion', fue: {c2 and c2['tipo']}"
    print("  control: mismo shell, status divergente → 'contradiccion' real OK")


if __name__ == "__main__":
    print("== P2.2-A · lock-GPU (enforcement por código) ==")
    est = test_gpu_estado_helper()
    test_reclamar_global_adjunta_evidencia(hay_gpu=est is not None)
    test_lock_proyecto_no_sondea()
    print("== P2.2-B · closed-loop ack (expires_at + dead-letter) ==")
    test_blocker_lleva_expires_at()
    test_blocker_vencido_cae_a_dead_letter()
    print("== P2.3-C · shell en la huella de entorno (mono-shell) ==")
    test_shell_en_env_key()
    test_divergencia_entre_shells_es_entorno_no_contradiccion()
    print(f"\nTODO OK. (estado aislado en {_TMP})")
