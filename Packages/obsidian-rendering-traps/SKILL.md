---
name: "obsidian-rendering-traps"
description: "Use when Obsidian $/== rendering breaks notes."
autoInject:
  keywords:
    - obsidian rendering
    - ==text==
    - highlight markers
    - dollar sign
    - currency dollar
    - mathjax
---

# Obsidian Rendering Traps ( $ / `==` / comments )

## Purpose
Ensure generated Obsidian Markdown won’t get corrupted by Obsidian parsing (notably `$` math delimiters and `==text==` highlight markers).

## Rules (copy these into output generation)

### Literal `$` / currency
- Never write raw currency like `$1000`, `$20,000`, `$0`.
- Prefer `\\$1,000` (escaped) or `1,000 USD`.

### Highlight markers `==`
- Always pad with spaces: ` ==text== `.
- Avoid bare `==text==` (unreliable rendering / swallowed text).

### Quick “where am I?” heuristic
- Prose vs math vs code blocks: treat `$` differently depending on context.

## References
See [TRAPS.md](references/TRAPS.md).
