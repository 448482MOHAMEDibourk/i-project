import json
from pathlib import Path
from typing import Any, Dict

BASE = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    BASE
    / "lessons"
    / "imported-from-failed"
    / "lesson-planner"
    / "data"
    / "config.json"
)


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolved_data_root() -> Path:
    cfg = load_config()
    data_root = cfg.get("data_root", ".")
    return (CONFIG_PATH.parent / data_root).resolve()


def resolved_path_for(key: str) -> Path:
    """Resolve a path for a top-level key inside config (e.g. subjects.arabic.programs_dir)

    This is a small helper used by the app to find important directories.
    """
    cfg = load_config()
    parts = key.split(".")
    node = cfg
    for p in parts:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            raise KeyError(f"Config key not found: {key}")
    if not isinstance(node, str):
        raise ValueError(f"Config key {key} did not resolve to a path string: {node}")
    return (CONFIG_PATH.parent / node).resolve()
