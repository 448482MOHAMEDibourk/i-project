#!/usr/bin/env python3
"""Validate naming conventions for files and directories.

Checks a set of paths for naming conventions (G14/G15):
- Python modules: snake_case (a-z0-9_)
- Other files/dirs: allow snake_case, kebab-case, dots, and numbers

Usage: python3 scripts/validate_naming.py --paths src scripts tests docs config
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from typing import List, Tuple


EXCLUDE_PATTERNS = [
    "data/archive",
    "data/raw",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
]


def is_excluded(path: str) -> bool:
    for p in EXCLUDE_PATTERNS:
        if p and p in path:
            return True
    return False


def check_paths(paths: List[str]) -> Tuple[bool, int]:
    errors = 0
    messages: List[str] = []

    py_re = re.compile(r"^[a-z0-9_]+\.py$")
    dir_re = re.compile(r"^[a-z0-9_.-]+$")
    other_re = re.compile(r"^[a-z0-9_.-]+$")

    for start in paths:
        if not os.path.exists(start):
            continue

        for root, dirs, files in os.walk(start, topdown=True):
            # filter out excluded dirs early
            dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d))]

            for d in dirs:
                full = os.path.join(root, d)
                if is_excluded(full):
                    continue
                if not dir_re.match(d):
                    messages.append(f"DIR ERROR (G14/G15): '{full}' should use snake_case or kebab-case (lowercase, numbers, '-', '_' or '.').")
                    errors += 1

            for f in files:
                full = os.path.join(root, f)
                if is_excluded(full):
                    continue

                # Skip hidden/system files
                if f.startswith("."):
                    continue

                if f.endswith(".py"):
                    if not py_re.match(f):
                        messages.append(f"FILE ERROR (G14): Python file '{full}' should be snake_case (e.g., my_file.py).")
                        errors += 1
                else:
                    # relaxed rule for docs/config/data files
                    if not other_re.match(f):
                        messages.append(f"FILE WARNING: File '{full}' has unusual characters; prefer snake_case or kebab-case.")

    if errors:
        print("--- Naming Validation FAILED (G14/G15) ---")
        for m in messages:
            print(m)
        return False, errors

    print("--- Naming Validation PASSED (G14/G15) ---")
    return True, 0


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="*", default=["docs", "src", "scripts", "tests", "config"])  # default targets
    args = parser.parse_args(argv)

    success, count = check_paths(args.paths)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
