"""
Lightweight web search for autonomous exploration. Optional; no API key required for DuckDuckGo.
"""
from __future__ import annotations

from typing import Any

SEARCH_AVAILABLE = False
_DDGS = None
_USE_REQUESTS = False
_REQ = None

try:
    from ddgs import DDGS
    _DDGS = DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        _DDGS = DDGS
        SEARCH_AVAILABLE = True
    except ImportError:
        try:
            import requests
            from bs4 import BeautifulSoup  # noqa: F401
            _REQ = requests
            _USE_REQUESTS = True
            SEARCH_AVAILABLE = True
        except ImportError:
            pass


def search_web(
    query: str,
    max_results: int = 5,
    timeout_seconds: int = 10,
) -> list[dict[str, Any]]:
    """
    Return a list of search results: [{"title", "snippet", "url"}, ...].
    Uses DuckDuckGo (no API key). Returns [] if deps unavailable or on error.
    """
    if not SEARCH_AVAILABLE:
        return []
    results: list[dict[str, Any]] = []
    try:
        if _DDGS is not None:
            with _DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", "") or r.get("snippet", ""),
                        "url": r.get("href", "") or r.get("url", ""),
                    })
        elif _USE_REQUESTS and _REQ is not None:
            from urllib.parse import quote_plus
            from bs4 import BeautifulSoup
            url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
            resp = _REQ.get(
                url,
                timeout=timeout_seconds,
                headers={"User-Agent": "CIG-APP/1.0"},
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select(".result__a")[:max_results]:
                title = a.get_text(strip=True) if a else ""
                href = a.get("href", "") if hasattr(a, "get") else ""
                results.append({"title": title, "snippet": "", "url": href})
    except Exception:
        results = []
    return results
