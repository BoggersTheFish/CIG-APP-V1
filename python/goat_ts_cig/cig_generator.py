"""
CIG Generator: idea maps, context expansion, evidence chains.
"""
import heapq
from collections import deque


def generate_idea_map(kg, seed_id: int, depth: int = 2) -> dict:
    """Extract subgraph around seed (BFS up to depth). Returns {center, related, edges}."""
    center = kg.get_node(seed_id)
    if not center:
        return {"center": None, "related": [], "edges": []}
    center_label = center["label"]
    related = []
    edges = []
    visited = {seed_id}
    queue = deque([(seed_id, 0)])
    while queue:
        nid, d = queue.popleft()
        if d >= depth:
            continue
        for e in kg.get_edges_from(nid):
            to_id = e["to_id"]
            if to_id not in visited:
                visited.add(to_id)
                node = kg.get_node(to_id)
                if node:
                    related.append(
                        {
                            "id": to_id,
                            "label": node["label"],
                            "activation": node.get("activation", 0),
                            "state": node.get("state", ""),
                        }
                    )
                    edges.append(
                        {"from": nid, "to": to_id, "type": e["type"], "weight": e["weight"]}
                    )
                    queue.append((to_id, d + 1))
    return {
        "center": {"id": seed_id, "label": center_label},
        "related": related,
        "edges": edges,
    }


def generate_context_expansion(kg) -> list:
    """Find clusters (connected components) with high activation. Returns list of clusters."""
    data = kg.to_json()
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = data["edges"]
    parent = {nid: nid for nid in nodes}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a, b):
        parent[find(a)] = find(b)

    for e in edges:
        a, b = e["from_id"], e["to_id"]
        if a in parent and b in parent:
            union(a, b)

    clusters = {}
    for nid in nodes:
        root = find(nid)
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(nodes[nid])

    return [
        {
            "nodes": cl,
            "total_activation": sum(n.get("activation", 0) for n in cl),
        }
        for cl in clusters.values()
    ]


def generate_evidence_chain(kg, from_id: int, to_id: int) -> list:
    """Shortest path (by hop count) between two nodes. Returns list of node ids or empty."""
    if from_id == to_id:
        return [from_id]
    data = kg.to_json()
    adj = {}
    for e in data["edges"]:
        a, b = e["from_id"], e["to_id"]
        adj.setdefault(a, []).append((b, e.get("weight", 1.0)))
    dist = {from_id: 0}
    prev = {}
    heap = [(0, from_id)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == to_id:
            path = []
            cur = to_id
            while cur is not None:
                path.append(cur)
                cur = prev.get(cur)
            path.reverse()
            return path
        if d > dist.get(u, float("inf")):
            continue
        for v, w in adj.get(u, []):
            nd = d + 1
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return []


def generate_all(kg, seed_id: int, rg=None, id_map=None, config: dict = None):
    """Run all CIG generators and hypothesis engine. Returns single dict."""
    from goat_ts_cig import hypothesis_engine
    config = config or {}
    out = {
        "idea_map": generate_idea_map(kg, seed_id, depth=2),
        "context_expansion": generate_context_expansion(kg),
        "hypotheses": hypothesis_engine.generate_hypotheses(
            kg, rg=rg, id_map=id_map,
            similarity_threshold=config.get("similarity_threshold", 0.3),
            use_llm=bool(config.get("llm")),
            config=config,
        ),
    }
    return out
