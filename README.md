# CIG-APP (Contextual Information Generator)

Hybrid Python + Rust implementation of the GOAT-TS CIG: a local-first, low-memory knowledge exploration system using Thinking Wave (TS) propagation over a SQLite-backed graph.

## Requirements

- Python 3.12+
- Rust (rustup) and maturin (for the optional Rust extension)
- No GPU; runs on low-end hardware (e.g. Intel Pentium Silver, limited RAM)

## Setup

```bash
pip install -r requirements.txt
# Optional: build Rust extension for propagation and similarity
rustup install stable
maturin develop --manifest-path=rust/Cargo.toml
```

Windows:

```powershell
.\setup_windows.ps1
```

Linux/Mac:

```bash
chmod +x setup_lowend.sh && ./setup_lowend.sh
```

## Usage

### Web UI (recommended)

From the project root:

```bash
python -m streamlit run app_ui.py
```

(If `streamlit` is on your PATH you can use `streamlit run app_ui.py` instead.)

The UI is a **single main page** with:

- **Seed concept** — e.g. "artificial intelligence".
- **Mode** — **Dry Run (Basic)** (TS propagation, graph, CIG only; no LLM/embeddings/online) or **Full Run (All Features)** (all optional deps required).
- **Run** — runs the pipeline (or autonomous exploration if "Run autonomous (5 cycles)" is checked in Full mode).
- **Sidebar** — UI theme (light/dark); **6. Advanced Features** expander: dependency checks (Ollama, Graphviz, Matplotlib), Ollama host/model, graph visualization, CSV/GraphML export, autonomous settings (reflection cycles, multi-seed, curiosity bias, LLM reflection), and Save.

**Verbose monitoring** — checkbox to show progress and post-run stats (node/edge counts). Single pipeline runs execute in a background thread so the UI shows "Running pipeline… (N s)" and a progress phase.

### Autonomous Exploration (optional)

- **What it does**: Runs several cycles (e.g. 5): generate search queries from the graph ? optionally run web search (DuckDuckGo, no API key) ? ingest snippets into the knowledge graph ? run TS propagation. The graph grows from the seed and related concepts.
- **Optional and off by default**: Enable in **Configuration** ? **Online**, or set `CIG_ONLINE_ENABLED=1` in a `.env` file (copy from `.env.example`).
- **No API key required** for DuckDuckGo. Optional `CIG_SEARCH_API_KEY` in `.env` is for future search APIs.
- **Local-only mode**: If online is disabled or search dependencies are missing, the UI offers "Run in local-only mode (no web search)"; the autonomous loop still runs with heuristic query expansion and TS.

### CLI

```bash
# Explore from a seed concept (output: idea map, context expansion, hypotheses)
python run.py --seed "AI"

# Output as JSON
python run.py --seed "AI" --json

# Ingest text from a file, then explore
python run.py --seed "concept" --ingest-file examples/sample.txt

# Override wave ticks
python run.py --seed "AI" --ticks 20
```

## Configuration

Edit `config.yaml`:

- `graph.path`: SQLite database path (default `data/knowledge_graph.db`)
- `wave.ticks`: Propagation steps (default 10)
- `wave.decay`: Activation decay per tick (default 0.9)
- `wave.activation_threshold`: Threshold for ACTIVE state (default 0.5)
- `online.enabled`: Allow web search in Autonomous Exploration (default false)
- `online.max_requests_per_run`: Cap on HTTP requests per autonomous run (default 30)

Optional `.env` (copy from `.env.example`): `CIG_ONLINE_ENABLED=0|1`, `CIG_SEARCH_API_KEY=`, `CIG_OLLAMA_HOST=`, `CIG_OLLAMA_MODEL=`

### Advanced Features (step 6 in the UI)

In **6. Advanced Features** you can configure:

- **Local LLM (Ollama)**: Use [Ollama](https://ollama.ai) for hypothesis phrasing and autonomous query expansion. Set host and model in the UI or via `CIG_OLLAMA_HOST` and `CIG_OLLAMA_MODEL` in `.env`. Config keys: `llm_ollama.enabled`, `llm_ollama.use_for_hypotheses`, `llm_ollama.use_for_autonomous`.
- **Graph visualization**: Export a subgraph around a seed as PNG (Graphviz or Matplotlib). Requires `graphviz` (and optionally Graphviz binaries from https://graphviz.org) or `matplotlib` + `networkx`.
- **Export**: Export the knowledge graph to CSV (nodes/edges) and the last run or autonomous result to JSON. Default directory: `config.export.default_dir` (e.g. `data/exports`).
- **Advanced autonomous**: Reflection cycles (extra propagation steps per cycle) and multiple seeds (run autonomous for each seed in sequence). Config: `advanced_autonomous.reflection_cycles`, `advanced_autonomous.multi_seed`.
- **Monitoring**: Option "Show progress during run" (`monitoring.show_progress`) for progress display when running the pipeline.

See `config.yaml` and `.env.example` for all keys.

## Design

- **Knowledge graph**: SQLite tables `nodes` (id, label, mass, activation, state, metadata) and `edges` (from_id, to_id, type, weight).
- **TS propagation**: Implemented in Rust (wave engine + constraint resolution + decay + state updates). Python syncs the graph to Rust, runs a full TS cycle, then writes activations/states back.
- **CIG outputs**: Idea map (BFS subgraph around seed), context expansion (connected-component clusters), evidence chains (shortest path), and hypothesis suggestions (similarity + tension on conflict edges).

## Tests

```bash
python run_tests.py
```

Or run pytest directly:

```bash
python -m pytest tests/ -v
```

## Config validation

Check `config.yaml` and `.env` integrity (Phase 19):

```bash
python validate_config.py
```

## Benchmark

```bash
python benchmark.py
```

(Rust extension must be built.) The script times TS propagation for 500 and 1000 nodes; optional pipeline/export timings are included when available.

## Improvements

Single-page UI (Dry Run / Full Run), Advanced Features in sidebar (Ollama, graph viz, CSV/GraphML export, autonomous settings, monitoring). Progress bar and background-thread run; verbose monitoring. Phases 13–19: Advanced Features shell, Ollama adapter, graph_viz/export_utils, autonomous reflection/multi-seed/curiosity bias, progress callback. Optional: embeddings, vector search, PDF ingestion, GraphML, undo/backup; theme toggle. Earlier: license (MIT), sidebar Feature status and one-click installs, export previews and downloads, curiosity bias and LLM reflection for autonomous mode, dashboard (activation overview), scaling notes in UI, theme toggle, human-in-loop pause, embeddings (optional), vector search (optional), PDF ingestion, GraphML export, undo/backup. Later: pipeline run feedback (“Running pipeline…” while non-autonomous run executes), Streamlit session-state fixes, **developer mode** in Setup (debug menus in all tabs).

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE). Copyright (c) 2026 BoggersTheFish.

## Recommended GitHub Topics

Apply these GitHub topics via repo settings: knowledge-graph streamlit rust-python local-ai thinking-waves sqlite ollama vector-search autonomous-exploration embeddings pdf-ingestion
