---
name: "unified-study-note"
description: "Create comprehensive, unified study reports by combining lecture slide PDFs, audio transcripts, personal notes, coding notebooks, and quiz solutions into a single structured Markdown note."
---

# Unified Study Note Generator

Use this skill to convert raw course materials (lecture slides, audio transcripts, student notes, practical notebooks, and quizzes) into a single, comprehensive, deduplicated study report in Markdown.

## Workflow

### 1. Gather Inputs & Output Destination
- **Confirm Sources**: Verify available inputs for the session/week (slide PDFs, audio transcripts, student notes, code notebooks, quizzes). Ask the user for any missing input sources if not already provided. Inputs can be:
  - Slide PDFs (local path or attachment)
  - Personal notes (`.md` or text in prompt)
  - Audio/video transcripts (`.txt`, `.md`, `.srt`, or inline text in prompt)
  - Practical code notebooks / scripts (e.g., `.ipynb`, `.py`, `.R`)
  - Quizzes / solutions
- **Output Target (Single Master Note Rule)**:
  - All study syntheses MUST merge directly into the course's single authoritative master note: `<Course Name>.md`.
  - Never create standalone fragmented files (e.g., `Week N - Notes.md`, `Week N - <Course>.md`).
  - Maintain the top-level chronological outline by academic week: `## Week N: <Topic Title> (Date / Lecture N)`.
  - **Incremental Master Note Merge**: If `<Course Name>.md` already contains previous weeks, read the existing note first to avoid duplicate definitions; merge the new week cleanly without overwriting or deleting earlier content.

### 2. Extract Source Content
- **Slides (PDF)**:
  - Extract all slide text, structure, and bullet points.
  - Render PNG images of slides using `pdftoppm -png -r 150` into an `images/` directory adjacent to the target file.
  - Filter images: Embed images ONLY for slides containing diagrams, plots, formulas, tables, architecture schemas, or visual figures. Skip plain text and title slides.
- **Personal Notes**:
  - Read all student notes and identify inline comments or questions wrapped in `%% %%` tags (e.g., `%%what is a contingency table?%%`).
  - Answer every `%% %%` question inline using evidence from the transcript, slides, or course context.
- **Audio Transcripts**:
  - Carefully interpret spoken transcript text, correcting misrecognized audio words into precise academic/domain terminology.
  - If raw audio/video is provided, transcribe using OmniRoute STT (`auto/best-stt` via `/v1/audio/transcriptions` with credentials from `.env`).
- **Code Notebooks & Practical Workbooks**:
  - Extract actual code blocks directly into syntax-highlighted code fences (e.g., ````python````, ````r````, ````sql````) rather than providing high-level text descriptions.
- **Quizzes & Solutions**:
  - Integrate quiz questions, choices, and official justifications directly into the corresponding concept sections to enrich explanations, rather than keeping a separate standalone quiz section.

### 3. Synthesize & Deduplicate
- **Backbone Structure**: Follow the logical flow of the lecture slides as the primary structure.
- **Obsidian Source Referencing (Mandatory)**: Always include explicit Obsidian references and wikilinks to all ingested source materials of any kind (e.g., slide PDFs `![[...]]` or `[[...]]`, personal student notes `[[...]]`, audio/video transcripts `[[...]]`, code notebooks/scripts `[[...]]`, Notion workbooks `[[...]]`, quizzes, lab files, and any other inputs) at the start of each weekly section and under relevant concept headers.
- **Information Depth**: Capture 100% of substantive concepts, formulas, derivation steps, parameter definitions, edge cases, theorems, proofs, code snippets, and practical arguments.
- **Unified Concept Sections**:
  - For each topic, merge slide bullets + transcript explanations + student note clarifications + code snippets + quiz insights into a single definitive, non-redundant section.
  - Merge definitions, formulas, bound code snippets, exam traps (`> [!warning]`), and student clarifications (`> [!tip]`) into a single narrative block.
- **Single Source of Truth**: State every fact, formula, and rule in **exactly one place**. Course logistics appear only in the top-level overview.
- **Formatting Standards**:
  - Use Obsidian callouts (`> [!note]`, `> [!warning]`, `> [!tip]`) for exam traps, clarifications, and critical warnings.
  - Use LaTeX math (`$...$` inline, `$$\n...\n$$` block) for mathematical formulas.
  - **Currency & Dollar Sign Escaping**: Always escape literal currency dollar signs in markdown prose with a backslash (`\$1,000`, `\$50`) or use ISO currency (`1,000 USD`) so Obsidian's MathJax renderer does not break.
  - Embed slide images using standard Markdown or Wikilinks (`![[slide-XX.png]]` or `![](images/slide-XX.png)`).
  - Refer to the `obsidian-markdown` skill for Obsidian-specific syntax, frontmatter, and formatting standards.
  - Include a structured **Course Logistics & Exam Overview** section if administrative/exam info is present in the week's materials.
  - **Language**: Match the primary language of the input sources (e.g., English sources -> English note).

### 4. Deliver Report
- Insert the synthesized `## Week N` section at the appropriate chronological insertion point in `<Course Name>.md`.
- Regenerate the master note's Table of Contents with valid Obsidian wikilinks (`- [[#Heading]]`).
- Verify that formatting (LaTeX `$$`, code fences, wikilinks, callouts) renders cleanly with no broken references before reporting completion.
