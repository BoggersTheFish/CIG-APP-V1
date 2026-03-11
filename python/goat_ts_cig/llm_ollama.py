"""Optional Ollama HTTP API adapter for local LLM (hypothesis phrasing, query expansion).
Phase 14, Steps 63-67: adapter class, env support (OLLAMA_HOST, OLLAMA_MODEL).
"""
from __future__ import annotations

import os
from typing import Any

import requests


def generate(prompt: str, host: str, model: str, timeout: int = 60) -> str:
    """Call Ollama /api/generate; return response text or error message string."""
    url = host.rstrip("/") + "/api/generate"
    try:
        r = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("response", "")
    except Exception as e:
        return f"[Ollama error: {e}]"


class OllamaAdapter:
    """Phase 14: Adapter for Ollama API; host/model from config or env (OLLAMA_HOST, OLLAMA_MODEL)."""

    def __init__(self, config: dict[str, Any] | None = None):
        config = config or {}
        ollama = config.get("llm_ollama") or {}
        self.host = (
            os.environ.get("OLLAMA_HOST")
            or os.environ.get("CIG_OLLAMA_HOST")
            or ollama.get("host", "http://127.0.0.1:11434")
        ).strip()
        self.model = (
            os.environ.get("OLLAMA_MODEL")
            or os.environ.get("CIG_OLLAMA_MODEL")
            or ollama.get("model", "llama2")
        ).strip() or "llama2"
        self.timeout = int(ollama.get("timeout", 60))

    def generate_hypothesis(self, prompt: str, timeout: int | None = None) -> str:
        """Generate text via Ollama; use for hypothesis phrasing or query expansion."""
        return generate(
            prompt,
            self.host,
            self.model,
            timeout=timeout if timeout is not None else self.timeout,
        )
