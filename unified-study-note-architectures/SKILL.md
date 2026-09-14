---
name: unified-study-note-architectures
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
4. **100% Slide & Source Exhaustiveness**: Every bullet point, definition, formula ($$...$$), derivation, parameter interpretation, verbatim code snippet, edge case, diagram takeaway, and lecture quiz must be explicitly articulated in full prose. High-level condensations or silent omissions are unacceptable.
5. **Textual Self-Sufficiency**: The prose must be 100% self-contained. Explain all definitions, causal mechanisms, mathematical parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive anchors.
6. **Uniform Taxonomy**: Pair LaTeX formulas with parameter breakdown tables, verbatim code fences with line-by-line commentary, and dedicated callouts for exam traps and practical quiz questions.

---

## Input Ingestion Pipeline (Recursive Diff & Dual-Track Processing)

Ingest course materials recursively across two tracks: pre-extract binary media (PDF/PPTX slides, audio) to `.staging_unified/`, and read native text/code (`.ipynb`, `.R`, `.py`, `.md`) directly in-place.

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

### Track A: Binary & Media Sources (Pre-Extraction to `.staging_unified/`)

1. **Slide Decks (Deterministic Text Extraction & Image Rendering)**:
   Extract full slide text and render high-resolution 150 DPI slide images into staging:
   ```bash
   python3 scripts/extract_slides.py "<pdf_path>" -o ".staging_unified/extracts/<deck_name>_extract.md" --images-dir ".staging_unified/images"
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
- Inspect the top of the Master Study Note for note-specific comment directives (`%% MASTER NOTE DIRECTIVE ... %%`). Follow declared course-specific granularity and formatting rules. If missing, initialize it. If the user asks most of the time for a specific behaviour, map it inside the block for future runs.

### 2. Raw Inventory & Topic Roadmap
Inspect extracted files from Track A (`.staging_unified/extracts/`) and native files from Track B. Map each incoming item to a **Target Topic** (`### <Topic>`) and categorize as **`NEW`** or **`DELTA`**:
- **Prose**: Core theoretical definitions, causal mechanisms, intuitions, and formal arguments.
- **Formulas & Parameter Tables**: Mathematical statements (`$$...$$`) and parameter tables.
- **Verbatim Code & Exercises**: Full runnable scripts with line-by-line walkthroughs.
- **Exam Traps**: Common mistakes, subtle bugs, and syntax collisions (`> [!warning] Exam Trap`).
- **Quizzes**: Slide questions and step-by-step solutions (`> [!tip] Slide Quiz & Practical Application`).
- **Visuals**: Identify every slide with diagrams, plots, architecture schemas, tables, drawings, or decision workflows to carry forward into the concept blocks.

### 3. Adaptive Execution Strategy (Inline vs Macro-Batch)
The Master Orchestrator oversees the **Big Picture** (topic roadmap, TOC, and audit gate) and selects the execution strategy:

- **A. INLINE Mode (Light Update $\le 3$ topics or $< 15\text{k}$ words)**:
  - Master Orchestrator drafts concept blocks and applies delta patches directly inline (0 sub-agent overhead).

- **B. MACRO-BATCH Mode (Heavy Update $> 3$ topics or multi-module synthesis)**:
  - Orchestrator establishes the roadmap and groups topics into **2–3 logical macro-clusters**.
  - Dispatches parallel sub-agents using an explicit, isolated context prompt:
    ```text
    Goal: Draft concept blocks for cluster: [Topic Names].
    Context:
    - Track A Extracts: .staging_unified/extracts/<assigned_files>
    - Track B Native Paths: <assigned_code_or_notebook_paths>
    - Output path: .staging_unified/drafts/<topic_slug>.md
    - Standard: Follow LaTeX parameter tables, verbatim code with line-by-line commentary, [!warning] Exam Trap, and [!tip] Slide Quiz callouts.
    ```
  - Orchestrator collects completed drafts from `.staging_unified/drafts/` and integrates them into `<Course Name>.md`.

---

### 4. Build & Update Concept Blocks (NEW vs DELTA)

#### A. If Topic is NEW: Build Full Concept Block
Construct the complete high-density section:

