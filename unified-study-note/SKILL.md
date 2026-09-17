---
name: unified-study-note
description: Synthesize slides, audio transcripts, lab code, and quizzes into an Obsidian master study note. Use when compiling, merging, or updating university course master notes.
---

# Unified Study Note Generator

Converts raw multi-source course materials (slides, workbooks, transcripts, practice scripts, quizzes) into a single, deduplicated, concept-centric Obsidian master note (`<Course Name>.md`).

Every source across the entire course directory tree is ingested as an authoritative input and synthesized into an exhaustive, fully self-contained study guide.

---

## Core Rules

1. **Single Master Note**: All course knowledge unifies into `<Course Name>.md` at `/Second-Brain/learning/tilburg-university/<Course Name>/`.
2. **Recursive Course Coverage**: Every single file across all folders and subfolders (`Modules/`, `Practical/`, `Canvas/`, `Materials/`, `Extended Tutorials/`, `Syllabus/`, etc.) must be evaluated and ingested.
3. **Topical Deduplication & Co-Location**: Group knowledge strictly by concept (`### <Topic>`). When a topic reappears across lectures or labs, fuse details directly into the existing section with inline citations (`[[<source-file>]]`). Avoid disconnected slide-by-slide summaries.
4. **100% Source Exhaustiveness & Lossless Reorganization**: Do not drop any bullet points, variables, or definitions present in the payload. Group, sequence, and deduplicate information, but NEVER summarize or omit details. The goal is a definitive, exhaustive university manual.
5. **Textual Self-Sufficiency**: The prose must be 100% self-contained. Explain all definitions, causal mechanisms, mathematical parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive anchors.
6. **Uniform Taxonomy**: Pair LaTeX formulas with parameter breakdown tables, verbatim code fences with line-by-line commentary, and dedicated callouts for exam traps and practical quiz questions.
7. **Visual Integration**: Never drop image placeholders (`![[...]]`) like slide snippets, diagrams, tables, or RStudio plots. Retain the placeholder and write a comprehensive educational caption below it.

---

## Input Ingestion Pipeline (Recursive Diff & Dual-Track Processing)

Ingest course materials recursively across two tracks: pre-extract binary media (PDF/PPTX slides, audio) to `.staging_unified/`, and read native text/code from every format directly in-place.

### 0. Deterministic Source Diffing (Closed-Loop Ingestion Gate)
Scan the entire course folder and all nested subdirectories recursively:
```bash
python3 scripts/diff_sources.py "<course_dir>" "<note_path>"
```
- **Recursive Scan**: Visits all subfolders (`Modules/`, `Practical/`, `Canvas/`, etc.) and detects every supported format (slides, audio, code, docs, workbooks).
- **Manifest Diffing**: Compares filenames and SHA-256 hashes against the manifest (`## Complete source record` or `## Synchronized Course Assets & Inventory`) at the bottom of `<Course Name>.md`.
- **Early-Exit**: If `new_sources` and `modified_sources` are empty, report that all course materials are already fully ingested and **stop immediately** (0 LLM tokens spent).
- **Scope**: Proceed only with files identified in `new_sources` or `modified_sources`.

---

### Track A: Binary & Media Sources (Pre-Extraction to `.staging_unified/extracts/`)

1. **Slide Decks (Deterministic Text Extraction & Image Rendering)**:
   Extract full slide text and render high-resolution 150 DPI slide images:
   ```bash
   python3 scripts/extract_slides.py "<pdf_path>" -o ".staging_unified/extracts/<deck_name>_extract.md"  --images-dir ".staging_unified/images"
   ```
   - Renders all slide PNGs to `.staging_unified/images/slide-XX.png` via macOS native Swift/PDFKit (with pdftoppm fallback).
   - Generates `.staging_unified/extracts/<deck_name>_extract.md` containing slide-by-slide text paired with corresponding image links (`![[slide-XX.png]]`).

