# UI Polish & Next-Phase Enhancements (Phases 9–12)

**Repository**: [CIG-APP-V1](https://github.com/BoggersTheFish/CIG-APP-V1)  
**Context**: Most mature public iteration of GOAT-TS / CIG as of March 2026. This addendum continues from earlier plan steps (43+) and focuses on **UI polish** and **next-phase capabilities**.

**Rule**: Every new feature/mode must have a dedicated UI control. New dependencies must either be auto-installed (with user confirmation) or have step-by-step guided instructions + confirmation before enabling.

---

## Phase 9: UI Polish & Dependency Management (Steps 43–50)

| Step | Objective | Outcome |
|------|-----------|---------|
| **43** | Sidebar feature toggles & dependency status indicators | Users see at a glance what is installed/missing (Ollama, Graphviz, NetworkX, Matplotlib, BeautifulSoup). |
| **44** | One-click install buttons for missing pip packages | Reduces friction; Graphviz binary still guided via https://graphviz.org/download/ |
| **45** | Theme toggle (light/dark) & layout improvements | Better accessibility; note: full theme change may require app restart. |
| **46** | Real-time progress & logging for autonomous/long runs | `st.status` or log area with cycle-by-cycle updates. |

---

## Phase 10: Visualization & Export Enhancements (Steps 51–56)

| Step | Objective | Outcome |
|------|-----------|---------|
| **51** | "Visualize Current Graph" button with preview | Export small subgraph (top activated nodes) to PNG, show in UI via `st.image`. |
| **52** | Export preview & format selector | Dropdown: JSON / CSV / Graphviz DOT / PNG; "Preview Export" + "Download" with `st.download_button`. |

---

## Phase 11: Advanced Autonomous & Reflection (Steps 57–62)

| Step | Objective | Outcome |
|------|-----------|---------|
| **57** | Sliders/toggles for autonomous behavior | Max cycles (1–20), Reflection depth (None/Light/Deep), Curiosity bias (0–1), Max search requests. |
| **58** | Optional reflection cycle using Ollama | After N cycles, prompt local LLM for gaps / next seed; UI toggle "Enable Reflection" + model selector. |

---

## Phase 12: Monitoring Dashboard & Scaling Prep (Steps 63–68)

| Step | Objective | Outcome |
|------|-----------|---------|
| **63** | Simple dashboard tab | Activation distribution, top nodes, convergence plot (e.g. matplotlib in Streamlit). |
| **64** | Document scaling notes in UI | Expander with summary + link to `SCALING.md`; "Export for distributed run" stub. |

---

## Recommended Implementation Order

1. **Dependency install buttons & status indicators** (Steps 43–44) — huge UX win.  
2. **Real-time progress/logging** (Step 46).  
3. **Visualization preview** (Step 51).  
4. **Advanced autonomous sliders** (Step 57).  
5. **Reflection with Ollama** (Step 58).

---

## Current State (as of March 2026)

- **Core**: Hybrid Python + Rust, local-first, SQLite + TS propagation, low-end hardware.
- **UI**: Setup, Configuration, Run & Explore, Optional Tools, Autonomous Exploration, Advanced Features.
- **Advanced Features**: Ollama, graph viz (PNG), CSV/JSON export, progress monitoring, reflection cycles, multi-seed.
- **Gaps**: Centralized dependency status in sidebar, one-click pip installs, theme toggle, live progress for autonomous, export preview, reflection depth/curiosity sliders, monitoring dashboard.
