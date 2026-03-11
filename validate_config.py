"""
Phase 19, Step 85: Validate config.yaml and .env integrity.
Run from project root: python validate_config.py
Exits 0 if valid, 1 if errors. Safe defaults are applied in load_config; this script
checks that required structure exists and optional keys have valid types.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "python"))

def main() -> int:
    errors: list[str] = []
    # Load .env into env (optional)
    env_path = os.path.join(ROOT, ".env")
    if os.path.isfile(env_path):
        try:
            for line in open(env_path, encoding="utf-8", errors="replace"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            errors.append(f".env: {e}")

    # Load config.yaml
    config_path = os.path.join(ROOT, "config.yaml")
    if not os.path.isfile(config_path):
        errors.append("config.yaml not found")
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        import yaml
        with open(config_path, encoding="utf-8", errors="replace") as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        errors.append(f"config.yaml: {e}")
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    # Required / expected structure
    if not isinstance(config.get("graph"), dict):
        errors.append("config.graph should be a dict (e.g. graph.path)")
    else:
        path = config["graph"].get("path")
        if path is None or (isinstance(path, str) and path.strip() == ""):
            errors.append("config.graph.path should be set")

    if not isinstance(config.get("wave"), dict):
        errors.append("config.wave should be a dict (ticks, decay, activation_threshold)")
    else:
        for key in ("ticks", "decay", "activation_threshold"):
            if key not in config["wave"]:
                errors.append(f"config.wave.{key} recommended")
            elif key == "ticks" and not isinstance(config["wave"][key], (int, float)):
                errors.append("config.wave.ticks should be a number")

    # Optional keys type checks
    if "llm_ollama" in config and not isinstance(config["llm_ollama"], dict):
        errors.append("config.llm_ollama should be a dict")
    if "advanced_autonomous" in config and not isinstance(config["advanced_autonomous"], dict):
        errors.append("config.advanced_autonomous should be a dict")
    if "advanced_autonomous" in config and isinstance(config["advanced_autonomous"], dict):
        aa = config["advanced_autonomous"]
        if "multi_seed" in aa and not isinstance(aa["multi_seed"], list):
            errors.append("config.advanced_autonomous.multi_seed should be a list")
        if "reflection_cycles" in aa and not isinstance(aa["reflection_cycles"], (int, float)):
            errors.append("config.advanced_autonomous.reflection_cycles should be a number")
        if "curiosity_bias" in aa and not isinstance(aa["curiosity_bias"], (int, float)):
            errors.append("config.advanced_autonomous.curiosity_bias should be a number")

    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        return 1
    print("Config and .env validation OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
