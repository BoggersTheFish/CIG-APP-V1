"""Tests for GraphML export (Step 9)."""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_to_graphml():
    try:
        import networkx as nx
    except ImportError:
        import pytest
        pytest.skip("networkx not installed")
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.export_utils import to_graphml
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    with tempfile.NamedTemporaryFile(suffix=".graphml", delete=False) as g:
        gml_path = g.name
    try:
        kg = KnowledgeGraph(db_path)
        kg.add_node("a")
        kg.add_node("b")
        kg.add_edge(1, 2, "relates", 1.0)
        out = to_graphml(kg, gml_path)
        kg.close()
        assert out == gml_path
        assert os.path.isfile(gml_path)
        G = nx.read_graphml(gml_path)
        assert G.number_of_nodes() == 2
        assert G.number_of_edges() == 1
    finally:
        if os.path.isfile(db_path):
            os.remove(db_path)
        if os.path.isfile(gml_path):
            os.remove(gml_path)
