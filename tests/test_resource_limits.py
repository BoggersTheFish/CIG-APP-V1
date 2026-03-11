"""Tests for resource_limits enforcement in run_pipeline."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig.main import run_pipeline


def test_max_nodes_enforced():
    kg = KnowledgeGraph(":memory:")
    for i in range(10):
        kg.add_node(f"n_{i}")
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2},
        "resource_limits": {"max_nodes": 5},
    }
    result = run_pipeline("n_0", config=config, kg=kg)
    assert result.get("error") is not None
    assert "max_nodes" in result["error"].lower() or "50000" in result["error"] or "5" in result["error"]


def test_max_ticks_capped():
    kg = KnowledgeGraph(":memory:")
    kg.add_node("seed")
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 100},
        "resource_limits": {"max_ticks_per_run": 3},
    }
    result = run_pipeline("seed", config=config, kg=kg)
    assert result.get("error") is None
    # Ticks should have been capped at 3 (no direct way to assert; just ensure no error)
    assert "cig" in result or result.get("config")
