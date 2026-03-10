# Cursor Agent Instructions

Follow this plan sequentially.

Complete each step fully before moving to the next.

If implementation issues occur:
- debug the issue
- update the implementation
- continue with the plan

Do not skip steps.

# PLAN.md: Engineering Implementation Plan for GOAT-TS (Evolving to Contextual Information Generator - CIG)

## Document Metadata
- **Author**: Grok 4 (xAI) acting as Principal Systems Architect and Research Engineer
- **Date**: March 10, 2026
- **Version**: 1.0
- **Purpose**: This document provides a complete, step-by-step engineering implementation plan for building GOAT-TS as a Contextual Information Generator (CIG). It is designed for execution by an autonomous coding agent in Cursor, ensuring sequential, executable steps without need for clarification.
- **Scope**: Consolidates ideas from existing repositories into a unified, scalable, hybrid Python+Rust architecture optimized for low-end hardware (e.g., Intel Pentium Silver CPU, limited RAM, no GPU). Focuses on knowledge exploration via TS (Thinking Wave) framework, emphasizing efficiency, local storage, and emergent contextual insights.
- **Assumptions**: The agent has access to a clean GitHub repository named "GOAT-TS" for implementation. Tools like Git, Python 3.12+, Rust (via rustup), maturin (for PyO3), and pytest are installed. No external services or internet beyond initial setup.

---

## 1. Analysis of the Existing Repositories

Based on inspection of the provided repositories via browsing their GitHub pages, here is a detailed analysis. The analysis identifies structure, purpose, existing functionality, reusable parts, improvements needed, and replacements to align with the new requirements (low-end hardware, Python+Rust hybrid, no heavy dependencies like NebulaGraph/Spark/Redis, local storage via SQLite, focus on CIG outputs like idea maps, context expansions, evidence chains, hypothesis suggestions).

### 1.1 GOAT-TS-DEVELOPMENT (https://github.com/BoggersTheFish/GOAT-TS-DEVELOPMENT)
- **Structure**: Early-stage repo with directories: data/, examples/, python/, rust/, tests/. Files: .gitignore, OPTIMIZATION.md, README.md, benchmark.py, config.yaml, requirements.txt, run.py, run_tests.py. Python-dominant (86.5%), Rust (13.5%). Single branch (main), 3 commits, latest on March 10, 2026.
- **Purpose**: Appears as a development fork for a lightweight GOAT-TS variant (referenced as "GOAT-TS-SUPERLITE CIG with wave propagation, data-gen…"). Focuses on wave propagation and data generation, with benchmarking and optimization notes.
- **Existing Functionality**: Basic setup for hybrid architecture, including run scripts, config, tests, and benchmarks. Likely includes initial wave propagation logic in Rust and Python orchestration.
- **Reusable Parts**: 
  - Directory structure (python/, rust/, data/, examples/, tests/) aligns closely with target architecture—reuse as base skeleton.
  - config.yaml for parameters (e.g., wave ticks, decay).
  - benchmark.py and OPTIMIZATION.md for performance tuning on low-end hardware.
  - run.py and run_tests.py as entry points.
- **Improvements/Replacements**: 
  - Expand Rust components for core compute (e.g., add constraint resolution, similarity search).
  - Replace any heavy deps with lightweight ones (e.g., SQLite instead of implied graph DB).
  - Add CIG-specific outputs (idea maps, etc.).
  - It's empty-ish (no detailed code in summary), so treat as a scaffold to build upon.

