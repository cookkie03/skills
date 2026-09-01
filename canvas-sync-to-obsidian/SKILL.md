---
name: canvas-sync-to-obsidian
description: Synchronize all Canvas courses and Tilburg University Google Drive
  ([EMAIL_REDACTED], /u/1/) to Obsidian Second-Brain, ensuring exhaustive 1-to-1
  verification of every module, file, assignment, page, media asset, and Notion
  workbook.
---
# Canvas Course & Google Drive Sync to Obsidian

Use this skill to perform a comprehensive, 1-to-1 audit and synchronization of all Tilburg University Canvas courses, course Notion workbooks, and the user's Tilburg University Google Drive (`[EMAIL_REDACTED]`, `/u/1/`) into the Obsidian Second-Brain vault at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/`.

## Mandatory Requirements & Architecture

### 1. Exhaustive 1-to-1 Extraction Across All Canvas Courses & Sections (Full-Depth Audit)
- **Every Active Course**: Recursively scan **every single active course** visible to the user on Canvas (via `/api/v1/courses?enrollment_state=active` and the Canvas Dashboard/Courses menu). No course may be skipped.
- **Every Section Inside Every Course (MANDATORY SECTION-BY-SECTION AUDIT)**:
  Inside **every** course, systematically inspect and audit **all navigation sections and tabs**:
  1. **Modules** (`/modules?include[]=items`):
     - Traverse all modules, sub-modules, content items, headers, embedded pages, file attachments, and **every external link/tool** (`ExternalUrl`, `ExternalTool`, "Video Clips", Panopto, YouTube) in their exact published sequence.
     - **Click and open every item without exception**: If an item is an external URL pointing to Panopto (`tilburguniversity.cloud.panopto.eu`), YouTube, or another external service, follow the link, inspect the contents (e.g. all playlist clips), and extract all media assets.
  2. **Syllabus** (`/assignments/syllabus` / syllabus page):
     - Extract course overview, exam logistics, grading breakdown, required literature, schedule, and assessment rules.
  3. **Files** (`/files` & `/folders`):
     - Recursively crawl all file folders and root directories. Check for slides, lab handbooks, datasets (`.csv`, `.xlsx`, `.sqlite`), code templates (`.py`, `.ipynb`, `.r`), and `.pdf` documents that may not be linked inside modules.
  4. **Pages** (`/pages`):
     - Query all published pages to catch standalone guides, tutorials, or reference wikis not nested inside the modules list.
  5. **Assignments** (`/assignments`):
     - Extract project prompts, lab assignment instructions, submission guidelines, and grading rubrics (excluding native quizzes).
  6. **Discussions** (`/discussion_topics`):
     - Inspect pinned Q&A threads, TA instructions, and resource-sharing posts.
  7. **Panopto Video / External Tools** (Navigation menu tabs):
     - Check dedicated course video folders (`Panopto Video` tab) and external tool integrations for unlinked recordings or playlists.
- **Historical & Complete Depth**:
  - Do NOT restrict checks to new or recently modified items. Verify that historical materials from earlier weeks, past blocks, or completed modules are fully preserved and accounted for in the vault.
