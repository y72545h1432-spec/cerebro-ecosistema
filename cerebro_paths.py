"""cerebro_paths.py — Rutas ROBUSTAS y conscientes de la nube (OneDrive). Stdlib + ctypes, sin deps.

GLOBALIZADO (2026-06-22, F6): la lógica anti-OneDrive nació en `tu-tienda/scripts/novu_paths.py` pero es
infra del ECOSISTEMA. Sirve directo a la regla #10 del hub (salud del PC) y al tema transversal de
F1-F5 "todo fuera de OneDrive": detectar placeholders deshidratados, materializarlos, dar un directorio
de estado SIEMPRE local, y resolver la raíz de un proyecto sobreviviendo a carpetas movidas / OneDrive
deshidratado / unidad distinta. `tu-tienda/scripts/novu_paths.py` ahora CONSUME este módulo.

API:
    is_dehydrated(path)                      -> True si es placeholder OneDrive (no descargado)
    materialized(path)                       -> existe Y se puede leer de verdad (fuerza hidratación)
    state_dir(name="cerebro")                -> carpeta de estado/locks SIEMPRE local (LOCALAPPDATA)
    resolve_root(marker_dir, sentinel, ...)  -> Path validado o None (robusto: env/puntero/conocidas/scan)
    write_pointer(path, root)                -> reescribe un puntero estable para acelerar la próxima
"""
import os
import pathlib
import string

try:
    import ctypes
except Exception:  # pragma: no cover (ctypes está en stdlib de CPython; defensa por si acaso)
    ctypes = None

# atributos de archivo "no esta aqui de verdad" (OneDrive/placeholders)
FILE_ATTRIBUTE_OFFLINE = 0x1000
FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x00040000
FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000
_DEHYDRATED = (FILE_ATTRIBUTE_OFFLINE | FILE_ATTRIBUTE_RECALL_ON_OPEN
               | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS)
INVALID = 0xFFFFFFFF


def is_dehydrated(path) -> bool:
    """True si el archivo es un placeholder OneDrive (no descargado). False si no se puede saber."""
    if ctypes is None or os.name != "nt":
        return False
    try:
        # GetFileAttributesW devuelve un int FIRMADO en ctypes: coercionar a unsigned de 32 bits
        # para que un archivo inexistente (-1) compare igual a INVALID (0xFFFFFFFF) y no caiga en la
        # máscara de deshidratado por error.
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path)) & 0xFFFFFFFF
    except Exception:
        return False
    if attrs == INVALID:
        return False
    return bool(attrs & _DEHYDRATED)


def materialized(path) -> bool:
    """El archivo existe Y se puede leer de verdad (toca 1 byte para forzar hidratación on-demand)."""
    p = pathlib.Path(path)
    if not p.exists():
        return False
    try:
        with open(p, "rb") as f:      # tocar 1 byte fuerza descarga on-demand si está deshidratado
            f.read(1)
    except OSError:
        return False
    return not is_dehydrated(p)


def state_dir(name: str = "cerebro") -> pathlib.Path:
    """Carpeta de estado/locks: SIEMPRE local (LOCALAPPDATA), NUNCA OneDrive. La crea si no existe."""
    base = os.environ.get("LOCALAPPDATA") or str(pathlib.Path.home())
    d = pathlib.Path(base) / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_pointer(pointer, root) -> None:
    """Reescribe un puntero estable (archivo de texto) a la raíz, para acelerar la próxima resolución."""
    try:
        p = pathlib.Path(pointer)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(root), encoding="utf-8")
    except OSError:
        pass


def _valid_root(cand, marker_dir, sentinel) -> bool:
    if not cand:
        return False
    root = pathlib.Path(cand)
    return (root / marker_dir).is_dir() and materialized(root / sentinel)


def _scan_drives(folder_name, marker_dir):
    """Último recurso: buscar X:\\<folder_name>\\<marker_dir> en cada unidad fija."""
    for letter in string.ascii_uppercase:
        base = f"{letter}:\\"
        if not os.path.isdir(base):
            continue
        cand = os.path.join(base, folder_name)
        if os.path.isdir(os.path.join(cand, marker_dir)):
            yield cand


def resolve_root(marker_dir, sentinel, *, env_var=None, pointer=None, known=(),
                 scan_drives_for=None, update_pointer=True):
    """Resuelve la raíz de un proyecto de forma ROBUSTA. Devuelve `Path` validado y materializado, o
    `None` si ninguna candidata valida (el llamador decide qué hacer ante None).

    Orden (primera que valide gana):
      1. variable de entorno `env_var`
      2. puntero estable `pointer` (archivo de texto con la ruta; fuera de la nube)
      3. ubicaciones `known` (iterable de rutas/strings)
      4. autodescubrimiento por unidades buscando `scan_drives_for` (nombre de carpeta) + `marker_dir`
    Valida con `marker_dir/` presente y `sentinel` MATERIALIZADO (no deshidratado). Si encuentra la raíz
    por un método tardío y hay `pointer`, lo REESCRIBE para acelerar la próxima vez.
    """
    seen = set()

    def _candidatas():
        if env_var:
            yield os.environ.get(env_var)
        if pointer:
            try:
                pp = pathlib.Path(pointer)
                if pp.exists():
                    yield pp.read_text(encoding="utf-8").strip()
            except OSError:
                pass
        for c in known:
            yield str(c)

    def _aceptar(cand):
        root = pathlib.Path(cand).resolve()
        if update_pointer and pointer:
            write_pointer(pointer, root)
        return root

    for cand in _candidatas():
        if not cand or cand in seen:
            continue
        seen.add(cand)
        if _valid_root(cand, marker_dir, sentinel):
            return _aceptar(cand)

    if scan_drives_for:
        for cand in _scan_drives(scan_drives_for, marker_dir):
            if _valid_root(cand, marker_dir, sentinel):
                return _aceptar(cand)

    return None
