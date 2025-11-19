## GitHub helpers for i-sys

This file documents simple steps and a script to sync the local `ai-school` clone with a remote GitHub repository.

- `AI_SCHOOL_REPO` should be set in `i-sys/.env` (or exported) to the repository URL (ssh or https).
- Use `scripts/clone_ai_school.sh` to clone or pull updates (it already exists).
- `scripts/sync_ai_school.sh` (below) adds a safe wrapper to push local changes back to the remote when desired.

Usage examples:

1. Clone or update:

```bash
./scripts/clone_ai_school.sh --branch main
```

2. Push local changes (careful - this will `git add` and `git commit` any changes in the clone):

```bash
./scripts/sync_ai_school.sh --message "Update from i-sys" --push
```

This wrapper is intentionally conservative: it runs `git status` and exits with non-zero if there are merge conflicts or the working tree is not clean (unless `--force` is passed).
