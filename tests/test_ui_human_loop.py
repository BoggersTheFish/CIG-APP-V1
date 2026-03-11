"""Tests for human-in-loop autonomous (Step 5)."""
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))


def test_run_autonomous_one_cycle_exists():
    from goat_ts_cig.autonomous_explore import run_autonomous_one_cycle
    assert callable(run_autonomous_one_cycle)


def test_run_autonomous_one_cycle_returns_tuple():
    import yaml
    from goat_ts_cig.autonomous_explore import run_autonomous_one_cycle
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as dbf:
        db_path = dbf.name
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        config_path = f.name
        f.write(yaml.dump({
            "graph": {"path": db_path},
            "wave": {"ticks": 2, "decay": 0.9},
            "online": {"enabled": False},
        }).encode())
    try:
        config = {"graph": {"path": db_path}, "wave": {"ticks": 2}, "online": {"enabled": False}}
        result, total_req, cycles_log = run_autonomous_one_cycle(
            config_path, config, "AI", 0, 2, False, 30, 10, 0, [], 0,
        )
        assert isinstance(result, dict)
        assert isinstance(total_req, int)
        assert isinstance(cycles_log, list)
        assert len(cycles_log) >= 1
    finally:
        if os.path.isfile(config_path):
            try:
                os.remove(config_path)
            except OSError:
                pass
        if os.path.isfile(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass
