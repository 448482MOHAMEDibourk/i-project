#!/usr/bin/env python3
"""Run a shell plan inside a sandbox (Docker if available, else best-effort local).

This is a minimal, best-effort sandbox helper used by `seven_pole_agent.py`.
It accepts a plan as a string or a path to a file containing shell commands.

Usage:
  python3 scripts/sandbox_runner.py --plan-file /path/to/plan.sh --timeout 60 --cpus 0.5 --memory 256m
  python3 scripts/sandbox_runner.py --plan-string "echo hi && sleep 1" --timeout 10
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_in_docker(
    script_path: Path, timeout: int, cpus: float, memory: str, image: str
):
    docker_bin = shutil.which("docker")
    if docker_bin is None:
        return False, "docker-not-found"

    # Mount the script's parent directory into the container
    host_dir = str(script_path.parent.resolve())
    container_workdir = "/workspace"
    container_script = f"{container_workdir}/{script_path.name}"

    cmd = [
        docker_bin,
        "run",
        "--rm",
        "--network=none",
        f"--cpus={cpus}",
        f"--memory={memory}",
        "-v",
        f"{host_dir}:{container_workdir}:ro",
        "-w",
        container_workdir,
        image,
        "bash",
        container_script,
    ]

    try:
        completed = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout
        )
        return True, completed.stdout.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def run_locally(script_path: Path, timeout: int):
    # Best-effort local execution with timeout
    try:
        completed = subprocess.run(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        return True, completed.stdout.decode(errors="ignore")
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan-file", type=str, help="Path to a shell script file to run")
    g.add_argument("--plan-string", type=str, help="Plan as a string of shell commands")
    parser.add_argument("--timeout", type=int, default=60, help="Max seconds for plan")
    parser.add_argument("--cpus", type=float, default=0.5, help="CPUs for docker")
    parser.add_argument(
        "--memory", type=str, default="256m", help="Memory limit for docker"
    )
    parser.add_argument(
        "--image", type=str, default="python:3.11-slim", help="Docker image for sandbox"
    )
    args = parser.parse_args()

    tmp_dir = None
    try:
        if args.plan_file:
            script_path = Path(args.plan_file)
            if not script_path.exists():
                print(f"plan file not found: {script_path}", file=sys.stderr)
                sys.exit(2)
        else:
            # write plan-string to a temp script
            tmp_dir = Path(tempfile.mkdtemp(prefix="sandbox_plan_"))
            script_path = tmp_dir / "plan.sh"
            script_path.write_text(args.plan_string)
            script_path.chmod(0o755)

        # Try docker first
        ok, out = run_in_docker(
            script_path, args.timeout, args.cpus, args.memory, args.image
        )
        if ok:
            print(out)
            sys.exit(0)

        # Fallback to local execution
        ok2, out2 = run_locally(script_path, args.timeout)
        if ok2:
            print(out2)
            sys.exit(0)

        # All failed
        print(out or out2 or "unknown error", file=sys.stderr)
        sys.exit(3)

    finally:
        if tmp_dir and tmp_dir.exists():
            try:
                shutil.rmtree(tmp_dir)
            except Exception:
                pass


if __name__ == "__main__":
    main()