```markdown
### <Concept Name>
[[<source-file-1>]] · [[<source-file-2>]] · [[#Related Concept]]

<Exhaustive narrative fusing slide bullets, workbook theory, and lecturer explanations into a coherent explanation.>

$$
\text{Formula}
$$

| Parameter | Mathematical Meaning | Dimension / Domain | Interpretation & Constraints |
| :--- | :--- | :--- | :--- |
| $x$ | Predictor feature vector | $\mathbb{R}^P$ | Input covariates without intercept |
| $\beta$ | Parameter coefficient vector | $\mathbb{R}^P$ | Rate of change in $y$ per unit change in $x$ |

```<language>
# Verbatim code snippet or workbook exercise solution
def execute_pipeline(data):
    # Line-by-line commentary linking code mechanics to theory
    pass
```

> [!warning] Exam Trap / Common Mistake
> Specific error identified in slides, practice quizzes, or lecture transcripts.

> [!tip] Slide Quiz & Practical Application
> Classroom exercise and solution walkthrough extracted directly from the lecture slides.

![[slide-XX.png]]
*Detailed caption articulating the visual insight and takeaway.*
```

#### B. If Topic ALREADY EXISTS: Surgical DELTA-Enrichment
Preserve existing theoretical narrative verbatim and inject only delta additions:
1. **Source Citation**: Append the new source wikilink to the header line (`[[Lab_02.R]]`).
2. **Parameter Table**: Append new parameter rows to the existing LaTeX table.
3. **Verbatim Code**: Add new practical code fences with line-by-line explanations.
4. **Exam Traps & Nuances**: Append new `> [!warning] Exam Trap` callouts for lecturer warnings or edge cases.
5. **Slide Quizzes**: Append new `> [!tip] Slide Quiz & Practical Application` callouts.
6. **Visual Embeds**: Whenever a slide contains a diagram, table, drawing, plot, architecture schema, or decision workflow, embed the image directly adjacent to the concept (`![[slide-XX.png]]`), move the referenced PNG from `.staging_unified/images/` into the course `images/` directory, and accompany with exhaustive prose explaining the visual insights.

---

### 5. Append Complete Source Record (Audit Manifest)
At the bottom of `<Course Name>.md`, append all newly processed sources (both Track A and Track B) to the manifest with their SHA-256 hashes (enabling future zero-token diffing):

```markdown
## Complete source record

### Source: `Modules/Module 1/Lecture1-Introduction to data mining.pdf`
- **SHA256**: `819db41f70a3118991a0c7104d49a62ee7192be43cb7ca9d63870bbbb5292c21`
- **Type**: Slide Deck Extract
<full extracted slide text>

### Source: `Materials/Recordings/26 09 03 S&M.m4a`
- **SHA256**: `a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e`
- **Type**: Audio Transcript
<full transcript text>

### Source: `Practical/week2/Week2_Coding.ipynb`
- **SHA256**: `6ec5dbfdc5d3989ad87e59bcf81987513d2fa112a95c5567b43a28b030fa42bc`
- **Type**: Native Code Notebook
```

---

### 6. Formatting Standards
- **LaTeX Math**: Inline math with `$...$`, multi-line blocks with `$$\n...\n$$`.
- **Currency**: Escape dollar signs as `\$1,000` or write `1,000 USD` to prevent MathJax parsing collisions.
- **Highlights**: Use ` == ` and ` = ` always with spaces around `==` for reliable Obsidian rendering.
- **Language**: Match the primary language of the course materials (English/Italian).
- **Obsidian Syntax & Edge Cases**: Refer to the `obsidian-markdown` skill for full Obsidian Flavored Markdown conventions, callouts, wikilinks, and tricky rendering behaviors.

---

### 7. Reconciliation Audit Gate & Cleanup
Run the verification script before completing the task:
```bash
python3 scripts/verify_note.py "<note_path>"
```
The audit gate verifies:
- [ ] **100% Source Accounting**: All definitions, formulas, code logic, and quiz questions from all new sources across all subfolders are fully articulated.
- [ ] **Formula Completeness**: Every equation has an accompanying parameter breakdown table.
- [ ] **Navigation & TOC**: Table of contents wikilinks (`- [[#Topic]]`) resolve cleanly to document headers.
- [ ] **Fence & Tag Symmetry**: Code fences and `<details>` blocks are properly balanced and closed.
- [ ] **Audit Trail Integrity**: All newly processed sources (Track A and Track B) are recorded in `## Complete source record` with zero truncation markers.

**Staging Cleanup**: Once the audit passes cleanly, delete `.staging_unified/` (discarding unreferenced slide images and temporary extracts, keeping the vault clean).
