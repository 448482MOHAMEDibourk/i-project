#!/usr/bin/env bash
# audit_errors.sh
# Goal: produce a single diagnostic file with linting and pytest output

set -uo pipefail

OUTPUT_FILE="DIAGNOSIS/CURRENT_ERRORS.txt"
mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "--- $(date) ---" > "$OUTPUT_FILE"

echo "--- DETECTING PATHS TO AUDIT ---" >> "$OUTPUT_FILE"
# prefer renamed paths if present, otherwise fall back to originals
LINT_PATHS=()
if [ -d "i_system" ]; then
  LINT_PATHS+=("i_system")
elif [ -d "i-sys" ]; then
  LINT_PATHS+=("i-sys")
fi

if [ -d "api_service" ]; then
  LINT_PATHS+=("api_service")
elif [ -d "new-project" ]; then
  LINT_PATHS+=("new-project")
fi

# Always consider ai-school subfolder if present under either location
# (this helps pick up new-project/ai-school or api_service/ai-school)
if [ -d "api_service/ai-school" ]; then
  LINT_PATHS+=("api_service/ai-school")
elif [ -d "new-project/ai-school" ]; then
  LINT_PATHS+=("new-project/ai-school")
fi

if [ ${#LINT_PATHS[@]} -eq 0 ]; then
  echo "No target paths found (i_system / i-sys / api_service / new-project)" >> "$OUTPUT_FILE"
  echo "No paths found locally. Exiting." >&2
  echo "--- AUDIT COMPLETE (no targets) ---" >> "$OUTPUT_FILE"
  head -n 20 "$OUTPUT_FILE"
  exit 0
fi

echo "Paths to audit: ${LINT_PATHS[*]}" >> "$OUTPUT_FILE"

echo "\n--- RUFF LINTING ERRORS (Active Code) ---" >> "$OUTPUT_FILE"
if command -v ruff >/dev/null 2>&1; then
  for p in "${LINT_PATHS[@]}"; do
    echo "--- ruff: $p ---" >> "$OUTPUT_FILE"
    ruff check "$p" >> "$OUTPUT_FILE" 2>&1 || true
  done
else
  echo "ruff not found in PATH; skipping ruff." >> "$OUTPUT_FILE"
fi

echo "\n--- PYTEST (Import & Config Errors) ---" >> "$OUTPUT_FILE"
if command -v pytest >/dev/null 2>&1; then
  # Ensure test-time imports can be resolved by adding possible package roots to PYTHONPATH
  export PYTHONPATH="${PYTHONPATH:-}"
  for d in i-sys i_system new-project api_service; do
    if [ -d "$d" ]; then
      export PYTHONPATH="$PWD/$d:$PYTHONPATH"
    fi
  done
  # run pytest only on the directories that exist (pytest tolerates being passed multiple paths)
  pytest -q "${LINT_PATHS[@]}" >> "$OUTPUT_FILE" 2>&1 || true
else
  echo "pytest not found in PATH; skipping pytest." >> "$OUTPUT_FILE"
fi

echo "\n--- AUDIT COMPLETE ---" >> "$OUTPUT_FILE"

echo "تم حفظ التقرير الشامل في: $OUTPUT_FILE"

echo "\n--- output preview ---"
head -n 20 "$OUTPUT_FILE"
