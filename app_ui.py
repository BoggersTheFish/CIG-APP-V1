"""
CIG-APP UI: Wizard-focused setup, clean tabs, modern layout.
Run from project root: streamlit run app_ui.py
Rebuild: Setup Wizard (first-run), Main Controls, Advanced Settings, Run & Results.
"""
from __future__ import annotations

import copy
import json
import os
import queue
import subprocess
import sys
import threading
import time

import streamlit as st

# Ensure project root and python package are on path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "python"))

CONFIG_PATH = os.path.join(ROOT, "config.yaml")
SETUP_FLAG_PATH = os.path.join(ROOT, "setup_complete.txt")
ENV_PATH = os.path.join(ROOT, ".env")

st.set_page_config(
    page_title="CIG-APP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----- Session state -----
if "cig_operation_in_progress" not in st.session_state:
    st.session_state.cig_operation_in_progress = False
if "last_run_result" not in st.session_state:
    st.session_state.last_run_result = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
_progress_holder = [0, 1, ""]


def _set_busy(busy: bool) -> None:
    st.session_state.cig_operation_in_progress = busy


def _is_busy() -> bool:
    return st.session_state.get("cig_operation_in_progress", False)


def _load_env_overrides() -> None:
    if not os.path.isfile(ENV_PATH):
        return
    try:
        for line in open(ENV_PATH, encoding="utf-8", errors="replace"):
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


def load_config() -> dict:
    _load_env_overrides()
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8", errors="replace") as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        config = {}
    default_host = os.environ.get("OLLAMA_HOST") or os.environ.get("CIG_OLLAMA_HOST") or "http://127.0.0.1:11434"
    default_model = os.environ.get("OLLAMA_MODEL") or os.environ.get("CIG_OLLAMA_MODEL") or "llama2"
    config.setdefault("llm_ollama", {}).update({
        "enabled": config.get("llm_ollama", {}).get("enabled", False),
        "host": config.get("llm_ollama", {}).get("host", default_host),
        "model": config.get("llm_ollama", {}).get("model", default_model),
    })
    return config


def save_config(config: dict) -> str | None:
    try:
        import yaml
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return None
    except Exception as e:
        return str(e)


def check_all_deps(config: dict) -> list[tuple[str, bool, str | None, str]]:
    """Return (name, ok, pip_pkg_or_none, description) for each dependency."""
    deps: list[tuple[str, bool, str | None, str]] = []

    # Ollama
    ok = False
    try:
        import requests as _r
        host = (config.get("llm_ollama") or {}).get("host", "http://127.0.0.1:11434")
        ok = _r.get(host.rstrip("/") + "/api/tags", timeout=2).status_code == 200
    except Exception:
        pass
    deps.append(("Ollama (Local LLM)", ok, None, "For hypothesis phrasing and autonomous query expansion. Runs locally."))

    # Graphviz binary
    ok = False
    try:
        ok = subprocess.run(["dot", "-V"], capture_output=True, timeout=2).returncode == 0
    except Exception:
        pass
    deps.append(("Graphviz (binary)", ok, None, "Required for graph PNG export. Download from https://graphviz.org and add to PATH."))

    # Graphviz Python
    try:
        import graphviz  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("Graphviz (Python)", ok, "graphviz", "Python wrapper for Graphviz rendering."))

    # Matplotlib
    try:
        import matplotlib  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("Matplotlib", ok, "matplotlib", "Alternative engine for graph visualization."))

    # sentence-transformers
    try:
        import sentence_transformers  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("sentence-transformers", ok, "sentence-transformers", "Optional embeddings for similarity."))

    # sqlite-vss
    try:
        import sqlite_vss  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("sqlite-vss", ok, "sqlite-vss", "Optional vector search."))

    # PyPDF2
    try:
        import PyPDF2  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("PyPDF2", ok, "PyPDF2", "PDF text ingestion."))

    # BeautifulSoup4
    try:
        import bs4  # noqa: F401
        ok = True
    except Exception:
        ok = False
    deps.append(("BeautifulSoup4", ok, "beautifulsoup4", "For web search result parsing."))

    return deps


def run_validate_config() -> tuple[bool, str]:
    """Run validate_config.py; return (success, message)."""
    try:
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "validate_config.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            return True, r.stdout or "Config valid."
        return False, r.stderr or r.stdout or "Validation failed."
    except Exception as e:
        return False, str(e)


