# LESSONS LEARNED — 2025-11-25T191608Z (UTC)

**Branch:** `chore/rename-i_system-api_service`

## 1) Summary

- Created automated diagnostic `audit_errors.sh` which writes `DIAGNOSIS/CURRENT_ERRORS.txt`.
- Reduced lint noise by excluding archive files from `ruff` via `pyproject.toml`.
- Enabled manual CI dispatch by adding `workflow_dispatch` to ai-school workflows.
- Applied small focused fixes to address import-order issues (E402, F404) in:
  - `i_system/ai-school/clients/aider_client.py`
  - `i_system/i_sys/helpers.py`

## 2) Current important findings

- Lint warnings remain (E402/F404) in a few files; see `DIAGNOSIS/CURRENT_ERRORS.txt` for full output.
- Pytest collection fails in CI/local runs because local packages are not installed (ModuleNotFoundError: `i_sys`, `lesson_data`).
- `data/archive/**` contains many broken/archival tests and legacy code that cause pre-commit or collection noise if not explicitly ignored.

## 3) What we changed (short list)

- `pyproject.toml`: `tool.ruff.exclude = ["data/archive/**"]`
- `.github/workflows/ai-school-ci.yml`: added `workflow_dispatch:`
- `audit_errors.sh`: new diagnostic script that runs `ruff` (if installed) and `pytest`, exports `PYTHONPATH` candidates, and writes `DIAGNOSIS/CURRENT_ERRORS.txt`.
- Minor source fixes to move imports/future-imports to file top to reduce E402/F404.

## 4) How to reproduce diagnostics locally

Run the repository-root diagnostic script (recommended):

```
./audit_errors.sh
```

If you want to run tests with local packages available (recommended long-term):

```
python3 -m pip install -e .
PYTHONPATH=$PWD pytest -q
```

## 5) Short actionable checklist (next steps)

- [ ] Finish remaining E402/F404 fixes — run `ruff check .` and fix files reported.
- [ ] Make package `i_sys` and/or `lesson_data` installable (e.g., `pip install -e .`) so pytest can collect tests reliably.
- [ ] Consider updating pre-commit config to ignore `data/archive/**` or move archives out of the repo to avoid noise.
- [ ] After packaging fixes, re-run `./audit_errors.sh` and verify `DIAGNOSIS/CURRENT_ERRORS.txt` is clear for critical issues.
- [ ] When ready, apply bulk rename (`i_system` → `i_system`, `api_service` → `api_service`) in a dedicated PR and run CI.

## 6) References

- Diagnostic output: `DIAGNOSIS/CURRENT_ERRORS.txt`
- Related branch: `chore/rename-i_system-api_service`
- Helpful commands: `ruff check . --fix`, `pytest -q`, `python3 -m pip install -e .`

---

Generated and committed by automation on `chore/rename-i_system-api_service`.

## Appendix: DIAGNOSIS/CURRENT_ERRORS.txt (excerpt — first 50 lines)

```
--- Tue 25 Nov 2025 07:41:01 PM +01 ---
--- DETECTING PATHS TO AUDIT ---
Paths to audit: i_system api_service
 api_service/ai-school
\n--- RUFF LINTING ERRORS (Active
 Code) ---
--- ruff: i_system ---
E402 Module level import not at t
op of file
  --> i_system/i_sys/helpers.py:9:1
   |
 7 | """
 8 |
 9 | import json
   | ^^^^^^^^^^^
10 | import os
11 | from pathlib import Path
   |

E402 Module level import not at t
op of file
  --> i_system/i_sys/helpers.py:10:1
   |
 9 | import json
10 | import os
   | ^^^^^^^^^
11 | from pathlib import Path
12 | from typing import Dict, Tup
le
   |

E402 Module level import not at t
op of file
  --> i_system/i_sys/helpers.py:11:1
   |
 9 | import json
10 | import os
11 | from pathlib import Path
   | ^^^^^^^^^^^^^^^^^^^^^^^^
12 | from typing import Dict, Tup
le
   |

E402 Module level import not at t
op of file
  --> i_system/i_sys/helpers.py:12:1
   |
10 | import os
11 | from pathlib import Path
12 | from typing import Dict, Tup
le
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
^^
13 |
14 | import requests
   |

E402 Module level import not at t
op of file
  --> i_system/i_sys/helpers.py:14:1
   |
```

Generated and committed by automation on `chore/rename-i_system-api_service`.

````
