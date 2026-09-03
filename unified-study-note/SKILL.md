---
name: unified-study-note
description: Merge raw course materials (slides PDF/PPTX, audio transcripts, personal notes, workbooks, quizzes, exercises) into a single, comprehensive, deduplicated Obsidian master study note with 100% information completeness and zero loss. Use whenever synthesizing, merging, compiling, or updating course materials, study guides, lecture slides, or recordings into Obsidian master notes.
---

# Unified Study Note Generator

Converts all raw course materials into a single, deduplicated, concept-centric master note in Obsidian. Every source (slides, workbooks, transcripts, practice scripts, quizzes) is ingested as an authoritative, first-class input and synthesized into an exhaustive, fully self-contained study guide.

## Core Rules

- **Single Master Note**: All content merges into `<Course Name>.md` at `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`. All course knowledge remains unified in this single file.
- **Topical Deduplication & Co-Location**: Group knowledge strictly by concept (`### <Topic>`). When a topic reappears across multiple slide decks, workbooks, or lecture sessions, fuse all details directly into the existing concept section with inline spot citations (`[[<source-file>]]`). Never dump disconnected slide-by-slide summaries.
- **100% Slide & Source Exhaustiveness**: Every single slide from every PDF/PPTX deck (every bullet point, definition, formula ($$...$$), derivation, parameter, verbatim code snippet, edge case, diagram takeaway, and lecture quiz) must be explicitly articulated in full in the text prose. High-level summaries, condensations, or silent omissions are strictly forbidden.
- **Textual Self-Sufficiency**: The Markdown prose must be 100% self-contained. Articulate all definitions, causal mechanisms, mathematical parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive references.
- **Uniform Taxonomy & Consistency**: Maintain uniform formatting standards across the note: LaTeX math blocks paired with parameter breakdown tables, verbatim code fences with line-by-line commentary, and dedicated callout boxes for exam traps and practical quiz questions.

---

## Input Processing & Ingestion Pipeline

Ingest and extract all raw materials into clean plain text before synthesis:

1. **PDF / PPTX Slide Decks (Mandatory Pre-Extraction)**:
   - Extract 100% of text, bullet points, and code from every slide into a persistent markdown extract file saved in the source directory (e.g., `<deck_name>_text_extract.md`). Treat this extract as a primary textual source.
   - For slides containing diagrams, plots, complex architecture schemas, or decision workflows, render high-resolution images via `pdftoppm -png -r 150` into `images/` and embed them (`![[slide-XX.png]]`), accompanied by full prose explaining the key takeaways.
2. **Audio & Video Transcripts**:
   - Transcribe all recordings via OmniRoute STT (`auto/best-stt`, endpoint `POST /v1/audio/transcriptions`).
   - Extract verbal lecturer nuances, exam tips, spoken metaphors, and student Q&A clarifications. Correct phonetic approximations of technical terms using the written materials.
3. **Personal notes**: Read in full. Resolve all inline comments or questions directly within the relevant concept section or dedicated callout (strip raw `%%` comment syntax from final output).
4. **Code Workbooks & Practice Scripts**:
   - Extract all code blocks, exercises, and solution scripts verbatim into syntax-highlighted fences (` ```python `, ` ```r `, ` ```sql `).
   - Pair every snippet with line-by-line explanations linking parameters to theoretical foundations.
5. **Quizzes & Formative Tests**:
   - Extract all quiz questions, multiple-choice options, correct solutions, and explanation rationale from slides, canvas quizzes, and practice scripts into dedicated callouts.

---

## Synthesis Workflow

### 1. Pre-Read Master Note
Open `<Course Name>.md` and inspect existing sections. Map all incoming topics to existing concept sections (merge) or identify new sections (insert) to maintain a clean, deduplicated concept hierarchy.

### 2. Comprehensive Raw Inventory & Topic Mapping
Read all extracted slide texts, transcripts, workbooks, and code files in full. Categorize every inventoried item by target **Concept Topic** (`### <Topic>`) and functional **Format**:

- **Prose**: Core theoretical definitions, causal mechanisms, intuitions, and formal arguments.
- **Formulas & Parameter Tables**: Mathematical statements (`$$...$$`), derivations, and detailed parameter breakdown tables.
- **Verbatim Code & Exercises**: Full code scripts with line-by-line theoretical walkthroughs.
- **Exam Traps & Fallacies**: Common mistakes, subtle bugs, and syntax collisions (`> [!warning] Exam Trap`).
- **Classroom Quizzes & Practice**: Slide questions and step-by-step solutions (`> [!tip] Slide Quiz & Practical Application`).
- **Visuals**: Diagram embeds (`![[slide-XX.png]]`) paired with exhaustive analytical commentary.

### 3. Build Unified Concept Blocks
Fuse all inventoried items into deep, high-density concept sections:

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

Rules:
- **Bold** key technical terms on first mention.
- Use Markdown tables for parameter breakdowns, feature matrices, and language comparisons (e.g., Python vs R).
- Use numbered lists for sequential derivations, algorithms, and decision rules.
- Maintain consistent callouts (`> [!note]`, `> [!warning]`, `> [!tip]`, `> [!important]`).
- Place visual embeds immediately adjacent to the concept they illustrate.

### 5. Formatting Standards
- **Obsidian Syntax & Edge Cases**: Refer to the `obsidian-markdown` skill for full Obsidian Flavored Markdown conventions, callouts, wikilinks, and tricky rendering behaviors.
- **LaTeX Math**: Inline math with `$...$`, multi-line blocks with `$$\n...\n$$`.
- **Currency**: Escape currency dollar signs as `\$1,000` or write `1,000 USD` to prevent MathJax parsing collisions.
- **Highlights**: Use ` == ` and ` = ` always with spaces around `==` for reliable Obsidian rendering.
- **Language**: Match the primary language of the course materials (English/Italian).

### 6. Reconciliation Audit Gate
Before completing the synthesis, perform an explicit coverage verification:
- [ ] **100% Slide Accounting**: Every slide across all PDF/PPTX decks has all bullets, quiz questions, and notes incorporated.
- [ ] **100% Workbook Accounting**: Every exercise, code task, and solution from all workbooks is fully articulated.
- [ ] **100% Formula Completeness**: Every equation has an accompanying parameter breakdown table.
- [ ] **Exam Pitfalls & Traps**: Every classroom warning or diagnostic note has a dedicated callout.
- [ ] **Audit Trail Integrity**: Every source file is present in the `## Complete source record` with zero truncation.
- [ ] **Navigation & TOC**: Table of contents wikilinks (`- [[#Topic]]`) resolve cleanly to document headers.
