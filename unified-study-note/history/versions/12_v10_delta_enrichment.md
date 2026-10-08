---
name: unified-study-note
description: Merge raw course materials (slides PDF/PPTX, audio transcripts, personal notes, workbooks, quizzes, exercises) into a single, comprehensive, deduplicated Obsidian master study note with 100% information completeness and zero loss. Use whenever synthesizing, merging, compiling, or updating course materials, study guides, lecture slides, or recordings into Obsidian master notes.
---

# Unified Study Note Generator

Converts all raw course materials into a single, deduplicated, concept-centric master note in Obsidian. Every source (slides, workbooks, transcripts, practice scripts, quizzes) is ingested as an authoritative, first-class input and synthesized into an exhaustive, fully self-contained study guide.

## Core Rules

- **Single Master Note**: All content merges into `<Course Name>.md` at `/Second-Brain/learning/tilburg-university/<Course Name>/`. All course knowledge remains unified in this single file.
- **Topical Deduplication & Co-Location**: Group knowledge strictly by concept (`### <Topic>`). When a topic reappears across multiple slide decks, workbooks, or lecture sessions, fuse all details directly into the existing concept section with inline spot citations (`[[<source-file>]]`). Never dump disconnected slide-by-slide summaries.
- **100% Slide & Source Exhaustiveness**: Every single slide from every PDF/PPTX deck (every bullet point, definition, formula ($$...$$), derivation, parameter, verbatim code snippet, edge case, diagram takeaway, and lecture quiz) must be explicitly articulated in full in the text prose. High-level summaries, condensations, or silent omissions are strictly forbidden.
- **Textual Self-Sufficiency**: The Markdown prose must be 100% self-contained. Articulate all definitions, causal mechanisms, mathematical parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive references.
- **Uniform Taxonomy & Consistency**: Maintain uniform formatting standards across the note: LaTeX math blocks paired with parameter breakdown tables, verbatim code fences with line-by-line commentary, and dedicated callout boxes for exam traps and practical quiz questions.

---

## Input Processing & Ingestion Pipeline (Deterministic Scripts)

Before synthesis, ingest and extract all raw materials into clean plain text using zero-LLM-token deterministic Python scripts located in `scripts/`:

### 0. Deterministic Source Diffing (Skip already processed files)
Before reading any files into the LLM context, compare the course directory against the Master Note's source manifest:
```bash
python3 scripts/diff_sources.py "<course_dir>" "<note_path>"
```
Only files listed under `new_sources` or `modified_sources` proceed to extraction.

### 1. PDF / PPTX Slide Decks (Pre-Extraction & Image Rendering)
Extract slide-by-slide text and render high-resolution 150 DPI images to `images/`:
```bash
python3 scripts/extract_slides.py "<pdf_path>"
```
- Generates `<deck_name>_extract.md` with slide text and automatic image links (`![[slide-XX.png]]`).
- Renders slide images via macOS native Swift/PDFKit (with pdftoppm / fitz fallback).
- For slides containing diagrams, plots, complex architecture schemas, or decision workflows, embed slide images (`![[slide-XX.png]]`) inside the master note alongside deep prose explaining the key takeaways.

### 2. Audio & Video Transcripts (OmniRoute STT)
Transcribe recordings via OmniRoute STT (`auto/best-stt`, endpoint `POST /v1/audio/transcriptions`):
```bash
python3 scripts/transcribe_audio.py "<audio_path>"
```
- Handles long audio files via automatic 10-minute chunking.
- Extracts verbal lecturer nuances, exam tips, spoken metaphors, and student Q&A clarifications.

### 3. Personal Notes & Daily Scratchpads
Read personal notes and scratchpads in full. Resolve all inline comments or questions directly within the relevant concept section (strip raw `%%` comment syntax from final output).

### 4. Code Workbooks & Practice Scripts
Extract all code blocks, exercises, and solution scripts verbatim from `.R`, `.py`, `.ipynb`, `.sql` into syntax-highlighted fences. Pair every snippet with line-by-line explanations linking parameters to theoretical foundations.

### 5. Quizzes & Formative Tests
Extract all quiz questions, multiple-choice options, correct solutions, and explanation rationale into dedicated callout blocks (`> [!tip] Slide Quiz & Practical Application`).

---

## Synthesis Workflow

### 1. Pre-Read Master Note
- Open `<Course Name>.md` and inspect existing sections. Map all incoming topics to existing concept sections (merge) or identify new sections (insert) to maintain a clean, deduplicated concept hierarchy.
- When reading or updating an existing Master Study Note, inspect the top of the file for note-specific Obsidian comment blocks (`%% MASTER NOTE DIRECTIVE ... %%`). Follow any declared course-specific granularity, return-value breakdown rules, and formatting constraints without overwriting existing topic structures. If the block is missing, initialize it.

### 2. Comprehensive Raw Inventory & Topic Mapping
Read all extracted slide texts, transcripts, workbooks, and code files in full. Categorize every inventoried item by target **Concept Topic** (`### <Topic>`) and classify whether each topic is **NEW** or **EXISTING (DELTA)**:

