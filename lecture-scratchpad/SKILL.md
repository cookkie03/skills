---
name: "lecture-scratchpad"
description: "Generate clean slide-by-slide personal scratchpad notes with sequential slide images and blank structured subheaders for real-time student note-taking in Obsidian."
---

# Lecture Slide Scratchpad Generator

Use this skill to prepare dedicated, slide-by-slide scratchpad notes for upcoming or live lectures so students have a clean, blank workspace to capture real-time notes directly underneath sequential slide images.

---

## Operating Principles

- **No Pre-Written Content**: Scratchpad notes are designed as real-time in-class worksheets. Never pre-populate slide summaries, transcripts, or synthetic notes.
- **Clean Structure Only**: Only include slide headers, sequential slide image embeds, and empty bullet prompts under standardized subheaders.

---

## Workflow

### 1. Ingest Slide Deck & Define Destination
- Target course directory: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`
- Output scratchpad note name: `Week N - Personal Notes.md` or `<Lecture/Topic> - Personal Notes.md`
- Locate slide PDF (`slides.pdf` or `LectureN-<Topic>.pdf`).

### 2. Render Slide PNGs
- Render all slides at 150 DPI into the module's `images/` directory (inside `Materials/Modules/<Module Name>/images/` or course `images/`):
  ```bash
  mkdir -p images
  pdftoppm -png -r 150 "<slides.pdf>" images/slide
  ```
- Slide images are named sequentially: `slide-01.png`, `slide-02.png`, etc.
- Ensure proper read permissions are set on rendered images (`chmod -R a+r images/`).

### 3. Generate Blank Scratchpad Markdown
Create the scratchpad note with standard Obsidian YAML frontmatter, a table of contents / logical section groupings, and the clean, 3-part blank subheader template for every slide:

```markdown
#### Slide <NN>: <Slide Title>
![[<relative-vault-path-to-slide-image.png>]]

### Key Slide Content
- 

### Spoken Lecture Takeaways & Audio Insights
- 

### Questions & Clarifications
- %% %%
```

### 4. Structural Standards
- **Slide Headings**: Pre-fill concise slide title or section topic for each slide (`#### Slide NN: <Title>`).
- **Key Slide Content**: Leave a single empty bullet prompt (`- `) for the student to jot down formulas, definitions, or code points during lecture.
- **Spoken Lecture Takeaways & Audio Insights**: Leave a single empty bullet prompt (`- `) for live verbal remarks, exam hints, and professor intuitions.
- **Questions & Clarifications**: Pre-populate an empty Obsidian comment block (`- %% %%`) for quick capture of personal doubts or discussion points.

### 5. Integration with Master Note Lifecycle
- Once the lecture concludes and the student completes their real-time notes, use the `unified-study-note` skill to synthesize and merge these scratchpad notes into the authoritative single master note (`<Course Name>.md`).
