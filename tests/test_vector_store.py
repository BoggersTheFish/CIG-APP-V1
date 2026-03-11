"""Tests for vector_store abstraction."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.vector_store import VectorStore, VECTOR_DIM

# 384-d placeholder
VEC = [0.1] * VECTOR_DIM


def test_vector_store_memory():
    vs = VectorStore(backend="memory")
    vs.add(1, VEC)
    vs.add(2, [x + 0.01 for x in VEC])
    out = vs.query(VEC, limit=2)
    assert len(out) >= 1
    assert out[0][0] == 1


def test_vector_store_add_query_dim_check():
    vs = VectorStore(backend="memory")
    assert vs.add(1, [0.0] * 10) is False
    assert vs.query([0.0] * 10, limit=1) == []
