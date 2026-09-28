from pathlib import Path

import networkx as nx
import pytest

from src.vision.ontologia import construir_ontologia, exportar_graphml


def test_ontologia_del_dominio_y_ejemplo_exportado(tmp_path: Path):
    grafo = construir_ontologia({"id_origen": "PKG-001_side", "clase_predicha": "danado"})
    assert grafo.number_of_edges() == 13
    assert grafo["prediccion:PKG-001_side"]["paquete_danado"]["rel"] == "asigna_clase"
    destino = tmp_path / "ontologia_logistica.graphml"
    exportar_graphml(grafo, destino)
    cargado = nx.read_graphml(destino)
    assert cargado.number_of_edges() == 13
    assert cargado["imagen:PKG-001_side"]["prediccion:PKG-001_side"]["rel"] == "genera"


def test_ontologia_rechaza_clases_ajenas():
    with pytest.raises(ValueError):
        construir_ontologia({"id_origen": "1", "clase_predicha": "despachado"})
