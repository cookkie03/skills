---
name: "notion-to-obsidian"
description: "Extract public or workspace Notion pages cleanly into Obsidian Markdown notes. Iteratively expands all toggle blocks with full-page progressive scrolling to bypass virtualized DOM lazy-loading, isolates code blocks from explanation text, preserves AST formatting (bold, italics, inline code, headings, lists, callouts, tables, math formulas, double line breaks), crawls nested sub-pages, downloads remote images locally to prevent URL expiration, escapes currency dollar signs, strips Notion UI noise, and syncs directly to the Obsidian vault in safe execution batches."
---

# Notion to Obsidian Extraction Skill

Use this skill whenever you need to convert public or workspace Notion pages into complete, faithfully formatted, rich Markdown notes for Obsidian with zero data loss.

## Core Extraction Pipeline

When extracting Notion pages:

### 1. Page & Index Discovery
- Navigate to the target Notion URL in Playwright `page` REPL.
- If the page is a course hub or database (e.g. `Data Mining (Practical)` or `Programming for Data Science Course Page`), extract all sub-page URLs from child link anchors (`a[href*="notion.site"]` or `a[href*="notion.so"]`).
- Maintain a queue of discovered sub-page URLs and their parent-child hierarchy to organize notes into the correct subfolders in Obsidian.

### 2. Safe Execution Batching
- Large workbooks (e.g. `Py2`, `Py4`, `Py6` with 300–1,200+ toggles, embedded code, and deep nesting) take significant time and memory to process.
- **Batch extractions into sets of 3–5 pages per REPL turn** to prevent the 120-second tool execution timeout.

### 3. Progressive Full-Scroll & Recursive Toggle Expansion (CRITICAL)
- **Virtualized DOM / Lazy Loading**: Notion virtualizes its DOM blocks and unmounts/lazy-loads content outside the visible viewport. Expanding a top-level toggle renders child elements that may contain additional closed toggles.
- **Mandatory Progressive Scroll & Multi-Pass Pattern**:
  - Run multiple top-to-bottom scroll passes across the page.
  - Step size: **500–800px** per scroll step, with a settling pause (**100–200ms**) after each step to allow Notion's IntersectionObservers to mount DOM nodes.
  - At every step, query and click all closed toggles:
    - `[aria-expanded="false"]`
    - `.notion-toggle-block:not(.notion-toggle-open)`
    - Div containers with triangle SVG icons (`svg` with triangle shape) and short label text.
  - Repeat the full top-to-bottom scroll cycle until a complete pass yields **0 newly opened toggles** and the total page height stabilizes.

### 4. DOM AST Node Parsing & Formatting Separation

#### A. Table of Contents Block
- Convert Notion's `.notion-table_of_contents-block` into an indented, nested Obsidian wikilink list (`- [[#Heading]]`, `  - [[#Sub-heading]]`) based on the element's `margin-inline-start` / `margin-left` indentation styling.
- Remove duplicate preceding plain "Table of Contents" label elements.

