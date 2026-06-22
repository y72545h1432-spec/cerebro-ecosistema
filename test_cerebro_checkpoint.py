"""Tests de cerebro_checkpoint.py (anti-bugs / muerte subita).

Redirige REMEMBER a un tmp aislado para no tocar el handoff real.
Cubre: ciclo en-curso -> recovery, cerrar-limpio -> no-recovery, parseo de campos,
escritura atomica (no quedan .tmp), degradacion sin checkpoint previo,
auto-checkpoint desde transcript, y recovery por-sesion (multi-sesion).
"""
import importlib
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cerebro_checkpoint as cp

_HOME = str(pathlib.Path.home())   # base portable para inferencia de proyecto (= home del que corre el test)


def _escribir_transcript(path: pathlib.Path, eventos):
    """Escribe un .jsonl estilo Claude Code. `eventos` = [(role, text_o_lista), ...]."""
    lineas = []
    for role, contenido in eventos:
        if isinstance(contenido, str):
            msg = {"role": role, "content": contenido}
        else:
            msg = {"role": role, "content": contenido}
        lineas.append(json.dumps({"type": role, "message": msg}))
    path.write_text("\n".join(lineas) + "\n", encoding="utf-8")


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        importlib.reload(cp)
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ckpt-test-"))
        cp.REMEMBER = self.tmp / "remember.md"

    def test_sin_checkpoint_no_recovery(self):
        rec = cp.recuperar()
        self.assertFalse(rec["existe"])
        self.assertFalse(rec["recovery"])

    def test_checkpoint_queda_en_curso_y_dispara_recovery(self):
        cp.checkpoint("hice X", "seguir con Y", tarea="T999", proyecto="tu-proyecto-agente",
                      archivos=["a.py", "b.py"])
        rec = cp.recuperar()
        self.assertTrue(rec["existe"])
        self.assertTrue(rec["recovery"])  # en-curso = muerte sucia si no se cierra
        self.assertEqual(rec["estado"], cp.EN_CURSO)
        self.assertEqual(rec["proyecto"], "tu-proyecto-agente")
        self.assertEqual(rec["tarea"], "T999")
        self.assertIn("hice X", rec["resumen"])
        self.assertIn("seguir con Y", rec["proximo_paso"])
        self.assertEqual(rec["archivos"], ["a.py", "b.py"])

    def test_cerrar_limpio_apaga_recovery_y_conserva_contexto(self):
        cp.checkpoint("trabajo en curso", "paso siguiente", tarea="T1", proyecto="hub",
                      archivos=["x.py"])
        self.assertTrue(cp.cerrar_limpio())
        rec = cp.recuperar()
        self.assertFalse(rec["recovery"])
        self.assertEqual(rec["estado"], cp.CERRADO)
        # el cierre limpio conserva el contexto del ultimo checkpoint
        self.assertEqual(rec["tarea"], "T1")
        self.assertEqual(rec["proyecto"], "hub")
        self.assertEqual(rec["archivos"], ["x.py"])

    def test_cerrar_limpio_sin_previo_no_lanza(self):
        # sin checkpoint previo, cerrar-limpio no debe lanzar y deja estado cerrado
        self.assertTrue(cp.cerrar_limpio("cierre directo"))
        self.assertEqual(cp.recuperar()["estado"], cp.CERRADO)

    def test_escritura_atomica_no_deja_tmp(self):
        cp.checkpoint("r", "n", proyecto="hub")
        sobrantes = list(self.tmp.glob(".remember-*.tmp"))
        self.assertEqual(sobrantes, [], "no debe quedar ningun temporal tras el replace")

    def test_ultimo_checkpoint_gana(self):
        cp.checkpoint("primero", "p1", proyecto="a")
        cp.checkpoint("segundo", "p2", proyecto="b")
        rec = cp.recuperar()
        self.assertEqual(rec["proyecto"], "b")
        self.assertIn("segundo", rec["resumen"])


