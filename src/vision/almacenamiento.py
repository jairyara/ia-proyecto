"""Publicación atómica por lote, fuera de la SPA; archivos originales inmutables.

El llamador serializa escritores mediante el bloqueo PostgreSQL del importador.
Tras un commit incierto NO borrar lo publicado: reintentar verifica y reutiliza.
"""

from hashlib import sha256
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from src.vision.manifiesto import ErrorVisual, MAX_BYTES, json_bytes, ruta_segura


PATRON_CLAVE = re.compile(r"[0-9a-f]{64}/(?:[0-9a-f]{64}\.png|mapa\.json)", re.ASCII)


def resolver_clave(raiz: Path, clave: str) -> Path:
    if not PATRON_CLAVE.fullmatch(clave):
        raise ErrorVisual("Clave de almacenamiento inválida.")
    base = raiz.absolute()
    destino = base / clave
    # También rechazar symlinks en la raíz configurada y sus ancestros.
    for parte in (destino, *destino.parents):
        if parte.is_symlink():
            raise ErrorVisual("Almacenamiento no admite enlaces simbólicos.")
    if not destino.resolve().is_relative_to(base.resolve()):
        raise ErrorVisual("Clave fuera del almacenamiento.")
    return destino


def _comprobar(ruta: Path, huella: str, size: int) -> None:
    if not ruta.is_file() or ruta.stat().st_size != size or sha256(ruta.read_bytes()).hexdigest() != huella:
        raise ErrorVisual("Almacenamiento ausente o alterado; no sobrescribir archivos publicados.")


def verificar_lote(raiz: Path, visual: dict, mapa: dict, lote: str) -> None:
    contenido = json_bytes(mapa)
    _comprobar(resolver_clave(raiz, f"{lote}/mapa.json"), sha256(contenido).hexdigest(), len(contenido))
    for i in visual["imagenes"]:
        _comprobar(resolver_clave(raiz, f"{lote}/{i['sha256']}.png"), i["sha256"], i["bytes"])


def _escribir(ruta: Path, contenido: bytes) -> None:
    with ruta.open("xb") as salida:
        salida.write(contenido)
        salida.flush()
        os.fsync(salida.fileno())


def publicar_lote(raiz: Path, originales: Path, visual: dict, mapa: dict, lote: str) -> None:
    destino = resolver_clave(raiz, f"{lote}/mapa.json").parent
    if destino.exists():
        verificar_lote(raiz, visual, mapa, lote)
        return
    raiz.mkdir(parents=True, exist_ok=True)
    # TemporaryDirectory limpia solamente su staging, nunca lotes publicados.
    with TemporaryDirectory(prefix=".staging-", dir=raiz) as temporal:
        staging = Path(temporal) / "lote"
        staging.mkdir()
        for i in visual["imagenes"]:
            origen = ruta_segura(originales, i["archivo"])
            if origen.stat().st_size > MAX_BYTES:
                raise ErrorVisual("Original supera el límite de bytes.")
            contenido = origen.read_bytes()
            if len(contenido) != i["bytes"] or sha256(contenido).hexdigest() != i["sha256"]:
                raise ErrorVisual("Original cambió después de su auditoría.")
            _escribir(staging / f"{i['sha256']}.png", contenido)
        _escribir(staging / "mapa.json", json_bytes(mapa))
        # En el mismo filesystem; sin punto donde un lector vea medio lote.
        staging.rename(destino)
    verificar_lote(raiz, visual, mapa, lote)
