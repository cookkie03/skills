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
  - Practical code notebooks (`.ipynb`)
  - Quizzes / solutions
- **Output Target (Single Master Note Rule)**:
  - All study syntheses MUST merge directly into the course's single authoritative master note: `<Course Name>.md`.
  - Never create standalone fragmented files (e.g., `Week N - Notes.md`, `Week N - <Course>.md`).
  - Maintain the top-level chronological outline by academic week: `## Week N: <Topic Title> (Date / Lecture N)`.

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
- **Code Notebooks & Notion Workbooks**:
  - Extract actual Python / R code blocks directly into code fences (` ```python `, ` ```r `) rather than providing high-level text descriptions.
  - **Notion Workbooks & Pages (Mandatory Toggle Expansion)**: When extracting or using Notion pages/workbooks as source inputs, ALWAYS execute progressive top-to-bottom scroll passes (~800px step size) and recursively expand all collapsible toggles (`[aria-expanded="false"]`, `.notion-toggle-block`, triangle SVGs) across multiple passes until 0 closed toggles remain to defeat Notion's virtualized DOM lazy-loading and ensure no sections (e.g. Dictionaries, Lists, Methods, Exercises) are truncated.
- **Quizzes & Solutions**:
  - Integrate quiz questions, choices, and official justifications directly into the corresponding concept sections to enrich explanations, rather than keeping a separate standalone quiz section.

### 3. Synthesize & Deduplicate
- **Slide-Grounded Structure & Source Attribution**:
  - Follow the lecture slide sequence as the primary outline, including a top-level **Course Logistics & Exam Overview** when administrative info is present.
  - Cite all ingested inputs at the top of each section using Obsidian wikilinks (`[[slides.pdf]]`, `[[transcript.md]]`, `[[student-notes.md]]`, `[[notebook.ipynb]]`, Notion workbooks, quizzes).
- **Exhaustive Unified Content (Zero Information Loss)**:
  - Fuse all source layers (slides, transcript explanations, student `%% %%` questions, bound code snippets, quiz insights) into unified concept sections with zero source siloing.
  - Enforce a Single Source of Truth with 100% substantive coverage: formulas, derivation steps, parameter definitions, proofs, and edge cases are stated in exactly one place.
- **Prose Style & Visual Formatting**:
  - Write high-density, filler-free prose with **bold keywords** and smooth conceptual transitions.
  - Enhance readability using structured **comparison tables** for tradeoffs/properties, and **bulleted/numbered lists** for step-by-step algorithms, assumptions, and parameter lists.
  - Standardize syntax: LaTeX math (`$`, `$$\n...\n$$`), Obsidian callouts (`> [!warning]`, `> [!tip]`), and filtered diagram embeds (`![[slide-XX.png]]`). Match source language.

### 4. Deliver Report
- Insert the synthesized `## Week N` section at the appropriate chronological insertion point in `<Course Name>.md`.
- Regenerate the master note's Table of Contents with valid Obsidian wikilinks (`- [[#Heading]]`).
- Verify that formatting (LaTeX `$$`, code fences, wikilinks, callouts) renders cleanly with no broken references before reporting completion.