### 1.2 GOAT-TS (https://github.com/BoggersTheFish/GOAT-TS)
- **Structure**: Mature repo with directories: configs/, docker/, examples/, infra/, scripts/, src/ (subdirs: agi_loop/, graph/, ingestion/, reasoning/, simulation/, physics/, monitoring/), tests/. Files: .env.example, .gitignore, CHANGELOG.md, CODEBASE.md, CONTRIBUTING.md, LICENSE, PLATFORM.md, README.md, README_ARCHITECTURE.md, ROADMAP.md, pytest.ini, requirements.txt. Python-only, with extensive scripts (e.g., goat_ts_gui.py, serve_api.py).
- **Purpose**: Full knowledge-graph-driven cognition scaffold using NebulaGraph for storage, PyTorch/LangChain for processing, Streamlit for GUI, Spark for ETL, Redis for caching. Implements ingestion, spreading activation, memory dynamics, gravity simulation, tension-based reasoning, hypothesis generation. Designed for local-to-distributed scaling.
- **Existing Functionality**: Comprehensive pipeline: text ingestion → graph build → cognition loop (activation spread, decay, states: ACTIVE/DORMANT/DEEP) → reasoning (tension, hypotheses). Provenance via waves. CLI/API/GUI interfaces.
- **Reusable Parts**:
  - Core concepts: TS wave propagation, node states, tension computation, hypothesis generation—port algorithms to Rust for efficiency.
  - src/reasoning/* for hypothesis logic.
  - src/simulation/* and src/physics/* for gravity/influence ideas (adapt to constraint interactions).
  - configs/*.yaml for parameter inspiration.
  - tests/ for pytest patterns.
  - ROADMAP.md for phased development ideas.
- **Improvements/Replacements**:
  - Heavy deps (NebulaGraph, Spark, Redis, PyTorch, LangChain) violate hardware constraints—replace with SQLite, pure Python/Rust algos, no LLM unless optional/local.
  - Remove Docker/infra/ for local-only focus.
  - Simplify GUI to CLI-only; add CIG outputs explicitly.
  - Port performance-critical parts (graph traversal, propagation) to Rust to handle low RAM.

### 1.3 GOAT-TS-LITE (https://github.com/BoggersTheFish/GOAT-TS-LITE)
- **Structure**: Minimal repo with directories: config/, reasoning/, src/. Files: .gitignore, README_GOATS_LITE.md, requirements.txt, run_windows.ps1, setup_goatts_lowend.sh, streamlit_app.py. Python (92.5%), Shell/PowerShell for setup. Single commit on March 10, 2026.
- **Purpose**: Lightweight, CPU-only variant for low-end systems, focusing on TS convergence, attractors, knowledge processing. Includes setup scripts for Windows/low-resource envs and Streamlit app.
- **Existing Functionality**: CPU-optimized runtime, reasoning module, convergence detection. Emphasizes low-resource execution.
- **Reusable Parts**:
  - setup_goatts_lowend.sh and run_windows.ps1 for cross-platform low-end setup.
  - reasoning/ for simplified hypothesis/tension logic.
  - Focus on convergence/attractors—integrate into TS engine.
- **Improvements/Replacements**:
  - Add Rust for better performance on low-end (e.g., multi-threaded propagation).
  - Remove Streamlit if GUI not needed; align with CLI.
  - Expand to full CIG features.

### 1.4 GOAT-TS-SUPERLITE (https://github.com/BoggersTheFish/GOAT-TS-SUPERLITE)
- **Structure**: Hybrid setup with directories: data/, examples/, python/ (sub: goat_ts_cig/, bindings/), rust/ (sub: goat_ts_core), tests/. Files: .gitignore, README.md, config.yaml, requirements.txt, run.py, run_tests.py. Python (81.8%), Rust (18.2%). Single commit on March 10, 2026.
- **Purpose**: Super-lightweight CIG implementation using TS framework. Local-first, low-memory, constraint-based wave propagation over knowledge graph. SQLite storage, PyO3 bindings, CLI/JSON outputs. Focuses on non-predictive exploration.
- **Existing Functionality**: Wave propagation, graph engine in Rust; Python orchestration, hypothesis generation, config/env overrides. Testing via pytest.
- **Reusable Parts**:
  - Entire structure matches target (python/, rust/, data/, etc.)—use as primary base.
  - rust/ for core engines (graph, wave).
  - python/bindings/ for PyO3.
  - config.yaml and env overrides.
  - run.py for CLI, examples/sample_usage.py.
  - README setup/build instructions.
- **Improvements/Replacements**:
  - Expand Rust modules (add constraint, similarity).
  - Add full CIG generators (idea maps, etc.).
  - Enhance testing/performance for low-end.

### Overall Consolidation Strategy
- **Key Insights**: GOAT-TS is heavy/full-featured; LITE/SUPERLITE/DEVELOPMENT are progressive lightenings toward low-end, hybrid. Common themes: TS waves, graph, reasoning/hypotheses.
- **Reuse**: Adopt SUPERLITE's hybrid structure/config/CLI as base. Port algorithms from GOAT-TS (propagation, tension). Use LITE's low-end setup scripts. DEVELOPMENT's benchmarks/optimizations.
- **Improvements**: Unify into scalable CIG: Add explicit outputs, Rust for efficiency, SQLite storage. Remove heavies; ensure no GPU/cloud.
- **Replacements**: NebulaGraph → SQLite; Spark/Redis → in-memory/Rust algos; LangChain → optional local LLM stubs.
- **Build Approach**: Start from SUPERLITE skeleton, incrementally add from others, evolve to CIG.

---

## 2. Consolidated Architecture Proposal

The unified architecture consolidates the TS framework from all repos into a CIG system. It models knowledge as a dynamic constraint network: nodes (concepts/docs/hypotheses) with weights/influence, edges (relationships/constraints), waves for propagation.

### High-Level Components
- **Knowledge Graph Engine**: Local SQLite-based graph (nodes/edges tables).
- **TS Wave Propagation Engine**: Rust: Activation, spread, decay, interaction, convergence.
- **CIG Generator**: Python: Produce idea maps (graph subviews), context expansions (clusters), evidence chains (paths), hypotheses (weak links).
- **Similarity Engine**: Rust: Embedding-free (string/Jaccard) or simple vec comparison for low-RAM.
- **Hypothesis Engine**: Python: Detect anomalies, suggest links.
- **Orchestration**: Python CLI, config-driven.

### Architecture Diagram (Text-Based)
```
User Input (CLI: --seed "concept")
  ↓
Python Orchestration (main.py)
  ├── Load Config (config.yaml)
  ├── Manage Graph (knowledge_graph.py) → SQLite (data/knowledge_graph.db)
  ├── Call Rust Bindings (rust_bindings.py) → Rust Lib (lib.rs)
  │     ├── Graph Traversal (graph_engine.rs)
  │     ├── Wave Propagation (wave_engine.rs)
  │     ├── Constraint Resolution (constraint_engine.rs)
  │     ├── Similarity Search (similarity_engine.rs)
  ↓
CIG Generation (cig_generator.py)
  ├── Idea Maps: Subgraph extraction
  ├── Context Expansion: Cluster detection
  ├── Evidence Chains: Path finding
  └── Hypothesis Suggestions: Anomaly detection (hypothesis_engine.py)
  ↓
Output: JSON/Text to stdout
```

### Key Design Principles
- **Efficiency**: Rust for compute-heavy (multi-threaded, low-mem algos like BFS for traversal).
- **Local-Only**: No net access post-setup.
- **Scalability**: Start small; add sharding later.
- **PyO3 Bindings**: Expose Rust as Python module.

---

## 3. Development Phases

- **Phase 1: Setup & Skeleton** (Steps 1-5): Repo init, structure, config, basic CLI.
- **Phase 2: Knowledge Graph** (Steps 6-10): SQLite impl, basic CRUD.
- **Phase 3: Rust Core** (Steps 11-20): Engines in Rust, bindings.
- **Phase 4: TS Propagation** (Steps 21-25): Algo impl.
- **Phase 5: CIG Generators** (Steps 26-30): Outputs.
- **Phase 6: Hypothesis & Similarity** (Steps 31-35): Advanced features.
- **Phase 7: Testing & Optimization** (Steps 36-40): Validate, tune.
- **Phase 8: Finalization** (Steps 41-42): Docs, scaling notes.
- **Phase 9: Search and Config** (Steps 43-45): Optional online search module, config and .env, connectivity check and warnings.
- **Phase 10: Autonomous Loop** (Steps 46-49): Query generator, autonomous exploration loop, integration with run_pipeline and KG.
- **Phase 11: UI Integration** (Steps 50-53): Autonomous Exploration step and checkbox, warnings, env overrides.
- **Phase 12: Testing and Docs** (Steps 54-58): Tests for search and autonomous, docs, request cap, integration test, plan reference.

---

## 4. Step-by-Step Implementation Plan

Each step is self-contained for autonomous execution.

### Step 1
**Objective**: Initialize the GitHub repository and create base structure based on GOAT-TS-SUPERLITE.
**Detailed Explanation**: Clone or create "GOAT-TS" repo, add directories/files from SUPERLITE, adapt .gitignore for Python/Rust/SQLite artifacts.
**Files to Create or Modify**:
- Create root: GOAT-TS/
- Create dirs: data/, examples/, python/, rust/src/, tests/
- Create: .gitignore (content: __pycache__/\n*.pyc\n*.pyo\n*.egg-info/\nrust/target/\n*.db\n*.log)
- Create: requirements.txt (content: pyo3\nmaturin\npytest\nsqlite3  # minimal)
- Create: config.yaml (YAML: graph: path: data/knowledge_graph.db\nwave: ticks: 10\ndecay: 0.9\nactivation_threshold: 0.5)
- Create: run.py (basic Python script: print("GOAT-TS CIG initialized"))
- Create: run_tests.py (import pytest; pytest.main())
**Exact Folder Locations**: All in root except rust/src/.
**Code Examples**: In run.py: ```python:disable-run
**Testing Instructions**: Run `python run.py` from root.
**Expected Outcome**: Outputs "GOAT-TS CIG initialized". Git commit: "Step 1: Repo skeleton".

### Step 2
**Objective**: Add cross-platform setup scripts from GOAT-TS-LITE.
**Detailed Explanation**: Port setup scripts for low-end install, ensuring deps and env setup.
**Files to Create or Modify**:
- Create: setup_lowend.sh (content: #!/bin/bash\npip install -r requirements.txt\nrustup install stable\ncargo build --manifest-path=rust/Cargo.toml)
- Create: setup_windows.ps1 (content: pip install -r requirements.txt\nrustup install stable\ncargo build --manifest-path=rust/Cargo.toml)
**Exact Folder Locations**: Root.
**Code Examples**: N/A (shell scripts).
**Testing Instructions**: Run setup_lowend.sh (Linux/Mac) or setup_windows.ps1 (Windows); verify deps installed.
**Expected Outcome**: Deps ready, Rust toolchain present. Commit: "Step 2: Setup scripts".

### Step 3
**Objective**: Initialize Rust project with Cargo and PyO3.
**Detailed Explanation**: Setup Rust lib for bindings, using maturin for dev.
**Files to Create or Modify**:
- Create: rust/Cargo.toml (content: [package]\nname = "goat_ts_core"\nversion = "0.1.0"\nedition = "2021"\n[lib]\nname = "goat_ts_core"\ncrate-type = ["cdylib"]\n[dependencies]\npyo3 = { version = "0.20", features = ["extension-module"] })
- Create: rust/src/lib.rs (basic: use pyo3::prelude::*; #[pymodule] fn goat_ts_core(_py: Python, m: &PyModule) -> PyResult<()> { Ok(()) })
**Exact Folder Locations**: rust/, rust/src/.
**Code Examples**: As above.
**Testing Instructions**: Run `cd rust; maturin develop` from root; then in Python: import goat_ts_core.
**Expected Outcome**: Rust module importable in Python. Commit: "Step 3: Rust init".

### Step 4
**Objective**: Add Python bindings stub from GOAT-TS-SUPERLITE.
**Detailed Explanation**: Create Python wrapper for Rust lib.
**Files to Create or Modify**:
- Create dir: python/bindings/
- Create: python/bindings/rust_bindings.py (content: try: import goat_ts_core except ImportError: print("Rust extension not built"); class Dummy: pass; goat_ts_core = Dummy())
**Exact Folder Locations**: python/bindings/.
**Code Examples**: As above, with fallback to pure Python.
**Testing Instructions**: Run Python interpreter: from bindings.rust_bindings import goat_ts_core.
**Expected Outcome**: Imports without error (uses dummy if not built). Commit: "Step 4: Bindings stub".

### Step 5
**Objective**: Add basic CLI interface in main.py, integrating config.
**Detailed Explanation**: Parse args (--seed), load config, print placeholder output.
**Files to Create or Modify**:
- Create dir: python/goat_ts_cig/
- Create: python/goat_ts_cig/main.py (use argparse, yaml.safe_load for config)
- Modify: run.py (import sys; sys.path.append('python'); from goat_ts_cig.main import main; main())
**Exact Folder Locations**: python/goat_ts_cig/.
**Code Examples**: In main.py: ```python\nimport argparse\nimport yaml\ndef main():\n    parser = argparse.ArgumentParser()\n    parser.add_argument('--seed', required=True)\n    args = parser.parse_args()\n    with open('config.yaml') as f:\n        config = yaml.safe_load(f)\n    print(f"Seed: {args.seed}, Config: {config}")\nif __name__ == '__main__': main()```
**Testing Instructions**: python run.py --seed "test"
**Expected Outcome**: Prints seed and config. Commit: "Step 5: Basic CLI".

### Step 6
**Objective**: Implement Knowledge Graph Engine in Python using SQLite.
**Detailed Explanation**: Create DB schema: nodes (id, label, mass:float, activation:float, state:str, metadata:str), edges (from_id, to_id, type:str, weight:float).
**Files to Create or Modify**:
- Create: python/goat_ts_cig/knowledge_graph.py
**Exact Folder Locations**: python/goat_ts_cig/.
**Code Examples**: ```python\nimport sqlite3\nclass KnowledgeGraph:\n    def __init__(self, path):\n        self.conn = sqlite3.connect(path)\n        self.create_tables()\n    def create_tables(self):\n        self.conn.execute('''CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY, label TEXT, mass REAL, activation REAL, state TEXT, metadata TEXT)''')\n        self.conn.execute('''CREATE TABLE IF NOT EXISTS edges (from_id INTEGER, to_id INTEGER, type TEXT, weight REAL)''')\n        self.conn.commit()\n    def add_node(self, label, mass=1.0, activation=0.0, state='DORMANT', metadata=''):\n        cur = self.conn.cursor()\n        cur.execute('INSERT INTO nodes (label, mass, activation, state, metadata) VALUES (?, ?, ?, ?, ?)', (label, mass, activation, state, metadata))\n        self.conn.commit()\n        return cur.lastrowid\n    # Add similar for add_edge, get_node, etc.```
**Testing Instructions**: In tests/test_graph.py: Create KG, add node, assert exists.
**Expected Outcome**: DB created in data/, nodes/edges manageable. Commit: "Step 6: KG Engine".

### Step 7
**Objective**: Integrate KG into main.py for seed node addition.
**Detailed Explanation**: On --seed, add node if not exists, set activation=1.0.
**Files to Create or Modify**:
- Modify: python/goat_ts_cig/main.py (import KnowledgeGraph; kg = KnowledgeGraph(config['graph']['path']); node_id = kg.add_node(args.seed, activation=1.0))
**Exact Folder Locations**: As above.
**Code Examples**: Add to main(): Above code.
**Testing Instructions**: python run.py --seed "AI"; Check data/knowledge_graph.db has node.
**Expected Outcome**: Seed node added with high activation. Commit: "Step 7: Seed Integration".

### Step 8
**Objective**: Add data ingestion from text/files.
**Detailed Explanation**: Simple text parser to extract concepts/relations (regex-based, no LLM).
**Files to Create or Modify**:
- Modify: knowledge_graph.py (add ingest_text method: split words, add nodes, link sequential).
**Exact Folder Locations**: As above.
**Code Examples**: ```python\def ingest_text(self, text):\n    words = text.split()\n    prev_id = None\n    for word in words:\n        node_id = self.add_node(word)\n        if prev_id:\n            self.add_edge(prev_id, node_id, 'relates', 1.0)\n        prev_id = node_id```
**Testing Instructions**: Test ingest, assert nodes/edges.
**Expected Outcome**: Text → graph population. Commit: "Step 8: Ingestion".

### Step 9
**Objective**: Add graph export to JSON for debugging.
**Detailed Explanation**: Dump nodes/edges to dict.
**Files to Create or Modify**:
- Modify: knowledge_graph.py (add to_json method).
**Exact Folder Locations**: As above.
**Code Examples**: ```python\def to_json(self):\n    nodes = self.conn.execute('SELECT * FROM nodes').fetchall()\n    edges = self.conn.execute('SELECT * FROM edges').fetchall()\n    return {'nodes': [dict(row) for row in nodes], 'edges': [dict(row) for row in edges]}```
**Testing Instructions**: Print json after seed.
**Expected Outcome**: JSON output. Commit: "Step 9: Export".

### Step 10
**Objective**: Add optional local LLM stub (placeholder).
**Detailed Explanation**: For future, but stub for now (no dep).
**Files to Create or Modify**:
- Create: python/goat_ts_cig/llm_stub.py (def generate(text): return "stub response")
**Exact Folder Locations**: python/goat_ts_cig/.
**Code Examples**: As above.
**Testing Instructions**: Import and call.
**Expected Outcome**: Placeholder for ingestion enhancement. Commit: "Step 10: LLM Stub".

### Step 11
**Objective**: Implement basic Graph Engine in Rust.
**Detailed Explanation**: Rust struct for in-memory graph mirror (Vec<Node>, Vec<Edge>), for fast ops.
**Files to Create or Modify**:
- Modify: rust/src/lib.rs (add mod graph_engine; use graph_engine::*;)
- Create: rust/src/graph_engine.rs
**Exact Folder Locations**: rust/src/.
**Code Examples**: In graph_engine.rs: ```rust\n#[derive(Clone)]\npub struct Node { id: u32, label: String, mass: f64, activation: f64, state: String }\npub struct Edge { from: u32, to: u32, typ: String, weight: f64 }\npub struct Graph { nodes: Vec<Node>, edges: Vec<Edge> }\nimpl Graph {\n    pub fn new() -> Self { Graph { nodes: vec![], edges: vec![] } }\n    pub fn add_node(&mut self, label: String) -> u32 {\n        let id = self.nodes.len() as u32;\n        self.nodes.push(Node { id, label, mass: 1.0, activation: 0.0, state: "DORMANT".to_string() });\n        id\n    }\n    // add_edge, etc.\n}```
**Testing Instructions**: Cargo test in rust/.
**Expected Outcome**: Rust graph ops. Commit: "Step 11: Rust Graph".

### Step 12
**Objective**: Expose Graph Engine to Python via PyO3.
**Detailed Explanation**: Add pymethods for Graph.
**Files to Create or Modify**:
- Modify: rust/src/lib.rs (add #[pyclass] to structs, #[pymethods] impl).
**Exact Folder Locations**: As above.
**Code Examples**: ```rust\n#[pyclass]\nstruct PyGraph { inner: Graph }\n#[pymethods]\nimpl PyGraph {\n    #[new]\n    fn new() -> Self { PyGraph { inner: Graph::new() } }\n    fn add_node(&mut self, label: String) -> u32 { self.inner.add_node(label) }\n}```
**Testing Instructions**: maturin develop; Python: g = PyGraph(); g.add_node("test")
**Expected Outcome**: Python-accessible graph. Commit: "Step 12: Graph Bindings".

### Step 13
**Objective**: Implement Wave Propagation Engine in Rust.
**Detailed Explanation**: Core TS algo: Activate seed, spread to neighbors with decay, multi-thread (rayon if low-overhead).
**Files to Create or Modify**:
- Create: rust/src/wave_engine.rs (fn propagate(graph: &mut Graph, seed_id: u32, ticks: u32, decay: f64))
**Exact Folder Locations**: rust/src/.
**Code Examples**: ```rust\nuse std::collections::VecDeque;\npub fn propagate(graph: &mut Graph, seed_id: u32, ticks: u32, decay: f64) {\n    if let Some(node) = graph.nodes.get_mut(seed_id as usize) { node.activation = 1.0; }\n    for _ in 0..ticks {\n        let mut queue = VecDeque::new();\n        for i in 0..graph.nodes.len() {\n            if graph.nodes[i].activation > 0.0 { queue.push_back(i as u32); }\n        }\n        while let Some(id) = queue.pop_front() {\n            // Find edges, spread activation * weight * decay\n            for edge in &graph.edges {\n                if edge.from == id {\n                    if let Some(target) = graph.nodes.get_mut(edge.to as usize) {\n                        target.activation += graph.nodes[id as usize].activation * edge.weight * decay;\n                    }\n                }\n            }\n        }\n    }\n}```
**Testing Instructions**: Add unit test: create graph, propagate, assert activations.
**Expected Outcome**: Activation spreads. Commit: "Step 13: Wave Engine".

### Step 14
**Objective**: Add constraint interaction to Wave Engine.
**Detailed Explanation**: For each tick, resolve constraints (e.g., if edge type='conflict', reduce activation).
**Files to Create or Modify**:
- Create: rust/src/constraint_engine.rs (fn resolve_constraints(graph: &mut Graph))
**Exact Folder Locations**: rust/src/.
**Code Examples**: ```rust\npub fn resolve_constraints(graph: &mut Graph) {\n    for edge in &graph.edges {\n        if edge.typ == "conflict" {\n            let from_act = graph.nodes[edge.from as usize].activation;\n            let to_act = graph.nodes[edge.to as usize].activation;\n            let avg = (from_act + to_act) / 2.0;\n            graph.nodes[edge.from as usize].activation = avg * 0.8; // Dampen\n            graph.nodes[edge.to as usize].activation = avg * 0.8;\n        }\n    }\n}```
**Testing Instructions**: Test with conflict edge, assert dampening.
**Expected Outcome**: Constraints affect propagation. Commit: "Step 14: Constraint Engine".

### Step 15
**Objective**: Implement Similarity Engine in Rust.
**Detailed Explanation**: Simple Jaccard similarity for labels (no embeddings for low-mem).
**Files to Create or Modify**:
- Create: rust/src/similarity_engine.rs (fn find_similar(graph: &Graph, id: u32, threshold: f64) -> Vec<u32>)
**Exact Folder Locations**: rust/src/.
**Code Examples**: ```rust\nfn jaccard(a: &str, b: &str) -> f64 { /* impl set intersection over union */ }\npub fn find_similar(graph: &Graph, id: u32, threshold: f64) -> Vec<u32> {\n    let label = &graph.nodes[id as usize].label;\n    graph.nodes.iter().enumerate().filter_map(|(i, n)| {\n        if i as u32 != id && jaccard(label, &n.label) > threshold { Some(i as u32) } else { None }\n    }).collect()\n}```
**Testing Instructions**: Test similar nodes.
**Expected Outcome**: Returns similar IDs. Commit: "Step 15: Similarity Engine".

### Step 16
**Objective**: Expose all Rust engines via PyO3.
**Detailed Explanation**: Add pyfunctions for propagate, resolve, find_similar.
**Files to Create or Modify**:
- Modify: rust/src/lib.rs (m.add_function(wrap_pyfunction!(propagate, m)?); etc.)
**Exact Folder Locations**: As above.
**Code Examples**: Use wrap_pyfunction! for each.
**Testing Instructions**: maturin develop; Python test calls.
**Expected Outcome**: All callable from Python. Commit: "Step 16: Full Bindings".

### Step 17
**Objective**: Integrate Rust Graph with Python KG (sync mechanism).
**Detailed Explanation**: Load SQLite to Rust Graph for compute, sync back.
**Files to Create or Modify**:
- Modify: knowledge_graph.py (add to_rust_graph, from_rust_graph methods).
**Exact Folder Locations**: As above.
**Code Examples**: ```python\ndef to_rust_graph(self):\n    from bindings.rust_bindings import PyGraph\n    rg = PyGraph()\n    node_map = {}\n    for row in self.conn.execute('SELECT id, label, mass, activation, state FROM nodes'):\n        nid = rg.add_node(row[1])\n        node_map[row[0]] = nid\n        # Set props\n    for row in self.conn.execute('SELECT from_id, to_id, type, weight FROM edges'):\n        rg.add_edge(node_map[row[0]], node_map[row[1]], row[2], row[3])\n    return rg```
**Testing Instructions**: Load, assert Rust graph matches.
**Expected Outcome**: Seamless sync. Commit: "Step 17: Graph Sync".

