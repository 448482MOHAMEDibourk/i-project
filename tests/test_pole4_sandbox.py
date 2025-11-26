import importlib


def test_pole4_uses_sandbox_and_returns_output(monkeypatch, tmp_path):
    # Import the agent module
    mod = importlib.import_module("scripts.seven_pole_agent")

    # Ensure sandbox config is enabled for the test
    if "sandbox" not in mod.CONFIG:
        mod.CONFIG["sandbox"] = {}
    mod.CONFIG["sandbox"].update(
        {
            "enabled": True,
            "timeout": 10,
            "cpus": 0.1,
            "memory": "64m",
            "image": "python:3.11-slim",
        }
    )

    # Create a small plan that echoes a unique marker
    marker = "POLE4_SANDBOX_MARKER_12345"
    plan = f"echo '{marker}'"

    # Call pole_4_execution directly
    out = mod.pole_4_execution(plan, dry_run=False, gentle=True)

    assert marker in out
