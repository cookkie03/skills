---
name: canvas-sync-to-obsidian
description: Synchronize Tilburg University Canvas courses, university Google Drive files (/u/1/), lecture slides, Panopto/YouTube media transcripts, and Notion workbooks into the Obsidian Second-Brain vault.
---

# Canvas Course & Google Drive Sync to Obsidian

Audit and synchronize Tilburg University Canvas courses, Google Drive files, and media recordings into the Obsidian Second-Brain vault (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/`).

---

## 1. Scope & Content Filtering

To keep the vault focused on permanent knowledge and structured coursework, apply explicit scope filtering:

### Synchronized Content (Permanent Course Knowledge)
- **Canvas Modules & Course Sections**: Full module hierarchies, content pages (`/pages/:url`), embedded notes, syllabi, assignment rubrics, and discussion resources converted to Obsidian Markdown.
- **Course Files & Slides**: Slides, lecture handouts, lab code (`.ipynb`, `.py`, `.r`), datasets (`.csv`, `.xlsx`, `.sqlite`), and documents (`.pdf`, `.docx`).
- **External Media & Links**: Panopto video recordings (`tilburguniversity.cloud.panopto.eu`), YouTube videos, and Notion workbooks.
- **Tilburg Google Drive (`/u/1/`)**: Academic and research files from the university Google account (`[EMAIL_REDACTED]`, account index `1`).

### Excluded Content (Explicit Scope Boundaries)
- **Canvas Announcements (`/announcements`)**: Announcements represent ephemeral, temporal notices rather than permanent study material. Skip automatic mirroring of announcement feeds unless the user explicitly requests an individual announcement.
- **Canvas Quizzes & Surveys (`/quizzes`)**: Interactive testing interfaces and surveys are excluded from vault generation.
- **Personal Google Drive (`/u/0/`)**: Exclude personal files (`[EMAIL_REDACTED]`). Sync operations target university workspace `/u/1/` exclusively.

---

## 2. Canvas Course Extraction Pipeline

### Step 1: Exhaustive 7-Section Traversal & Parity Audit
Recursively scan every active course visible on Canvas (`/api/v1/courses?enrollment_state=active` and dashboard). Within each course, systematically inspect all 7 core sections:

1. **Modules (`/modules?include[]=items`)**:
   - Traverse all modules, sub-modules, content items, headers, embedded pages, file attachments, and external links (`ExternalUrl`, `ExternalTool`, "Video Clips", Panopto, YouTube) in exact published sequence.
   - Click and inspect every item. If an item points to Panopto or YouTube, resolve and extract its media assets.
2. **Syllabus (`/assignments/syllabus`)**:
   - Extract course overview, exam logistics, grading breakdown, schedule, and assessment rules into a structured `<Course>/Syllabus.md`.
3. **Files & Folders (`/files`, `/folders`)**:
   - Crawl all folders and root directories for unlinked slides, datasets, code templates, and PDFs.
4. **Pages (`/pages`)**:
   - Query all published pages to capture standalone guides, wikis, or tutorials not nested in modules.
5. **Assignments (`/assignments`)**:
   - Extract project prompts, lab instructions, and grading rubrics (excluding interactive quiz types).
6. **Discussions (`/discussion_topics`)**:
   - Extract pinned Q&A threads, TA instructions, and resource-sharing posts.
7. **Panopto Video Tab (`Panopto Video` navigation item)**:
   - Check dedicated course Panopto folders for standalone recordings or playlist feeds not linked inside weekly modules.

Compare every item against `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/`. Download new files and update modified files based on remote timestamps and content hashes.

### Step 2: Canvas HTML to Obsidian Markdown
For each content page (`/pages/:url`), convert HTML into Obsidian Markdown:
- **Structure & Typography**: Headings (H1–H6), paragraphs, lists, bold (`**text**`), italics (`*text*`), and inline code (`` `code` ``).
- **Tables**: Convert `<table>` elements to standard Markdown pipe tables with header dividers.
- **Math & LaTeX**: Convert `<span class="mathjax_equation">`, `<math>`, or `\( ... \)` to standard Obsidian math:
  - Display blocks: `$$\nformula\n$$`
  - Inline: `$formula$`
  - Escape currency symbols (`\$50`, `\$1,000`) to prevent MathJax collision.
- **Wikilinks**: Map internal page/file links to Obsidian wikilinks (`[[Note Name]]`, `[[Slide.pdf]]`).

### Step 3: Local Image Asset Downloads
- Download embedded page images (`<img src="...">`, `/files/:id/preview`, `/files/:id/download`) into `<Course>/Modules/images/`.
- Replace remote image links in Markdown with local embeds (`![[image.png]]` or `![Caption](images/image.png)`) to ensure offline rendering.

---

## 3. Media Extraction & Cloud Audio Transcription

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
     -H "Authorization: Bearer ${OMNIROUTE_API_KEY}" \
     -H "Content-Type: multipart/form-data" \
     -F file="@chunk_000.mp3" \
     -F model="groq/whisper-large-v3-turbo"
   ```
4. Save the merged MP3 and the full Markdown transcript directly in the module directory:
   - Audio: `<Course>/Modules/Week N/<prefix>_merged_audio.mp3`
   - Transcript: `<Course>/Modules/Week N/<prefix>_transcript.md`

---

## 4. Google Drive Mirroring (/u/1/)

1. Access Tilburg University Google account (`/u/1/` / `[EMAIL_REDACTED]`).
2. Search folders matching course abbreviations (`IDT`, `Programming`, `PfDS`, `DM`, `DMBG`, `NLP`, `S&M`, `SM`, `GROW`, `Tesi`).
3. Download Colab/Jupyter notebooks (`.ipynb`), scripts (`.py`, `.r`), and datasets (`.csv`, `.xlsx`, `.sqlite`) into the corresponding vault course folder.
4. Update local copies when remote file modification timestamps change.

---

## 5. Notion Workbook Delegation

When a course module links to a Notion guide or workbook:
1. Apply the progressive scrolling and recursive toggle expansion pipeline defined in `notion-to-obsidian`.
2. Download all remote images locally to `<Course>/Workbooks/images/`.
3. Save converted Markdown workbooks under `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/Workbooks/`.

---

## 6. Verification & Parity Report

At the end of each synchronization pass, output an audit summary:

```markdown
### Sync Verification Summary
- **Course**: [Course Name]
- **Modules Scanned**: [N]
- **Canvas Pages Converted**: [N]
- **Files Synced / Updated**: [N]
- **Audio Processed & Transcribed**: [N]
- **Notion Workbooks Extracted**: [N]
- **Scope Verification**: Announcements and Quizzes bypassed; Google Drive /u/1/ synced.
```
