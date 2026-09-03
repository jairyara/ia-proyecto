"""Adaptador del sistema híbrido con trazabilidad lista para la UI."""

from __future__ import annotations

from api.schemas.hibrido_dto import ConsultaHibridaRequest
from src.hibrido.sistema import (
    CLASE_DESCRIPCIONES,
    CONSULTAS_EJEMPLO,
    DOCS,
    RULES,
    TRAIN_X,
    TRAIN_Y,
    answer,
)


def responder_consulta(solicitud: ConsultaHibridaRequest) -> dict:
    """Responde la consulta con la triple señal auditada del sistema híbrido."""

    resultado = answer(solicitud.consulta)
    return {
        "consulta": resultado["consulta"],
        "reglas": resultado["reglas_detalle"],
        "evidencia": {
            "documento": resultado["evidencia"],
            "similitud": resultado["similitud"],
        },
        "clasificacion": {
            "clase": resultado["clase"],
            "descripcion": CLASE_DESCRIPCIONES.get(resultado["clase"], ""),
            "probabilidades": resultado["clases"],
        },
    }


def obtener_contexto() -> dict:
    """Expone la configuración del sistema para documentar la interfaz."""

    return {
        "reglas": [
            {
                "accion": regla.accion,
                "palabras": list(regla.palabras),
                "descripcion": regla.descripcion,
            }
            for regla in RULES
        ],
        "clases": [
            {"clase": clase, "descripcion": CLASE_DESCRIPCIONES.get(clase, "")}
            for clase in sorted(set(TRAIN_Y))
        ],
        "consultas_ejemplo": list(CONSULTAS_EJEMPLO),
        "base_conocimiento": {
            "total_documentos": len(DOCS),
            "documentos": list(DOCS),
        },
        "entrenamiento": {
            "total_ejemplos": len(TRAIN_X),
            "ejemplos": [
                {"texto": texto, "clase": clase}
                for texto, clase in zip(TRAIN_X, TRAIN_Y)
            ],
        },
    }
