# Optimization Notes (CIG-APP / GOAT-TS)

## Low-end tips

- **Embeddings**: Use the mini model (`all-MiniLM-L6-v2`) to keep RAM under ~100MB; disable embeddings if memory is tight.
- **Vector search**: sqlite-vss adds modest overhead; keep vector table small or disable on very low-RAM machines.
- **PDF ingest**: Limit page count or file size in config to avoid long blocks; extract in chunks if needed.
- **UI**: Disable optional sidebar installs and heavy visualizations on low-end; use CLI for batch runs.

## Embeddings RAM

Embeddings: <100MB with mini model (`all-MiniLM-L6-v2`). First load downloads the model; subsequent runs use cache. Disable `advanced.embeddings.enabled` on low-RAM machines.

## Vector query time

sqlite-vss KNN query time grows with index size; for <10k vectors expect <100ms per query on typical hardware. Disable `vector.enabled` if hypothesis step feels slow.

## PDF ingest limits

Large PDFs can block the UI; prefer smaller documents or run ingest in a separate batch. `ingestion.pdf_enabled` can be set to `false` to hide the PDF uploader. No hard page limit is enforced; consider chunking very large files.

- **Rust wave engine**: Propagation uses a single-tick copy-update to avoid read/write conflicts. For graphs with ≥100 nodes, `rayon` parallelizes the per-node activation update (incoming sum).
- **Convergence**: `propagate_until_convergence` in `wave_engine.rs` stops when activation delta < epsilon (not wired in default full_ts_cycle; can be enabled for early exit).
- **Memory**: Python KG sync uses batched SQLite reads (default batch 5000) in `to_rust_graph` to limit peak RAM. Rust structs use `u32`/`f64`; switching to `u16`/`f32` would reduce footprint for very large graphs but requires binding and Python sync changes.
- **Profiling**: Use `cargo build --release` and `maturin develop --release` for production. Python: `python -m cProfile -s cumtime run.py --seed x` to find hot paths.
- **Target**: Aim for <1s full cycle on 1000 nodes on low-end hardware (e.g. Intel Pentium Silver).
