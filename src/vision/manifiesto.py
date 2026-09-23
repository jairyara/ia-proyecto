"""Contrato del piloto de paquetes v2; etiquetas/grupos provienen de la fuente."""

from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import warnings

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "data/manifests"
DEFAULT_RAIZ = ROOT / "data/visual/paquetes-v2"
DEFAULT_MANIFIESTO = MANIFESTS / "piloto-visual-v1.json"
INVENTARIO = MANIFESTS / "paquetes-v2-inventario.json"
FUENTE = MANIFESTS / "paquetes-v2-fuente.json"
API = "https://api.kaggle.com/v1/datasets"
HANDLE = "christianvorhemus/industrial-quality-control-of-packages"
VERSION = 2
MAX_BYTES = 2 * 1024 * 1024
MAX_PIXELES = 2_000_000
PATRON = re.compile(r"(damaged|intact)/(side|top)/(\d{13})_(side|top)\.png", re.ASCII)
ETIQUETAS = {"damaged": "danado", "intact": "intacto"}


class ErrorVisual(ValueError):
    """Datos no admisibles; no corregir ni completar automáticamente el piloto."""


def hash_archivo(ruta: Path) -> str:
    return sha256(ruta.read_bytes()).hexdigest()


def json_bytes(datos) -> bytes:
    return (json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def interpretar_ruta(ruta: str) -> tuple[str, str, str]:
    if not isinstance(ruta, str) or not (match := PATRON.fullmatch(ruta)):
        raise ErrorVisual("Ruta de origen inválida; se esperaba clase/vista/serial_vista.png.")
    clase, vista, serial, sufijo = match.groups()
    if vista != sufijo:
        raise ErrorVisual("Vista en directorio y nombre no coinciden.")
    return clase, vista, serial


def ruta_segura(raiz: Path, relativa: str) -> Path:
    interpretar_ruta(relativa)
    base = raiz.resolve()
    destino = base.joinpath(*PurePosixPath(relativa).parts)
    if not destino.resolve().is_relative_to(base):
        raise ErrorVisual("Archivo fuera de la raíz visual.")
    for parte in (destino, *destino.parents):
        if parte == base:
            break
        if parte.is_symlink():
            raise ErrorVisual("No se aceptan enlaces simbólicos dentro de la raíz visual.")
    return destino


def validar_inventario(datos: dict) -> list[dict]:
    if not isinstance(datos, dict) or datos.get("version") != VERSION or not isinstance(datos.get("archivos"), list):
        raise ErrorVisual("Inventario no corresponde a la versión 2.")
    archivos = datos["archivos"]
    vistos, grupos, conteos = set(), {}, Counter()
    for archivo in archivos:
        if not isinstance(archivo, dict) or set(archivo) != {"ruta", "bytes"}:
            raise ErrorVisual("Registro de inventario inválido.")
        ruta, size = archivo["ruta"], archivo["bytes"]
        clase, vista, serial = interpretar_ruta(ruta)
        if ruta in vistos or type(size) is not int or not 0 < size <= MAX_BYTES:
            raise ErrorVisual("Archivo repetido o tamaño no admisible en inventario.")
        vistos.add(ruta)
        conteos[(clase, vista)] += 1
        grupos.setdefault(serial, []).append((clase, vista))
    if conteos != Counter({(c, v): 100 for c in ETIQUETAS for v in ("side", "top")}):
        raise ErrorVisual("Inventario debe tener 400 archivos: 100 por clase/vista.")
    if len(grupos) != 200 or any(len(g) != 2 or len({c for c, _ in g}) != 1 or {v for _, v in g} != {"side", "top"} for g in grupos.values()):
        raise ErrorVisual("Grupos inconsistentes: se requieren 200 seriales con dos vistas y una etiqueta.")
    return sorted(archivos, key=lambda a: a["ruta"])


def cargar_fuente() -> tuple[dict, list[dict]]:
    fuente = json.loads(FUENTE.read_text(encoding="utf-8"))
    if fuente.get("handle") != HANDLE or fuente.get("version") != VERSION or fuente.get("licencia_declarada") != "GPL 2":
        raise ErrorVisual("Fuente, versión o licencia no corresponde al piloto aprobado.")
    if fuente.get("inventario_sha256") != hash_archivo(INVENTARIO):
        raise ErrorVisual("Hash del inventario no coincide con la fuente registrada.")
    inventario = validar_inventario(json.loads(INVENTARIO.read_text(encoding="utf-8")))
    return fuente, inventario


@dataclass(frozen=True)
class ImagenAuditada:
    id_origen: str
    archivo: str
    grupo_origen: str
    etiqueta_origen: str
    etiqueta: str
    vista: str
    sha256: str
    sha256_pixeles: str
    mime: str
    bytes: int
    ancho: int
    alto: int
    modo: str


def auditar_imagen(contenido: bytes, relativa: str) -> ImagenAuditada:
    clase, vista, serial = interpretar_ruta(relativa)
    if not 0 < len(contenido) <= MAX_BYTES:
        raise ErrorVisual("Imagen vacía o supera el límite de 2 MiB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(contenido), formats=["PNG"]) as imagen:
                if imagen.width * imagen.height > MAX_PIXELES or imagen.size != (960, 540):
                    raise ErrorVisual("Dimensiones no coinciden con originales 960×540.")
                if imagen.mode != "RGB" or getattr(imagen, "n_frames", 1) != 1:
                    raise ErrorVisual("Se requiere PNG RGB de un único cuadro.")
                imagen.verify()
            with Image.open(BytesIO(contenido), formats=["PNG"]) as imagen:
                imagen.load()  # verify() no garantiza que el raster completo se decodifique.
                huella_pixeles = sha256(imagen.tobytes()).hexdigest()
    except (OSError, SyntaxError, UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ErrorVisual("Imagen corrupta, no PNG o no decodificable de forma segura.") from exc
    return ImagenAuditada(
        f"{serial}_{vista}", relativa, serial, clase, ETIQUETAS[clase], vista,
        sha256(contenido).hexdigest(), huella_pixeles, "image/png", len(contenido), 960, 540, "RGB",
    )


def auditar_piloto(raiz: Path, *, manifiesto: dict | None = None) -> dict:
    """Lee originales; nunca reetiqueta, modifica imágenes ni conecta a BD."""
    _, inventario = cargar_fuente()
    seleccion = [a for a in inventario if "/side/" in a["ruta"]]
    registros, hashes, pixeles = [], set(), set()
    for archivo in seleccion:
        ruta = ruta_segura(raiz, archivo["ruta"])
        if not ruta.is_file() or ruta.stat().st_size != archivo["bytes"]:
            raise ErrorVisual(f"Archivo ausente o tamaño distinto de la fuente: {archivo['ruta']}")
        registro = auditar_imagen(ruta.read_bytes(), archivo["ruta"])
        if registro.sha256 in hashes or registro.sha256_pixeles in pixeles:
            raise ErrorVisual("Imágenes duplicadas por bytes o por píxeles decodificados.")
        hashes.add(registro.sha256)
        pixeles.add(registro.sha256_pixeles)
        registros.append(asdict(registro))
    resultado = {
        "schema_version": 1, "piloto": "piloto-visual-v1", "fuente_handle": HANDLE,
        "fuente_version": VERSION, "fuente_sha256": hash_archivo(FUENTE),
        "inventario_sha256": hash_archivo(INVENTARIO),
        "algoritmo_seleccion": "todas-las-vistas-side-v1", "imagenes": registros,
        "conteos": {"imagenes": 200, "grupos": 200, "intacto": 100, "danado": 100},
        "bytes_total": sum(r["bytes"] for r in registros),
        "auditoria_tecnica": "aprobada",
        "aviso": "Imágenes sintéticas farmacéuticas. No corresponden a envíos Amazon. Sin asociaciones todavía.",
    }
    if manifiesto is not None and manifiesto != resultado:
        raise ErrorVisual("Originales o metadatos difieren del manifiesto fijado; no sobrescribir la versión.")
    return resultado
