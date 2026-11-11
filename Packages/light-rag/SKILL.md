---
name: light-rag
description: >
  Manage and query local LightRAG knowledge bases (KBs) via the `ragcli` CLI.
  Trigger whenever the user mentions LightRAG, ragcli, a KB by name, or asks to query/search/ingest/create a knowledge base, even if they just say "check the wiki/vault/KB for X" or "what do we know about Y" — there is likely already a KB with the answer. ALWAYS check existing KBs before creating a new one or falling back to grep/find.
---
# LightRAG Skill

The CLI is self-documenting and evolves — don't rely on memorized flags.
Always run `ragcli -h` and `ragcli <subcommand> -h` (e.g. `ragcli kb -h`, `ragcli query -h`) to see current usage before constructing a command.

## Workflow

1. **Check what already exists before doing anything else**: `ragcli kb ls` (or `ragcli status`). If a KB already covers the topic, query it instead of re-reading source files by hand or creating a duplicate KB — that's the entire point of this tool.
2. **Query**: check `ragcli query -h` and run it non-interactively. If the target server isn't up, the relevant `server`/`status` subcommand will say so — start it the same way (check `-h` for syntax).
3. **Create/ingest**: only after step 1 finds nothing suitable. Use `ragcli kb -h` and `ragcli ingest -h` to find the right subcommands and flags.
4. **Maintenance/troubleshooting**: `ragcli <subcommand> -h` for any other operation (server lifecycle, MCP registration, resetting/moving a KB, clearing a stuck ingest pipeline, etc.) — the subcommand list from `ragcli -h` plus `-h` on each covers all of it.

Config lives in `~/Documents/lightrag-kb/config/global.env`; the KB registry (names, ports, sources, providers) is `~/Documents/lightrag-kb/registry.yaml`.