### Step 18
**Objective**: Add multi-threaded support in Rust (using rayon for propagation).
**Detailed Explanation**: Parallelize spread loop if nodes > threshold.
**Files to Create or Modify**:
- Modify: Cargo.toml (add rayon = "1.5")
- Modify: wave_engine.rs (use rayon::prelude::*; par_iter for queue processing).
**Exact Folder Locations**: As above.
**Code Examples**: ```rust\nuse rayon::prelude::*;\n// In propagate: queue.par_iter().for_each(|&id| { /* spread */ });```
**Testing Instructions**: Benchmark on multi-core.
**Expected Outcome**: Faster on low-end multi-thread. Commit: "Step 18: Multi-thread".

### Step 19
**Objective**: Add convergence detection in Wave Engine.
**Detailed Explanation**: Stop if activations change < epsilon over ticks.
**Files to Create or Modify**:
- Modify: wave_engine.rs (add prev_acts vec, check delta).
**Exact Folder Locations**: As above.
**Code Examples**: ```rust\nlet mut prev_acts = vec![0.0; graph.nodes.len()];\n// After spread: let delta = graph.nodes.iter().zip(&prev_acts).map(|(n, p)| (n.activation - *p).abs()).sum::<f64>();\nif delta < 0.01 { break; }```
**Testing Instructions**: Test early stop.
**Expected Outcome**: Efficient termination. Commit: "Step 19: Convergence".

### Step 20
**Objective**: Optimize Rust for low-mem (use compact structs).
**Detailed Explanation**: Use u16 for IDs if graph small, f32 instead of f64.
**Files to Create or Modify**:
- Modify: structs (id: u16, mass: f32, etc.)
**Exact Folder Locations**: As above.
**Code Examples**: Change types, test.
**Testing Instructions**: Measure mem usage.
**Expected Outcome**: Reduced footprint. Commit: "Step 20: Mem Opt".

