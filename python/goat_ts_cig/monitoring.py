"""
Lightweight monitoring metrics for TS runs and graph state.
Used by the Streamlit dashboard and for interoperability exports.
"""
from __future__ import annotations


def collect_metrics(kg, result: dict | None = None) -> dict:
    """
    Collect metrics from the knowledge graph and optional pipeline result.
    Returns dict: node_count, edge_count, activation_mean, activation_max,
    activation_min, top_tension_edges, hypotheses_count, cycles_count.
    """
    data = kg.to_json()
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    activations = [float(n.get("activation") or 0) for n in nodes]
    metrics = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "activation_mean": sum(activations) / len(activations) if activations else 0,
        "activation_max": max(activations) if activations else 0,
        "activation_min": min(activations) if activations else 0,
    }
    node_by_id = {n["id"]: n for n in nodes}
    tension_edges = []
    for e in edges:
        if e.get("type") != "conflict":
            continue
        a, b = node_by_id.get(e["from_id"]), node_by_id.get(e["to_id"])
        if a and b:
            act_a = float(a.get("activation") or 0)
            act_b = float(b.get("activation") or 0)
            tension_edges.append({
                "from_id": e["from_id"],
                "to_id": e["to_id"],
                "from_label": a.get("label", ""),
                "to_label": b.get("label", ""),
                "tension": abs(act_a - act_b),
            })
    tension_edges.sort(key=lambda x: -x["tension"])
    metrics["top_tension_edges"] = tension_edges[:20]
    if result:
        cig = result.get("cig") or {}
        metrics["hypotheses_count"] = len(cig.get("hypotheses") or [])
        metrics["cycles_count"] = len(result.get("cycles") or [])
    else:
        metrics["hypotheses_count"] = 0
        metrics["cycles_count"] = 0
    return metrics
