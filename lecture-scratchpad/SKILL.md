---
name: "lecture-scratchpad"
description: "Generate sequential slide-by-slide personal scratchpad notes with rendered images for upcoming lectures and real-time student note-taking in Obsidian."
---

# Lecture Slide Scratchpad Generator

Use this skill to prepare dedicated, slide-by-slide scratchpad notes for upcoming or live lectures so students can capture real-time notes directly underneath sequential slide images.

---

## Workflow

### 1. Ingest Slide Deck & Define Destination
- Target course directory: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`
- Output scratchpad note name: `Week N - Personal Notes.md` or `<Lecture/Topic> - Personal Notes.md`
- Locate slide PDF (`slides.pdf`).

### 2. Render Slide PNGs
- Render all slides at 150 DPI into the local `images/` directory (inside `Materials/Week N/images/` or course `images/`):
  ```bash
  mkdir -p images
  pdftoppm -png -r 150 "<slides.pdf>" images/slide
  ```
- Slide images will be named sequentially: `slide-01.png`, `slide-02.png`, or `<prefix>-slide-01.png`, etc.

### 3. Generate Scratchpad Markdown
Create the scratchpad note with standard Obsidian YAML frontmatter and a clean, 3-part structural template for every slide:

```markdown
#### Slide <NN>: <Slide Title / First Line>
![[<slide-image.png>]]

### Key Slide Content
- Bullet points summarizing the written text, definitions, formulas, tables, and code directly visible on the slide.

### Spoken Lecture Takeaways & Audio Insights
- Crucial verbal explanations, intuitions, real-world examples, caveats, exam hints, and emphasis spoken by the professor during the lecture or audio recording that must definitely be included.

### Questions & Clarifications
- %% Questions that arise while studying, personal doubts, or discussion board prompts %%
```

### 4. Structural Standards
- **Key Slide Content**: Pre-populate concise bullet points extracted from the slide text, maintaining LaTeX math notation and code snippets.
- **Spoken Lecture Takeaways & Audio Insights**: If pre-recorded audio transcripts are available, pre-fill key verbal takeaways from the corresponding transcript segment; if preparing ahead of live lectures, leave clean bullet prompts (`- `) for active student note-taking.
- **Questions & Clarifications**: Always include dedicated question prompts wrapped in Obsidian comment syntax (`- %% %%`) so student inquiries and clarifications stand out during synthesis.

### 5. Integration with Master Note Lifecycle
- Once the lecture concludes and all personal notes, scratchpad takeaways, and student questions are completed, use the `unified-study-note` skill to synthesize and merge these scratchpad notes into the authoritative single master note (`<Course Name>.md`).
