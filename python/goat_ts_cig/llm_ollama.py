"""Optional Ollama HTTP API adapter for local LLM (hypothesis phrasing, query expansion)."""
from __future__ import annotations

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
