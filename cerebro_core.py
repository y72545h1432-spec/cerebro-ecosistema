"""cerebro_core.py — BASE COMUN del ecosistema (stdlib-only, sin deps de otros cerebro_*.py).

POR QUE EXISTE (2026-06-21): la auditoria de consolidacion encontro 4-5 reimplementaciones de la
MISMA logica repartidas por los modulos (escritura atomica de JSON, append-only JSONL, lectura
tolerante con fallback a .bak, helpers de tiempo, normalizacion, huella de entorno, mutex de
proceso). Divergian en manejo de errores/fsync/rollback -> riesgo de bug silencioso. Este modulo es
la FUENTE UNICA de esas utilidades; cada modulo importa de aqui en vez de copiarlas.

Es la CAPA BASE: NO importa ningun otro cerebro_*.py (los demas dependen de el, no al reves). Solo
stdlib. Las firmas conservan EXACTAMENTE la semantica de las versiones canonicas que reemplazan
(p.ej. el respaldo es `path.with_suffix('.bak')`, igual que el _read_tolerante historico).
"""
from __future__ import annotations
import json, os, sys, time, socket, ctypes, tempfile, pathlib, platform, unicodedata
from datetime import datetime, timedelta

# Estado compartido fuera de OneDrive y fuera de cualquier runtime (convencion del ecosistema).
STATE_DIR = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "cerebro"
LOCKDIR = STATE_DIR / "_locks"

MUTEX_TTL = 30    # s: el mutex de proceso caduca por si un proceso muere dentro
MUTEX_SPIN = 12   # s: cuanto reintento tomar el mutex antes de rendirme


# --------------------------------------------------------------------------- tiempo
def now() -> str:
    """ISO 8601 con segundos (sin microsegundos). Reloj de pared local (supuesto mono-host)."""
    return datetime.now().isoformat(timespec="seconds")


def is_expired(iso: str, minutes: int) -> bool:
    """True si pasaron MAS de `minutes` desde `iso`. ISO invalido -> True (ante la duda, vencido)."""
    try:
        return datetime.now() - datetime.fromisoformat(iso) > timedelta(minutes=minutes)
    except Exception:
        return True


def age_minutes(iso: str, ahora: datetime | None = None) -> float | None:
    """Edad en minutos de `iso` (None si invalido). `ahora` inyectable para test."""
    try:
        ref = ahora or datetime.now()
        return (ref - datetime.fromisoformat(iso)).total_seconds() / 60.0
    except Exception:
        return None


# --------------------------------------------------------------------------- normalizacion
def unfold(s: str) -> str:
    """minusculas sin acentos: heuristicas que no deben depender de tildes ('diseno'=='diseño')."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def to_list(v) -> list:
    """Coacciona str/lista a lista de items no vacios (separa por comas, hace strip)."""
    if not v:
        return []
    if isinstance(v, str):
        v = [v]
    out: list = []
    for it in v:
        out += [p.strip() for p in str(it).split(",") if p.strip()]
    return out


# --------------------------------------------------------------------------- sistema
def pid_alive(pid) -> bool:
    """True si el proceso sigue vivo (Windows). Sin pid -> False. Error de API -> True
    (ante la duda no matamos una sesion por un fallo de la API)."""
    if not pid:
        return False
    try:
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(0x1000, False, int(pid))  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            if k32.GetExitCodeProcess(h, ctypes.byref(code)):
                return code.value == 259  # STILL_ACTIVE
            return True
        finally:
            k32.CloseHandle(h)
    except Exception:
        return True


def shell_effective() -> str:
    """El shell con el que subprocess.run(shell=True) ejecutaria un comando-str (cmd.exe en Windows)."""
    if os.name == "nt":
        return os.environ.get("COMSPEC", "cmd.exe")
    return os.environ.get("SHELL", "/bin/sh")


def env_fingerprint() -> dict:
    """Huella del entorno que ejecuta ESTE proceso: lo que casi siempre explica una discrepancia."""
    return {
        "host": socket.gethostname(),
        "cwd": os.getcwd(),
        "python": sys.executable,
        "py_version": platform.python_version(),
        "venv": os.environ.get("VIRTUAL_ENV", ""),
        "os": platform.platform(),
        "shell": shell_effective(),
    }


# --------------------------------------------------------------------------- IO atomica
def write_atomic(path, data) -> None:
    """Escritura atomica: respaldo .bak del ultimo bueno + tmp con fsync + os.replace (atomico en
    NTFS: o ves el viejo entero, o el nuevo entero, nunca medio). `data` dict -> JSON (indent=1);
    str -> texto tal cual. El respaldo es `path.with_suffix('.bak')` (mismo convenio que
    read_json_tolerant, para que el fallback lo encuentre)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            path.replace(path.with_suffix(".bak"))  # respaldo del ultimo bueno
        except OSError:
            pass
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


