"""
Autonomous exploration: multi-cycle query generation, optional web search, ingest, TS propagation.
"""
from __future__ import annotations

import os
import time
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
    Heuristic / LLM-backed query generator for autonomous loop.

    - Cycle 0 returns [seed_label].
    - Later cycles return up to max_queries labels.
    - If llm_ollama.enabled + use_for_autonomous: delegate to local LLM.
    - Otherwise: use activation-based heuristic, optionally biased by
      advanced_autonomous.curiosity_bias (0.0–1.0).
    """
    if cycle_index == 0:
        return [seed_label]

    cfg = config or {}
    ollama_cfg = (cfg.get("llm_ollama") or {})
    if ollama_cfg.get("enabled") and ollama_cfg.get("use_for_autonomous"):
        try:
            from goat_ts_cig.llm_ollama import generate as ollama_generate
            prompt = (
                f"Suggest {max_queries} short search queries (one per line) "
                f"to expand knowledge about: {seed_label}. "
                "Only output the queries, one per line."
            )
            out = ollama_generate(
                prompt,
                ollama_cfg.get("host", "http://127.0.0.1:11434"),
                ollama_cfg.get("model", "llama2"),
                timeout=30,
            )
            lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.strip().startswith("[")]
            if lines:
                return lines[:max_queries]
        except Exception:
            # Fall back to heuristic if the LLM call fails.
            pass

    data = kg.to_json()
    nodes = data.get("nodes", [])

    # Curiosity bias: 0.0 = favor high activation; 1.0 = favor low/novel nodes.
    adv = cfg.get("advanced_autonomous") or {}
    try:
        curiosity = float(adv.get("curiosity_bias", 0.0))
    except Exception:
        curiosity = 0.0
    curiosity = max(0.0, min(1.0, curiosity))

    def _score(n: dict) -> float:
        a = float(n.get("activation", 0.0) or 0.0)
        if curiosity <= 0.0:
            return a
        if curiosity >= 1.0:
            return 1.0 - a
        # Linear blend between high-activation preference and low-activation preference.
        return (1.0 - curiosity) * a + curiosity * (1.0 - a)

    nodes_sorted = sorted(nodes, key=_score, reverse=True)
    queries: list[str] = []
    for n in nodes_sorted:
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
    seeds: list[str] | None = None,
    backup_before_run: bool = False,
    cooldown_seconds: int = 0,
) -> dict:
    """
    Run autonomous exploration: multiple cycles of query generation, optional web search,
    ingest into KG, and TS propagation. If seeds is provided, run for each seed in sequence
    (shared KG). Returns same structure as run_pipeline plus "cycles" list.
    """
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.main import run_pipeline
    from goat_ts_cig.search_fetcher import SEARCH_AVAILABLE, search_web

    if config is None:
        config = _load_config(config_path)
    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    if backup_before_run and db_path and db_path.strip() != ":memory:":
        try:
            from goat_ts_cig.undo import backup_db
            backup_db(db_path)
        except Exception:
            pass
    try:
        kg = KnowledgeGraph(db_path)
    except Exception as e:
        return {"error": f"Failed to open graph at {db_path}: {e}", "config": config}

    if seeds is None:
        seeds = [seed_query]
    adv = config.get("advanced_autonomous") or {}
    reflection = int(adv.get("reflection_cycles", 0))

    online_cfg = config.get("online") or {}
    use_online = online_cfg.get("enabled", False) and SEARCH_AVAILABLE
    if online_override is not None:
        use_online = online_override
    max_requests = online_cfg.get("max_requests_per_run", 30)
    timeout_seconds = online_cfg.get("timeout_seconds", 10)

    total_requests = 0
    cycles_log: list[dict] = []
    result = None

    for seed in seeds:
        current_seed = seed.strip()
        if not current_seed:
            continue
        for cycle in range(max_cycles):
            queries = generate_next_queries(
                kg, current_seed, cycle, max_queries_per_cycle, config
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
                    if cooldown_seconds > 0:
                        time.sleep(cooldown_seconds)
            cycles_log.append({"seed": current_seed, "queries": queries, "ingested_count": ingested_count})

            result = run_pipeline(
                current_seed,
                config_path=config_path,
                config=config,
                kg=kg,
            )
            if result.get("error"):
                result["cycles"] = cycles_log
                return result
            for _ in range(reflection):
                result = run_pipeline(current_seed, config=config, kg=kg)
                if result.get("error"):
                    result["cycles"] = cycles_log
                    return result

    if result is None:
        result = {"seed": seed_query, "config": config, "cig": {}, "graph": kg.to_json()}
    result["cycles"] = cycles_log

    # Optional LLM-based reflection at the end of the autonomous run.
    if adv.get("llm_reflection"):
        try:
            ollama_cfg = (config.get("llm_ollama") or {})
            if ollama_cfg.get("enabled"):
                from goat_ts_cig.llm_ollama import generate as ollama_generate
                summary_lines = []
                summary_lines.append(f"Autonomous exploration finished for seed '{seed_query}'.")
                summary_lines.append(f"Total cycles: {len(cycles_log)}.")
                if cycles_log:
                    summary_lines.append("Cycles (seed, queries, ingested_count):")
                    for i, cy in enumerate(cycles_log):
                        summary_lines.append(
                            f"  Cycle {i+1}: seed={cy.get('seed')}, "
                            f"queries={cy.get('queries', [])}, "
                            f"ingested={cy.get('ingested_count', 0)}"
                        )
                prompt = (
                    "You are reviewing the results of an autonomous knowledge-graph exploration.\n"
                    + "\n".join(summary_lines)
                    + "\n\n"
                    "In 3–6 short bullet points:\n"
                    "- Summarize what was explored.\n"
                    "- Point out any obvious gaps or missing angles.\n"
                    "- Suggest 1–3 concrete next seeds or queries.\n"
                )
                reflection_text = ollama_generate(
                    prompt,
                    ollama_cfg.get("host", "http://127.0.0.1:11434"),
                    ollama_cfg.get("model", "llama2"),
                    timeout=60,
                )
                result["reflection_suggestion"] = reflection_text
        except Exception:
            # Reflection is optional; ignore errors here.
            pass

    return result


def run_autonomous_one_cycle(
    config_path: str | None,
    config: dict,
    current_seed: str,
    cycle_index: int,
    max_queries_per_cycle: int,
    use_online: bool,
    max_requests: int,
    timeout_seconds: int,
    total_requests: int,
    cycles_log: list,
    reflection: int,
    cooldown_seconds: int = 0,
) -> tuple[dict, int, list]:
    """
    Run exactly one autonomous cycle (queries, optional search/ingest, pipeline, reflection).
    Returns (result, new_total_requests, new_cycles_log).
    """
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.main import run_pipeline
    from goat_ts_cig.search_fetcher import search_web

    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    kg = KnowledgeGraph(db_path)
    queries = generate_next_queries(kg, current_seed, cycle_index, max_queries_per_cycle, config)
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
            if cooldown_seconds > 0:
                time.sleep(cooldown_seconds)
    cycles_log = list(cycles_log) + [{"seed": current_seed, "queries": queries, "ingested_count": ingested_count}]
    result = run_pipeline(current_seed, config_path=config_path, config=config, kg=kg)
    if result.get("error"):
        result["cycles"] = cycles_log
        return result, total_requests, cycles_log
    for _ in range(reflection):
        result = run_pipeline(current_seed, config=config, kg=kg)
        if result.get("error"):
            result["cycles"] = cycles_log
            return result, total_requests, cycles_log
    result["cycles"] = cycles_log
    return result, total_requests, cycles_log