- **Prose**: Core theoretical definitions, causal mechanisms, intuitions, and formal arguments.
- **Formulas & Parameter Tables**: Mathematical statements (`$$...$$`), derivations, and detailed parameter breakdown tables.
- **Verbatim Code & Exercises**: Full code scripts with line-by-line theoretical walkthroughs.
- **Exam Traps & Fallacies**: Common mistakes, subtle bugs, and syntax collisions (`> [!warning] Exam Trap`).
- **Classroom Quizzes & Practice**: Slide questions and step-by-step solutions (`> [!tip] Slide Quiz & Practical Application`).
- **Visuals**: Diagram, Tables, Images inside slides embeds (`![[slide-XX.png]]`) paired with exhaustive analytical commentary.

### 3. Build & Update Concept Blocks (NEW vs DELTA-Enrichment)

#### A. If Topic is NEW: Build Full Concept Block
For topics not yet present in the Master Note, construct the complete high-density section:

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
> Specific error identified in slides, practice quizzes, or lecture transcripts (e.g., factor-to-numeric coercion trap in R, VS Code REPL terminal collision in Python).

> [!tip] Slide Quiz & Practical Application
> Classroom exercise and solution walkthrough extracted directly from the lecture slides.

![[slide-XX.png]]
*Detailed caption articulating the visual insight and takeaway.*
```

#### B. If Topic ALREADY EXISTS: Surgical DELTA-Enrichment
Do **not** rewrite, summarize, or overwrite existing theoretical explanations. Apply surgical patch updates to the existing `### <Topic>` section:
1. **Source Link Update**: Append the new source wikilink to the header line (e.g., `[[Lab_02.R]]`).
2. **Parameter Table**: Add new parameter/hyperparameter rows to the existing LaTeX table if introduced in the new source.
3. **Verbatim Code**: Insert new code fences for lab exercises with accompanying line-by-line explanations.
4. **Exam Traps & Nuances**: Append new `> [!warning] Exam Trap` callouts for newly identified pitfalls or verbal lecturer warnings.
5. **Slide Quizzes**: Append new `> [!tip] Slide Quiz & Practical Application` callouts.
6. **Visual Embeds**: Add `![[slide-XX.png]]` with analytical captions for newly introduced charts or decision diagrams.

Rules:
- **Bold** key technical terms on first mention.
- Use Markdown tables for parameter breakdowns, feature matrices, and language comparisons (e.g., Python vs R).
- Use numbered lists for sequential derivations, algorithms, and decision rules.
- Maintain consistent callouts (`> [!note]`, `> [!warning]`, `> [!tip]`, `> [!important]`).
- Place visual embeds immediately adjacent to the concept they illustrate.

### 4. Append Complete Source Record (Audit Manifest)
At the bottom of `<Course Name>.md`, maintain the complete, un-truncated audit trail of all ingested sources with their SHA-256 hashes:

```markdown
## Complete source record

### Source: `Lecture1-Introduction to data mining.pdf`
- **SHA256**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **Type**: Slide Deck Extract
<full extracted slide text>

### Source: `26 09 03 S&M.m4a`
- **SHA256**: `a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e`
- **Type**: Audio Transcript
<full transcript text>
```

### 5. Formatting Standards
- **Obsidian Syntax & Edge Cases**: Refer to the `obsidian-markdown` skill for full Obsidian Flavored Markdown conventions, callouts, wikilinks, and tricky rendering behaviors.
- **LaTeX Math**: Inline math with `$...$`, multi-line blocks with `$$\n...\n$$`.
- **Currency**: Escape currency dollar signs as `\$1,000` or write `1,000 USD` to prevent MathJax parsing collisions.
- **Highlights**: Use ` == ` and ` = ` always with spaces around `==` for reliable Obsidian rendering.
- **Language**: Match the primary language of the course materials (English/Italian).

### 6. Reconciliation Audit Gate
Before completing the synthesis, run the verification script:
```bash
python3 scripts/verify_note.py "<note_path>"
```
The audit gate verifies:
- [ ] **100% Slide Accounting**: Every slide across all PDF/PPTX decks has all bullets, quiz questions, and notes incorporated.
- [ ] **100% Workbook Accounting**: Every exercise, code task, and solution from all workbooks is fully articulated.
- [ ] **100% Formula Completeness**: Every equation has an accompanying parameter breakdown table.
- [ ] **Exam Pitfalls & Traps**: Every classroom warning or diagnostic note has a dedicated callout.
- [ ] **Reconciliation Audit**: 100% of extracted definitions, formulas, code logic, visual takeaways, and exam caveats are fully articulated in the text prose with zero omissions.
- [ ] **Navigation & TOC**: Table of contents wikilinks (`- [[#Topic]]`) resolve cleanly to document headers.
- [ ] **Code Fence & Tag Symmetry**: All fences and `<details>` blocks are properly closed.
- [ ] **Audit Trail Integrity**: Zero truncated source markers detected.
