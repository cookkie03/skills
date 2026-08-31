---
name: "notion-to-obsidian"
description: "Extract public or workspace Notion pages cleanly into Obsidian Markdown notes. Iteratively expands all toggle blocks with full-page progressive scrolling to bypass virtualized DOM lazy-loading, isolates code blocks from explanation text, preserves AST formatting (bold, italics, inline code, headings, lists, callouts, tables, math formulas, double line breaks), crawls nested sub-pages, strips Notion UI noise, and syncs directly to the Obsidian vault in safe execution batches."
---

# Notion to Obsidian Extraction Skill

Use this skill whenever you need to convert public or workspace Notion pages into complete, faithfully formatted, rich Markdown notes for Obsidian.

## Core Extraction Pipeline

When extracting Notion pages:

### 1. Page & Index Discovery
- Navigate to the Notion URL in Playwright `page` REPL.
- If the page is a main course hub (e.g. `Data Mining (Practical)` or `Programming for Data Science`), extract all sub-page URLs from child links (`a[href*="notion.site"]` or `a[href*="notion.so"]`).

### 2. Execution Batching
- Large workbooks (e.g. `Py2`, `Py4`, `Py6` with 300–1,200+ toggles and deep nesting) take significant processing time.
- **Batch extractions into sets of 4–5 pages per REPL turn** to prevent the 120-second tool execution timeout.

### 3. Progressive Full-Scroll & Recursive Toggle Expansion (CRITICAL)
- **Virtualized DOM / Lazy Loading**: Notion does not render the entire DOM on page load; it virtualizes blocks and lazy-loads content only as the viewport scrolls. Furthermore, expanding top-level toggles exposes new nested sub-toggles that must also be scrolled into view and expanded.
- **Mandatory Progressive Scroll Pattern**:
  - Run multiple top-to-bottom scroll passes (step size ~800px).
  - At each scroll step, query and click all closed toggles (`[aria-expanded="false"]`, `.notion-toggle-block:not(.notion-toggle-open)`, or divs containing triangle SVG icons).
  - Repeat the full top-to-bottom pass until a complete pass finds **0 closed toggles** and document height stabilizes.

### 4. DOM AST Node Parsing & Separation
- **Table of Contents**: Convert Notion's `.notion-table_of_contents-block` into an indented, nested Obsidian wikilink list (`- [[#Heading]]`, `  - [[#Sub-heading]]`) based on the element's `margin-inline-start` / `margin-left` indentation. Remove duplicate preceding plain "Table of Contents" labels.
- **Code vs Explanation**: Extract pure code lines from `.line-numbers` (or code container pre/code) into fenced Markdown code blocks (```python / ```r). Place explanation text outside as plain Markdown paragraphs.
- **Inline Code**: Detect inline code elements (`code`, `.notion-inline-code`, or spans with monospace font / highlighted background) and format them as inline backticks (``` `code` ```).
- **Math & Equations**: Convert KaTeX elements (`.katex`, `annotation[encoding="application/x-tex"]`) into Obsidian-compatible LaTeX. Always write display/block equations on separate lines using the multiline form `$$\nformula\n$$`. Use `$formula$` only for genuinely inline equations.
- **Tables**: Convert Notion tables (`table`, `tr`, `td`) into Markdown pipe tables (`| Col 1 | Col 2 |\n|---|---|`).
- **Images**: Convert Notion image blocks (`img`) into `![Caption](url)` or save local image assets.
- **Headings & Structure**: Preserve headers (`#`, `##`, `###`), bold (`**text**`), italics (`*text*`), lists (`- `, `1. `), callouts (`> [!info]`), and double line breaks (`\n\n`) for paragraph spacing.

### 5. Strip UI Noise
- Remove Notion topbars, footers, breadcrumbs, "Get Notion free" buttons, and cookie banners before parsing.

