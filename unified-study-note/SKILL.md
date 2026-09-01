---
name: "unified-study-note"
description: "Create and incrementally update comprehensive, unified course master notes in Obsidian by synthesizing lecture slides, raw audio recordings or transcripts, student notes, code notebooks, and quizzes with cross-week deduplication."
---

# Unified Study Note Generator

Use this skill to convert raw course materials (lecture slides, raw audio/video recordings, transcripts, student notes, practical code notebooks, and quizzes) into a single, comprehensive, deduplicated master study note in Obsidian.

---

## Core Principles & Constraints

1. **Single Master Note Rule**:
   - Maintain EXACTLY ONE authoritative master markdown file per course: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md`.
   - Never generate separate fragmented weekly notes (`Notes - <Course>.md`, `Week N - Notes.md`, `Week N - <Course>.md`, standalone syllabus stubs).
   - All incoming materials must be merged chronologically into this single file under `## Week N: <Topic Title> (Date / Lecture N)`.

2. **Progressive Academic Scope**:
   - Synthesize master notes strictly up to the currently active/completed academic week.
   - For upcoming/in-progress lectures: Render slide PNGs to `images/` and prepare a live scratchpad note (`Week N - Personal Notes.md`) with sequential slide image embeds (`![[...]]`) to support real-time student note-taking before merging upon week conclusion.

3. **Non-Destructive & Zero Information Loss**:
   - Never overwrite, truncate, or delete established sections, prior weekly syntheses, or existing student annotations in `<Course Name>.md`.
   - Preserve 100% substantive depth: retain every formula, derivation step, parameter definition, algorithm step, bound code argument, and edge case.

---

## Step-by-Step Workflow

### 1. Ingest Inputs & Identify Scope
- **Identify Course & Target Week**: Determine `<Course Name>` and the target week (`Week N`).
- **Locate Target Master Note**: Check `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md`. If it does not exist, initialize it with frontmatter and a Table of Contents.
- **Audit Available Input Sources**:
  - **Slide PDFs** (local path or attachment)
  - **Audio/Video Recordings** (`.m4a`, `.mp3`, `.wav`, `.aac`, `.mp4`) OR **Transcripts** (`.txt`, `.md`, `.srt`, inline text)
  - **Student Scratchpad / Personal Notes** (`.md` or prompt text, with optional `%% %%` questions)
  - **Practical Code Notebooks** (`.ipynb`, `.py`, `.R`, `.Rmd`) or **Notion Workbooks**
  - **Quizzes / Exercises / Mock Questions**

---

### 2. Audio Processing Pipeline (Speech-to-Text)
- If the input audio is provided as a **raw recording file** (rather than a pre-existing transcript):
  - **OmniRoute STT Policy**: Never use local Whisper (`whisper.cpp`, `OpenWhispr.app`). Always route transcription through OmniRoute's `auto/best-stt` model (`/v1/audio/transcriptions`) using credentials from `/Users/luca/.aside/u/0/.env` (`OMNIROUTE_API_KEY`, `OMNIROUTE_BASE_URL` with fallback to `models.json`).
  - **Save Transcript Asset**: Save the full transcription output to a markdown transcript file (e.g., `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/transcripts/Week N - Audio Transcript.md` or alongside course assets) so it can be cited and referenced via Obsidian wikilinks (`[[Week N - Audio Transcript.md]]`).
  - **Domain Terminology Normalization**: Review spoken phonetic errors, domain-specific abbreviations, and mathematical terms during transcript analysis.

---

### 3. Master Note Pre-Read & Cross-Week Reconciliation
- **Mandatory Pre-Read**: Before drafting `## Week N`, read the entire existing `<Course Name>.md` (all previous weeks `Week 1` through `Week N-1`).
- **Cross-Week Deduplication**:
  - Identify concepts, mathematical notations, dataset descriptions, and foundational definitions already introduced in prior weeks.
  - Do NOT redefine or re-explain established concepts from scratch. Instead, reference earlier sections using Obsidian wikilinks (e.g., `(see [[#Week 1: Linear Models|Week 1: Ordinary Least Squares]])`).
- **Focus on the Delta**:
  - Frame Week N material around what is *new*, *extended*, or *contrasted* relative to prior lectures (e.g., how Ridge/Lasso penalty terms modify the OLS loss function defined in Week 1).
- **Notation & Terminology Consistency**:
  - Enforce consistent variable names, matrix dimensions, and symbol conventions across all weeks.

---

### 4. Deep Extraction & Source Preparation

