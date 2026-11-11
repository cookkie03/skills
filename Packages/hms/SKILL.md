---
name: hms
description: "Delegate operational work to the Hermes Agent CLI (`hermes`) as a headless subagent while you orchestrate and verify. Use whenever the user mentions /hms, hms, hermes cli, headless hermes, /hermes, or asks you to delegate bounded work to Hermes while you supervise. Also use for scoped code edits, repository analysis, refactors, build/test triage, multi-turn batch tasks, or second opinions. Prefer `hermes chat --oneshot -Q` or `hermes chat --query-file` for non-interactive task execution."
metadata:
  {
    "openclaw":
      {
        "emoji": "☤",
        "requires": { "bins": ["hermes"] },
        "install":
          [
            {
              "id": "shell",
              "kind": "shell",
              "command": "pipx upgrade hermes-agent || hermes update",
              "bins": ["hermes"],
              "label": "Update Hermes Agent CLI",
            },
          ],
      },
  }
---

# hms - Hermes CLI as a supervised subagent

Use `hermes` for bounded operational work, not for final judgment. You brief it, scope it, run it, then verify its output, logs, and diffs before reporting to the user.

## Fast Start

```bash
hermes --version
hermes chat -h
git -C /path/to/repo status --short

hermes chat --in /path/to/repo --yolo --oneshot -Q -q "<self-contained task>"
cat /tmp/hms-task/brief.md | hermes chat --in /path/to/repo --yolo --oneshot -Q --query-file -
```

Build commands from the installed help output (`hermes chat -h`). Hermes flags differ across subcommands; do not pass a flag to `hermes chat` unless `hermes chat -h` lists it. In particular, always include `--oneshot -Q` and `--yolo` for autonomous non-interactive executions.

## Brief

Give Hermes a standalone task: goal, paths, constraints, allowed scope, tests to run, and the exact report you need. Mention unrelated user changes explicitly and tell Hermes not to commit, push, delete, or touch out-of-scope paths.

```text
You are a headless Hermes subagent. Work in /path/to/repo.
Task: <goal>
Scope: touch only <paths>; preserve existing behavior unless requested.
Verification: run <checks> if feasible.
Report: files changed, commands run, test results, blockers, residual risks.
```

## Robust Run

For substantial work, keep brief and logs separate:

```bash
hermes chat \
  --in /path/to/repo \
  --yolo \
  --oneshot \
  -Q \
  --query-file - \
  < /tmp/hms-task/brief.md \
  > /tmp/hms-task/stdout.log \
  2> /tmp/hms-task/stderr.log
```

After launch, inspect early stdout/stderr before assuming Hermes started. After completion, success means: acceptable exit code, non-empty response, no CLI usage error in logs, and `git status`/diff matches the requested scope.

## Operating Rules

- Use `--oneshot -Q` and `--query-file` (or `-q`) for implementation, repo analysis, test triage, structured answers, and second opinions.
- Use `--yolo` for autonomous tool execution so the subagent does not block waiting for TTY approval.
- Use `--in DIR` to set the primary workspace root directory.
- Use `--worktree` (`-w`) for isolated git repository execution without altering the main working tree directly.
- Use `-m MODEL` or `--provider PROVIDER` when overriding the model/provider for specialized passes (e.g. `-m anthropic/claude-sonnet-4`).
- Use `-t TOOLSETS` and `-s SKILLS` to limit or preload specific toolsets and skills for the subagent session.
- Use `--max-turns N` or `--run-budget SECONDS` for bounding multi-turn tool loops or execution time.
- Use `--resume SESSION_ID` or `-c SESSION_NAME --create-if-missing` for multi-turn iterative subagent tasks.
- Prefer foreground execution until the command is known to start cleanly. Background runs must capture stdout and stderr separately.
- Run parallel Hermes jobs only for independent chunks; reconcile overlapping edits manually.

## Failure Checks

If the output is empty or Hermes exits immediately, inspect stderr/logs first; bad flags or missing dependencies often prevent startup. If lease/lock error occurs (`OSError: [Errno 28]` or runtime lease error), clean stale leases or free disk space. If a hook or plugin warning appears, separate it from the actual run by checking exit code, stderr, final response, and repo diff.
