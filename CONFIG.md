# Configuration Reference

This document lists all `config.yaml` keys and how `.env` overrides map into config. Use `validate_config.py` to check config and environment.

## config.yaml Sections

| Section | Key | Type | Default / Notes |
|---------|-----|------|-----------------|
| **graph** | path | string | `data/knowledge_graph.db` — SQLite database path. |
| **wave** | ticks | int | 10 — number of TS propagation ticks. |
| **wave** | decay | float | 0.9 — decay λ per tick. |
| **wave** | activation_threshold | float | 0.5 — threshold for activation. |
| **wave** | activation_fn | string | linear — linear \| tanh \| capped. |
| **wave** | use_frontier | bool | false — frontier-based propagation. |
| **wave** | use_convergence | bool | false — stop when delta < epsilon. |
| **wave** | max_ticks | int | 100 — when use_convergence. |
| **wave** | epsilon | float | 1e-5 — convergence threshold. |
| (root) | similarity_threshold | float | 0.3 — min similarity for hypotheses. |
| (root) | tension_threshold | float | 0.3 — min activation diff for tension. |
| **llm** | - | bool | true — master LLM switch. |
| **online** | enabled | bool | true — enable web search in autonomous. |
| **online** | max_requests_per_run | int | 30 — cap on search requests. |
| **online** | timeout_seconds | int | 10 — request timeout. |
| **llm_ollama** | enabled | bool | true — use Ollama. |
| **llm_ollama** | host | string | http://127.0.0.1:11434 | 
| **llm_ollama** | model | string | llama2 |
| **llm_ollama** | use_for_hypotheses | bool | true |
| **llm_ollama** | use_for_autonomous | bool | true |
| **export** | default_dir | string | data/exports |
| **advanced_autonomous** | reflection_cycles | int | 3 |
| **advanced_autonomous** | multi_seed | list | [] |
| **advanced_autonomous** | curiosity_bias | float | 0.0 |
| **advanced_autonomous** | llm_reflection | bool | false |
| **monitoring** | show_progress | bool | true |
| **advanced** | embeddings.enabled | bool | false |
| **vector** | enabled | bool | false — sqlite-vss. |
| **vector** | add_suggested_edges | bool | false — when true, add "suggested_relates" edges for similarity hypotheses. |
| **vector** | alpha | float | 0.1 — vector-augmented activation boost weight. |
| **vector** | similarity_top_k | int | 5 — max similar nodes for boost. |
| **vector** | similarity_threshold | float | 0.0 — min similarity for boost. |
| **ingestion** | pdf_enabled | bool | true |
| **resource_limits** | max_nodes | int | 50000 — fail if graph larger. |
| **resource_limits** | max_ticks_per_run | int | 500 — cap wave.ticks. |
| **resource_limits** | max_memory_mb | int | 0 — no check when 0. |
| (root) | advanced_features_enabled | bool | false — shell toggle. |

## .env Overrides

These environment variables are read at startup (e.g. by `app_ui.load_config()`) and override or supply config:

| Variable | Maps to | Notes |
|----------|---------|--------|
| CIG_ONLINE_ENABLED | online.enabled | 0/1 or true/false. |
| CIG_SEARCH_API_KEY | (reserved) | Future search API key. |
| OLLAMA_HOST or CIG_OLLAMA_HOST | llm_ollama.host | Ollama server URL. |
| OLLAMA_MODEL or CIG_OLLAMA_MODEL | llm_ollama.model | Ollama model name. |

Copy `.env.example` to `.env` and adjust. Validation: `python validate_config.py`.