- **1-to-1 Obsidian Vault Matching Audit**:
  - Compare every item on Canvas against the target Obsidian vault directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/`).
  - If any item is missing or incomplete in the vault, immediately download, format, and save it to establish 100% parity.

### 2. Full Page Content Extraction & 1-to-1 Markdown Conversion
- **Canvas HTML to Obsidian Markdown**: For every content page on Canvas (`/pages/:url`), fetch the complete raw HTML body and convert it faithfully into Obsidian Markdown:
  - **Headings & Structure**: Preserve exact heading levels (H1–H6), paragraphs, line breaks, and thematic breaks (`---`).
  - **Formatting**: Preserve bold (`**text**`), italics (`*text*`), underline (`<u>text</u>`), strikethrough (`~~text~~`), inline code (`` `code` ``), and blockquotes.
  - **Tables**: Convert HTML tables (`<table>`, `<tr>`, `<th>`, `<td>`) into standard Markdown pipe tables with headers.
  - **Lists**: Convert unordered (`<ul>`) and ordered (`<ol>`) lists, preserving nested indentation.
  - **Math & LaTeX**: Detect Canvas MathJax/LaTeX equations (`<span class="mathjax_equation">`, `<math>`, or `\( ... \)` / `\[ ... \]`) and convert them to standard Obsidian LaTeX:
    - Multiline display equations: `$$\nformula\n$$`
    - Inline equations: `$formula$`
    - Escape standalone currency dollar signs (e.g. `\$1,000`, `\$50`) to prevent broken math rendering.
  - **Links**: Convert Canvas internal page/file links to relative Obsidian wikilinks (`[[Target Note]]`, `[[Target File.pdf]]`) where appropriate.

### 3. Local Image Download & Embedded Asset Rendering (CRITICAL)
- **Preserve Every Image**: When Canvas content pages contain embedded images (`<img src="...">`, `/files/:id/preview`, `/files/:id/download`, or external URLs):
  - **Download all image files locally** into the course asset directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/Modules/images/` or `images/`).
  - Name image files cleanly based on page context and original filename (e.g. `module2-figure1.png`).
  - Replace remote Canvas image links in the Markdown note with local Obsidian image embeds:
    ```markdown
    ![[image-name.png]]
    ```
    or standard relative Markdown embeds `![Caption](images/image-name.png)`.
  - Ensure zero broken image links so all figures, diagrams, and illustrations render completely offline in Obsidian.

### 4. Incremental Synchronization & Updating Modified Files
- **File Update & Parity Policy**:
  - For every file (`.pdf`, `.ipynb`, `.py`, `.r`, `.csv`, `.xlsx`, `.zip`, `.docx`, etc.) hosted on Canvas or Google Drive:
    - **New Files**: Download immediately and place in the designated folder (`<Course Directory>/Modules/`, `Workbooks/`, ...).
    - **Modified Files**: Check the Canvas `updated_at` timestamp, file size, or hash/content diff against the local file. If an updated version is detected on Canvas, overwrite/update the local copy to keep lecture slides, lab materials, and syllabi strictly up to date.
    - **Preserve User Additions**: Never delete local notes or files created by the user during synchronization passes.

### 5. Notion Workbook Extraction (Skill Delegation to notion-to-obsidian)
- Whenever a Notion workbook, guide, or page link is encountered (e.g. `Programming for Data Science` workbooks or `Data Mining` practical guides):
  - **Delegate extraction entirely to the `notion-to-obsidian` skill** (`/Users/luca/.aside/u/0/skills/user/notion-to-obsidian/SKILL.md`).
  - Follow the mandatory progressive scrolling (~600–800px step) and recursive toggle expansion pipeline defined in `notion-to-obsidian`.
  - Download all remote images locally into the course workbook images directory.
  - Save extracted workbooks under `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/Workbooks/`.

### 6. Google Drive Inspection & Semantic Mirroring (STRICT: /u/1/ ONLY)
- **Account Identification**: Exclusively access the user's Tilburg University Google account (`[EMAIL_REDACTED]`, account index `1` in `googleAccounts`, `/u/1/`).
- **Strict Personal Account Exclusion**: NEVER inspect, crawl, or mirror the user's personal Google account (`/u/0/` / `[EMAIL_REDACTED]`).
- **Flexible Hierarchy Interpretation**: Google Drive folders (`Colab Notebooks/`, `Colab Notebooks/Tesi/`, `Google AI Studio/`, course-named folders, root Drive, or "Shared with me") do not adhere to a rigid naming convention. Inspect and interpret the content, topic, file type, and purpose of every item matching course keywords (`IDT`, `Programming`, `PfDS`, `DM`, `DMBG`, `NLP`, `S&M`, `SM`, `GROW`, `Tesi`).
- **Semantic Mirroring to Obsidian**:
  - Identify new files, modified existing files (checking modification timestamps / content diffs), and unmirrored historical files.
  - Map them into their appropriate semantic home in the Obsidian Second-Brain vault (e.g. `<Course Directory>/Workbooks/`, `<Course Directory>/Modules/`, or project/thesis directories).
  - Convert Google Colab / Jupyter notebooks (`.ipynb`), `.py`, `.r`, datasets (`.csv`, `.xlsx`, `.sqlite`), and documents into clean local notes or native assets.

