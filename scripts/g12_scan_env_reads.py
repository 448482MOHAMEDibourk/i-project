#!/usr/bin/env python3
"""Simple scanner to find env reads (os.getenv / os.environ[...]) and emit mapping CSV.

This is a conservative, regex-based dry-run scanner used to produce a reviewable
mapping before running an automated codemod.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import List


def scan_file(path: Path):
    results = []
    getenv_re = re.compile(r"os\.getenv\(\s*(['\"])([A-Za-z0-9_]+)\1")
    environ_re = re.compile(r"os\.environ\[\s*(['\"])([A-Za-z0-9_]+)\1\s*\]")
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return results
    for i, line in enumerate(text.splitlines(), start=1):
        for m in getenv_re.finditer(line):
            results.append((str(path), m.group(2), i, "os.getenv"))
        for m in environ_re.finditer(line):
            results.append((str(path), m.group(2), i, "os.environ"))
    return results


def gather_files(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            continue
        for f in p.rglob("*.py"):
            # skip venv/site-packages
            if any(part in (".venv", "venv", "site-packages") for part in f.parts):
                continue
            files.append(f)
    return files


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--paths", nargs="+", default=["src", "scripts"], help="Paths to scan"
    )
    p.add_argument("--out", default=".tmp_g12_refactor", help="Output directory")
    args = p.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / "mapping_replacements.csv"

    files = gather_files(args.paths)
    mappings = []
    for f in files:
        mappings.extend(scan_file(f))

    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["file", "env_name", "lineno", "kind"])
        for row in mappings:
            writer.writerow(row)

    print(f"Wrote {len(mappings)} entries to {csv_path}")


if __name__ == "__main__":
    main()
