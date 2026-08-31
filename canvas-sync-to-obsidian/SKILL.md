---
name: "canvas-sync-to-obsidian"
description: "Synchronize all Canvas courses and Tilburg University Google Drive (l.putelli@tilburguniversity.edu, /u/1/) to Obsidian Second-Brain, ensuring exhaustive 1-to-1 verification of every module, file, assignment, page, media asset, and Notion workbook."
---

# Canvas Course & Google Drive Sync to Obsidian

Use this skill to perform a comprehensive, 1-to-1 audit and synchronization of all Tilburg University Canvas courses, course Notion workbooks, and the user's Tilburg University Google Drive (`l.putelli@tilburguniversity.edu`, `/u/1/`) into the Obsidian Second-Brain vault at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/`.

## Mandatory Requirements

### 1. Exhaustive Historical & Current Verification (Full-Depth Audit)
- **Every Section & Module**: At every sync pass, recursively scan **every section, module, sub-module, file, assignment, discussion, and content page** across **all active Canvas courses** (strictly skipping announcements and quizzes).
- **Canvas API Endpoints**: Query `/modules`, `/files`, `/discussion_topics`, and `/pages` across all sections. Do NOT query or sync `/announcements` or `/quizzes`.
- **Include Old/Historical Materials**: Do NOT restrict checks to new or recently modified items. Verify that older materials from earlier weeks, previous blocks, or past modules are completely preserved in the vault.
- **1-to-1 Second-Brain Matching Audit**:
  - Compare every item found on Canvas against the target Obsidian vault directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/`).
  - If any item (regardless of age or upload date) is missing or incomplete in the vault, immediately download, format, and save it to establish 100% parity.

### 2. Monitored Active Courses & Vault Mappings
1. **Interactive Data Transformation** (`320099-M-6`, Course ID: `21939`, prefix: `IDT`)
   - Path: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Interactive Data Transformation/Interactive Data Transformation.md`
2. **Natural Language Processing** (`880268-M-6` / `880221-M-6`, Course ID: `23277`, prefix: `NLP`)
   - Path: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Natural Language Processing/Natural Language Processing.md`
3. **Data Mining for Business and Governance** (`880267-M-5`, Course ID: `22823`, prefix: `DM` / `DMBG`)
   - Path: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Data Mining/Data Mining.md`
4. **Programming for Data Science** (`880271-M-6` / `880272-M-5`, Course ID: `22866`, prefix: `PfDS` / `Programming`)
   - Path: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Programming for Data Science/Programming for Data Science.md`
5. **Statistics and Methodology** (`880270-M-5`, Course ID: `24011`, prefix: `S&M` / `SM`)
   - Path: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Statistics and Methodology/Statistics and Methodology.md`
6. **Support & Degree Courses**:
   - **GROW M DSS** (`23020`, prefix: `GROW`) -> `/Users/luca/Documents/Second-Brain/learning/tilburg-university/Grow/Grow.md`
   - **MSc DSS General Program Information** (`4130`)

### 3. Notion Workbook Extraction (Skill Delegation to notion-to-obsidian)
- Whenever a Notion workbook, guide, or page link is encountered (e.g. `Programming for Data Science` workbooks Py1–Py7S and R1–R7, or `Data Mining` practical guides):
  - **Delegate extraction entirely to the `notion-to-obsidian` skill** (`/Users/luca/.aside/u/0/skills/user/notion-to-obsidian/SKILL.md`).
  - Follow the mandatory progressive scrolling (~800px step) and recursive toggle expansion pipeline defined in `notion-to-obsidian`.
  - Save extracted workbooks under `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/Workbooks/`.
  - Link extracted workbooks directly from the unified course master note (`<Course Name>.md`).

### 4. Google Drive Inspection & Semantic Mirroring (STRICT: /u/1/ ONLY)
- **Account Identification**: Exclusively access the user's Tilburg University Google account (`l.putelli@tilburguniversity.edu`, account index `1` in `googleAccounts`, `/u/1/`).
- **Strict Personal Account Exclusion**: NEVER inspect, crawl, or mirror the user's personal Google account (`/u/0/` / `luca.putelli99@gmail.com`).
- **Flexible Hierarchy Interpretation**: Google Drive folders (`Colab Notebooks/`, `Colab Notebooks/Tesi/`, `Google AI Studio/`, course-named folders, root Drive, or "Shared with me") do not adhere to a rigid naming convention. Inspect and interpret the content, topic, file type, and purpose of every item matching course keywords (`IDT`, `Programming`, `PfDS`, `DM`, `DMBG`, `NLP`, `S&M`, `SM`, `GROW`, `Tesi`).
- **Semantic Mirroring to Obsidian**:
  - Identify new files, modified existing files (checking modification timestamps / content diffs), and unmirrored historical files.
  - Map them into their appropriate semantic home in the Obsidian Second-Brain vault (e.g. `<Course Directory>/Workbooks/`, `<Course Directory>/Modules/`, or project/thesis directories).
  - Convert Google Colab / Jupyter notebooks (`.ipynb`), `.py`, `.r`, datasets (`.csv`, `.xlsx`, `.sqlite`), and documents into clean local notes or native assets.