2. **Audio & Video Transcripts (OmniRoute STT)**:
   Transcribe audio recordings via OmniRoute STT (`auto/best-stt`):
   ```bash
   python3 scripts/transcribe_audio.py "<audio_path>" -o ".staging_unified/extracts/<audio_name>_transcript.md"
   ```
   - Handles long audio files automatically via 10-minute chunking.
   - Captures verbal professor explanations, exam hints, student Q&A, and technical nuances.

---

### Track B: Native Text & Code Sources (Direct In-Place Reading)

Native text and code sources do **not** need temporary staging files. Read them directly from their original disk paths:

1. **Code Notebooks & Scripts (`.ipynb`, `.R`, `.py`, `.sql`)**:
   Read code cells, exercises, and solution keys directly from their course folders. Extract code verbatim into syntax fences with line-by-line theoretical commentary.
2. **Workbooks, Notion Pages & Canvas Summaries (`.md`)**:
   Read markdown practicals and guides directly in-place, fusing theoretical background and exercise walkthroughs into target concept blocks.
3. **Personal Notes & Scratchpads**:
   Read personal notes and scratchpads in full. Resolve inline student doubts directly within topic sections (strip raw `%%` comment syntax in final output).
4. **Quizzes & Solutions**:
   Extract all quiz questions, multiple-choice options, correct solutions, and explanation rationale into `> [!tip] Slide Quiz & Practical Application` callouts.

---

## Synthesis Workflow

### 1. Pre-Read Master Note
- Open `<Course Name>.md` and inspect existing sections and Table of Contents (TOC).
- Inspect top comment directives (`%% MASTER NOTE DIRECTIVE ... %%`). Follow declared course-specific rules.

### 2. Zero-Token Staging Copy & Tagging Sub-Agent
- **Zero-Token Staging Copy**: Copy all raw materials (Track A extracts and Track B native/material files) into `.staging_unified/sources/` using OS/Python copy tools (`shutil.copy2`). **NEVER tag or write into original source files.**
- **Topic Roadmap**: Master Orchestrator establishes the target topic list (`#topic-slug`).
- **Tagging Sub-Agent**: Dispatched to scan staged files in `.staging_unified/sources/` and insert standard boundary tags around sentences, paragraphs, code fences, and formulas:
  ```markdown
  %% BLOCK-START | id:<unique_id> | ref:<source_relative_path> | tags: #topic-1, #topic-2 %%
  <Raw text / formula / code snippet>
  %% BLOCK-END %%
  ```
  - Supports **multi-tagging** (a single block can belong to multiple topic tags).

### 3. Deterministic Extraction & Zero-Token Payload Assembly
- A deterministic Python script parses tagged files in `.staging_unified/sources/`:
  - **Regex Parsing**: Matches `%% BLOCK-START ... %%` to `%% BLOCK-END %%`.
  - **Demultiplexing**: Groups extracted blocks by topic tag.
  - **Zero-Token Payload Writing**: Writes single-topic payload files to `.staging_unified/payloads/payload_<topic_slug>.md`.
  - Each extracted block retains its source citation header (`> [Source: <ref>]`).

### 4. Topic-Specialized Sub-Agents (Lossless Generation)
- Orchestrator dispatches topic-specialized sub-agents per topic (or 2-3 topic cluster).
- Sub-agents receive **ONLY** their assigned `payload_<topic_slug>.md` file (100% relevant context, zero noise).
- **CRITICAL DIRECTIVE**: Sub-agents must perform a **Lossless Reorganization**. They must not drop details, summarize out nuances, or skip bullet points.
- Sub-agents must structure the output strictly in this 5-layer format:
  1. **Narrative/Theory**: Exhaustive prose combining slide bullets, transcript intuition, and book concepts.
  2. **Math & Formulas**: LaTeX block (`$$...$$`) immediately followed by a Parameter Breakdown Table (Variable, Meaning, Domain).
  3. **Callouts (Tips/Traps)**: Isolate transcript warnings into `> [!warning] Exam Trap` and practical quizzes into `> [!tip] Slide Quiz`.
  4. **Code Implementation**: Verbatim R/Python code blocks with line-by-line comments linking code mechanics to the theory.
  5. **Visual Context**: Preserve every image placeholder (e.g., `![[slide-04.png]]`, `![[Rplot_kmeans.png]]`) from the payload and add a detailed didactic caption explaining the visual insights.
