---
name: "unified-study-note"
description: "Create comprehensive, unified study reports by combining lecture slide PDFs, audio transcripts, personal notes, coding scripts, and quiz solutions into a single structured Markdown note."
---

# Unified Study Note Generator

Converts raw course materials into a single, deduplicated, concept-centric master note in Obsidian. Slides are the structural backbone; all other sources enrich each topic in place.

## Core Rules

- **Single master note**: All content merges into `<Course Name>.md` at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`. Never create fragmented files.
- **Topical deduplication**: Organize by concept (`### <Topic>`), not by week. Still follow the slide order as the backbone — each slide topic maps to exactly one concept section. If a topic reappears across sessions, merge it into the existing section with a spot citation.
- **Zero information loss**: Capture every formula, derivation, parameter definition, proof, edge case, code snippet, and quiz insight. No high-level summaries; state everything once, in full, in the right place.
- **Consistency within a note**: Formatting choices (callout types, table styles, code block conventions) must stay coherent and consistent throughout a given master note. Conventions may differ across notes for different courses.

---

## Input Processing

  
If not present, ask the user what are the input, both path to follow to find files and attached resources. Process every input collected, here some instructions for special input:

- **Slides (PDF)**: Primary structural backbone. Extract all text and bullets. Render PNGs via `pdftoppm -png -r 150` into `images/`. Embed images only for slides with diagrams, plots, formulas, tables, or visual schemas — skip plain text and title slides.
- **Audio / Video**: If raw audio/video is provided, transcribe via OmniRoute STT (`auto/best-stt`, endpoint `POST /v1/audio/transcriptions`, credentials from `.env`). For pre-existing transcripts, correct domain-specific and course-resource term misrecognitions before synthesis (e.g., map phonetic approximations to the correct technical term using slide vocabulary as reference).
- **Personal notes**: Read in full. Treat any inline questions or comments as instructions — answer or act on them directly within the relevant concept section or in a dedicated callout. Do not expose the original comment syntax in the output.
- **Code scripts / notebooks**: Extract code blocks verbatim into syntax-highlighted fences using the source language (e.g., ` ```python `, ` ```r `, ` ```sql `). Pair each block with a concise line-by-line explanation linking parameters to the surrounding theory.

---

## Synthesis Workflow

### 1. Pre-read master note
Open `<Course Name>.md` and identify existing concept sections. Map each incoming slide topic to an existing section (merge) or a new section (insert). This prevents duplicate definitions.

### 2. Build concept sections
Follow the slide order. 

For each topic, produce one unified section:

```markdown
### <Concept Name>
[[<source-file>]] · [[#Related Concept]]

<High-density narrative: definition + intuition + formal statement fused from slides and transcript.>

$$
\text{Formula}
$$

| Parameter | Meaning |
| :--- | :--- |
| $x$ | ... |

\```python
# verbatim code with line-by-line commentary
\```

> [!warning] Exam Trap
> ...

> [!tip] Clarification
> ...

![[slide-XX.png]]
```

Rules:
- Bold key terms on first mention.
- Use tables for parameter lists, comparisons, and structured breakdowns.
- Use numbered lists for algorithms and step-by-step proofs.
- Use callouts (`> [!note]`, `> [!warning]`, `> [!tip]`, `> [!important]`) for exam traps, clarifications, and critical caveats — choose the type that best fits the content; keep usage consistent within the note.
- Embed all and only the slide with images inline, closest to the concept they illustrate.
- Flexible inline citations: attach `[[source-file]]` directly to the claim or section header, not as a mandatory block. Add `[[#ConceptName]]` wikilinks when cross-referencing within the note.

### 3. Formatting standards
- LaTeX math: `$...$` inline, `$$\n...\n$$` block.
- Currency: always write `\$1,000` or `1,000 USD` to avoid MathJax collisions. (See `obsidian-markdown` skill for full Obsidian formatting reference.)
- Language: match the primary language of the input sources.

### 4. Integrate & verify
- Insert or merge each concept section at the correct position in `<Course Name>.md`.
- Update the master note's Table of Contents with Obsidian wikilinks (`- [[#Concept Name]]`).
- Verify LaTeX blocks, code fences, wikilinks, and callouts render cleanly before reporting completion.
