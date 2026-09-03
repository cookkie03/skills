---
name: notion-to-obsidian
description: Extract public or workspace Notion pages (notion.site, notion.so, course workbooks, practical guides) into complete Obsidian Markdown notes with local image assets, expanded toggles, and LaTeX math preservation.
---

# Notion to Obsidian Extraction

Convert public or workspace Notion pages and course workbooks into complete, faithfully formatted Obsidian Markdown notes with offline assets and zero data loss.

## Execution Pipeline

### Phase 1: Discovery & URL Queue
1. Navigate to the target Notion URL in Aside (`openTab(url)` or `page.goto(url)`).
2. For course hubs or database indexes (e.g. `Data Mining (Practical)` or `Programming for Data Science`), extract child page URLs from anchor elements (`a[href*="notion.site"]`, `a[href*="notion.so"]`).
3. Maintain parent-child hierarchy to organize output notes into matching vault subfolders (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/Workbooks/`).
4. **Batch Processing**: For large workbooks (300–1,200+ toggles), process 3–5 pages per REPL turn to avoid execution timeouts.

### Phase 2: Progressive Scroll & Recursive Toggle Expansion
Notion virtualizes DOM blocks and unmounts nodes outside the active viewport. Expanding parent toggles dynamically mounts child toggles that may also be collapsed.

- **Progressive Scroll**: Scroll the page from top to bottom in increments of **600px** with a **120ms pause** per step to allow `IntersectionObserver` handlers to mount elements.
- **Multi-Pass Toggle Expansion**: On each scroll step, find and click all collapsed toggle elements:
  - `[aria-expanded="false"]`
  - `.notion-toggle-block:not(.notion-toggle-open)`
  - Triangle SVG containers within toggle headers.
- **Convergence Criterion**: Repeat full top-to-bottom scroll passes until a complete pass yields **0 newly opened toggles** and document height stabilizes.

### Phase 3: DOM AST Parsing & Asset Extraction

#### 1. Table of Contents
- Parse `.notion-table_of_contents-block` into an indented Obsidian wikilink list (`- [[#Heading]]`, `  - [[#Sub-heading]]`) matching the element's indent margin styling.
- Remove redundant plain-text "Table of Contents" label elements preceding the block.

#### 2. Code Blocks & Language Detection
- Extract code text from `.line-numbers` or `pre code` containers into fenced code blocks (` ```python `, ` ```r `, ` ```sql `, ` ```bash `, ` ```json `).
- Separate prose explanations and captions outside the code fence as standard paragraphs.
- Detect language dynamically from `.notion-code-block-language` or class attributes.

#### 3. Math & KaTeX Equations
- **Block Equations**: Convert `.notion-equation-block`, `.katex-display`, or `annotation[encoding="application/x-tex"]` into multiline LaTeX blocks:
  ```markdown
  $$
  formula
  $$
  ```
- **Inline Equations**: Convert inline `.katex` elements to `$formula$`.
- **Currency Escaping**: Standalone currency figures (e.g. `$1,000`, `$50`) must be escaped as `\$1,000` to prevent Obsidian's MathJax renderer from misinterpreting currency signs as LaTeX delimiters.
- **Equals Spacing**: Inside code blocks (and when emitting literal `=` / `==`), always pad with spaces: write ` = ` and ` == `, never bare `=` / `==`.

#### 4. Tables & Structural Blocks
- **Tables**: Convert `.notion-table-block` into standard Markdown pipe tables with header dividers (`| Col 1 | Col 2 |\n|---|---|\n| Val 1 | Val 2 |`). Replace internal newlines in cells with spaces.
- **Callouts**: Map `.notion-callout-block` to Obsidian callouts (`> [!note]`, `> [!tip]`, `> [!warning]`, `> [!info]`), preserving emoji icons.
- **Typography & Lists**: Preserve Headings (H1–H3), nested bullet/numbered lists, bold (`**text**`), italics (`*text*`), and inline code (`` `code` ``). **Do not use bold inside headers** — it glitches Obsidian formatting.

#### 5. Local Image Downloads (Asset Expiration Prevention)
- Notion embeds images on temporary AWS S3 signed URLs that expire within hours.
- Download all image assets locally into the vault asset directory (`/Users/luca/Documents/Second-Brain/learning/tilburg-university/<Course>/Workbooks/images/`).
- Name images with unique slugs (e.g. `<workbook-slug>-fig-01.png`) and replace remote URLs in Markdown with local embeds (`![[image.png]]` or `![alt](images/image.png)`).

### Phase 4: Vault Placement & Non-Destructive Update
- Write converted Markdown files and images to the target vault directory.
- Include standard YAML frontmatter (`title`, `source`, `tags`, `date_extracted`).
- **Non-Destructive Merge**: If a note already exists with user annotations or custom callouts, preserve user additions intact while updating structural content.

---

## REPL Extraction Template

Execute this automation in `aside repl`:

```js
// 1. Expand all Notion toggles with progressive scroll
async function expandAllNotionToggles(p) {
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

// 2. Parse DOM AST to Obsidian Markdown
async function convertNotionToMarkdown(p, pageTitle, pageUrl) {
  return await p.evaluate(({ title, url }) => {
    const pageEl = document.querySelector('.notion-page-content') || document.querySelector('main') || document.body;
    const clone = pageEl.cloneNode(true);

    // Strip Notion UI noise
    const noise = clone.querySelectorAll('a[href*="cookie-notice"], button, .notion-topbar, .notion-sidebar, nav, [aria-label*="Breadcrumb"]');
    noise.forEach(n => {
      if (n.innerText && (n.innerText.includes('Get Notion free') || n.innerText.includes('Skip to content') || n.innerText.includes('Cookie'))) {
        n.remove();
      }
    });

    // Table of Contents
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

    // Code Blocks
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
        replacementHtml += `\n\n\`\`\`${lang}\n${codeText}\n\`\`\`\n\n`;
      }
      if (expText && expText !== codeText) {
        replacementHtml += `\n\n${expText}\n\n`;
      }
      codeBlock.outerHTML = replacementHtml;
    });

    // Tables
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
        return node.textContent.replace(/\$([0-9]+(?:\.[0-9]+)?)/g, '\\$$$1');
      }
      if (node.nodeType === Node.ELEMENT_NODE) {
        const tag = node.tagName.toLowerCase();
        const className = node.getAttribute('class') || '';

        if (['script', 'style', 'button', 'nav'].includes(tag)) return '';

        // Math / KaTeX
        if (className.includes('katex') || className.includes('notion-equation')) {
          const texAnnotation = node.querySelector('annotation[encoding="application/x-tex"]');
          const mathTex = texAnnotation ? texAnnotation.textContent.trim() : node.innerText.trim();
          return className.includes('notion-equation-block') || className.includes('katex-display')
            ? `\n\n$$\n${mathTex}\n$$\n\n`
            : ` $${mathTex}$ `;
        }

        // Inline code
        const isMono = Boolean(
          (node.style?.fontFamily && node.style?.fontFamily.toLowerCase().includes('mono')) ||
          className.includes('notion-inline-code')
        );
        if (tag === 'code' || isMono) {
          return ` \`${node.innerText.trim()}\` `;
        }

        // Bold / Italics
        if (tag === 'strong' || tag === 'b' || node.style?.fontWeight === 'bold' || node.style?.fontWeight >= 600) {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? ` **${inner}** ` : '';
        }
        if (tag === 'em' || tag === 'i' || node.style?.fontStyle === 'italic') {
          const inner = Array.from(node.childNodes).map(parseNode).join('').trim();
          return inner ? ` *${inner}* ` : '';
        }

        // Images
        if (tag === 'img') {
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

        // Paragraphs
        if (tag === 'p' || tag === 'div') {
          const inner = Array.from(node.childNodes).map(parseNode).join('');
          return inner.trim() ? `\n\n${inner.trim()}` : '';
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
