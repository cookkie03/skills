---
name: locality
description: Use Locality when the user wants to find, read, or edit connected company sources through local filesystem files.
---

# Locality

Locality projects connected company sources into the local filesystem so agents can inspect, edit, review, and safely push supported changes back through the product path.
Connected sources can include Notion, Google Docs, Google Calendar, Gmail, Linear, Slack, and Granola.

## Where to work

- Connected source files are under `/Users/luca/Library/CloudStorage/Locality/notion`.
- Read the nearest mount-local `AGENTS.md` before source-specific edits. `CLAUDE.md` is usually an alias for the same rules.
- Online-only files hydrate automatically when opened by the filesystem.

## Locality CLI workflow

- Use `loc info <path>` for mount and connector context.
- If the user asks you to connect a provider before mounting, run `loc connect <provider> --no-browser`, share the authorization URL, and ask the user to open it while you wait for verification.
- Read the nearest mount-local `AGENTS.md` before connector-specific work; it may narrow writable/read-only paths and creation rules.
- For discovery or research tasks, triage by path and title first, browse mounted directories with normal filesystem tools, then open only the most relevant Markdown files.
- If path/title triage gives no hits, narrow the scope or ask the user for a better starting point instead of relying on broad Locality search.
- If useful results are outside a user-provided path or source scope, do not read them until the user permits it; report the skipped path or result as unavailable.
- Use `loc locate <url-or-title>` for mounted Notion page or database URLs/titles.
- Edit mounted Markdown directly for writable sources.
- Use `loc status <path>` to inspect pending local changes.
- Use `loc inspect <path>` when you need a read-only remote comparison for a hydrated file.
- Use `loc diff <path>` before asking the user to review changes or before pushing.
- Use `loc mv <source> <dest>` for intentional page/file moves or renames, then inspect with `loc status <path>` or `loc diff <path>`.
- Unless the user asked you to apply edits remotely, leave edits pending for Locality review and tell the user what changed.
- If desktop Live Mode is on, safe local edits may sync automatically. Use `loc live-mode status <file>` to inspect state. Do not run routine `loc pull` or `loc push` after every edit.
- If the user asks you to sync, publish, send, update the source, or apply the edit remotely, run `loc diff <path>` first, then `loc push <path> -y` for safe plans.
- If Live Mode is paused, conflicted, or review-needed, inspect with `loc status <path>` and `loc diff <path>` before pushing.
- If push says the remote changed since last sync, run `loc pull <path>`, resolve any inline conflict markers in the Markdown, rerun `loc diff <path>`, then push again.

## Creating Notion Content

- Read `/Users/luca/Library/CloudStorage/Locality/notion/AGENTS.md` for connector-specific creation rules.
- Prefer `loc create page --title "New Page" --parent <parent-directory>` for new pages.
- Create a Notion database with `loc create database --title "Tasks" --parent <page-dir>`, edit its draft `_schema.yaml`, inspect with `loc diff <path>`, then push explicitly.
- Pages are directories; edit or create the `page.md` inside the page directory.
- To create a child page, create `parent-page/new-page/page.md`.
- New `page.md` files need YAML frontmatter with `title: "..."` and no `loc:` identity block.
- Existing files already have an `loc:` block; preserve it and edit only the body, `title`, and supported property frontmatter.
- Database rows can be created as `database/new-row/page.md` or, where supported, direct `database/new-row.md` files.

## Connector boundaries

- Notion pages are directories with `page.md`; child pages live as child directories. Preserve Locality identity frontmatter, block IDs, directives starting with `::loc{`, `_schema.yaml`, `AGENTS.md`, and `CLAUDE.md` unless explicitly asked.
- Google Docs files are writable Markdown documents. Preserve Locality frontmatter and follow the mount-local `AGENTS.md` for supported formatting.
- Calendar mounts expose drafts for new events. Create and edit Calendar drafts only through the filesystem shape described in the mount-local `AGENTS.md`, then use `loc diff <path>` and explicit push when the user asks to publish.
- Gmail mounts expose `draft/` for remote Gmail drafts and local draft creates. Leave messages in `draft/` when the user asks to draft or revise.
- Use `outbox/` only when the user explicitly asks to send now. Moving an existing draft into `outbox/` sends that draft after applying local edits.
- Create and edit Gmail outbound files only through the filesystem shape described in the mount-local `AGENTS.md`, then use `loc diff <path>` and explicit push when the user asks to send.
- Linear issue edits and Linear status moves are supported through the mounted issue files when the mount-local `AGENTS.md` says so. Inspect with `loc diff <path>` before pushing.
- Slack and Granola mounts are read-only. Do not edit, create, delete, rename, or push files there.

## MCP fallback

If your sandbox cannot run the host `loc` CLI, such as in Claude Cowork or
another isolated agent runtime, fall back to the Locality MCP tool named `loc`.
Pass the same CLI arguments as JSON `argv`, for example:

```json
{"argv":["status","/Users/luca/Library/CloudStorage/Locality/notion","--json"]}
```

Locality configures this MCP fallback automatically for supported local agents.
Prefer direct CLI execution whenever it is available.

## Suggested user prompt

```text
Use Locality to work with my connected sources under /Users/luca/Library/CloudStorage/Locality/notion. Discover context by browsing mounted folders and using normal filesystem tools. Use `loc locate <url-or-title>` only for Notion page or database URLs/titles. Edit mounted Markdown directly, use `loc status <path>` and `loc diff <path>` to inspect pending work, and leave changes pending for Locality review unless I ask you to apply them remotely. When I do, follow the nearest mount-local `AGENTS.md` and run `loc push <path> -y` for safe plans.
```
