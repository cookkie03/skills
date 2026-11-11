---
name: "lecture-scratchpad"
description: "Generate slide-by-slide personal scratchpad worksheets with rendered slide images and blank note-taking sections in Obsidian. Use when preparing for lectures, processing course slide PDFs, generating in-class worksheets, or converting lecture slides into personal notes."
---

# Lecture Slide Scratchpad Generator

Generate slide-by-slide personal scratchpad notes in Obsidian with sequential rendered slide images and blank structured subheaders for real-time student note-taking during live lectures.

## Operating Principles

- **Deterministic & Zero-Token**: Execute the bundled script `scripts/generate_scratchpad.py` to render images and generate markdown without spending LLM generation tokens.
- **Blank Worksheets**: Keep scratchpads strictly as clean in-class worksheets with empty bullet prompts (`- `). Do not pre-fill summaries, synthetic explanations, or transcript text.
- **Standardized Visual Layout**: Every slide embeds its corresponding rendered PNG image above two structured capture sections.

---

## Execution

Run the bundled script:

```bash
python3 /Users/luca/.aside/u/0/skills/user/lecture-scratchpad/scripts/generate_scratchpad.py \
  --pdf "/path/to/slides.pdf" \
  --output "/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/Week N - Personal Notes.md"
```

### CLI Parameters

| Option | Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `--pdf` | `-p` | Path to the source slide deck PDF | **Required** |
| `--output` | `-o` | Target markdown note path in the vault | **Required** |
| `--images-dir`| `-i` | Custom directory for rendered slide PNGs | `<pdf_dir>/images/` |
| `--dpi` | | Resolution for rendered slide images | `150` |
| `--force` | `-f` | Overwrite existing output note | `false` |
| `--course` | | Course name override | Inferred from path |
| `--lecture` | | Lecture / Week label override | Inferred from path |
| `--title` | | Note title override | `"<Lecture> — Personal Notes"` |

---

## Markdown Structure

Each generated note contains YAML frontmatter, header metadata, and a sequential section per slide:

```markdown
---
course: "<Course Name>"
lecture: "<Week N / Lecture N>"
date: "YYYY-MM-DD"
type: "Personal Scratchpad Notes"
tags:
  - scratchpad
  - lecture-notes
---

# <Lecture> — Personal Notes

> **Course**: <Course Name>  
> **Slide Deck**: `<slides.pdf>` (N Slides)  
> **Date**: YYYY-MM-DD  

---

#### Slide 01: <Slide Title>
![[<relative-vault-path-to-image.png>]]

### Spoken Lecture Takeaways & Audio Insights
- 

### Questions & Clarifications
- 

---
```

---

## Testing & Quality Assurance

Run the test suite to verify script functionality and seams:

```bash
python3 /Users/luca/.aside/u/0/skills/user/lecture-scratchpad/tests/test_generate_scratchpad.py
```

---

## Lifecycle & Downstream Synthesis

1. **Before / During Lecture**: Generate the scratchpad note and capture spoken remarks, professor emphasis, formulas, and questions in real time.
2. **Post-Lecture Synthesis**: Once the lecture ends and student notes are captured, invoke the `unified-study-note` skill to synthesize raw slides, transcripts, lab code, and this scratchpad note into the course master note (`<Course Name>.md`).
