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
    # Phase 14: Env overrides for Ollama (OLLAMA_HOST/MODEL or CIG_OLLAMA_*)
    default_host = "http://127.0.0.1:11434"
    default_model = "llama2"
    if os.environ.get("OLLAMA_HOST", "").strip():
        default_host = os.environ.get("OLLAMA_HOST", default_host).strip()
    elif os.environ.get("CIG_OLLAMA_HOST", "").strip():
        default_host = os.environ.get("CIG_OLLAMA_HOST", default_host).strip()
    if os.environ.get("OLLAMA_MODEL", "").strip():
        default_model = os.environ.get("OLLAMA_MODEL", default_model).strip()
    elif os.environ.get("CIG_OLLAMA_MODEL", "").strip():
        default_model = os.environ.get("CIG_OLLAMA_MODEL", default_model).strip()
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


def check_advanced_deps(config: dict) -> list[tuple[str, bool, str | None]]:
    """Phase 13: Dependency checks for Advanced Features (Ollama, Graphviz, Matplotlib).
    Returns list of (display_name, ok, pip_cmd_or_none). None = no pip (e.g. Ollama = external).
    """
    result: list[tuple[str, bool, str | None]] = []

    # Ollama (local LLM) — detected via API, no pip
    ollama_ok = False
    try:
        import requests as _req
        host = (config.get("llm_ollama") or {}).get("host", "http://127.0.0.1:11434")
        r = _req.get(host.rstrip("/") + "/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    result.append(("Ollama (local LLM)", ollama_ok, None))

    # Graphviz (Python) — pip install graphviz
    gv_ok = False
    try:
        import graphviz  # noqa: F401
        gv_ok = True
    except Exception:
        pass
    result.append(("Graphviz (Python)", gv_ok, "pip install graphviz"))

    # Matplotlib — pip install matplotlib
    mpl_ok = False
    try:
        import matplotlib  # noqa: F401
        mpl_ok = True
    except Exception:
        pass
    result.append(("Matplotlib", mpl_ok, "pip install matplotlib"))

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

# ----- Sidebar: 6. Advanced Features (Phase 13, Steps 59-62) -----
_config_for_adv = load_config()
_adv_deps = check_advanced_deps(_config_for_adv)
with st.sidebar.expander("6. Advanced Features", expanded=False):
    st.caption("Optional deps for LLM, graph viz, and exports.")
    for name, ok, pip_cmd in _adv_deps:
        st.write(f"{'✅' if ok else '❌'} {name}")
    # Phase 14: Ollama not detected warning
    _ollama_ok = next((ok for n, ok, _ in _adv_deps if "Ollama" in n), False)
    if not _ollama_ok:
        st.warning("Ollama not detected. Install from https://ollama.ai and start the server for LLM features.")
    # Ollama host and model (Phase 14, Steps 63-67)
    _ollama_cfg = _config_for_adv.get("llm_ollama") or {}
    st.text_input(
        "Ollama host",
        value=_ollama_cfg.get("host", "http://127.0.0.1:11434"),
        key="adv_ollama_host",
        help="e.g. http://127.0.0.1:11434",
    )
    _model_opts = ["llama2", "llama3.2", "mistral", "phi3", "Other"]
    _cur_model = _ollama_cfg.get("model", "llama2")
    _model_idx = _model_opts.index(_cur_model) if _cur_model in _model_opts else _model_opts.index("Other")
    st.selectbox(
        "Ollama model",
        _model_opts,
        index=_model_idx,
        key="adv_ollama_model_sel",
    )
    if st.session_state.get("adv_ollama_model_sel") == "Other":
        st.text_input("Custom model name", value=_cur_model if _cur_model not in _model_opts else "", key="adv_ollama_model_custom")
    # Master toggle (persisted in config)
    adv_enabled = st.checkbox(
        "Enable advanced features",
        value=_config_for_adv.get("advanced_features_enabled", False),
        key="adv_features_enabled",
        help="Use Ollama, Graphviz, Matplotlib when available.",
    )
    # Install buttons for pip-installable deps
    for name, ok, pip_cmd in _adv_deps:
        if ok or not pip_cmd:
            continue
        # pip_cmd is e.g. "pip install graphviz"
        pkg = pip_cmd.replace("pip install", "").strip() if pip_cmd else None
        if pkg and st.button(f"Install {name}", key=f"adv_install_{name.replace(' ', '_')}", disabled=_is_busy()):
            _set_busy(True)
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                )
                if r.returncode == 0:
                    st.success(f"Installed {pkg}. Re-check deps by re-opening this section.")
                else:
                    st.code(r.stderr or r.stdout or "pip failed")
            finally:
                _set_busy(False)
            st.rerun()
    _ollama_missing = any(not ok and pip_cmd is None for _, ok, pip_cmd in _adv_deps)
    if _ollama_missing:
        st.caption("Ollama: install from https://ollama.ai and ensure the server is running.")
    # ----- Phase 15-16: Graph visualization and exports (Steps 68-74) -----
    st.markdown("---")
    st.caption("Graph visualization")
    _last_seed = (st.session_state.get("last_run_result") or {}).get("seed", "")
    _viz_seed = st.text_input("Seed label for graph", value=_last_seed or "artificial intelligence", key="adv_viz_seed")
    _gv_ok = next((ok for n, ok, _ in _adv_deps if "Graphviz" in n and "Python" in n), False)
    _mpl_ok = next((ok for n, ok, _ in _adv_deps if n == "Matplotlib"), False)
    _viz_engine = "graphviz" if _gv_ok else ("matplotlib" if _mpl_ok else None)
    if _viz_engine and st.button("Visualize Graph", key="adv_viz_btn", disabled=_is_busy()):
        _set_busy(True)
        try:
            from goat_ts_cig.knowledge_graph import KnowledgeGraph
            from goat_ts_cig.graph_viz import export_subgraph_png
            _db = (_config_for_adv.get("graph") or {}).get("path", "data/knowledge_graph.db")
            if not _db or _db == ":memory:":
                st.warning("Graph path is in-memory or missing. Run a pipeline first with a file DB.")
            else:
                _kg = KnowledgeGraph(os.path.join(ROOT, _db) if not os.path.isabs(_db) else _db)
                _node = _kg.get_node_by_label(_viz_seed.strip()) if _viz_seed.strip() else None
                if not _node:
                    st.warning(f"Seed label '{_viz_seed}' not found in graph.")
                else:
                    _out = os.path.join(ROOT, "data", "exports", "subgraph.png")
                    os.makedirs(os.path.dirname(_out), exist_ok=True)
                    export_subgraph_png(_kg, _node["id"], _out, depth=2, engine=_viz_engine)
                    st.session_state["adv_viz_graph_path"] = _out
                _kg.close()
        except Exception as e:
            st.error(str(e))
        finally:
            _set_busy(False)
        st.rerun()
    if not _viz_engine:
        st.caption("Install Graphviz or Matplotlib to visualize.")
    _viz_path = st.session_state.get("adv_viz_graph_path")
    if _viz_path and os.path.isfile(_viz_path):
        st.image(_viz_path, caption="Graph (subgraph)", use_container_width=True)
        with open(_viz_path, "rb") as _f:
            st.download_button("Download graph PNG", data=_f.read(), file_name="subgraph.png", mime="image/png", key="adv_dl_png")
    st.caption("Export data")
    _export_dir = (_config_for_adv.get("export") or {}).get("default_dir", "data/exports")
    _export_dir_resolved = os.path.join(ROOT, _export_dir) if not os.path.isabs(_export_dir) else _export_dir
    if st.button("Export CSV", key="adv_export_csv_btn", disabled=_is_busy()):
        _set_busy(True)
        try:
            from goat_ts_cig.knowledge_graph import KnowledgeGraph
            from goat_ts_cig.export_utils import export_graph_csv
            _db = (_config_for_adv.get("graph") or {}).get("path", "data/knowledge_graph.db")
            if not _db or _db == ":memory:":
                st.warning("Graph path is in-memory or missing.")
            else:
                _kg = KnowledgeGraph(os.path.join(ROOT, _db) if not os.path.isabs(_db) else _db)
                _paths = export_graph_csv(_kg, _export_dir_resolved)
                _kg.close()
                st.session_state["adv_export_csv_paths"] = _paths
        except Exception as e:
            st.error(str(e))
        finally:
            _set_busy(False)
        st.rerun()
    _csv_paths = st.session_state.get("adv_export_csv_paths", [])
    if _csv_paths:
        for _p in _csv_paths:
            if os.path.isfile(_p):
                with open(_p, "r", encoding="utf-8") as _f:
                    st.download_button(f"Download {os.path.basename(_p)}", data=_f.read(), file_name=os.path.basename(_p), mime="text/csv", key=f"adv_dl_csv_{os.path.basename(_p)}")
    if st.button("Export GraphML", key="adv_export_graphml_btn", disabled=_is_busy()):
        _set_busy(True)
        try:
            from goat_ts_cig.knowledge_graph import KnowledgeGraph
            from goat_ts_cig.export_utils import to_graphml
            _db = (_config_for_adv.get("graph") or {}).get("path", "data/knowledge_graph.db")
            if not _db or _db == ":memory:":
                st.warning("Graph path is in-memory or missing.")
            else:
                _kg = KnowledgeGraph(os.path.join(ROOT, _db) if not os.path.isabs(_db) else _db)
                _gml_path = os.path.join(_export_dir_resolved, "graph.graphml")
                os.makedirs(_export_dir_resolved, exist_ok=True)
                to_graphml(_kg, _gml_path)
                _kg.close()
                st.session_state["adv_export_graphml_path"] = _gml_path
        except Exception as e:
            st.error(str(e))
        finally:
            _set_busy(False)
        st.rerun()
    _gml_path = st.session_state.get("adv_export_graphml_path")
    if _gml_path and os.path.isfile(_gml_path):
        with open(_gml_path, "r", encoding="utf-8") as _f:
            st.download_button("Download GraphML", data=_f.read(), file_name="graph.graphml", mime="application/xml", key="adv_dl_graphml")
    # Save advanced settings to config (Phase 14: include Ollama host/model)
    if st.button("Save advanced settings", key="save_adv_settings", disabled=_is_busy()):
        cfg = load_config()
        cfg["advanced_features_enabled"] = st.session_state.get("adv_features_enabled", False)
        cfg.setdefault("llm_ollama", {})
        cfg["llm_ollama"]["host"] = (st.session_state.get("adv_ollama_host") or "http://127.0.0.1:11434").strip()
        _sel = st.session_state.get("adv_ollama_model_sel", "llama2")
        _model = (st.session_state.get("adv_ollama_model_custom") or "").strip() if _sel == "Other" else _sel
        cfg["llm_ollama"]["model"] = _model or "llama2"
        err = save_config(cfg)
        if err:
            st.sidebar.error(err)
        else:
            st.sidebar.success("Saved.")
        st.rerun()

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