### Step 21
**Objective**: Design and implement full TS Propagation Algorithm.
**Detailed Explanation**: Combine propagate + resolve + decay per tick; states update (if act<0.1 → DORMANT).
**Files to Create or Modify**:
- Modify: wave_engine.rs (fn full_ts_cycle(graph: &mut Graph, seed: u32, ticks: u32, decay: f64) { for t in 0..ticks { propagate(...); resolve_constraints(...); apply_decay(graph, decay); update_states(graph); } })
**Exact Folder Locations**: As above.
**Code Examples**: Add apply_decay: nodes.iter_mut().for_each(|n| n.activation *= decay); update_states: if n.activation < 0.1 { n.state = "DORMANT" } else if >0.5 { "ACTIVE" } else { "DEEP" }
**Testing Instructions**: Full cycle test.
**Expected Outcome**: Emergent clusters. Commit: "Step 21: TS Algo".

### Step 22
**Objective**: Integrate TS into main.py.
**Detailed Explanation**: After seed, sync to Rust, run full_ts_cycle, sync back.
**Files to Create or Modify**:
- Modify: main.py (rg = kg.to_rust_graph(); goat_ts_core.full_ts_cycle(rg.inner, seed_id, config['wave']['ticks'], config['wave']['decay']); kg.from_rust_graph(rg))
**Exact Folder Locations**: As above.
**Code Examples**: Assume bindings expose full_ts_cycle.
**Testing Instructions**: Run with seed, check activations updated.
**Expected Outcome**: Graph updated post-propagation. Commit: "Step 22: TS Integration".

### Step 23
**Objective**: Add decay and state transitions.
**Detailed Explanation**: Already in Rust; expose if needed.
**Files to Create or Modify**: N/A (covered in 21).
**Testing Instructions**: Verify states change.
**Expected Outcome**: Dynamic states. Commit: "Step 23: Decay/States".

### Step 24
**Objective**: Add influence score computation.
**Detailed Explanation**: Post-propagation, compute cluster influence (sum activations in cluster).
**Files to Create or Modify**:
- Modify: wave_engine.rs (fn compute_influence(graph: &Graph) -> f64 { graph.nodes.iter().map(|n| n.activation).sum() })
**Exact Folder Locations**: As above.
**Code Examples**: As above.
**Testing Instructions**: Test sum.
**Expected Outcome**: Aggregate score. Commit: "Step 24: Influence".

### Step 25
**Objective**: Handle large graphs (pagination in sync).
**Detailed Explanation**: For low-RAM, batch load nodes/edges.
**Files to Create or Modify**:
- Modify: knowledge_graph.py (batch in to_rust_graph).
**Exact Folder Locations**: As above.
**Code Examples**: Use LIMIT/OFFSET in SQL.
**Testing Instructions**: Test with 1000 nodes.
**Expected Outcome**: No OOM. Commit: "Step 25: Large Graph".

