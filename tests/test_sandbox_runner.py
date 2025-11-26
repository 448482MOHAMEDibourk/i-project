import subprocess
import sys


def run_cmd(cmd, timeout=10):
    completed = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout
    )
    return completed.returncode, completed.stdout.decode(errors="ignore")


def test_sandbox_runner_plan_string_executes_ok():
    # Simple plan should print marker and exit 0
    cmd = [
        sys.executable,
        "scripts/sandbox_runner.py",
        "--plan-string",
        "echo 'TEST_SANDBOX_OK'",
        "--timeout",
        "5",
    ]
    rc, out = run_cmd(cmd, timeout=10)
    assert rc == 0
    assert "TEST_SANDBOX_OK" in out


def test_sandbox_runner_timeout_behavior():
    # A sleep longer than timeout should cause a non-zero exit (timeout)
    cmd = [
        sys.executable,
        "scripts/sandbox_runner.py",
        "--plan-string",
        "sleep 2; echo done",
        "--timeout",
        "1",
    ]
    try:
        completed = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=5
        )
        rc = completed.returncode
    except subprocess.TimeoutExpired:
        # If our test runner itself times out, consider it a failure
        assert False, "test runner timed out"

    # Expect non-zero (timeout or failure)
    assert rc != 0
