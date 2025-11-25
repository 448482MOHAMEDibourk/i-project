#!/usr/bin/env python3
"""Simple unused-dependencies checker.

Heuristic approach:
- Read `requirements.txt` (if present) and extract package names
- Search Python/JS/TS files under given paths for `import pkg` or `from pkg import`
- Report packages not found by those heuristics

This is intentionally simple and conservative; it is meant to catch obvious dead entries.
"""
from __future__ import annotations

import argparse
import os
import re
from typing import List, Set


def read_requirements(req_path: str = "requirements.txt") -> Set[str]:
    pkgs: Set[str] = set()
    if not os.path.exists(req_path):
        return pkgs
    with open(req_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-r ") or line.startswith("--requirement"):
                continue
            # split off version or extras
            name = re.split(r"[=<>\[]", line)[0].lower()
            name = name.strip()
            if name:
                pkgs.add(name)
    return pkgs


def scan_code_for_imports(paths: List[str], pkgs: Set[str]) -> Set[str]:
    used: Set[str] = set()
    if not pkgs:
        return used

    code_ext = (".py", ".js", ".ts")
    # build regex table for packages for faster checks
    pkg_regex = {
        p: re.compile(
            rf"(^|\s|\.|\(|\[|\")((from)\s+{re.escape(p)}\b|(import)\s+{re.escape(p)}\b)"
        )
        for p in pkgs
    }

    for start in paths:
        if not os.path.exists(start):
            continue
        for root, _, files in os.walk(start):
            for f in files:
                if not f.endswith(code_ext):
                    continue
                fp = os.path.join(root, f)
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                        for p, rx in pkg_regex.items():
                            if rx.search(content):
                                used.add(p)
                except Exception:
                    # skip unreadable files
                    continue
    return used


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--paths", nargs="*", default=["src", "scripts", "tests"]
    )  # paths to search
    parser.add_argument(
        "--req", default="requirements.txt", help="Path to requirements.txt"
    )
    args = parser.parse_args(argv)

    pkgs = read_requirements(args.req)
    if not pkgs:
        print("Warning: no packages found in requirements.txt; skipping G11 check.")
        return 0

    print(
        f"--- Checking for Unused Dependencies (G11): {len(pkgs)} packages to check ---"
    )
    used = scan_code_for_imports(args.paths, pkgs)
    unused = sorted(list(pkgs - used))

    if unused:
        print(f"--- G11 FAILURE: Found {len(unused)} UNUSED Dependencies ---")
        for u in unused:
            print(f"- {u}")
        return 1

    print(
        "--- G11 PASSED: All packages in requirements.txt appear to be used (heuristic). ---"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
