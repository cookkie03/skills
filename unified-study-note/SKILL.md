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
- **Topical Deduplication**: Every topic has exactly one definitive home. Read the existing master note first to cross-reference established concepts (`[[#Topic Name]]`) rather than repeating definitions. Keep mathematical notation and code block consistent.
- **Spot Citations**: Cite source files inline (`[[slide.pdf]]`, `[[transcript.md]]`, `[[notes.md]]`) where relevant, without requiring mandatory attribution headers.

---

## Workflow

### 1. Source Intake & Pre-Processing
- **Locate Master Note**: Read the existing `<Course Name>.md` to identify established sections, notations, and cross-reference targets. If it does not exist, initialize it with frontmatter and a Table of Contents.
- **Audit Available Input Sources**:
  - **Slide PDFs** (local path or attachment)
  - **Audio/Video Recordings** (`.m4a`, `.mp3`, `.wav`, `.aac`, `.mp4`) OR **Transcripts** (`.txt`, `.md`, `.srt`, inline text)
  - **Student Scratchpad / Personal Notes** (`.md` or prompt text, with optional `%% %%` questions)
  - **Practical Code Notebooks** (`.ipynb`, `.py`, `.R`, `.Rmd`) or **Notion Workbooks** usually already formatted for Obsidian.
  - **Quizzes / Exercises / Mock Questions**

- **Audio Inputs**: If raw audio/video (`.m4a`, `.mp3`, `.wav`, `.mp4`) is provided, transcribe using OmniRoute STT (`auto/best-stt` via `/v1/audio/transcriptions` with credentials from `/.aside/u/0/.env`). Save the output to a transcript file for inline referencing. Review spoken phonetic errors, domain-specific abbreviations, and mathematical terms during transcript analysis.

- **Slide PDFs**: Render images with `pdftoppm -png -r 150 <slides.pdf> images/slide`. Embed only essential figures, diagrams, plots, and visual schemas (`![[slide-XX.png]]`).

### 2. Multi-Layer Information Fusion
- **Personal Notes & Inline Questions (`%% %%`)**: Resolve all `%%question%%` comments directly in the text, formatting answers as `> [!tip] Student Clarification`.
- **Code & Notebooks**: Extract runnable code into fenced blocks (` ```python `, ` ```r `) with argument annotations.
- **Quizzes, Exercises & Past Exams**:
  - Embed quiz questions, multiple-choice options, trap explanations, and official reasoning directly inside the corresponding concept section:
    ```markdown
    > [!warning] Exam Trap & Quiz Insight
    > **Question**: <Quiz Question>
    > **Key Takeaway**: <Explanation of why the distractor is wrong and the correct choice holds>
    ```

### 3. Formatting & Obsidian Standards
- **Math Formatting**: Inline math `$f(x)$`, display math on dedicated lines `$$\n...\n$$`.
- **Currency Escaping**: Escape literal dollar signs in prose (`\$1,000`, `\$50`) or use ISO codes (`1,000 USD`) to prevent MathJax parsing breaks.
- **Structured Elements**: Use Markdown comparison tables for trade-offs and callouts (`> [!note]`, `> [!warning]`, `> [!tip]`) for critical takeaways.

### 4. Merge & Verification
- Insert the new topical section non-destructively into `<Course Name>.md`.
- Refresh the Table of Contents at the top with Obsidian internal links (`- [[#Heading]]`).
- Verify that formulas, image embeds, and wikilinks render cleanly.


