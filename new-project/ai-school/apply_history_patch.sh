#!/usr/bin/env bash
set -euo pipefail

# apply_history_patch.sh
# Copies mirror history records from the workspace into the official history tree
# and appends summary lines to CONSOLIDATED.md and PRIORITIES.md.

WORKSPACE_ROOT="$(cd "$(dirname "$0")" && pwd)"
MIRROR_DIR="$WORKSPACE_ROOT/history-mirror/experiments/reasons-for-success"
DEST_DIR="/home/eburk/Documents/i-project/history/experiments/reasons-for-success"

echo "Mirror dir: $MIRROR_DIR"
echo "Destination dir: $DEST_DIR"

mkdir -p "$DEST_DIR"

for f in "$MIRROR_DIR"/*; do
  if [ -f "$f" ]; then
    echo "Copying $(basename "$f") to $DEST_DIR"
    cp -v "$f" "$DEST_DIR/"
  fi
done

# Append brief entries to CONSOLIDATED.md and PRIORITIES.md
CONSOLIDATED="/home/eburk/Documents/i-project/history/CONSOLIDATED.md"
PRIORITIES="/home/eburk/Documents/i-project/priorities/PRIORITIES.md"

if [ -f "$CONSOLIDATED" ]; then
  ENTRY_CON="- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49."
  if ! grep -Fqx -- "$ENTRY_CON" "$CONSOLIDATED"; then
    echo "$ENTRY_CON" >> "$CONSOLIDATED"
    echo "Updated $CONSOLIDATED"
  else
    echo "Entry already present in $CONSOLIDATED — skipping"
  fi
else
  echo "Warning: $CONSOLIDATED not found — skipping consolidated update"
fi

if [ -f "$PRIORITIES" ]; then
  ENTRY_PRI="- ai-school: investigate training performance (dummy_accuracy 0.49) — 2025-11-18"
  if ! grep -Fqx -- "$ENTRY_PRI" "$PRIORITIES"; then
    echo "$ENTRY_PRI" >> "$PRIORITIES"
    echo "Updated $PRIORITIES"
  else
    echo "Entry already present in $PRIORITIES — skipping"
  fi
else
  echo "Warning: $PRIORITIES not found — skipping priorities update"
fi

echo "Done. Please review the copied files and updates in the official history tree."
