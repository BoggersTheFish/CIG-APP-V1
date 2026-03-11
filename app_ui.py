"""
CIG-APP UI: single-page Dry Run (basic) or Full Run (all features).
Run from project root: streamlit run app_ui.py
"""
from __future__ import annotations

import copy
import io
import json
import os
import subprocess
import sys
import time

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

if "cig_operation_in_progress" not in st.session_state:
    st.session_state.cig_operation_in_progress = False


def _set_busy(busy: bool) -> None:
    st.session_state.cig_operation_in_progress = busy


def _is_busy() -> bool:
    return st.session_state.get("cig_operation_in_progress", False)


def _load_env_overrides() -> None:
    env_path = os.path.join(ROOT, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        for line in open(env_path, encoding="utf-8", errors="replace"):
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
    config.setdefault("llm_ollama", {}).update({
        "enabled": config.get("llm_ollama", {}).get("enabled", False),
        "host": config.get("llm_ollama", {}).get("host", "http://127.0.0.1:11434"),
        "model": config.get("llm_ollama", {}).get("model", "llama2"),
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


def check_full_deps(config: dict) -> list[tuple[str, bool, str]]:
    """Return list of (display_name, ok, install_hint). All must be ok for Full Run."""
    result: list[tuple[str, bool, str]] = []

    # Ollama (local LLM)
    ollama_ok = False
    try:
        import requests as _req
        host = (config.get("llm_ollama") or {}).get("host", "http://127.0.0.1:11434")
        r = _req.get(host.rstrip("/") + "/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    result.append((
        "Ollama (local LLM)",
        ollama_ok,
        "Install from https://ollama.ai — then run e.g. ollama pull llama2 and ensure Ollama is running.",
    ))

    # Graphviz binary (dot)
    dot_ok = False
    try:
        r = subprocess.run(
            ["dot", "-V"],
            capture_output=True,
            timeout=2,
        )
        dot_ok = r.returncode == 0
    except Exception:
        pass
    result.append((
        "Graphviz (binary)",
        dot_ok,
        "Download Graphviz from https://graphviz.org and add to PATH.",
    ))

    # Graphviz Python
    gv_ok = False
    try:
        import graphviz  # noqa: F401
        gv_ok = True
    except Exception:
        pass
    result.append((
        "Graphviz (Python)",
        gv_ok,
        "pip install graphviz",
    ))

    # sentence-transformers
    st_ok = False
    try:
        import sentence_transformers  # noqa: F401
        st_ok = True
    except Exception:
        pass
    result.append((
        "sentence-transformers",
        st_ok,
        "pip install sentence-transformers",
    ))

    # sqlite-vss (vector search)
    vss_ok = False
    try:
        import sqlite_vss  # noqa: F401
        vss_ok = True
    except Exception:
        pass
    result.append((
        "sqlite-vss",
        vss_ok,
        "pip install sqlite-vss",
    ))

    # PyPDF2
    pdf_ok = False
    try:
        import PyPDF2  # noqa: F401
        pdf_ok = True
    except Exception:
        pass
    result.append((
        "PyPDF2",
        pdf_ok,
        "pip install PyPDF2",
    ))

    # beautifulsoup4
    bs4_ok = False
    try:
        import bs4  # noqa: F401
        bs4_ok = True
    except Exception:
        pass
    result.append((
        "beautifulsoup4",
        bs4_ok,
        "pip install beautifulsoup4",
    ))

    return result


# ----- Sidebar: theme only -----
if "theme" not in st.session_state:
    st.session_state.theme = "light"
theme = st.sidebar.selectbox(
    "UI Theme",
    ["light", "dark"],
    index=0 if st.session_state.get("theme") == "light" else 1,
    key="sidebar_theme",
)
st.session_state.theme = theme
_bg = "white" if theme == "light" else "#0e1117"
_fg = "black" if theme == "light" else "white"
st.markdown(
    f'<style>section[data-testid="stSidebar"] {{ background-color: {_bg}; color: {_fg}; }} .stApp {{ background-color: {_bg}; color: {_fg}; }}</style>',
    unsafe_allow_html=True,
)

# ----- Main: single page -----
st.title("CIG-APP: Contextual Information Generator")

# Seed (persisted via key="seed_input")
seed = st.text_input(
    "Enter your seed concept (e.g., artificial intelligence)",
    value="artificial intelligence",
    key="seed_input",
)

# Mode (persisted via key="mode_radio")
mode = st.radio(
    "Mode",
    ["Dry Run (Basic)", "Full Run (All Features)"],
    key="mode_radio",
)

config = load_config()
full_deps = check_full_deps(config) if mode == "Full Run (All Features)" else []
all_deps_ok = all(ok for _, ok, _ in full_deps) if full_deps else True

if mode == "Full Run (All Features)":
    st.subheader("Full Run dependencies")
    for name, ok, _ in full_deps:
        st.write(f"{'✅' if ok else '❌'} {name}")
    if not all_deps_ok:
        st.error("Missing dependencies — install them and click **Re-Check Deps** before running.")
        with st.expander("Install steps"):
            for name, ok, hint in full_deps:
                if not ok:
                    st.markdown(f"**{name}**")
                    st.code(hint, language="text")
        if st.button("Re-Check Deps", key="recheck_deps"):
            st.rerun()

run_disabled = _is_busy() or (mode == "Full Run (All Features)" and not all_deps_ok)

if st.button("Run", type="primary", disabled=run_disabled, key="btn_run"):
    if not seed.strip():
        st.error("Enter a seed concept.")
    else:
        _set_busy(True)
        seed_val = seed.strip()
        with st.status("Running...", expanded=True):
            try:
                from goat_ts_cig.main import run_pipeline
                if mode == "Dry Run (Basic)":
                    # Core only: TS propagation, graph, CIG outputs. No LLM, embeddings, vector, PDF, online.
                    dry_config = copy.deepcopy(config)
                    dry_config["llm"] = False
                    dry_config.setdefault("llm_ollama", {})["enabled"] = False
                    dry_config.setdefault("online", {})["enabled"] = False
                    dry_config.setdefault("advanced", {})["embeddings"] = {"enabled": False}
                    dry_config.setdefault("vector", {})["enabled"] = False
                    dry_config.setdefault("ingestion", {})["pdf_enabled"] = False
                    result = run_pipeline(
                        seed=seed_val,
                        config_path=CONFIG_PATH,
                        config=dry_config,
                        ticks_override=10,
                    )
                else:
                    # Full: use config as-is (ticks=10 hardcoded)
                    result = run_pipeline(
                        seed=seed_val,
                        config_path=CONFIG_PATH,
                        config=config,
                        ticks_override=10,
                    )
                st.session_state["last_run_result"] = result
            except Exception as e:
                st.session_state["last_run_result"] = {"error": str(e)}
            finally:
                _set_busy(False)
        st.rerun()

# ----- Output area -----
result = st.session_state.get("last_run_result")
if result:
    if result.get("error"):
        st.error(result["error"])
    else:
        st.success(f"Done. Seed **{result.get('seed', '')}** (node_id={result.get('node_id', '')}).")
        cig = result.get("cig") or {}
        # Text: idea map, context expansion
        if cig.get("idea_map"):
            with st.expander("Idea map"):
                st.json(cig["idea_map"])
        if cig.get("context_expansion"):
            with st.expander("Context expansion"):
                st.write(cig["context_expansion"])
        # Hypotheses
        if cig.get("hypotheses"):
            with st.expander("Hypotheses"):
                for h in cig["hypotheses"]:
                    st.write(f"**{h.get('from', '')}** → **{h.get('to', '')}**")
                    if h.get("natural_language"):
                        st.caption(h["natural_language"])
        # Graph image (Full only)
        if mode == "Full Run (All Features)":
            try:
                from goat_ts_cig.knowledge_graph import KnowledgeGraph
                from goat_ts_cig.graph_viz import export_subgraph_png
                node_id = result.get("node_id")
                if node_id is not None:
                    db_path = (config.get("graph") or {}).get("path", "data/knowledge_graph.db")
                    if db_path and db_path != ":memory:":
                        kg = KnowledgeGraph(db_path)
                        out_path = os.path.join(ROOT, "data", "exports", "subgraph.png")
                        os.makedirs(os.path.dirname(out_path), exist_ok=True)
                        export_subgraph_png(kg, node_id, out_path, depth=2, engine="graphviz")
                        st.image(out_path, caption="Graph (subgraph)", use_container_width=True)
                        with open(out_path, "rb") as f:
                            st.download_button("Download graph PNG", data=f.read(), file_name="subgraph.png", mime="image/png", key="dl_png")
                        kg.close()
            except Exception as e:
                st.caption(f"Graph viz skipped: {e}")
        # Export JSON
        out_json = json.dumps(result, indent=2)
        st.download_button(
            "Download result JSON",
            data=out_json,
            file_name="cig_result.json",
            mime="application/json",
            key="dl_json",
        )