### 6. Sync to Obsidian Vault
- Write generated markdown files to temporary storage (`tmp/`) in REPL, then copy them directly into the target Obsidian vault directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/`) via `cp` in `bash`.

### 7. Non-Destructive Preservation Rule
- When generating or updating Markdown notes from Notion pages, never overwrite or wipe manual annotations or customized sections that the user has added locally in Obsidian.
- If a note already exists with custom edits, merge new content cleanly or preserve the user's added sections and commentary intact.

### 8. Obsidian Markdown Formatting Standards (Skill Reference: obsidian-markdown)
- All generated notes and converted elements must strictly follow the Obsidian Flavored Markdown guidelines specified in the `obsidian-markdown` skill (`/Users/luca/.aside/u/0/skills/user/obsidian-markdown/SKILL.md`).
- Ensure consistent usage of frontmatter YAML, wikilinks (`[[Note Name]]`, `[[#Heading]]`), embeds (`![[asset]]`), standard callout types (`> [!info]`, `> [!tip]`, `> [!warning]`), highlights (`==text==`), and LaTeX math blocks (`$$\n...\n$$`).

---

## Production Extraction Script Template

```js
// 1. Progressive scroll and recursive multi-pass toggle expansion
async function expandAllNotionTogglesWithScroll(p) {
  return await p.evaluate(async () => {
    let totalOpened = 0;
    for (let pass = 0; pass < 5; pass++) {
      let passOpened = 0;
      const step = 800;
      for (let scrollY = 0; scrollY <= document.body.scrollHeight; scrollY += step) {
        window.scrollTo(0, scrollY);
        await new Promise(r => setTimeout(r, 100));

        const toggles = Array.from(document.querySelectorAll('*')).filter(el => {
          return (
            el.getAttribute('aria-expanded') === 'false' ||
            (el.classList && el.classList.contains('notion-toggle-block') && !el.classList.contains('notion-toggle-open')) ||
            (el.tagName === 'DIV' && el.querySelector('svg') && el.innerText && el.innerText.length < 150 && el.querySelector('svg').outerHTML.includes('triangle'))
          );
        });

        for (const t of toggles) {
          try {
            t.click();
            passOpened++;
            totalOpened++;
          } catch(e) {}
        }
      }
      if (passOpened === 0) break;
      await new Promise(r => setTimeout(r, 600));
    }
    return totalOpened;
  });
}

// 2. Full DOM AST Parser
async function convertNotionASTComplete(p, pageTitle, pageUrl) {
  return await p.evaluate(({ title, url }) => {
    const pageEl = document.querySelector('.notion-page-content') || document.querySelector('main') || document.body;
    const clone = pageEl.cloneNode(true);

    // Remove UI noise
    const noise = clone.querySelectorAll('a[href*="cookie-notice"], button, .notion-topbar, .notion-sidebar, nav');
    noise.forEach(n => {
      if (n.innerText && (n.innerText.includes('Get Notion free') || n.innerText.includes('Skip to content') || n.innerText.includes('Cookie'))) {
        n.remove();
      }
    });

    // Process Table of Contents Block
    const tocBlocks = Array.from(clone.querySelectorAll('.notion-table_of_contents-block'));
    tocBlocks.forEach(tocBlock => {
      let prev = tocBlock.previousElementSibling;
      if (prev && prev.innerText && prev.innerText.trim().toLowerCase() === 'table of contents') {
        prev.remove();
      }

      const links = Array.from(tocBlock.querySelectorAll('a'));
      let tocMd = '\n\n## Table of Contents\n\n';
      links.forEach(a => {
        const text = a.innerText.trim();
        const innerDiv = a.querySelector('div[style*="margin-inline-start"], div[style*="margin-left"]');
        const styleStr = innerDiv ? innerDiv.getAttribute('style') : '';
        const marginMatch = styleStr.match(/margin-inline-start:\s*(\d+)px/) || styleStr.match(/margin-left:\s*(\d+)px/);
        const indentPx = marginMatch ? parseInt(marginMatch[1], 10) : 0;
        const level = Math.round(indentPx / 24);
        const indent = '  '.repeat(level);
        tocMd += `${indent}- [[#${text}]]\n`;
      });
      tocBlock.outerHTML = tocMd + '\n\n';
    });

    // Process code blocks
    const codeBlocks = Array.from(clone.querySelectorAll('.notion-selectable.notion-code-block, .notion-code-block'));
    codeBlocks.forEach(codeBlock => {
      const lineNumbers = codeBlock.querySelector('.line-numbers');
      const codeText = lineNumbers ? lineNumbers.innerText.trim() : (codeBlock.querySelector('pre, code') ? codeBlock.querySelector('pre, code').innerText.trim() : codeBlock.innerText.trim());

      // Detect language if available from code block UI / class
      const langText = (codeBlock.querySelector('.notion-code-block-language, [aria-label*="language"], .language')?.innerText || '').toLowerCase().trim();
      let lang = 'python';
      if (langText.includes('r') || codeBlock.className.includes('language-r')) lang = 'r';
      else if (langText.includes('sql') || codeBlock.className.includes('language-sql')) lang = 'sql';
      else if (langText.includes('bash') || langText.includes('shell') || codeBlock.className.includes('language-bash')) lang = 'bash';
      else if (langText.includes('json') || codeBlock.className.includes('language-json')) lang = 'json';
      else if (langText) lang = langText;

      const blockClone = codeBlock.cloneNode(true);
      const cloneLineNumbers = blockClone.querySelector('.line-numbers');
      if (cloneLineNumbers) cloneLineNumbers.remove();
      const expText = blockClone.innerText.trim();

      let replacementHtml = '';
      if (codeText) {
        replacementHtml += `\n\n\`\`\`${lang}\n${codeText}\n\`\`\`\n\n`;
      }
      if (expText && expText !== codeText) {
        replacementHtml += `\n\n${expText}\n\n`;
      }

      codeBlock.outerHTML = replacementHtml;
    });

    // Process Tables
    const tables = Array.from(clone.querySelectorAll('table, .notion-table-block'));
    tables.forEach(tbl => {
      const rows = Array.from(tbl.querySelectorAll('tr'));
      if (rows.length > 0) {
        let tableMd = '\n\n';
        rows.forEach((r, idx) => {
          const cells = Array.from(r.querySelectorAll('th, td')).map(c => c.innerText.trim().replace(/\n/g, ' '));
          tableMd += '| ' + cells.join(' | ') + ' |\n';
          if (idx === 0) {
            tableMd += '| ' + cells.map(() => '---').join(' | ') + ' |\n';
          }
        });
        tbl.outerHTML = tableMd + '\n\n';
      }
    });

    function parseNode(node) {
      if (!node) return '';
      if (node.nodeType === Node.TEXT_NODE) return node.textContent;
      if (node.nodeType === Node.ELEMENT_NODE) {
        const tag = node.tagName.toLowerCase();
        const className = node.getAttribute('class') || '';

        if (tag === 'script' || tag === 'style' || tag === 'button' || tag === 'nav') return '';

        // Math / KaTeX equations
        if (className.includes('katex') || className.includes('notion-equation')) {
          const texAnnotation = node.querySelector('annotation[encoding="application/x-tex"]');
          const mathTex = texAnnotation ? texAnnotation.textContent.trim() : node.innerText.trim();
          return className.includes('notion-equation-block')
            ? `\n\n$$\n${mathTex}\n$$\n\n`
            : ` $${mathTex}$ `;
        }

        // Inline code
        const hasCodeBackground = Boolean(
          (node.style?.backgroundColor && node.style?.backgroundColor !== 'transparent' && node.style?.backgroundColor !== 'rgba(0, 0, 0, 0)') ||
          (node.style?.fontFamily && node.style?.fontFamily.toLowerCase().includes('mono')) ||
          className.includes('notion-inline-code')
        );
        if (tag === 'code' || className.includes('notion-inline-code') || (tag === 'span' && hasCodeBackground && node.innerText.trim().length > 0 && !node.querySelector('*'))) {
          return ` \`${node.innerText.trim()}\` `;
        }

        // Bold text
        if (tag === 'strong' || tag === 'b' || node.style?.fontWeight === 'bold' || node.style?.fontWeight >= 600) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? ` **${inner}** ` : '';
        }

        // Italic text
        if (tag === 'em' || tag === 'i' || node.style?.fontStyle === 'italic') {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? ` *${inner}* ` : '';
        }

        // Images
        if (tag === 'img') {
          const alt = node.getAttribute('alt') || 'Image';
          const src = node.getAttribute('src');
          return src ? `\n\n![${alt}](${src})\n\n` : '';
        }

        // Headings
        if (className.includes('notion-header-block') || className.includes('notion-h1-block') || (tag === 'h1' && !node.closest('.notion-header-block'))) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? `\n\n# ${inner}\n\n` : '';
        }
        if (className.includes('notion-sub_header-block') || className.includes('notion-h2-block') || (tag === 'h2' && !node.closest('.notion-sub_header-block'))) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? `\n\n## ${inner}\n\n` : '';
        }
        if (className.includes('notion-sub_sub_header-block') || className.includes('notion-h3-block') || (tag === 'h3' && !node.closest('.notion-sub_sub_header-block'))) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? `\n\n### ${inner}\n\n` : '';
        }

        // Callouts
        if (className.includes('notion-callout-block')) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? `\n\n> [!info] Note\n> ${inner.replace(/\n/g, '\n> ')}\n\n` : '';
        }

        // Lists
        if (tag === 'li' || className.includes('notion-bulleted_list-block')) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? `\n- ${inner}` : '';
        }

        // Paragraphs & Line Breaks
        if (tag === 'p' || tag === 'div') {
          const inner = Array.from(node.childNodes).map(parseNode).join('');
          if (!inner.trim()) return '';
          return `\n\n${inner.trim()}`;
        }

        return Array.from(node.childNodes).map(parseNode).join('');
      }

      return '';
    }

    const rawBody = parseNode(clone);
    const cleanedBody = rawBody.replace(/\n{3,}/g, '\n\n').trim();

    return `# ${title}\n\n> **Source**: [Notion Guide](${url})\n\n${cleanedBody}`;
  }, { title: pageTitle, url: pageUrl });
}
```

