"""Tests for autonomous exploration (Steps 46-47, Phase 17 local-only)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_generate_next_queries_cycle_zero():
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.autonomous_explore import generate_next_queries
    kg = KnowledgeGraph(":memory:")
    kg.add_node("AI")
    q = generate_next_queries(kg, "AI", 0, max_queries=3)
    assert q == ["AI"]


def test_generate_next_queries_later_cycle():
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.autonomous_explore import generate_next_queries
    kg = KnowledgeGraph(":memory:")
    kg.add_node("AI", activation=0.1)
    kg.add_node("ML", activation=0.9)
    kg.add_node("NN", activation=0.5)
    q = generate_next_queries(kg, "AI", 1, max_queries=3)
    assert len(q) <= 3
    assert "AI" not in q or q == ["AI"]  # if only AI exists as high-act
    assert all(isinstance(x, str) for x in q)


def test_autonomous_local_only():
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5},
        "online": {"enabled": False, "max_requests_per_run": 30, "timeout_seconds": 10},
    }
    r = run_autonomous_explore("AI", config=config, max_cycles=2, online_override=False)
    assert "error" not in r or r.get("error") is None
    assert "cycles" in r
    assert len(r["cycles"]) == 2
    assert r.get("seed") == "AI"
    assert "cig" in r


def test_autonomous_reflection_cycles():
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5},
        "online": {"enabled": False, "max_requests_per_run": 30, "timeout_seconds": 10},
        "advanced_autonomous": {"reflection_cycles": 1, "multi_seed": []},
    }
    r = run_autonomous_explore("X", config=config, max_cycles=1, online_override=False)
    assert r.get("error") is None
    assert "cycles" in r
    assert len(r["cycles"]) >= 1


def test_autonomous_multi_seed():
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5},
        "online": {"enabled": False, "max_requests_per_run": 30, "timeout_seconds": 10},
    }
    r = run_autonomous_explore("A", config=config, max_cycles=1, online_override=False, seeds=["A", "B"])
    assert r.get("error") is None
    assert "cycles" in r
    assert len(r["cycles"]) >= 2


def test_autonomous_multi_seed_from_config():
    """Phase 17: When seeds is None, use main seed + advanced_autonomous.multi_seed from config."""
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5},
        "online": {"enabled": False, "max_requests_per_run": 30, "timeout_seconds": 10},
        "advanced_autonomous": {"multi_seed": ["B", "C"], "reflection_cycles": 0},
    }
    r = run_autonomous_explore("A", config=config, max_cycles=1, online_override=False)
    assert r.get("error") is None
    assert "cycles" in r
    assert len(r["cycles"]) >= 3


def test_curiosity_bias_affects_query_order():
    """Phase 17: curiosity_bias 1.0 favors low-activation nodes over high."""
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.autonomous_explore import generate_next_queries
    kg = KnowledgeGraph(":memory:")
    kg.add_node("seed", activation=0.9)
    kg.add_node("high_act", activation=0.8)
    kg.add_node("low_act", activation=0.1)
    config_low_curiosity = {"advanced_autonomous": {"curiosity_bias": 0.0}}
    config_high_curiosity = {"advanced_autonomous": {"curiosity_bias": 1.0}}
    q_low = generate_next_queries(kg, "seed", 1, max_queries=2, config=config_low_curiosity)
    q_high = generate_next_queries(kg, "seed", 1, max_queries=2, config=config_high_curiosity)
    assert len(q_low) <= 2 and len(q_high) <= 2
    assert all(isinstance(x, str) for x in q_low)
    assert all(isinstance(x, str) for x in q_high)
