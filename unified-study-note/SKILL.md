---
name: unified-study-note
description: Synthesize slides, audio transcripts, lab code, and quizzes into an Obsidian master study note. Use when compiling, merging, or updating university course master notes.
---

# Unified Study Note Orchestration Playbook

You orchestrate the conversion of raw multi-source course materials (slides, workbooks, transcripts, practice scripts, quizzes) into a single, concept-centric Obsidian master note (`<Course Name>.md`).

**Your role is strictly orchestration**: drive the pipeline via `scripts/`, dispatch subagents to synthesize every source across the entire course directory tree into an exhaustive, fully self-contained study guide.

---

## Core Rules

1. **Single Master Note**: All course knowledge unifies into `<Course Name>.md` at `/Second-Brain/learning/tilburg-university/<Course Name>/`.
2. **Recursive Course Coverage**: Every single file across all folders and subfolders (`Modules/`, `Practical/`, `Canvas/`, `Materials/`, `Extended Tutorials/`, `Syllabus/`, etc.) must be evaluated and ingested.
3. **Topical Deduplication & Co-Location**: Group knowledge strictly by concept (`### <Topic>`). When a topic reappears across lectures or labs, fuse details directly into the existing section with inline citations (`[[<source-file>]]`). Avoid disconnected slide-by-slide summaries.
4. **100% Source Exhaustiveness & Lossless Reorganization**: Do not drop any bullet points, variables, or definitions present in the payload. Group, sequence, and deduplicate information, but NEVER summarize or omit details. The goal is a definitive, exhaustive university manual.
5. **Textual Self-Sufficiency**: The prose must be 100% self-contained. Explain all definitions, causal mechanisms, mathematical parameter interpretations, and graphical insights directly in the surrounding text, using visual embeds and code blocks as supportive anchors.
6. **Dynamic Component Freedom**: You have full freedom to design the structure of each section using tables, nested callouts, snippets, and lists to maximize output quality, as long as information retention is strictly lossless.
7. **Active Visual Curation**: Treat image placeholders (`![[...]]`) as visual data. Use `vision_analyze` to look at them. **Always** retain structural diagrams, tables, and plots, and embed them with a caption explaining the insights you observed.

---

## Input Ingestion Pipeline (Recursive Diff & Dual-Track Processing)

Ingest course materials recursively across two tracks: pre-extract binary media (PDF/PPTX slides, audio) to `.staging_unified/`, and read native text/code from every format directly in-place.

### 0. Deterministic Source Diffing (Closed-Loop Ingestion Gate)
Scan the entire course folder and all nested subdirectories recursively:
```bash
python3 scripts/diff_sources.py "<course_dir>" "<note_path>" [--force-include <regex>] [--json]
```
- **Recursive Scan**: Visits all subfolders (`Modules/`, `Practical/`, `Canvas/`, etc.) and detects every supported format (slides, audio, code, docs, workbooks).
- **Manifest Diffing**: Compares filenames and SHA-256 hashes against the manifest (`## Complete source record` or `## Synchronized Course Assets & Inventory`) at the bottom of `<Course Name>.md`.
- **Early-Exit**: If `new_sources` and `modified_sources` are empty, report that all course materials are already fully ingested and **stop immediately** (0 LLM tokens spent).
- **Scope**: Proceed only with files identified in `new_sources` or `modified_sources`.

---

### Track A: Binary & Media Sources (Pre-Extraction to `.staging_unified/extracts/`)

1. **Slide Decks (Deterministic Text Extraction & Image Rendering)**:
   Extract full slide text and render high-resolution 150 DPI slide images:
   ```bash
   python3 scripts/extract_slides.py <file.pdf> [-o output.md] [--images-dir <path>]
   ```
   - Renders all slide PNGs to `.staging_unified/images/slide-XX.png` via macOS native Swift/PDFKit (with pdftoppm fallback).
   - Generates `.staging_unified/extracts/<deck_name>_extract.md` containing slide-by-slide text paired with corresponding image links (`![[slide-XX.png]]`).

2. **Audio & Video Transcripts (OmniRoute STT)**:
   Transcribe audio recordings via OmniRoute STT (`auto/best-stt`):
   ```bash
   python3 scripts/transcribe_audio.py "<audio_path.m4a>" -o ".staging_unified/extracts/<audio_name>_transcript.md" [--model auto/best-stt]
   ```
   - Handles long audio files automatically via 10-minute chunking.
   - Captures verbal professor explanations, exam hints, student Q&A, and technical nuances.

