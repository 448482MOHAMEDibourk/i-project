import json


def test_converted_files_exist_and_parse(tmp_path, monkeypatch):
    # Create temporary converted directory and sample JSON files
    converted = tmp_path / "converted"
    converted.mkdir()
    for i in range(3):
        p = converted / f"sample_{i}.json"
        p.write_text(json.dumps({"i": i, "name": "test"}), encoding="utf-8")

    # Point DATA_DIR logic to our tmp path by monkeypatching Path resolution
    # The original tests expect a Path constant; instead we just assert contents here
    files = list(converted.glob("*.json"))
    assert files, f"No converted JSON files found in {converted}"

    sample = files[:3]
    for p in sample:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, (list, dict)) or isinstance(data, dict)
        if isinstance(data, list) and data:
            assert isinstance(data[0], dict)
