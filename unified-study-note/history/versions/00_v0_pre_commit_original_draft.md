---
name: "unified-study-note"
description: "Create comprehensive, unified study reports by combining lecture slide PDFs, audio transcripts, personal notes, coding notebooks, and quiz solutions into a single chronologically ordered, concept-centric Markdown note."
---

# Unified Study Note Generator

Use this skill to convert raw, heterogeneous course materials (lecture slides, audio transcripts, student notes, practical notebooks, and quiz solutions) into a single, chronologically organized, fully unified study report within the course's master note in Obsidian.

## Core Rules & Architecture

### 1. Chronological & Concept-Centric Hierarchy
- **Chronological Primary Backbone**:
  - Always structure the study notes chronologically by academic week and lecture order: `## Week N: <Topic Title> (Date / Lecture N)`.
  - This preserves temporal context so you can immediately associate concepts with the specific class or week they were taught.
- **Concept-Centric Subsections (STRICT NO SOURCE SILOING)**:
  - Inside each `## Week N` section, subdivide exclusively by **theoretical topic / concept**: `### <Concept Name>`.
  - **FORBIDDEN**: Never create headings named after source types (e.g. `### Slides Summary`, `### Lecture Transcript`, `### My Personal Notes`, `### Practical Exercises`, `### Quiz Review`).
  - Merge all 5 source streams (Slides + Audio + Personal Notes + Code Notebooks + Quizzes) directly into that concept's unified section.

### 2. Single Master Note Rule
- **Target File**: All study notes MUST be merged directly into the course's **single authoritative master note**:
  `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md`
- **NEVER create standalone fragmented files** such as `Week N - Notes.md`, `Lecture N - Notes.md`, `Week N - <Course>.md`, or separate syllabus/announcements notes.
- **Table of Contents Maintenance**: Always update the master note's top-level Table of Contents with Obsidian wikilinks targeting the new week heading (`- [[#Week N: <Topic Title>]]`).

---

## Synthesis Workflow

### Step 1. Gather & Extract Inputs
- **Audio / Video Transcripts (STRICT - NO LOCAL WHISPER)**:
  - **NEVER use Whisper local** (`whisper.cpp`, `OpenWhispr.app`, local `.bin` models).
  - **ALWAYS use OmniRoute STT** with environment credentials configured in Hermes (`HERMES_CUSTOM_OMNIROUTE_API_KEY`) to access model `auto/best-stt` via the OpenAI-compatible transcription endpoint (`POST /v1/audio/transcriptions`).
  - Spoken words from transcripts must be mapped to precise academic terminology.
- **Slides (PDF)**:
  - Extract slide text, hierarchical bullet points, and definitions.
  - Render PNG images using `pdftoppm -png -r 150` into an adjacent `images/` directory.
  - Embed slide images (`![[slide-XX.png]]`) ONLY for slides containing diagrams, plots, formulas, tables, architecture schemas, or visual figures (skip plain text and title slides).
- **Personal Notes & Questions**:
  - Read all student scratchpad notes and scan for inline questions or comments wrapped in `%% %%` tags (e.g. `%%what is a contingency table?%%`).
  - Answer every `%% %%` question using evidence from the transcript, lecture slides, or course context.
- **Code Notebooks & Notion Workbooks**:
  - Extract runnable Python (` ```python `) and R (` ```r `) snippets directly from Jupyter notebooks (`.ipynb`) and Notion workbooks.
  - For Notion pages, execute progressive top-to-bottom scroll passes (~800px step size) and recursively expand all toggles (`[aria-expanded="false"]`, `.notion-toggle-block`) before AST extraction.
- **Quizzes & Practice Questions**:
  - Extract questions, correct choices, and official justifications to integrate directly into relevant concept sections.

---

### Step 2. Concept Section Anatomy

Every concept subsection within `## Week N` must follow this integrated structure:

```markdown
### <Concept / Topic Name>

#### 1. Theoretical Intuition & Formal Definitions
- Core definitions synthesized from slide bullets + lecturer's spoken explanation from the audio transcript.
- Key mathematical or statistical terms bolded with intuitive analogies.

#### 2. Mathematical Formulation & Visuals
$$\nFormula\n$$
- Formal equations, parameter descriptions, and dimensional breakdown.
- Visual diagram: ![[slide-XX.png]] (if visual figure/schema exists on slide).

#### 3. Practical Implementation (Python / R)
```python
# Clean runnable snippet extracted from practical notebook / Notion workbook
```
- Direct line-by-line explanation linking code parameters to the theory above.

#### 4. Exam Traps & Student Clarifications
> [!warning] Exam Trap & Quiz Insight
> [Question context]: Why option A is correct and why common distractor B is incorrect.

> [!tip] Student Clarification (Resolved: %% Original Question %%)
> **Q:** [Question asked in student personal notes]
> **A:** [Comprehensive answer resolved from lecture explanation or literature]
```

---

### Step 3. Master Note Integration & Verification
1. Open the course's master note: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md`.
2. Locate the appropriate chronological insertion point (or append under the latest week).
3. Insert the newly generated `## Week N` content.
4. Regenerate / update the master Table of Contents at the top of the file with valid Obsidian wikilinks.
5. Verify that formatting (LaTeX `$$`, code fences, wikilinks, callouts) renders cleanly with no broken references.
