---
name: "unified-study-note"
description: "Merge raw course materials (slides, audio recordings/transcripts, personal notes, code notebooks, quizzes) into a single, comprehensive, deduplicated Obsidian master note with zero information loss."
---

# Unified Study Note Merger

Use this skill to perform an exhaustive, non-destructive merge of multi-modal course materials into a single authoritative master note (`<Course Name>.md`) in Obsidian.

---

## Core Principles

- **Single Master Note**: All material merges into EXACTLY ONE authoritative master markdown file per course: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md`. Never create fragmented note files.
- **Exhaustive Merge (Zero Information Loss)**: This is a full information merge, NOT a high-level summary. Retain every formula, derivation step, parameter definition, algorithm step, bound code argument, and edge case. Rewrite prose for clarity and high density.
- **Topical Deduplication**: Every topic has exactly one definitive home. Read the existing master note first to cross-reference established concepts (`[[#Topic Name]]`) rather than repeating definitions. Keep mathematical notation and code blocks consistent.
- **Spot Citations**: Cite source files inline (`[[slide.pdf]]`, `[[transcript.md]]`, `[[notes.md]]`) where relevant, without requiring mandatory attribution headers.

---

## Workflow

### 1. Source Intake & Pre-Processing
- **Locate Master Note**: Read the existing `<Course Name>.md` to identify established sections, notations, and cross-reference targets. If it does not exist, initialize it with frontmatter and a Table of Contents.
- **Audit Available Input Sources**:
  - **Slide Documents** (slide PDFs, presentations, attachments)
  - **Audio / Video Recordings or Transcripts** (audio/video recording files, text transcripts, subtitles, or inline text)
  - **Student Scratchpad / Personal Notes** (markdown notes or prompt text, with optional `%% %%` questions)
  - **Practical Code Notebooks & Workbooks** (code notebooks, scripts, query files, or Notion workbooks formatted for Obsidian)
  - **Quizzes / Exercises / Mock Questions**

- **Audio Inputs**: If raw audio/video recordings are provided, transcribe using OmniRoute STT (`auto/best-stt` via `/v1/audio/transcriptions` with credentials from `/.aside/u/0/.env`). Save the output to a transcript file for inline referencing. Review spoken phonetic errors, domain-specific abbreviations, and mathematical terms during transcript analysis.

- **Slide Documents**: Render images with `pdftoppm -png -r 150 <slides.pdf> images/slide`. Embed only essential figures, diagrams, plots, and visual schemas (`![[slide-XX.png]]`).

### 2. Multi-Layer Information Fusion
For each topic, fuse all available source streams into a single unified narrative block with zero source siloing:
- **Slides & Visuals**: Anchor core definitions, formulas, and structural hierarchy to the slide sequence. Place filtered diagram embeds (`![[slide-XX.png]]`) directly adjacent to their conceptual explanations.
- **Spoken Audio & Transcripts**: Expand compact slide bullets with verbal intuition, real-world examples, proofs, and edge cases from the lecture, eliminating conversational filler while preserving complete academic depth.
- **Personal Notes & Inline Questions (`%% %%`)**: Integrate student observations and resolve all inline `%%question%%` comments directly in context using:
  ```markdown
  > [!tip] Student Clarification: <Question / Concept>
  > <Detailed, evidence-backed answer derived from the lecture and transcript>
  ```
- **Code Notebooks, Scripts & Workbooks**: Bind theory to practical implementation by embedding runnable code blocks in their respective language fences with parameter breakdowns directly underneath their theoretical concepts.
- **Quizzes, Exercises & Past Exams**: Embed quiz questions, trap justifications, and multiple-choice explanations directly into the relevant concept section:
  ```markdown
  > [!warning] Exam Trap & Quiz Insight
  > **Question**: <Quiz Question>
  > **Key Takeaway**: <Explanation of why distractors fail and why the correct choice holds>
  ```
- **Course Logistics & Announcements**: If the materials contain syllabus updates, exam guidelines, or administrative rules, isolate them into a concise overview section rather than scattering them across concept sections.

### 3. Formatting & Obsidian Standards
- **Math Formatting**: Inline math `$f(x)$`, display math on dedicated lines `$$\n...\n$$`.
- **Currency Escaping**: Escape literal dollar signs in prose (`\$1,000`, `\$50`) or use ISO codes (`1,000 USD`) to prevent MathJax parsing breaks.
- **Structured Elements**: Use Markdown comparison tables for trade-offs and callouts (`> [!note]`, `> [!warning]`, `> [!tip]`) for critical takeaways.
- **Obsidian Reference**: Consult the `obsidian-markdown` skill for further syntax guidelines.

### 4. Merge & Verification
- Insert the new topical section non-destructively into `<Course Name>.md`.
- Refresh the Table of Contents at the top with Obsidian internal links (`- [[#Heading]]`).
- Verify that formulas, image embeds, and wikilinks render cleanly.
