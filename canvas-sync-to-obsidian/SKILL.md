---
name: canvas-sync-to-obsidian
description: Synchronize Tilburg University Canvas courses, university Google Drive files (/u/1/), lecture slides, Panopto/YouTube media transcripts, Notion workbooks, and external course sources into the Obsidian Second-Brain vault.
---

# Canvas Course & Universal Source Sync to Obsidian

Audit and synchronize Tilburg University Canvas courses, university Google Drive files (`/u/1/`), and all nested external course sources into the Obsidian Second-Brain vault (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/`).

> **Read-Only Operation Rule**: All remote platforms (Canvas, Panopto, Google Drive, Notion, NAS) are strictly accessed in read-only mode. Never modify, upload, overwrite, or delete remote assets.

---

## 1. Scope & Strict Directory Boundaries

To ensure clear organization, prevent data overwrites, and isolate automated downloads from personal notes:

### Target Directories (Exclusively Managed by this Skill)
- `<Course>/Materials/`: **The SINGLE target container** for Canvas and ALL recursively extracted course sources (slides, Canvas pages, Notion workspaces, Panopto/YouTube media transcripts, datasets, external web documentation).
- `<Course>/Google Drive/`: **The SINGLE target container** for academic files and school PC lab work from the university Google Drive (`/u/1/` / `[EMAIL_REDACTED]`).

### Protected Directories (Strictly Out of Scope / Never Touched)
- **Ignore and never modify, inspect, or move** any other directory at `<Course>/` (e.g. `<Course>/Lectures/`, `<Course>/Workbooks/`, `<Course>/Practicals/`, `<Course>/_Docs/`, or root student notes like `<Course>/<Course>.md`).

### Excluded Content
- **Canvas Announcements (`/announcements`)** & **Quizzes (`/quizzes`)**: Ephemeral notices and interactive testing interfaces are skipped unless explicitly requested.
- **Personal Google Drive (`/u/0/`)**: Excluded (`[EMAIL_REDACTED]`).

---

## 2. Differential Mirror & Parity Audit Engine

Before downloading, converting, or writing any asset, perform a differential parity check against the local filesystem in `<Course>/Materials/` (or `<Course>/Google Drive/`):

1. **Item Identity Check**:
   - **Path & Hierarchy Resolution**: Resolve the canonical destination path inside `<Course>/Materials/` based on Canvas module/page nesting.
   - **Modification Fingerprint**: Compare remote `updated_at` / `modified_time` and file byte size / SHA-256 hash against the local file.
2. **Action Matrix**:
   | State | Check | Action |
   |---|---|---|
   | **Identical** | Hash/size/timestamp matches local file | **Skip (No-op)**: Do not re-download, re-transcribe, or re-parse. |
   | **Modified** | Remote timestamp newer or content altered | **In-Place Update**: Overwrite and update the matching file at its exact existing path. |
   | **New / Missing** | File does not exist locally | **Ingest**: Download, convert, and place into the proper hierarchical folder. |

---

## 3. Universal Recursive Chain Extraction

Canvas serves as the single hierarchical source of truth. The traversal inspects all Canvas sections (Modules, Syllabus, Pages, Files, Assignments, Discussions, Panopto):

```
Canvas Module / Page
  ├── Canvas Content (.md)
  ├── Native Attachments (.pdf, .pptx, .R, .ipynb, .csv, all formats)
  └── External Link / Tool Detected
        ├── If Notion Workspace    → Delegate to `notion-to-obsidian` skill (recursive workspace extract)
        ├── If Panopto / YouTube    → Extract audio stream + cloud STT transcript (.mp3 + _transcript.md)
        ├── If External Doc / Web   → Crawl & convert to Obsidian Markdown with local assets
        └── Target Placement       → Nest directly inside <Course>/Materials/<Module Path>/<Item Name>/
```

### A. Canvas Module & Page Hierarchy
- Every Canvas Module maps directly to `<Course>/Materials/<Module Name>/`.
- Canvas pages (`/pages/:url`) convert to standard Obsidian Markdown (headings, pipe tables, KaTeX math `$$...$$`, inline code, escaped currency `\$`).
- Embedded page images download locally to `<Course>/Materials/images/` (or `<Module>/images/`) with wikilinks (`![[image.png]]`).

### B. Notion Workspace Delegation (`notion-to-obsidian`)
When an item, syllabus link, or external tool points to Notion (`notion.site`, `notion.so`):
1. **Root Discovery**: Inspect top banner and navigation to resolve the course workspace root (e.g. Course Page, Workbooks Gallery/Database).
2. **Delegate Extraction**: Invoke the `notion-to-obsidian` skill to extract the entire Notion workspace (progressive scrolling, recursive toggle expansion, LaTeX math, code blocks, and local image downloading).
3. **Exhaustive Scope**: Extract ALL linked child pages and database entries even if Canvas links only a single landing page.
4. **Placement**: Nest the entire extracted Notion folder tree **directly at the Canvas location where the link was found** (e.g. `<Course>/Materials/Syllabus/Course Page/Workbooks/` or `<Course>/Materials/Week N/<Workbook Name>/`).

---

## 4. Media Extraction & Cloud Audio Transcription

To conserve local storage and system resources, extract audio only (no video files) and perform speech-to-text via cloud API.

### Audio Extraction Pipeline

#### Panopto Audio Stream Extraction (`tilburguniversity.cloud.panopto.eu`)
1. Obtain the delivery ID or playlist ID from the Panopto URL (`deliveryId=<ID>` or `id=<ID>`).
2. Query Panopto's DeliveryInfo endpoint to retrieve the master stream / HLS playlist:
   ```js
   // Inside aside repl or page context:
   const deliveryId = "DELIVERY_UUID";
   const infoUrl = `https://tilburguniversity.cloud.panopto.eu/Panopto/Pages/Viewer/DeliveryInfo.aspx?deliveryId=${deliveryId}&isMaster=true`;
   const res = await fetch(infoUrl);
   const data = await res.json();
   // Extract audio/video stream URL:
   const streamUrl = data.Delivery?.StreamUrl || data.Delivery?.Streams?.[0]?.StreamUrl;
   ```
3. Download and convert the audio stream to MP3 using FFmpeg:
   ```bash
   ffmpeg -i "<STREAM_URL>" -vn -acodec libmp3lame -q:a 2 "<OUTPUT_AUDIO>.mp3"
   ```

#### YouTube Audio Extraction
Extract audio via yt-dlp:
```bash
/Users/luca/.aside/runtime/bin/python3 -m yt_dlp -x --audio-format mp3 -o "%(title)s.%(ext)s" "<URL>"
```

#### Consolidation Per Canvas Link
- If a single Panopto link contains multiple clips or a playlist (`pid=...`), download all clip audio streams and merge them into one consolidated MP3 (e.g. `<prefix>_merged_audio.mp3`).
- Keep clips from different Canvas links/modules separate.

### OmniRoute Cloud STT (No Local Models)
Local transcription models consume significant memory and compute. All speech-to-text processing uses OmniRoute cloud STT:

1. Read `OMNIROUTE_API_KEY` and `OMNIROUTE_BASE_URL` from `/Users/luca/.aside/u/0/.env`.
2. Segment audio files longer than 10 minutes into 600-second chunks using FFmpeg:
   ```bash
   ffmpeg -i merged_audio.mp3 -f segment -segment_time 600 -c copy chunk_%03d.mp3
   ```
3. Transcribe each chunk via `POST ${OMNIROUTE_BASE_URL}/audio/transcriptions` with model `groq/whisper-large-v3-turbo` (or `auto/best-stt`):
   ```bash
   curl -s -X POST "${OMNIROUTE_BASE_URL}/audio/transcriptions" \
     -H "Authorization: Bearer ${OMNI...KEY}" \
     -H "Content-Type: multipart/form-data" \
     -F file="@chunk_000.mp3" \
     -F model="groq/whisper-large-v3-turbo"
   ```
4. Save the merged MP3 and the full Markdown transcript directly inside the module directory:
   - Audio: `<Course>/Materials/<Module Path>/<prefix>_merged_audio.mp3`
   - Transcript: `<Course>/Materials/<Module Path>/<prefix>_transcript.md`

---

## 5. University Google Drive Mirroring (`/u/1/`)

1. **Scope**: Access Tilburg University account (`/u/1/` / `[EMAIL_REDACTED]`).
2. **Search**: Inspect folders matching course abbreviations (`IDT`, `Programming`, `PfDS`, `DM`, `DMBG`, `NLP`, `S&M`, `SM`, `GROW`, `Tesi`).
3. **Universal Ingestion**: Download all course files found on Drive (notebooks, scripts, datasets, slides, documents, archives) exclusively into:
   ```
   <Course>/Google Drive/
   ```
4. **Differential Parity**: Apply hash/timestamp comparison (skip identical, update modified in-place). Never create arbitrary subfolders like `<Course>/Google Drive/Google Drive/`.

---

## 6. Parity & Verification Summary

At the completion of synchronization, generate a concise audit report:

```markdown
### Sync Verification Summary
- **Course**: [Course Name]
- **Target Updated**: `<Course>/Materials/` & `<Course>/Google Drive/`
- **Protected Folders Ignored**: `Lectures/`, `Workbooks/`, `Practicals/`, etc. (Untouched)
- **Differential Audit Metrics**:
  - Total Items Scanned: [N]
  - Unchanged (Skipped): [N]
  - Updated In-Place: [N]
  - Newly Ingested: [N] (Canvas Pages: [N], Notion Pages: [N], Audio Transcripts: [N])
```
