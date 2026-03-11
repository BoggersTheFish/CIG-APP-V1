# CIG-APP (Contextual Information Generator)

Hybrid Python + Rust implementation of the GOAT-TS CIG: a local-first, low-memory knowledge exploration system using Thinking Wave (TS) propagation over a SQLite-backed graph.

---

## Requirements

- Python 3.12+
- Rust (rustup) and maturin for the optional Rust extension
- No GPU; runs on low-end hardware (e.g. Intel Pentium Silver, limited RAM)

---

## Setup

**Install Python dependencies:**

```bash
pip install -r requirements.txt
```

**Optional — build Rust extension (propagation and similarity):**

```bash
rustup install stable
maturin develop --manifest-path=rust/Cargo.toml
```

**Windows:**

```powershell
.\setup_windows.ps1
```

**Linux / macOS:**

```bash
chmod +x setup_lowend.sh && ./setup_lowend.sh
```

---

## Usage

### Web UI (recommended)

From the project root:

```bash
python -m streamlit run app_ui.py
```

If `streamlit` is on your PATH you can use:

```bash
streamlit run app_ui.py
```

The UI has five steps:

1. **Setup** — Environment checks and install commands  
2. **Configuration** — Edit all config options  
3. **Run & Explore** — Seed, optional ingest, run pipeline, view results  
4. **Optional Tools** — Run tests, benchmark, edit config, reset DB  
5. **Autonomous Exploration** — Multi-cycle query, search, ingest, and TS propagation  

In **Run & Explore** you can enable **Autonomous Exploration Mode** to run multiple cycles of query generation, optional web search, ingest, and TS propagation.

### Autonomous Exploration (optional)

- **What it does** — Runs several cycles (e.g. 5): generate search queries from the graph, optionally run web search (DuckDuckGo, no API key), ingest snippets into the knowledge graph, then run TS propagation. The graph grows from the seed and related concepts.
- **Off by default** — Enable under **Configuration → Online**, or set `CIG_ONLINE_ENABLED=1` in a `.env` file (copy from `.env.example`).
- **No API key** required for DuckDuckGo. Optional `CIG_SEARCH_API_KEY` in `.env` is for future search APIs.
- **Local-only mode** — If online is disabled or search dependencies are missing, the UI offers "Run in local-only mode (no web search)"; the autonomous loop still runs with heuristic query expansion and TS.

### CLI

```bash
# Explore from a seed concept (idea map, context expansion, hypotheses)
python run.py --seed "AI"

# Output as JSON
python run.py --seed "AI" --json

# Ingest text from a file, then explore
python run.py --seed "concept" --ingest-file examples/sample.txt

# Override wave ticks
python run.py --seed "AI" --ticks 20
```

---

## Configuration

Edit `config.yaml`:

| Key | Description |
|-----|-------------|
| `graph.path` | SQLite database path (default `data/knowledge_graph.db`) |
| `wave.ticks` | Propagation steps (default 10) |
| `wave.decay` | Activation decay per tick (default 0.9) |
| `wave.activation_threshold` | Threshold for ACTIVE state (default 0.5) |
| `online.enabled` | Allow web search in Autonomous Exploration (default false) |
| `online.max_requests_per_run` | Cap on HTTP requests per autonomous run (default 30) |

**Optional `.env`** (copy from `.env.example`):

- `CIG_ONLINE_ENABLED=0` or `1`
- `CIG_SEARCH_API_KEY=` (for future APIs)

---

## Design

- **Knowledge graph** — SQLite tables: `nodes` (id, label, mass, activation, state, metadata) and `edges` (from_id, to_id, type, weight).
- **TS propagation** — Implemented in Rust (wave engine, constraint resolution, decay, state updates). Python syncs the graph to Rust, runs a full TS cycle, then writes activations and states back.
- **CIG outputs** — Idea map (BFS subgraph around seed), context expansion (connected-component clusters), evidence chains (shortest path), and hypothesis suggestions (similarity and tension on conflict edges).

---

## Tests

```bash
python run_tests.py
```

---

## Benchmark

```bash
python benchmark.py
```

Requires the Rust extension to be built.

---

## License

See repository.
