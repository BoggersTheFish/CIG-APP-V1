### Usage Guide for CIG-APP
**(GUI Usage and Terminal Usage – detailed but easy to follow)**

---

## 1. Prerequisites (for both GUI and terminal)

- **OS**: Windows, Linux, or macOS
- **Python**: 3.12+
- **Rust toolchain**: via `rustup` (for optional Rust acceleration)
- **Project root**: e.g. `c:\Users\gamin\Desktop\CIG-APP`

From project root:

```bash
pip install -r requirements.txt
```

Optional but recommended (Rust extension):

```bash
# from project root
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

python -m pip install maturin
python -m maturin develop --manifest-path=rust/Cargo.toml
```

When using the **GUI auto-setup**, the app can create `.venv` and build the extension for you.

---

## 2. GUI Usage (Streamlit App)

### 2.1 Start the GUI

**Preferred (with venv):**

```powershell
cd c:\Users\gamin\Desktop\CIG-APP
.venv\Scripts\python -m streamlit run app_ui.py
```

This opens a browser (typically `http://localhost:8501`). The sidebar shows steps:

1. Setup  
2. Configuration  
3. Run & Explore  
4. Optional Tools  
5. Autonomous Exploration  
6. Advanced Features  

While any long operation is running, the app:

- Shows an **“operation in progress”** banner at the top.
- Disables all other action buttons (prevents accidental double-runs).
- Shows progress bars and status messages for the running job.

**New UI controls:** Feature status (sidebar) with one-click installs; theme toggle (light/dark); human-in-loop pause in Autonomous; optional embeddings (sentence-transformers) and vector search (sqlite-vss); backup/restore before autonomous; export preview and GraphML; PDF ingest (PyPDF2). **Developer mode** (Step 1 – Setup): enable “Developer mode (show debug menus in all tabs)” to see Debug expanders in every step (session state, config, pipeline/autonomous state). Pipeline runs (non-autonomous) show “Running pipeline… (N s)” while executing. See Step 6 and Optional Tools for toggles.

---

### 2.2 Step 1 – Setup

**Environment checks:**

- **Python 3.12+**: shows your Python version and whether it’s OK.
- **Pip packages**: checks `PyYAML`, `pytest`, and `maturin`.
- **Rust (cargo)**: checks if Rust is installed.
- **Rust extension (goat_ts_core)**: checks if the compiled Rust extension is present.

**Install commands:**

- **Run pip install -r requirements.txt**  
  - Button runs `python -m pip install -r requirements.txt`.  
  - Shows progress and the full pip output.

- **Rust toolchain and extension:**
  - Static reference:
    - `rustup install stable`
    - `maturin develop --manifest-path=rust/Cargo.toml`
  - **Run rustup install stable** (button, only if Rust is detected):
    - Installs or updates the stable Rust toolchain.
  - **Build Rust extension (maturin develop)** (button, only if Rust is detected):
    - If you are **not** in a venv:
      - Creates `.venv` in the project root.
      - Installs `maturin` into `.venv`.
      - Builds and installs the Rust extension using `.venv`’s Python.
      - Starts a **new Streamlit instance using `.venv`** on port 8502 and opens it in your browser.
      - Shows a link to `http://localhost:8502` and a note that you can switch to the new app.
    - If you **are** in a venv:
      - Runs `python -m maturin develop --manifest-path=rust/Cargo.toml` directly with your current Python.
    - All output (stdout/stderr) is captured and displayed; if something fails, you see the real error.

**Setup scripts (optional):**

- **Run setup_windows.ps1**  
  - Executes `setup_windows.ps1` with PowerShell:
    - `powershell -ExecutionPolicy Bypass -File setup_windows.ps1`
  - Shows script output; if PowerShell isn’t found, shows a clear error.

- **Run setup_lowend.sh**  
  - Executes `setup_lowend.sh` with Bash:
    - `bash setup_lowend.sh`
  - On Windows, if `bash` is missing, it tells you to use WSL or Git Bash or run the script on Linux/Mac.
  - Shows full script output.

**Completion hints:**

- If Python and pip checks pass, you see a “Environment ready” success note guiding you to **2. Configuration** and **3. Run & Explore**.

---

### 2.3 Step 2 – Configuration

This step configures `config.yaml` through the UI.

If `config.yaml` does not exist:

