---
name: cdx
description: "Delegate operational work to the OpenAI Codex CLI (`codex`) as a headless subagent while you orchestrate and verify. Use when the user mentions cdx, codex cli, or headless Codex, or when you need a bounded parallel/secondary Codex pass for scoped code edits, repository analysis, refactors, code review, build/test triage, batch work, structured JSON output, or a second opinion. Prefer `codex exec` for non-interactive task execution and `codex review` for review-only work."
---

# cdx - Codex CLI as a delegated subagent

`codex` is an agentic CLI. In `exec` mode it can run non-interactively, read and edit files, run shell commands, and return a final answer. Treat it like a subagent you supervise: brief it with a complete task, constrain its workspace and permissions, then verify its claims and diffs before relying on them.

Use `cdx` to offload bounded operational work you would otherwise hand to another agent: large-context repository reads, scoped edits, refactors, build/test triage, structured extraction, review passes, or independent second opinions.

## Core Loop

```bash
codex exec -C /path/to/repo "<self-contained task>"
codex exec -C /path/to/repo --add-dir /extra/path "<task that needs both roots>"
codex exec -C /path/to/repo --sandbox workspace-write "<task that may edit files>"
codex exec -C /path/to/repo --json -o /tmp/cdx-last-message.txt "<task>"
codex review --uncommitted "Focus on bugs, regressions, and missing tests."
```

Write prompts as standalone briefs. Include the goal, relevant paths, constraints, expected output, and verification requirements. `codex exec` can read instructions from stdin; when a prompt and piped stdin are both supplied, stdin is appended as a `<stdin>` block.

If a flag is uncertain, run `codex -h`, `codex exec -h`, or `codex review -h` before guessing. The installed CLI is the source of truth for exact flags.

## Delegation Rules

- Scope every run with `-C /path/to/repo`; add writable roots with `--add-dir` only when the task genuinely needs them.
- Choose `codex exec` for implementation, investigation, test triage, or structured answers.
- Choose `codex review` for review-only work. Use `--uncommitted`, `--base <branch>`, or `--commit <sha>` to make the reviewed diff explicit.
- Use `--sandbox read-only` for analysis-only passes and `--sandbox workspace-write` for bounded edits. Avoid `danger-full-access` unless the user explicitly accepts that risk.
- Use `--ask-for-approval on-request` or `on-failure` when a run may need commands outside the sandbox. Use `never` only inside a trusted external sandbox.
- Use `--search` only when live web search is necessary for the delegated task.
- Use `-m <model>` or `-p <profile>` only when there is a clear reason to override the user's Codex defaults.
- Add `--skip-git-repo-check` only for non-repository folders.
- Add `--ephemeral` for throwaway analysis that should not persist a session.

## Prompt Template

```text
You are a headless Codex subagent. Work in /path/to/repo.

Task: <specific goal>

Constraints:
- Touch only <paths>.
- Preserve existing behavior unless the task says otherwise.
- Do not commit, push, or run destructive commands.
- If blocked by auth, missing dependencies, or permissions, stop and report the exact blocker.

Verification:
- Run <specific tests/checks> if feasible.
- Report files changed, commands run, and remaining risks.
```

Keep the main agent responsible for task selection, final integration, and final user communication. Do not blindly pass a delegated result through.

## Output Capture

For automation or clean handoff, prefer explicit output files:

```bash
codex exec -C /path/to/repo -o /tmp/cdx-result.txt "<task>"
```

Use `--json` when event streams are useful for tooling or auditing. Use `--output-schema <schema.json>` when the final answer must be machine-validated JSON. After the run, read the final message or JSON, then inspect any touched files yourself.

## Parallel Fan-Out

Run multiple `codex exec` calls only for independent chunks, with separate scopes and output files. Ask each run to avoid committing and to report exact edits. Reconcile results manually; if two runs touch the same file, inspect carefully before applying or keeping both changes.

## Auth And Failure Handling

If Codex reports missing authentication, stop and tell the user to run `codex login` or open Codex interactively to complete login.

If the CLI fails because a flag changed, rerun the relevant help command and adapt to the installed version. If sandboxing blocks a necessary command, either rerun with an appropriate approval policy or ask the user before escalating risky access.

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

Useful current CLI surfaces include `exec`, `review`, `resume`, `fork`, `mcp`, `plugin`, `doctor`, `sandbox`, `cloud`, `completion`, and `update`. Confirm with local help because Codex CLI evolves quickly.
