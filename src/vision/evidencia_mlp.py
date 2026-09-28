# Dashboard · Semana 08 — Reconocimiento, evidencia y ontología
"""Registro explícito e idempotente del experimento MLP sobre el piloto importado."""

from hashlib import sha256
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.persistencia.imagenes import Imagen, PilotoVisual
from src.persistencia.modelo_visual import ModeloVisual, MuestraModeloVisual
from src.persistencia.modelos import Dataset
from src.vision.manifiesto import ErrorVisual
from src.vision.particion import ParticionVisual


def registrar_modelo(
    sesion: Session, particion: ParticionVisual, metadatos: dict,
    artefacto: Path, *, version_piloto: str = "v1",
) -> tuple[ModeloVisual, bool]:
    """Se invoca dentro de una transacción; jamás modifica etiquetas originales."""
    if metadatos.get("dataset_manifiesto_sha256") != particion.manifiesto_sha256:
        raise ErrorVisual("El manifiesto del modelo no corresponde a las imágenes verificadas.")
    if metadatos.get("particion", {}).get("ids") != particion.ids_por_split():
        raise ErrorVisual("La partición del modelo no corresponde a las imágenes verificadas.")
    if not artefacto.is_file() or sha256(artefacto.read_bytes()).hexdigest() != metadatos.get("modelo_sha256"):
        raise ErrorVisual("El artefacto del modelo falta o cambió.")
    if artefacto.name != "modelo_mlp_logistica.pkl" or artefacto.parent.name != "semana08":
        raise ErrorVisual("Nombre de artefacto no reconocido.")
    piloto = sesion.scalar(select(PilotoVisual).where(PilotoVisual.version == version_piloto))
    if piloto is None:
        raise ErrorVisual("Importa primero la versión requerida del piloto visual.")
    dataset = sesion.get(Dataset, piloto.dataset_visual_id)
    if dataset is None or dataset.sha256 != particion.manifiesto_sha256:
        raise ErrorVisual("Dataset visual persistido no corresponde al manifiesto auditado.")
    imagenes = sesion.scalars(select(Imagen).where(Imagen.dataset_id == dataset.id)).all()
    por_origen = {imagen.id_origen: imagen for imagen in imagenes}
    if len(imagenes) != len(particion.muestras) or len(por_origen) != len(imagenes):
        raise ErrorVisual("El inventario persistido no corresponde al conjunto de entrenamiento.")
    for muestra in particion.muestras:
        imagen = por_origen.get(muestra.id_origen)
        if imagen is None or (imagen.sha256, imagen.grupo_origen, imagen.etiqueta) != (
            muestra.sha256, muestra.grupo_origen, muestra.etiqueta
        ):
            raise ErrorVisual("Metadatos de imagen persistida no corresponden al piloto auditado.")

    version = metadatos.get("version")
    if not isinstance(version, str) or not version:
        raise ErrorVisual("Versión de modelo ausente.")
    metadatos_json = json.dumps(metadatos, ensure_ascii=False, sort_keys=True)
    esperadas = []
    predicciones = {p["id_origen"]: p for p in metadatos["predicciones_test"]}
    if set(predicciones) != set(particion.ids_por_split()["test"]):
        raise ErrorVisual("Faltan predicciones del conjunto reservado.")
    for split, indices in (("train", particion.indices_train), ("test", particion.indices_test)):
        for indice in indices:
            muestra = particion.muestras[indice]
            pred = predicciones.get(muestra.id_origen) if split == "test" else None
            if pred and pred["etiqueta_real"] != muestra.etiqueta:
                raise ErrorVisual("La etiqueta real difiere de la predicción registrada.")
            esperadas.append((por_origen[muestra.id_origen].id, split,
                              pred["clase_predicha"] if pred else None,
                              pred["probabilidad_predicha"] if pred else None))

    existente = sesion.scalar(select(ModeloVisual).where(ModeloVisual.version == version))
    if existente:
        if (existente.dataset_id, existente.manifiesto_sha256, existente.artefacto_sha256,
            existente.metadatos_json) != (dataset.id, particion.manifiesto_sha256,
                                           metadatos["modelo_sha256"], metadatos_json):
            raise ErrorVisual("La versión del modelo ya existe con otro contenido.")
        actuales = sesion.execute(select(MuestraModeloVisual.imagen_id, MuestraModeloVisual.split,
            MuestraModeloVisual.clase_predicha, MuestraModeloVisual.probabilidad)
            .where(MuestraModeloVisual.modelo_id == existente.id)).all()
        if sorted(actuales) != sorted(esperadas):
            raise ErrorVisual("La evidencia del modelo persistido está incompleta o alterada.")
        return existente, False

    modelo = ModeloVisual(dataset_id=dataset.id, version=version,
                          manifiesto_sha256=particion.manifiesto_sha256,
                          artefacto_sha256=metadatos["modelo_sha256"],
                          artefacto_clave=f"semana08/{artefacto.name}",
                          metadatos_json=metadatos_json)
    sesion.add(modelo)
    sesion.flush()
    sesion.add_all([
        MuestraModeloVisual(modelo_id=modelo.id, dataset_id=dataset.id, imagen_id=imagen_id,
                            split=split, clase_predicha=clase, probabilidad=probabilidad)
        for imagen_id, split, clase, probabilidad in esperadas
    ])
    sesion.flush()
    return modelo, True
