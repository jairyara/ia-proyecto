"""Sistema Inteligente para Logística (Proyecto 8).

Arquitectura modular del sistema:
- `src.comun`: Utilidades de cálculo geoespacial (Haversine) y clientes de red con tolerancia a fallos.
- `src.datos`: Generación sintética y extracción curada de datasets públicos (Amazon Last Mile ALMRRC 2021).
- `src.modelado`: Modelos predictivos supervisados y evaluación de riesgo de retraso.
- `src.clasificacion`: Clasificador simbólico y mapeo de taxonomía de IA para requerimientos logísticos.
- `src.busqueda`: Búsqueda heurística A*, líneas base no informadas (Dijkstra/BFS) y replanificación dinámica de rutas.
- `src.vision`: Contratos y partición del piloto visual de paquetes (Semana 08),
  más soporte de la escena didáctica de Semana 09.

Entradas semanales de visión que viven directamente en `src/`:
- `src.semana08_reconocimiento`: MLP, evidencia persistente y ontología.
- `src.semana09_vision`: Canny, Otsu y regiones sobre una escena sintética.
- `src.semana10_texturas`: regiones, histograma de intensidad y LBP sobre
  150 imágenes auditadas; genera descriptores 53D y evidencia visual, sin clasificar.

El mapa de archivos, integraciones y límites de Semanas 08–10 está en
`src/vision/__init__.py`. Estas entradas no se importan desde aquí para evitar
ejecutar dependencias visuales al usar otros módulos del proyecto.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.busqueda import (
        GrafoEntregas,
        Parada,
        ResultadoBusqueda,
        ResultadoReplanificacion,
        a_estrella,
        bfs,
        dijkstra,
        heuristica_haversine_km,
        heuristica_haversine_segundos,
        heuristica_manhattan,
        replanificar_ruta,
    )
    from src.clasificacion import (
        CATEGORIES,
        Category,
        Classification,
        Requirement,
        classify_requirement,
        load_requirements,
    )
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
    "GrafoEntregas",
    "Parada",
    "ResultadoBusqueda",
    "ResultadoReplanificacion",
    "a_estrella",
    "heuristica_haversine_km",
    "heuristica_haversine_segundos",
    "heuristica_manhattan",
    "dijkstra",
    "bfs",
    "replanificar_ruta",
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
    if name in {
        "GrafoEntregas",
        "Parada",
        "ResultadoBusqueda",
        "ResultadoReplanificacion",
        "a_estrella",
        "heuristica_haversine_km",
        "heuristica_haversine_segundos",
        "heuristica_manhattan",
        "dijkstra",
        "bfs",
        "replanificar_ruta",
    }:
        import src.busqueda as busqueda
        return getattr(busqueda, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
