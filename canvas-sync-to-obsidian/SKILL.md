---
name: "canvas-sync-to-obsidian"
description: "Synchronize Tilburg University Canvas courses (materials, announcements, read-only quizzes), university Google Drive files (/u/1/), lecture slides, Panopto/YouTube media audio streams, Notion workbooks, and external course sources into the Obsidian Second-Brain vault."
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
4. **Source-specific destinations**: Place Canvas and linked course assets under the course's established `Materials/` hierarchy. Place university Google Drive-derived assets under a separate course-level `Google Drive/` folder, preserving meaningful existing subfolders. Respect explicit user-approved exceptions and do not relocate existing personal work automatically.

---

## 2. Protected Directories & Boundaries

- **Student Personal Notes & Private Work**:
  - Never modify, overwrite, delete, or relocate the user's personal notes, master course notes (`<Course>/<Course>.md`), lecture scratchpads (`Week N - Personal Notes.md`), personal scripts, or private folders (`Lectures/`, `Workbooks/`, `Practice/`, `_Docs/`).
- **Excluded Remote Content**:
  - Personal Google Drive accounts (`/u/0/`) are excluded (`[EMAIL_REDACTED]`).

---

## 3. Differential Mirror & Parity Audit Engine

Before downloading or processing any asset, perform a differential parity check against the local course directory:

1. **Item Identity Check**:
   - Compare remote file size, modification timestamp (`updated_at`), or SHA-256 hash against existing local files.
2. **Action Matrix**:
   | State | Check | Action |
   |---|---|---|
   | **Identical** | Hash/size/timestamp matches local file | **Skip (No-op)**: Do not re-download, re-transcribe, or re-parse. |
   | **Modified** | Remote timestamp newer or content altered | Preserve personal edits and annotations. For user work, save a separately labelled version rather than overwriting. Update an unmodified source mirror only when safe. |
   | **New / Missing** | File does not exist locally | **Route to Resolved User Path**: Place into the user-confirmed or established directory. |

---

## 4. Extraction & Ingestion Pipelines

### A. Native Files & Slides
- Download course files (PDFs, notebooks, scripts, datasets) directly into the resolved user path for that week/topic.
- Decompress lab/dataset archives (`.zip`) in-place where applicable.
- **No `*_text_extract.md` generation**: Do not generate text extract markdown files during download. Pre-extraction is handled in temporary staging (`.staging_unified/`) by `unified-study-note` during study note compilation.

### B. Canvas Content Pages
- Convert Canvas pages (`/pages/:url`) to clean Obsidian Markdown (preserving headings, pipe tables, KaTeX math `$$...$$`, inline code, and escaping standalone currency `\$`).
- Download embedded page images locally and reference them via wikilinks (`![[image.png]]`).
- Deduplicate repeated links to the same Canvas page by page ID: keep one canonical local page. For Machine Learning, the shared reading page belongs at `Materials/Reading materials.md`, not once per week.

### C. Canvas Announcements (`/announcements`)
- Ingest and synchronize course announcements into the course hierarchy (e.g. `<Course>/Materials/Announcements/` or the designated module location).
- Convert announcement content into clean Obsidian Markdown with timestamps, author metadata, and links.

### D. Canvas Quizzes & Surveys (`/quizzes`) — Strict Read-Only & Zero-Attempt Rule
- Synchronize quiz solutions, descriptions, instructions, publicly visible practice questions, files named quiz, and already-submitted review feedback in **strict read-only mode**.
- **NEVER Start or Take a Quiz**: Never click "Take the Quiz", "Start Quiz", "Begin Quiz", "Resume", or submit any answers. The synchronization must NEVER consume a student quiz attempt or trigger a timed session.
- **Skip Rule**: Consider all files, but if inspecting interactive Canvas quiz pages requires clicking "Start/Take Quiz" or initiating an active attempt, **SKIP the interactive quiz page immediately** and record it in the sync summary as skipped to protect student attempts.

### E. Media Extraction (Audio Streams Only)
- Extract audio streams from Panopto / YouTube links and save `.m4a` audio in the designated course Materials folder. Preserve valid existing formats without duplicating them solely for conversion.
- Compare the extracted audio duration with the source duration, verify an audio stream with ffprobe, and remove any intermediate video after a successful extraction. A nonzero file or valid codec alone does not establish completeness.
- **No `_transcript.md` Artifact Generation**: Do not generate separate transcript markdown files in the vault. Transcription is performed on-demand in temporary staging (`.staging_unified/`) by `unified-study-note` and recorded directly into the master note's source audit record.

### F. Notion Workspaces Delegation (`notion-to-obsidian`)
- When a module item points to Notion (`notion.site`, `notion.so`), invoke the `notion-to-obsidian` skill to recursively extract pages, toggles, LaTeX math, code blocks, and all media/attachments.
- **Strict Local Assets Policy**: All Notion images and file attachments must be downloaded into a local `Attachments/` folder adjacent to the workbooks, linked via Obsidian wikilinks (`![[Pasted image ...]]` / `[[...]]`). Remote proxy image URLs (`/image/...`) are strictly prohibited.

### G. University Google Drive Mirroring (`/u/1/`)
- Access Tilburg University Google Drive (`/u/1/` / `[EMAIL_REDACTED]`).
- Compare by content hash where possible. Place new or distinct Drive-derived files under `<Course>/Google Drive/`, separate from `Materials/`; preserve existing student work and meaningful structure. Skip byte-identical copies, and do not relocate existing user files without permission.

---

## 5. Parity & Verification Summary

A resource is complete only after verifying (1) file presence, (2) content integrity and completeness, including source-duration comparison for audio, (3) the correct destination, and (4) a resolving local wikilink. Persist an inventory of pending and failed items for resumption. Report inaccessible, ambiguous, unverified, and skipped items explicitly; do not claim parity from partial checks.

At the completion of synchronization, provide an audit report:

```markdown
### Canvas Sync Verification Summary
- **Course**: [Course Name]
- **Target Path Used**: [Resolved local folder path]
- **Differential Audit Metrics**:
  - Total Items Scanned: [N]
  - Unchanged (Skipped): [N]
  - Updated In-Place: [N]
  - Newly Downloaded: [N] (Files: [N], Canvas Pages: [N], Announcements: [N], Read-Only Quizzes: [N], Media Streams: [N])
  - Quizzes Skipped (Required Active Attempt): [N]
```
