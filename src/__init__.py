"""Sistema Inteligente para Logística (Proyecto 8).

Arquitectura modular del sistema:
- `src.comun`: Utilidades de cálculo geoespacial (Haversine) y clientes de red con tolerancia a fallos.
- `src.datos`: Generación sintética y extracción curada de datasets públicos (Amazon Last Mile ALMRRC 2021).
- `src.modelado`: Modelos predictivos supervisados y evaluación de riesgo de retraso.
- `src.clasificacion`: Clasificador simbólico y mapeo de taxonomía de IA para requerimientos logísticos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.comun import descargar_json, haversine_km
    from src.datos import (
        construir_grafos_muestra,
        generar_pedidos,
        guardar_pedidos,
        procesar_paradas_a_dataframe,
        seleccionar_rutas_estratificadas,
    )
    from src.modelado import (
        cargar_pedidos,
        construir_pipelines,
        entrenar_y_evaluar,
        guardar_artefactos,
    )
    from src.clasificacion import (
        CATEGORIES,
        Category,
        Classification,
        Requirement,
        classify_requirement,
        load_requirements,
    )

__all__ = [
    "haversine_km",
    "descargar_json",
    "generar_pedidos",
    "guardar_pedidos",
    "seleccionar_rutas_estratificadas",
    "procesar_paradas_a_dataframe",
    "construir_grafos_muestra",
    "cargar_pedidos",
    "construir_pipelines",
    "entrenar_y_evaluar",
    "guardar_artefactos",
    "CATEGORIES",
    "Category",
    "Classification",
    "Requirement",
    "classify_requirement",
    "load_requirements",
]


def __getattr__(name: str):
    if name in {"haversine_km", "descargar_json"}:
        import src.comun as comun
        return getattr(comun, name)
    if name in {
        "generar_pedidos",
        "guardar_pedidos",
        "seleccionar_rutas_estratificadas",
        "procesar_paradas_a_dataframe",
        "construir_grafos_muestra",
    }:
        import src.datos as datos
        return getattr(datos, name)
    if name in {
        "cargar_pedidos",
        "construir_pipelines",
        "entrenar_y_evaluar",
        "guardar_artefactos",
    }:
        import src.modelado as modelado
        return getattr(modelado, name)
    if name in {
        "CATEGORIES",
        "Category",
        "Classification",
        "Requirement",
        "classify_requirement",
        "load_requirements",
    }:
        import src.clasificacion as clasificacion
        return getattr(clasificacion, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