---

### Track B: Native Text & Code Sources (Direct In-Place Reading)

Native text and code sources do **not** need temporary staging files. Read them directly from their original disk paths:

1. **Code Notebooks & Scripts (`.ipynb`, `.R`, `.py`, `.sql`)**:
   Read code cells, exercises, and solution keys directly from their course folders. Extract code verbatim into syntax fences with line-by-line theoretical commentary.
2. **Workbooks, Notion Pages & Canvas Summaries (`.md`)**:
   Read markdown practicals and guides directly in-place, fusing theoretical background and exercise walkthroughs into target concept blocks.
3. **Personal Notes & Scratchpads**:
   Read personal notes and scratchpads in full. Resolve inline student doubts directly within topic sections (strip raw `%%` comment syntax in final output).
4. **Quizzes & Solutions**:
   Extract all quiz questions, multiple-choice options, correct solutions, and explanation rationale into `> [!tip] Slide Quiz & Practical Application` callouts.

---

## Synthesis Workflow

### 1. Pre-Read & Target Extraction
- Open `<Course Name>.md` and inspect existing sections and Table of Contents (TOC).
- Inspect top comment directives (`%% MASTER NOTE DIRECTIVE ... %%`). Follow declared course-specific rules.
- Identify existing topics and declare the new hierarchy of topics to cover. The Orchestrator collects all existing topics into a target Topic Vocabulary.

### 2. Map Phase: Line-Level Classification (`llm_classifier.py`)
USAGE: `python3 scripts/llm_classifier.py <sources_dir> <output.json> --topics "A, B, C" --endpoint <url> --model auto/best-free`
- Run the classifier script on the raw files/folders. 
- The script preprocesses raw context by injecting line numbers (`1| ...\n2| ...`).
- It iterates using `auto/best-free` (or `auto/best-cheap`) via OmniRoute.
- **Aggressive Multi‑Tagging (Zero‑Drop)**: The classifier must be *highly permissive* and assign **multiple tags** to every fragment whenever any plausible topic connection exists. This applies to **all** sources (personal notes, slides, PDFs, code, audio). The goal is to guarantee that no semantic fragment is stranded; overlapping tags create redundancy that preserves full coverage.
- Forces JSON responses mapping `start_line`, `end_line`, `topic` (matched from vocabulary), and `source_granularity` (slide/minute marker).
- Results are appended to a Master Dictionary File (`classified_map.json`).
- Orchestrator reviews and validates the Master Dictionary File before proceeding.

### 3. Reduce Phase: Zero-Token Payload Builder (`payload_builder.py`)
USAGE: `python3 scripts/payload_builder.py <master_map.json> <sources_dir> <payloads_output_dir>`
- A purely mechanical and deterministic Python script.
- Iterates over `classified_map.json`, opens the raw source files, and does deterministic slicing `lines[start_line : end_line]`.
- Groups fragments by topic and generates focused payload files `payloads/payload_<topic>.md`.
- Each payload combines all raw sources that speak about that specific topic.

### 4. Topic-Specialized Sub-Agents (Lossless Generation & Direct Write)
- You dispatch **topic-specialized** sub-agents receiving **ONLY** their focused micro-payloads.
- **CRITICAL DIRECTIVE**: Sub-agents must perform a **Lossless Reorganization**, keeping every explanation, code blocks, code results, math blocks, quiz and questions with justifications and any other relevant information. They must not drop details, summarize out nuances, or skip bullet points.
- **Personal Notes as Meta-Directives**: Sub-agents must watch for source chunks derived from personal notes. These are not only passive data, but usually **design rules and structural directives** for how to format or explain that specific topic. Sub-agents must obey them.
- **Active Vision Analysis**: Payloads contain local image pathways (e.g., `![[slide-04.png]]`). You must instruct sub-agents (via `delegate_task` context) to actively use the `vision_analyze` tool on these images. They must look at diagrams and extract tables mathematically, embedding the actual image combined with an analytical markdown caption based on their visual findings.
- **High-Density Component Library**: Give them architectural freedom to design the structure using Obsidian Markdown components optimally to maximize quality, provided they retain strict limits:
  1. **Exhaustive Prose** (High‑Density Technical Exposition): Write every concept as a compact, information‑dense block. Use a Definition → Mechanism → Intuition → Edge‑Case pattern. Avoid narrative filler (“then we see…”, “in this slide”), keep sentences short and fact‑centric, and never omit a bullet, parameter, or nuance.
  2. **Math & Formulas**: Every LaTeX block (`$$...$$`) MUST be paired with a Parameter Breakdown Table (Variable, Meaning, Constraints).
  3. **Strategic Callouts**: Use Obsidian callouts (`> [!warning]`, `> [!tip]`, `> [!quote]`) to isolate traps, quiz questions, and critical notes.
  4. **Code with Theory**: Verbatim code blocks must include line-by-line theoretical comments.
  5. **Visual Context**: Never omit images from the payload; embed them with the detailed didactic caption created by `vision_analyze`.
