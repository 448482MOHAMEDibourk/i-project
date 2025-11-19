import json

from lesson_data.loader import load_config, resolved_data_root


def test_load_config_and_resolve_paths():
    cfg = load_config()
    assert "version" in cfg
    root = resolved_data_root()
    # The converted folder should exist relative to config
    converted = root / "converted"
    assert converted.exists(), (
        f"Converted folder not found under resolved data root: {converted}"
    )
    files = list(converted.glob("*.json"))
    assert files, "No converted json files found by loader"
    # Try loading one file
    with files[0].open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, (list, dict))
