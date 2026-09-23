"""Lecturas paginadas del piloto; nunca crea ni modifica datos."""

from contextlib import contextmanager
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/api/datos", tags=["inspección de datos"])


@contextmanager
def _sesion():
    # Los módulos históricos deben seguir importándose sin driver ni configuración BD.
    from src.configuracion import ErrorConfiguracion
    from src.persistencia.sesion import abrir_sesion, crear_motor
    try:
        motor = crear_motor()
        try:
            with abrir_sesion(motor) as sesion:
                yield sesion
        finally:
            motor.dispose()
    except (ErrorConfiguracion, SQLAlchemyError) as error:
        raise HTTPException(status_code=503, detail="Base de datos no disponible.") from error


def _piloto(sesion):
    from src.persistencia.imagenes import PilotoVisual
    return sesion.scalars(select(PilotoVisual).order_by(PilotoVisual.id.desc())).first()


def _resumen(sesion):
    from src.persistencia.imagenes import AsociacionVisual, Imagen
    from src.persistencia.modelos import Dataset
    amazon = sesion.scalars(select(Dataset).where(Dataset.fuente.like("%amazon%"), Dataset.estado == "completo").order_by(Dataset.id.desc())).first()
    piloto = _piloto(sesion)
    if amazon is None:
        amazon = sesion.scalars(select(Dataset).where(Dataset.num_paradas > 0, Dataset.estado == "completo").order_by(Dataset.id.desc())).first()
    imagenes = sesion.scalar(select(func.count(Imagen.id)).where(Imagen.dataset_id == piloto.dataset_visual_id)) if piloto else 0
    asociaciones = sesion.scalar(select(func.count(AsociacionVisual.id)).where(AsociacionVisual.piloto_id == piloto.id)) if piloto else 0
    clases = dict(sesion.execute(select(Imagen.etiqueta, func.count(Imagen.id)).where(Imagen.dataset_id == piloto.dataset_visual_id).group_by(Imagen.etiqueta)).all()) if piloto else {}
    grupos = sesion.scalar(select(func.count(func.distinct(Imagen.grupo_origen))).where(Imagen.dataset_id == piloto.dataset_visual_id)) if piloto else 0
    return {
        "amazon": {"dataset_id": amazon.id, "fuente": amazon.fuente, "version": amazon.version, "procedencia": amazon.procedencia,
                   "paradas": amazon.num_paradas, "rutas": amazon.num_rutas, "estaciones": amazon.num_estaciones} if amazon else None,
        "visual": {"piloto_id": piloto.id, "version": piloto.version, "imagenes": imagenes, "grupos": grupos,
                   "clases": clases, "asociaciones": asociaciones, "sin_asociacion": max(0, amazon.num_paradas - asociaciones) if amazon else None} if piloto else None,
        "modelo_visual": None,
    }


@router.get("/resumen")
def resumen():
    with _sesion() as sesion:
        return _resumen(sesion)


@router.get("/paradas")
def paradas(limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
            ruta: str | None = None, estacion: str | None = None):
    from src.datos.consulta import listar_paradas
    from src.persistencia.imagenes import AsociacionVisual
    with _sesion() as sesion:
        info = _resumen(sesion)
        if not info["amazon"]:
            return {"items": [], "total": 0, "limite": limite, "offset": offset}
        pagina = listar_paradas(sesion, info["amazon"]["dataset_id"], route_id=ruta or None,
                                station_code=estacion or None, limite=limite, offset=offset)
        ids = [item.id for item in pagina.items]
        asociadas = {}
        if ids and info["visual"]:
            asociadas = dict(sesion.execute(select(AsociacionVisual.parada_id, AsociacionVisual.imagen_id).where(
                AsociacionVisual.piloto_id == info["visual"]["piloto_id"], AsociacionVisual.parada_id.in_(ids))).all())
        return {"items": [{"id": item.id, "pedido_id": item.pedido_id, "route_id": item.route_id,
                            "station_code": item.station_code, "stop_id": item.stop_id, "tipo_parada": item.tipo_parada,
                            "num_paquetes": item.num_paquetes, "distancia_deposito_km": float(item.distancia_deposito_km),
                            "retrasado_estimado": item.retrasado_estimado, "imagen_id": asociadas.get(item.id)} for item in pagina.items],
                "total": pagina.total, "limite": limite, "offset": offset}