#### B. Code Blocks vs Explanation Separation
- Extract pure code lines from `.line-numbers` or `pre code` containers directly into fenced Markdown code blocks (```python, ```r, ```sql, ```bash, ```json).
- Detect language dynamically from Notion's language selector (`.notion-code-block-language`, `[aria-label*="language"]`, or class names).
- Ensure explanation text, commentary, or descriptions accompanying the block are placed cleanly outside the code fence as standard prose paragraphs.
- Preserve exact whitespace and indentation within code blocks.

#### C. Math & Equations (KaTeX / LaTeX & Dollar Sign Escaping)
- **Display / Block Equations**: Convert Notion equation blocks (`.notion-equation-block`, `.katex-display`, or `annotation[encoding="application/x-tex"]`) into multiline Obsidian LaTeX blocks:
  ```markdown
  $$
  formula
  $$
  ```
- **Inline Equations**: Convert inline KaTeX elements (`.katex`, inline `.notion-equation`) into inline LaTeX (`$formula$`).
- **Currency & Dollar Sign Escaping ($ Issue)**:
  - Raw currency figures or numbers containing dollar signs (e.g. `$1,000`, `$50`, `$100k`) MUST be escaped as `\$1,000` or written as `1,000 USD` in prose to prevent Obsidian's MathJax renderer from treating currency symbols as broken LaTeX math delimiters.

#### D. Tables
- Convert Notion table blocks (`.notion-table-block`, `table`, `tr`, `td`) into standard Markdown pipe tables with header dividers (`| Col 1 | Col 2 |\n|---|---|\n| Val 1 | Val 2 |`).
- Cleanly replace internal newlines inside table cells with spaces or `<br>` tags to prevent table row breakage.

#### E. Callouts & Blockquotes
- Convert Notion callout blocks (`.notion-callout-block`) into Obsidian callouts (`> [!note]`, `> [!tip]`, `> [!warning]`, `> [!info]`).
- Preserve the callout icon/emoji if present (e.g. `> [!tip] 💡 Tip`).

#### F. Lists & Headings
- Headings: Preserve H1 (`#`), H2 (`##`), H3 (`###`).
- Lists: Bullet lists (`- `) and numbered lists (`1. `), preserving nested indentation levels.
- Text Styles: Bold (`**text**`), Italics (`*text*`), Strikethrough (`~~text~~`), Inline Code (`` `code` ``).
- Paragraphs: Ensure consistent double line breaks (`\n\n`) between structural blocks.

#### G. Local Image Download & URL Expiration Prevention (CRITICAL)
- **AWS S3 URL Expiration**: Notion hosts embedded images on temporary AWS S3 signed URLs that expire after a few hours, causing broken images in Obsidian if hotlinked.
- **Local Download Requirement**:
  - Download all remote image assets directly into the local vault asset directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/Workbooks/images/` or `images/`).
  - Name downloaded images with a unique, descriptive slug (e.g. `<workbook-slug>-fig-01.png`).
  - Replace remote Notion image URLs in the Markdown output with local Obsidian image embeds: `![[<image-name>.png]]` or `![alt](images/<image-name>.png)`.

### 5. Strip Notion UI Noise
- Strip Notion topbars, sidebars, navigation bars, breadcrumbs, search bars, "Get Notion free" buttons, template clone banners, and cookie notices prior to Markdown serialization.

### 6. Sync to Obsidian Vault & Non-Destructive Preservation
- Write converted Markdown files and downloaded images to temporary storage (`tmp/`) in REPL, then copy them directly into the target Obsidian vault directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/Workbooks/`).
- **Non-Destructive User Edits**: If a note already exists locally with user annotations, personal notes, or custom callouts, preserve the user's modifications intact and merge new structural content cleanly.

### 7. Obsidian Markdown Standards (Skill Reference: obsidian-markdown)
- All generated notes must adhere strictly to the guidelines in the `obsidian-markdown` skill (`/Users/luca/.aside/u/0/skills/user/obsidian-markdown/SKILL.md`).
- Include standard YAML frontmatter properties (`title`, `source`, `tags`, `date_extracted`).

---

## Production Extraction Script Template

```js
// 1. Progressive scroll and recursive multi-pass toggle expansion
async function expandAllNotionTogglesWithScroll(p) {
  return await p.evaluate(async () => {
    let totalOpened = 0;
    for (let pass = 0; pass < 6; pass++) {
      let passOpened = 0;
      const step = 600;
      const docHeight = () => Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
      
      for (let scrollY = 0; scrollY <= docHeight(); scrollY += step) {
        window.scrollTo(0, scrollY);
        await new Promise(r => setTimeout(r, 120));

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
      await new Promise(r => setTimeout(r, 500));
    }
    return totalOpened;
  });
}

// 2. Full DOM AST Parser with Image Asset Extraction & Math Escaping
async function convertNotionASTComplete(p, pageTitle, pageUrl) {
  return await p.evaluate(({ title, url }) => {
    const pageEl = document.querySelector('.notion-page-content') || document.querySelector('main') || document.body;
    const clone = pageEl.cloneNode(true);

    // Remove UI noise
    const noise = clone.querySelectorAll('a[href*="cookie-notice"], button, .notion-topbar, .notion-sidebar, nav, [aria-label*="Breadcrumb"]');
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
        replacementHtml += `\n\n```${lang}\n${codeText}\n```\n\n`;
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
      if (node.nodeType === Node.TEXT_NODE) {
        // Escape standalone currency dollar signs ($1,000 -> \$1,000)
        return node.textContent.replace(/\$([0-9]+(?:\.[0-9]+)?)/g, '\\$$$1');
      }
      if (node.nodeType === Node.ELEMENT_NODE) {
        const tag = node.tagName.toLowerCase();
        const className = node.getAttribute('class') || '';

        if (tag === 'script' || tag === 'style' || tag === 'button' || tag === 'nav') return '';

        // Math / KaTeX equations
        if (className.includes('katex') || className.includes('notion-equation')) {
          const texAnnotation = node.querySelector('annotation[encoding="application/x-tex"]');
          const mathTex = texAnnotation ? texAnnotation.textContent.trim() : node.innerText.trim();
          return className.includes('notion-equation-block') || className.includes('katex-display')
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
          return ` `${node.innerText.trim()}` `;
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
          return src ? `\n\n![Image](${src})\n\n` : '';
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
          return inner ? `\n\n> [!note]\n> ${inner.replace(/\n/g, '\n> ')}\n\n` : '';
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