class AutoCheckpointTest(unittest.TestCase):
    """El auto-checkpoint NO depende de disciplina: lee el transcript del hook."""

    def setUp(self):
        importlib.reload(cp)
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ckpt-auto-"))
        cp.REMEMBER = self.tmp / "remember.md"
        self.tr = self.tmp / "transcript.jsonl"
        # mapa de inferencia FIJO para el test (no depende de proyectos.local.toml del que corra)
        cp._PROYECTOS = {(_HOME + r"\tu-proyecto-agente").replace("/", "\\").lower().rstrip("\\"): "tu-proyecto-agente"}

    def test_auto_extrae_ultimo_prompt_y_asistente(self):
        _escribir_transcript(self.tr, [
            ("user", "Haz el bootstrap N85 paso-2"),
            ("assistant", [{"type": "text", "text": "Genero requirements.lock (red, no VRAM)."}]),
            ("user", [{"type": "tool_result", "content": "ok"}]),  # se ignora (no es prompt humano)
            ("assistant", [{"type": "text", "text": "Ahora download_models.py; leo model_manifest.py"}]),
        ])
        payload = {"session_id": "sess-AAA", "transcript_path": str(self.tr),
                   "cwd": _HOME + r"\tu-proyecto-agente", "prompt": "(continua)"}
        cp.auto_desde_payload(payload)
        # queda en-curso, por-sesion, con el estado REAL capturado del transcript
        dirty = cp.escanear(current_session=None)
        self.assertEqual(len(dirty), 1)
        d = dirty[0]
        self.assertEqual(d["estado"], cp.EN_CURSO)
        self.assertEqual(d["sesion"], "sess-AAA")
        self.assertEqual(d["proyecto"], "tu-proyecto-agente")  # inferido del cwd
        self.assertIn("download_models.py", d["resumen"] + d["proximo_paso"])

    def test_auto_deriva_sesion_del_transcript_si_falta_session_id(self):
        tr = self.tmp / "sess-DERIVED.jsonl"  # nombre = <session_id>.jsonl (estilo Claude Code)
        _escribir_transcript(tr, [("assistant", [{"type": "text", "text": "trabajando"}])])
        cp.auto_desde_payload({"transcript_path": str(tr), "cwd": r"C:\tu-tienda"})  # sin session_id
        dirty = cp.escanear(current_session=None)
        self.assertEqual([d["sesion"] for d in dirty], ["sess-DERIVED"])

    def test_auto_nunca_lanza_con_payload_malo(self):
        # transcript inexistente / payload incompleto -> degrada, no lanza
        cp.auto_desde_payload({"session_id": "x", "transcript_path": str(self.tmp / "no.jsonl")})
        cp.auto_desde_payload({})  # sin nada


class RecoveryPorSesionTest(unittest.TestCase):
    """Multi-sesion: un cierre limpio viejo NO debe enmascarar una muerte sucia nueva."""

    def setUp(self):
        importlib.reload(cp)
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="ckpt-multi-"))
        cp.REMEMBER = self.tmp / "remember.md"
        self.tr = self.tmp / "t.jsonl"
        _escribir_transcript(self.tr, [
            ("user", "trabajo importante"),
            ("assistant", [{"type": "text", "text": "haciendo el trabajo importante"}]),
        ])

    def test_cierre_viejo_no_enmascara_muerte_sucia_nueva(self):
        # Sesion A: trabajo y cierre limpio
        cp.auto_desde_payload({"session_id": "A", "transcript_path": str(self.tr),
                               "cwd": _HOME + r"\tu-proyecto-agente"})
        cp.cerrar_limpio(sesion="A")
        # Sesion B: trabaja y MUERE sucia (nunca cierra)
        cp.auto_desde_payload({"session_id": "B", "transcript_path": str(self.tr),
                               "cwd": r"C:\tu-tienda"})
        # Al abrir una sesion nueva C, el escaneo ve la muerte sucia de B (no la de A, cerrada)
        dirty = cp.escanear(current_session="C")
        sesiones = {d["sesion"] for d in dirty}
        self.assertIn("B", sesiones)
        self.assertNotIn("A", sesiones)  # A cerro limpio -> no es muerte sucia

    def test_sesion_actual_se_excluye(self):
        cp.auto_desde_payload({"session_id": "B", "transcript_path": str(self.tr),
                               "cwd": r"C:\tu-tienda"})
        # si la sesion actual ES B (reanudacion normal, no crash), no se reporta como muerte
        self.assertEqual(cp.escanear(current_session="B"), [])

    def test_prune_borra_cerrados_viejos_pero_no_en_curso(self):
        import os, time
        cp.auto_desde_payload({"session_id": "VIEJA", "transcript_path": str(self.tr), "cwd": ""})
        cp.cerrar_limpio(sesion="VIEJA")          # cerrada
        cp.auto_desde_payload({"session_id": "VIVA", "transcript_path": str(self.tr), "cwd": ""})  # en-curso
        # envejecer ambos archivos 10 dias
        viejo = time.time() - 10 * 86400
        for f in cp._ckpt_dir().glob("*.md"):
            os.utime(f, (viejo, viejo))
        cp._prune_viejos(dias=7)
        nombres = {f.stem for f in cp._ckpt_dir().glob("*.md")}
        self.assertNotIn("VIEJA", nombres)        # cerrada + vieja -> borrada
        self.assertIn("VIVA", nombres)            # en-curso -> jamas se borra

    def test_cerrar_limpio_sesion_apaga_su_recovery(self):
        cp.auto_desde_payload({"session_id": "B", "transcript_path": str(self.tr),
                               "cwd": r"C:\tu-tienda"})
        self.assertTrue(cp.escanear(current_session="C"))  # antes de cerrar: hay muerte sucia
        cp.cerrar_limpio(sesion="B")
        self.assertEqual(cp.escanear(current_session="C"), [])  # tras cerrar: ya no


if __name__ == "__main__":
    unittest.main(verbosity=2)
