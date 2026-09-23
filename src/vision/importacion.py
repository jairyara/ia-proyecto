"""Importador administrativo del piloto: PostgreSQL + lote de archivos inmutable."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session

from src.datos.validacion import ManifiestoAmazon, validar_amazon
from src.persistencia.imagenes import AsociacionVisual, Imagen, PilotoVisual
from src.persistencia.logistica import Parada
from src.persistencia.modelos import Dataset, Importacion
from src.vision.almacenamiento import publicar_lote, verificar_lote
from src.vision.asociacion import construir_mapa, hash_mapa
from src.vision.manifiesto import ErrorVisual, auditar_piloto, json_bytes


LOCK_VISUAL = 2026092204
VERSION_IMPORTADOR = "visual-1"


class ErrorImportacionVisual(RuntimeError):
    """Mensaje administrativo sin credenciales ni detalles internos SQL."""


def _valores_imagen(i: dict, dataset_id: int, lote: str) -> dict:
    return {"dataset_id": dataset_id, "clave_archivo": f"{lote}/{i['sha256']}.png",
            **{k: i[k] for k in ("id_origen", "sha256", "mime", "bytes", "ancho", "alto",
                                 "grupo_origen", "etiqueta_origen", "etiqueta")}}


def _persistir(sesion: Session, visual: dict, mapa: dict, lote: str, amazon: Dataset,
               visual_version: str) -> tuple[PilotoVisual, bool]:
    existente = sesion.scalar(select(PilotoVisual).where(PilotoVisual.version == mapa["version"]))
    mapa_texto = json_bytes(mapa).decode()
    if existente:
        if existente.mapa_sha256 != lote or existente.mapa_json != mapa_texto or existente.dataset_amazon_id != amazon.id:
            raise ErrorVisual("Piloto ya existe con otro mapa; crea una versión nueva.")
        if (existente.algoritmo, existente.semilla_paradas, existente.semilla_imagenes) != (
            mapa["algoritmo"], mapa["semilla_paradas"], mapa["semilla_imagenes"]):
            raise ErrorVisual("Metadatos del piloto alterados.")
        dataset = sesion.get(Dataset, existente.dataset_visual_id)
        if (dataset.fuente, dataset.version, dataset.sha256, dataset.procedencia) != (
            mapa["visual"]["fuente"], visual_version, mapa["visual"]["sha256"], mapa["aviso"]):
            raise ErrorVisual("Dataset visual persistido difiere del manifiesto.")
        imagenes = sesion.scalars(select(Imagen).where(Imagen.dataset_id == dataset.id)).all()
        esperadas = {i["id_origen"]: _valores_imagen(i, dataset.id, lote) for i in visual["imagenes"]}
        if len(imagenes) != 200 or any(
            i.id_origen not in esperadas or any(getattr(i, k) != v for k, v in esperadas[i.id_origen].items())
            for i in imagenes
        ):
            raise ErrorVisual("Metadatos de imágenes persistidas alterados.")
        pares = sesion.execute(select(Parada.pedido_id, Imagen.id_origen, AsociacionVisual.tipo_asociacion)
            .select_from(AsociacionVisual).join(Parada, Parada.id == AsociacionVisual.parada_id)
            .join(Imagen, Imagen.id == AsociacionVisual.imagen_id)
            .where(AsociacionVisual.piloto_id == existente.id)).all()
        esperado = [(a["pedido_id"], a["imagen_id_origen"], "simulada") for a in mapa["asociaciones"]]
        if sorted(pares) != esperado:
            raise ErrorVisual("Asociaciones persistidas difieren del mapa; no reasignar.")
        return existente, False
    dataset = Dataset(fuente=mapa["visual"]["fuente"], version=visual_version,
                      sha256=mapa["visual"]["sha256"], procedencia=mapa["aviso"], estado="completo",
                      num_paradas=0, num_rutas=0, num_estaciones=0)
    sesion.add(dataset)
    sesion.flush()
    imagenes = [Imagen(**_valores_imagen(i, dataset.id, lote)) for i in visual["imagenes"]]
    sesion.add_all(imagenes)
    sesion.flush()
    ids = {i.id_origen: i.id for i in imagenes}
    paradas = dict(sesion.execute(select(Parada.pedido_id, Parada.id).where(Parada.dataset_id == amazon.id)).all())
    piloto = PilotoVisual(version=mapa["version"], dataset_amazon_id=amazon.id, dataset_visual_id=dataset.id,
                          algoritmo=mapa["algoritmo"], semilla_paradas=mapa["semilla_paradas"],
                          semilla_imagenes=mapa["semilla_imagenes"], mapa_sha256=lote, mapa_json=mapa_texto)
    sesion.add(piloto)
    sesion.flush()
    sesion.add_all([AsociacionVisual(piloto_id=piloto.id, dataset_amazon_id=amazon.id,
                    dataset_visual_id=dataset.id, parada_id=paradas[a["pedido_id"]],
                    imagen_id=ids[a["imagen_id_origen"]], tipo_asociacion="simulada")
                    for a in mapa["asociaciones"]])
    sesion.flush()
    return piloto, True


def importar_piloto(originales: Path, manifiesto: Path, csv: Path, amazon: ManifiestoAmazon,
                     almacenamiento: Path, *, motor: Engine | None = None,
                     dry_run: bool = False, version: str = "v1") -> dict:
    """Dry-run valida ambos orígenes sin BD ni escrituras (no prueba su estado en BD).

    Todo lote publicado se conserva si falla commit: puede estar referenciado tras
    una pérdida de conexión. El siguiente intento verifica y reutiliza; nunca borra
    archivos ajenos o versiones anteriores. No servir archivos sin metadatos en BD.
    """
    visual_bytes = manifiesto.read_bytes()
    huella = sha256(visual_bytes).hexdigest()
    intento_id = None
    visual_version = f"2-side-{version}"
    if not dry_run:
        if motor is None:
            raise ValueError("Importación real requiere motor explícito.")
        with Session(motor) as sesion, sesion.begin():
            intento = Importacion(fuente="piloto-visual", version=version, sha256=huella,
                version_importador=VERSION_IMPORTADOR, estado="en_curso", filas_leidas=0, filas_insertadas=0)
            sesion.add(intento)
            sesion.flush()
            intento_id = intento.id
    try:
        visual = json.loads(visual_bytes)
        auditar_piloto(originales, manifiesto=visual)
        csv_bytes = csv.read_bytes()
        mapa = construir_mapa(csv_bytes, amazon, visual, visual_bytes, version=version)
        lote = hash_mapa(mapa)
        if dry_run:
            return {"estado": "validado", "imagenes": 200, "asociaciones": 200,
                    "mapa_sha256": lote, "filas_insertadas": 0}
        with Session(motor) as sesion, sesion.begin():
            sesion.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": LOCK_VISUAL})
            # Coordinar con el seed Amazon sin alterar los módulos históricos.
            sesion.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": 2026092202})
            dataset = sesion.scalar(select(Dataset).where(Dataset.fuente == amazon.fuente, Dataset.version == amazon.version))
            if dataset is None or (dataset.sha256, dataset.num_paradas, dataset.num_rutas, dataset.num_estaciones, dataset.procedencia) != (
                amazon.sha256, amazon.paradas, amazon.rutas, amazon.estaciones, amazon.procedencia
            ):
                raise ErrorVisual("Importa primero la versión exacta del dataset Amazon.")
            # El CSV validado determina el universo, no una consulta con filas extra/faltantes.
            ids_csv = {f["pedido_id"] for f in validar_amazon(csv_bytes, amazon).filas}
            ids_bd = set(sesion.scalars(select(Parada.pedido_id).where(Parada.dataset_id == dataset.id)))
            if ids_bd != ids_csv:
                raise ErrorVisual("Las paradas en BD difieren del CSV fijado.")
            piloto, nuevo = _persistir(sesion, visual, mapa, lote, dataset, visual_version)
            if nuevo:
                publicar_lote(almacenamiento, originales, visual, mapa, lote)
            else:
                verificar_lote(almacenamiento, visual, mapa, lote)
            intento = sesion.get(Importacion, intento_id)
            intento.dataset_id = piloto.dataset_visual_id
            intento.estado = "completada" if nuevo else "sin_cambios"
            intento.filas_leidas, intento.filas_insertadas = 200, 200 if nuevo else 0
            intento.terminado_en = datetime.now(timezone.utc)
            resultado = {"estado": intento.estado, "piloto_id": piloto.id, "importacion_id": intento_id,
                         "imagenes": 200, "asociaciones": 200, "mapa_sha256": lote,
                         "filas_insertadas": intento.filas_insertadas}
        return resultado
    except Exception as exc:
        mensaje = str(exc) if isinstance(exc, ErrorVisual) else "Falló la importación visual; no se publicaron metadatos parciales."
        if intento_id is not None:
            try:
                with Session(motor) as sesion, sesion.begin():
                    intento = sesion.get(Importacion, intento_id)
                    # Commit pudo completarse aunque el cliente perdiera la respuesta.
                    if intento.estado == "en_curso":
                        intento.estado, intento.error = "fallida", mensaje
                        intento.terminado_en = datetime.now(timezone.utc)
            except Exception:
                raise ErrorImportacionVisual("No se pudo confirmar el resultado ni actualizar auditoría; conservar archivos y reintentar.") from None
        if isinstance(exc, ErrorVisual):
            raise
        raise ErrorImportacionVisual(mensaje) from None
