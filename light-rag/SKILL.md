---
name: light-rag
description: >
  Manage and query LightRAG knowledge bases (KBs) via the `lightrag-kb` toolchain.
  Trigger when user mentions: LightRAG, ragcli, query/ingest/create KB, local OCR RAG.
---

# LightRAG Skill

## 1. Paths & Execution (Direct Access - DO NOT run search or find commands)
- **Root Directory**: `~/Documents/lightrag-kb` (check here first; do not run search or grep to find it).
- **CLI Executable**: Run `ragcli` directly if in PATH, or run `~/Documents/lightrag-kb/bin/ragcli`.
- **Config & Registry**: `~/Documents/lightrag-kb/config/global.env` and `~/Documents/lightrag-kb/registry.yaml`.

## 2. Command Reference

| Action | Command |
|---|---|
| List KBs & Status | `ragcli list` |
| Status Summary | `ragcli status` |
| Create KB | `ragcli create <name> <src_folder> [--port N] [--ocr mineru\|glmocr] [--provider ollama\|openrouter]` |
| Ingest folder | `ragcli ingest <name> [--force]` |
| Server Control | `ragcli start\|stop\|restart <name\|all>` |
| Register MCP | `ragcli mcp-add <name>` |
| Rebuild `.env` | `ragcli regen <name\|all>` (run after registry or global config edits) |

## 3. Querying & MCP
- **MCP Server Tool**: If registered, query using the `lightrag-<name>/query` tool.
- **Direct Query API**: `POST http://127.0.0.1:<port>/query` with `{"query": "question", "mode": "mix"}`.
- **Query Modes**: `mix` (default, vector+graph), `local` (detailed facts), `global` (overviews), `naive` (vector-only).

## 4. Troubleshooting
- **Server Down**: If status is down, start it: `ragcli start <name>`.
- **OpenRouter Embedding Error**: Add `EMBEDDING_USE_BASE64=false` to `kb/<kb_name>/.env` and run `ragcli restart <kb_name>`.
- **Logs**: View logs under `/tmp/lightrag-<name>.log` or `kb/<name>/lightrag.log`.
