import csv
from pathlib import Path

import modules.metrics as metrics


def test_metrics_tracker_and_log_event(tmp_path):
    # Point BENCHMARK_FILE to a temp file
    metrics.BENCHMARK_FILE = tmp_path / "benchmarks.csv"

    mt = metrics.MetricsTracker()
    mt.start_pole("pole_x")
    # end_pole should write a row
    duration = mt.end_pole("pole_x", task_id="t1", model="m1", success=True)
    assert duration is not None

    # log a custom event
    metrics.log_event("t1", "requeue", details="attempt 1/3", model="m1", success=False)

    # Read CSV and confirm rows exist
    with open(metrics.BENCHMARK_FILE, newline="") as f:
        reader = list(csv.reader(f))

    # Header + at least two rows (end_pole and log_event)
    assert len(reader) >= 3
    header = reader[0]
    assert header[0] == "timestamp"
