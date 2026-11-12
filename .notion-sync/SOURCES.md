# Upstream skill selection

This file documents the editable selection in `sources.json`. GitHub is the source of truth; `third_party/` is a generated mirror and should not be edited manually.

## How selection works

- `include` contains paths relative to the root of the upstream repository.
- An include can point to one skill directory containing `SKILL.md` or `skill.md`, or to a category directory whose immediate child directories contain skills.
- `exclude_skill_paths` contains paths relative to that source's `destination`. Excluding a `SKILL.md` removes its complete skill directory from both the GitHub mirror and the Notion sync.
- `destination` is the dedicated local mirror path below `third_party/`. It is generated and replaced during each refresh.
- Keep all selected skills from the same upstream repository in one source entry and one destination.

## Personal skills selected automatically

Personal skills are discovered recursively in root-level skill folders and in one-level category folders. Each skill folder must contain `SKILL.md` or `skill.md`. The category folder also becomes the Notion `Category` property.

### `Wiki/`
`daily-notes/`, `wiki-artifact/`, `wiki-ingest/`, `wiki-init/`, `wiki-lint/`, `wiki-preprocess/`, `wiki-query/`, `wiki-save/`, `workspace-setup/`.

### `Packages/`
`agy/` (Antigravity CLI), `aside-browser/` (Aside Browser CLI), `caldav/`, `cdx/` (Codex CLI), `glm-ocr/`, `hms/` (Hermes CLI), `light-rag/`, `obsidian-bases-superpowers/`, `obsidian-rendering-traps/`, `spotipy/` (Spotify).

### `Education Workflow/`
`canvas-sync-to-obsidian/`, `lecture-scratchpad/`, `notion-to-obsidian/`, `unified-study-note/`.

### Standalone
`provider-privacy-analysis/` remains at the repository root because it does not fit the three groups above.

Add a new skill under one of these category folders (for example, `Packages/my-tool/SKILL.md`) or keep it as a root-level folder. Delete its folder to remove the managed Notion page. Moving an existing skill between categories preserves its Notion page identity as long as its skill-folder name stays the same.

## Current upstream selections

