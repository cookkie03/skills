# Obsidian Rendering Traps — detail

## `$` and currency
- Obsidian treats `$...$` as inline math (and `$$...$$` as display math).
- Raw `$1000` / `$20,000` / `$0` can be interpreted as starting math delimiters.
- Fix: escape dollars (`\\$1,000`) or spell out currency (`1,000 USD`).

## `==text==` highlight markers
- Obsidian highlight parsing is sensitive to surrounding characters.
- Fix: always format as ` ==text== `.

## Minimal examples
- BAD: `$1000`
- GOOD: `\\$1,000`
- BAD: `==text==`
- GOOD: ` ==text== `
