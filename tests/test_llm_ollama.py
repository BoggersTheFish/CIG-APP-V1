"""Tests for llm_ollama (Phase 14, Steps 63, 67). Mock Ollama; ensure fallback to non-LLM."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_ollama_generate_mock(monkeypatch):
    from goat_ts_cig import llm_ollama

    def fake_post(*args, **kwargs):
        class R:
            status_code = 200
            def json(self):
                return {"response": "mock reply"}
            def raise_for_status(self):
                pass
        return R()

    monkeypatch.setattr("goat_ts_cig.llm_ollama.requests.post", fake_post)
    out = llm_ollama.generate("hi", "http://localhost:11434", "llama2")
    assert "mock reply" in out


def test_ollama_generate_error_response(monkeypatch):
    from goat_ts_cig import llm_ollama

    def fake_post(*args, **kwargs):
        raise ConnectionError("refused")

    monkeypatch.setattr("goat_ts_cig.llm_ollama.requests.post", fake_post)
    out = llm_ollama.generate("hi", "http://localhost:11434", "llama2")
    assert "[Ollama error:" in out


def test_ollama_adapter_generate_hypothesis(monkeypatch):
    """Phase 14: OllamaAdapter.generate_hypothesis uses config host/model."""
    from goat_ts_cig import llm_ollama

    def fake_post(*args, **kwargs):
        class R:
            status_code = 200
            def json(self):
                return {"response": "adapter reply"}
            def raise_for_status(self):
                pass
        return R()

    monkeypatch.setattr("goat_ts_cig.llm_ollama.requests.post", fake_post)
    adapter = llm_ollama.OllamaAdapter({"llm_ollama": {"host": "http://127.0.0.1:11434", "model": "llama2"}})
    out = adapter.generate_hypothesis("Suggest a link.")
    assert "adapter reply" in out


def test_hypothesis_engine_fallback_non_llm():
    """Phase 14: When use_llm=False or llm_ollama.enabled=False, no Ollama call; stub used if LLM path taken."""
    from goat_ts_cig.hypothesis_engine import generate_hypotheses
    from goat_ts_cig.knowledge_graph import KnowledgeGraph

    kg = KnowledgeGraph(":memory:")
    kg.add_node("a")
    kg.add_node("b")
    kg.add_edge(1, 2, "relates", 1.0)
    config = {"llm": False, "llm_ollama": {"enabled": False}}
    hyps = generate_hypotheses(kg, use_llm=False, config=config)
    # May have hypotheses from tension/similarity; no natural_language from Ollama
    for h in hyps:
        assert "from" in h and "to" in h
    # With use_llm=True but enabled=False, stub is used
    config2 = {"llm": True, "llm_ollama": {"enabled": False}}
    hyps2 = generate_hypotheses(kg, use_llm=True, config=config2)
    for h in hyps2:
        assert "from" in h and "to" in h
        if "natural_language" in h:
            assert "stub" in h["natural_language"].lower() or len(h["natural_language"]) < 50