### 7. Media Processing Policy (Panopto & YouTube) - Audio Extraction, Merging & OmniRoute STT
- Whenever a Panopto video (`tilburguniversity.cloud.panopto.eu`) or YouTube video (`youtube.com`, `youtu.be`) link is encountered in any module, item, page, or lecture post:
  - **Do NOT save video files** (extract audio only).
  - **Panopto Playlist & Multi-Clip Handling**:
    - If a Panopto link is a playlist (`pid=...`) or contains multiple video clips, resolve and download the audio for **all individual video clips inside that specific playlist/link**.
    - **Merge rule (CRITICAL)**: Merge all audio clips from that single Panopto link/playlist into one single consolidated `.mp3` file (e.g. `02design_missing_merged_audio.mp3` or `02slr_merged_audio.mp3`).
    - **Isolation rule**: NEVER merge clips across different Canvas links, different modules, or different weeks. Each Canvas item/link produces its own standalone merged audio and transcript.
  - **Extract Audio**:
    - *Panopto*: Fetch authenticated stream via `DeliveryInfo.aspx` (`deliveryId=<ID>&isMaster=true`) or plain HLS variant URLs, download `fragmented.mp4` / audio stream via `ffmpeg` / `curl`, and convert to MP3.
    - *YouTube*: Extract audio via `yt-dlp` (`/Users/luca/.aside/runtime/bin/python3 -m yt_dlp -x --audio-format mp3 <URL>`).
  - **STT Transcription Policy (STRICT - NO LOCAL WHISPER)**:
    - **NEVER use Whisper local** (`whisper.cpp`, `OpenWhispr.app`, local `.bin` models).
    - **ALWAYS use OmniRoute STT**: Read `OMNIROUTE_API_KEY` and `OMNIROUTE_BASE_URL` from `/Users/luca/.aside/u/0/.env` (or fallback to `models.json`). Access the OpenAI-compatible audio transcription endpoint (`POST ${OMNIROUTE_BASE_URL}/audio/transcriptions`) using `groq/whisper-large-v3-turbo` (or `auto/best-stt`).
    - Split long merged audio files into ~10-minute segments (600s) with `ffmpeg -f segment` before transcribing to respect API payload limits, then concatenate the resulting transcript text.
  - **Keep Local Copies in Materials Folder (CRITICAL)**:
    - **Keep a permanent copy of the merged audio `.mp3`** directly inside the module/materials folder in Obsidian (e.g. `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/Modules/Week N/<prefix>_merged_audio.mp3`).
    - **Keep the full Markdown transcript `.md`** in the same folder (e.g. `<prefix>_transcript.md`) structured with a table of contents, segment timestamps, and complete verbatim text.
    - Clean up temporary chunk files after merging and transcription.

### 8. Exclusion Policy (Announcements & Quizzes - STRICT EXCLUSIONS)
- **ALWAYS SKIP / IGNORE ALL ANNOUNCEMENTS**: Whenever Canvas announcements (`/announcements`, announcement feeds, or announcement posts) are encountered, ALWAYS skip and ignore them completely. Do NOT download, export, parse, or mirror announcements into the vault.
- **ALWAYS SKIP / IGNORE ALL QUIZZES**: Whenever Canvas quizzes (native `/quizzes` endpoints, Canvas assignments of type quiz, or embedded interactive quizzes/surveys) are encountered, ALWAYS skip and ignore them completely. Do NOT download, export, parse, or generate notes for quizzes automatically.
- **Explicit User Request Exception**: Sync an individual announcement or quiz ONLY if the user explicitly requests it in a session.

### 9. Obsidian Markdown Formatting Standards (Skill Reference: obsidian-markdown)
- When generating, updating, or formatting notes, strictly follow the Obsidian Flavored Markdown standards defined in the `obsidian-markdown` skill (`/Users/luca/.aside/u/0/skills/user/obsidian-markdown/SKILL.md`).
- Adhere to YAML frontmatter properties, wikilinks (`[[Note Name]]`, `[[#Heading]]`), asset embeds (`![[embed]]`), callouts (`> [!note]`, `> [!warning]`), highlights (`==text==`), private comments (`%%comment%%`), and LaTeX math blocks (`$$\n...\n$$`).
