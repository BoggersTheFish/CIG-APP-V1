import argparse
import json
import logging
import os
import pprint
import yaml

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig import cig_generator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def _apply_vector_boost(kg: KnowledgeGraph, config: dict) -> None:
    """
    For nodes with stored vectors, add alpha * sim(C_i, C_j) * A_j from top-K similar nodes.
    Config: vector.enabled, vector.alpha, vector.similarity_top_k, vector.similarity_threshold.
    """
    vec_cfg = config.get("vector") or {}
    if not vec_cfg.get("enabled") or not hasattr(kg, "get_embedding"):
        return
    alpha = float(vec_cfg.get("alpha", 0.1))
    if alpha <= 0:
        return
    top_k = int(vec_cfg.get("similarity_top_k", 5))
    sim_threshold = float(vec_cfg.get("similarity_threshold", 0.0))
    try:
        cur = kg.conn.execute("SELECT id FROM vectors")
        node_ids_with_vec = [r[0] for r in cur.fetchall()]
    except Exception:
        return
    if not node_ids_with_vec:
        return
    boosts = {}
    for nid in node_ids_with_vec:
        emb = kg.get_embedding(nid)
        if not emb or len(emb) != 384:
            continue
        similar = kg.query_similar_vectors(emb, limit=top_k + 1)
        boost = 0.0
        for other_id, dist in similar:
            if other_id == nid:
                continue
            sim = 1.0 / (1.0 + float(dist)) if float(dist) >= 0 else 1.0
            if sim < sim_threshold:
                continue
            other = kg.get_node(other_id)
            act_j = (other or {}).get("activation") or 0.0
            boost += alpha * sim * act_j
        boosts[nid] = boost
    for nid, boost in boosts.items():
        if boost <= 0:
            continue
        node = kg.get_node(nid)
        current = (node or {}).get("activation") or 0.0
        kg.update_node_activation(nid, current + boost)


