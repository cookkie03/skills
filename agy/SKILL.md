---
name: agy
description: "Delegate operational work to the Antigravity (`agy`) agentic CLI as a headless subagent while you orchestrate and verify. Use whenever the user mentions agy, antigravity, or gemini as a CLI tool, or when you would otherwise spawn a subagent for scoped code edits, refactors, repository analysis, codebase Q&A, build/test triage, batch or parallel tasks, or second opinions. agy runs real tools inside a scoped workspace and returns a result; you remain responsible for review."
metadata:
  {
    "openclaw":
      {
        "emoji": "🛰️",
        "requires": { "bins": ["agy"] },
        "install":
          [
            {
              "id": "shell",
              "kind": "shell",
              "command": "agy update",
              "bins": ["agy"],
              "label": "Update Antigravity CLI",
            },
          ],
      },
  }
---

# agy - Antigravity CLI as a supervised subagent

Use `agy` for bounded operational work, not for final judgment. You brief it, scope it, run it, then verify its output, logs, and diffs before reporting to the user.

## Fast Start

```bash
agy -h
agy models
git -C /path/to/repo status --short

agy -p "<self-contained task>" --add-dir /path/to/repo
cat /tmp/agy-task/brief.md | agy -p "Execute this brief." --add-dir /path/to/repo
```

Build commands from the installed help output. `agy` flags change; confirm the exact names for autonomous execution, continuation, timeout, plugins, and model selection before using them.

## Brief

Give agy a standalone task: goal, paths, constraints, allowed scope, tests to run, and the exact report you need. Mention unrelated user changes explicitly and tell agy not to commit, push, delete, or touch out-of-scope paths.

```text
You are a headless Antigravity subagent. Work in /path/to/repo.
Task: <goal>
Scope: touch only <paths>; preserve existing behavior unless requested.
Verification: run <checks> if feasible.
Report: files changed, commands run, test results, blockers, residual risks.
```

## Robust Run

For substantial work, keep brief and logs separate:

```bash
agy -p "Execute the brief from stdin." \
  --add-dir /path/to/repo \
  < /tmp/agy-task/brief.md \
  > /tmp/agy-task/stdout.log \
  2> /tmp/agy-task/stderr.log
```

After launch, inspect early stdout/stderr before assuming agy started. After completion, success means: acceptable exit code, non-empty output, no CLI usage/auth error in logs, and `git status`/diff matches the requested scope.

## Operating Rules

- Use print mode (`-p`) for non-interactive delegation; agy cannot ask follow-ups, so the prompt must be complete.
- Use `--add-dir` to scope the workspace. Repeat it only when extra roots are genuinely needed.
- For autonomous edit/test runs, confirm the current skip-permissions flag with `agy -h`; use it only for trusted, scoped tasks.
- For long work, confirm and use the current timeout flag, commonly `--print-timeout`.
- Use `agy models` before overriding the model. Prefer defaults unless complexity or cost clearly argues otherwise.
- Prefer foreground execution until the command is known to start cleanly. Background runs must capture stdout and stderr separately.
- Run parallel agy jobs only for independent chunks; reconcile overlapping edits manually.

## Failure Checks

If output is empty or agy exits immediately, inspect stderr/logs first; bad flags often prevent startup. If auth fails, stop and tell the user: "agy richiede login: esegui `agy` una volta in modo interattivo nel terminale, poi dimmi quando sei pronto." If a plugin or environment warning appears, separate it from the actual run by checking exit code, stderr, output, and repo diff.

## Discovery

```bash
agy -h
agy models
agy plugin -h
agy update
```
