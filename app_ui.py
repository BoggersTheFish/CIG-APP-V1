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
import time
import webbrowser
from types import SimpleNamespace

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

# Global lock: when any long-running operation is in progress, other action buttons are disabled
if "cig_operation_in_progress" not in st.session_state:
    st.session_state.cig_operation_in_progress = False

# Lightweight activity log so the user can see what actions the app is taking.
if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


def _set_busy(busy: bool) -> None:
    st.session_state.cig_operation_in_progress = busy


def _is_busy() -> bool:
    return st.session_state.get("cig_operation_in_progress", False)


def _append_log(msg: str) -> None:
    """Append a short, human-readable line to the activity log."""
    try:
        ts = time.strftime("%H:%M:%S")
    except Exception:
        ts = "--:--:--"
    line = f"[{ts}] {msg}"
    st.session_state.activity_log.append(line)
    # Keep the log bounded so it does not grow forever.
    if len(st.session_state.activity_log) > 400:
        st.session_state.activity_log = st.session_state.activity_log[-400:]


def _append_log_output(text: str, max_lines: int = 10) -> None:
    """Append a short snippet of command/output to the activity log (last max_lines)."""
    if not (text and text.strip()):
        return
    lines = [ln.rstrip()[:200] for ln in text.strip().splitlines()]
    for ln in lines[-max_lines:]:
        _append_log("  │ " + ln)