# ----- Custom CSS -----
def _inject_css(dark: bool) -> None:
    bg = "#0e1117" if dark else "#ffffff"
    fg = "#fafafa" if dark else "#262730"
    card_bg = "#1e2127" if dark else "#f0f2f6"
    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {bg}; color: {fg}; }}
        .stButton > button {{ border-radius: 6px; font-weight: 500; }}
        .stButton > button:first-child {{ background-color: #4CAF50; color: white; }}
        div[data-testid="stExpander"] {{ background-color: {card_bg}; border-radius: 8px; margin: 0.5rem 0; }}
        .block-container {{ padding-top: 1.5rem; max-width: 1100px; }}
        h1 {{ font-family: Arial, sans-serif; margin-bottom: 0.5rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----- Header -----
_inject_css(st.session_state.dark_mode)
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.title("CIG-APP: Contextual Information Generator")
    st.caption("v1.0 — Local-first knowledge exploration with Thinking Wave propagation")
with c3:
    dark = st.checkbox("Dark mode", value=st.session_state.dark_mode, key="dark_mode_cb")
    st.session_state.dark_mode = dark

# ----- Tabs -----
tab1, tab2, tab3, tab4 = st.tabs(["Setup Wizard", "Main Controls", "Advanced Settings", "Run & Results"])

# ========== Tab 1: Setup Wizard ==========
with tab1:
    st.header("Welcome to CIG-APP: Let's Get You Set Up!")
    setup_done = os.path.isfile(SETUP_FLAG_PATH)

    st.subheader("Step 1: Check & Install Dependencies")
    config = load_config()
    deps = check_all_deps(config)
    installed = sum(1 for (_, ok, _, _) in deps if ok)
    st.progress(installed / len(deps) if deps else 1.0)

    # Grid of dep cards (3 columns)
    cols = st.columns(3)
    for i, (name, ok, pip_pkg, desc) in enumerate(deps):
        with cols[i % 3]:
            with st.container():
                status = "✅" if ok else "❌"
                st.markdown(f"**{status} {name}**")
                st.caption(desc)
                if not ok:
                    if pip_pkg:
                        key = f"install_{name.replace(' ', '_')}"
                        if st.button(f"Install {pip_pkg}", key=key, disabled=_is_busy()):
                            _set_busy(True)
                            with st.spinner(f"Installing {pip_pkg}..."):
                                r = subprocess.run(
                                    [sys.executable, "-m", "pip", "install", pip_pkg],
                                    cwd=ROOT,
                                    capture_output=True,
                                    text=True,
                                    timeout=120,
                                )
                                if r.returncode == 0:
                                    st.success(f"Installed {pip_pkg}. Re-run to refresh.")
                                else:
                                    st.error((r.stderr or r.stdout or "Install failed")[:500])
                            _set_busy(False)
                            st.rerun()
                    else:
                        if "Ollama" in name:
                            st.link_button("Download Ollama", "https://ollama.ai", key=f"ollama_link_{i}")
                        elif "Graphviz" in name and "binary" in name:
                            st.link_button("Download Graphviz", "https://graphviz.org/download/", key=f"gv_link_{i}")

    st.subheader("Step 2: Configure Environment")
    with st.expander("Edit .env (optional)"):
        env_content = ""
        if os.path.isfile(ENV_PATH):
            try:
                env_content = open(ENV_PATH, encoding="utf-8").read()
            except Exception:
                pass
        env_edit = st.text_area(".env contents", value=env_content, height=120, key="env_editor")
        if st.button("Save .env", key="save_env"):
            try:
                with open(ENV_PATH, "w", encoding="utf-8") as f:
                    f.write(env_edit)
                st.success("Saved.")
            except Exception as e:
                st.error(str(e))

    with st.expander("Edit config.yaml"):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                yaml_content = f.read()
        except Exception:
            yaml_content = ""
        yaml_edit = st.text_area("config.yaml", value=yaml_content, height=200, key="yaml_editor")
        if st.button("Save config.yaml", key="save_yaml"):
            try:
                import yaml
                yaml.safe_load(yaml_edit)
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    f.write(yaml_edit)
                st.success("Saved.")
            except Exception as e:
                st.error(f"Invalid YAML or write failed: {e}")

    if st.button("Validate config", key="validate_cfg"):
        ok, msg = run_validate_config()
        if ok:
            st.success("Config valid!")
        else:
            st.error(msg)

    st.subheader("Step 3: Quick Test")
    if st.button("Run sample test (Dry Run)", key="sample_test", disabled=_is_busy()):
        _set_busy(True)
        with st.spinner("Running sample pipeline..."):
            try:
                from goat_ts_cig.main import run_pipeline
                cfg = load_config()
                dry = copy.deepcopy(cfg)
                dry["llm"] = False
                dry.setdefault("llm_ollama", {})["enabled"] = False
                dry.setdefault("online", {})["enabled"] = False
                res = run_pipeline("test", config_path=CONFIG_PATH, config=dry, ticks_override=3)
                if res.get("error"):
                    st.error(res["error"])
                else:
                    st.success(f"Sample run OK. Seed={res.get('seed')}, node_id={res.get('node_id')}")
            except Exception as e:
                st.error(str(e))
        _set_busy(False)

    if st.button("Complete setup", key="complete_setup"):
        try:
            with open(SETUP_FLAG_PATH, "w") as f:
                f.write("setup completed\n")
            st.success("Setup complete! You can use Main Controls and other tabs.")
            st.balloons()
        except Exception as e:
            st.error(str(e))

    if not setup_done:
        st.warning("Complete the steps above and click **Complete setup** to unlock the full flow. See README.md for help.")

# ========== Tab 2: Main Controls ==========
with tab2:
    st.header("Main Controls")
    config = load_config()
    seed = st.text_input(
        "Enter your seed concept (e.g., artificial intelligence)",
        value="artificial intelligence",
        key="seed_main",
    )
    mode = st.radio(
        "Run mode",
        ["Dry Run (Basic)", "Full Run (All Features)"],
        key="mode_main",
        help="Dry: TS propagation and CIG only. Full: includes LLM, embeddings, graph viz, etc.",
    )
    verbose = st.checkbox("Verbose monitoring (progress and stats)", value=True, key="verbose_main")
    st.session_state.verbose_monitoring = verbose

    full_deps = check_all_deps(config)
    full_deps_ok = all(ok for _, ok, _, _ in full_deps)
    run_autonomous = False
    if mode == "Full Run (All Features)":
        if not full_deps_ok:
            st.warning("Some dependencies are missing. Install them in the Setup Wizard tab.")
        run_autonomous = st.checkbox("Run autonomous (5 cycles)", value=False, key="run_auto_cb")

    run_disabled = _is_busy() or (mode == "Full Run (All Features)" and not full_deps_ok)

    if st.button("Run pipeline", type="primary", disabled=run_disabled, key="btn_run_main"):
        if not seed.strip():
            st.error("Enter a seed concept.")
        else:
            seed_val = seed.strip()
            config = load_config()
            if run_autonomous:
                _set_busy(True)
                with st.status("Running autonomous exploration...", expanded=True):
                    try:
                        from goat_ts_cig.autonomous_explore import run_autonomous_explore
                        adv = config.get("advanced_autonomous") or {}
                        seeds_list = [seed_val] + [s for s in (adv.get("multi_seed") or []) if isinstance(s, str) and s.strip()]
                        result = run_autonomous_explore(
                            seed_val,
                            config_path=CONFIG_PATH,
                            config=config,
                            max_cycles=5,
                            max_queries_per_cycle=3,
                            online_override=None,
                            seeds=seeds_list if len(seeds_list) > 1 else None,
                        )
                        st.session_state.last_run_result = result
                    except Exception as e:
                        st.session_state.last_run_result = {"error": str(e)}
                    finally:
                        _set_busy(False)
                st.rerun()
            else:
                _progress_holder[0], _progress_holder[1], _progress_holder[2] = 0, 1, "starting"

                def _progress_cb(c, t, m):
                    _progress_holder[0], _progress_holder[1], _progress_holder[2] = c, t, m

                def _run_bg():
                    res, err = None, None
                    try:
                        from goat_ts_cig.main import run_pipeline
                        if mode == "Dry Run (Basic)":
                            dry = copy.deepcopy(config)
                            dry["llm"] = False
                            dry.setdefault("llm_ollama", {})["enabled"] = False
                            dry.setdefault("online", {})["enabled"] = False
                            dry.setdefault("advanced", {})["embeddings"] = {"enabled": False}
                            dry.setdefault("vector", {})["enabled"] = False
                            dry.setdefault("ingestion", {})["pdf_enabled"] = False
                            res = run_pipeline(seed_val, config_path=CONFIG_PATH, config=dry, ticks_override=10, progress_callback=_progress_cb)
                        else:
                            res = run_pipeline(seed_val, config_path=CONFIG_PATH, config=config, ticks_override=10, progress_callback=_progress_cb)
                    except Exception as e:
                        err = e
                    try:
                        _q.put((res, err))
                    except Exception:
                        pass

                _q = queue.Queue()
                st.session_state["_pipeline_queue"] = _q
                _t = threading.Thread(target=_run_bg)
                _t.start()
                st.session_state.pipeline_running = True
                st.session_state.pipeline_start_time = time.time()
                st.rerun()

    # Pipeline running view (when single run in background)
    if st.session_state.get("pipeline_running"):
        _thread = st.session_state.get("_pipeline_thread")
        if _thread is not None and not getattr(_thread, "is_alive", lambda: False)():
            st.session_state.pipeline_running = False
            st.session_state["_pipeline_thread"] = None
            _q = st.session_state.pop("_pipeline_queue", None)
            if _q:
                try:
                    res, err = _q.get_nowait()
                    st.session_state.last_run_result = {"error": str(err)} if err else res
                except queue.Empty:
                    st.session_state.last_run_result = {"error": "No result from pipeline."}
            st.rerun()
        else:
            elapsed = int(time.time() - st.session_state.get("pipeline_start_time", time.time()))
            st.info(f"Running pipeline... ({elapsed} s)")
            c, t, m = _progress_holder[0], _progress_holder[1], _progress_holder[2]
            if t and t > 0:
                st.progress(c / t, text=m)
            time.sleep(1)
            st.rerun()

# ========== Tab 3: Advanced Settings ==========
with tab3:
    st.header("Advanced Settings")
    config = load_config()
    with st.expander("Autonomous exploration"):
        adv = config.get("advanced_autonomous") or {}
        ref = st.number_input("Reflection cycles (extra runs per cycle)", 0, 10, int(adv.get("reflection_cycles", 3)), key="adv_ref")
        multi = st.text_area("Multi-seed (one per line)", value="\n".join(adv.get("multi_seed") or []), height=60, key="adv_multi")
        curiosity = st.slider("Curiosity bias (0=high activation, 1=novel nodes)", 0.0, 1.0, float(adv.get("curiosity_bias", 0.0)), 0.1, key="adv_curiosity")
        llm_ref = st.checkbox("LLM reflection (Ollama summary after autonomous)", value=bool(adv.get("llm_reflection", False)), key="adv_llm_ref")
    with st.expander("LLM (Ollama)"):
        o = config.get("llm_ollama") or {}
        st.text_input("Ollama host", value=o.get("host", "http://127.0.0.1:11434"), key="adv_ollama_host")
        st.text_input("Ollama model", value=o.get("model", "llama2"), key="adv_ollama_model")
    with st.expander("Online & limits"):
        on = config.get("online") or {}
        st.checkbox("Online search enabled", value=on.get("enabled", False), key="adv_online")
        st.number_input("Max requests per run", 10, 100, int(on.get("max_requests_per_run", 30)), key="adv_max_req")

    if st.button("Save advanced settings", key="save_adv"):
        cfg = load_config()
        cfg.setdefault("advanced_autonomous", {})
        cfg["advanced_autonomous"]["reflection_cycles"] = int(st.session_state.get("adv_ref", 3))
        cfg["advanced_autonomous"]["multi_seed"] = [ln.strip() for ln in (st.session_state.get("adv_multi") or "").splitlines() if ln.strip()]
        cfg["advanced_autonomous"]["curiosity_bias"] = float(st.session_state.get("adv_curiosity", 0.0))
        cfg["advanced_autonomous"]["llm_reflection"] = bool(st.session_state.get("adv_llm_ref", False))
        cfg.setdefault("llm_ollama", {})
        cfg["llm_ollama"]["host"] = st.session_state.get("adv_ollama_host", "http://127.0.0.1:11434")
        cfg["llm_ollama"]["model"] = st.session_state.get("adv_ollama_model", "llama2")
        cfg.setdefault("online", {})
        cfg["online"]["enabled"] = bool(st.session_state.get("adv_online", False))
        cfg["online"]["max_requests_per_run"] = int(st.session_state.get("adv_max_req", 30))
        err = save_config(cfg)
        if err:
            st.error(err)
        else:
            st.success("Saved.")

# ========== Tab 4: Run & Results ==========
with tab4:
    st.header("Run & Results")
    result = st.session_state.get("last_run_result")
    if not result:
        st.info("Run a pipeline from **Main Controls** to see results here.")
    else:
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(f"Seed **{result.get('seed', '')}** (node_id={result.get('node_id', '')})")
            if st.session_state.get("verbose_monitoring"):
                g = result.get("graph") or {}
                st.caption(f"Stats: {len(g.get('nodes', []))} nodes, {len(g.get('edges', []))} edges")

            cig = result.get("cig") or {}
            if cig.get("idea_map"):
                with st.expander("Idea map"):
                    st.json(cig["idea_map"])
            if cig.get("hypotheses"):
                with st.expander("Hypotheses"):
                    for h in cig["hypotheses"]:
                        st.write(f"**{h.get('from')}** → **{h.get('to')}**")
                        if h.get("natural_language"):
                            st.caption(h["natural_language"])
            if result.get("cycles"):
                with st.expander("Cycles summary"):
                    for i, cy in enumerate(result["cycles"]):
                        st.markdown(f"**Cycle {i+1}** (seed={cy.get('seed')}): queries={cy.get('queries', [])}, ingested={cy.get('ingested_count', 0)}")
            if result.get("reflection_suggestion"):
                with st.expander("LLM reflection"):
                    st.write(result["reflection_suggestion"])

            config = load_config()
            try:
                from goat_ts_cig.knowledge_graph import KnowledgeGraph
                from goat_ts_cig.graph_viz import export_subgraph_png
                nid = result.get("node_id")
                db = (config.get("graph") or {}).get("path", "data/knowledge_graph.db")
                if nid is not None and db and db != ":memory:":
                    kg = KnowledgeGraph(os.path.join(ROOT, db) if not os.path.isabs(db) else db)
                    out = os.path.join(ROOT, "data", "exports", "subgraph.png")
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    export_subgraph_png(kg, nid, out, depth=2, engine="graphviz")
                    st.image(out, caption="Graph (subgraph)", use_container_width=True)
                    with open(out, "rb") as f:
                        st.download_button("Download PNG", data=f.read(), file_name="subgraph.png", mime="image/png", key="dl_png")
                    kg.close()
            except Exception as e:
                st.caption(f"Graph viz: {e}")

            st.download_button(
                "Export result JSON",
                data=json.dumps(result, indent=2),
                file_name="cig_result.json",
                mime="application/json",
                key="dl_json",
            )
            # Export CSV and GraphML from current graph DB
            db = (config.get("graph") or {}).get("path", "data/knowledge_graph.db")
            if db and db != ":memory:":
                try:
                    from goat_ts_cig.knowledge_graph import KnowledgeGraph
                    from goat_ts_cig.export_utils import export_graph_csv, to_graphml
                    kg = KnowledgeGraph(os.path.join(ROOT, db) if not os.path.isabs(db) else db)
                    export_dir = os.path.join(ROOT, "data", "exports")
                    os.makedirs(export_dir, exist_ok=True)
                    csv_paths = export_graph_csv(kg, export_dir)
                    gml_path = os.path.join(export_dir, "graph.graphml")
                    to_graphml(kg, gml_path)
                    kg.close()
                    for p in csv_paths:
                        if os.path.isfile(p):
                            with open(p, "r", encoding="utf-8") as f:
                                st.download_button(f"Download {os.path.basename(p)}", data=f.read(), file_name=os.path.basename(p), mime="text/csv", key=f"dl_{os.path.basename(p)}")
                    if os.path.isfile(gml_path):
                        with open(gml_path, "r", encoding="utf-8") as f:
                            st.download_button("Download GraphML", data=f.read(), file_name="graph.graphml", mime="application/xml", key="dl_graphml")
                except Exception as e:
                    st.caption(f"Export CSV/GraphML: {e}")
