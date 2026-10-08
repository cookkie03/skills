---
name: unified-study-note-architectures
description: Use when creating or updating unified study master notes.
---

# Unified Study Note (Adaptive Delta Architecture)

Converts raw multi-source course materials (slides, transcripts, lab code, quizzes, workbooks) into a single, deduplicated, concept-centric Obsidian master note (`<Course Name>.md`).

This architecture maximizes token efficiency and eliminates context overload by pairing **zero-token deterministic Python pipelines** (for diffing, extraction, and transcription) with **surgical delta-enrichment** (patching existing concept blocks without repeating theory) and **adaptive bounded batching** (inline for light updates, macro-batches via `delegate_task` for massive updates).

---

## The 5-Phase Execution Pipeline

```
[Course Source Files]
         │
         ▼  PHASE 1: Deterministic Source Diffing (0 LLM Tokens)
┌─────────────────────────────────────────────────────────────┐
│ Run: python3 <skill>/scripts/diff_sources.py <course_dir>   │
│ - Reads '## Complete source record' in <Course Name>.md     │
│ - Outputs: new_sources (skips 100% of already recorded files)│
└─────────────────────────────────────────────────────────────┘
         │
         ▼  PHASE 2: Deterministic Ingestion (0 LLM Tokens)
┌─────────────────────────────────────────────────────────────┐
│ Extract only NEW sources into .staging_unified/extracts/:   │
│ - Slides: python3 <skill>/scripts/extract_slides.py         │
│ - Audio:  python3 <skill>/scripts/transcribe_audio.py       │
│ - Code:   Read verbatim from .R, .py, .ipynb                │
└─────────────────────────────────────────────────────────────┘
         │
         ▼  PHASE 3: Topic Inventory & Blueprinting
┌─────────────────────────────────────────────────────────────┐
│ Master Orchestrator creates .staging_unified/inventory.json │
│ - Classifies each extract item into Target Topic            │
│ - Assigns Mode per topic:                                   │
│   • DELTA: Topic already in Master Note -> surgical patch   │
│   • NEW:   Topic absent -> full section draft               │
│ - Selects Strategy: INLINE (<3 items) vs BATCH (>3 items)   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼  PHASE 4: Drafting & Delta-Enrichment
┌─────────────────────────────────────────────────────────────┐
│ Execute drafting into .staging_unified/drafts/:             │
│ - Mode NEW: Full Obsidian concept block                     │
│ - Mode DELTA: Surgical additions (parameters, traps, code)  │
│ - INLINE: Orchestrator writes directly                      │
│ - BATCH:  Spawn 2-3 macro-batch subagents via delegate_task │
└─────────────────────────────────────────────────────────────┘
         │
         ▼  PHASE 5: Master Assembly & Audit Gate
┌─────────────────────────────────────────────────────────────┐
│ Orchestrator updates <Course Name>.md:                      │
│ 1. Apply delta patches to existing topics                   │
│ 2. Insert new topic blocks into logical TOC hierarchy       │
│ 3. Append new source extracts to '## Complete source record'│
│ 4. Run: python3 <skill>/scripts/verify_note.py <note_path>  │
│ 5. Clean staging directory .staging_unified/                │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Zero-Token Deterministic Source Diffing

Before reading raw files into LLM context, identify what is genuinely new:

1. Locate the Master Note at `/Users/luca/Library/CloudStorage/SynologyDrive-Drive/Second-Brain/learning/tilburg-university/<Course Name>/<Course Name>.md` (or the current course folder).
2. Execute the diff tool:
   ```bash
   python3 ~/.hermes/skills/aside/unified-study-note-architectures/scripts/diff_sources.py "<course_dir>" "<note_path>"
   ```
3. Read the resulting JSON summary.
   - If `new_sources` is empty: Report that all course materials are already fully recorded in the Master Note and stop.
   - If `new_sources` has items: Proceed to Phase 2 processing **only** those specific files.

---

## Phase 2: Deterministic Extraction (No LLM Tokens)

Extract text and transcribe audio using deterministic Python utilities saving to `.staging_unified/extracts/`:

1. **PDF / PPTX Slide Decks**:
   ```bash
   python3 ~/.hermes/skills/aside/unified-study-note-architectures/scripts/extract_slides.py "<pdf_path>" -o ".staging_unified/extracts/<deck_name>_extract.md"
   ```
   - For diagrams/plots, render PNGs with `pdftoppm -png -r 150 <pdf_path> images/slide` and reference them as `![[slide-XX.png]]`.
2. **Audio / Video Recordings**:
   ```bash
   python3 ~/.hermes/skills/aside/unified-study-note-architectures/scripts/transcribe_audio.py "<audio_path>" -o ".staging_unified/extracts/<audio_name>_transcript.md"
   ```
   - Uses OmniRoute STT (`auto/best-stt`) with automatic 10-minute slicing.
3. **Lab Workbooks & Code**:
   - Note paths to `.R`, `.py`, `.ipynb` scripts for direct verbatim inclusion in Phase 4.

---

## Phase 3: Topic Inventory & Routing Blueprint

The Master Orchestrator inspects the generated extracts and the existing Master Note's Table of Contents (TOC).

Generate `.staging_unified/inventory.json`:
```json
{
  "topics": [
    {
      "topic_name": "Principal Component Analysis",
      "heading": "### Principal Component Analysis",
      "mode": "DELTA",
      "sources": ["Lab_02_PCA.R", "Lecture_02_audio_transcript.md"],
      "delta_items": {
        "parameters": ["scale. = TRUE", "center = TRUE"],
        "code_snippets": ["prcomp(df, scale. = TRUE)"],
        "exam_traps": ["Coercing qualitative factors before PCA"],
        "quizzes": []
      }
    },
    {
      "topic_name": "t-Distributed Stochastic Neighbor Embedding",
      "heading": "### t-SNE",
      "mode": "NEW",
      "sources": ["Lecture_02_Slides_extract.md", "Lecture_02_audio_transcript.md"],
      "target_section": "## Non-linear Dimensionality Reduction"
    }
  ]
}
```

### Routing Strategy Selection:
- **INLINE Mode (Light Update)**: $\le 3$ topics or total new raw content $< 15\text{k}$ words. The Master Orchestrator drafts directly.
- **MACRO-BATCH Mode (Heavy Update)**: $> 3$ topics or whole-course syntheses. Group topics into 2–3 logical macro-clusters and spawn subagents via `delegate_task`.

---

## Phase 4: Drafting & Delta-Enrichment

Draft content to `.staging_unified/drafts/<topic_slug>.md`.

### A. Mode: NEW Topic Block Structure
For topics not yet present in the Master Note, generate a complete concept block:

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
> Specific error identified in slides, practice quizzes, or lecture transcripts.

> [!tip] Slide Quiz & Practical Application
> Classroom exercise and solution walkthrough extracted directly from the lecture slides.

![[slide-XX.png]]
*Detailed caption articulating the visual insight and takeaway.*
```