- The app warns: “No `config.yaml` found. Defaults will be used; click **Save configuration** to create one.”

**Sections:**

- **Graph**
  - **Database path**: path to the SQLite knowledge graph (default `data/knowledge_graph.db`).
  - You can use `:memory:` for an in-memory graph (primarily for tests or quick experiments).

- **Wave (TS propagation)**
  - **Ticks**: number of propagation steps per run (e.g. 10).
  - **Decay**: activation decay per tick (0–1).
  - **Activation threshold**: activation level above which nodes are considered ACTIVE.

- **Hypothesis (optional)**
  - **Similarity threshold**: minimum similarity for suggesting new links.
  - **Tension threshold**: activation difference threshold across conflict edges for detecting tension.

- **LLM (optional)**
  - **Use LLM for hypothesis phrasing**: toggles LLM usage.
  - Depending on step 6 configuration, this uses the built-in stub or **Ollama**.

- **Online (autonomous exploration)**
  - **Enable online search**: allow web search (DuckDuckGo) during autonomous runs.
  - **Max requests per run**: upper bound on HTTP requests per autonomous run.
  - Timeout settings are read from `config.yaml` and respected in the code.

**Save configuration:**

- Clicking **Save configuration**:
  - Writes your settings into `config.yaml`.
  - Preserves advanced keys (`llm_ollama`, `export`, `advanced_autonomous`, `monitoring`) and merges with the existing config.
  - Shows a live YAML preview of what’s saved.

Advanced features (Ollama, export, advanced autonomous, monitoring) are mainly adjusted in **Step 6**.

---

### 2.4 Step 3 – Run & Explore

This is the main one-shot pipeline runner.

**Inputs:**

- **Seed concept**: central node label (e.g. `AI`).
- **Autonomous Exploration Mode** (checkbox):
  - If off: runs a single pipeline pass (ingest → propagate → CIG generation).
  - If on: runs 5 autonomous cycles:
    - Generate queries → optional online search → ingest → TS propagation.
  - When on, the step:
    - Calls `check_online_available` to see if search deps and config are ready.
    - Offers a **“Run in local-only mode (no web search)”** checkbox as needed.

- **Ingest text (optional)**:
  - **None** – do not ingest extra text.
  - **Paste text** – a large textarea; words become nodes and are linked sequentially.
  - **Upload file** – upload `.txt` or `.md`, which is decoded with UTF-8 `errors="replace"` and ingested.

- **Override wave ticks for this run**:
  - If checked, you can set a temporary tick count.

**Run pipeline:**

- **Run pipeline** button:
  - Disabled if another operation is in progress.
  - Shows a status panel and progress bar:
    - Spinner text changes depending on whether Autonomous Mode is on.
  - If Autonomous Mode is **off**:
    - Calls `run_pipeline(seed, ...)` with:
      - Optional `ingest_text`.
      - Optional `ticks_override`.
      - An optional progress callback if monitoring is enabled.
  - If Autonomous Mode is **on**:
    - Calls `run_autonomous_explore` for 5 cycles:
      - Uses `advanced_autonomous.multi_seed` to run for additional seeds in sequence.
      - Optionally uses online search, depending on `online.enabled` and the toggle.

All operations store their result in `st.session_state["last_run_result"]`.

**Outputs:**

- **Success banner** with:
  - Seed.
  - Node ID.
  - Whether Rust was used (`rust_used`).

- **Cycles summary** (when cycles exist):
  - For each cycle:
    - Index (1-based).
    - Seed label (including multi-seed).
    - Query list.
    - Count of ingested snippets.

- **Tabs:**
  - **Idea map**: BFS subgraph around the seed.
  - **Context expansion**: cluster partitions with total activations.
  - **Hypotheses**: suggestions derived from similarity/tension; optionally LLM-phrased.
  - **Graph summary**:
    - Node and edge counts.
    - Node table as a dataframe.
  - **Raw JSON**: entire pipeline result (useful for debugging or exporting).

- **Clear result**:
  - Button to clear the last run result (disabled while busy).

---

### 2.5 Step 4 – Optional Tools

Utility panel for development and maintenance.

- **Run tests**:
  - Runs `python run_tests.py`.
  - Shows a progress bar and a status panel with full pytest output.

- **Run benchmark**:
  - Runs `python benchmark.py`.
  - Benchmarks propagation performance (requires Rust extension).

