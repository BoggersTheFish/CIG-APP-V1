"""Tests for monitoring metrics."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig.monitoring import collect_metrics


def test_collect_metrics():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a", activation=0.8)
    kg.add_node("b", activation=0.2)
    kg.add_edge(1, 2, "relates", 1.0)
    m = collect_metrics(kg, None)
    assert m["node_count"] == 2
    assert m["edge_count"] == 1
    assert m["activation_mean"] == 0.5
    assert m["activation_max"] == 0.8
    assert m["activation_min"] == 0.2
    assert m["hypotheses_count"] == 0
    result = {"cig": {"hypotheses": [{"from": 1, "to": 2}]}, "cycles": [{}]}
    m2 = collect_metrics(kg, result)
    assert m2["hypotheses_count"] == 1
    assert m2["cycles_count"] == 1
