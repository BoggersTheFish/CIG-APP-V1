"""
Lightweight embeddings via sentence-transformers (all-MiniLM-L6-v2).
Optional: only used when advanced.embeddings.enabled and sentence_transformers installed.
"""
from __future__ import annotations

_model = None


def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(text: str) -> list[float]:
    """
    Embed a single text string. Returns a list of floats (vector).
    Raises if sentence_transformers is not installed or model fails to load.
    """
    model = _load_model()
    return model.encode(text, convert_to_numpy=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts. Returns list of vectors."""
    if not texts:
        return []
    model = _load_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def available() -> bool:
    """Return True if sentence_transformers and the default model can be used."""
    try:
        import importlib.util
        if importlib.util.find_spec("sentence_transformers") is None:
            return False
        _load_model()
        return True
    except Exception:
        return False


def embed_safe(text: str) -> list[float] | None:
    """Embed a single text. Returns 384-d vector or None if embeddings unavailable."""
    try:
        if not available():
            return None
        return embed(text)
    except Exception:
        return None


def embed_batch_safe(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts. Returns list of vectors (or empty list if unavailable)."""
    try:
        if not texts or not available():
            return []
        return embed_batch(texts)
    except Exception:
        return []


# Dimension for all-MiniLM-L6-v2; required for sqlite-vss in this codebase
EMBEDDING_DIM = 384
