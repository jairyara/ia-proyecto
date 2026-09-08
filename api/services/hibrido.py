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

CONSULTAS_DEMOSTRACION = [
    *CONSULTAS_EJEMPLO,
    "La entrega llegará tarde y está fuera de la ventana horaria pactada",
    "El paquete express es urgente y requiere despacho prioritario",
    "El destinatario está ausente y no responde en la dirección registrada",
    "El paquete frágil requiere embalaje especial y manejo delicado",
    "Un accidente bloqueó la vía y el furgón refrigerado perdió temperatura",
]


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
            "clase_modelo": resultado["clase_modelo"],
            "descripcion": (
                CLASE_DESCRIPCIONES.get(resultado["clase"], "")
                if resultado["aceptada"]
                else "La entrada no aporta evidencia suficiente para asignar una categoría confiable."
            ),
            "aceptada": resultado["aceptada"],
            "motivo_revision": resultado["motivo_revision"],
            "terminos_reconocidos": resultado["terminos_reconocidos"],
            "margen": resultado["margen"],
            "probabilidades": resultado["clases"],
            "factores": resultado["factores"],
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
        "consultas_demostracion": list(CONSULTAS_DEMOSTRACION),
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
