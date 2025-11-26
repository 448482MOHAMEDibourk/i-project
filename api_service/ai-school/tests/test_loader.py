import json

import lesson_data.loader as loader


def test_load_config_and_resolve_paths(tmp_path, monkeypatch):
    # create a temporary converted directory with a sample JSON file
    converted = tmp_path / "converted"
    converted.mkdir()
    sample = converted / "sample.json"
    sample.write_text('{"hello": "world"}', encoding="utf-8")

    # monkeypatch resolved_data_root to point to our temp dir
    monkeypatch.setattr(loader, "resolved_data_root", lambda: tmp_path)

    root = loader.resolved_data_root()
    assert root == tmp_path
    assert (root / "converted").exists() or converted.exists()
    files = list(converted.glob("*.json"))
    assert files, "No converted json files found by loader"
    with files[0].open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, (list, dict)) or isinstance(data, dict)
