"""Tests for llm_ollama (Steps 63, 67)."""
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
