"""
Benchmark: time propagation / full cycle on N nodes.
Phase 19: optional pipeline and export timings.
Run from project root: python benchmark.py
"""
import os
import sys
import time
import timeit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph


def bench_full_cycle(n_nodes: int = 500, ticks: int = 10, number: int = 5):
    kg = KnowledgeGraph(":memory:")
    for i in range(n_nodes):
        kg.add_node(f"node_{i}")
    for i in range(n_nodes - 1):
        kg.add_edge(i + 1, i + 2, "relates", 1.0)
    rg, id_map = kg.to_rust_graph()
    if rg is None:
        print("Rust extension not built; skipping benchmark.")
        return
    def run():
        rg.full_ts_cycle(0, ticks=ticks, decay=0.9, activation_threshold=0.5)
    t = timeit.timeit(run, number=number)
    print(f"Nodes: {n_nodes}, Ticks: {ticks}, Runs: {number}")
    print(f"Total: {t:.3f}s, Per run: {t/number:.3f}s")


def bench_pipeline_once():
    """Time a single run_pipeline call (seed, small graph)."""
    try:
        from goat_ts_cig.main import run_pipeline
        config = {"graph": {"path": ":memory:"}, "wave": {"ticks": 5, "decay": 0.9, "activation_threshold": 0.5}}
        start = time.perf_counter()
        result = run_pipeline("bench", config=config)
        elapsed = time.perf_counter() - start
        if result.get("error"):
            print("Pipeline benchmark: run failed:", result.get("error"))
        else:
            print(f"Pipeline (in-memory, 5 ticks): {elapsed:.3f}s")
    except Exception as e:
        print("Pipeline benchmark skipped:", e)


def bench_export_csv(n_nodes: int = 200):
    """Time export_graph_csv on a small graph."""
    try:
        from goat_ts_cig.export_utils import export_graph_csv
        import tempfile
        kg = KnowledgeGraph(":memory:")
        for i in range(n_nodes):
            kg.add_node(f"n_{i}")
        for i in range(n_nodes - 1):
            kg.add_edge(i + 1, i + 2, "relates", 1.0)
        with tempfile.TemporaryDirectory() as d:
            start = time.perf_counter()
            export_graph_csv(kg, d)
            elapsed = time.perf_counter() - start
        print(f"Export CSV ({n_nodes} nodes): {elapsed:.3f}s")
    except Exception as e:
        print("Export CSV benchmark skipped:", e)


if __name__ == "__main__":
    bench_full_cycle(500, number=10)
    bench_full_cycle(1000, number=5)
    bench_pipeline_once()
    bench_export_csv(200)
