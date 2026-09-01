---
name: "lecture-scratchpad"
description: "Generate sequential slide-by-slide personal scratchpad notes with rendered images for upcoming lectures and real-time student note-taking in Obsidian."
---

# Lecture Slide Scratchpad Generator

Use this skill to prepare dedicated, slide-by-slide scratchpad notes for upcoming or live lectures so students can take real-time notes directly underneath sequential slide images.

---

## Workflow

### 1. Ingest Slide Deck & Define Destination
- Target course directory: `/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course Name>/`
- Output scratchpad note name: `Week N - Personal Notes.md` or `<Lecture/Topic> - Personal Notes.md`
- Locate slide PDF (`slides.pdf`).

### 2. Render Slide PNGs
- Render all slides at 150 DPI into the local `images/` directory:
  ```bash
  mkdir -p images
  pdftoppm -png -r 150 "<slides.pdf>" images/slide
  ```
- Slide images will be named sequentially: `slide-01.png`, `slide-02.png`, etc.

### 3. Generate Scratchpad Markdown
- Create the scratchpad note with:
  - Standard Obsidian frontmatter (tags, course, date).
  - Clean sequential sections for every slide:
    ```markdown
    ## Slide 1: <Slide Title / First Line>

    ![[slide-01.png]]

    ### Notes & Observations
    - 

    ### Questions
    - %% %%
    ```
- Keep prompt placeholders clean so the student can immediately type notes or insert inline questions with `%% %%` during class.

### 4. Integration with Master Note Lifecycle
- Once the lecture concludes and personal notes/recordings are completed, use the `unified-study-note` skill to merge these scratchpad notes into the authoritative course master note (`<Course Name>.md`).
