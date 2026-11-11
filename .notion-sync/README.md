# GitHub → Notion Skills mirror

GitHub is the source of truth. The scheduled workflow refreshes configured third-party snapshots, then mirrors every personal and configured third-party skill into the native Notion Skills database.

## Behaviour

- Personal skills are discovered as top-level directories containing `SKILL.md`.
- Third-party sources are configured in `sources.json` and copied below their dedicated `third_party/<owner>/<repo>/` directory.
- Skill body, Name, Description, source, category, repository path, GitHub URL, and supporting files are mirrored.
- Supporting files are attached as one ZIP in Notion's Files property, preserving relative paths.
- Folder moves preserve page identity when the skill folder name stays the same.
- Removed repository skills are moved to Notion Trash. Only pages with this syncer's `Sync ID` are managed.
- Direct Notion edits are overwritten on the next sync.

## Configuration

Edit `sources.json` to control the selected paths. The current path inventory and add/remove instructions are in [SOURCES.md](./SOURCES.md).

- `include` selects one skill directory or a category directory containing skill directories.
- `exclude_skill_paths` omits individual skills, using paths relative to the source's `destination`.
- Removing a source object removes its managed `third_party/` destination on the next successful refresh and moves its Notion pages to Trash.
- Personal skills are discovered automatically in top-level folders containing `SKILL.md` or `skill.md`.

Each upstream uses a dedicated destination directory. That destination is a generated mirror and is replaced on every upstream refresh. Do not edit it manually.

## Required GitHub secret

Repository secret: `NOTION_API_TOKEN`.

The database IDs are configured in the workflow file. The Notion integration must be shared with the Skills database and have read, insert, and update content capabilities.

## Schedule

The workflow runs hourly and after pushes to `main`. It can also be run manually from the Actions tab.
