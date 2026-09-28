"""Lecturas del MLP visual persistido; no entrena ni ejecuta pickle en HTTP."""

import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from api.routers.datos import _sesion


router = APIRouter(prefix="/api/modelo-visual", tags=["Semana 8 · reconocimiento visual"])


class EstadoModelo(BaseModel):
    estado: str
    version: str | None = None
    dataset_id: int | None = None
    total_train: int = 0
    total_test: int = 0
    accuracy: float | None = None
    accuracy_baseline: float | None = None
    matriz_confusion: list[list[int]] | None = None
    por_clase: dict | None = None
    convergencia_advertida: bool | None = None
    aviso: str


class PrediccionDTO(BaseModel):
    imagen_id: int
    id_origen: str
    etiqueta_real: str
    clase_predicha: str
    probabilidad_predicha: float = Field(ge=0, le=1)
    archivo_url: str


class PaginaPredicciones(BaseModel):
    items: list[PrediccionDTO]
    total: int
    limite: int
    offset: int


class RelacionDTO(BaseModel):
    origen: str
    relacion: str
    destino: str


class OntologiaDTO(BaseModel):
    version: str
    ejemplo_imagen_id: int | None
    relaciones: list[RelacionDTO]


def _ultimo_modelo(sesion):
    from src.persistencia.modelo_visual import ModeloVisual
    return sesion.scalar(select(ModeloVisual).order_by(ModeloVisual.id.desc()))


@router.get("/resumen", response_model=EstadoModelo)
def resumen_modelo():
    """Métricas de la prueba reservada o estado explícito sin entrenamiento."""
    with _sesion() as sesion:
        modelo = _ultimo_modelo(sesion)
        if modelo is None:
            return EstadoModelo(estado="no_entrenado", aviso="No hay modelo visual registrado en PostgreSQL.")
        meta = json.loads(modelo.metadatos_json)
        ev = meta["evaluacion"]
        return EstadoModelo(
            estado="evaluado", version=modelo.version, dataset_id=modelo.dataset_id,
            total_train=meta["particion"]["train"], total_test=meta["particion"]["test"],
            accuracy=ev["accuracy"], accuracy_baseline=ev["accuracy_baseline"],
            matriz_confusion=ev["matriz_confusion"], por_clase=ev["por_clase"],
            convergencia_advertida=meta["modelo"]["convergencia_advertida"],
            aviso="Piloto sintético didáctico; no autoriza decisiones automáticas de despacho.",
        )


@router.get("/predicciones", response_model=PaginaPredicciones)
def predicciones_test(limite: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Solo predicciones del conjunto de prueba, con etiqueta de origen separada."""
    from src.persistencia.imagenes import Imagen
    from src.persistencia.modelo_visual import MuestraModeloVisual
    with _sesion() as sesion:
        modelo = _ultimo_modelo(sesion)
        if modelo is None:
            return PaginaPredicciones(items=[], total=0, limite=limite, offset=offset)
        filtro = (MuestraModeloVisual.modelo_id == modelo.id, MuestraModeloVisual.split == "test")
        total = sesion.scalar(select(func.count(MuestraModeloVisual.id)).where(*filtro))
        filas = sesion.execute(select(MuestraModeloVisual, Imagen)
            .join(Imagen, Imagen.id == MuestraModeloVisual.imagen_id)
            .where(*filtro).order_by(Imagen.id).limit(limite).offset(offset)).all()
        return PaginaPredicciones(items=[PrediccionDTO(
            imagen_id=imagen.id, id_origen=imagen.id_origen, etiqueta_real=imagen.etiqueta,
            clase_predicha=muestra.clase_predicha, probabilidad_predicha=muestra.probabilidad,
            archivo_url=f"/api/datos/imagenes/{imagen.id}/archivo",
        ) for muestra, imagen in filas], total=total, limite=limite, offset=offset)


@router.get("/ontologia", response_model=OntologiaDTO)
def ontologia_ejemplo(imagen_id: int | None = Query(None, ge=1)):
    """Vocabulario y una predicción reservada; por defecto, la primera."""
    from src.persistencia.imagenes import Imagen
    from src.persistencia.modelo_visual import MuestraModeloVisual
    from src.vision.ontologia import VERSION_GRAFO, construir_ontologia
    with _sesion() as sesion:
        modelo = _ultimo_modelo(sesion)
        ejemplo = None
        if modelo is not None:
            consulta = (select(MuestraModeloVisual, Imagen)
                .join(Imagen, Imagen.id == MuestraModeloVisual.imagen_id)
                .where(MuestraModeloVisual.modelo_id == modelo.id,
                       MuestraModeloVisual.split == "test"))
            if imagen_id is not None:
                consulta = consulta.where(Imagen.id == imagen_id)
            ejemplo = sesion.execute(consulta.order_by(Imagen.id).limit(1)).first()
        if imagen_id is not None and ejemplo is None:
            raise HTTPException(status_code=404, detail="No existe una predicción de prueba para esa imagen.")
        pred = {"id_origen": ejemplo.Imagen.id_origen,
                "clase_predicha": ejemplo.MuestraModeloVisual.clase_predicha} if ejemplo else None
        grafo = construir_ontologia(pred)
        return OntologiaDTO(version=VERSION_GRAFO,
                            ejemplo_imagen_id=ejemplo.Imagen.id if ejemplo else None,
                            relaciones=[RelacionDTO(origen=a, relacion=d["rel"], destino=b)
                                        for a, b, d in grafo.edges(data=True)])
