#!/usr/bin/env python3
"""Check PR changed files against protected path patterns.

Exit non-zero if protected paths are changed and no EXCEPTION is present.
"""

import json
import os
import re
import subprocess
import sys


def load_event():
    path = os.environ.get("GITHUB_EVENT_PATH")
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


PROTECTED_PATTERNS = [
    r"^data/archive/",
    r"^docs/.*\\.md$",
    r"^projects/cards/",
    r"^configs/default_choices\\..*",
    r"^scripts/run_",
    r"^scripts/commands/",
]

# Append-only patterns: these paths must not be modified or deleted (only additions allowed)
APPEND_ONLY_PATTERNS = [
    r"^data/archive/",
    r"^data/experiments/",
    r"^knowledge/",
]


def matches_protected(path):
    for p in PROTECTED_PATTERNS:
        if re.search(p, path):
            return True
    return False


def git_changed_files_status(base_ref):
    # fetch of base_ref should be done in workflow step
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-status", f"origin/{base_ref}...HEAD"]
        )
        lines = out.decode().splitlines()
        # returns list of (status, path)
        files = []
        for line in lines:
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 1:
                # sometimes space separated
                parts = line.split(maxsplit=1)
            if len(parts) == 2:
                status, path = parts
                files.append((status.strip(), path.strip()))
        return files
    except subprocess.CalledProcessError:
        return []


def main():
    ev = load_event()
    pr = ev.get("pull_request", {})
    base_ref = pr.get("base", {}).get("ref")
    title = pr.get("title", "")
    body = pr.get("body", "") or ""
    labels = [lbl.get("name") for lbl in pr.get("labels", [])]

    if not base_ref:
        print("No base ref found in event payload; skipping protected path check.")
        return 0

    files_status = git_changed_files_status(base_ref)
    files = [p for (_, p) in files_status]
    protected = [f for f in files if matches_protected(f)]

    # detect append-only violations: modified (M) or deleted (D) in append-only paths
    append_violations = []
    for status, path in files_status:
        if status.upper() in {"M", "D"}:
            for p in APPEND_ONLY_PATTERNS:
                if re.search(p, path):
                    append_violations.append((status, path))
                    break

    if not protected:
        print("No protected paths changed.")
        return 0

    has_exception = False
    # check title/body/labels for EXCEPTION
    if "EXCEPTION:" in title or "EXCEPTION:" in body:
        has_exception = True
    if any(lbl.upper() == "EXCEPTION" for lbl in (labels or [])):
        has_exception = True

    if has_exception:
        print("Protected paths changed, but EXCEPTION provided. Allowed.")
        if protected:
            print("Changed protected files:")
            for p in protected:
                print(" - ", p)
        if append_violations:
            print("Append-only violations detected but EXCEPTION allows them:")
            for s, p in append_violations:
                print(f" - {s}\t{p}")
        return 0

    # If there are append-only violations, fail with a clear message
    if append_violations:
        print(
            "ERROR: Append-only paths were modified or deleted but no EXCEPTION provided."
        )
        print("Append-only files changed (status:\tpath):")
        for s, p in append_violations:
            print(f" - {s}\t{p}")
        print(
            "\nThese paths are append-only. Do not modify or delete existing records. To correct data, add a new record/entry with explanation."
        )
        print(
            "If this change is required, include an 'EXCEPTION: <paths>' line in the PR body and link the approval issue."
        )
        return 2

    if protected:
        print("ERROR: Protected paths were changed but no EXCEPTION provided.")
        print("Changed protected files:")
        for p in protected:
            print(" - ", p)
        print(
            "\nTo approve this change, include an 'EXCEPTION: <paths>' line in the PR body or add an 'EXCEPTION' label, and link the approval issue."
        )
        return 2

    print("No protected or append-only violations detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
