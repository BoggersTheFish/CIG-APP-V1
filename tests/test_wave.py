"""Tests for wave/TS (when Rust extension available)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

import pytest

try:
    from bindings.rust_bindings import goat_ts_core
    HAS_RUST = hasattr(goat_ts_core, "PyGraph")
except Exception:
    HAS_RUST = False


@pytest.mark.skipif(not HAS_RUST, reason="Rust extension not built")
def test_pygraph_propagate():
    PyGraph = goat_ts_core.PyGraph
    g = PyGraph()
    g.add_node("a")
    g.add_node("b")
    g.add_node("c")
    g.add_edge(0, 1, "relates", 1.0)
    g.add_edge(1, 2, "relates", 1.0)
    g.full_ts_cycle(0, ticks=5, decay=0.9, activation_threshold=0.5)
    assert g.get_node_activation(0) is not None
    assert g.get_node_activation(1) is not None
    assert g.compute_influence() > 0
