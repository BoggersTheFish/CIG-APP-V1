"""Tests for research_agent (goal-conditioned exploration)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.research_agent import _decompose_goal_ollama, run_research_agent


def test_decompose_goal_fallback():
    # When Ollama not enabled or fails, returns [goal]
    config = {"llm_ollama": {"enabled": False}}
    seeds = _decompose_goal_ollama("machine learning", config)
    assert seeds == ["machine learning"]


def test_run_research_agent_local():
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2},
        "online": {"enabled": False},
        "llm_ollama": {"enabled": False},
    }
    result = run_research_agent("AI", config=config, max_cycles=2, summarize=False)
    assert "goal" in result and result["goal"] == "AI"
    assert "seeds_used" in result
    assert "cycles" in result
    assert result.get("error") is None or "summary" in result