### 5. Media Processing Policy (Panopto & YouTube) - OmniRoute STT via Aside .env
- Whenever a Panopto video (`tilburguniversity.cloud.panopto.eu`) or YouTube video (`youtube.com`, `youtu.be`) is encountered in any module, page, or lecture post:
  - **Do NOT save video files**.
  - **Extract Audio Only**:
    - *Panopto*: Fetch authenticated direct audio stream via `DeliveryInfo.aspx` (`deliveryId=<ID>&isMaster=true`) or use `yt-dlp` (`/Users/luca/.aside/runtime/bin/python3 -m yt_dlp -x --audio-format mp3`).
    - *YouTube*: Extract audio via `yt-dlp` (`/Users/luca/.aside/runtime/bin/python3 -m yt_dlp -x --audio-format mp3 <URL>`).
  - **STT Transcription Policy (STRICT - NO LOCAL WHISPER)**:
    - **NEVER use Whisper local** (`whisper.cpp`, `OpenWhispr.app`, local `.bin` models).
    - **ALWAYS use OmniRoute STT**: Read `OMNIROUTE_API_KEY` and `OMNIROUTE_BASE_URL` from `/Users/luca/.aside/u/0/.env` (or fallback to `models.json` under `providers.omniroute.apiKey`). Access the model `auto/best-stt` via the OpenAI-compatible audio transcription endpoint (`POST ${OMNIROUTE_BASE_URL}/audio/transcriptions`).
  - **Save & Merge Transcript**:
    - Format the transcribed audio and merge the resulting lecture summary directly into the course's single unified note (`<Course Name>.md`) under the relevant week/module following the established note architecture.
  - Delete temporary audio files after transcription completes.

### 6. Exclusion Policy (Announcements & Quizzes - STRICT EXCLUSIONS)
- **ALWAYS SKIP / IGNORE ALL ANNOUNCEMENTS**: Whenever Canvas announcements (`/announcements`, announcement feeds, or announcement posts) are encountered, ALWAYS skip and ignore them completely. Do NOT download, export, parse, or mirror announcements into the vault.
- **ALWAYS SKIP / IGNORE ALL QUIZZES**: Whenever Canvas quizzes (native `/quizzes` endpoints, Canvas assignments of type quiz, or embedded interactive quizzes/surveys) are encountered, ALWAYS skip and ignore them completely. Do NOT download, export, parse, or generate notes for quizzes automatically.
- **Explicit User Request Exception**: Sync an individual announcement or quiz ONLY if the user explicitly requests it in a session.

### 7. Single Unified Master Note Architecture & Non-Destructive Update Rule (CRITICAL)
- **Strict Single-Note Rule**: Every course in `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/` has **EXACTLY ONE single master markdown file**:
  - `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Directory>/<Course Name>.md`
- **NO Scattered / Duplicate Notes**:
  - NEVER create separate `Notes - <Course>.md`, `Week N - Notes.md`, `Lecture N - Notes.md`, `Week N - <Course>.md`, `Announcements.md`, or separate syllabus files.
- **Strict Non-Destructive Update & Architecture Preservation Rule**:
  - **NEVER delete, overwrite, wipe, or truncate existing content or sections** inside `<Course Name>.md`.
  - **Preserve User Annotations**: If the user has added personal notes, scratchpad remarks, study comments, custom callouts, or annotations to the master file, keep all of them intact.
  - **Follow the Existing Architecture**: Inspect the existing note layout (headers, callouts, formatting style, Table of Contents). Integrate newly discovered materials, slide references, and lecture summaries into the existing structure according to the note's established architecture.
- **Course Folder Layout**:
  - `<Course Directory>/<Course Name>.md` (Single Authoritative Note)
  - `<Course Directory>/Workbooks/` (Notion workbooks & Jupyter `.ipynb` notebooks)
  - `<Course Directory>/Modules/` (Raw slides `.pdf`, datasets `.csv`/`.sqlite`, lab packages `.zip`)

### 8. Obsidian Markdown Formatting Standards (Skill Reference: obsidian-markdown)
- When generating, updating, or formatting notes, strictly follow the Obsidian Flavored Markdown standards defined in the `obsidian-markdown` skill (`/Users/luca/.aside/u/0/skills/user/obsidian-markdown/SKILL.md`).
- Adhere to YAML frontmatter properties, wikilinks (`[[Note Name]]`, `[[#Heading]]`), asset embeds (`![[embed]]`), callouts (`> [!note]`, `> [!warning]`), highlights (`==text==`), private comments (`%%comment%%`), and LaTeX math blocks (`$$\n...\n$$`).
