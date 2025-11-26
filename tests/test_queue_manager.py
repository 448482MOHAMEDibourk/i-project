import json
import time

import modules.queue_manager as qm


def setup_tmp_dirs(tmp_path):
    qm.QUEUE_DIR = tmp_path / "queue"
    qm.PENDING_DIR = qm.QUEUE_DIR / "pending"
    qm.PROCESSING_DIR = qm.QUEUE_DIR / "processing"
    qm.COMPLETED_DIR = qm.QUEUE_DIR / "completed"
    qm.FAILED_DIR = qm.QUEUE_DIR / "failed"
    qm.PAUSED_DIR = qm.QUEUE_DIR / "paused"


def test_push_and_pop_cycle(tmp_path):
    setup_tmp_dirs(tmp_path)

    # push a task
    tid = qm.push_task("do work", metadata={"x": 1})
    pending = qm.get_pending_tasks()
    assert any(p["id"] == tid for p in pending)

    # pop it into processing
    task = qm.pop_task()
    assert task is not None
    assert task["id"] == tid
    assert task["status"] == "processing"

    # complete it
    qm.complete_task(tid, result={"ok": True})
    assert not (qm.PROCESSING_DIR / f"{tid}.json").exists()
    assert (qm.COMPLETED_DIR / f"{tid}.json").exists()


def test_fail_task_moves_to_failed(tmp_path):
    setup_tmp_dirs(tmp_path)

    tid = qm.push_task("will fail")
    task = qm.pop_task()
    assert task["id"] == tid

    qm.fail_task(tid, error="boom")
    assert not (qm.PROCESSING_DIR / f"{tid}.json").exists()
    failed = qm.FAILED_DIR / f"{tid}.json"
    assert failed.exists()
    data = json.loads(failed.read_text())
    assert data["status"] == "failed"
    assert data["error"] == "boom"


def test_fifo_ordering(tmp_path):
    setup_tmp_dirs(tmp_path)

    # push multiple tasks with tiny delays to ensure different timestamps
    ids = []
    for i in range(3):
        ids.append(qm.push_task(f"task {i}"))
        time.sleep(0.01)

    pending = qm.get_pending_tasks()
    assert [p["id"] for p in pending] == ids
