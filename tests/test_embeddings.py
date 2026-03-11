"""Tests for lightweight embeddings (Step 6)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_embed():
    try:
        from goat_ts_cig.embeddings import embed, available
    except ImportError:
        import pytest
        pytest.skip("sentence_transformers not installed")
    if not available():
        import pytest
        pytest.skip("embeddings not available")
    vec = embed("test")
    assert isinstance(vec, list)
    assert len(vec) > 0
    assert all(isinstance(x, (int, float)) for x in vec)


def test_embed_batch():
    try:
        from goat_ts_cig.embeddings import embed_batch, available
    except ImportError:
        import pytest
        pytest.skip("sentence_transformers not installed")
    if not available():
        import pytest
        pytest.skip("embeddings not available")
    vecs = embed_batch(["hello", "world"])
    assert len(vecs) == 2
    assert len(vecs[0]) == len(vecs[1])
    assert len(vecs[0]) > 0