| Upstream repository | `include` paths (upstream-relative) | Selected skill(s) | Local mirror |
|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering`, `skills/productivity`, `skills/in-progress`, `skills/misc` | 38 skills across four categories (invalid upstream YAML in `software-factory` excluded) | `third_party/mattpocock/skills` |
| [obra/superpowers](https://github.com/obra/superpowers) | `skills` | 15 skills | `third_party/obra/superpowers` |
| [anthropics/skills](https://github.com/anthropics/skills) | `skills` | 19 skills | `third_party/anthropics/skills` |
| [obsidianmd/obsidian-skills](https://github.com/obsidianmd/obsidian-skills) | `plugins/obsidian/skills` | 7 skills | `third_party/kepano/obsidian-skills` |
| [Harmeet10000/skills](https://github.com/Harmeet10000/skills) | `skills/ai-ml/crawl4ai-skill` | `crawl4ai` | `third_party/harmeet10000/AgentNexus-LangChain-FastAPI` |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | `skills/find-skills` | `find-skills` | `third_party/vercel-labs/skills` |
| [sorty-organizer/Sorty](https://github.com/sorty-organizer/Sorty) | `.agents/skills/sorty` | `sorty` | `third_party/sorty-organizer/Sorty` |
| [Rizzo-AI-Academy/rizzo-flow](https://github.com/Rizzo-AI-Academy/rizzo-flow) | `skills/rizzo-flow` | `rizzo-flow` | `third_party/Rizzo-AI-Academy/rizzo-flow` |
| [tailscale/tailscale-skill](https://github.com/tailscale/tailscale-skill) | `skills/tailscale` | `tailscale` | `third_party/tailscale/tailscale-skill` |
| [Nebutra/MinerU-Skill](https://github.com/Nebutra/MinerU-Skill) | `.` | `mineru` (nested duplicate excluded) | `third_party/Nebutra/MinerU-Skill` |
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | `graphify` | `graphify` | `third_party/Graphify-Labs/graphify` |
| [codeflash-ai/locality](https://github.com/codeflash-ai/locality) | `apps/desktop/src-tauri/src` | Generated `locality` skill, extracted from `agent_guidance.rs` | `third_party/codeflash-ai/locality` |
| [morluto/rea](https://github.com/morluto/rea) | `.agents/skills/reverse-engineer-anything` | `reverse-engineer-anything` | `third_party/morluto/rea` |
| [claude-office-skills/skills](https://github.com/claude-office-skills/skills) | `spotify-automation` | `Spotify Automation` | `third_party/claude-office-skills/skills` |
| [paki81/qwen-tts](https://github.com/paki81/qwen-tts) | `.` | `qwen-tts` | `third_party/paki81/qwen-tts` |

| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | `skills/agent-browser` | `agent-browser` | `third_party/vercel-labs/agent-browser` |
| [vercel-labs/opensrc](https://github.com/vercel-labs/opensrc) | `skills/opensrc` | `opensrc` | `third_party/vercel-labs/opensrc` |
| [tasteskill/tasteskill](https://github.com/tasteskill/tasteskill) | `skills` | 12 skills | `third_party/tasteskill/tasteskill` |
| [mvanhorn/cli-printing-press](https://github.com/mvanhorn/cli-printing-press) | `skills` | 9 skills | `third_party/mvanhorn/cli-printing-press` |
| [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | `.` | `notebooklm-py` (root skill) | `third_party/teng-lin/notebooklm-py` |
| [trycua/cua](https://github.com/trycua/cua) | `libs/cua-driver/rust/Skills/cua-driver` | `cua-driver` (complete cross-platform pack) | `third_party/trycua/cua` |

For Locality, `extractor_file` is `apps/desktop/src-tauri/src/agent_guidance.rs`; `mount_path` controls the filesystem root rendered inside the generated skill.

## How to change the selection

### Add or remove one skill from an existing repository

Edit that source's `include` array in `sources.json`.

- Remove an exact skill-directory path to stop mirroring that skill.
- Add another exact skill-directory path to mirror it.
- A category include, such as Matt Pocock's `skills/engineering`, selects all immediate child directories that contain a skill entrypoint. To omit just one skill from a category, add its `SKILL.md` path to `exclude_skill_paths`, relative to `destination`. Example for Matt Pocock: `engineering/diagnosing-bugs/SKILL.md`.

Removing a selected skill removes its directory from the generated GitHub mirror. The Notion sync then moves the matching managed Skill page to Trash.

### Remove an entire upstream repository

Remove that source object from the `sources` array in `sources.json`. The upstream ownership manifest records configured destinations; the next successful run deletes the removed source's `third_party/` mirror and moves its managed Notion pages to Trash.

Do not leave an empty source entry. If no skill from a repository should remain, remove the whole source object.

### Add a new upstream repository

Add one source object with:

- a unique `id`;
- `label`, `repo` and `branch`;
- one or more upstream-relative skill-directory paths in `include`;
- `source_path_prefix`, the common parent used to reproduce selected paths inside the mirror;
- a unique `destination` below `third_party/`.

Keep all selected skills from the same repository in one source object and one destination.

### Add or remove a personal skill

Personal skills are detected automatically in root-level directories and in one-level category folders. Add a folder such as `Packages/my-skill/SKILL.md`, `Wiki/my-skill/SKILL.md`, or `Education Workflow/my-skill/SKILL.md` (or keep a standalone root-level folder). Deleting that skill folder removes its managed Notion page on the next sync.

## Important

- The workflow runs hourly at minute 17, after pushes to `main`, or manually from GitHub Actions.
- Do not edit files inside `third_party/` to customise a skill: they are replaced from upstream on the next refresh.
- A removed Notion page is moved to Trash, not permanently deleted.
- Only pages carrying this sync's `Sync ID` are managed; other Notion pages are left untouched.

| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `.agents/skills/impeccable` | `impeccable` | `third_party/pbakaus/impeccable` |
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | `skills/readme-blueprint-generator` | `readme-blueprint-generator` | `third_party/github/awesome-copilot` |
