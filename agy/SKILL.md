---
name: agy
description: "Delegate operational work to the Antigravity (`agy`) agentic CLI as a headless subagent while you orchestrate and review. Use whenever you'd otherwise spawn a subagent or grind through hands-on work yourself: scoped code edits, refactors, file/repo analysis over large context, codebase Q&A, running and triaging builds/tests, batch or parallel tasks, second opinions, or any time the user mentions agy, antigravity, or gemini as a CLI tool. agy runs real tools (reads, edits, shell) inside a scoped workspace and returns the result, so you stay the orchestrator and verify its output."
homepage: https://antigravity.google/
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
# agy — Antigravity CLI as a delegated subagent

`agy` is an **agentic** CLI: in print mode it plans, runs tools (read/edit files, shell), and returns a result. Treat it like a subagent you supervise. You stay the orchestrator — frame the task, scope its workspace, then **review what it returns**. Don't blindly trust the output; verify edits and claims before building on them.

Use it to offload work you'd otherwise do by hand or hand to a subagent: it absorbs the token-heavy operational grind (large-context reads, multi-file edits, test triage) and hands back a result.

## Core loop

```bash
agy -p "<self-contained task>"             # one-shot, prints result, exits
agy -p "<task>" --add-dir /path/to/repo   # scope its workspace to a dir
agy -p "<task>" --model "<model-name>"    # pick model (see: agy models)
cat file.md | agy -p "<task>"             # stdin is appended to the prompt
```

Print mode is non-interactive — write **complete, standalone prompts**, the way you'd brief a subagent: goal, relevant paths, constraints, and the exact output you want back. agy can't ask follow-ups.

> **Flag changed or not working?** Run `agy -h` before guessing — it's the live source of truth for all flags and their exact names.

> **Login required?** If agy responds asking for authentication, stop immediately and tell the user: "agy richiede login — esegui `agy` una volta in modo interattivo nel terminale per completare il login, poi dimmi quando sei pronto."

## Delegating effectively

- **Scope the workspace** with `--add-dir` (repeatable) so agy only sees relevant dirs — sharper results, fewer tokens. Without it the workspace is the current dir.
- **Autonomous runs**: add the skip-permissions flag (`agy -h` for the exact name) when you want agy to edit/run without prompting. Only for trusted, scoped tasks — never aim it at secrets or destructive ops you can't reverse.
- **Long tasks**: bump `--print-timeout` (e.g. `15m`) for big refactors or full test runs; default is `5m`.
- **Parallel fan-out**: launch several `agy -p` calls in the background (`&`) for independent chunks, then collect and review.
- **Multi-turn**: short flags for continue/interactive exist — run `agy -h` to confirm current names. Prefer fresh one-shots unless context must carry over.

## Picking a model

Before choosing, fetch the live list:

```bash
agy models
```

General heuristic: lighter/faster models for routine operational work (edits, lookups, summaries); heavier reasoning models for architecture decisions, tricky debugging, or when you want a cross-model second opinion. Match cost to complexity.

## What to delegate vs. keep

Delegate: bounded, well-specified work — "refactor X in `src/`", "find where Y is wired up", "run the suite and report failures", "summarize these 2k lines". Keep yourself: deciding *what* to do, stitching results together, and final review.

## Discovery

```bash
agy -h          # full flag reference (source of truth)
agy models      # available models with exact names
agy plugin -h   # plugin subcommands
agy update      # update the CLI
```

Auth/first run: if a call stalls, run `agy` once interactively to complete login.