def _start_streamlit_with_venv(venv_python: str, port: int = 8502) -> None:
    """Start streamlit with the venv Python on the given port and open the browser."""
    app_path = os.path.join(ROOT, "app_ui.py")
    url = f"http://localhost:{port}"
    try:
        kwargs = {"cwd": ROOT, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        if sys.platform != "win32":
            kwargs["start_new_session"] = True
        subprocess.Popen(
            [venv_python, "-m", "streamlit", "run", app_path, "--server.port", str(port)],
            **kwargs,
        )
        time.sleep(4)
        webbrowser.open(url)
    except FileNotFoundError:
        st.warning("Could not start Streamlit in .venv. Install deps in .venv: `.venv\\Scripts\\pip install -r requirements.txt` then run `.venv\\Scripts\\python -m streamlit run app_ui.py`.")
    except Exception:
        pass
    st.markdown(f"**Open the app (with .venv):** [{url}]({url})")
    st.caption("If the tab shows \"connection refused\", run manually: **`.venv\\Scripts\\python -m streamlit run app_ui.py`** (Windows) or **`.venv/bin/python -m streamlit run app_ui.py`** (Linux/Mac). Stop the current server with Ctrl+C first.")


def _load_env_overrides():
    """Apply .env overrides (CIG_ONLINE_ENABLED, CIG_SEARCH_API_KEY) to environment."""
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


def load_config():
    _load_env_overrides()
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8", errors="replace") as f:
            config = yaml.safe_load(f) or {}
    except Exception:
        config = {}
    # Env overrides
    if os.environ.get("CIG_ONLINE_ENABLED", "").lower() in ("1", "true"):
        config.setdefault("online", {})["enabled"] = True
    key = os.environ.get("CIG_SEARCH_API_KEY", "").strip()
    if key:
        config.setdefault("online", {})["search_api_key"] = key
    if os.environ.get("CIG_OLLAMA_HOST", "").strip():
        config.setdefault("llm_ollama", {})["host"] = os.environ.get("CIG_OLLAMA_HOST", "").strip()
    if os.environ.get("CIG_OLLAMA_MODEL", "").strip():
        config.setdefault("llm_ollama", {})["model"] = os.environ.get("CIG_OLLAMA_MODEL", "").strip()
    # Defaults for Advanced Features keys
    config.setdefault("llm_ollama", {}).update({
        "enabled": config.get("llm_ollama", {}).get("enabled", False),
        "host": config.get("llm_ollama", {}).get("host", "http://127.0.0.1:11434"),
        "model": config.get("llm_ollama", {}).get("model", "llama2"),
        "use_for_hypotheses": config.get("llm_ollama", {}).get("use_for_hypotheses", False),
        "use_for_autonomous": config.get("llm_ollama", {}).get("use_for_autonomous", False),
    })
    config.setdefault("export", {}).setdefault("default_dir", "data/exports")
    config.setdefault("advanced_autonomous", {}).update({
        "reflection_cycles": config.get("advanced_autonomous", {}).get("reflection_cycles", 0),
        "multi_seed": config.get("advanced_autonomous", {}).get("multi_seed", []),
    })
    config.setdefault("monitoring", {}).setdefault("show_progress", False)
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
            encoding="utf-8",
            errors="replace",
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


def _optional_dep_spec(name: str, module: str, pip_packages: list[str] | None) -> tuple[str, str, list[str] | None]:
    """Return (display_name, import_module, pip_install_list or None for no pip install)."""
    return (name, module, pip_packages)


def _check_optional_deps(config: dict) -> list[tuple[str, bool, list[str] | None]]:
    """Return list of (display_name, installed, pip_packages or None)."""
    import importlib.util
    result: list[tuple[str, bool, list[str] | None]] = []
    for name, mod, pip in [
        _optional_dep_spec("Graphviz (Python)", "graphviz", ["graphviz"]),
        _optional_dep_spec("NetworkX", "networkx", ["networkx"]),
        _optional_dep_spec("Matplotlib", "matplotlib", ["matplotlib"]),
        _optional_dep_spec("BeautifulSoup (search)", "bs4", None),
        _optional_dep_spec("Sentence Transformers (embeddings)", "sentence_transformers", ["sentence-transformers"]),
    ]:
        ok = importlib.util.find_spec(mod) is not None
        result.append((name, ok, pip))
    ollama_ok = False
    try:
        import requests as _req
        host = (config.get("llm_ollama") or {}).get("host", "http://127.0.0.1:11434")
        r = _req.get(host.rstrip("/") + "/api/tags", timeout=2)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    result.append(("Ollama (local LLM)", ollama_ok, None))
    return result


# ----- Sidebar: step selection -----
st.sidebar.title("CIG-APP")
st.sidebar.caption("Contextual Information Generator")
st.sidebar.markdown("---")
step = st.sidebar.radio(
    "Step",
    [
        "1. Setup",
        "2. Configuration",
        "3. Run & Explore",
        "4. Optional Tools",
        "5. Autonomous Exploration",
        "6. Advanced Features",
    ],
    index=0,
)
st.sidebar.caption("Run from project root: `python -m streamlit run app_ui.py`")

# ----- Sidebar: theme toggle (persist in session) -----
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

# ----- Sidebar: optional dependency status & one-click install (Steps 43-44) -----
_config_sidebar = load_config()
_optional_deps = _check_optional_deps(_config_sidebar)
with st.sidebar.expander("Feature status", expanded=False):
    st.caption("Optional dependencies. Install missing ones below or in **6. Advanced Features**.")
    for name, installed, pip_packages in _optional_deps:
        if installed:
            st.markdown(f"- **{name}**: installed")
        else:
            if pip_packages:
                st.markdown(f"- **{name}**: missing (`pip install {' '.join(pip_packages)}`)")
            else:
                st.markdown(f"- **{name}**: not detected (see Step 6 for setup)")
    st.caption("One-click install (pip):")
    for name, installed, pip_packages in _optional_deps:
        if installed or not pip_packages:
            continue
        key_confirm = f"sidebar_confirm_install_{name.replace(' ', '_')}"
        key_btn = f"sidebar_install_{name.replace(' ', '_')}"
        if st.checkbox(f"Install {name}", value=False, key=key_confirm, disabled=_is_busy()):
            if st.button(f"Run pip install {' '.join(pip_packages)}", key=key_btn, disabled=_is_busy()):
                _set_busy(True)
                try:
                    _append_log(f"Sidebar: installing {name} ({' '.join(pip_packages)}) (CMD: {sys.executable} -m pip install {' '.join(pip_packages)}, cwd={ROOT}).")
                    r = subprocess.run(
                        [sys.executable, "-m", "pip", "install", *pip_packages],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=120,
                    )
                    if r.returncode == 0:
                        st.sidebar.success(f"Installed {name}. Refresh the page to update status.")
                        _append_log(f"Sidebar: installed {name}.")
                    else:
                        st.sidebar.error(r.stderr or r.stdout or "Install failed.")
                        _append_log_output((r.stderr or r.stdout or "").strip(), 6)
                finally:
                    _set_busy(False)
                st.rerun()
    st.caption("Ollama: install from https://ollama.ai — then configure in Step 6.")

if _is_busy():
    st.sidebar.warning("Operation in progress — wait for it to finish.")

# ----- Global: show when an operation is running -----
if _is_busy():
    st.info("⏳ **An operation is in progress.** Please wait for it to finish. Other buttons are disabled.")

# Global activity view so the user can see what is going on under the hood.
log_lines = st.session_state.get("activity_log", [])
with st.expander("Activity details (what the app is doing)", expanded=False):
    if log_lines:
        # Show the most recent part of the log.
        st.code("\n".join(log_lines[-200:]), language="text")
    else:
        st.caption("No activity yet. When you click buttons, commands and steps will appear here.")

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
        st.caption("Install Rust from https://rustup.rs if needed. Then install toolchain and build extension.")
        if rust_ok and st.button("Run rustup install stable", disabled=_is_busy(), key="btn_rustup_install"):
            _set_busy(True)
            try:
                _append_log(f"Starting: rustup install stable (CMD: rustup install stable, cwd={ROOT}).")
                prog = st.progress(0, text="Installing Rust stable toolchain...")
                with st.status("Running rustup install stable...", expanded=True):
                    r = subprocess.run(
                        ["rustup", "install", "stable"],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=300,
                    )
                    if r.returncode == 0:
                        st.success("Rust stable toolchain installed or already up to date.")
                        _append_log("Finished: rustup install stable (success).")
                    else:
                        st.error(r.stderr or r.stdout or "rustup failed")
                        _append_log("Finished: rustup install stable (failed). See Setup details and terminal output for errors.")
                        _append_log_output((r.stderr or r.stdout or "").strip(), 8)
                prog.progress(1.0, text="Done.")
            finally:
                _set_busy(False)
        if rust_ok and st.button("Build Rust extension (maturin develop)", disabled=_is_busy(), key="btn_maturin_develop"):
            _set_busy(True)
            try:
                _append_log("Starting: build Rust extension (maturin develop).")
                in_venv = getattr(sys, "prefix", None) != getattr(sys, "base_prefix", None)
                venv_dir = os.path.join(ROOT, ".venv")
                if sys.platform == "win32":
                    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
                else:
                    venv_python = os.path.join(venv_dir, "bin", "python")
                use_venv = not in_venv
                combined = ""
                prog = st.progress(0, text="Building Rust extension...")
                with st.status("Running maturin develop...", expanded=True):
                    if use_venv:
                        if not os.path.isdir(venv_dir):
                            st.caption("No virtualenv detected. Creating .venv...")
                            _append_log(f"No active virtualenv. Creating .venv for build (CMD: {sys.executable} -m venv {venv_dir}, cwd={ROOT}).")
                            r0 = subprocess.run(
                                [sys.executable, "-m", "venv", venv_dir],
                                cwd=ROOT,
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                timeout=60,
                            )
                            if r0.returncode != 0:
                                st.error("Failed to create .venv: " + (r0.stderr or r0.stdout or ""))
                                combined = (r0.stdout or "") + "\n" + (r0.stderr or "")
                                _append_log("Failed to create .venv. See activity details and output for errors.")
                            else:
                                st.caption("Installing maturin into .venv...")
                                _append_log(f"Created .venv. Installing maturin into .venv (CMD: {venv_python} -m pip install maturin, cwd={ROOT}).")
                                r1 = subprocess.run(
                                    [venv_python, "-m", "pip", "install", "maturin"],
                                    cwd=ROOT,
                                    capture_output=True,
                                    text=True,
                                    encoding="utf-8",
                                    errors="replace",
                                    timeout=120,
                                )
                                if r1.returncode != 0:
                                    st.error("Failed to install maturin in .venv: " + (r1.stderr or r1.stdout or ""))
                                    combined = (r1.stdout or "") + "\n" + (r1.stderr or "")
                                    _append_log("Failed to install maturin in .venv.")
                                else:
                                    st.caption("Installing app dependencies (Streamlit, etc.) into .venv...")
                                    _append_log(f"Installing requirements.txt into .venv (including Streamlit) (CMD: {venv_python} -m pip install -r requirements.txt, cwd={ROOT}).")
                                    r_req = subprocess.run(
                                        [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
                                        cwd=ROOT,
                                        capture_output=True,
                                        text=True,
                                        encoding="utf-8",
                                        errors="replace",
                                        timeout=180,
                                    )
                                    if r_req.returncode != 0:
                                        st.warning("Could not install full requirements in .venv: " + (r_req.stderr or r_req.stdout or "")[:500])
                                        _append_log("requirements.txt install in .venv reported errors; build will continue but Streamlit in .venv may be incomplete.")
                                    r = subprocess.run(
                                        [venv_python, "-m", "maturin", "develop", "--manifest-path=rust/Cargo.toml"],
                                        cwd=ROOT,
                                        capture_output=True,
                                        text=True,
                                        encoding="utf-8",
                                        errors="replace",
                                        timeout=300,
                                    )
                                    out = (r.stdout or "").strip()
                                    err = (r.stderr or "").strip()
                                    combined = (out + "\n" + err).strip() or "(no output)"
                                    if r.returncode == 0:
                                        _start_streamlit_with_venv(venv_python)
                                        st.success("Rust extension built in .venv. Opening app with .venv… (Rust 'dead code' warnings above are harmless.)")
                                        _append_log("Rust extension built in .venv successfully. Launched app using .venv Python.")
                                    else:
                                        st.error("Build failed. See output below.")
                                        _append_log("Rust extension build in .venv failed. See activity details for the maturin output.")
                                    if combined:
                                        st.code(combined, language="text")
                                        _append_log_output(combined, 12)
                        else:
                            st.caption("Using existing .venv...")
                            _append_log(f"Using existing .venv for Rust build (CMD sequence: {venv_python} -m pip install maturin && {venv_python} -m pip install -r requirements.txt && {venv_python} -m maturin develop --manifest-path=rust/Cargo.toml, cwd={ROOT}).")
                            subprocess.run(
                                [venv_python, "-m", "pip", "install", "maturin"],
                                cwd=ROOT,
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                timeout=120,
                            )
                            subprocess.run(
                                [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
                                cwd=ROOT,
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                timeout=180,
                            )
                            r = subprocess.run(
                                [venv_python, "-m", "maturin", "develop", "--manifest-path=rust/Cargo.toml"],
                                cwd=ROOT,
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                errors="replace",
                                timeout=300,
                            )
                            out = (r.stdout or "").strip()
                            err = (r.stderr or "").strip()
                            combined = (out + "\n" + err).strip() or "(no output)"
                            if r.returncode == 0:
                                _start_streamlit_with_venv(venv_python)
                                st.success("Rust extension built in .venv. Opening app with .venv… (Rust 'dead code' warnings above are harmless.)")
                                _append_log("Rust extension built successfully in existing .venv. Launched app using .venv Python.")
                            else:
                                st.error("Build failed. See output below.")
                                _append_log("Rust extension build in existing .venv failed. See activity details for the maturin output.")
                        if combined:
                            st.code(combined, language="text")
                            _append_log_output(combined, 12)
                    else:
                        _append_log(f"Running maturin develop in the currently active environment (no .venv auto-creation) (CMD: {sys.executable} -m maturin develop --manifest-path=rust/Cargo.toml, cwd={ROOT}).")
                        r = subprocess.run(
                            [sys.executable, "-m", "maturin", "develop", "--manifest-path=rust/Cargo.toml"],
                            cwd=ROOT,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=300,
                        )
                        out = (r.stdout or "").strip()
                        err = (r.stderr or "").strip()
                        combined = (out + "\n" + err).strip() or "(no output)"
                        if r.returncode == 0:
                            st.success("Rust extension built. You can use propagation and similarity now. (Rust 'dead code' warnings above are harmless.)")
                            _append_log("Rust extension built successfully in the current environment.")
                        else:
                            st.error("Build failed. See output below for the actual error.")
                            st.caption("If the error mentions permissions or target directory, try a fresh venv.")
                            _append_log("Rust extension build failed in the current environment. See activity details for the maturin output.")
                        st.code(combined, language="text")
                        if combined:
                            _append_log_output(combined, 12)
                prog.progress(1.0, text="Done.")
            finally:
                _append_log("Finished: build Rust extension step.")
                _set_busy(False)
        if not rust_ok:
            st.caption("Install Rust first: https://rustup.rs — then rerun this step.")
        if st.button("Run pip install -r requirements.txt", disabled=_is_busy(), key="btn_pip_install"):
            _set_busy(True)
            try:
                _append_log(f"Starting: pip install -r requirements.txt (current Python) (CMD: {sys.executable} -m pip install -r requirements.txt, cwd={ROOT}).")
                prog = st.progress(0, text="Installing dependencies...")
                r = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                )
                prog.progress(1.0, text="Done.")
                if r.returncode == 0:
                    st.success("Install finished.")
                    _append_log("Finished: pip install -r requirements.txt (success).")
                else:
                    st.error(r.stderr or r.stdout)
                    _append_log("Finished: pip install -r requirements.txt (failed). See output for errors.")
                    _append_log_output((r.stderr or r.stdout or "").strip(), 8)
            finally:
                _set_busy(False)
        st.divider()
        st.markdown("**Setup scripts** (optional):")
        script_win = os.path.join(ROOT, "setup_windows.ps1")
        script_unix = os.path.join(ROOT, "setup_lowend.sh")
        col_win, col_unix = st.columns(2)
        with col_win:
            if os.path.isfile(script_win):
                if st.button("Run setup_windows.ps1", disabled=_is_busy(), key="btn_setup_win", help="Run Windows setup script (PowerShell)."):
                    _set_busy(True)
                    try:
                        _append_log(f"Starting: setup_windows.ps1 (PowerShell) (CMD: powershell -ExecutionPolicy Bypass -File {script_win}, cwd={ROOT}).")
                        prog = st.progress(0, text="Running setup_windows.ps1...")
                        with st.status("Running Windows setup script...", expanded=True):
                            try:
                                r = subprocess.run(
                                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_win],
                                    cwd=ROOT,
                                    capture_output=True,
                                    text=True,
                                    encoding="utf-8",
                                    errors="replace",
                                    timeout=300,
                                )
                            except FileNotFoundError:
                                r = SimpleNamespace(returncode=1, stdout="", stderr="PowerShell not found. Run the script manually from a PowerShell window.")
                            if r.returncode == 0:
                                st.success("Script finished.")
                                _append_log("Finished: setup_windows.ps1 (success).")
                            else:
                                st.error(r.stderr or r.stdout or "Script failed.")
                                _append_log("Finished: setup_windows.ps1 (failed). See script output for details.")
                            out = (r.stdout or r.stderr or "(no output)").strip()
                            st.code(out, language="text")
                            _append_log_output(out, 8)
                        prog.progress(1.0, text="Done.")
                    finally:
                        _set_busy(False)
            else:
                st.caption("`setup_windows.ps1` not found.")
        with col_unix:
            if os.path.isfile(script_unix):
                if st.button("Run setup_lowend.sh", disabled=_is_busy(), key="btn_setup_unix", help="Run Linux/Mac setup script (bash)."):
                    _set_busy(True)
                    try:
                        _append_log(f"Starting: setup_lowend.sh (bash) (CMD: bash {script_unix}, cwd={ROOT}).")
                        prog = st.progress(0, text="Running setup_lowend.sh...")
                        with st.status("Running setup_lowend.sh...", expanded=True):
                            try:
                                r = subprocess.run(
                                    ["bash", script_unix],
                                    cwd=ROOT,
                                    capture_output=True,
                                    text=True,
                                    encoding="utf-8",
                                    errors="replace",
                                    timeout=300,
                                )
                            except FileNotFoundError:
                                r = SimpleNamespace(returncode=1, stdout="", stderr="bash not found. On Windows use WSL or Git Bash, or run this script on Linux/Mac.")
                            if r.returncode == 0:
                                st.success("Script finished.")
                                _append_log("Finished: setup_lowend.sh (success).")
                            else:
                                st.error(r.stderr or r.stdout or "Script failed.")
                                _append_log("Finished: setup_lowend.sh (failed). See script output for details.")
                            out = (r.stdout or r.stderr or "(no output)").strip()
                            st.code(out, language="text")
                            _append_log_output(out, 8)
                        prog.progress(1.0, text="Done.")
                    finally:
                        _set_busy(False)
            else:
                st.caption("`setup_lowend.sh` not found.")
    if not py_ok:
        st.warning("Python 3.12+ is required. Install from python.org or your package manager.")
    if not pip_ok:
        st.warning("Run `pip install -r requirements.txt` from the project root.")
    if not ext_ok and rust_ok:
        st.info("Rust extension is optional. Pipeline runs without it; propagation and similarity will be skipped.")
    if py_ok and pip_ok:
        st.success("Environment ready. Continue to **Configuration** then **Run & Explore**.")

# ----- 2. Configuration -----
elif step == "2. Configuration":
    st.header("2. Configuration")
    st.markdown("Edit `config.yaml` and optional parameters. Changes are saved when you click **Save configuration**.")
    config = load_config()
    if not config and not os.path.isfile(CONFIG_PATH):
        st.info("No `config.yaml` found. Defaults will be used; click **Save configuration** to create one.")
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
        emb_enabled = st.checkbox(
            "Enable Embeddings (similarity via all-MiniLM-L6-v2)",
            value=bool(((config.get("advanced") or {}).get("embeddings") or {}).get("enabled", False)),
            help="Use lightweight embeddings for hypothesis similarity when Sentence Transformers is installed.",
            key="cfg_embeddings",
        )
        if not any(x[0] == "Sentence Transformers (embeddings)" and x[1] for x in _check_optional_deps(config)):
            st.caption("Install Sentence Transformers: pip install sentence-transformers (see Feature status in sidebar).")
        if "advanced" not in config:
            config["advanced"] = {}
        if "embeddings" not in config["advanced"]:
            config["advanced"]["embeddings"] = {}
        config["advanced"]["embeddings"]["enabled"] = emb_enabled

    with st.expander("LLM (optional)"):
        use_llm = st.checkbox(
            "Use LLM for hypothesis phrasing",
            value=bool(config.get("llm", False)),
            help="If enabled, uses the stub or Ollama (when configured in step 6) to phrase hypothesis suggestions.",
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

    if st.button("Save configuration", disabled=_is_busy(), key="btn_save_config"):
        _set_busy(True)
        try:
            _append_log("Saving configuration to config.yaml...")
            with st.status("Saving configuration...", expanded=True):
                err = save_config(config)
                if err:
                    st.error(f"Save failed: {err}")
                    _append_log(f"Save configuration failed: {err}")
                else:
                    st.success("Configuration saved to config.yaml")
                    _append_log("Configuration saved to config.yaml.")
        finally:
            _set_busy(False)

    st.caption("Advanced options (Ollama, export, reflection, monitoring): see **6. Advanced Features**.")
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
    online_ok = False
    run_local_only = True
    if autonomous_mode:
        st.caption("Runs 5 cycles: generate queries → optional web search → ingest → TS propagation.")
        from goat_ts_cig.autonomous_explore import check_online_available
        online_ok, online_msg = check_online_available(config)
        run_local_only = False
        if not online_ok:
            st.warning(online_msg)
            run_local_only = st.checkbox("Run in local-only mode (no web search)", value=True, key="run_local_3")

    ingest_option = st.radio(
        "Ingest text (optional)",
        ["None", "Paste text", "Upload file"],
        horizontal=True,
        help="Add text to the graph before propagation; words become nodes.",
    )
    ingest_text = None
    if ingest_option == "Paste text":
        ingest_text = st.text_area("Paste text to ingest (words become nodes, sequential links)", height=120, placeholder="Paste or type text here...")
    elif ingest_option == "Upload file":
        up = st.file_uploader("Upload a text file", type=["txt", "md"])
        if up:
            ingest_text = up.read().decode("utf-8", errors="replace")

    ticks_override = None
    if st.checkbox("Override wave ticks for this run"):
        ticks_override = st.number_input("Ticks", min_value=1, max_value=500, value=10)

    show_progress = (config.get("monitoring") or {}).get("show_progress", False)

    if st.button("Run pipeline", type="primary", disabled=_is_busy(), key="btn_run_pipeline"):
        if not seed:
            st.error("Enter a seed concept.")
        else:
            _set_busy(True)
            try:
                mode_label = "autonomous exploration" if autonomous_mode else "pipeline"
                _append_log(f"Starting: {mode_label} run with seed '{seed}' (ingest={ingest_option}, show_progress={show_progress}).")
                def _progress_cb(cur, tot, msg):
                    if tot and tot > 0:
                        st.session_state["_prog"] = (cur, tot, msg)
                spinner_msg = "Running pipeline..." if not autonomous_mode else "Running autonomous exploration..."
                if show_progress:
                    spinner_msg = "Running propagation..."
                prog = st.progress(0, text=spinner_msg)
                with st.status(spinner_msg, expanded=True):
                    try:
                        if autonomous_mode:
                            from goat_ts_cig.autonomous_explore import run_autonomous_explore
                            online_override = False if (not online_ok or run_local_only) else None
                            adv = config.get("advanced_autonomous") or {}
                            seeds_list = [seed] + (adv.get("multi_seed") or [])
                            result = run_autonomous_explore(
                                seed,
                                config_path=CONFIG_PATH,
                                config=config,
                                max_cycles=5,
                                max_queries_per_cycle=3,
                                online_override=online_override,
                                seeds=seeds_list if len(seeds_list) > 1 else None,
                            )
                        else:
                            from goat_ts_cig.main import run_pipeline
                            result = run_pipeline(
                                seed=seed,
                                config_path=CONFIG_PATH,
                                config=config,
                                ingest_text=ingest_text or None,
                                ticks_override=ticks_override,
                                progress_callback=_progress_cb if show_progress else None,
                            )
                    except Exception as e:
                        st.exception(e)
                        result = {"error": str(e)}
                        _append_log(f"{mode_label.capitalize()} run raised an exception: {e}")
                    st.session_state["last_run_result"] = result
                    if result and not result.get("error"):
                        g = result.get("graph") or {}
                        n_nodes = len(g.get("nodes", []))
                        n_edges = len(g.get("edges", []))
                        _append_log(f"Result: seed={result.get('seed')} node_id={result.get('node_id')} rust_used={result.get('rust_used')} nodes={n_nodes} edges={n_edges}")
                        for i, cy in enumerate(result.get("cycles") or []):
                            q = cy.get("queries", [])
                            ing = cy.get("ingested_count", 0)
                            _append_log(f"  Cycle {i+1}: queries={q}, ingested={ing}")
                prog.progress(1.0, text="Done.")
            finally:
                _append_log(f"Finished: {mode_label} run.")
                _set_busy(False)

    result = st.session_state.get("last_run_result")
    if result:
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(f"Done. Seed **{result['seed']}** (node_id={result['node_id']}). Rust used: **{result.get('rust_used', False)}**.")
            if result.get("cycles"):
                with st.expander("Cycles summary"):
                    for i, cy in enumerate(result["cycles"]):
                        seed_label = cy.get("seed", "")
                        extra = f" seed={seed_label}" if seed_label else ""
                        st.markdown(f"**Cycle {i+1}{extra}:** queries = {cy.get('queries', [])}, ingested = {cy.get('ingested_count', 0)}")
            # Simple dashboard: activation distribution of top nodes.
            g_dash = result.get("graph") or {}
            nodes_dash = g_dash.get("nodes") or []
            if nodes_dash:
                with st.expander("Dashboard (activation overview)"):
                    try:
                        import pandas as _pd  # lightweight and already common
                        df_nodes = _pd.DataFrame(nodes_dash)
                        if "activation" in df_nodes.columns and "label" in df_nodes.columns:
                            df_top = df_nodes.sort_values("activation", ascending=False).head(30)
                            st.bar_chart(data=df_top.set_index("label")["activation"])
                        else:
                            st.json(nodes_dash[:30])
                    except Exception:
                        st.json(nodes_dash[:30])
        if st.button("Clear result", key="clear_run_result", disabled=_is_busy()):
            del st.session_state["last_run_result"]
            st.rerun()
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
        if st.button("Run tests", disabled=_is_busy(), key="btn_run_tests"):
            _set_busy(True)
            try:
                _append_log(f"Starting: run_tests.py (pytest) (CMD: {sys.executable} run_tests.py, cwd={ROOT}).")
                prog = st.progress(0, text="Running tests...")
                with st.status("Running pytest...", expanded=True):
                    r = subprocess.run(
                        [sys.executable, "run_tests.py"],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=60,
                    )
                    if r.returncode == 0:
                        st.success("Tests passed.")
                        _append_log("Finished: tests passed.")
                    else:
                        st.error("Tests failed.")
                        _append_log("Finished: tests failed. See pytest output for details.")
                    out = (r.stdout or r.stderr or "(no output)").strip()
                    st.code(out, language="text")
                    _append_log_output(out, 12)
                prog.progress(1.0, text="Done.")
            finally:
                _set_busy(False)

    elif tool == "Run benchmark":
        st.caption("Times propagation on 500 and 1000 nodes (requires Rust extension).")
        if st.button("Run benchmark", disabled=_is_busy(), key="btn_benchmark"):
            _set_busy(True)
            try:
                _append_log(f"Starting: benchmark.py (propagation benchmark) (CMD: {sys.executable} benchmark.py, cwd={ROOT}).")
                prog = st.progress(0, text="Benchmarking...")
                with st.status("Running benchmark...", expanded=True):
                    r = subprocess.run(
                        [sys.executable, "benchmark.py"],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=120,
                    )
                    out = (r.stdout or r.stderr or "(no output)").strip()
                    st.code(out, language="text")
                    _append_log_output(out, 10)
                prog.progress(1.0, text="Done.")
            finally:
                _append_log("Finished: benchmark.py run.")
                _set_busy(False)

    elif tool == "View / edit config file":
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, encoding="utf-8", errors="replace") as f:
                raw = st.text_area("config.yaml", value=f.read(), height=300)
            if st.button("Overwrite config.yaml", disabled=_is_busy(), key="btn_overwrite_config"):
                _set_busy(True)
                try:
                    _append_log("Overwriting config.yaml from editor...")
                    with st.status("Saving config.yaml...", expanded=True):
                        try:
                            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                                f.write(raw)
                            st.success("Saved.")
                            _append_log("config.yaml overwritten successfully.")
                        except Exception as e:
                            st.error(str(e))
                            _append_log(f"Overwrite config failed: {e}")
                finally:
                    _set_busy(False)
        else:
            st.warning("config.yaml not found at project root.")

    elif tool == "Reset database":
        st.caption("Delete the SQLite database so the next run starts with an empty graph.")
        if (db_path or "").strip() == ":memory:":
            st.info("Database path is `:memory:` (in-memory). Nothing to delete; each run uses a fresh graph.")
        elif os.path.isfile(abs_db):
            st.warning(f"File exists: `{abs_db}`")
            if st.button("Delete database", type="secondary", disabled=_is_busy(), key="btn_delete_db"):
                _set_busy(True)
                try:
                    _append_log(f"Deleting database: {abs_db}")
                    with st.status("Deleting database...", expanded=True):
                        try:
                            os.remove(abs_db)
                            st.success("Database deleted.")
                            _append_log("Database deleted successfully.")
                        except Exception as e:
                            st.error(str(e))
                            _append_log(f"Delete database failed: {e}")
                finally:
                    _set_busy(False)
        else:
            st.info(f"No database file at `{abs_db}` yet.")

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
    human_loop = st.toggle("Human-in-Loop (pause after each cycle)", value=False, key="human_loop_5")

    show_progress_5 = (config.get("monitoring") or {}).get("show_progress", False)
    adv_5 = config.get("advanced_autonomous") or {}
    seeds_5 = [seed_auto.strip()] + (adv_5.get("multi_seed") or [])
    reflection_5 = int(adv_5.get("reflection_cycles") or 0)
    use_online_val = use_online_5 and (online_ok or not run_local_only_5)
    max_requests_5 = (config.get("online") or {}).get("max_requests_per_run", 30)
    timeout_5 = (config.get("online") or {}).get("timeout_seconds", 10)

    # Human-in-loop: run one cycle at a time and wait for Continue
    from goat_ts_cig.autonomous_explore import run_autonomous_one_cycle
    hilo = st.session_state.get("autonomous_human_loop") or {}
    if human_loop and hilo and st.button("Continue to next cycle", key="hilo_continue", disabled=_is_busy()):
        _set_busy(True)
        try:
            c_cycle = hilo.get("cycle", 0)
            c_seed_idx = hilo.get("seed_idx", 0)
            c_seeds = hilo.get("seeds", seeds_5)
            c_seed = c_seeds[c_seed_idx] if c_seed_idx < len(c_seeds) else seed_auto
            result, total_req, cycles_log = run_autonomous_one_cycle(
                CONFIG_PATH, config, c_seed, c_cycle, max_q, use_online_val,
                max_requests_5, timeout_5, hilo.get("total_requests", 0), hilo.get("cycles_log", []), reflection_5,
            )
            if result.get("error"):
                st.session_state["last_autonomous_result"] = result
                st.session_state["autonomous_human_loop"] = {}
            else:
                next_cycle = c_cycle + 1
                next_seed_idx = c_seed_idx
                if next_cycle >= max_cycles:
                    next_cycle = 0
                    next_seed_idx += 1
                if next_seed_idx >= len(c_seeds):
                    result["cycles"] = cycles_log
                    if adv_5.get("llm_reflection"):
                        try:
                            from goat_ts_cig.llm_ollama import generate as ollama_generate
                            ollama_cfg = (config.get("llm_ollama") or {})
                            if ollama_cfg.get("enabled"):
                                prompt = f"Autonomous exploration finished. Cycles: {cycles_log}. Summarize, note gaps, suggest 1-3 next seeds."
                                result["reflection_suggestion"] = ollama_generate(
                                    prompt, ollama_cfg.get("host", "http://127.0.0.1:11434"),
                                    ollama_cfg.get("model", "llama2"), timeout=60,
                                )
                        except Exception:
                            pass
                    st.session_state["last_autonomous_result"] = result
                    st.session_state["autonomous_human_loop"] = {}
                else:
                    st.session_state["autonomous_human_loop"] = {
                        "cycle": next_cycle, "seed_idx": next_seed_idx, "seeds": c_seeds,
                        "total_requests": total_req, "cycles_log": cycles_log,
                    }
                    st.session_state["last_autonomous_result"] = result
            _append_log(f"Human-in-loop: cycle {c_cycle + 1} done.")
        finally:
            _set_busy(False)
        st.rerun()

    if st.button("Run autonomous exploration", type="primary", key="run_auto", disabled=_is_busy()):
        if not seed_auto:
            st.error("Enter a seed query.")
        elif human_loop:
            _set_busy(True)
            try:
                _append_log("Starting: autonomous exploration (human-in-loop).")
                st.session_state["autonomous_human_loop"] = {"cycle": 0, "seed_idx": 0, "seeds": seeds_5, "total_requests": 0, "cycles_log": []}
                current_seed = seeds_5[0]
                result, tr, cl = run_autonomous_one_cycle(
                    CONFIG_PATH, config, current_seed, 0, max_q, use_online_val,
                    max_requests_5, timeout_5, 0, [], reflection_5,
                )
                st.session_state["last_autonomous_result"] = result
                if result.get("error"):
                    st.session_state["autonomous_human_loop"] = {}
                elif (max_cycles > 1) or (len(seeds_5) > 1):
                    next_c, next_s = 1, 0
                    if next_c >= max_cycles:
                        next_c, next_s = 0, 1
                    if next_s < len(seeds_5):
                        st.session_state["autonomous_human_loop"] = {"cycle": next_c, "seed_idx": next_s, "seeds": seeds_5, "total_requests": tr, "cycles_log": cl}
                    else:
                        st.session_state["autonomous_human_loop"] = {}
                else:
                    st.session_state["autonomous_human_loop"] = {}
                _append_log("Human-in-loop: cycle 1 done.")
            finally:
                _set_busy(False)
            st.rerun()
        else:
            _set_busy(True)
            try:
                _append_log(f"Starting: autonomous exploration seed='{seed_auto}' cycles={max_cycles} queries/cycle={max_q} online={use_online_5 and online_ok}.")
                prog = st.progress(0, text="Running autonomous exploration...")
                with st.status("Running autonomous exploration...", expanded=True):
                    try:
                        from goat_ts_cig.autonomous_explore import run_autonomous_explore
                        online_override = use_online_val
                        result = run_autonomous_explore(
                            seed_auto,
                            config_path=CONFIG_PATH,
                            config=config,
                            max_cycles=max_cycles,
                            max_queries_per_cycle=max_q,
                            online_override=online_override,
                            seeds=seeds_5 if len(seeds_5) > 1 else None,
                        )
                    except Exception as e:
                        st.exception(e)
                        result = {"error": str(e)}
                        _append_log(f"Autonomous exploration raised an exception: {e}")
                    st.session_state["last_autonomous_result"] = result
                    if result and not result.get("error"):
                        for i, cy in enumerate(result.get("cycles") or []):
                            q = cy.get("queries", [])
                            ing = cy.get("ingested_count", 0)
                            _append_log(f"  Cycle {i+1}: queries={q}, ingested={ing}")
                prog.progress(1.0, text="Done.")
                _append_log("Finished: autonomous exploration.")
            finally:
                _set_busy(False)

    result_auto = st.session_state.get("last_autonomous_result")
    if result_auto:
        if result_auto.get("error"):
            st.error(result_auto["error"])
        else:
            st.success(f"Done. Seed **{result_auto['seed']}** (node_id={result_auto['node_id']}).")
            with st.expander("Cycles summary"):
                for i, cy in enumerate(result_auto.get("cycles", [])):
                    seed_label = cy.get("seed", "")
                    extra = f" seed={seed_label}" if seed_label else ""
                    st.markdown(f"**Cycle {i+1}{extra}:** queries = {cy.get('queries', [])}, ingested = {cy.get('ingested_count', 0)}")
            if result_auto.get("reflection_suggestion"):
                with st.expander("LLM reflection suggestion"):
                    st.markdown(result_auto["reflection_suggestion"])
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
        if st.button("Clear result", key="clear_auto_result", disabled=_is_busy()):
            del st.session_state["last_autonomous_result"]
            st.rerun()

# ----- 6. Advanced Features -----
elif step == "6. Advanced Features":
    st.header("6. Advanced Features")
    st.caption("Optional capabilities: local LLM (Ollama), graph visualization, export, advanced autonomous, progress monitoring.")
    config = load_config()
    with st.expander("Dependency check", expanded=True):
        st.caption("Status of optional dependencies. Install or enable as needed for each feature below.")
        ollama_cfg = config.get("llm_ollama") or {}
        ollama_host = ollama_cfg.get("host", "http://127.0.0.1:11434")
        ollama_ok = False
        try:
            import requests as _req
            r = _req.get(ollama_host.rstrip("/") + "/api/tags", timeout=2)
            ollama_ok = r.status_code == 200
        except Exception:
            pass
        st.markdown(f"- **Ollama (local LLM):** {'✅ Available' if ollama_ok else '❌ Not detected'}")
        try:
            import graphviz  # noqa: F401
            gv_ok = True
        except ImportError:
            gv_ok = False
        st.markdown(f"- **Graphviz:** {'✅ Installed' if gv_ok else '❌ Not installed'}")
        try:
            import matplotlib  # noqa: F401
            mpl_ok = True
        except ImportError:
            mpl_ok = False
        st.markdown(f"- **Matplotlib:** {'✅ Installed' if mpl_ok else '❌ Not installed'}")

    with st.expander("Graph visualization"):
        try:
            import graphviz  # noqa: F401
            gv_ok = True
        except ImportError:
            gv_ok = False
        try:
            import matplotlib  # noqa: F401
            mpl_ok = True
        except ImportError:
            mpl_ok = False
        if gv_ok or mpl_ok:
            st.success("Graphviz or Matplotlib available.")
            engine = st.selectbox("Engine", ["graphviz", "matplotlib"], key="viz_engine")
            if engine == "matplotlib" and not mpl_ok:
                st.warning("Matplotlib not installed.")
            else:
                depth = st.number_input("BFS depth", 1, 5, 2, key="viz_depth")
                export_dir = (config.get("export") or {}).get("default_dir", "data/exports")
                os.makedirs(export_dir, exist_ok=True)
                default_path = os.path.join(export_dir, "subgraph.png")
                out_path = st.text_input("Output path", value=default_path, key="viz_path")
                _last = st.session_state.get("last_run_result") or st.session_state.get("last_autonomous_result") or {}
                seed_label = st.text_input("Seed label for export", value=_last.get("seed", "AI"), key="viz_seed", help="Node label to center the subgraph on.")
                st.caption("Output path is relative to project root.")
                if st.button("Export subgraph PNG", key="export_png", disabled=_is_busy()):
                    _set_busy(True)
                    try:
                        _append_log(f"Exporting subgraph PNG (seed={seed_label}, depth={depth}, engine={engine}) to {out_path}...")
                        prog = st.progress(0, text="Exporting subgraph PNG...")
                        with st.status("Exporting subgraph...", expanded=True):
                            try:
                                from goat_ts_cig.knowledge_graph import KnowledgeGraph
                                from goat_ts_cig.graph_viz import export_subgraph_png
                                db_path = (config.get("graph") or {}).get("path", "data/knowledge_graph.db")
                                if (db_path or "").strip() == ":memory:":
                                    st.warning("Database is in-memory (:memory:). Export uses an empty graph. Set a file path in Configuration.")
                                    _append_log("Export subgraph skipped: database is :memory:.")
                                else:
                                    kg = KnowledgeGraph(db_path)
                                    node = kg.get_node_by_label(seed_label.strip())
                                    if not node:
                                        st.error("Seed label not found in graph.")
                                        _append_log(f"Export subgraph failed: seed label '{seed_label}' not found.")
                                    else:
                                        out_resolved = os.path.normpath(os.path.join(ROOT, out_path) if not os.path.isabs(out_path) else out_path)
                                        out_dir = os.path.dirname(out_resolved)
                                        if out_dir:
                                            os.makedirs(out_dir, exist_ok=True)
                                        export_subgraph_png(kg, node["id"], out_resolved, depth=int(depth), engine=engine)
                                        st.success(f"Saved to {out_resolved}")
                                        _append_log(f"Exported subgraph PNG to {out_resolved}")
                                        try:
                                            st.image(out_resolved, caption="Subgraph preview", use_container_width=True)
                                            with open(out_resolved, "rb") as f:
                                                st.download_button(
                                                    "Download PNG",
                                                    data=f.read(),
                                                    file_name=os.path.basename(out_resolved),
                                                    mime="image/png",
                                                    key="download_subgraph_png",
                                                )
                                        except Exception:
                                            # If preview/load fails, the export path is still shown above.
                                            pass
                            except Exception as ex:
                                st.error(str(ex))
                                _append_log(f"Export subgraph PNG failed: {ex}")
                        prog.progress(1.0, text="Done.")
                    finally:
                        _set_busy(False)
        else:
            st.warning("Graphviz and Matplotlib not available.")
        if not gv_ok:
            st.markdown("To enable Graphviz: (1) Install Graphviz binaries from https://graphviz.org  (2) Run: `pip install graphviz`")
            if st.button("Run pip install graphviz", key="install_gv", disabled=_is_busy()):
                _set_busy(True)
                try:
                    _append_log(f"Installing graphviz package (pip install graphviz) (CMD: {sys.executable} -m pip install graphviz, cwd={ROOT}).")
                    prog = st.progress(0, text="Installing graphviz...")
                    with st.status("Installing graphviz package...", expanded=True):
                        r = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "graphviz"],
                            cwd=ROOT,
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=60,
                        )
                        if r.returncode == 0:
                            st.success("Installed. Refresh the app or re-open this step.")
                            _append_log("graphviz package installed.")
                        else:
                            st.code(r.stderr or r.stdout)
                            _append_log("pip install graphviz failed.")
                            _append_log_output((r.stderr or r.stdout or "").strip(), 6)
                    prog.progress(1.0, text="Done.")
                finally:
                    _set_busy(False)

    with st.expander("Local LLM (Ollama)"):
        if ollama_ok:
            st.success("Ollama is available.")
            ollama_cfg = config.get("llm_ollama") or {}
            host_in = st.text_input("Ollama host", value=ollama_cfg.get("host", "http://127.0.0.1:11434"), key="ollama_host")
            model_in = st.text_input("Model name", value=ollama_cfg.get("model", "llama2"), key="ollama_model")
            use_hyp = st.checkbox("Use for hypothesis phrasing", value=ollama_cfg.get("use_for_hypotheses", False), key="ollama_hyp")
            use_auto = st.checkbox("Use for autonomous query expansion", value=ollama_cfg.get("use_for_autonomous", False), key="ollama_auto")
            if st.button("Save LLM settings", key="save_ollama", disabled=_is_busy()):
                _set_busy(True)
                try:
                    _append_log("Saving LLM (Ollama) settings to config...")
                    with st.status("Saving LLM settings...", expanded=True):
                        config = load_config()
                        config["llm_ollama"] = {
                            "enabled": True,
                            "host": host_in.strip() or "http://127.0.0.1:11434",
                            "model": (model_in or "llama2").strip() or "llama2",
                            "use_for_hypotheses": use_hyp,
                            "use_for_autonomous": use_auto,
                        }
                        save_config(config)
                        st.success("Saved.")
                        _append_log("LLM settings saved.")
                finally:
                    _set_busy(False)
                st.rerun()
        else:
            st.warning("Ollama not detected.")
            with st.expander("How to enable Ollama"):
                st.markdown("""
                1. Install Ollama from https://ollama.ai
                2. In a terminal run: `ollama pull llama2` (or another model)
                3. Ensure Ollama is running (it usually starts with the app)
                """)
            if st.button("I've completed these steps", key="ollama_confirm", disabled=_is_busy()):
                st.rerun()

    with st.expander("Export"):
        config = load_config()
        export_dir = (config.get("export") or {}).get("default_dir", "data/exports")
        db_path_export = (config.get("graph") or {}).get("path", "data/knowledge_graph.db")
        if (db_path_export or "").strip() == ":memory:":
            st.warning("Database path is `:memory:`; CSV export will be empty. Set a file path in Configuration for real data.")
        csv_path = st.text_input("CSV output directory", value=export_dir, key="export_csv_dir", help="Nodes and edges written as nodes.csv and edges.csv here.")
        if st.button("Export graph to CSV", key="btn_csv", disabled=_is_busy()):
            _set_busy(True)
            try:
                out_dir = csv_path.strip() or export_dir
                _append_log(f"Exporting graph to CSV in {out_dir}...")
                prog = st.progress(0, text="Exporting graph to CSV...")
                with st.status("Exporting graph (nodes.csv, edges.csv)...", expanded=True):
                    try:
                        from goat_ts_cig.knowledge_graph import KnowledgeGraph
                        from goat_ts_cig.export_utils import export_graph_csv
                        kg = KnowledgeGraph(db_path_export)
                        os.makedirs(out_dir, exist_ok=True)
                        paths = export_graph_csv(kg, out_dir)
                        st.success(f"Exported to {paths[0]} and {paths[1]}")
                        try:
                            st.caption("Preview of nodes.csv (first 10 lines):")
                            with open(paths[0], encoding="utf-8", errors="replace") as f_nodes:
                                head_nodes = "".join(f_nodes.readlines()[:10])
                            st.code(head_nodes or "(empty)", language="text")
                            st.caption("Preview of edges.csv (first 10 lines):")
                            with open(paths[1], encoding="utf-8", errors="replace") as f_edges:
                                head_edges = "".join(f_edges.readlines()[:10])
                            st.code(head_edges or "(empty)", language="text")
                            with open(paths[0], "rb") as f_nodes_bin:
                                st.download_button(
                                    "Download nodes.csv",
                                    data=f_nodes_bin.read(),
                                    file_name=os.path.basename(paths[0]),
                                    mime="text/csv",
                                    key="download_nodes_csv",
                                )
                            with open(paths[1], "rb") as f_edges_bin:
                                st.download_button(
                                    "Download edges.csv",
                                    data=f_edges_bin.read(),
                                    file_name=os.path.basename(paths[1]),
                                    mime="text/csv",
                                    key="download_edges_csv",
                                )
                        except Exception:
                            # If preview fails, the files are still written to disk.
                            pass
                        _append_log(f"Exported graph to CSV: {paths[0]}, {paths[1]}")
                    except Exception as ex:
                        st.error(str(ex))
                        _append_log(f"Export graph to CSV failed: {ex}")
                prog.progress(1.0, text="Done.")
            finally:
                _set_busy(False)
        json_path = st.text_input("JSON output path", value=os.path.join(export_dir, "last_result.json"), key="export_json_path", help="Last pipeline or autonomous result as JSON.")
        if st.button("Export last result to JSON", key="btn_json", disabled=_is_busy()):
            last = st.session_state.get("last_run_result") or st.session_state.get("last_autonomous_result")
            if not last:
                st.warning("No run result in session. Run pipeline or autonomous first.")
            else:
                _set_busy(True)
                try:
                    jpath = json_path.strip() or os.path.join(export_dir, "last_result.json")
                    _append_log(f"Exporting last result to JSON: {jpath}")
                    prog = st.progress(0, text="Exporting result to JSON...")
                    with st.status("Exporting last result...", expanded=True):
                        try:
                            from goat_ts_cig.export_utils import export_cig_json
                            export_cig_json(last, jpath)
                            st.success(f"Saved to {jpath}")
                            try:
                                st.caption("Preview of JSON (first 40 lines):")
                                with open(jpath, encoding="utf-8", errors="replace") as f_json:
                                    lines = f_json.readlines()[:40]
                                st.code("".join(lines) or "(empty)", language="json")
                                with open(jpath, "rb") as f_json_bin:
                                    st.download_button(
                                        "Download JSON",
                                        data=f_json_bin.read(),
                                        file_name=os.path.basename(jpath),
                                        mime="application/json",
                                        key="download_last_json",
                                    )
                            except Exception:
                                pass
                            _append_log(f"Exported last result to {jpath}")
                        except Exception as ex:
                            st.error(str(ex))
                            _append_log(f"Export last result to JSON failed: {ex}")
                    prog.progress(1.0, text="Done.")
                finally:
                    _set_busy(False)

    with st.expander("Advanced autonomous"):
        adv = config.get("advanced_autonomous") or {}
        reflection_default = int(adv.get("reflection_cycles") or 0)
        reflection = st.number_input("Reflection cycles (0–5)", 0, 5, value=min(5, max(0, reflection_default)), key="adv_reflection", help="Extra propagation steps per autonomous cycle.")
        curiosity_default = float((adv.get("curiosity_bias") or 0.0) or 0.0)
        curiosity = st.slider(
            "Curiosity bias (0 = stable, 1 = exploratory)",
            min_value=0.0,
            max_value=1.0,
            value=max(0.0, min(1.0, curiosity_default)),
            step=0.05,
            key="adv_curiosity_bias",
            help="Controls how much autonomous query generation prefers lower-activation / novel nodes.",
        )
        llm_reflection = bool(adv.get("llm_reflection", False))
        llm_reflection = st.checkbox(
            "Use LLM reflection at the end of autonomous run (if Ollama enabled)",
            value=llm_reflection,
            key="adv_llm_reflection",
        )
        multi_seed_list = adv.get("multi_seed") or []
        if not isinstance(multi_seed_list, list):
            multi_seed_list = []
        multi_seed_text = st.text_area("Additional seeds (one per line)", value="\n".join(str(s) for s in multi_seed_list), key="adv_multi_seed", help="Run autonomous for each seed in sequence (shared graph).")
        if st.button("Save advanced autonomous settings", key="save_adv_auto", disabled=_is_busy()):
            _set_busy(True)
            try:
                _append_log("Saving advanced autonomous settings...")
                with st.status("Saving advanced autonomous settings...", expanded=True):
                    config = load_config()
                    config["advanced_autonomous"] = {
                        "reflection_cycles": int(reflection),
                        "curiosity_bias": float(curiosity),
                        "llm_reflection": bool(llm_reflection),
                        "multi_seed": [s.strip() for s in multi_seed_text.splitlines() if s.strip()],
                    }
                    save_config(config)
                    st.success("Saved.")
                    _append_log("Advanced autonomous settings saved.")
            finally:
                _set_busy(False)
            st.rerun()

    with st.expander("Monitoring"):
        mon = config.get("monitoring") or {}
        show_progress = st.checkbox("Show progress during run", value=bool(mon.get("show_progress", False)), key="mon_show_progress", help="Show progress when running pipeline or autonomous.")
        if st.button("Save monitoring settings", key="save_mon", disabled=_is_busy()):
            _set_busy(True)
            try:
                _append_log("Saving monitoring settings (show_progress)...")
                with st.status("Saving monitoring settings...", expanded=True):
                    config = load_config()
                    config["monitoring"] = {"show_progress": show_progress}
                    save_config(config)
                    st.success("Saved.")
                    _append_log("Monitoring settings saved.")
            finally:
                _set_busy(False)
            st.rerun()

    with st.expander("Scaling notes"):
        st.markdown(
            "See `SCALING.md` for detailed strategy. In short:\n\n"
            "- Short-term: batch sync to Rust, optional in-memory caches, and optional node limits for very low RAM.\n"
            "- Medium-term: shard graphs across multiple SQLite files and only run TS on relevant shards.\n"
            "- Long-term: distributed workers owning different shards, coordinated by a lightweight controller.\n\n"
            "This UI currently targets the short-term, single-machine path; future versions may add export hooks for "
            "multi-shard or distributed execution."
        )
