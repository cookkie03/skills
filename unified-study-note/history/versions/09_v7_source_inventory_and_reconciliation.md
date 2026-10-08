---
name: unified-study-note
description: Merge raw course materials (slides, audio recordings/transcripts, personal notes, code notebooks, quizzes, readings) into a single, comprehensive, deduplicated Obsidian master note with zero information loss.
---

# Unified Study Note Generator

Converts raw course materials into a single, deduplicated, concept-centric master note in Obsidian. All provided sources are ingested as equal, first-class inputs and synthesized into an authoritative, fully self-contained study guide.

## Core Rules

- **Single master note**: All content merges into `<Course Name>.md` at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`. Never create fragmented files.
- **Topical deduplication**: Organize by concept (`### <Topic>`). If a topic reappears across sessions or sources, merge it into the existing concept section with inline spot citations.
- **Zero information loss**: Capture every formula, derivation, parameter definition, proof, edge case, code block, and quiz insight. No high-level summaries; state everything once, in full, in the right place.
- **Textual self-sufficiency**: The Markdown text must be 100% self-contained. Never rely on an embedded image or code snippet alone to convey meaning — explain all theory, parameter meanings, and visual takeaways fully in the surrounding text.
- **Consistency within a note**: Formatting conventions (callout styles, table structures, code annotations) must remain uniform across a given master note.

---

## Input Processing

Ask the user for missing input paths or resources if not provided. Ingest all materials into plain text before synthesis:

- **Slides (PDF)**: Extract all text and bullet points into a temporary text extract to treat as a primary textual source. Render slide graphics via `pdftoppm -png -r 150` into `images/`. Embed images only for slides containing diagrams, plots, complex formulas, tables, or visual schemas (skip plain text and title slides).
- **Audio / Video**: Transcribe raw audio/video via OmniRoute STT (`auto/best-stt`, endpoint `POST /v1/audio/transcriptions`, credentials from `.env`). For existing transcripts, correct technical terms and phonetic errors using the written materials as reference.
- **Personal notes**: Read in full. Resolve any inline comments or questions directly within the relevant concept section or dedicated callout (strip raw `%%` comment syntax from final output).
- **Code scripts / notebooks**: Extract code blocks verbatim into syntax-highlighted fences using the source language (` ```python `, ` ```r `, ` ```sql `). Pair each block with line-by-line commentary linking parameters to the theory.
- **Other documents (DOCX, HTML, readings)**: Extract all text, tables, and definitions into plain text for ingestion.

---

## Synthesis Workflow

### 1. Pre-read master note
Open `<Course Name>.md` and inspect existing sections. Map each incoming topic to an existing section (merge) or a new section (insert) to prevent duplicate definitions.

### 2. Full Source Ingestion & Raw Inventory
Read all extracted texts, transcripts, notes, and code files in full. Build a preliminary raw inventory, classifying every item by **Topic** (`### <Topic>`) and target **Format**:

- **Prose**: Core theoretical definitions, mechanisms, intuitions, and formal arguments.
- **Formulas & Tables**: Mathematical statements (`$$...$$`), derivations, and parameter breakdown tables.
- **Code**: Verbatim scripts and functions with line-by-line theoretical explanation.
- **Callouts**: Exam traps/fallacies (`> [!warning]`), intuitive clarifications (`> [!tip]`), and essential caveats (`> [!note]`).
- **Visuals**: Embedded images (`![[slide-XX.png]]`) paired with complete prose explaining what the visualization demonstrates.

### 3. Build concept sections
Synthesize the inventoried items into unified, high-density concept blocks:

```markdown
### <Concept Name>
[[<source-file>]] · [[#Related Concept]]

<High-density narrative: definition + intuition + formal statement fused across all sources.>

$$
\text{Formula}
$$

| Parameter | Meaning |
| :--- | :--- |
| $x$ | ... |

\```<language>
# verbatim code with line-by-line commentary
\```

> [!warning] Exam Trap
> ...

> [!tip] Clarification
> ...

![[slide-XX.png]]
*Caption describing the key takeaway.*
```

Rules:
- Bold key terms on first mention.
- Use Markdown tables for parameter definitions, comparisons, and feature matrices.
- Use numbered lists for sequential algorithms, decision rules, and derivations.
- Use callouts (`> [!note]`, `> [!warning]`, `> [!tip]`, `> [!important]`) purposefully; keep usage consistent within the note.
- Place visual embeds closest to the concept they illustrate.
- Use flexible inline spot citations `[[<source-file>]]` and internal wikilinks `[[#Concept Name]]` for cross-references.

### 4. Formatting standards
- **LaTeX math**: `$...$` inline, `$$\n...\n$$` block.
- **Currency**: Escape dollar signs as `\$1,000` or write `1,000 USD` to avoid MathJax parsing errors. (See `obsidian-markdown` skill for full Obsidian syntax reference.)
- **Language**: Match the primary language of the course materials.

### 5. Integrate & verify
- Insert or merge each concept section at its proper logical location in `<Course Name>.md`.
- **Reconciliation Audit**: Check against the raw inventory to verify that 100% of extracted definitions, formulas, code logic, visual takeaways, and exam caveats are fully written into the prose with zero omissions.
- Update the master note's Table of Contents with Obsidian wikilinks (`- [[#Concept Name]]`).
- Verify that LaTeX blocks, code fences, wikilinks, and callouts render cleanly.