def read_json_tolerant(path) -> dict | None:
    """Lee JSON; si el principal esta corrupto, prueba `path.with_suffix('.bak')`. None si ambos fallan."""
    path = pathlib.Path(path)
    for p in (path, path.with_suffix(".bak")):
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None


def append_jsonl(path, item: dict, max_bytes: int | None = None,
                 bak_suffix: str = ".jsonl.bak") -> None:
    """Append-only JSONL liviano para watchers/logs. Si `max_bytes` y el archivo lo supera, rota a
    `path.with_suffix(bak_suffix)` antes de escribir. Una linea = un objeto compacto."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if max_bytes:
        try:
            if path.exists() and path.stat().st_size > max_bytes:
                path.replace(path.with_suffix(bak_suffix))
        except OSError:
            pass
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_jsonl(path) -> list:
    """Lee un JSONL completo, tolerante (salta lineas vacias o mal formadas). [] si no existe."""
    path = pathlib.Path(path)
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


# --------------------------------------------------------------------------- mutex de proceso
class FileMutex:
    """Mutex de proceso basado en un LOCK del SISTEMA OPERATIVO sobre un lockfile
    (msvcrt.locking en Windows, fcntl.flock en POSIX). Serializa el read-modify-write entre procesos
    -> sin lost updates ni lineas corruptas.

    Por que un lock del SO y no un lockfile O_EXCL hecho a mano (como la version historica): el O_EXCL
    "crear-y-luego-escribir-pid" tiene una ventana TOCTOU (otro proceso lee el lockfile aun vacio, lo
    cree muerto y roba el lock) y deja locks rancios si el proceso muere. El lock del SO no tiene esa
    ventana y se LIBERA SOLO cuando el proceso muere (el SO cierra el handle) -> nada de TTL/pid-guessing.

    `lockdir` parametrizable: los tests reapuntan el dir de locks de su modulo para aislarse. Tras
    MUTEX_SPIN s de contencion se rinde y entra igual (best-effort, evita deadlock; solo alcanzable bajo
    contencion patologica que el uso real nunca produce)."""
    def __init__(self, name: str = "multisesion", lockdir=None):
        self.lockdir = pathlib.Path(lockdir) if lockdir else LOCKDIR
        self.lockdir.mkdir(parents=True, exist_ok=True)
        self.file = self.lockdir / f"mutex_{name}.lock"
        self._fh = None
        self._locked = False

    def _try_lock(self) -> bool:
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)  # no bloqueante: lanza si tomado
                return True
            except OSError:
                return False
        import fcntl
        try:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def __enter__(self):
        self._fh = open(self.file, "a+", encoding="utf-8")  # handle estable para el lock del SO
        try:
            self._fh.seek(0)   # bloqueamos/desbloqueamos siempre el byte 0 (misma region)
        except OSError:
            pass
        fin = time.time() + MUTEX_SPIN
        while True:
            if self._try_lock():
                self._locked = True
                return self
            if time.time() > fin:
                return self  # me rindo y entro igual (best-effort): evita deadlock
            time.sleep(0.05)

    def __exit__(self, *a):
        try:
            if self._locked and self._fh is not None:
                if os.name == "nt":
                    import msvcrt
                    try:
                        self._fh.seek(0)
                        msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    import fcntl
                    try:
                        fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
                    except OSError:
                        pass
        finally:
            self._locked = False
            if self._fh is not None:
                try:
                    self._fh.close()
                except OSError:
                    pass
            self._fh = None
