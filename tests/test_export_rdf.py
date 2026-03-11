"""Tests for RDF and Neo4j Cypher export."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig.export_utils import to_rdf, to_neo4j_cypher


def test_to_rdf_turtle():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("hello")
    kg.add_node("world")
    kg.add_edge(1, 2, "relates", 1.0)
    with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as f:
        path = f.name
    try:
        to_rdf(kg, path, format="turtle")
        assert os.path.isfile(path)
        content = open(path, encoding="utf-8").read()
        assert "cig:" in content or "node/1" in content
        assert "hello" in content
    finally:
        if os.path.isfile(path):
            os.remove(path)


def test_to_neo4j_cypher():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    with tempfile.NamedTemporaryFile(suffix=".cypher", delete=False) as f:
        path = f.name
    try:
        to_neo4j_cypher(kg, path)
        assert os.path.isfile(path)
        content = open(path, encoding="utf-8").read()
        assert "CREATE" in content
        assert "RELATES" in content or "relates" in content
    finally:
        if os.path.isfile(path):
            os.remove(path)
