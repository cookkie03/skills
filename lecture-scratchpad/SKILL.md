---
name: "lecture-scratchpad"
description: "Generate clean slide-by-slide personal scratchpad notes with sequential slide images and blank structured subheaders for real-time student note-taking in Obsidian using a zero-token script."
---

# Lecture Slide Scratchpad Generator

Use this skill to prepare dedicated, slide-by-slide scratchpad notes for upcoming or live lectures so students have a clean, blank workspace to capture real-time notes directly underneath sequential slide images.

---

## Operating Principles

- **Zero-Token Automation**: Always execute the bundled script `scripts/generate_scratchpad.py` instead of generating or writing note content through LLM generation.
- **No Pre-Written Content**: Scratchpad notes are designed as real-time in-class worksheets. Never pre-populate slide summaries, transcripts, or synthetic notes.
- **Clean Structure Only**: Only include slide headers, sequential slide image embeds, and empty bullet prompts under standardized subheaders.

---

## Quick Execution (Zero-Token Script)

Run the bundled deterministic script:

```bash
python3 /Users/luca/.aside/u/0/skills/user/lecture-scratchpad/scripts/generate_scratchpad.py \
  --pdf "/path/to/slides.pdf" \
  --output "/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/Week N - Personal Notes.md"
```

The script automatically:
1. Renders all slides at 150 DPI into the module's `images/` folder (`slide-01.png`, `slide-02.png`, etc.).
2. Sets proper read permissions on rendered images.
3. Extracts concise slide titles from PDF text.
4. Generates standard Obsidian YAML frontmatter and per-slide templates.

---

## Markdown Template Specification

For every slide in the generated note:

```markdown
#### Slide <NN>: <Slide Title>
![[<relative-vault-path-to-slide-image.png>]]

### Spoken Lecture Takeaways & Audio Insights
- 

### Questions & Clarifications
- 
```

### Structural Standards
- **Slide Headings**: Pre-fill concise slide title or section topic for each slide (`#### Slide NN: <Title>`).
- **Spoken Lecture Takeaways & Audio Insights**: Single empty bullet prompt (`- `) for live verbal remarks, exam hints, and professor intuitions.
- **Questions & Clarifications**: Single empty bullet prompt (`- `) for live student questions, personal doubts, or discussion points.

---

## Integration with Master Note Lifecycle
- Once the lecture concludes and the student completes their real-time notes, use the `unified-study-note` skill to synthesize and merge these scratchpad notes into the authoritative single master note (`<Course Name>.md`).
