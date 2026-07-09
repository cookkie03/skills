---
name: obsidian-bases-superpowers
description: Design, build, and validate power-user Obsidian Bases workflows. Use whenever the user needs a `.base` file, database-like dashboard, Base view, filter, formula, summary, embed, contextual pane, or dynamic control panel for an Obsidian vault.
---

# Obsidian Bases Superpowers

Use this skill to turn an Obsidian vault into a set of powers: scope, signal, lenses, context, and action. Build the working `.base` artifact, verify it against the vault and the official syntax, and leave only the operational notes needed to maintain it.

## Core Loop

1. **Map the vault shape**: Inspect the relevant folders, tags, note properties, and example notes when a vault is available. If no vault is available, ask for the target collection and infer a minimal property model. Complete when every required property, tag, folder, and file type used by the base is accounted for.
2. **Choose the power**: Name the base's job as one primary power: `command center`, `review queue`, `gallery`, `relationship lens`, `cleanup radar`, `progress tracker`, or `context pane`. Complete when the power explains what the user will decide or do from the base.
3. **Design the data contract**: Define the frontmatter properties the notes need, plus any file properties or formulas the base derives. Prefer properties the user can maintain naturally. Complete when every visible column/card/list item has a source: note property, file property, or formula.
4. **Compose the base**: Build valid YAML with global `filters`, optional `formulas`, `properties`, `summaries`, and one or more `views`. Complete when all view-level filters, groups, orders, and summaries match the chosen power.
5. **Expose the control knobs**: Deliver the base with terse maintenance notes: its source properties, where its scope is defined, and which formulas are safe to adjust. Give a fuller walkthrough only when the user explicitly asks to learn. Complete when a future agent or vault owner can maintain the base without reverse-engineering it.
6. **Validate hard**: Parse YAML, verify every `formula.x` reference is defined, verify every summary name exists, verify string/formula quoting, and check whether the design depends on Obsidian 1.10 features or community plugins. Complete when the base can be pasted into a `.base` file or `base` code block without known syntax errors.

## Bases Mental Model

- A base is not SQL or Dataview. There is no `from` source; a base starts from the vault, then narrows results with filters.
- Global filters apply to every view. View filters are combined with global filters using `AND`.
- Views are lenses over the same dataset. Use multiple views instead of multiple near-duplicate bases when the underlying collection is the same.
- Formulas are virtual properties defined in the `.base` file. They can be displayed, filtered, sorted, grouped, and summarized like other properties.
- Note properties come from Markdown frontmatter and can be referenced as `status`, `note.status`, or `note["status"]`.
- File properties come from Obsidian metadata, such as `file.name`, `file.path`, `file.folder`, `file.ext`, `file.size`, `file.tags`, `file.links`, `file.ctime`, and `file.mtime`.
- `this` makes contextual bases. In the main pane it refers to the base file; when embedded it refers to the note containing the embed; in the sidebar it refers to the active main-pane file.
- Embedded bases can use `![[Name.base]]`, `![[Name.base#View Name]]`, or a fenced `base` code block.

## View Choice

- Use `table` for operational dashboards, prioritization, sorting, grouping, summaries, and dense editing.
- Use `cards` for libraries, media, projects, people, places, and any collection where an image or short visual identity matters.
- Use `list` for lightweight reading queues, navigation panes, and compact contextual embeds.
- Use `map` only when notes have location data and the Maps plugin is available.

## Formula Moves

Use formulas to turn raw properties into signals:

- **Status labels**: `if(status == "done", "Done", "Active")`
- **Urgency**: `if(due, ((date(due) - today()) / 86400000).round(), null)`
- **Freshness**: `file.mtime.relative()`
- **Link display**: `file.asLink(file.basename)`
- **Normalized lists**: `list(tags_or_people).contains(this)`
- **Images**: `image(cover)` or `image("path/or/url")`
- **Icons**: `icon("arrow-right")`, usually as compact visual state
- **Regex scopes**: `/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)`

Use `if()` guards around optional properties before date math, number math, links, images, or string operations.

## Advanced Patterns

Read [references/POWER_PATTERNS.md](references/POWER_PATTERNS.md) when the user needs a reusable recipe, a control-panel design, contextual behavior, or a more capable Base than a simple table.

## Validation Traps

- Quote formulas as YAML strings. Prefer single quotes around formulas that contain double-quoted text.
- Do not use display names in filters or formulas; use the real property names.
- Do not reference `formula.name` unless `name` exists under `formulas`.
- Avoid `file.backlinks` unless necessary; prefer reversing the lookup with `file.links` or `file.hasLink()` because backlinks are heavier and may not refresh immediately.
- Check the installed Obsidian version before relying on a layout or its settings. The official Map view requires Obsidian 1.10 and the Maps plugin.
- Date subtraction returns a millisecond difference in the official Bases docs. Divide by `86400000` before using day-level number functions.

## Official Documentation Checked

This skill is based on the complete official Bases documentation family: [Introduction](https://obsidian.md/help/bases), [Create a base](https://obsidian.md/help/bases/create-base), [Syntax](https://obsidian.md/help/bases/syntax), [Views](https://obsidian.md/help/bases/views), [Functions](https://obsidian.md/help/bases/functions), [Table](https://obsidian.md/help/bases/views/table), [List](https://obsidian.md/help/bases/views/list), [Cards](https://obsidian.md/help/bases/views/cards), and [Map](https://obsidian.md/help/bases/views/map).
