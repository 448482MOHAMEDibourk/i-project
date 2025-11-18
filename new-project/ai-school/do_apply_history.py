#!/usr/bin/env python3
import os
import shutil

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
MIRROR_DIR = os.path.join(
    WORKSPACE_ROOT, "history-mirror", "experiments", "reasons-for-success"
)
DEST_DIR = "/home/eburk/Documents/i-project/history/experiments/reasons-for-success"
CONSOLIDATED = "/home/eburk/Documents/i-project/history/CONSOLIDATED.md"
PRIORITIES = "/home/eburk/Documents/i-project/priorities/PRIORITIES.md"


def main():
    results = {
        "copied": [],
        "errors": [],
        "consolidated_updated": False,
        "priorities_updated": False,
    }
    os.makedirs(DEST_DIR, exist_ok=True)
    for fname in os.listdir(MIRROR_DIR):
        src = os.path.join(MIRROR_DIR, fname)
        dst = os.path.join(DEST_DIR, fname)
        try:
            shutil.copy2(src, dst)
            results["copied"].append(dst)
        except Exception as e:
            results["errors"].append({"file": src, "error": str(e)})

    # append consolidated (idempotent)
    try:
        if os.path.exists(CONSOLIDATED):
            entry = "- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.\n"
            with open(CONSOLIDATED, "r", encoding="utf-8") as f:
                content = f.read()
            if entry.strip() not in content:
                with open(CONSOLIDATED, "a", encoding="utf-8") as f:
                    f.write("\n" + entry)
                results["consolidated_updated"] = True
            else:
                results["consolidated_updated"] = False
        else:
            results["errors"].append(
                {"file": CONSOLIDATED, "error": "CONSOLIDATED.md not found"}
            )
    except Exception as e:
        results["errors"].append({"file": CONSOLIDATED, "error": str(e)})

    # append priorities (idempotent)
    try:
        if os.path.exists(PRIORITIES):
            entryp = "- ai-school: investigate training performance (dummy_accuracy 0.49) — 2025-11-18\n"
            with open(PRIORITIES, "r", encoding="utf-8") as f:
                pcontent = f.read()
            if entryp.strip() not in pcontent:
                with open(PRIORITIES, "a", encoding="utf-8") as f:
                    f.write("\n" + entryp)
                results["priorities_updated"] = True
            else:
                results["priorities_updated"] = False
        else:
            results["errors"].append(
                {"file": PRIORITIES, "error": "PRIORITIES.md not found"}
            )
    except Exception as e:
        results["errors"].append({"file": PRIORITIES, "error": str(e)})

    print(results)


if __name__ == "__main__":
    main()
