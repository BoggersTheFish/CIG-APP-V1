"""Integration test: seed -> propagate -> generate -> assert outputs."""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from goat_ts_cig.knowledge_graph import KnowledgeGraph
from goat_ts_cig import cig_generator


def test_full_pipeline_in_process():
    kg = KnowledgeGraph(":memory:")
    kg.ingest_text("alpha beta gamma delta")
    node = kg.get_node_by_label("alpha")
    assert node is not None
    node_id = node["id"]
    kg.update_node_activation(node_id, 1.0)
    rg, id_map = kg.to_rust_graph()
    if rg is not None and id_map:
        seed_rust_id = id_map.index(node_id)
        rg.full_ts_cycle(seed_rust_id, 3, 0.9, 0.5)
        kg.from_rust_graph(rg, id_map)
    out = cig_generator.generate_all(kg, node_id, rg=rg, id_map=id_map)
    assert "idea_map" in out
    assert "context_expansion" in out
    assert "hypotheses" in out
    assert out["idea_map"]["center"]["label"] == "alpha"


def test_cli_json_output():
    root = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        [sys.executable, "run.py", "--seed", "test_cli", "--json"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "seed" in data and data["seed"] == "test_cli"
    assert "cig" in data
    assert "idea_map" in data["cig"]


def test_autonomous_integration_local_only():
    """Integration: run_autonomous_explore with in-memory DB, no network."""
    from goat_ts_cig.autonomous_explore import run_autonomous_explore
    config = {
        "graph": {"path": ":memory:"},
        "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5},
        "online": {"enabled": False, "max_requests_per_run": 30, "timeout_seconds": 10},
    }
    result = run_autonomous_explore("AI", config=config, max_cycles=2, online_override=False)
    assert result.get("seed") == "AI"
    assert "cycles" in result and len(result["cycles"]) == 2
    assert "cig" in result and "graph" in result


def test_export_integration():
    """Integration: pipeline result + export CSV/JSON (as in Advanced Features UI)."""
    import tempfile
    from goat_ts_cig.main import run_pipeline
    from goat_ts_cig.knowledge_graph import KnowledgeGraph
    from goat_ts_cig.export_utils import export_graph_csv, export_cig_json
    result = run_pipeline("export_test", config={"graph": {"path": ":memory:"}, "wave": {"ticks": 2, "decay": 0.9, "activation_threshold": 0.5}})
    assert result.get("error") is None
    with tempfile.TemporaryDirectory() as d:
        kg = KnowledgeGraph(":memory:")
        kg.add_node("a")
        kg.add_node("b")
        kg.add_edge(1, 2, "relates", 1.0)
        paths = export_graph_csv(kg, d)
        assert len(paths) == 2 and all(os.path.isfile(p) for p in paths)
        json_path = os.path.join(d, "out.json")
        export_cig_json(result, json_path)
        assert os.path.isfile(json_path)
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("seed") == "export_test"
