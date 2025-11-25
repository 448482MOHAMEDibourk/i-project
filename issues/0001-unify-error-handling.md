---
title: Unify error-handling contract across clients (follow-up)
labels: enhancement, follow-up, backlog
---

## Summary

Apply the `(bool, str)` error-handling contract adopted for `AiderClient`
to other client modules and health-check helpers in the repository. This
ensures a consistent programmatic contract across services and simplifies
consumers' error handling logic.

## Why

- Consistency: downstream code can inspect `ok` rather than parsing strings.
- Testability: easier to write deterministic tests for success/error paths.
- Compliance: aligns with repository engineering rules (M3, G7).

## Scope / Suggested targets

- `new-project/i-sys/i_sys/helpers.py` (already returns `(bool, str)` — verify and harmonize)
- Any client under `new-project/i-sys/ai-school/clients/` (for example `aider_client.py`, any other wrappers)
- Scripts or utilities that return/print error strings which are consumed programmatically

## Acceptance criteria

1. Each targeted client exposes an interface that returns `Tuple[bool, str]` for key operations.
2. Unit tests added for each client demonstrating success and failure cases (mock network as needed).
3. Existing callers updated or adapter functions added where immediate sweeping changes would be disruptive.
4. PR(s) opened per client or grouped sensibly, each with passing CI.

## Steps

1. Audit repository for clients/health-checks that return error strings.
2. For each candidate file:
   - Implement `(bool, str)` return contract.
   - Add/adjust unit tests (mock network I/O).
   - Ensure backwards-compatibility via adapters if required.
3. Open PR(s) with clear PR bodies and cross-reference this follow-up issue.

## Estimate

- Audit: 1-2 hours
- Per client: 1-3 hours (depending on complexity and tests required)

## Notes

- Keep changes isolated per PR when practical to ease review.
- Link to current PR that introduced AiderClient changes: `chore/unify-error-handling`.