- **View / edit config file**:
  - Displays raw `config.yaml` in a textarea, read as UTF-8 with `errors="replace"`.
  - **Overwrite config.yaml** writes any changes back to disk.

- **Reset database**:
  - Shows the DB path from `graph.path`.
  - If `:memory:`, explains nothing needs to be deleted.
  - If the file exists:
    - Warns that it exists and offers a **Delete database** button.
    - Deletes the file if clicked.

All buttons honor the global lock and show clear output.

---

### 2.6 Step 5 – Autonomous Exploration

Provides a focused view for multi-cycle, possibly online, exploration.

**Inputs:**

- **Seed query**: main starting concept.
- **Number of cycles**: number of autonomous iterations (slider).
- **Max queries per cycle**: number of queries to generate per cycle.
- **Use online search (if available)**: toggles web search on/off.
- Also uses `advanced_autonomous.multi_seed` from the config:
  - It builds a list `[seed_query] + multi_seed` so each seed gets explored.

**Execution:**

- **Run autonomous exploration**:
  - Disabled when an operation is in progress.
  - Shows a progress bar and status.
  - Calls `run_autonomous_explore` with:
    - `max_cycles`
    - `max_queries_per_cycle`
    - `online_override` (based on availability and toggles)
    - `seeds` if there is more than one seed.

**Outputs:**

- Same pattern as step 3:
  - Success banner.
  - Cycles summary (with per-cycle seed names).
  - Tabs for Idea map, Context expansion, Hypotheses, Graph summary, Raw JSON.
  - **Clear result** button to clear `last_autonomous_result`.

---

### 2.7 Step 6 – Advanced Features

Central place for advanced configuration and tools.

**Dependency check:**

- **Ollama (local LLM)**: checks if `host/api/tags` is reachable.
- **Graphviz**: checks if Python `graphviz` package is importable.
- **Matplotlib**: checks if `matplotlib` is importable.

Provides a quick overview of which features can be used.

**Graph visualization:**

- Requires Graphviz **or** Matplotlib:
  - **Engine**: `graphviz` or `matplotlib`.
  - **BFS depth**: depth from the seed in the graph.
  - **Output path**: PNG path (default under `data/exports`).
  - **Seed label for export**: defaults to the last run’s seed; can be changed.
  - **Export subgraph PNG**:
    - For non-`:memory:` DB:
      - Opens the KG.
      - Finds the seed node by label.
      - Builds a subgraph and writes a PNG via the chosen engine.
    - For `:memory:` DB:
      - Shows a warning that the graph is empty.

- If Graphviz is missing:
  - Provides an explanation and a **Run pip install graphviz** button.

**Local LLM (Ollama):**

- If Ollama is reachable:
  - **Ollama host**: e.g. `http://127.0.0.1:11434`.
  - **Model name**: e.g. `llama2`.
  - Toggle usage:
    - For hypothesis phrasing.
    - For autonomous query expansion.
  - **Save LLM settings**:
    - Writes `llm_ollama` into `config.yaml`.
    - Reruns the app to apply changes.

- If not reachable:
  - Shows a “How to enable Ollama” guide:
    - Install from `https://ollama.ai`.
    - Pull a model: `ollama pull llama2` (or other).
    - Ensure the service is running.
  - “I’ve completed these steps” button re-checks availability.

**Export:**

- Uses `export_utils` to:
  - **Export graph to CSV**:
    - Generates `nodes.csv` and `edges.csv` in a chosen directory.
    - Handles `:memory:` graph with a warning.
  - **Export last result to JSON**:
    - Writes the last pipeline or autonomous result to a JSON file.

**Advanced autonomous:**

- Manages `advanced_autonomous` config:
  - **Reflection cycles (0–5)**: extra propagation-only passes after each main cycle.
  - **Additional seeds (one per line)**:
    - Each seed is processed in sequence, sharing the same KG.
  - **Save advanced autonomous settings**:
    - Writes to `config.yaml`.
    - Reruns the app.

**Monitoring:**

- **Show progress during run**:
  - Toggles `monitoring.show_progress`.
  - When enabled, the pipeline uses a progress callback to update the UI.
  - Saving reruns the app.

---

## 3. Terminal Usage

Most features are available without the GUI via CLI and small scripts.

### 3.1 Setup

