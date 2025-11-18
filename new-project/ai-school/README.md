# ai-school

Minimal scaffold for the ai-school demo project.

Quickstart

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the smoke example:

```bash
python run_ordered_prompt.py
```

3. The smoke training writes `models/dummy_metrics.json` and `ordered_output.json`.

Purpose

This small scaffold is intended to make it easy to run the local smoke test and to integrate a minimal CI workflow for validation.
