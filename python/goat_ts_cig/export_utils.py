"""Export graph to CSV, GraphML, and CIG result to JSON. Phases 15-16, Steps 68-74."""
from __future__ import annotations

import csv
import json
import os


def to_graphml(kg, path: str) -> str:
    """Export knowledge graph to GraphML via networkx. Returns output path."""
    import networkx as nx
    data = kg.to_json()
    G = nx.Graph()
    for n in data.get("nodes", []):
        G.add_node(
            n["id"],
            label=n.get("label", ""),
            mass=float(n.get("mass", 1.0)),
            activation=float(n.get("activation", 0)),
            state=n.get("state", ""),
        )
    for e in data.get("edges", []):
        G.add_edge(e["from_id"], e["to_id"], type=e.get("type", "relates"), weight=float(e.get("weight", 1.0)))
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    nx.write_graphml(G, path)
    return path


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


def to_rdf(kg, path: str, format: str = "turtle") -> str:
    """
    Export knowledge graph to RDF (Turtle or N-Triples).
    format: "turtle" | "nt". External tools (e.g. Neo4j with RDF plugin) can import the result.
    """
    data = kg.to_json()
    base = "http://cig.example.org/"
    lines = []
    if format == "turtle":
        lines.append("@prefix cig: <" + base + "> .")
        lines.append("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
        lines.append("")
    for n in data.get("nodes", []):
        nid = n.get("id")
        label = (n.get("label") or "").replace("\\", "\\\\").replace('"', '\\"')
        act = float(n.get("activation") or 0)
        state = (n.get("state") or "").replace("\\", "\\\\").replace('"', '\\"')
        if format == "turtle":
            lines.append(f"<{base}node/{nid}> rdf:type cig:Node ;")
            lines.append(f'  cig:label "{label}" ;')
            lines.append(f"  cig:activation {act} ;")
            lines.append(f'  cig:state "{state}" .')
        else:
            lines.append(f"<{base}node/{nid}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <{base}Node> .")
            lines.append(f'<{base}node/{nid}> <{base}label> "{label}" .')
            lines.append(f"<{base}node/{nid}> <{base}activation> \"{act}\"^^<http://www.w3.org/2001/XMLSchema#double> .")
    for e in data.get("edges", []):
        fr, to = e.get("from_id"), e.get("to_id")
        if format == "turtle":
            lines.append(f"<{base}node/{fr}> cig:relates <{base}node/{to}> .")
        else:
            lines.append(f"<{base}node/{fr}> <{base}relates> <{base}node/{to}> .")
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def to_neo4j_cypher(kg, path: str) -> str:
    """
    Export graph as Cypher CREATE statements for Neo4j import.
    Run the output file in Neo4j browser or via cypher-shell.
    """
    data = kg.to_json()
    lines = ["// CIG-APP export for Neo4j", "// Create nodes then relationships.", ""]
    for n in data.get("nodes", []):
        nid = n.get("id")
        label = (n.get("label") or "").replace("\\", "\\\\").replace("'", "\\'")
        act = float(n.get("activation") or 0)
        state = (n.get("state") or "").replace("'", "\\'")
        lines.append(f"CREATE (n{nid}:Node {{id: {nid}, label: '{label}', activation: {act}, state: '{state}'}});")
    lines.append("")
    for e in data.get("edges", []):
        fr, to = e.get("from_id"), e.get("to_id")
        typ = (e.get("type") or "relates").replace("'", "\\'")
        w = float(e.get("weight") or 1.0)
        rel = "RELATES" if typ == "relates" else typ.upper().replace(" ", "_")
        lines.append(f"MATCH (a:Node {{id: {fr}}}), (b:Node {{id: {to}}}) CREATE (a)-[:{rel} {{weight: {w}}}]->(b);")
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
