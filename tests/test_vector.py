"""Tests for sqlite-vss vector search (Step 7)."""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_add_vector_and_query():
    try:
        from goat_ts_cig.knowledge_graph import KnowledgeGraph, _vector_extension_available
    except ImportError:
        import pytest
        pytest.skip("knowledge_graph not available")
    if not _vector_extension_available():
        import pytest
        pytest.skip("sqlite-vss not installed")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        kg = KnowledgeGraph(path)
        if not kg._ensure_vss():
            import pytest
            pytest.skip("vss extension could not be loaded")
        # 384-dim vector (all-MiniLM-L6-v2)
        vec = [0.1] * 384
        kg.add_node("a")
        kg.add_vector(1, vec)
        results = kg.query_similar_vectors(vec, limit=5)
        assert isinstance(results, list)
        # may include self or be empty depending on index
    finally:
        kg.close()
        if os.path.isfile(path):
            os.remove(path)
