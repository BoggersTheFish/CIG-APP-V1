"""
CIG-APP UI: step-by-step setup, configuration, and run.
Run from project root: streamlit run app_ui.py
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys

import streamlit as st

# Ensure project root and python package are on path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "python"))

st.set_page_config(
    page_title="CIG-APP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CONFIG_PATH = os.path.join(ROOT, "config.yaml")


def _load_env_overrides():
    """Apply .env overrides (CIG_ONLINE_ENABLED, CIG_SEARCH_API_KEY) to environment."""
    env_path = os.path.join(ROOT, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k:
                    os.environ[k] = v
    except Exception:
        pass


def load_config():
    _load_env_overrides()
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        config = {}
    # Env overrides
    if os.environ.get("CIG_ONLINE_ENABLED", "").lower() in ("1", "true"):
        config.setdefault("online", {})["enabled"] = True
    key = os.environ.get("CIG_SEARCH_API_KEY", "").strip()
    if key:
        config.setdefault("online", {})["search_api_key"] = key
    return config


def save_config(config: dict) -> str | None:
    try:
        import yaml
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return None
    except Exception as e:
        return str(e)


def check_python():
    v = sys.version_info
    return v.major >= 3 and v.minor >= 12, f"{v.major}.{v.minor}.{v.micro}"


def check_pip_packages():
    try:
        import yaml
        import pytest
        import maturin
        return True, "PyYAML, pytest, maturin OK"
    except ImportError as e:
        return False, str(e)


def check_rust():
    try:
        out = subprocess.run(
            ["cargo", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=ROOT,
        )
        if out.returncode == 0:
            return True, (out.stdout or out.stderr or "").strip()
        return False, out.stderr or "cargo not found"
    except FileNotFoundError:
        return False, "cargo not in PATH (install rustup)"
    except Exception as e:
        return False, str(e)


def check_rust_extension():
    try:
        from bindings.rust_bindings import goat_ts_core
        ok = hasattr(goat_ts_core, "PyGraph")
        return ok, "Rust extension (goat_ts_core) built" if ok else "Rust extension not built"
    except Exception as e:
        return False, str(e)


# ----- Sidebar: step selection -----
st.sidebar.title("CIG-APP")
st.sidebar.caption("Contextual Information Generator")
st.sidebar.caption("Run from project root: `python -m streamlit run app_ui.py`")
step = st.sidebar.radio(
    "Step",
    [
        "1. Setup",
        "2. Configuration",
        "3. Run & Explore",
        "4. Optional Tools",
        "5. Autonomous Exploration",
    ],
    index=0,
)

# ----- 1. Setup -----
if step == "1. Setup":
    st.header("1. Setup")
    st.markdown("Walk through environment checks and install steps.")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Environment checks")
        py_ok, py_ver = check_python()
        st.markdown(f"- **Python 3.12+**: {'✅' if py_ok else '❌'} {py_ver}")
        pip_ok, pip_msg = check_pip_packages()
        st.markdown(f"- **Pip packages** (PyYAML, pytest, maturin): {'✅' if pip_ok else '❌'} {pip_msg}")
        rust_ok, rust_msg = check_rust()
        st.markdown(f"- **Rust** (cargo): {'✅' if rust_ok else '❌'} {rust_msg}")
        ext_ok, ext_msg = check_rust_extension()
        st.markdown(f"- **Rust extension** (goat_ts_core): {'✅' if ext_ok else '❌'} {ext_msg}")
    with c2:
        st.subheader("Install commands")
        st.code("pip install -r requirements.txt", language="bash")
        st.caption("Install Python dependencies (run in project root).")
        st.code("rustup install stable\nmaturin develop --manifest-path=rust/Cargo.toml", language="bash")
        st.caption("Build Rust extension (requires virtualenv active for maturin develop).")
        if st.button("Run pip install -r requirements.txt"):
            with st.spinner("Installing..."):
                r = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            if r.returncode == 0:
                st.success("Install finished.")
            else:
                st.error(r.stderr or r.stdout)
        st.divider()
        st.markdown("**Setup scripts** (optional):")
        st.markdown("- Windows: `.\setup_windows.ps1`")
        st.markdown("- Linux/Mac: `./setup_lowend.sh`")
    if not py_ok:
        st.warning("Python 3.12+ is required. Install from python.org or your package manager.")
    if not pip_ok:
        st.warning("Run `pip install -r requirements.txt` from the project root.")
    if not ext_ok and rust_ok:
        st.info("Rust extension is optional. Pipeline runs without it; propagation and similarity will be skipped.")

# ----- 2. Configuration -----
elif step == "2. Configuration":
    st.header("2. Configuration")
    st.markdown("Edit `config.yaml` and optional parameters. Changes are saved when you click **Save configuration**.")
    config = load_config()
    graph = config.get("graph") or {}
    wave = config.get("wave") or {}

    with st.expander("Graph", expanded=True):
        graph_path = st.text_input(
            "Database path",
            value=graph.get("path", "data/knowledge_graph.db"),
            help="SQLite file path for the knowledge graph (nodes/edges).",
        )
        graph["path"] = graph_path

    with st.expander("Wave (TS propagation)", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            wave_ticks = st.number_input(
                "Ticks",
                min_value=1,
                max_value=500,
                value=int(wave.get("ticks", 10)),
                help="Number of propagation steps per run.",
            )
        with col2:
            wave_decay = st.number_input(
                "Decay",
                min_value=0.0,
                max_value=1.0,
                value=float(wave.get("decay", 0.9)),
                step=0.05,
                format="%.2f",
                help="Activation decay per tick (0–1).",
            )
        with col3:
            wave_threshold = st.number_input(
                "Activation threshold",
                min_value=0.0,
                max_value=1.0,
                value=float(wave.get("activation_threshold", 0.5)),
                step=0.05,
                format="%.2f",
                help="Threshold above which a node is considered ACTIVE.",
            )
        wave["ticks"] = wave_ticks
        wave["decay"] = wave_decay
        wave["activation_threshold"] = wave_threshold

    with st.expander("Hypothesis (optional)"):
        sim_thresh = st.number_input(
            "Similarity threshold",
            min_value=0.0,
            max_value=1.0,
            value=float(config.get("similarity_threshold", 0.3)),
            step=0.05,
            format="%.2f",
            help="Minimum Jaccard similarity to suggest a link between nodes.",
        )
        tension_thresh = st.number_input(
            "Tension threshold",
            min_value=0.0,
            max_value=1.0,
            value=float(config.get("tension_threshold", 0.3)),
            step=0.05,
            format="%.2f",
            help="Activation difference on conflict edges to suggest resolution.",
        )
        config["similarity_threshold"] = sim_thresh
        config["tension_threshold"] = tension_thresh

    with st.expander("LLM (optional)"):
        use_llm = st.checkbox(
            "Use LLM stub for hypothesis phrasing",
            value=bool(config.get("llm", False)),
            help="If enabled, hypothesis_engine will call the local LLM stub to phrase suggestions.",
        )
        config["llm"] = use_llm

    with st.expander("Online (autonomous exploration)"):
        online_enabled = st.checkbox(
            "Enable online search",
            value=bool((config.get("online") or {}).get("enabled", False)),
            help="Allow web search in Autonomous Exploration (DuckDuckGo, no API key).",
        )
        max_req = st.number_input(
            "Max requests per run",
            min_value=5,
            max_value=100,
            value=int((config.get("online") or {}).get("max_requests_per_run", 30)),
        )
        config["online"] = {
            "enabled": online_enabled,
            "max_requests_per_run": max_req,
            "timeout_seconds": int((config.get("online") or {}).get("timeout_seconds", 10)),
        }

    config["graph"] = graph
    config["wave"] = wave

    if st.button("Save configuration"):
        err = save_config(config)
        if err:
            st.error(f"Save failed: {err}")
        else:
            st.success("Configuration saved to config.yaml")

    st.divider()
    st.subheader("Current config.yaml")
    try:
        import yaml
        buf = io.StringIO()
        yaml.dump(config, buf, default_flow_style=False, sort_keys=False)
        st.code(buf.getvalue(), language="yaml")
    except Exception:
        st.code(json.dumps(config, indent=2), language="json")

# ----- 3. Run & Explore -----
elif step == "3. Run & Explore":
    st.header("3. Run & Explore")
    st.markdown("Set a seed concept, optionally ingest text, then run the CIG pipeline.")
    config = load_config()

    seed = st.text_input(
        "Seed concept",
        value="AI",
        help="Starting node label for exploration (added to graph if missing).",
    ).strip()

    autonomous_mode = st.checkbox(
        "Autonomous Exploration Mode",
        value=False,
        help="Run multiple cycles: generate queries → optional web search → ingest → TS propagation.",
    )
    if autonomous_mode:
        st.caption("Runs 5 cycles: generate queries → optional web search → ingest → TS propagation.")
        from goat_ts_cig.autonomous_explore import check_online_available
        online_ok, online_msg = check_online_available(config)
        run_local_only = False
        if not online_ok:
            st.warning(online_msg)
            run_local_only = st.checkbox("Run in local-only mode (no web search)", value=True)

    ingest_option = st.radio(
        "Ingest text (optional)",
        ["None", "Paste text", "Upload file"],
        horizontal=True,
    )
    ingest_text = None
    if ingest_option == "Paste text":
        ingest_text = st.text_area("Paste text to ingest (words become nodes, sequential links)", height=120)
    elif ingest_option == "Upload file":
        up = st.file_uploader("Upload a text file", type=["txt", "md"])
        if up:
            ingest_text = up.read().decode("utf-8", errors="replace")

    ticks_override = None
    if st.checkbox("Override wave ticks for this run"):
        ticks_override = st.number_input("Ticks", min_value=1, max_value=500, value=10)

    if st.button("Run pipeline", type="primary"):
        if not seed:
            st.error("Enter a seed concept.")
        else:
            with st.spinner("Running pipeline..." if not autonomous_mode else "Running autonomous exploration..."):
                try:
                    if autonomous_mode:
                        from goat_ts_cig.autonomous_explore import run_autonomous_explore
                        online_override = False if (not online_ok or run_local_only) else None
                        result = run_autonomous_explore(
                            seed,
                            config_path=CONFIG_PATH,
                            config=config,
                            max_cycles=5,
                            max_queries_per_cycle=3,
                            online_override=online_override,
                        )
                    else:
                        from goat_ts_cig.main import run_pipeline
                        result = run_pipeline(
                            seed=seed,
                            config_path=CONFIG_PATH,
                            ingest_text=ingest_text or None,
                            ticks_override=ticks_override,
                        )
                except Exception as e:
                    st.exception(e)
                    result = {"error": str(e)}
            st.session_state["last_run_result"] = result

    result = st.session_state.get("last_run_result")
    if result:
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(f"Done. Seed **{result['seed']}** (node_id={result['node_id']}). Rust used: **{result.get('rust_used', False)}**.")
            if result.get("cycles"):
                with st.expander("Cycles summary"):
                    for i, cy in enumerate(result["cycles"]):
                        st.markdown(f"**Cycle {i+1}:** queries = {cy.get('queries', [])}, ingested = {cy.get('ingested_count', 0)}")
            cig = result.get("cig") or {}
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Idea map", "Context expansion", "Hypotheses", "Graph summary", "Raw JSON"])
            with tab1:
                st.json(cig.get("idea_map") or {})
            with tab2:
                st.json(cig.get("context_expansion") or [])
            with tab3:
                st.json(cig.get("hypotheses") or [])
            with tab4:
                g = result.get("graph") or {}
                st.metric("Nodes", len(g.get("nodes", [])))
                st.metric("Edges", len(g.get("edges", [])))
                if g.get("nodes"):
                    st.dataframe(g["nodes"], use_container_width=True, hide_index=True)
            with tab5:
                st.json(result)

# ----- 4. Optional Tools -----
elif step == "4. Optional Tools":
    st.header("4. Optional Tools")
    config = load_config()
    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    abs_db = os.path.normpath(os.path.join(ROOT, db_path) if not os.path.isabs(db_path) else db_path)

    tool = st.radio(
        "Tool",
        ["Run tests", "Run benchmark", "View / edit config file", "Reset database"],
        horizontal=True,
    )

    if tool == "Run tests":
        st.caption("Runs pytest on the tests/ directory.")
        if st.button("Run tests"):
            with st.spinner("Running pytest..."):
                r = subprocess.run(
                    [sys.executable, "run_tests.py"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            if r.returncode == 0:
                st.success("Tests passed.")
            else:
                st.error("Tests failed.")
            st.code(r.stdout or r.stderr or "(no output)", language="text")

    elif tool == "Run benchmark":
        st.caption("Times propagation on 500 and 1000 nodes (requires Rust extension).")
        if st.button("Run benchmark"):
            with st.spinner("Benchmarking..."):
                r = subprocess.run(
                    [sys.executable, "benchmark.py"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            st.code(r.stdout or r.stderr or "(no output)", language="text")

    elif tool == "View / edit config file":
        if os.path.isfile(CONFIG_PATH):
            raw = st.text_area("config.yaml", value=open(CONFIG_PATH, encoding="utf-8").read(), height=300)
            if st.button("Overwrite config.yaml"):
                try:
                    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                        f.write(raw)
                    st.success("Saved.")
                except Exception as e:
                    st.error(str(e))
        else:
            st.warning("config.yaml not found at project root.")

    elif tool == "Reset database":
        st.caption(f"Delete the SQLite database at `{db_path}` so the next run starts with an empty graph.")
        if os.path.isfile(abs_db):
            st.warning(f"File exists: {abs_db}")
            if st.button("Delete database", type="secondary"):
                try:
                    os.remove(abs_db)
                    st.success("Database deleted.")
                except Exception as e:
                    st.error(str(e))
        else:
            st.info(f"No database file at {abs_db} yet.")

# ----- 5. Autonomous Exploration -----
elif step == "5. Autonomous Exploration":
    st.header("5. Autonomous Exploration")
    st.markdown("""
    **Autonomous mode** runs multiple cycles to expand the knowledge graph:
    - Generate search queries from the current graph (heuristic or seed).
    - Optionally run web search (DuckDuckGo, no API key).
    - Ingest results into the graph and run TS propagation.
    """)
    config = load_config()
    from goat_ts_cig.autonomous_explore import check_online_available
    online_ok, online_msg = check_online_available(config)
    if not online_ok:
        st.warning(online_msg)
        run_local_only_5 = st.checkbox("Run in local-only mode (no web search)", value=True, key="local_only_5")
    else:
        run_local_only_5 = False

    seed_auto = st.text_input("Seed query", value="AI", key="seed_auto").strip()
    max_cycles = st.slider("Number of cycles", 1, 10, 5, key="max_cycles")
    max_q = st.slider("Max queries per cycle", 1, 5, 3, key="max_q")
    use_online_5 = st.checkbox("Use online search (if available)", value=bool(online_ok), key="use_online_5")

    if st.button("Run autonomous exploration", type="primary", key="run_auto"):
        if not seed_auto:
            st.error("Enter a seed query.")
        else:
            with st.spinner("Running autonomous exploration..."):
                try:
                    from goat_ts_cig.autonomous_explore import run_autonomous_explore
                    online_override = None
                    if not online_ok or run_local_only_5:
                        online_override = False
                    elif not use_online_5:
                        online_override = False
                    else:
                        online_override = True
                    result = run_autonomous_explore(
                        seed_auto,
                        config_path=CONFIG_PATH,
                        config=config,
                        max_cycles=max_cycles,
                        max_queries_per_cycle=max_q,
                        online_override=online_override,
                    )
                except Exception as e:
                    st.exception(e)
                    result = {"error": str(e)}
            st.session_state["last_autonomous_result"] = result

    result_auto = st.session_state.get("last_autonomous_result")
    if result_auto:
        if result_auto.get("error"):
            st.error(result_auto["error"])
        else:
            st.success(f"Done. Seed **{result_auto['seed']}** (node_id={result_auto['node_id']}).")
            with st.expander("Cycles summary"):
                for i, cy in enumerate(result_auto.get("cycles", [])):
                    st.markdown(f"**Cycle {i+1}:** queries = {cy.get('queries', [])}, ingested = {cy.get('ingested_count', 0)}")
            cig = result_auto.get("cig") or {}
            t1, t2, t3, t4, t5 = st.tabs(["Idea map", "Context expansion", "Hypotheses", "Graph summary", "Raw JSON"])
            with t1:
                st.json(cig.get("idea_map") or {})
            with t2:
                st.json(cig.get("context_expansion") or [])
            with t3:
                st.json(cig.get("hypotheses") or [])
            with t4:
                g = result_auto.get("graph") or {}
                st.metric("Nodes", len(g.get("nodes", [])))
                st.metric("Edges", len(g.get("edges", [])))
                if g.get("nodes"):
                    st.dataframe(g["nodes"], use_container_width=True, hide_index=True)
            with t5:
                st.json(result_auto)
