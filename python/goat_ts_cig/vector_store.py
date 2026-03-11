"""
Vector store abstraction for hybrid graph-vector reasoning.
Backends: sqlite_vss (KnowledgeGraph), memory (in-memory dict), faiss (optional).
Used by hypothesis_engine and (future) TS propagation for similarity-augmented activation.
"""
from __future__ import annotations

from typing import Any

try:
    from goat_ts_cig.embeddings import EMBEDDING_DIM as VECTOR_DIM
except Exception:
    VECTOR_DIM = 384  # all-MiniLM-L6-v2


class VectorStore:
    """
    Unified interface for adding and querying node vectors.
    Backend can be "sqlite_vss" (uses KnowledgeGraph), "memory", or "faiss".
    """

    def __init__(self, backend: str = "memory", kg: Any = None, **kwargs: Any):
        self.backend = backend
        self._kg = kg
        self._memory: dict[int, list[float]] = {}
        self._faiss_index = None
        self._faiss_id_list: list[int] = []
        if backend == "faiss":
            self._init_faiss(**kwargs)

    def _init_faiss(self, **kwargs: Any) -> None:
        try:
            import faiss
            self._faiss_index = faiss.IndexFlatL2(VECTOR_DIM)
            self._faiss_id_list = []
        except Exception:
            self._faiss_index = None

    def add(self, node_id: int, embedding: list[float]) -> bool:
        """Store vector for node_id. Returns True if stored."""
        if len(embedding) != VECTOR_DIM:
            return False
        if self.backend == "memory":
            self._memory[node_id] = list(embedding)
            return True
        if self.backend == "sqlite_vss" and self._kg is not None and hasattr(self._kg, "add_vector"):
            self._kg.add_vector(node_id, embedding)
            return True
        if self.backend == "faiss" and self._faiss_index is not None:
            try:
                import faiss
                import numpy as np
                vec = np.array([embedding], dtype="float32")
                self._faiss_index.add(vec)
                self._faiss_id_list.append(node_id)
                return True
            except Exception:
                return False
        return False

    def query(self, embedding: list[float], limit: int = 10) -> list[tuple[int, float]]:
        """
        Return list of (node_id, score_or_distance).
        For sqlite_vss/faiss: distance (lower = more similar).
        We return (node_id, distance); callers can convert to similarity if needed.
        """
        if len(embedding) != VECTOR_DIM:
            return []
        if self.backend == "memory":
            import math
            scores: list[tuple[float, int]] = []
            for nid, vec in self._memory.items():
                dot = sum(a * b for a, b in zip(embedding, vec))
                na = math.sqrt(sum(a * a for a in embedding))
                nb = math.sqrt(sum(b * b for b in vec))
                if na > 0 and nb > 0:
                    sim = dot / (na * nb)
                    scores.append((1.0 - sim, nid))  # distance = 1 - sim
            scores.sort(key=lambda x: x[0])
            return [(nid, d) for d, nid in scores[:limit]]
        if self.backend == "sqlite_vss" and self._kg is not None and hasattr(self._kg, "query_similar_vectors"):
            pairs = self._kg.query_similar_vectors(embedding, limit=limit)
            return [(nid, float(dist)) for nid, dist in pairs]
        if self.backend == "faiss" and self._faiss_index is not None and self._faiss_id_list:
            try:
                import faiss
                import numpy as np
                vec = np.array([embedding], dtype="float32")
                D, I = self._faiss_index.search(vec, min(limit, len(self._faiss_id_list)))
                out = []
                for j, idx in enumerate(I[0]):
                    if 0 <= idx < len(self._faiss_id_list):
                        out.append((self._faiss_id_list[idx], float(D[0][j])))
                return out
            except Exception:
                return []
        return []


def get_vector_store(backend: str, kg: Any = None, config: dict | None = None) -> VectorStore:
    """Factory: return a VectorStore for the given backend and config."""
    config = config or {}
    if backend == "sqlite_vss":
        return VectorStore(backend="sqlite_vss", kg=kg)
    if backend == "faiss":
        return VectorStore(backend="faiss")
    return VectorStore(backend="memory")
