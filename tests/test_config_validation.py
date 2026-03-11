"""Phase 19: Config and .env validation (Steps 83, 85)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_validate_config_exits_zero():
    """validate_config.py exits 0 when config.yaml is valid."""
    root = os.path.join(os.path.dirname(__file__), "..")
    validate_path = os.path.join(root, "validate_config.py")
    assert os.path.isfile(validate_path)
    import subprocess
    r = subprocess.run(
        [sys.executable, validate_path],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert r.returncode == 0, (r.stderr or r.stdout)
    assert "OK" in (r.stdout or "")
