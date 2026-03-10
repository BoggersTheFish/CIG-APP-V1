# Scaling Strategy (CIG-APP / GOAT-TS)

Optional Streamlit UI and Autonomous Exploration (online search) are documented in **PLAN.md** addendum (Steps 43–58).

## Short-term (single machine, low-RAM)

- **Batch sync**: `to_rust_graph(batch_size=5000)` already uses LIMIT/OFFSET for nodes and edges to avoid loading the full graph at once.
- **In-memory caches**: Optional Python-side cache of recent `to_json()` or idea-map results if the same seed is queried repeatedly.
- **Node limit**: For very low RAM, consider a hard limit (e.g. 10k nodes) and either reject new ingest or evict low-activation nodes.

## Medium-term (larger graphs)

- **Multiple SQLite files**: Shard by label prefix or topic; run TS only on the shard containing the seed and its neighborhood (e.g. precompute label→shard index).
- **Rust release build**: Always use `maturin develop --release` and `cargo build --release` for production to maximize throughput.

## Long-term (distributed)

- **Multiple DB files**: Each worker owns one or more SQLite files; a coordinator assigns seeds to workers by shard.
- **Rust actors / async**: Replace single in-process PyGraph with a pool of Rust workers (e.g. via IPC or RPC) that run full_ts_cycle and return updated activations.
- **GPU**: Not required for current design; if needed later, consider roc or similar for parallel propagation on large adjacency matrices.
