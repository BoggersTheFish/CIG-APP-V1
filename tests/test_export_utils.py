"""Tests for export_utils (Steps 72, 74)."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_export_graph_csv():
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.export_utils import export_graph_csv
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    with tempfile.TemporaryDirectory() as d:
        paths = export_graph_csv(kg, d)
        assert len(paths) == 2
        assert os.path.isfile(paths[0])
        assert os.path.isfile(paths[1])
        with open(paths[0], encoding="utf-8") as f:
            lines = f.readlines()
        assert "id" in lines[0]
        assert "1" in lines[1] or "2" in lines[1]
        with open(paths[1], encoding="utf-8") as f:
            lines = f.readlines()
        assert "from_id" in lines[0]


def test_export_cig_json():
    from goat_ts_cig.export_utils import export_cig_json
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        export_cig_json({"seed": "AI", "node_id": 1}, path)
        assert os.path.isfile(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["seed"] == "AI"
        assert data["node_id"] == 1
    finally:
        if os.path.isfile(path):
            os.remove(path)