From project root:

```bash
pip install -r requirements.txt
```

Optional scripts:

- **Windows**:

```powershell
.\setup_windows.ps1
```

- **Linux/Mac**:

```bash
bash ./setup_lowend.sh
```

Rust extension (CLI-style):

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

python -m pip install maturin
python -m maturin develop --manifest-path=rust/Cargo.toml
```

---

### 3.2 Run the pipeline from terminal

```bash
python run.py --seed "AI"
```

Options:

- `--json`: output JSON with idea map, context expansion, hypotheses, and graph.
- `--ticks N`: override wave ticks from config.
- `--ingest-file PATH`: ingest a file of text before running.

Examples:

```bash
python run.py --seed "AI" --ticks 20
python run.py --seed "climate change" --ingest-file examples/sample.txt --json
```

---

### 3.3 Autonomous exploration (terminal)

Basic usage with `python -c`:

```bash
python -c "from goat_ts_cig.autonomous_explore import run_autonomous_explore; \
print(run_autonomous_explore('AI', max_cycles=3, online_override=False))"
```

Or via a small script:

```python
from goat_ts_cig.autonomous_explore import run_autonomous_explore
import json

if __name__ == "__main__":
    result = run_autonomous_explore("AI", max_cycles=3, online_override=False)
    print(json.dumps(result, indent=2))
```

Then:

```bash
python scripts/autonomous_cli.py
```

To enable online search:

- Ensure `config.yaml` has:

```yaml
online:
  enabled: true
```

or `.env` has:

```bash
CIG_ONLINE_ENABLED=1
```

---

### 3.4 Tests and benchmark

```bash
python run_tests.py     # runs pytest
python benchmark.py     # runs Rust-backed benchmark (if extension built)
```

---

### 3.5 Exporting data (terminal)

Use the library functions directly:

```python
from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig.export_utils import export_graph_csv, export_cig_json
from goat_ts_cig.main import run_pipeline
import json

if __name__ == "__main__":
    kg = KnowledgeGraph("data/knowledge_graph.db")
    paths = export_graph_csv(kg, "data/exports")
    print("CSV:", paths)

    result = run_pipeline("AI")
    export_cig_json(result, "data/exports/last_result.json")
    print("Wrote data/exports/last_result.json")
```

Run:

```bash
python scripts/export_graph.py
```

---

### 3.6 Ollama usage (terminal)

Configure via `.env` and `config.yaml`:

- `.env`:

```bash
CIG_OLLAMA_HOST=http://127.0.0.1:11434
CIG_OLLAMA_MODEL=llama2
```

- `config.yaml`:

```yaml
llm: true
llm_ollama:
  enabled: true
  host: "http://127.0.0.1:11434"
  model: "llama2"
  use_for_hypotheses: true
  use_for_autonomous: true
```

Then:

- Any `run_pipeline` call that has `llm: true` and `llm_ollama.enabled: true` will use Ollama for:
  - Hypothesis phrasing (if `use_for_hypotheses`).
  - Autonomous query generation (if `use_for_autonomous`).

---

## 4. Recommended Flows

### 4.1 First-time GUI flow

1. **Setup (Step 1)**
   - Use **Run pip install -r requirements.txt**.
   - If needed, use **Run rustup install stable**.
   - Use **Build Rust extension (maturin develop)**:
     - Let it create `.venv` and auto-open the `.venv`-based app.
2. **Configuration (Step 2)**
   - Set graph DB path, wave settings, and optional hypothesis/LLM/online options.
   - Save configuration.
3. **Run & Explore (Step 3)**
   - Run with a simple seed (e.g. `AI`).
   - Optionally ingest some sample text.
4. **Autonomous Exploration (Step 5)**
   - Try a few local-only cycles.
   - Then enable online search and try again.
5. **Advanced Features (Step 6)**
   - Enable and configure Ollama.
   - Export a subgraph PNG.
   - Export graph and last result to CSV/JSON.
   - Tune advanced autonomous options and monitoring.

---

### 4.2 Terminal-first flow

1. Install dependencies and, optionally, build the Rust extension using a venv.
2. Edit `config.yaml` manually (or copy from examples).
3. Use `python run.py --seed ...` to drive the pipeline.
4. Use small helper scripts or `python -c` to:
   - Run autonomous exploration.
   - Export graph and results.

