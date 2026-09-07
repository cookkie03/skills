---
name: "canvas-sync-to-obsidian"
description: "Synchronize Tilburg University Canvas courses, university Google Drive files (/u/1/), lecture slides, Panopto/YouTube media transcripts, Notion workbooks, and external course sources into the Obsidian Second-Brain vault."
---

# Canvas Course & Universal Source Sync to Obsidian

Audit and synchronize Tilburg University Canvas courses, university Google Drive files (`/u/1/`), and all nested external course sources into the Obsidian Second-Brain vault (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/` or CloudStorage equivalent).

> **Read-Only Remote Operation Rule**: All remote platforms (Canvas, Panopto, Google Drive, Notion, NAS) are strictly accessed in read-only mode. Never modify, upload, overwrite, or delete remote assets.

---

## 1. Respect Existing User Paths & No Arbitrary Folder Creation

1. **Adapt to User's Established Paths**:
   - Always inspect the existing directory hierarchy within the course folder before placing downloaded materials.
   - Match the exact folder patterns already established by the user (e.g. `Materials/Week N/`, `Materials/Modules/Week N/`, `Materials/Modules/Lecture N - <Topic>/`, `Modules/Chapter N/`, etc.).
2. **Never Invent or Create Folder Templates**:
   - Do not generate arbitrary new folder structures, synthetic module containers, or hardcoded path templates on your own.
3. **Ask the User When Unclear (`ask_user_question`)**:
   - If a new module, week, or asset does not match an unambiguous existing folder pattern in the course, **always ask the user where the files should be placed** before writing or downloading anything.

---

## 2. Protected Directories & Boundaries

- **Student Personal Notes & Private Work**:
  - Never modify, overwrite, delete, or relocate the user's personal notes, master course notes (`<Course>/<Course>.md`), lecture scratchpads (`Week N - Personal Notes.md`), personal scripts, or private folders (`Lectures/`, `Workbooks/`, `Practice/`, `_Docs/`).
- **Excluded Remote Content**:
  - Ephemeral notices, active quiz-taking forms, and personal Google Drive accounts (`/u/0/`) are excluded unless explicitly requested.

---

## 3. Differential Mirror & Parity Audit Engine

Before downloading or processing any asset, perform a differential parity check against the local course directory:

1. **Item Identity Check**:
   - Compare remote file size, modification timestamp (`updated_at`), or SHA-256 hash against existing local files.
2. **Action Matrix**:
   | State | Check | Action |
   |---|---|---|
   | **Identical** | Hash/size/timestamp matches local file | **Skip (No-op)**: Do not re-download, re-transcribe, or re-parse. |
   | **Modified** | Remote timestamp newer or content altered | **In-Place Update**: Overwrite and update the matching file at its existing path. |
   | **New / Missing** | File does not exist locally | **Route to Resolved User Path**: Place into the user-confirmed or established directory. |

---

## 4. Extraction & Ingestion Pipelines

### A. Native Files & Slides
- Download course files (PDFs, notebooks, scripts, datasets) directly into the resolved user path for that week/topic.
- When slide or lecture PDFs are downloaded, generate a companion `*_text_extract.md` to support study and note synthesis.
- Decompress lab/dataset archives (`.zip`) in-place where applicable.

### B. Canvas Content Pages
- Convert Canvas pages (`/pages/:url`) to clean Obsidian Markdown (preserving headings, pipe tables, KaTeX math `$$...$$`, inline code, and escaping standalone currency `\$`).
- Download embedded page images locally and reference them via wikilinks (`![[image.png]]`).

### C. Panopto & Audio Cloud Transcription
- Extract audio streams (HLS/master stream) from Panopto / YouTube links without downloading bulky video files.
- Transcribe audio chunks via OmniRoute cloud STT using model `auto/best-stt` (or `groq/whisper-large-v3-turbo`).
- Save the consolidated audio and transcript directly inside the designated user folder for that lecture/topic:
  - Audio: `<prefix>_merged_audio.mp3`
  - Transcript: `<prefix>_transcript.md`

### D. Notion Workspaces Delegation (`notion-to-obsidian`)
- When a module item points to Notion (`notion.site`, `notion.so`), invoke the `notion-to-obsidian` skill to recursively extract pages, toggles, LaTeX math, code blocks, and local image assets.

### E. University Google Drive Mirroring (`/u/1/`)
- Access Tilburg University Google Drive (`/u/1/` / `[EMAIL_REDACTED]`).
- Search for course-related files, deduplicate by content hash against existing course files, and place new items into the user's designated course structure.

---

## 5. Parity & Verification Summary

At the completion of synchronization, provide an audit report:

```markdown
### Canvas Sync Verification Summary
- **Course**: [Course Name]
- **Target Path Used**: [Resolved local folder path]
- **Differential Audit Metrics**:
  - Total Items Scanned: [N]
  - Unchanged (Skipped): [N]
  - Updated In-Place: [N]
  - Newly Downloaded: [N] (Files: [N], Canvas Pages: [N], Audio Transcripts: [N])
```

