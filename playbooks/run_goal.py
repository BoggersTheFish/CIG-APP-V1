#!/usr/bin/env python3
"""
Run goal-conditioned research: pass a goal string, get seeds from LLM (or fallback),
run autonomous exploration, optional summary. Requires Ollama for decomposition/summary.
Usage (from project root): python playbooks/run_goal.py "map the field of X"
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.research_agent import run_research_agent

def main():
    goal = sys.argv[1] if len(sys.argv) > 1 else "explore artificial intelligence"
    print("Goal:", goal)
    result = run_research_agent(goal, max_cycles=3, max_queries_per_cycle=3, summarize=True)
    if result.get("error"):
        print("Error:", result["error"])
        sys.exit(1)
    print("Seeds used:", result.get("seeds_used", []))
    print("Cycles:", len(result.get("cycles", [])))
    if result.get("summary"):
        print("Summary:", result["summary"][:500])

if __name__ == "__main__":
    main()
