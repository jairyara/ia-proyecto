# Dashboard · Semana 08 — Reconocimiento, evidencia y ontología
"""Grafo semántico didáctico de inspección; no ejecuta reglas de despacho."""

from pathlib import Path

import networkx as nx


VERSION_GRAFO = "ontologia-logistica-v1"


def construir_ontologia(prediccion: dict | None = None) -> nx.DiGraph:
    grafo = nx.DiGraph(version=VERSION_GRAFO)
    grafo.add_edges_from([
        ("imagen_paquete", "paquete", {"rel": "evidencia_estado"}),
        ("modelo_mlp", "imagen_paquete", {"rel": "analiza"}),
        ("modelo_mlp", "prediccion_inspeccion", {"rel": "produce"}),
        ("prediccion_inspeccion", "paquete_intacto", {"rel": "puede_clasificar_como"}),
        ("prediccion_inspeccion", "paquete_danado", {"rel": "puede_clasificar_como"}),
        ("paquete_intacto", "paquete", {"rel": "es_estado_de"}),
        ("paquete_danado", "paquete", {"rel": "es_estado_de"}),
        ("paquete_danado", "revision_humana", {"rel": "requiere_confirmacion"}),
        ("paquete_intacto", "revision_humana", {"rel": "requiere_confirmacion"}),
        ("revision_humana", "decision_despacho", {"rel": "fundamenta"}),
    ])
    if prediccion is not None:
        id_origen = prediccion["id_origen"]
        clase = prediccion["clase_predicha"]
        if not isinstance(id_origen, str) or not id_origen or clase not in ("danado", "intacto"):
            raise ValueError("Predicción no válida para la ontología logística.")
        imagen = f"imagen:{id_origen}"
        evento = f"prediccion:{id_origen}"
        grafo.add_edge(imagen, evento, rel="genera")
        grafo.add_edge(evento, f"paquete_{clase}", rel="asigna_clase")
        grafo.add_edge(evento, "revision_humana", rel="requiere_confirmacion")
    return grafo


def exportar_graphml(grafo: nx.DiGraph, destino: Path) -> None:
    """Exporta el grafo final, incluida la predicción concreta; nunca antes."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(grafo, destino)
    cargado = nx.read_graphml(destino)
    if set(cargado.edges(data="rel")) != set(grafo.edges(data="rel")):
        raise RuntimeError("GraphML no conservó todas las relaciones.")