### Step 26
**Objective**: Implement CIG Generator for Idea Maps.
**Detailed Explanation**: Extract subgraph around seed (BFS depth 2), format as dict.
**Files to Create or Modify**:
- Create: python/goat_ts_cig/cig_generator.py (def generate_idea_map(kg, seed_id): # BFS, return {'center': ..., 'related': [...]} )
**Exact Folder Locations**: python/goat_ts_cig/.
**Code Examples**: Use queue for BFS.
**Testing Instructions**: Generate, assert structure.
**Expected Outcome**: Map output. Commit: "Step 26: Idea Maps".

### Step 27
**Objective**: Add Context Expansion.
**Detailed Explanation**: Find clusters (connected components with high activation).
**Files to Create or Modify**:
- Modify: cig_generator.py (def generate_context_expansion(kg): # Union-find or DFS for clusters)
**Exact Folder Locations**: As above.
**Code Examples**: Impl union-find in Python.
**Testing Instructions**: Post-propagation, clusters.
**Expected Outcome**: Grouped knowledge. Commit: "Step 27: Context Expansion".

### Step 28
**Objective**: Add Evidence Chains.
**Detailed Explanation**: Shortest path or all paths between nodes.
**Files to Create or Modify**:
- Modify: cig_generator.py (def generate_evidence_chain(kg, from_id, to_id): # Dijkstra)
**Exact Folder Locations**: As above.
**Code Examples**: Use heapq for Dijkstra.
**Testing Instructions**: Path exists.
**Expected Outcome**: Connection paths. Commit: "Step 28: Evidence Chains".

### Step 29
**Objective**: Integrate CIG into main.py.
**Detailed Explanation**: After TS, call generators, print JSON.
**Files to Create or Modify**:
- Modify: main.py (import cig_generator; maps = cig_generator.generate_idea_map(...); print(json.dumps(maps)))
**Exact Folder Locations**: As above.
**Code Examples**: Add --json flag.
**Testing Instructions**: Run --seed --json, valid JSON.
**Expected Outcome**: Full outputs. Commit: "Step 29: CIG Integration".

### Step 30
**Objective**: Add output formatting (text/JSON).
**Detailed Explanation**: Pretty-print for CLI.
**Files to Create or Modify**:
- Modify: main.py (if not json: print formatted text)
**Exact Folder Locations**: As above.
**Code Examples**: Use pprint.
**Testing Instructions**: Non-json output readable.
**Expected Outcome**: User-friendly. Commit: "Step 30: Output".

### Step 31
**Objective**: Implement Hypothesis Engine.
**Detailed Explanation**: Detect weak connections (similar but no edge), suggest links.
**Files to Create or Modify**:
- Create: python/goat_ts_cig/hypothesis_engine.py (def generate_hypotheses(kg, rust_sim): similar = rust_sim.find_similar(...); for pair if no edge: suggest)
**Exact Folder Locations**: python/goat_ts_cig/.
**Code Examples**: Return list of {"from":, "to":, "reason": "similarity > thresh"}
**Testing Instructions**: Suggest on test graph.
**Expected Outcome**: Hypotheses list. Commit: "Step 31: Hypothesis Engine".

### Step 32
**Objective**: Integrate Hypothesis into CIG.
**Detailed Explanation**: Add to generate outputs.
**Files to Create or Modify**:
- Modify: cig_generator.py (call hypothesis_engine)
**Exact Folder Locations**: As above.
**Code Examples**: Append to output dict.
**Testing Instructions**: Hypotheses in output.
**Expected Outcome**: Complete CIG. Commit: "Step 32: Hypothesis Integration".

### Step 33
**Objective**: Enhance Similarity with contextual (post-propagation).
**Detailed Explanation**: Weight by activation.
**Files to Create or Modify**:
- Modify: similarity_engine.rs (multiply jaccard by act)
**Exact Folder Locations**: As above.
**Code Examples**: In find_similar: > threshold * n.activation
**Testing Instructions**: Test weighted.
**Expected Outcome**: Context-aware. Commit: "Step 33: Contextual Sim".

### Step 34
**Objective**: Add anomaly detection for hypotheses.
**Detailed Explanation**: High tension: act mismatch on conflict edges.
**Files to Create or Modify**:
- Modify: hypothesis_engine.py (scan edges, if conflict and |act_diff| > thresh: hypothesize resolution)
**Exact Folder Locations**: As above.
**Code Examples**: From GOAT-TS tension.
**Testing Instructions**: Detect.
**Expected Outcome**: Tension-based. Commit: "Step 34: Anomaly".

### Step 35
**Objective**: Optional LLM for hypothesis refinement (stub).
**Detailed Explanation**: If enabled, use stub to phrase suggestions.
**Files to Create or Modify**:
- Modify: hypothesis_engine.py (if config['llm']: llm_stub.generate(...))
**Exact Folder Locations**: As above.
**Code Examples**: Append natural lang.
**Testing Instructions**: With/without.
**Expected Outcome**: Enhanced output. Commit: "Step 35: LLM Hypothesis".

### Step 36
**Objective**: Add unit tests for all modules.
**Detailed Explanation**: Pytest for Python, Cargo for Rust.
**Files to Create or Modify**:
- Create: tests/test_graph.py, test_wave.py, etc.
**Exact Folder Locations**: tests/.
**Code Examples**: def test_add_node(): kg = KnowledgeGraph(':memory:'); id = kg.add_node("test"); assert id == 1
**Testing Instructions**: python run_tests.py
**Expected Outcome**: 100% coverage. Commit: "Step 36: Unit Tests".

### Step 37
**Objective**: Add integration tests for full pipeline.
**Detailed Explanation**: Seed → propagate → generate → assert outputs.
**Files to Create or Modify**:
- Create: tests/test_full.py
**Exact Folder Locations**: tests/.
**Code Examples**: Run main with args, check JSON.
**Testing Instructions**: pytest tests/
**Expected Outcome**: End-to-end. Commit: "Step 37: Integration Tests".

### Step 38
**Objective**: Add benchmarks from DEVELOPMENT.
**Detailed Explanation**: Time propagation on N nodes.
**Files to Create or Modify**:
- Create: benchmark.py (use timeit on full cycle)
**Exact Folder Locations**: Root.
**Code Examples**: timeit.timeit(lambda: full_ts_cycle(...), number=10)
**Testing Instructions**: python benchmark.py
**Expected Outcome**: Perf metrics. Commit: "Step 38: Benchmarks".

### Step 39
**Objective**: Optimize for low-end (profile, reduce allocations).
**Detailed Explanation**: Use cargo flamegraph or Python cProfile.
**Files to Create or Modify**:
- Create: OPTIMIZATION.md (notes from runs)
**Exact Folder Locations**: Root.
**Code Examples**: N/A.
**Testing Instructions**: Profile, apply fixes (e.g., reuse vecs in Rust).
**Expected Outcome**: <1s on 1000 nodes. Commit: "Step 39: Optimization".

### Step 40
**Objective**: Add error handling and logging.
**Detailed Explanation**: Try/except, println! in Rust.
**Files to Create or Modify**:
- All modules (add logs).
**Exact Folder Locations**: All.
**Code Examples**: use log crate in Rust.
**Testing Instructions**: Induce error, check log.
**Expected Outcome**: Robust. Commit: "Step 40: Handling".

### Step 41
**Objective**: Document in README.md.
**Detailed Explanation**: Include setup, usage, design.
**Files to Create or Modify**:
- Create: README.md (from SUPERLITE, add new)
**Exact Folder Locations**: Root.
**Code Examples**: Markdown sections.
**Testing Instructions**: N/A.
**Expected Outcome**: Complete docs. Commit: "Step 41: Docs".

### Step 42
**Objective**: Add scaling strategy notes.
**Detailed Explanation**: For future: Shard SQLite, distributed Rust workers.
**Files to Create or Modify**:
- Create: SCALING.md
**Exact Folder Locations**: Root.
**Code Examples**: Text on sharding.
**Testing Instructions**: N/A.
**Expected Outcome**: Roadmap. Commit: "Step 42: Scaling".

---

## 5. Rust Module Design
- **lib.rs**: Entry, exports modules.
- **graph_engine.rs**: Graph struct, CRUD.
- **wave_engine.rs**: Propagation, decay, states.
- **constraint_engine.rs**: Resolution logic.
- **similarity_engine.rs**: Jaccard-based search.
- All use compact types, rayon for parallel.

## 6. Python Module Design
- **knowledge_graph.py**: SQLite wrapper, sync.
- **cig_generator.py**: Output generators.
- **hypothesis_engine.py**: Suggestion algos.
- **main.py**: Orchestrate.
- **rust_bindings.py**: Import wrapper.

## 7. PyO3 Binding Implementation
- Use #[pyclass], #[pymethods], wrap_pyfunction!.
- Fallback pure Python impls for non-critical.

## 8. TS Propagation Algorithm Design
- Input: Seed, ticks, decay, threshold.
- Loop: Activate → Spread (BFS/parallel) → Resolve constraints → Decay → Update states → Check convergence.
- Output: Updated graph.

## 9. Knowledge Graph Storage Strategy
- SQLite: nodes/edges tables, indexes on id/label.
- Backup: Serialize to JSON if DB fails.
- Limit: 10k nodes for low-RAM.

## 10. Context Generation Pipeline
- Post-TS: Cluster (DFS) → Maps (BFS) → Chains (Dijkstra) → Hypotheses (sim + tension).

## 11. Hypothesis Generation Algorithm
- Scan similar unpaired → Suggest edge.
- Scan tension edges → Suggest resolution.
- Rank by score (sim * act_diff).

## 12. CLI Interface
- Args: --seed, --ingest-file, --json, --ticks.
- Env: Override config (e.g., CIG_DECAY=0.8).

## 13. Testing Strategy
- Unit: Per function.
- Integration: Pipeline.
- Perf: Benchmarks < thresholds.
- Coverage: >90%.

## 14. Performance Optimization
- Rust for loops.
- Batch DB.
- Early convergence.
- Profile-guided.

## 15. Scaling Strategy
- Short-term: In-mem caches.
- Long: Multiple DB files, Rust actors for dist.
- GPU: Optional via roc if needed.

This plan is complete; execute sequentially in Cursor.

---

# ADDENDUM: Optional UI and Autonomous Online Exploration (Steps 43–58)

## Document Metadata (Addendum)
- **Version**: 1.1 (Addendum)
- **Date**: March 2026
- **Purpose**: Extend the CIG implementation with an optional Streamlit UI and an optional "Autonomous Exploration Mode" in which the system uses online search (minimal, ethical) to build and expand the knowledge graph iteratively. Designed for execution by an autonomous coding agent; no clarification required.
- **Scope**: UI remains lightweight (no GPU, low RAM). Online search is optional; users are warned when network or API keys are missing. CLI remains primary; UI runs locally via `python -m streamlit run app_ui.py`.

---

## Addendum §1. Analysis and Integration with Existing Plan and Repositories

### 1.1 Relation to Existing PLAN.md (Steps 1–42)
- Steps 1–42 already deliver: repo skeleton, KG (SQLite), Rust engines (graph, wave, constraint, similarity), CIG generators (idea map, context expansion, evidence chains, hypotheses), CLI, tests, docs. The codebase has `app_ui.py` (Streamlit) at project root with Setup, Configuration, Run & Explore, Optional Tools.
- This addendum **builds on** that UI and does **not** replace it: add a new sidebar step "5. Autonomous Exploration," a new Python module for the autonomous loop, a lightweight search module, and config/env for online options. All online features are **optional** and **off by default**.

### 1.2 Reuse from GOAT-TS Repositories
- **GOAT-TS (scripts/goat_ts_gui.py)**: Setup Wizard (step progress, run_cmd, session state for deps_ok/docker_ok/connect_ok), Config Editor (load/save YAML, expanders per section), buttons for actions (Install, Check status), optional background task pattern (`_run_wizard_task` with threading). **Adapt**: No Docker/NebulaGraph; reuse wizard-style progress, config load/save, and button-triggered subprocess or in-process runs.
- **GOAT-TS (scripts/streamlit_viz.py)**: Simple sidebar radio for mode, slider for parameters, "Run demo" button, display of JSON and metrics. **Adapt**: Same pattern for "Run pipeline" vs "Run autonomous exploration" and for iteration count / max searches.
- **GOAT-TS-LITE (streamlit_app.py)**: Lightweight Streamlit for low-end; keep the same principle (minimal widgets, no heavy charts).
- **Existing CIG-APP app_ui.py**: Already has steps 1–4 (Setup, Configuration, Run & Explore, Optional Tools). Add step "5. Autonomous Exploration" in the sidebar and a new page; add checkbox "Autonomous Exploration Mode" in Run & Explore that switches behavior to the autonomous loop when "Run pipeline" is clicked.

### 1.3 Hardware and Dependency Constraints
- No new heavy dependencies: add only `requests` and `beautifulsoup4` (or a single optional extra: `duckduckgo-search` for search without API key). Streamlit is already in requirements.txt. Prefer one lightweight search path (e.g. DuckDuckGo HTML or duckduckgo-search) to keep install small.
- Autonomous loop must run in-process (no separate GPU process); each "cycle" = one or a few HTTP requests, ingest into KG, one TS run. Cap total requests per autonomous run (e.g. 5 cycles × 3 queries × 2 URLs = 30 requests max) to avoid long runs on low-end hardware.

---

## Addendum §2. Updated Architecture Proposal

### 2.1 New Components (All Optional)
- **UI (existing app_ui.py extended)**: New sidebar step "5. Autonomous Exploration" and optional checkbox in "Run & Explore" to enable Autonomous Mode. No new entrypoint; same `app_ui.py`.
- **Autonomous exploration module** (`python/goat_ts_cig/autonomous_explore.py`): Single entry function `run_autonomous_explore(seed_query, config, max_cycles=5, max_queries_per_cycle=3, ...)` that loops: reflect on current graph → generate next search query(ies) → fetch via search module → ingest into KG → run TS propagation → repeat. Returns same structure as `run_pipeline` (seed, node_id, cig, graph, config, rust_used, plus list of cycles with queries and ingested counts).
- **Search module** (`python/goat_ts_cig/search_fetcher.py`): `search_web(query, max_results=5)` returning list of `{"title", "snippet", "url", "body"}` (body optional, from fetch). Implementation: prefer DuckDuckGo (no API key) via `duckduckgo-search` or requests + HTML parsing; no Google Custom Search unless user supplies API key in .env. Rate-limit and timeout every request.
- **Config and env**: In `config.yaml` add optional section `online: { enabled: false, max_requests_per_run: 30, timeout_seconds: 10 }`. In `.env` (or .env.example): `CIG_SEARCH_API_KEY=` (optional), `CIG_ONLINE_ENABLED=0`. If `online.enabled` is false or env disables it, UI shows a warning and does not perform network requests; autonomous mode can still run in "local-only" (expand queries from graph labels only, no fetch).

### 2.2 Architecture Diagram (Addendum)

```
User enables "Autonomous Exploration" in UI and clicks Run
  ↓
app_ui.py → run_autonomous_explore(seed, config, max_cycles=5, ...)
  ↓
autonomous_explore.py
  ├── cycle 1..N:
  │     ├── query_generator: next_queries(graph, seed, cycle)  [heuristic or LLM stub]
  │     ├── search_fetcher.search_web(q)  [optional; skip if no net / disabled]
  │     ├── kg.ingest_text(snippet/body) for each result
  │     ├── run_pipeline(seed, ...)  [TS + CIG]
  │     └── reflect: update graph state for next cycle
  ↓
Return { seed, node_id, cig, graph, config, rust_used, cycles: [{ queries, ingested }] }
  ↓
UI displays same tabs (Idea map, Context, Hypotheses, Graph, JSON) + Autonomous summary
```

### 2.3 Data Flow for Search and Ingestion
- `search_fetcher.search_web(query)` → list of result dicts.
- Each result: at least `title`, `snippet`; optionally `body` (page text, truncated) for better ingestion. `body` is fetched only if config allows and timeout is set (e.g. one request per result URL, max 2–5 URLs per query).
- Ingestion: for each result, call `kg.ingest_text(snippet)` or `kg.ingest_text(body)` if body present. Existing `ingest_text` splits on whitespace and links sequential; no change to KG schema. Optionally link the new subgraph to the seed node with one edge (seed_id → first new node) so TS propagates from seed into new content.

---

## Addendum §3. New Development Phases

- **Phase 9: Search and Config** (Steps 43–45): Lightweight search module, config and .env for online, connectivity check and warnings.
- **Phase 10: Autonomous Loop** (Steps 46–49): Query generator (heuristic), autonomous_explore loop, integration with run_pipeline and KG.
- **Phase 11: UI Integration** (Steps 50–53): Add "Autonomous Exploration" step and checkbox, wire run_autonomous_explore, show warnings and results.
- **Phase 12: Testing and Docs** (Steps 54–58): Tests for search (mocked), autonomous (local-only), UI; docs and fallback behavior.

---

## Addendum §4. Step-by-Step Implementation Plan (Steps 43–58)

### Step 43
**Objective**: Add optional dependencies for online search and create `.env.example` for API keys and online toggle.
**Detailed Explanation**: Keep core requirements.txt minimal; add a separate optional list or comment for "online" deps. Create `.env.example` with placeholders so users can copy to `.env` and set keys if they use optional search APIs. Do not require API keys for the default DuckDuckGo path.
**Files to Create or Modify**:
- Create: `.env.example` at repository root.
- Modify: `requirements.txt` (add optional deps or a comment; see below).
- Modify: `.gitignore` (ensure `.env` is ignored if not already).
**Exact Folder Locations**: Repository root.
**Code Examples**:
- `.env.example` content:
```
# Optional: set to 1 to allow online search in Autonomous Exploration (default 0)
CIG_ONLINE_ENABLED=0
# Optional: for future Google Custom Search or other API (not required for DuckDuckGo)
CIG_SEARCH_API_KEY=
```
- In `requirements.txt` append new line(s):
```
# Optional for autonomous online exploration (install if using search):
# requests>=2.28
# beautifulsoup4>=4.11
# duckduckgo-search>=4.0
```
Or add a single optional extra: `requests`, `beautifulsoup4` (and optionally `duckduckgo-search`) so one `pip install -r requirements.txt` installs them; prefer adding them as real optional lines so agent can add them.
**Testing Instructions**: Ensure `.env` is in .gitignore; run `pip install -r requirements.txt` and confirm no error. Copy .env.example to .env and run app; no crash.
**Expected Outcome**: `.env.example` exists; optional deps documented or added; `.env` ignored. Commit: "Step 43: Optional online config and .env.example".

### Step 44
**Objective**: Implement lightweight search module in `search_fetcher.py` with DuckDuckGo (no API key) and optional fetch of page body.
**Detailed Explanation**: Create a module that, given a query string, returns a list of search results. Use `duckduckgo-search` if available (pip install duckduckgo-search), else fall back to a simple requests+BeautifulSoup fetch of DuckDuckGo HTML. Each result must have at least `title`, `snippet`, `url`. Optionally fetch `url` to get `body` (truncated to e.g. 2000 chars), with a per-request timeout (e.g. 5 s) and max 2–3 body fetches per query to keep latency low. If neither duckduckgo-search nor requests is available, the module should expose a stub that returns an empty list and a flag `search_available = False`.
**Files to Create or Modify**:
- Create: `python/goat_ts_cig/search_fetcher.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Code Examples**:
```python
# search_fetcher.py
"""Lightweight web search for autonomous exploration. Optional; no API key required for DuckDuckGo."""
from __future__ import annotations
import os
from typing import Any

SEARCH_AVAILABLE = False
try:
    from duckduckgo_search import DDGS
    SEARCH_AVAILABLE = True
except ImportError:
    try:
        import requests
        from bs4 import BeautifulSoup
        SEARCH_AVAILABLE = True
    except ImportError:
        pass

def search_web(query: str, max_results: int = 5, timeout_seconds: int = 10) -> list[dict[str, Any]]:
    if not SEARCH_AVAILABLE:
        return []
    results = []
    try:
        if "DDGS" in dir():
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({"title": r.get("title", ""), "snippet": r.get("body", ""), "url": r.get("href", "")})
        else:
            url = "https://html.duckduckgo.com/html/?q=" + requests.utils.quote(query)
            resp = requests.get(url, timeout=timeout_seconds, headers={"User-Agent": "CIG-APP/1.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select(".result__a")[:max_results]:
                results.append({"title": a.get_text(strip=True), "snippet": "", "url": a.get("href", "")})
    except Exception:
        results = []
    return results
```
(Agent should implement robustly: try duckduckgo_search first; if ImportError, try requests+BeautifulSoup; if still ImportError, set SEARCH_AVAILABLE=False and return []. Add optional body fetch with timeout and max 2–3 per query.)
**Testing Instructions**: Unit test: mock or skip if no network; test that search_web("test") returns list of dicts with title/snippet/url when deps and network available; test that when SEARCH_AVAILABLE is False, search_web returns [].
**Expected Outcome**: `search_fetcher.search_web(query)` returns up to max_results items; no crash when optional deps missing. Commit: "Step 44: Search fetcher module".

### Step 45
**Objective**: Add `online` section to config.yaml and load it in main/app_ui; add connectivity check and user-facing warning when online is disabled or unavailable.
**Detailed Explanation**: In config.yaml add:
```yaml
online:
  enabled: false
  max_requests_per_run: 30
  timeout_seconds: 10
```
Load this in the UI and in autonomous_explore. Add a function `check_online_available(config)` that returns (bool, message): True if config says enabled and search_fetcher.SEARCH_AVAILABLE is True (and optionally a quick socket check to 8.8.8.8 or similar); False with a short message otherwise (e.g. "Online search disabled in config", "Search dependencies not installed", "No network"). In the UI, when the user selects Autonomous Exploration, show a warning box if check_online_available is False, and offer "Run in local-only mode (no web search)" so the autonomous loop still runs but skips search and uses only heuristic query expansion from graph labels.
**Files to Create or Modify**:
- Modify: `config.yaml` (add `online` section).
- Create or modify: `python/goat_ts_cig/autonomous_explore.py` (stub that only defines `check_online_available` and reads config; full loop in Step 47).
- Modify: `app_ui.py` (in Run & Explore or Autonomous step, call check_online_available and show warning).
**Exact Folder Locations**: Root for config; `python/goat_ts_cig/` for module; root for app_ui.py.
**Code Examples**:
- In `autonomous_explore.py` (stub for Step 45):
```python
def check_online_available(config: dict) -> tuple[bool, str]:
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
```
**Testing Instructions**: Set online.enabled to false; run app and open Autonomous; see warning. Set true and install deps; see "available" (or "no network" if socket check fails).
**Expected Outcome**: Config has online section; UI shows clear warning when online search is not available; local-only mode is offered. Commit: "Step 45: Config and online availability check".

### Step 46
**Objective**: Implement heuristic query generator that, given current graph and seed, suggests next search queries (no LLM required).
**Detailed Explanation**: Add a function `generate_next_queries(kg, seed_label, cycle_index, max_queries=3)` in `autonomous_explore.py`. Heuristic: (1) first cycle: return [seed_label]; (2) later cycles: get top-K nodes by activation (e.g. from to_json, sort nodes by activation descending, take labels of top 5); form queries as "seed_label + top_label" or just top_label. Return a list of up to max_queries strings. This gives the autonomous loop something to "search for" without any LLM. Optional: if config has llm enabled, call llm_stub.generate("Suggest 3 search queries to expand knowledge about " + seed_label) and parse lines as queries (fallback to heuristic if stub returns empty).
**Files to Create or Modify**:
- Modify: `python/goat_ts_cig/autonomous_explore.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Code Examples**:
```python
def generate_next_queries(kg, seed_label: str, cycle_index: int, max_queries: int = 3, config: dict | None = None) -> list[str]:
    if cycle_index == 0:
        return [seed_label]
    data = kg.to_json()
    nodes = sorted(data.get("nodes", []), key=lambda n: n.get("activation", 0), reverse=True)
    queries = []
    for n in nodes[:5]:
        label = (n.get("label") or "").strip()
        if label and label != seed_label and label not in queries:
            queries.append(label)
            if len(queries) >= max_queries:
                break
    if not queries:
        queries = [seed_label]
    return queries[:max_queries]
```
**Testing Instructions**: Create KG with a few nodes and activations; call generate_next_queries(kg, "AI", 1, 3); assert return list length <= 3 and contains non-seed labels with high activation.
**Expected Outcome**: Heuristic query list for each cycle. Commit: "Step 46: Heuristic query generator".

### Step 47
**Objective**: Implement full autonomous exploration loop in `autonomous_explore.py`.
**Detailed Explanation**: Implement `run_autonomous_explore(seed_query, config_path=None, config=None, max_cycles=5, max_queries_per_cycle=3, online_override=None)` that: (1) loads config if not provided; (2) opens KG from config graph.path; (3) determines whether to use web search (config online.enabled and search_fetcher.SEARCH_AVAILABLE and online_override != False); (4) for cycle in 0..max_cycles-1: (a) generate_next_queries(kg, seed_query, cycle, max_queries_per_cycle); (b) for each query, if online: call search_fetcher.search_web(query, max_results=5); for each result ingest_text(snippet or body); (c) ensure seed node exists and set activation 1.0; (d) call run_pipeline(seed_query, ...) to run TS and CIG; (e) record cycle info (queries, num_ingested); (5) return dict like run_pipeline (seed, node_id, cig, graph, config, rust_used) plus key "cycles": [{ "queries": [...], "ingested_count": N }, ...]. If online is false, skip search_web and ingest in (4)(b) but still do (4)(c)–(4)(e) so the graph evolves from heuristic-only expansion (e.g. add nodes from query strings as single-node ingest if desired, or just re-run TS). Cap total HTTP requests using config online.max_requests_per_run.
**Files to Create or Modify**:
- Modify: `python/goat_ts_cig/autonomous_explore.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Code Examples**: (Pseudocode structure; agent to implement fully.)
```python
def run_autonomous_explore(seed_query: str, config_path: str | None = None, config: dict | None = None,
                           max_cycles: int = 5, max_queries_per_cycle: int = 3, online_override: bool | None = None):
    config = config or load_config(config_path)
    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    kg = KnowledgeGraph(db_path)
    use_online = (config.get("online") or {}).get("enabled", False) and SEARCH_AVAILABLE
    if online_override is not None:
        use_online = online_override
    max_requests = (config.get("online") or {}).get("max_requests_per_run", 30)
    cycles_log = []
    for cycle in range(max_cycles):
        queries = generate_next_queries(kg, seed_query, cycle, max_queries_per_cycle, config)
        ingested = 0
        if use_online:
            for q in queries:
                if total_requests >= max_requests: break
                results = search_web(q, max_results=5, timeout_seconds=...)
                for r in results:
                    kg.ingest_text(r.get("snippet") or r.get("title") or "")
                    ingested += 1
                total_requests += 1
        cycles_log.append({"queries": queries, "ingested_count": ingested})
        run_pipeline(seed_query, config_path=..., config=config, ...)  # re-use existing; ensure same KG
    # After loop, run_pipeline once more and return its result plus cycles_log
    result = run_pipeline(seed_query, config_path=config_path, config=config)
    result["cycles"] = cycles_log
    return result
```
(Agent must integrate with existing run_pipeline so the same KG instance is used; run_pipeline currently creates its own KG, so either pass kg into run_pipeline or refactor run_pipeline to accept an optional kg argument. Prefer adding an optional `kg=None` to run_pipeline so autonomous can pass the same kg.)
**Testing Instructions**: Call run_autonomous_explore("AI", max_cycles=2, online_override=False); assert result has "cycles" with 2 entries and "cig" and "graph"; no HTTP calls. With online_override=True and deps/network, run with max_cycles=1 and assert at least one cycle has ingested_count >= 0.
**Expected Outcome**: Single entry point for autonomous run; works in local-only and with search when available. Commit: "Step 47: Autonomous exploration loop".

### Step 48
**Objective**: Refactor `run_pipeline` in main.py to accept an optional pre-built KnowledgeGraph instance so the autonomous loop can reuse one KG across cycles.
**Detailed Explanation**: Change the signature of run_pipeline to add an optional parameter `kg=None`. When `kg` is provided, use it and do not create a new KnowledgeGraph; when `kg` is None, create as today. This allows autonomous_explore to create one KG, run multiple ingest + pipeline steps on it, and return the final result.
**Files to Create or Modify**:
- Modify: `python/goat_ts_cig/main.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Code Examples**:
```python
def run_pipeline(seed: str, config_path: str | None = None, ingest_text: str | None = None,
                ticks_override: int | None = None, config_overrides: dict | None = None, kg=None):
    ...
    if kg is None:
        try:
            kg = KnowledgeGraph(db_path)
        except Exception as e:
            return {"error": ...}
    else:
        db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")  # for logging only
    # rest unchanged: ingest_text, existing node, to_rust_graph, full_ts_cycle, from_rust_graph, cig_generator
```
**Testing Instructions**: Run pipeline with kg=None (unchanged behavior); run with kg=KnowledgeGraph(":memory:") and seed "x", assert no error and result has node_id.
**Expected Outcome**: run_pipeline(..., kg=my_kg) uses my_kg. Commit: "Step 48: run_pipeline accepts optional kg".

### Step 49
**Objective**: Connect autonomous loop to run_pipeline with shared KG and cap total requests; add optional link from seed to first ingested node per cycle for better propagation.
**Detailed Explanation**: In autonomous_explore, create one KG, then for each cycle: run search + ingest (if online), then call run_pipeline(seed_query, config=config, kg=kg) so TS runs on the same KG. Do not pass ingest_text into run_pipeline from autonomous (ingest is already done in the loop). Optionally after ingesting snippets in a cycle, add one edge from the seed node id to the first newly created node in that batch so that TS propagation pulls activation into the new content. Cap total_requests across all cycles and all queries against config online.max_requests_per_run.
**Files to Create or Modify**:
- Modify: `python/goat_ts_cig/autonomous_explore.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Testing Instructions**: run_autonomous_explore with max_cycles=3, online_override=False; verify 3 cycles in result and graph has more nodes after heuristic-only. With online true and network, verify requests capped.
**Expected Outcome**: Autonomous loop uses single KG and run_pipeline(..., kg=kg); request cap enforced. Commit: "Step 49: Autonomous loop integration with run_pipeline".

### Step 50
**Objective**: Add sidebar step "5. Autonomous Exploration" and a dedicated page that explains the feature and allows running it with parameters.
**Detailed Explanation**: In app_ui.py, add a fifth option to the sidebar radio: "5. Autonomous Exploration". On that page: (1) Title and short description (autonomous mode runs N cycles, each generating queries, optionally searching the web, ingesting into the graph, and running TS); (2) Seed query text input (default "AI"); (3) Number of cycles (slider 1–10, default 5); (4) Max queries per cycle (1–5, default 3); (5) Checkbox "Use online search (if available)" (default True; if check_online_available is False, show warning and option "Run in local-only mode"); (6) Button "Run autonomous exploration"; (7) On run, call run_autonomous_explore(seed_query, config_path=CONFIG_PATH, max_cycles=..., max_queries_per_cycle=..., online_override=use_online); store result in st.session_state["last_autonomous_result"]; (8) Display success message and same tabs as Run & Explore (Idea map, Context, Hypotheses, Graph summary, Raw JSON) plus an expander "Cycles summary" showing cycles_log (queries and ingested_count per cycle).
**Files to Create or Modify**:
- Modify: `app_ui.py`
**Exact Folder Locations**: Repository root.
**Code Examples**: Add to sidebar: `step = st.sidebar.radio(..., ["1. Setup", "2. Configuration", "3. Run & Explore", "4. Optional Tools", "5. Autonomous Exploration"], ...)`. Add block `elif step == "5. Autonomous Exploration":` with the form and run button and result display reusing the same tab layout as in "3. Run & Explore" and adding the cycles summary.
**Testing Instructions**: Open UI, go to step 5, set seed "AI", cycles 2, click Run (with online off); see result and cycles summary with 2 entries.
**Expected Outcome**: New step in UI; user can run autonomous exploration and see CIG outputs plus per-cycle log. Commit: "Step 50: UI step Autonomous Exploration".

### Step 51
**Objective**: In "Run & Explore" add a checkbox "Autonomous Exploration Mode" that, when checked, runs run_autonomous_explore instead of run_pipeline when the user clicks "Run pipeline".
**Detailed Explanation**: In the "3. Run & Explore" section, add a checkbox st.checkbox("Autonomous Exploration Mode", value=False). When the user clicks "Run pipeline": if the checkbox is True, call run_autonomous_explore(seed, config_path=CONFIG_PATH, max_cycles=5, max_queries_per_cycle=3, ...) and store result in st.session_state["last_run_result"] (same key as normal run so the same tab display works); if checkbox is False, keep current behavior (run_pipeline). When Autonomous is checked, show a short note: "Runs 5 cycles: generate queries → optional web search → ingest → TS propagation."
**Files to Create or Modify**:
- Modify: `app_ui.py`
**Exact Folder Locations**: Repository root.
**Code Examples**:
```python
autonomous_mode = st.checkbox("Autonomous Exploration Mode", value=False,
    help="Run multiple cycles of query generation, optional web search, ingest, and TS.")
if autonomous_mode:
    st.caption("Runs 5 cycles: generate queries → optional web search → ingest → TS propagation.")
...
if st.button("Run pipeline", type="primary"):
    ...
    if autonomous_mode:
        from goat_ts_cig.autonomous_explore import run_autonomous_explore
        result = run_autonomous_explore(seed, config_path=CONFIG_PATH, max_cycles=5, ...)
    else:
        result = run_pipeline(...)
    st.session_state["last_run_result"] = result
```
**Testing Instructions**: In Run & Explore, check Autonomous, enter seed, click Run; verify result includes "cycles" and same tabs render.
**Expected Outcome**: Single "Run pipeline" button drives either normal or autonomous run based on checkbox. Commit: "Step 51: Run & Explore autonomous checkbox".

### Step 52
**Objective**: Show a clear warning when online search is disabled or unavailable and offer "Run in local-only mode" in both step 5 and when Autonomous is checked in step 3.
**Detailed Explanation**: Wherever autonomous is offered (step 5 and step 3 with checkbox), call check_online_available(config). If False, display st.warning(message) and a checkbox "Run in local-only mode (no web search)" default True so the user can still run autonomous with online_override=False. When "Run in local-only mode" is checked, pass online_override=False to run_autonomous_explore.
**Files to Create or Modify**:
- Modify: `app_ui.py`
**Exact Folder Locations**: Repository root.
**Testing Instructions**: Set config online.enabled to false; open step 5; see warning and local-only option; run and verify no HTTP requests.
**Expected Outcome**: Users are never surprised; they see why web search is off and can still run local-only. Commit: "Step 52: Online unavailable warning and local-only option".

### Step 53
**Objective**: Add optional .env loading in app_ui and autonomous_explore so CIG_ONLINE_ENABLED and CIG_SEARCH_API_KEY override or supplement config.
**Detailed Explanation**: At startup of app_ui (or when loading config), if a `.env` file exists, load it (e.g. with python-dotenv if already a dependency, or manually parse KEY=VALUE lines). If CIG_ONLINE_ENABLED is set to 1 or true, set config["online"]["enabled"] = True (merge into loaded config). If CIG_SEARCH_API_KEY is set, store in config for future use (e.g. config["online"]["search_api_key"]). Prefer not adding python-dotenv if not already present; instead document in README that users can set env vars and implement a minimal .env reader that only reads CIG_ONLINE_ENABLED and CIG_SEARCH_API_KEY (no extra deps). If python-dotenv is already in requirements, use load_dotenv().
**Files to Create or Modify**:
- Modify: `app_ui.py` (load .env when loading config).
- Modify: `python/goat_ts_cig/autonomous_explore.py` or a small config helper (apply env overrides to config).
**Exact Folder Locations**: Root and python/goat_ts_cig/.
**Code Examples**: Minimal .env read without dotenv: `if os.path.isfile(".env"): [apply line.strip() for line in open(".env") if "=" in line and not line.startswith("#")]` and set os.environ or a small dict. Then in load_config(), after yaml.safe_load, if os.environ.get("CIG_ONLINE_ENABLED", "").lower() in ("1", "true"): config.setdefault("online", {})["enabled"] = True.
**Testing Instructions**: Create .env with CIG_ONLINE_ENABLED=1; load config in UI; verify config["online"]["enabled"] is True.
**Expected Outcome**: Env vars can enable online or pass API key without editing config file. Commit: "Step 53: Env overrides for online and API key".

### Step 54
**Objective**: Add unit tests for search_fetcher (mocked or skip when no deps) and for generate_next_queries and run_autonomous_explore (local-only, no network).
**Detailed Explanation**: tests/test_search_fetcher.py: test that search_web returns list; when SEARCH_AVAILABLE is False, search_web("x") returns []. Mock or skip actual HTTP. tests/test_autonomous.py: test generate_next_queries returns non-empty list for cycle 0 (seed) and for cycle 1 with a graph that has nodes; test run_autonomous_explore("AI", max_cycles=2, online_override=False) returns dict with "cycles" of length 2, "seed"=="AI", and "cig" present. No real network calls.
**Files to Create or Modify**:
- Create: `tests/test_search_fetcher.py`
- Create: `tests/test_autonomous.py`
**Exact Folder Locations**: `tests/`.
**Code Examples**:
```python
# test_search_fetcher.py
def test_search_web_returns_list():
    from goat_ts_cig.search_fetcher import search_web
    r = search_web("test query", max_results=2)
    assert isinstance(r, list)
    for item in r:
        assert "title" in item or "url" in item or "snippet" in item
```
```python
# test_autonomous.py
def test_autonomous_local_only():
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    r = run_autonomous_explore("AI", config={"graph": {"path": ":memory:"}, "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5}}, max_cycles=2, online_override=False)
    assert "error" not in r or r.get("error") is None
    assert "cycles" in r and len(r["cycles"]) == 2
    assert r.get("seed") == "AI"
```
(Note: run_autonomous_explore may need to accept config with graph.path ":memory:" and create KG from it; agent should implement so tests can use in-memory DB.)
**Testing Instructions**: pytest tests/test_search_fetcher.py tests/test_autonomous.py -v
**Expected Outcome**: All new tests pass. Commit: "Step 54: Tests for search and autonomous".

### Step 55
**Objective**: Document the autonomous exploration feature and online options in README.md and add a short "Autonomous Exploration" section in the UI (step 5) as markdown.
**Detailed Explanation**: In README.md add a subsection "Autonomous Exploration (optional)" that describes: (1) what it does (multi-cycle query → search → ingest → TS); (2) that it is optional and off by default; (3) config.yaml online section and .env variables; (4) that no API key is required for DuckDuckGo; (5) local-only mode when network or config disables online. In app_ui step 5, add st.markdown with a brief bullet list of steps the autonomous loop performs.
**Files to Create or Modify**:
- Modify: `README.md`
- Modify: `app_ui.py` (step 5 intro text)
**Exact Folder Locations**: Root.
**Testing Instructions**: Read README and step 5 UI; confirm instructions are clear.
**Expected Outcome**: Users can enable and use autonomous mode from docs and UI. Commit: "Step 55: Docs for autonomous exploration".

### Step 56
**Objective**: Enforce request cap and timeouts in search_fetcher and autonomous_explore to avoid long runs on low-end hardware.
**Detailed Explanation**: In search_fetcher.search_web, always pass timeout_seconds to requests (or duckduckgo-search if it supports it). In autonomous_explore, maintain a running count of HTTP requests (each search_web call counts as 1; each optional body fetch counts as 1); when count >= config online.max_requests_per_run, skip further search_web calls for that run. Log or store in cycles_log when cap was hit.
**Files to Create or Modify**:
- Modify: `python/goat_ts_cig/search_fetcher.py`
- Modify: `python/goat_ts_cig/autonomous_explore.py`
**Exact Folder Locations**: `python/goat_ts_cig/`.
**Testing Instructions**: Set max_requests_per_run=2; run autonomous with online; verify at most 2 requests (or 2 search_web calls) and run completes.
**Expected Outcome**: No runaway requests; low-end safe. Commit: "Step 56: Request cap and timeouts".

### Step 57
**Objective**: Add integration test that runs the full UI flow for autonomous (local-only) via subprocess or by calling run_autonomous_explore directly and asserting on result structure.
**Detailed Explanation**: In tests/test_full.py or a new tests/test_ui_autonomous.py, add a test that calls run_autonomous_explore with config pointing to :memory: or a temp DB, max_cycles=2, online_override=False, and asserts result has keys seed, node_id, cig, graph, cycles, and that len(result["cycles"]) == 2. This is an integration test for the autonomous feature.
**Files to Create or Modify**:
- Modify: `tests/test_full.py` or create `tests/test_ui_autonomous.py`
**Exact Folder Locations**: `tests/`.
**Testing Instructions**: pytest tests/test_full.py -k autonomous or pytest tests/test_ui_autonomous.py
**Expected Outcome**: Integration test passes. Commit: "Step 57: Integration test for autonomous".

### Step 58
**Objective**: Finalize addendum: update PLAN.md (this document) to reference the addendum in the main "Development Phases" and add a short "Optional UI and Autonomous Exploration" subsection to the scaling or roadmap section if present; ensure no steps are missing.
**Detailed Explanation**: In the main PLAN.md section "3. Development Phases", add Phase 9–12 (Steps 43–58) as a bullet list. In README or SCALING.md, add one line: "Optional Streamlit UI and Autonomous Exploration (online search) are documented in PLAN.md addendum (Steps 43–58)." No new code; documentation only.
**Files to Create or Modify**:
- Modify: `plan.md` (in the original Phase list near the top, add phases 9–12 and step ranges 43–58).
- Modify: `README.md` or `SCALING.md` (one-line reference to addendum).
**Exact Folder Locations**: Repository root.
**Code Examples**: In plan.md, under "## 3. Development Phases", add:
- **Phase 9: Search and Config** (Steps 43–45)
- **Phase 10: Autonomous Loop** (Steps 46–49)
- **Phase 11: UI Integration** (Steps 50–53)
- **Phase 12: Testing and Docs** (Steps 54–58)
**Testing Instructions**: N/A.
**Expected Outcome**: Plan and docs are consistent; agent can execute Steps 43–58 in order. Commit: "Step 58: Plan and doc reference for addendum".

---

## Addendum §5. UI Design with Streamlit (Summary)

- **Existing**: Steps 1–4 (Setup, Configuration, Run & Explore, Optional Tools). Reuse layout: sidebar radio, expanders, buttons, session state for results.
- **New step 5**: "Autonomous Exploration" — dedicated page with seed input, cycle/query sliders, "Use online search" checkbox, warning when offline, "Run in local-only mode", and "Run autonomous exploration" button. Results: same tabs as Run & Explore plus "Cycles summary" expander.
- **Run & Explore**: Add checkbox "Autonomous Exploration Mode"; when checked, "Run pipeline" calls run_autonomous_explore instead of run_pipeline; show short caption and respect online-available warning + local-only option.
- **No new entrypoint**: Single file app_ui.py. No separate ui.py unless the agent prefers to split (plan allows either).

---

## Addendum §6. Autonomous Exploration Algorithm (Summary)

1. Load config; open KG (or create from config graph.path).
2. Determine use_online = config.online.enabled and SEARCH_AVAILABLE and (optional) network check; respect online_override.
3. total_requests = 0.
4. For cycle in 0..max_cycles-1:
   - queries = generate_next_queries(kg, seed_query, cycle, max_queries_per_cycle).
   - For each query: if use_online and total_requests < max_requests_per_run: results = search_web(query, max_results=5); for each result: kg.ingest_text(snippet or title); total_requests += 1 (and optionally +1 per body fetch if implemented).
   - Ensure seed node exists; set activation 1.0.
   - run_pipeline(seed_query, config=config, kg=kg).
   - Append to cycles_log: { queries, ingested_count }.
5. Return last run_pipeline result plus cycles_log.

---

## Addendum §7. Online Search Implementation (Summary)

- **Primary**: duckduckgo-search (no API key) or requests + BeautifulSoup on DuckDuckGo HTML. Function search_web(query, max_results=5, timeout_seconds=10) → list of { title, snippet, url [, body ] }.
- **Optional body fetch**: For up to 2–3 results per query, GET url with timeout 5s, parse with BeautifulSoup, take text and truncate to 2000 chars; add as "body". Skip if timeout or error.
- **Fallback**: If neither duckduckgo-search nor requests available, SEARCH_AVAILABLE=False and search_web returns [].

---

## Addendum §8. Ingestion from Search Results (Summary)

- Use existing kg.ingest_text(text). For each search result, pass result["snippet"] or result.get("body") or result["title"] so that at least one string is ingested. No new KG schema; sequential word linking as in current ingest_text. Optionally add one edge from seed node to first new node per cycle to improve propagation (Step 49).

---

## Addendum §9. Config and Env Handling (Summary)

- **config.yaml**: online.enabled (bool), online.max_requests_per_run (int), online.timeout_seconds (int). Optional: online.search_api_key for future use.
- **.env**: CIG_ONLINE_ENABLED (0/1), CIG_SEARCH_API_KEY (string). Load .env in app and merge into config (Step 53). .env.example documents variables.

---

## Addendum §10. Testing Strategy for New Feature (Summary)

- **Unit**: search_fetcher returns list; generate_next_queries returns list of strings; check_online_available returns (bool, str).
- **Integration**: run_autonomous_explore(..., online_override=False, max_cycles=2) returns full result with cycles; run_pipeline(..., kg=kg) uses provided kg.
- **No live network in CI**: Mock or skip tests that would perform HTTP; mark with pytest.mark.skipif or use pytest with --ignore for optional online tests if needed.

---

## Addendum §11. Performance Considerations (Summary)

- Cap total HTTP requests per run (e.g. 30); cap per-request timeout (e.g. 10 s). Limit body fetches to 2–3 per query. Run autonomous in-process; no GPU. Batch ingest: existing ingest_text is already per-snippet; no need to batch across results.

---

## Addendum §12. Optional Fallback Modes (Summary)

- **Online disabled in config or env**: Show warning in UI; offer "Run in local-only mode". Autonomous loop runs without search_web; only heuristic queries and TS.
- **Search dependencies not installed**: SEARCH_AVAILABLE=False; search_web returns []; same local-only offer.
- **Network error during run**: Catch exception in search_web; append empty list for that query; continue cycle; do not abort entire run.

---

End of addendum. Execute Steps 43 through 58 sequentially.
```