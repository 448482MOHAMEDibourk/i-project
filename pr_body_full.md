# PR: Unify error handling for Aider client

## Summary

This PR unifies the error-handling contract for the Aider client used by i_system.
Instead of returning an opaque string that sometimes started with `[error]`, the
client now returns a consistent tuple `(ok: bool, message: str)` where `ok` is
True for success and False for failure, and `message` contains the response text
or an error string prefixed with `[error]`.

## Files changed

- `api_service/i_system/ai-school/clients/aider_client.py`
  - `AiderClient.ask` now returns `Tuple[bool, str]` and normalizes JSON/text
    responses and errors.
- `api_service/i_system/ai-school/tests/test_aider_client.py` (new)
  - Unit tests covering: plain text success, JSON success, HTTP error (404),
    and connection exception (ConnectionError). Tests are mocked and deterministic.

## Why

- Aligns with the project's error-handling convention used by `helpers.py` and
  other health checks (returns `(bool, str)`).
- Enables downstream code to programmatically inspect `ok` instead of parsing
  strings, improving reliability and testability.
- Fulfills project rules: `M3` (mandatory CI tests) and `G7` (unified run/start).

## Testing

- Tests were executed locally in an isolated virtualenv (`.venv-test`):

  - `pytest api_service/i_system/ai-school/tests/test_aider_client.py` → 4 passed

## CI / Next steps

- This branch includes tests and is ready for CI. After opening the PR please
  run the repository CI to confirm everything passes on remote runners.
- Follow-ups (separate PRs):
  - Refactor `AiderClient.ask` to reduce cognitive complexity (lint suggestion).
  - Apply the same `(bool, str)` contract to other clients if desired.

## Refactor performed

- During this branch I refactored `AiderClient.ask` to extract small helper
  functions (`_safe_text`, `_extract_text`) and simplified the control flow to
  reduce nesting and cognitive complexity while preserving behavior and error
  formatting. All unit tests still pass locally (`4 passed`).

## Notes

- If you prefer a different tuple shape or custom exception types, we can iterate
  in follow-up PRs; the goal here is to establish a reliable machine-readable
  contract for error handling.

Signed-off-by: i-project automation
