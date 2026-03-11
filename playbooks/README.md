# Research Playbooks

Example configs and scripts for specific research tasks. Copy and adjust for your use case.

## Literature map (single seed)

- **Goal**: Explore a niche field from one seed concept.
- **Config**: Use `playbooks/config_literature_map.yaml` as a base (low ticks, no online, optional embeddings).
- **Steps**: Run Setup Wizard → Main Controls → enter seed (e.g. "cognitive load") → Dry or Full Run → inspect Run & Results (idea map, hypotheses, export GraphML/RDF).

## Tension / contradiction mapping

- **Goal**: Surface tensions between concepts (conflict edges and activation mismatch).
- **Config**: Enable hypotheses; use a corpus that has conflict edges or add them via ingest.
- **Steps**: Ingest text that mentions opposing terms; run pipeline; open **Monitoring** in Run & Results and check "Top tension edges"; export and refine.

## Autonomous exploration (multi-cycle)

- **Goal**: Grow the graph over several cycles with optional web search.
- **Config**: `online.enabled: true` and `advanced_autonomous` (reflection_cycles, curiosity_bias, llm_reflection) as needed.
- **Steps**: Main Controls → Full Run → check "Run autonomous (5 cycles)" → Run; review cycles and LLM reflection in Run & Results.

## Goal-conditioned research (research_agent)

- **Goal**: High-level goal → LLM-decomposed seeds → autonomous run → summary.
- **Script**: `playbooks/run_goal.py` (run from project root with a goal string).
- **Requires**: Ollama enabled for decomposition and optional summary.
