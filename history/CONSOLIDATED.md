# Consolidated History Index

This file is an index and consolidated summary of the `history/` directory. It lists the major folders, important files, and a short description of their purpose. Use the relative links to open each section.

## Top-level contents

- `CONSOLIDATED.md` — this file (high-level index and summary of history).
- `experiments/` — container for post-mortems, timestamped notes, and per-project experiments.
- `project-tech-cards/` — short technical cards describing projects and their key technologies.
- `project-build-plans/` — build plan templates and notes for creating new projects.
- `root-docs/` — reference copies of root-level documentation and templates archived for auditing and reproduction.

---

## experiments/

The `experiments` folder contains the detailed review notes, timestamped reasons for failure/success, and possible solutions for past projects.

- `experiments/INDEX.md` — index of experiment notes and timestamped files.
- `experiments/CONSOLIDATED.md` — (if present) consolidated notes aggregated from experiment-specific post-mortems.
- `experiments/projects/` — a folder containing the projects that were evaluated (e.g., `failed-projects/`, `succeed-projects/`). Each project subfolder may include README, notes, and outputs.
- `experiments/reasons-for-failure/` — timestamped markdown files explaining why projects failed.
- `experiments/reasons-for-success/` — timestamped markdown files explaining success factors.
- `experiments/solutions/` — timestamped solution proposals and applied fixes.

If you are reproducing an old experiment, start from the timestamped note in `reasons-for-failure` (or `reasons-for-success`) and read the linked project folder in `projects/`.

---

## project-tech-cards/

Contains one-file technical overviews per project. Examples:

- `project-tech-cards/ai-assistant.md`
- `project-tech-cards/ai-school.md`
- `project-tech-cards/Automation.md`
- `project-tech-cards/TutFit.md`
- `project-tech-cards/i_system.md`

Use these to quickly recall stack choices, known gaps, and next steps when revisiting a project.

---

## project-build-plans/

High-level templates and notes for bootstrapping new projects. See `project-build-plans/README.md` for details.

---

## root-docs/

Reference copies of important repository-wide files (policies, templates, and setup scripts). This directory is intended to store archival snapshots of files from the project root so we can reconstruct historical environments or policies.

Current files in `history/root-docs`:

- `.github/` — issue/PR templates archived under history.
- `.gitignore` — reference ignore rules.
- `CODEOWNERS` — reference code owners file.
- `CONTRIBUTING.md` — archived contributing guide.
- `ENVIRONMENT.md` — archived environment and tooling guide.
- `PROJECT_TEMPLATE.md` — project template.
- `PULL_REQUEST_TEMPLATE.md` — PR template.
- `README_PROJECT_TEMPLATE.md` — README template for new projects.
- `SECURITY.md` — archived security policy summary.
- `setup.sh` — reference setup script (may be minimal; use root `setup.sh` if present and authoritative).

---

## How to use this index

- When changing a root-level policy or template, create a dated snapshot in `history/root-docs` (e.g., `CONTRIBUTING_20251118.md`) before editing the live file.
- When investigating a failed project, review `experiments/reasons-for-failure/*` for the timestamped notes and follow the links to the project's folder in `experiments/projects/`.
- Keep `CONSOLIDATED.md` up-to-date: add a one-line summary and link to any new timestamped note or major policy change you add to `history/`.

---

If you want I can also:

- auto-generate dated snapshots for all root files changed in the last commit.
- add a small script `scripts/history-snapshot.sh` and a CI job that runs it on merge to main.
  Consolidated experiment notes

This file aggregates the auto-generated Failure / Success / Solutions notes for projects scanned on 2025-11-18.

## Automation

Summary:

- Gaps in test coverage, complex developer environment, dependency on specific tooling (Ollama).

Root causes:

- Incomplete automated test coverage
- Complex developer environment setup causing onboarding friction
- Dependencies on specific tooling that may be unstable

Success factors:

- Clear automation focus, modular tooling, documented workflows and VS Code tasks, emphasis on code quality and monitoring.

Proposed solutions:

- Implement CI that runs unit/integration tests on PRs
- Provide lightweight Docker-based dev environment
- Add monitoring dashboards and troubleshooting docs

## TutFit

Summary:

- Separation of backend and mobile; risks include broad scope, UI asset quality, and limited product-market validation.

Root causes:

- Broad scope (Flutter + backend) increasing complexity
- Need for clearer roadmap and user testing

Success factors:

- Well-structured repo, clear tech choices (FastAPI + Flutter), good setup guides

Proposed solutions:

- Narrow MVP scope and prioritize features
- Create automated deployment pipeline and sample data
- Improve UI assets or use placeholders

## ai-assistant

Summary:

- README is empty; repository lacks basic documentation.

Root causes:

- Missing project documentation and setup instructions
- Possibly incomplete packaging or CI

Success factors:

- N/A (insufficient documentation)

Proposed solutions:

- Add a minimal README with setup and demo
- Add CI checks and a smoke test

## ai-school

Summary:

- Project contains a README template but appears scaffolded without implementation details.

Root causes:

- Scaffolded but not actively developed; missing onboarding and contribution guidance

Success factors:

- README template provides a good starting structure

Proposed solutions:

- Populate README with installation/usage
- Add basic CI and CONTRIBUTING guide

## Notes

These consolidated notes were generated automatically from project README files. They are starting points; please expand each project's timestamped notes with logs, post-mortem findings, and action items when available.

- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- Provides test commands and venv setup in README

Proposed solutions:

- Add automated tests and CI checks
- Provide example data and a quickstart script

## Notes

These consolidated notes were generated automatically from project README files. They are starting points; please expand each project's timestamped notes with logs, post-mortem findings, and action items when available.

- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.

- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
- 2025-11-18: ai-school — run_ordered_prompt.py produced dummy_accuracy: 0.49.
