#!/usr/bin/env python3
"""Codemod to migrate module-level env reads to central settings access.

Produces a dry-run tree under `.tmp_g12_refactor/dryrun/` and a mapping CSV
`.tmp_g12_refactor/mapping_replacements.csv` with rows: file,location,env_name,target

Usage:
  python3 scripts/g12_codemod_replace_envs.py --paths src scripts --dry-run --out .tmp_g12_refactor

Notes:
 - This is a conservative, best-effort codemod. Review the CSV and dryrun tree
   before applying changes to the real repo. It replaces `os.getenv("FOO")`
   and `os.environ["FOO"]` with `settings.get("FOO")` and attempts to add
   `from src.config.settings import settings` when needed.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List, Tuple

import libcst as cst
import libcst.matchers as m


class EnvToSettingsTransformer(cst.CSTTransformer):
    """Transformer that replaces os.getenv(...) and os.environ[...] with settings.get(...).

    It records mappings into `self.mappings` as tuples (env_name, lineno, orig_code).
    """

    def __init__(self, filename: str, mappings: List[Tuple[str, str, int]]):
        super().__init__()
        self.filename = filename
        self.mappings = mappings
        self.add_settings_import = False

    def _string_value(self, node: cst.BaseExpression) -> str | None:
        if isinstance(node, cst.SimpleString):
            try:
                return node.evaluated_value
            except Exception:
                return None
        return None

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        # match os.getenv("FOO")
        if m.matches(
            original.func, m.Attribute(value=m.Name("os"), attr=m.Name("getenv"))
        ):
            if original.args:
                envname = self._string_value(original.args[0].value)
                if envname:
                    # record mapping (file, envname, lineno)
                    lineno = getattr(original, "lineno", 0)
                    self.mappings.append((self.filename, envname, lineno))
                    self.add_settings_import = True
                    # produce settings.get("FOO")
                    new_call = cst.Call(
                        func=cst.Attribute(
                            value=cst.Name("settings"), attr=cst.Name("get")
                        ),
                        args=[cst.Arg(value=cst.SimpleString(f'"{envname}"'))],
                    )
                    return new_call
        return updated

    def leave_Subscript(
        self, original: cst.Subscript, updated: cst.Subscript
    ) -> cst.BaseExpression:
        # match os.environ["FOO"]
        if m.matches(
            original.value, m.Attribute(value=m.Name("os"), attr=m.Name("environ"))
        ):
            # slices is a list of SubscriptElement
            if original.slice and len(original.slice) == 1:
                elt = original.slice[0]
                if isinstance(elt.slice.value, cst.SimpleString):
                    envname = elt.slice.value.evaluated_value
                    lineno = getattr(original, "lineno", 0)
                    self.mappings.append((self.filename, envname, lineno))
                    self.add_settings_import = True
                    new_call = cst.Call(
                        func=cst.Attribute(
                            value=cst.Name("settings"), attr=cst.Name("get")
                        ),
                        args=[cst.Arg(value=cst.SimpleString(f'"{envname}"'))],
                    )
                    return new_call
        return updated


def process_file(
    path: Path, out_root: Path, dry_run: bool, mappings: List[Tuple[str, str, int]]
) -> bool:
    src_text = path.read_text(encoding="utf-8")
    try:
        module = cst.parse_module(src_text)
    except Exception as e:
        print(f"[skip] parse error {path}: {e}")
        return False

    transformer = EnvToSettingsTransformer(str(path), mappings)
    new_mod = module.visit(transformer)

    new_code = new_mod.code

    # If transformer wants settings import and source doesn't already import it,
    # prepend a conservative import. We check for the string 'src.config.settings' or 'config.settings'.
    if transformer.add_settings_import:
        if (
            "from src.config.settings import settings" not in src_text
            and "from config.settings import settings" not in src_text
            and "import settings" not in src_text
        ):
            import_line = "from src.config.settings import settings\n"
            new_code = import_line + new_code

    if dry_run:
        # Ensure path resolution so relative_to works even if an absolute
        # path or different cwd representation is provided. Use resolved
        # paths to avoid ValueError seen when path is not a subpath.
        try:
            rel = path.resolve().relative_to(Path.cwd().resolve())
        except Exception:
            # Fallback: make the path relative to filesystem root (drop leading
            # anchor) so we still preserve a stable relative path under the
            # dry-run output. As a last resort, use the file name.
            try:
                rel = path.resolve().relative_to(path.resolve().anchor)
            except Exception:
                rel = Path(path.name)

        target = out_root / "dryrun" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_code, encoding="utf-8")
    else:
        path.write_text(new_code, encoding="utf-8")
    return True


def gather_files(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            continue
        for f in p.rglob("*.py"):
            # skip virtualenvs and site-packages
            if any(part in (".venv", "venv", "site-packages") for part in f.parts):
                continue
            files.append(f)
    return files


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="G12 codemod: migrate env reads to settings.get()"
    )
    p.add_argument(
        "--paths", nargs="+", default=["src", "scripts"], help="Root paths to scan"
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Write transformed files to out/dryrun instead of inplace",
    )
    p.add_argument(
        "--out",
        default=".tmp_g12_refactor",
        help="Output root for dry-run and mapping CSV",
    )
    args = p.parse_args(argv)

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    dry_run = bool(args.dry_run)
    files = gather_files(args.paths)
    print(f"Found {len(files)} python files to inspect")

    mappings: List[Tuple[str, str, int]] = []
    for f in files:
        process_file(f, out_root, dry_run, mappings)

    csv_path = out_root / "mapping_replacements.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["file", "env_name", "lineno"])
        for row in mappings:
            writer.writerow(list(row))

    print(f"Done. mapping CSV: {csv_path}. Dry-run files at {out_root / 'dryrun'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