### B. Mode: DELTA-Enrichment (Surgical Patch)
For topics already in the Master Note, **do not rewrite the existing explanation**. Generate a surgical patch file specifying additions:

1. **Source Citation**: Prepend new wikilinks to the top source bar (`[[Slide_02.pdf]]`).
2. **Parameter Table**: Add new rows to the existing LaTeX parameter table.
3. **Verbatim Code**: Append practical code examples with line-by-line comments.
4. **Exam Traps**: Add new `> [!warning] Exam Trap` callouts.
5. **Quizzes**: Add new `> [!tip] Slide Quiz & Practical Application` callouts.

---

## Phase 5: Master Assembly & Audit Gate

The Master Orchestrator performs final integration:

1. **Apply Patches**: Apply delta enrichments to existing topic headings in `<Course Name>.md`.
2. **Insert New Blocks**: Insert new topic blocks under their designated parent modules.
3. **Update TOC**: Regenerate or extend the master Table of Contents with valid wikilinks (`- [[#Topic Name]]`).
4. **Update Source Record**: Append the full raw text extract of all new sources into `## Complete source record`:
   ```markdown
   ### Source: `<filename>`
   <full extracted text or transcript>
   ```
5. **Run Audit Script**:
   ```bash
   python3 ~/.hermes/skills/aside/unified-study-note-architectures/scripts/verify_note.py "<note_path>"
   ```
   The audit gate verifies:
   - [x] All TOC wikilinks resolve to valid headings.
   - [x] Symmetry of all code fences and HTML `<details>` tags.
   - [x] Zero truncation markers in the audit trail.
6. **Clean Staging**: Remove `.staging_unified/` once the audit passes cleanly.
