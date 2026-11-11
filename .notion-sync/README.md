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

Add upstreams to `sources.json`. Each upstream uses a dedicated destination directory. That destination is a read-only mirror of the upstream and is replaced on every upstream refresh.

## Required GitHub secret

Repository secret: `NOTION_API_TOKEN`.

The database IDs are configured in the workflow file. The Notion integration must be shared with the Skills database and have read, insert, and update content capabilities.

## Schedule

The workflow runs hourly and after pushes to `main`. It can also be run manually from the Actions tab.
