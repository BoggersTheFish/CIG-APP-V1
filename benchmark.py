"""
Benchmark: time propagation / full cycle on N nodes.
Phase 19: optional pipeline and export timings.
CLI: python benchmark.py [--nodes 500] [--ticks 10] [--runs 5] [--frontier] [--pipeline] [--export]
"""
import argparse
import os
import sys
import time
import timeit

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph


def bench_full_cycle(n_nodes: int = 500, ticks: int = 10, number: int = 5, use_frontier: bool = False):
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
        rg.full_ts_cycle(0, ticks, 0.9, 0.5, activation_fn="linear", use_frontier=use_frontier, use_convergence=False, max_ticks=100, epsilon=1e-5)
    t = timeit.timeit(run, number=number)
    print(f"Nodes: {n_nodes}, Ticks: {ticks}, Frontier: {use_frontier}, Runs: {number}")
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


def main():
    p = argparse.ArgumentParser(description="CIG-APP benchmarks")
    p.add_argument("--nodes", type=int, default=500, help="Graph size for propagation benchmark")
    p.add_argument("--ticks", type=int, default=10, help="Ticks per run")
    p.add_argument("--runs", type=int, default=5, help="Number of runs to average")
    p.add_argument("--frontier", action="store_true", help="Use frontier-based propagation")
    p.add_argument("--pipeline", action="store_true", help="Also run pipeline benchmark")
    p.add_argument("--export", action="store_true", help="Also run export benchmark")
    args = p.parse_args()
    print("=== Propagation ===")
    bench_full_cycle(args.nodes, args.ticks, args.runs, use_frontier=args.frontier)
    if args.pipeline:
        print("=== Pipeline ===")
        bench_pipeline_once()
    if args.export:
        print("=== Export CSV ===")
        bench_export_csv(min(args.nodes, 500))


if __name__ == "__main__":
    main()
