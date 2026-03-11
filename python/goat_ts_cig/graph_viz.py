"""Export subgraph as PNG (graphviz or matplotlib)."""
from __future__ import annotations

import os
from collections import deque


def export_subgraph_png(
    kg,
    seed_id: int,
    output_path: str,
    depth: int = 2,
    engine: str = "graphviz",
) -> str:
    """Build subgraph via BFS from seed; render to PNG. Returns path to file."""
    nodes_set = {seed_id}
    queue = deque([(seed_id, 0)])
    while queue:
        nid, d = queue.popleft()
        if d >= depth:
            continue
        for e in kg.get_edges_from(nid):
            to_id = e["to_id"]
            if to_id not in nodes_set:
                nodes_set.add(to_id)
                queue.append((to_id, d + 1))
    edges = []
    for nid in nodes_set:
        for e in kg.get_edges_from(nid):
            if e["to_id"] in nodes_set:
                edges.append((nid, e["to_id"]))

    if engine == "graphviz":
        import graphviz
        g = graphviz.Digraph()
        for nid in nodes_set:
            node = kg.get_node(nid)
            label = (node.get("label") or str(nid))[:20] if node else str(nid)
            g.node(str(nid), label=label)
        for a, b in edges:
            g.edge(str(a), str(b))
        base = output_path if not output_path.endswith(".png") else output_path[:-4]
        g.render(format="png", outfile=base, cleanup=True)
        return base + ".png"
    else:
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("matplotlib engine requires: pip install networkx matplotlib")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        G = nx.DiGraph()
        G.add_nodes_from(nodes_set)
        G.add_edges_from(edges)
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color="lightblue")
        plt.savefig(output_path)
        plt.close()
        return output_path
