"""Tests for graph_viz (Steps 68, 71)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_export_subgraph_png_graphviz():
    try:
        import graphviz  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("graphviz not installed")
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.graph_viz import export_subgraph_png
    import tempfile
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        try:
            export_subgraph_png(kg, 1, path, depth=1, engine="graphviz")
        except Exception as e:
            if type(e).__name__ == "ExecutableNotFound" or "dot" in str(e).lower() or "PATH" in str(e):
                import pytest
                pytest.skip("Graphviz 'dot' executable not on PATH")
            raise
        assert os.path.isfile(path) or os.path.isfile(path.replace(".png", "") + ".png")
    finally:
        for p in (path, path.replace(".png", "") + ".png"):
            if os.path.isfile(p):
                os.remove(p)


def test_export_subgraph_png_matplotlib():
    try:
        import matplotlib  # noqa: F401
        import networkx  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("matplotlib or networkx not installed")
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.graph_viz import export_subgraph_png
    import tempfile
    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        path = f.name
    try:
        export_subgraph_png(kg, 1, path, depth=1, engine="matplotlib")
        assert os.path.isfile(path)
    finally:
        if os.path.isfile(path):
            os.remove(path)
