# TS (Thinking System) Propagation Model

This document describes the propagation equations, state transitions, and configuration knobs used in CIG-APP-V1 and how they relate to the GOAT-TS vision.

## 1. Activation Update

The core update per tick is:

- **Incoming**: For each node \(i\), sum contributions from neighbors \(j\) that point to \(i\):
  \[
  \mathit{incoming}_i = \sum_{j \to i} A_j(t) \cdot W_{ji} \cdot \lambda
  \]
  where \(A_j(t)\) is the activation of node \(j\), \(W_{ji}\) is the edge weight, and \(\lambda\) is the decay factor.

- **New activation**: The implementation uses this as the new activation (optionally passed through a non-linear function):
  \[
  A_i(t+1) = f(\mathit{incoming}_i)
  \]
  with \(f\) one of: **linear** (identity), **tanh**, or **capped** (clamp to \([0, 1]\)).

- **Decay**: After propagation, all activations are multiplied by \(\lambda\):
  \[
  A_i \leftarrow A_i \cdot \lambda
  \]

Parameters (from `config.yaml` → `wave`):

| Parameter | Key | Effect |
|-----------|-----|--------|
| Ticks | `ticks` | Number of propagation steps per run. |
| Decay | `decay` | \(\lambda\); applied each tick (e.g. 0.9). |
| Activation threshold | `activation_threshold` | Used for state labels and (when `use_frontier`) to define the active frontier. |
| Activation function | `activation_fn` | `linear`, `tanh`, or `capped`. |
| Frontier mode | `use_frontier` | If true, only nodes with \(A_i \geq\) threshold push to neighbors (reduces work on large graphs). |
| Convergence mode | `use_convergence` | If true, run until \(\|A(t+1) - A(t)\| < \varepsilon\) or `max_ticks`. |
| Epsilon | `epsilon` | Convergence threshold when `use_convergence` is true. |

## 2. State Transitions

After each tick, node state is set from activation:

| Condition | State |
|-----------|--------|
| \(A_i < 0.1\) | DORMANT |
| \(A_i \geq\) `activation_threshold` | ACTIVE |
| Otherwise | DEEP |

These are written back to the graph and used for display and filtering.

## 3. Constraint Resolution

After propagation and before decay, **conflict** edges are resolved: for each conflict edge between nodes \(i\) and \(j\), both activations are damped toward their average (e.g. 80% of average), so conflicting concepts pull each other down.

## 4. Vector-Augmented Activation (Hybrid)

When `vector.enabled` and `vector.alpha > 0`, a **post-cycle** step in Python adds a boost from similar nodes (by embedding):

\[
A_i \leftarrow A_i + \alpha \sum_{j \in \mathrm{top}\text{-}K(i)} \mathrm{sim}(C_i, C_j) \cdot A_j
\]

- \(C_i\) is the embedding of node \(i\) (384-d, from sentence-transformers).
- \(\mathrm{sim}\) is derived from sqlite-vss distance (e.g. \(1/(1+\mathrm{dist})\)).
- Config: `vector.alpha`, `vector.similarity_top_k`, `vector.similarity_threshold`.

This is applied once after the Rust TS cycle and sync back; it does not run inside the tick loop.

## 5. How Hybrid Graph–Vector Fits

- **Graph**: Edges and weights drive the standard propagation.
- **Vectors**: Used for (1) hypothesis suggestions (similar nodes without edges) and (2) the optional vector boost above.
- See **ARCHITECTURE.md** for the split between GOAT-TS (NebulaGraph/Spark) and CIG-APP-V1 (SQLite + Rust + optional sqlite-vss).
