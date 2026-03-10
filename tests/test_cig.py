"""Tests for CIG generator."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig import cig_generator


def test_idea_map():
    kg = KnowledgeGraph(":memory:")
    a = kg.add_node("concept")
    b = kg.add_node("related")
    kg.add_edge(a, b, "relates", 1.0)
    m = cig_generator.generate_idea_map(kg, a, depth=2)
    assert m["center"]["label"] == "concept"
    assert len(m["related"]) >= 1
    assert any(r["label"] == "related" for r in m["related"])


def test_context_expansion():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    clusters = cig_generator.generate_context_expansion(kg)
    assert len(clusters) >= 1
    assert "total_activation" in clusters[0]


def test_evidence_chain():
    kg = KnowledgeGraph(":memory:")
    a = kg.add_node("a")
    b = kg.add_node("b")
    c = kg.add_node("c")
    kg.add_edge(1, 2, "relates", 1.0)
    kg.add_edge(2, 3, "relates", 1.0)
    path = cig_generator.generate_evidence_chain(kg, 1, 3)
    assert path == [1, 2, 3]
