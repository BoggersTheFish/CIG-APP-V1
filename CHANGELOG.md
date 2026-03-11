# Changelog

## v1.0-alpha (March 11, 2026)

### Release
- MIT license & docs completion
- UI polish: sidebar deps/installs, theme toggle, previews, dashboard
- Autonomous: human-in-loop, reflection, curiosity bias, request slider, cooldown
- Embeddings (mini), sqlite-vss vector search
- PDF ingestion (PyPDF2), GraphML export
- Undo/backup, expanded tests, perf notes

### Later updates
- **Pipeline run feedback**: Non-autonomous pipeline runs in a background thread; UI shows “Running pipeline… (N s)” and refreshes every second until done.
- **Streamlit fixes**: Removed conflicting `st.session_state` writes after widgets (run_seed, run_autonomous_mode, run_override_ticks) to fix `StreamlitAPIException`.
- **Developer mode**: In **1. Setup**, checkbox “Developer mode (show debug menus in all tabs)” enables **Debug** expanders in every step (session state, config, last result, pipeline/autonomous state, etc.) for easier debugging.
