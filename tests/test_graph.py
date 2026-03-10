"""Tests for Knowledge Graph (Steps 6-9)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph


def test_add_node():
    kg = KnowledgeGraph(":memory:")
    nid = kg.add_node("test")
    assert nid == 1
    node = kg.get_node(nid)
    assert node["label"] == "test"
    assert node["activation"] == 0.0
    assert node["state"] == "DORMANT"


def test_add_edge():
    kg = KnowledgeGraph(":memory:")
    a = kg.add_node("a")
    b = kg.add_node("b")
    kg.add_edge(a, b, "relates", 1.0)
    edges = kg.get_all_edges()
    assert len(edges) == 1
    assert edges[0]["from_id"] == a and edges[0]["to_id"] == b


def test_ingest_text():
    kg = KnowledgeGraph(":memory:")
    kg.ingest_text("hello world foo")
    data = kg.to_json()
    assert len(data["nodes"]) >= 3
    assert len(data["edges"]) >= 2


def test_to_json():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("x", activation=0.5)
    kg.add_node("y")
    kg.add_edge(1, 2, "relates", 1.0)
    out = kg.to_json()
    assert "nodes" in out and "edges" in out
    assert len(out["nodes"]) == 2 and len(out["edges"]) == 1
