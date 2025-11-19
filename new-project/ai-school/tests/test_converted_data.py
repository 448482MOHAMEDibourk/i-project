import json
from pathlib import Path

DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "lessons"
    / "imported-from-failed"
    / "lesson-planner"
    / "data"
    / "converted"
)


def test_converted_files_exist_and_parse():
    assert DATA_DIR.exists(), f"Converted data dir not found: {DATA_DIR}"
    files = list(DATA_DIR.glob("*.json"))
    assert files, f"No converted JSON files found in {DATA_DIR}"

    # Pick a few files to sanity-check parseability and basic structure
    sample = files[:3]
    for p in sample:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # Expect top-level to be a list or dict
        assert isinstance(data, (list, dict)), f"Unexpected JSON top-level type in {p}"
        # If list, expect elements to be dicts with at least one key
        if isinstance(data, list) and data:
            assert isinstance(data[0], dict), f"Expected list of objects in {p}"
            assert data[0], f"First object in {p} is empty"
