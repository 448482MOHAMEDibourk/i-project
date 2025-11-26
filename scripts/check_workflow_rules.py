#!/usr/bin/env python3
"""Simple CI/PR check for workflow rules.

Checks:
- For changed files under `data/` (or matching patterns), ensure a `TASKS.*` file exists in the affected folder root.
- Warn if `data/CONSOLIDATED.md` was not updated when data-derived folders changed (optional fail flag).

Usage:
  python scripts/check_workflow_rules.py [--base origin/feat/import-converted-data] [--fail-on-missing-consolidated]

Exit codes:
  0: OK or only warnings
  1: Failure (missing TASKS files or fatal errors)

This is intentionally small and conservative. It is safe to run locally and in CI.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List, Set


def run(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def get_changed_files(base: str) -> List[str]:
    # fetch minimal refs so origin/<base> exists
    try:
        subprocess.run(["git", "fetch", "--no-tags", "origin", base.split("/")[1]], check=False)
    except Exception:
        pass
    try:
        out = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    except subprocess.CalledProcessError:
        # fallback to all tracked files if diff fails
        out = run(["git", "ls-files"]) or ""
    return [line for line in out.splitlines() if line]


def top_data_folder(path: str) -> str | None:
    # For a path like data/foo/bar/baz.txt -> return data/foo
    parts = path.split(os.sep)
    if len(parts) >= 2 and parts[0] == "data":
        return os.path.join("data", parts[1])
    return None


def check_tasks_for_folders(folders: Set[str]) -> List[str]:
    missing = []
    for folder in sorted(folders):
        exists = False
        for name in ("TASKS.md", "TASKS.yaml", "TODO.md"):
            if os.path.exists(os.path.join(folder, name)):
                exists = True
                break
        if not exists:
            missing.append(folder)
    return missing


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/feat/import-converted-data", help="Git base ref to diff against")
    parser.add_argument("--fail-on-missing-consolidated", action="store_true", help="Treat missing CONSOLIDATED.md update as failure")
    args = parser.parse_args(argv)

    changed = get_changed_files(args.base)
    if not changed:
        print("No changed files detected.")
        return 0

    data_folders: Set[str] = set()
    consolidated_changed = False
    for p in changed:
        if p == "data/CONSOLIDATED.md":
            consolidated_changed = True
        tf = top_data_folder(p)
        if tf:
            data_folders.add(tf)

    if not data_folders:
        print("No data-derived folders changed. Nothing to check.")
        return 0

    print(f"Data-derived folders changed: {', '.join(sorted(data_folders))}")

    missing_tasks = check_tasks_for_folders(data_folders)
    if missing_tasks:
        print("ERROR: The following data-derived folders are missing a TASKS.* file:")
        for m in missing_tasks:
            print(f"  - {m} (add TASKS.md or TODO.md)")
        print("Failing check.")
        return 1

    if not consolidated_changed:
        msg = "Warning: 'data/CONSOLIDATED.md' was not modified; consider updating it with summaries of these runs."
        if args.fail_on_missing_consolidated:
            print("ERROR:", msg)
            return 1
        else:
            print("WARN:", msg)

    print("All workflow rule checks passed (or only warnings).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Fatal error in check_workflow_rules:", e, file=sys.stderr)
        sys.exit(2)
