"""
Autonomous exploration: multi-cycle query generation, optional web search, ingest, TS propagation.
"""
from __future__ import annotations

import os
import yaml


def _load_config(config_path: str | None) -> dict:
    if config_path is None:
        config_path = "config.yaml"
    if not os.path.isfile(config_path):
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    try:
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def check_online_available(config: dict) -> tuple[bool, str]:
    """
    Return (True, message) if online search is available; (False, reason) otherwise.
    Checks config online.enabled and search module availability.
    """
    online = config.get("online") or {}
    if not online.get("enabled", False):
        return False, "Online search is disabled in config (online.enabled)."
    try:
        from goat_ts_cig.search_fetcher import SEARCH_AVAILABLE
        if not SEARCH_AVAILABLE:
            return False, "Search dependencies not installed (requests/beautifulsoup4 or duckduckgo-search)."
    except Exception:
        return False, "Search module not available."
    return True, "Online search available."


def generate_next_queries(
    kg,
    seed_label: str,
    cycle_index: int,
    max_queries: int = 3,
    config: dict | None = None,
) -> list[str]:
    """
    Heuristic query generator for autonomous loop. Cycle 0 returns [seed_label].
    Later cycles return top activation node labels (up to max_queries).
    """
    if cycle_index == 0:
        return [seed_label]
    data = kg.to_json()
    nodes = sorted(
        data.get("nodes", []),
        key=lambda n: n.get("activation", 0.0),
        reverse=True,
    )
    queries: list[str] = []
    for n in nodes:
        label = (n.get("label") or "").strip()
        if label and label != seed_label and label not in queries:
            queries.append(label)
            if len(queries) >= max_queries:
                break
    if not queries:
        queries = [seed_label]
    return queries[:max_queries]


def run_autonomous_explore(
    seed_query: str,
    config_path: str | None = None,
    config: dict | None = None,
    max_cycles: int = 5,
    max_queries_per_cycle: int = 3,
    online_override: bool | None = None,
) -> dict:
    """
    Run autonomous exploration: multiple cycles of query generation, optional web search,
    ingest into KG, and TS propagation. Returns same structure as run_pipeline plus "cycles" list.
    """
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.main import run_pipeline
    from goat_ts_cig.search_fetcher import SEARCH_AVAILABLE, search_web

    if config is None:
        config = _load_config(config_path)
    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    try:
        kg = KnowledgeGraph(db_path)
    except Exception as e:
        return {"error": f"Failed to open graph at {db_path}: {e}", "config": config}

    online_cfg = config.get("online") or {}
    use_online = online_cfg.get("enabled", False) and SEARCH_AVAILABLE
    if online_override is not None:
        use_online = online_override
    max_requests = online_cfg.get("max_requests_per_run", 30)
    timeout_seconds = online_cfg.get("timeout_seconds", 10)

    total_requests = 0
    cycles_log: list[dict] = []

    for cycle in range(max_cycles):
        queries = generate_next_queries(
            kg, seed_query, cycle, max_queries_per_cycle, config
        )
        ingested_count = 0
        if use_online:
            for q in queries:
                if total_requests >= max_requests:
                    break
                results = search_web(q, max_results=5, timeout_seconds=timeout_seconds)
                for r in results:
                    text = (r.get("snippet") or r.get("body") or r.get("title") or "").strip()
                    if text:
                        kg.ingest_text(text)
                        ingested_count += 1
                total_requests += 1
        cycles_log.append({"queries": queries, "ingested_count": ingested_count})

        result = run_pipeline(
            seed_query,
            config_path=config_path,
            config=config,
            kg=kg,
        )
        if result.get("error"):
            result["cycles"] = cycles_log
            return result

    result["cycles"] = cycles_log
    return result
