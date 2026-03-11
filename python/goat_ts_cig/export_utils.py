"""Export graph to CSV and CIG result to JSON."""
from __future__ import annotations

import csv
import json
import os


def export_graph_csv(kg, dir_path: str) -> list[str]:
    """Write nodes and edges to nodes.csv and edges.csv in dir_path. Returns [nodes_path, edges_path]."""
    os.makedirs(dir_path, exist_ok=True)
    data = kg.to_json()
    nodes_path = os.path.join(dir_path, "nodes.csv")
    edges_path = os.path.join(dir_path, "edges.csv")
    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "label", "mass", "activation", "state", "metadata"])
        for n in data["nodes"]:
            w.writerow([
                n.get("id"),
                n.get("label", ""),
                n.get("mass", 1.0),
                n.get("activation", 0),
                n.get("state", ""),
                n.get("metadata", ""),
            ])
    with open(edges_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from_id", "to_id", "type", "weight"])
        for e in data["edges"]:
            w.writerow([
                e.get("from_id"),
                e.get("to_id"),
                e.get("type", "relates"),
                e.get("weight", 1.0),
            ])
    return [nodes_path, edges_path]


def export_cig_json(result_dict: dict, path: str) -> str:
    """Write run_pipeline/autonomous result dict to JSON file. Returns path."""
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, indent=2)
    return path
