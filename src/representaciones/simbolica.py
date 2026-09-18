# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Representación simbólica derivada de las magnitudes numéricas Amazon."""

from __future__ import annotations

from dataclasses import dataclass

from src.representaciones.numerica import CAMPOS_VECTOR, VectorParada


@dataclass(frozen=True)
class UmbralDatos:
    hecho: str
    campo: str
    limite: float
    descripcion: str

    def como_dict(self) -> dict:
        """Serializa el umbral con una única estructura para API y reportes."""
        return {
            "hecho": self.hecho,
            "campo": self.campo,
            "comparador": ">",
            "limite": self.limite,
            "descripcion": self.descripcion,
            "origen": "percentil_75_amazon",
        }


@dataclass(frozen=True)
class ReglaRepresentacion:
    accion: str
    premisas: tuple[str, ...]
    descripcion: str


REGLAS_REPRESENTACION: tuple[ReglaRepresentacion, ...] = (
    ReglaRepresentacion(
        "riesgo_desviacion_operativa",
        ("parada_lejana", "servicio_prolongado"),
        "La distancia alta y la atención prolongada pueden desviar la jornada.",
    ),
    ReglaRepresentacion(
        "reservar_tiempo_descarga",
        ("volumen_alto", "servicio_prolongado"),
        "Reserva una franja de descarga cuando coinciden volumen y servicio altos.",
    ),
    ReglaRepresentacion(
        "revisar_asignacion_vehiculo",
        ("parada_lejana", "volumen_alto"),
        "Revisa la asignación del vehículo para una parada lejana y voluminosa.",
    ),
)


def construir_umbrales(estadisticas: dict) -> tuple[UmbralDatos, ...]:
    """Construye los hechos usando Q3/P75 calculado del dataset real."""
    limites = dict(zip(CAMPOS_VECTOR, estadisticas["q3"]))
    return (
        UmbralDatos("parada_lejana", "distancia_deposito_km", float(limites["distancia_deposito_km"]), "La distancia supera el percentil 75 del dataset."),
        UmbralDatos("volumen_alto", "volumen_total_m3", float(limites["volumen_total_m3"]), "El volumen supera el percentil 75 del dataset."),
        UmbralDatos("servicio_prolongado", "tiempo_servicio_seg", float(limites["tiempo_servicio_seg"]), "El tiempo de servicio supera el percentil 75 del dataset."),
    )


def vector_a_hechos(vector: VectorParada, umbrales: tuple[UmbralDatos, ...]) -> list[dict]:
    """Traduce Numérico → Simbólico y conserva la evidencia cuantitativa."""
    valores = dict(zip(CAMPOS_VECTOR, vector.vector().tolist()))
    return [
        {
            **umbral.como_dict(),
            "valor": float(valores[umbral.campo]),
        }
        for umbral in umbrales
        if valores[umbral.campo] > umbral.limite
    ]


def describir_hecho(hecho: str, umbrales: tuple[UmbralDatos, ...]) -> dict:
    """Traduce Simbólico → Numérico mostrando el umbral que creó el hecho."""
    for umbral in umbrales:
        if umbral.hecho == hecho:
            return umbral.como_dict()
    raise KeyError(f"Hecho no derivado por Semana 07: {hecho}")


def evaluar_reglas(hechos: set[str] | list[str]) -> dict:
    """Evalúa reglas mediante contención de conjuntos y explica faltantes."""
    conocidos = set(hechos)
    activadas = []
    parciales = []
    for regla in REGLAS_REPRESENTACION:
        premisas = set(regla.premisas)
        base = {
            "accion": regla.accion,
            "descripcion": regla.descripcion,
            "premisas": sorted(premisas),
            "origen": "regla_didactica_del_proyecto",
        }
        if premisas.issubset(conocidos):
            activadas.append(base)
        elif premisas & conocidos:
            parciales.append(
                {
                    **base,
                    "cumplidas": sorted(premisas & conocidos),
                    "faltantes": sorted(premisas - conocidos),
                }
            )
    return {"activadas": activadas, "parciales": parciales}
