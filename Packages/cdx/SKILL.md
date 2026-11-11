---
name: cdx
description: "Delegate operational work to the OpenAI Codex CLI (`codex`) as a headless subagent while you orchestrate and verify. Use when the user mentions /cdx, cdx, codex cli, headless Codex, or asks you to let Codex implement/test while you supervise. Also use for bounded secondary Codex passes: scoped code edits, repository analysis, refactors, code review, build/test triage, batch work, structured JSON output, or second opinions. Prefer `codex exec` for non-interactive task execution and `codex review` for review-only work."
---

# cdx - Codex CLI as a supervised subagent

Use `codex` for bounded operational work, not for final judgment. You brief it, scope it, run it, then verify its output, logs, and diffs before reporting to the user.

## Fast Start

```bash
codex --version
codex exec -h
git -C /path/to/repo status --short

codex exec -C /path/to/repo --sandbox workspace-write -o /tmp/cdx-final.txt "<self-contained task>"
codex review --uncommitted "Focus on bugs, regressions, and missing tests."
```

Build commands from the installed help output. Top-level `codex` flags and `codex exec` flags differ; do not pass a flag to `codex exec` unless `codex exec -h` lists it. In particular, do not add `--ask-for-approval` to `codex exec`.

## Brief

Give Codex a standalone task: goal, paths, constraints, allowed scope, tests to run, and the exact report you need. Mention unrelated user changes explicitly and tell Codex not to commit, push, delete, or touch out-of-scope paths.

```text
You are a headless Codex subagent. Work in /path/to/repo.
Task: <goal>
Scope: touch only <paths>; preserve existing behavior unless requested.
Verification: run <checks> if feasible.
Report: files changed, commands run, test results, blockers, residual risks.
```

## Robust Run

For substantial work, keep brief and logs separate:

```bash
codex exec \
  -C /path/to/repo \
  --sandbox workspace-write \
  -o /tmp/cdx-task/final.txt \
  - < /tmp/cdx-task/brief.md \
  > /tmp/cdx-task/stdout.log \
  2> /tmp/cdx-task/stderr.log
```

After launch, inspect early stdout/stderr before assuming Codex started. After completion, success means: acceptable exit code, non-empty final message, no CLI usage error in logs, and `git status`/diff matches the requested scope.

## Operating Rules

- Use `codex exec` for implementation, repo analysis, test triage, structured answers, and second opinions.
- Use `codex review` for review-only work; make the diff explicit with `--uncommitted`, `--base <branch>`, or `--commit <sha>`.
- Use `-C` for the primary workspace and `--add-dir` only when extra writable roots are genuinely needed.
- Use `--sandbox read-only` for analysis and `--sandbox workspace-write` for bounded edits. Ask before `danger-full-access` or bypass flags.
- Use `--json` for event streams and `--output-schema <file>` for machine-validated final JSON.
- Use `--search`, `-m`, `-p`, `--ephemeral`, or `--skip-git-repo-check` only when listed by help and justified by the task.
- Prefer foreground execution until the command is known to start cleanly. Background runs must capture stdout, stderr, and final output separately.
- Run parallel Codex jobs only for independent chunks; reconcile overlapping edits manually.

## Failure Checks

If the final file is empty or Codex exits immediately, inspect stderr/logs first; bad flags often prevent startup. If auth fails, stop and ask the user to run `codex login` or complete an interactive Codex login. If a hook or MCP warning appears, separate it from the actual run by checking exit code, stderr, final output, and repo diff.

## Discovery

```bash
codex -h
codex exec -h
codex review -h
codex doctor
codex features
codex mcp -h
codex plugin -h
```