- **Slide PDF Processing**:
  - Extract complete slide text, structure, bullet points, and code snippets.
  - Render slide images:
    ```bash
    mkdir -p images
    pdftoppm -png -r 150 "<slides.pdf>" images/slide
    ```
  - **Smart Visual Filtering**: Embed ONLY slides containing diagrams, architecture charts, plots, conceptual tables, or derivation trees (`![[slide-XX.png]]`). Skip plain bulleted slides, introductory slides, and title cards.

- **Student Notes & Questions (`%% %%`)**:
  - Read student notes and locate all inline student questions or reflections wrapped in `%% %%` tags (e.g., `%%what is the intuition behind L1 sparsity?%%`).
  - Answer every question directly within the concept synthesis, wrapped in a callout:
    ```markdown
    > [!tip] Student Clarification: Intuition behind L1 Sparsity
    > <Rigorous, clear answer supported by transcript and slide evidence>
    ```

- **Code Notebooks & Notion Workbooks**:
  - Extract runnable Python/R code blocks into properly syntax-highlighted code fences (` ```python `, ` ```r `) with line-by-line annotations of key arguments and parameters.
  - **Notion Workbooks (Mandatory Toggle Expansion)**: If ingesting Notion pages/workbooks, perform progressive scrolling (~800px steps) and recursively expand all collapsible toggles (`[aria-expanded="false"]`, `.notion-toggle-block`, triangle SVGs) across multiple passes until 0 closed toggles remain to defeat virtualized DOM lazy-loading.

- **Quizzes, Exercises & Past Exams**:
  - Embed quiz questions, multiple-choice options, trap explanations, and official reasoning directly inside the corresponding concept section:
    ```markdown
    > [!warning] Exam Trap & Quiz Insight
    > **Question**: <Quiz Question>
    > **Key Takeaway**: <Explanation of why the distractor is wrong and the correct choice holds>
    ```

---

### 5. Synthesize & Structure Week N Content

- **Chronological Week Heading**:
  ```markdown
  ## Week N: <Topic Title> (<Date> / Lecture <N>)
  ```

- **Source Attribution Callout**:
  Place an attribution callout immediately below the week header:
  ```markdown
  > [!abstract] Ingested Sources
  > - Slides: [[<Slide-Filename>.pdf]]
  > - Transcript: [[<Transcript-Filename>.md]]
  > - Personal Notes: [[Week N - Personal Notes.md]]
  > - Notebook: [[<Notebook-Filename>.ipynb]]
  ```

- **Concept-Driven Hierarchy (Zero Siloing)**:
  - Subdivide Week N strictly by concept (`### <Concept Name>`), following the logical flow of lecture slides.
  - Strictly prohibit siloed headings like `### Slides Summary`, `### Transcript Notes`, or `### Lab Code`.
  - Every concept section must seamlessly fuse slide definitions + spoken lecture nuance + student question answers + bound code + quiz insights into a single unified explanation.

- **Prose & Formatting Standards**:
  - High-density, lucid prose with **bold keywords** and clear transitions.
  - **Comparison Tables**: Use Markdown tables for comparing algorithms, hyperparameters, pros/cons, and assumptions.
  - **Obsidian Flavored Markdown (see `obsidian-markdown` skill)**:
    - Inline math: `$f(x) = \sigma(w^T x + b)$`
    - Display math:
      $$\mathcal{L}_{Ridge}(\theta) = \frac{1}{2n} \sum_{i=1}^n (y_i - \hat{y}_i)^2 + \lambda \|\theta\|_2^2$$
    - **Currency Escaping**: Always escape literal currency dollar signs (`\$1,000`, `\$50,000`) or write explicit ISO codes (`1,000 USD`) so Obsidian's MathJax renderer does not break.
    - Callout types: `> [!note]`, `> [!warning]`, `> [!tip]`, `> [!example]`, `> [!abstract]`.

---

### 6. Non-Destructive Merge & Verification

1. **Insert into Master Note**:
   - Insert the synthesized `## Week N` section into `<Course Name>.md` at the correct chronological position.
2. **Update Master Table of Contents**:
   - Refresh the Table of Contents at the top of the file using Obsidian internal links:
     ```markdown
     - [[#Week 1: <Topic 1> (Date)|Week 1: <Topic 1>]]
     - [[#Week 2: <Topic 2> (Date)|Week 2: <Topic 2>]]
     ```
3. **Quality & Rendering Verification**:
   - Verify all wikilinks, image embeds (`![[slide-XX.png]]`), and LaTeX formulas render without syntax errors.
   - Confirm that no prior week content was modified, removed, or truncated.

