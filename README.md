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

The UI walks through: **Setup**, **Configuration**, **Run & Explore**, **Optional Tools**, and **5. Autonomous Exploration**. In **Run & Explore** you can enable **Autonomous Exploration Mode** to run multiple cycles of query generation, optional web search, ingest, and TS propagation.

### Autonomous Exploration (optional)

- **What it does**: Runs several cycles (e.g. 5): generate search queries from the graph → optionally run web search (DuckDuckGo, no API key) → ingest snippets into the knowledge graph → run TS propagation. The graph grows from the seed and related concepts.
- **Optional and off by default**: Enable in **Configuration** → **Online**, or set `CIG_ONLINE_ENABLED=1` in a `.env` file (copy from `.env.example`).
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

Optional `.env` (copy from `.env.example`): `CIG_ONLINE_ENABLED=0|1`, `CIG_SEARCH_API_KEY=`

## Design

- **Knowledge graph**: SQLite tables `nodes` (id, label, mass, activation, state, metadata) and `edges` (from_id, to_id, type, weight).
- **TS propagation**: Implemented in Rust (wave engine + constraint resolution + decay + state updates). Python syncs the graph to Rust, runs a full TS cycle, then writes activations/states back.
- **CIG outputs**: Idea map (BFS subgraph around seed), context expansion (connected-component clusters), evidence chains (shortest path), and hypothesis suggestions (similarity + tension on conflict edges).

## Tests

```bash
python run_tests.py
```

## Benchmark

```bash
python benchmark.py
```

(Rust extension must be built.)

## License

See repository.
