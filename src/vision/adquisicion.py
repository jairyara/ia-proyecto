"""Descarga administrativa selectiva de originales Kaggle v2; no importa a BD."""

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import urlopen

from src.vision.manifiesto import (
    API, HANDLE, VERSION, MAX_BYTES, DEFAULT_RAIZ, DEFAULT_MANIFIESTO,
    ErrorVisual, auditar_imagen, auditar_piloto, cargar_fuente, json_bytes,
    ruta_segura, validar_inventario,
)


def descargar_bytes(url: str, limite: int) -> bytes:
    """TLS verificado, plazo y tamaño acotados; nunca descarga ZIP completo."""
    ultimo_error = None
    for intento in range(3):
        try:
            with urlopen(url, timeout=45) as respuesta:
                if urlparse(respuesta.url).scheme != "https":
                    raise ErrorVisual("Redirección de descarga no segura.")
                contenido = respuesta.read(limite + 1)
                if len(contenido) > limite:
                    raise ErrorVisual("Respuesta supera el límite de descarga.")
                return contenido
        except (URLError, TimeoutError, ConnectionError) as exc:
            ultimo_error = exc
            if intento < 2:
                time.sleep(intento + 1)
    raise ErrorVisual("No fue posible descargar desde Kaggle; revisa conectividad/acceso y reintenta.") from ultimo_error


def verificar_inventario_remoto(esperado: list[dict]) -> None:
    archivos, token, tokens = [], None, set()
    for _ in range(25):  # Evita paginación infinita o un dataset inesperadamente grande.
        params = {"datasetVersionNumber": VERSION, "pageSize": 200}
        if token:
            params["pageToken"] = token
        respuesta = json.loads(descargar_bytes(f"{API}/list/{HANDLE}?{urlencode(params)}", 2 * 1024 * 1024))
        if respuesta.get("errorMessage") or not isinstance(respuesta.get("datasetFiles"), list):
            raise ErrorVisual("Respuesta de inventario Kaggle inválida.")
        archivos.extend({"ruta": f["name"], "bytes": f["totalBytes"]} for f in respuesta["datasetFiles"])
        token = respuesta.get("nextPageToken")
        if not token:
            break
        if token in tokens:
            raise ErrorVisual("Token de paginación repetido.")
        tokens.add(token)
    else:
        raise ErrorVisual("Inventario remoto excede límite de páginas.")
    actual = validar_inventario({"version": VERSION, "archivos": archivos})
    if actual != esperado:
        raise ErrorVisual("Inventario remoto cambió respecto de la versión fijada.")


def guardar_nuevo(destino: Path, contenido: bytes) -> None:
    """Publicación sin sobrescribir; temporales propios se eliminan ante fallos."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(dir=destino.parent, prefix=".descarga-", delete=False) as f:
            temporal = Path(f.name)
            f.write(contenido)
            f.flush()
            os.fsync(f.fileno())
        os.link(temporal, destino)  # Falla si alguien publicó ese nombre; no reemplaza originales.
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def adquirir(raiz: Path, manifiesto: Path, *, dry_run=False) -> dict:
    _, inventario = cargar_fuente()
    seleccion = [a for a in inventario if "/side/" in a["ruta"]]
    resumen = {"imagenes": len(seleccion), "bytes": sum(a["bytes"] for a in seleccion), "version": VERSION}
    if dry_run:
        return {"estado": "plan_validado_sin_red_ni_escrituras", **resumen}
    previo = json.loads(manifiesto.read_text(encoding="utf-8")) if manifiesto.exists() else None
    hashes_previos = {r["archivo"]: r["sha256"] for r in previo["imagenes"]} if previo else {}
    verificar_inventario_remoto(inventario)
    for numero, archivo in enumerate(seleccion, start=1):
        ruta = ruta_segura(raiz, archivo["ruta"])
        existe = ruta.exists()
        if existe:
            if not ruta.is_file() or ruta.stat().st_size != archivo["bytes"]:
                raise ErrorVisual(f"Archivo local inválido; no se sobrescribe: {archivo['ruta']}")
            contenido = ruta.read_bytes()
        else:
            url = f"{API}/download/{HANDLE}/{quote(archivo['ruta'], safe='')}?datasetVersionNumber={VERSION}"
            contenido = descargar_bytes(url, MAX_BYTES)
        if len(contenido) != archivo["bytes"]:
            raise ErrorVisual(f"Tamaño de descarga distinto del inventario: {archivo['ruta']}")
        registro = auditar_imagen(contenido, archivo["ruta"])
        if previo and hashes_previos.get(archivo["ruta"]) != registro.sha256:
            raise ErrorVisual("SHA-256 distinto del manifiesto previo; no reemplazar originales.")
        if not existe:
            guardar_nuevo(ruta, contenido)
        print(f"{numero}/200: {'verificado' if existe else 'descargado'} {archivo['ruta']}", file=sys.stderr)
    resultado = auditar_piloto(raiz, manifiesto=previo)
    if previo is None:
        guardar_nuevo(manifiesto, json_bytes(resultado))
    return {"estado": "sin_cambios" if previo else "adquirido_y_auditado", **resumen}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=DEFAULT_RAIZ)
    parser.add_argument("--manifiesto", type=Path, default=DEFAULT_MANIFIESTO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(adquirir(args.raiz, args.manifiesto, dry_run=args.dry_run), ensure_ascii=False))
        return 0
    except (ErrorVisual, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error de adquisición: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