def run_pipeline(
    seed: str,
    config_path: str | None = None,
    ingest_text: str | None = None,
    ticks_override: int | None = None,
    config_overrides: dict | None = None,
    kg=None,
    config: dict | None = None,
    progress_callback=None,
):
    """
    Run the full CIG pipeline and return results for UI/API.
    If kg is provided, use it (for autonomous loop); otherwise create from config graph.path.
    If config is provided, use it instead of loading from file.
    Returns: dict with seed, node_id, cig, graph, config, rust_used, error (if any).
    """
    if config is None:
        if config_path is None:
            config_path = "config.yaml"
        if not os.path.isfile(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            return {"error": f"Failed to load config: {e}", "config": {}}
    if config_overrides:
        for k, v in config_overrides.items():
            if "." in k:
                section, key = k.split(".", 1)
                config.setdefault(section, {})[key] = v
            else:
                config[k] = v
    if ticks_override is not None:
        config.setdefault("wave", {})["ticks"] = ticks_override
    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    if kg is None:
        try:
            kg = KnowledgeGraph(db_path)
        except Exception as e:
            return {"error": f"Failed to open graph at {db_path}: {e}", "config": config}
    limits = config.get("resource_limits") or {}
    max_nodes = limits.get("max_nodes")
    if max_nodes is not None and isinstance(max_nodes, (int, float)):
        data = kg.to_json()
        n_nodes = len(data.get("nodes", []))
        if n_nodes > int(max_nodes):
            return {"error": f"Graph has {n_nodes} nodes; resource_limits.max_nodes is {max_nodes}. Increase the limit or use a smaller graph.", "config": config}
    if ingest_text:
        kg.ingest_text(ingest_text)
    existing = kg.get_node_by_label(seed)
    if existing:
        node_id = existing["id"]
        kg.update_node_activation(node_id, 1.0)
    else:
        node_id = kg.add_node(seed, activation=1.0)
    rg, id_map = kg.to_rust_graph()
    rust_used = rg is not None and len(id_map) > 0
    wave = config.get("wave", {})
    ticks = wave.get("ticks", 10)
    max_ticks_cap = (limits.get("max_ticks_per_run") or 0) or 999999
    if isinstance(max_ticks_cap, (int, float)):
        ticks = min(ticks, int(max_ticks_cap))
    if progress_callback:
        progress_callback(0, ticks, "starting")
    if rust_used:
        try:
            seed_rust_id = id_map.index(node_id)
        except ValueError:
            seed_rust_id = 0
        decay = wave.get("decay", 0.9)
        threshold = wave.get("activation_threshold", 0.5)
        activation_fn = wave.get("activation_fn", "linear")
        use_frontier = wave.get("use_frontier", False)
        use_convergence = wave.get("use_convergence", False)
        max_ticks = wave.get("max_ticks", 100)
        epsilon = wave.get("epsilon", 1e-5)
        rg.full_ts_cycle(
            seed_rust_id, ticks, decay, threshold,
            activation_fn=activation_fn,
            use_frontier=use_frontier,
            use_convergence=use_convergence,
            max_ticks=max_ticks,
            epsilon=epsilon,
        )
        kg.from_rust_graph(rg, id_map)
        # Vector-augmented activation: add alpha * sim * A_j from similar nodes (when enabled)
        _apply_vector_boost(kg, config)
    if progress_callback:
        progress_callback(ticks, ticks, "done")
    try:
        cig_out = cig_generator.generate_all(kg, node_id, rg=rg, id_map=id_map, config=config)
    except Exception as e:
        return {"error": f"CIG generation failed: {e}", "seed": seed, "node_id": node_id, "config": config}
    return {
        "seed": seed,
        "node_id": node_id,
        "cig": cig_out,
        "graph": kg.to_json(),
        "config": config,
        "rust_used": rust_used,
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser(description="GOAT-TS CIG")
    parser.add_argument("--seed", required=True, help="Seed concept for exploration")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--ticks", type=int, help="Override wave ticks from config")
    parser.add_argument("--ingest-file", type=str, help="Ingest text from file")
    args = parser.parse_args()

    config_path = "config.yaml"
    if not os.path.isfile(config_path):
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.ticks is not None:
        config.setdefault("wave", {})["ticks"] = args.ticks

    db_path = config.get("graph", {}).get("path", "data/knowledge_graph.db")
    try:
        kg = KnowledgeGraph(db_path)
    except Exception as e:
        log.exception("Failed to open knowledge graph at %s: %s", db_path, e)
        raise
    if args.ingest_file and os.path.isfile(args.ingest_file):
        with open(args.ingest_file, encoding="utf-8") as f:
            kg.ingest_text(f.read())

    existing = kg.get_node_by_label(args.seed)
    if existing:
        node_id = existing["id"]
        kg.update_node_activation(node_id, 1.0)
    else:
        node_id = kg.add_node(args.seed, activation=1.0)

    # TS propagation via Rust (if available)
    rg, id_map = kg.to_rust_graph()
    if rg is not None and id_map:
        log.info("Running TS propagation (Rust)")
        try:
            seed_rust_id = id_map.index(node_id)
        except ValueError:
            seed_rust_id = 0
        wave = config.get("wave", {})
        ticks = wave.get("ticks", 10)
        decay = wave.get("decay", 0.9)
        threshold = wave.get("activation_threshold", 0.5)
        rg.full_ts_cycle(
            seed_rust_id, ticks, decay, threshold,
            activation_fn=wave.get("activation_fn", "linear"),
            use_frontier=wave.get("use_frontier", False),
            use_convergence=wave.get("use_convergence", False),
            max_ticks=wave.get("max_ticks", 100),
            epsilon=wave.get("epsilon", 1e-5),
        )
        kg.from_rust_graph(rg, id_map)
        _apply_vector_boost(kg, config)
    else:
        log.info("Rust extension not used; skipping propagation")

    # CIG outputs
    cig_out = cig_generator.generate_all(kg, node_id, rg=rg, id_map=id_map, config=config)

    if args.json:
        out = {"seed": args.seed, "node_id": node_id, "cig": cig_out, "graph": kg.to_json()}
        print(json.dumps(out, indent=2))
    else:
        print(f"Seed: {args.seed} (NodeId: {node_id})")
        print("--- Idea map ---")
        pprint.pprint(cig_out["idea_map"])
        print("--- Context expansion (clusters) ---")
        pprint.pprint(cig_out["context_expansion"])
        print("--- Hypotheses ---")
        pprint.pprint(cig_out["hypotheses"])


if __name__ == "__main__":
    main()
