"""
Research Agent: goal-conditioned exploration.
Accepts a high-level goal (e.g. "map X field", "find tensions between A and B"),
decomposes it via LLM into seeds/steps, runs autonomous exploration, and optionally summarizes.
"""
from __future__ import annotations


def _decompose_goal_ollama(goal: str, config: dict) -> list[str]:
    """Use Ollama to turn a goal into a list of seed concepts. Returns [goal] on failure."""
    ollama = (config.get("llm_ollama") or {})
    if not ollama.get("enabled"):
        return [goal.strip() or "research"]
    try:
        from goat_ts_cig.llm_ollama import generate as ollama_generate
        prompt = (
            f"Goal: {goal}\n\n"
            "Output 1–5 short seed concepts or phrases to explore (one per line). "
            "Only output the seeds, nothing else."
        )
        out = ollama_generate(
            prompt,
            ollama.get("host", "http://127.0.0.1:11434"),
            ollama.get("model", "llama2"),
            timeout=45,
        )
        lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.strip().startswith("[")]
        if lines:
            return lines[:5]
    except Exception:
        pass
    return [goal.strip() or "research"]


def run_research_agent(
    goal: str,
    config_path: str | None = None,
    config: dict | None = None,
    max_cycles: int = 5,
    max_queries_per_cycle: int = 3,
    summarize: bool = True,
) -> dict:
    """
    Run goal-conditioned research: decompose goal into seeds, run autonomous exploration,
    then optionally summarize with LLM. Returns same shape as run_autonomous_explore plus
    goal, seeds_used, and summary (if summarize=True).
    """
    from goat_ts_cig.autonomous_explore import run_autonomous_explore

    if config is None:
        import os
        import yaml
        path = config_path or "config.yaml"
        if not os.path.isfile(path):
            path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        try:
            with open(path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception:
            config = {}

    seeds = _decompose_goal_ollama(goal, config)
    result = run_autonomous_explore(
        seeds[0],
        config_path=config_path,
        config=config,
        max_cycles=max_cycles,
        max_queries_per_cycle=max_queries_per_cycle,
        seeds=seeds if len(seeds) > 1 else None,
    )
    result["goal"] = goal
    result["seeds_used"] = seeds

    if summarize and not result.get("error"):
        ollama = (config.get("llm_ollama") or {})
        if ollama.get("enabled"):
            try:
                from goat_ts_cig.llm_ollama import generate as ollama_generate
                summary_parts = [
                    f"Goal: {goal}",
                    f"Seeds explored: {seeds}",
                    f"Cycles: {len(result.get('cycles', []))}",
                ]
                if result.get("cig", {}).get("hypotheses"):
                    summary_parts.append(
                        "Sample hypotheses: " + str(result["cig"]["hypotheses"][:3])
                    )
                prompt = (
                    "You are summarizing a research exploration.\n\n"
                    + "\n".join(summary_parts)
                    + "\n\nIn 2–4 sentences: what was explored and what are the main takeaways?"
                )
                result["summary"] = ollama_generate(
                    prompt,
                    ollama.get("host", "http://127.0.0.1:11434"),
                    ollama.get("model", "llama2"),
                    timeout=60,
                )
            except Exception:
                result["summary"] = None
    else:
        result["summary"] = None

    return result
