"""Tests for search_fetcher (Step 44)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_search_web_returns_list():
    from goat_ts_cig.search_fetcher import search_web
    r = search_web("test query", max_results=2)
    assert isinstance(r, list)
    for item in r:
        assert isinstance(item, dict)
        assert "title" in item or "url" in item or "snippet" in item


def test_search_web_structure():
    from goat_ts_cig.search_fetcher import search_web, SEARCH_AVAILABLE
    r = search_web("python", max_results=1)
    if SEARCH_AVAILABLE and r:
        assert "title" in r[0]
        assert "snippet" in r[0] or "url" in r[0]
