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


def matches_protected(path):
    for p in PROTECTED_PATTERNS:
        if re.search(p, path):
            return True
    return False


def git_changed_files(base_ref):
    # fetch of base_ref should be done in workflow step
    try:
        out = subprocess.check_output(["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"]) 
        files = out.decode().splitlines()
        return files
    except subprocess.CalledProcessError:
        return []


def main():
    ev = load_event()
    pr = ev.get("pull_request", {})
    base_ref = pr.get("base", {}).get("ref")
    title = pr.get("title", "")
    body = pr.get("body", "") or ""
    labels = [l.get("name") for l in pr.get("labels", [])]

    if not base_ref:
        print("No base ref found in event payload; skipping protected path check.")
        return 0

    files = git_changed_files(base_ref)
    protected = [f for f in files if matches_protected(f)]

    if not protected:
        print("No protected paths changed.")
        return 0

    has_exception = False
    # check title/body/labels for EXCEPTION
    if "EXCEPTION:" in title or "EXCEPTION:" in body:
        has_exception = True
    if any(l.upper() == "EXCEPTION" for l in (labels or [])):
        has_exception = True

    if has_exception:
        print("Protected paths changed, but EXCEPTION provided. Allowed.")
        print("Changed protected files:")
        for p in protected:
            print(" - ", p)
        return 0

    print("ERROR: Protected paths were changed but no EXCEPTION provided.")
    print("Changed protected files:")
    for p in protected:
        print(" - ", p)
    print("\nTo approve this change, include an 'EXCEPTION: <paths>' line in the PR body or add an 'EXCEPTION' label, and link the approval issue.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
