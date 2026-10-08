---
name: unified-study-note
description: Merge raw course materials (slides, audio recordings/transcripts, personal notes, code notebooks, quizzes, readings) into a single, comprehensive, deduplicated Obsidian master note with zero information loss.
---

# Unified Study Note Generator

Converts raw course materials into a single, deduplicated, concept-centric master note in Obsidian. All provided sources are ingested as equal, first-class inputs and synthesized into an authoritative, fully self-contained study guide.

## Core Rules

- **Single master note**: All content merges into `<Course Name>.md` at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`. Keep all course knowledge unified in this single file.
- **Topical deduplication**: Organize by concept (`### <Topic>`). When a topic reappears across sessions or sources, merge it directly into the existing concept section with inline spot citations.
- **Exhaustive concept preservation**: Capture every formula, derivation, parameter definition, proof, edge case, code block, and quiz insight in full. State everything once, fully articulated, in its rightful conceptual home.
- **Textual self-sufficiency**: Ensure the Markdown prose is completely self-contained. Articulate all definitions, theoretical arguments, parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive references.
- **Consistency within a note**: Maintain uniform formatting conventions (callout styles, table structures, code annotations) throughout a given master note.

---

## Input Processing

Ingest all provided materials into plain text before synthesis:

- **Slides (PDF)**: Extract all text and bullet points into a persistent markdown extract file saved in the source materials directory (e.g., `<deck-name>_text_extract.md`) and treat it as a primary textual source. Render slide graphics via `pdftoppm -png -r 150` into `images/`. Embed images specifically for slides containing diagrams, plots, complex formulas, tables, or visual schemas (omit plain text and title slides).
- **Audio / Video**: Transcribe raw audio/video via OmniRoute STT (`auto/best-stt`, endpoint `POST /v1/audio/transcriptions`, credentials from `.env`). For existing transcripts, correct technical terms and phonetic approximations using the written materials as reference.
- **Personal notes**: Read in full. Resolve all inline comments or questions directly within the relevant concept section or dedicated callout (strip raw `%%` comment syntax from final output).
- **Code scripts / notebooks**: Extract code blocks verbatim into syntax-highlighted fences using the source language (` ```python `, ` ```r `, ` ```sql `). Pair each block with line-by-line commentary linking parameters to the theoretical principles.

---

## Synthesis Workflow

### 1. Pre-read master note
Open `<Course Name>.md` and inspect existing sections. Map incoming topics to existing concept sections (merge) or new sections (insert) to maintain a clean, deduplicated concept tree.

### 2. Raw Inventory & Topic-Format Mapping
Read all extracted texts, transcripts, notes, and code files in full. Build a structured raw inventory, classifying every item by target **Topic** (`### <Topic>`) and functional **Format**:

- **Prose**: Core theoretical definitions, causal mechanisms, intuitions, and formal arguments.
- **Formulas & Tables**: Mathematical statements (`$$...$$`), derivations, and parameter breakdown tables.
- **Code**: Verbatim scripts and functions with line-by-line theoretical explanation.
- **Callouts**: Exam traps and common fallacies (`> [!warning]`), intuitive clarifications (`> [!tip]`), and essential caveats (`> [!note]`).
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

```<language>
# verbatim code with line-by-line commentary
```

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
- **Reconciliation Audit**: Verify against the raw inventory that 100% of extracted definitions, formulas, code logic, visual takeaways, and exam caveats are fully articulated in the text prose with zero omissions.
- Update the master note's Table of Contents with Obsidian wikilinks (`- [[#Concept Name]]`).
- Verify that LaTeX blocks, code fences, wikilinks, and callouts render cleanly.
