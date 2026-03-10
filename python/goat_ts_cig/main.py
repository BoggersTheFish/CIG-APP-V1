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


def run_pipeline(
    seed: str,
    config_path: str | None = None,
    ingest_text: str | None = None,
    ticks_override: int | None = None,
    config_overrides: dict | None = None,
    kg=None,
    config: dict | None = None,
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
    if rust_used:
        try:
            seed_rust_id = id_map.index(node_id)
        except ValueError:
            seed_rust_id = 0
        ticks = config.get("wave", {}).get("ticks", 10)
        decay = config.get("wave", {}).get("decay", 0.9)
        threshold = config.get("wave", {}).get("activation_threshold", 0.5)
        rg.full_ts_cycle(seed_rust_id, ticks, decay, threshold)
        kg.from_rust_graph(rg, id_map)
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
        ticks = config.get("wave", {}).get("ticks", 10)
        decay = config.get("wave", {}).get("decay", 0.9)
        threshold = config.get("wave", {}).get("activation_threshold", 0.5)
        rg.full_ts_cycle(seed_rust_id, ticks, decay, threshold)
        kg.from_rust_graph(rg, id_map)
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
