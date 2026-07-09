# Obsidian Bases Power Patterns

Load this reference when a user needs reusable examples or a `.base` design that behaves like a custom control panel rather than a static table.

## Pattern Language

- **Scope**: the notes admitted by global filters.
- **Signal**: formulas that turn raw properties into meaningful state.
- **Lens**: each view's layout, filters, order, group, and summaries.
- **Context**: use `this` so a base changes depending on where it is embedded or what file is active.
- **Action**: the edit, review, export, navigation, or decision the user performs from the base.

## Command Center

Use for projects, clients, courses, writing pipelines, or personal operating dashboards.

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'file.hasTag("project")'

formulas:
  link: 'file.asLink(file.basename)'
  freshness: 'file.mtime.relative()'
  days_until_due: 'if(due, ((date(due) - today()) / 86400000).round(), "")'
  state: 'if(status == "done", icon("check"), if(due && date(due) < today(), icon("flame"), icon("circle")))'

properties:
  formula.link:
    displayName: "Project"
  formula.state:
    displayName: ""
  formula.freshness:
    displayName: "Updated"

views:
  - type: table
    name: "Active"
    filters:
      and:
        - 'status != "done"'
    groupBy:
      property: area
      direction: ASC
    order:
      - formula.state
      - formula.link
      - status
      - due
      - formula.freshness
```

Implementation notes:

- `file.asLink()` keeps the dashboard navigable.
- The first view is the default embed view.
- Group by the stable dimension the user thinks in: area, client, course, phase, or owner.

## Context Pane

Use when the base should act like an intelligent sidebar or embedded pane for the current note.

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'file.hasLink(this.file)'

formulas:
  note: 'file.asLink(file.basename)'
  updated: 'file.mtime.relative()'

views:
  - type: list
    name: "Links Here"
    order:
      - formula.note
      - formula.updated
```

Variants:

- Use `file.hasLink(this.file)` for "notes that link to this".
- Use `file.links.contains(this.file.asLink())` only when the link-object shape is verified in the vault.
- Use `authors.contains(this)` for author/person pages when frontmatter stores wikilinks to people.

## Review Queue

Use for resurfacing notes that need attention.

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'status != "done"'

formulas:
  age: 'file.mtime.relative()'
  stale: 'file.mtime < now() - "14d"'
  review_signal: 'if(formula.stale, "Review", "Fresh")'

views:
  - type: table
    name: "Stale"
    filters:
      and:
        - 'formula.stale'
    order:
      - file.name
      - status
      - formula.age
      - owner
```

Implementation notes:

- Review queues should filter aggressively. A review queue with everything in it is just guilt with columns.
- Use file modification time for maintenance flows, but domain dates like `last_reviewed` for serious systems.

## Cleanup Radar

Use when the user wants to improve vault hygiene.

```yaml
filters:
  and:
    - 'file.ext == "md"'

formulas:
  missing_status: '!file.hasProperty("status")'
  missing_tags: 'file.tags.isEmpty()'
  too_large: 'file.size > 10000'
  issue_count: '[formula.missing_status, formula.missing_tags, formula.too_large].filter(value).length'

views:
  - type: table
    name: "Needs Cleanup"
    filters:
      and:
        - 'formula.issue_count > 0'
    order:
      - file.name
      - formula.issue_count
      - formula.missing_status
      - formula.missing_tags
      - formula.too_large
```

Implementation notes:

- A cleanup base is a diagnostic instrument; keep each issue formula separate so the user can trust the count.
- Avoid fixing everything through one clever formula that cannot be inspected.

## Gallery

Use for books, articles, recipes, people, places, screenshots, artwork, trips, or products.

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'file.hasTag("book")'

formulas:
  cover_image: 'if(cover, image(cover), "")'
  byline: 'if(author, "by " + author, "")'
  display_status: 'if(status, status.title(), "Unsorted")'

views:
  - type: cards
    name: "Library"
    order:
      - formula.cover_image
      - file.name
      - formula.byline
      - formula.display_status

  - type: table
    name: "Reading Queue"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - priority
```

Implementation notes:

- Pair a visual cards view with a table view for operational work.
- Keep image paths as properties when the user will curate them manually.

## Map Lens

Use only when the Maps plugin is available and the note set has location properties.

```yaml
filters:
  and:
    - 'file.ext == "md"'
    - 'file.hasProperty("location")'

views:
  - type: map
    name: "Places"
    order:
      - file.name
      - location
      - status
```

Implementation notes:

- Confirm the exact property shape expected by the installed Maps view before promising a map.
- Keep a table fallback for editing missing or malformed locations.

## Summaries As Powers

Use summaries when the view should answer a question at a glance:

```yaml
summaries:
  numericMaxOrBlank: 'values.filter(value.isType("number")).reduce(if(acc == null || value > acc, value, acc), null)'

views:
  - type: table
    name: "Budget"
    order:
      - file.name
      - cost
      - paid
    summaries:
      cost: Sum
      paid: Checked
```

Good summary questions:

- How many are done?
- What is the total cost?
- What is the latest date?
- How many unique people, clients, areas, or sources appear?

## Optional Onboarding

Only when the user explicitly asks for instruction, explain the implementation in this order:

1. Start with one plain table over a small folder or tag.
2. Add one view-level filter to make the table useful.
3. Add one formula that turns raw data into signal.
4. Add one second view that changes the lens.
5. Embed the base into a note and explain how the default view works.
6. Add `this` only after the user understands normal filters.

Stop after each step and ask the user to predict what will change before showing the next YAML fragment.

## Official Docs To Recheck

- Introduction: https://obsidian.md/help/bases
- Create and embed: https://obsidian.md/help/bases/create-base
- Syntax: https://obsidian.md/help/bases/syntax
- Views: https://obsidian.md/help/bases/views
- Functions: https://obsidian.md/help/bases/functions