@router.get("/imagenes")
def imagenes(limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), etiqueta: str | None = None):
    from src.persistencia.imagenes import Imagen
    if etiqueta not in (None, "intacto", "danado"):
        raise HTTPException(status_code=422, detail="Etiqueta inválida.")
    with _sesion() as sesion:
        piloto = _piloto(sesion)
        if not piloto:
            return {"items": [], "total": 0, "limite": limite, "offset": offset}
        consulta = select(Imagen).where(Imagen.dataset_id == piloto.dataset_visual_id)
        if etiqueta:
            consulta = consulta.where(Imagen.etiqueta == etiqueta)
        total = sesion.scalar(select(func.count()).select_from(consulta.subquery()))
        filas = sesion.scalars(consulta.order_by(Imagen.id).limit(limite).offset(offset)).all()
        return {"items": [{"id": i.id, "id_origen": i.id_origen, "etiqueta": i.etiqueta,
                            "etiqueta_origen": i.etiqueta_origen, "grupo_origen": i.grupo_origen,
                            "ancho": i.ancho, "alto": i.alto, "bytes": i.bytes,
                            "archivo_url": f"/api/datos/imagenes/{i.id}/archivo"} for i in filas],
                "total": total, "limite": limite, "offset": offset}


@router.get("/imagenes/{imagen_id}")
def detalle_imagen(imagen_id: int):
    from src.persistencia.imagenes import AsociacionVisual, Imagen
    from src.persistencia.logistica import Estacion, Parada, Ruta
    with _sesion() as sesion:
        imagen = sesion.get(Imagen, imagen_id)
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada.")
        asociacion = sesion.scalar(select(AsociacionVisual).where(AsociacionVisual.imagen_id == imagen_id))
        parada = sesion.get(Parada, asociacion.parada_id) if asociacion else None
        ruta = sesion.get(Ruta, parada.ruta_id) if parada else None
        estacion = sesion.get(Estacion, ruta.estacion_id) if ruta else None
        return {"id": imagen.id, "id_origen": imagen.id_origen, "etiqueta": imagen.etiqueta,
                "etiqueta_origen": imagen.etiqueta_origen, "grupo_origen": imagen.grupo_origen,
                "ancho": imagen.ancho, "alto": imagen.alto, "bytes": imagen.bytes,
                "archivo_url": f"/api/datos/imagenes/{imagen.id}/archivo",
                "asociacion": {"pedido_id": parada.pedido_id, "route_id": ruta.route_id,
                               "station_code": estacion.station_code, "tipo": asociacion.tipo_asociacion} if parada else None}


@router.get("/imagenes/{imagen_id}/archivo")
def archivo_imagen(imagen_id: int):
    from src.configuracion import ROOT
    from src.persistencia.imagenes import Imagen
    from src.vision.almacenamiento import resolver_clave
    from src.vision.manifiesto import ErrorVisual
    with _sesion() as sesion:
        imagen = sesion.get(Imagen, imagen_id)
        if not imagen:
            raise HTTPException(status_code=404, detail="Imagen no encontrada.")
        clave = imagen.clave_archivo
    raiz = Path(os.getenv("VISUAL_STORAGE_ROOT") or ROOT / "data/visual/almacen")
    try:
        ruta = resolver_clave(raiz, clave)
    except ErrorVisual as error:
        raise HTTPException(status_code=503, detail="Almacenamiento visual inválido.") from error
    if not ruta.is_file() or ruta.stat().st_size != imagen.bytes:
        raise HTTPException(status_code=503, detail="Archivo visual no disponible.")
    return FileResponse(ruta, media_type="image/png", headers={"Cache-Control": "private, max-age=3600", "X-Content-Type-Options": "nosniff"})