- Output saved to `.staging_unified/drafts/<topic_slug>.md`.

### 5. Master Note Merging (NEW vs DELTA Integration)
- Orchestrator integrates completed drafts into `<Course Name>.md`:
  - **NEW Topics**: Append the full properly-layered concept block.
    ```markdown
    ### <Concept Name>
    [[<source-file-1>]] · [[<source-file-2>]]
    
    <Lossless narrative combining theory, definitions, and transcript intuitions...>
    
    $$ Z = XW $$
    
    | Parameter | Mathematical Meaning | Dimension / Domain | Interpretation & Constraints |
    | :--- | :--- | :--- | :--- |
    | $X$ | Dati originali | $\mathbb{R}^{n \times p}$ | Deve essere centrato |
    
    > [!warning] Exam Trap: Standardizzazione
    > [Dettaglio dall'audio o slide su possibili errori comuni]
    
    ```R
    # Il parametro center e scale sono fondamentali
    pca_result <- prcomp(data, center = TRUE, scale. = TRUE)
    ```
    
    ![[slide-04.png]]
    *Figura: [Caption esplicativa dettagliata estratta dal testo/audio relativo]*
    ```
  - **DELTA Topics**: Surgically inject missing definitions, formulas, or code snippets inline into existing sections, appending source citations to top section headers.

---

### 6. Append Complete Source Record (Audit Manifest)
At the bottom of `<Course Name>.md`, append all newly processed sources (both Track A and Track B) to the manifest with their SHA-256 hashes (enabling future zero-token diffing):

```markdown
## Complete source record

### Source: `Modules/Module 1/Lecture1-Introduction to data mining.pdf`
- **SHA256**: `819db41f70a3118991a0c7104d49a62ee7192be43cb7ca9d63870bbbb5292c21`
- **Type**: Slide Deck Extract

### Source: `Materials/Recordings/26 09 03 S&M.m4a`
- **SHA256**: `a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e`
- **Type**: Audio Transcript

### Source: `Practical/week2/Week2_Coding.ipynb`
- **SHA256**: `6ec5dbfdc5d3989ad87e59bcf81987513d2fa112a95c5567b43a28b030fa42bc`
- **Type**: Native Code Notebook
```

---

### 7. Formatting Standards
- **LaTeX Math**: Inline math with `$...$`, multi-line blocks with `$$\n...\n$$`.
- **Currency**: Escape dollar signs as `\$1,000` or write `1,000 USD` to prevent MathJax parsing collisions.
- **Highlights**: Use ` == ` and ` = ` always with spaces around `==` for reliable Obsidian rendering.
- **Language**: Match the primary language of the course materials (English/Italian).
- **Obsidian Syntax & Edge Cases**: Refer to the `obsidian-markdown` skill for full Obsidian Flavored Markdown conventions, callouts, wikilinks, and tricky rendering behaviors.

---

### 8. Reconciliation Audit Gate & Cleanup
Run the verification script before completing the task:
```bash
python3 scripts/verify_note.py "<note_path>"
```
The audit gate verifies:
- [ ] **100% Source Exhaustiveness**: Every file detected in `diff_sources.py` is recorded in `## Complete source record`.
- [ ] **Visual Asset Integrity**: Embedded images referenced in markdown exist on disk under `images/`.
- [ ] **Navigation & TOC**: Table of contents wikilinks (`- [[#Topic]]`) resolve cleanly to document headers.
- [ ] **Fence & Tag Symmetry**: Code fences and `<details>` blocks are properly balanced and closed.
- [ ] **Formula Completeness**: Every equation has an accompanying parameter breakdown table.
- [ ] **Staging Cleanup**: Delete `.staging_unified/` once audit passes.