- **Direct Injection**: The Sub-Agent writes the generated structured output **directly into the Master Note** (`<Course Name>.md`), creating or replacing the corresponding section under `### <Topic Name>`. No intermediate drafts are needed.

### 5. Master Note Direct Integration (Sub-Agent Task)
- **Direct Injection**: Sub-Agents do NOT save intermediate drafts. They write their 5-Layer formatted output **directly into the Master Note** (`<Course Name>.md`).
  - **NEW Topics**: Append or create the full properly-layered concept block directly under `### <Concept Name>`.
    ```markdown
    ### <Concept Name>
    [[<source-file-1>]] · [[<source-file-2>]]
    
    <Lossless narrative combining theory, definitions, and transcript intuitions...>
    
    $$ Z = XW $$
    
    | Parameter | Mathematical Meaning | Dimension / Domain | Interpretation & Constraints |
    | :--- | :--- | :--- | :--- |
    | $X$ | Dati originali | $\mathbb{R}^{n \times p}$ | Deve essere centrato |
    
    > [!warning] Exam Trap: Standardizzazione
    > [Dettaglio dall'audio o slide su possibili errori comuni]
    
    ```R
    # Il parametro center e scale sono fondamentali
    pca_result <- prcomp(data, center = TRUE, scale. = TRUE)
    ```
    
    ![[slide-04.png]]
    *Figura: [Caption esplicativa dettagliata estratta dal testo/audio relativo]
  - **DELTA Topics**: Surgically inject missing definitions, formulas, or code snippets inline into existing sections, appending source citations to top section headers.

---

### 6. Append Complete Source Record (Audit Manifest)
**Fully mechanical — never compile manually.** Run the dedicated script which:
- Calls `update_source_record.py --json` internally.
USAGE: `python3 scripts/update_source_record.py <course_dir> <note_path> [--force-include <regex>]`
- Strips and rebuilds the entire `## Complete source record` section with all known sources (new + ingested + modified), SHA-256 hashes, and type labels.

```bash
python3 scripts/update_source_record.py <course_dir> <note_path> [--force-include <regex>]
```

---

### 7. Formatting Standards
- **LaTeX Math**: Inline math with `$...$`, multi-line blocks with `$$Z = XW$$`.
- **Currency**: Escape dollar signs as `\$1,000` or write `1,000 USD` to prevent MathJax parsing collisions.
- **Highlights**: Use ` == ` and ` = ` always with spaces around `==` for reliable Obsidian rendering.
- **Language**: Match the primary language of the course materials (English/Italian).
- **Obsidian Syntax & Edge Cases**: Refer to the `obsidian-markdown` skill for full Obsidian Flavored Markdown conventions, callouts, wikilinks, and tricky rendering behaviors.

---

### 8. Reconciliation Audit Gate & Final Verification
1. Automated Structural Check
Run the verification script to mechanically clear structural integrity:
```bash
python3 scripts/verify_note.py "<note_path>"
```
- [ ] Confirms TOC wikilink resolution and embedded image (images/) presence.
- [ ] Confirms Code fences, <details>, and $/$$ tag symmetry.

2. Orchestrator Semantic Re-Read
Before handing off as "done", the Orchestrator MUST read back the newly integrated topic sections to mathematically ensure:
- [ ] Zero-Loss Data Integrity: No transcript nuance or slide bullet was summarized away. Deduplication must merge facts into dense wording, not erase them.
- [ ] 5-Layer Coherence: Verify that Math Parameter Tables correctly map the preceding $$ equation, and Code implementation aligns strictly with the theory.
- [ ] Clean Output: Complete eradication of [placeholders], hallucinated fragments, and generic AI boilerplate prose.
- [ ] Source Exhaustiveness (End-to-End): Ensure the classification map successfully transferred data from every source detected by diff_sources.py into the Master Note text.
