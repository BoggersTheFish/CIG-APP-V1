"""
Benchmark: time propagation / full cycle on N nodes.
Run from project root: python benchmark.py
"""
import os
import sys
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


if __name__ == "__main__":
    bench_full_cycle(500, number=10)
    bench_full_cycle(1000, number=5)
