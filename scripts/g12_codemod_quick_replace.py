#!/usr/bin/env python3
"""Quick, conservative replacer for os.getenv/os.environ -> settings.get

This script is a simpler, more forgiving alternative to the libcst codemod
for small, targeted runs. It performs string-based replacements for literal
env keys and writes a mapping CSV and a dry-run tree under the provided out
directory.

Usage:
  python3 scripts/g12_codemod_quick_replace.py --paths <paths...> --out .tmp_quick
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import List

GETENV_RE = re.compile(r"os\.getenv\(\s*(['\"])([A-Za-z0-9_]+)\1\s*\)")
ENVIRON_RE = re.compile(r"os\.environ\[\s*(['\"])([A-Za-z0-9_]+)\1\s*\]")


def process_file(path: Path, out_root: Path, dry_run: bool, mappings: list):
    src = path.read_text(encoding="utf-8")
    new = src
    changed = False

    def _repl_getenv(m):
        nonlocal changed
        key = m.group(2)
        changed = True
        mappings.append((str(path), key))
        return f'settings.get("{key}")'

    def _repl_environ(m):
        nonlocal changed
        key = m.group(2)
        changed = True
        mappings.append((str(path), key))
        return f'settings.get("{key}")'

    new = GETENV_RE.sub(_repl_getenv, new)
    new = ENVIRON_RE.sub(_repl_environ, new)

    if changed:
        # ensure import exists
        if (
            "from src.config.settings import settings" not in new
            and "from config.settings import settings" not in new
            and "import settings" not in new
        ):
            new = "from src.config.settings import settings\n" + new

    if dry_run:
        target = out_root / path.relative_to(Path.cwd())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new, encoding="utf-8")
    else:
        if changed:
            path.write_text(new, encoding="utf-8")


def gather_files(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            continue
        for f in p.rglob("*.py"):
            if any(part in (".venv", "venv", "site-packages") for part in f.parts):
                continue
            files.append(f)
    return files


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--paths", nargs="+", required=True)
    p.add_argument("--out", default=".tmp_quick")
    p.add_argument("--dry-run", action="store_true", default=True)
    args = p.parse_args(argv)

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    files = gather_files(args.paths)
    print(f"Found {len(files)} python files to inspect (quick replacer)")

    mappings = []
    for f in files:
        process_file(f, out_root, args.dry_run, mappings)

    csv_path = out_root / "mapping_quick.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["file", "env_name"])
        for row in mappings:
            writer.writerow(list(row))

    print(f"Done. mapping CSV: {csv_path}. Dry-run files at {out_root}")


if __name__ == "__main__":
    raise SystemExit(main())
