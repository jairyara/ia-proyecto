# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Integra datos Amazon, distancia euclidiana, reglas simbólicas y AFD POD."""

from __future__ import annotations

from src.representaciones.automata import SECUENCIAS_DEMOSTRACION, validar_entrega
from src.representaciones.numerica import (
    CAMPOS_VECTOR,
    calcular_estadisticas,
    cargar_dataset,
    evaluar_vector,
    perfiles_demostracion,
    vector_desde_fila,
)
from src.representaciones.simbolica import (
    REGLAS_REPRESENTACION,
    construir_umbrales,
    evaluar_reglas,
    vector_a_hechos,
)


def contexto_dataset() -> dict:
    """Resume fuente, estadísticas, perfiles y distribución de hechos."""
    datos = cargar_dataset()
    estadisticas = calcular_estadisticas(datos)
    umbrales = construir_umbrales(estadisticas)
    indicadores = datos.loc[:, list(CAMPOS_VECTOR)].gt(estadisticas["q3"])
    distribucion = indicadores.sum(axis=1).value_counts().sort_index()
    return {
        "fuente": {
            "nombre": "Amazon Last Mile Routing Challenge 2021",
            "archivo": "data/amazon_pedidos.csv",
            "tipo": "datos reales curados",
            "total_registros": int(len(datos)),
            "total_columnas": int(len(datos.columns)),
            "rutas": int(datos["route_id"].nunique()),
            "nulos_en_variables": int(datos[list(CAMPOS_VECTOR)].isna().sum().sum()),
        },
        "estadisticas": estadisticas,
        "umbrales": [item.como_dict() for item in umbrales],
        "distribucion_hechos": [
            {"cantidad_hechos": int(cantidad), "registros": int(registros)}
            for cantidad, registros in distribucion.items()
        ],
        "reglas": [
            {
                "accion": regla.accion,
                "premisas": list(regla.premisas),
                "descripcion": regla.descripcion,
                "origen": "regla_didactica_del_proyecto",
            }
            for regla in REGLAS_REPRESENTACION
        ],
        "perfiles": perfiles_demostracion(datos, estadisticas),
        "algoritmos": {
            "numerico": "Distancia euclidiana cruda y normalizada por IQR",
            "simbolico": "Contención de conjuntos con issubset",
            "secuencial": "Autómata Finito Determinista",
            "entrenamiento": "No aplica",
        },
    }


def evaluar_parada(pedido_id: str, secuencia_pod: str = "AVF") -> dict:
    """Evalúa una parada real con las tres representaciones."""
    datos = cargar_dataset()
    coincidencias = datos.loc[datos["pedido_id"] == pedido_id]
    if coincidencias.empty:
        raise ValueError(f"No existe el pedido Amazon: {pedido_id}")
    fila = coincidencias.iloc[0]
    estadisticas = calcular_estadisticas(datos)
    vector = vector_desde_fila(fila)
    numerica = evaluar_vector(vector, estadisticas)
    umbrales = construir_umbrales(estadisticas)
    hechos_detalle = vector_a_hechos(vector, umbrales)
    hechos = [item["hecho"] for item in hechos_detalle]
    reglas = evaluar_reglas(hechos)
    return {
        "pedido": {
            "pedido_id": str(fila["pedido_id"]),
            "route_id": str(fila["route_id"]),
            "station_code": str(fila["station_code"]),
        },
        "numerica": numerica,
        "simbolica": {
            "hechos": hechos,
            "hechos_detalle": hechos_detalle,
            "reglas_activadas": reglas["activadas"],
            "reglas_parciales": reglas["parciales"],
        },
        "automata_pod": validar_entrega(secuencia_pod),
        "procedencia": {
            "vector": "fila real de data/amazon_pedidos.csv",
            "referencia": "mediana de 14.411 registros",
            "escala": "IQR de 14.411 registros",
            "hechos": "comparación estricta con P75 del dataset",
            "reglas": "decisiones didácticas del proyecto",
            "secuencia_pod": "escenario controlado; Amazon no registra eventos A/V/F/C",
        },
    }


def evaluaciones_pod() -> list[dict]:
    """Ejecuta las cuatro secuencias controladas del protocolo POD."""
    return [validar_entrega(secuencia) for secuencia in SECUENCIAS_DEMOSTRACION]
