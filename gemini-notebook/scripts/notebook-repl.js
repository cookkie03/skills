// Evaluate in Aside REPL: const nb = eval(await fs.readFile(PATH, 'utf8'));
// All functions require the explicitly selected Aside Page. No imports or private APIs.
(() => {
  const fail = message => { throw new Error(`Gemini Notebook: ${message}`); };
  const exact = (page, role, name) => page.getByRole(role, { name, exact: true });
  async function one(locator, description) {
    const n = await locator.count();
    if (n !== 1) fail(`${description}: expected exactly one match, found ${n}; inspect a fresh snapshot`);
    return locator;
  }
  async function click(page, role, name) {
    const target = await one(exact(page, role, name), `${role} ${JSON.stringify(name)}`);
    if (!await target.isVisible() || !await target.isEnabled()) fail(`${name} is hidden or disabled`);
    await target.click({timeout: 10000});
    return await snapshot(page, {interactive: true});
  }
  return {
    // A snapshot establishes state and refreshes refs. No persistent data is changed.
    inspect: async page => await snapshot(page, {interactive: true}),
    full: async page => await snapshot(page),
    click,
    openSources: async page => await click(page, 'button', 'Add source'),
    openStudio: async (page, kind) => {
      // Other Studio buttons may generate immediately; do not treat them as navigation.
      if (kind !== 'Reports') fail('only Reports is verified as a non-generating picker; inspect other Studio actions manually');
      return await click(page, 'button', kind);
    },
    // Prepare only. Submitting sends data to Google and is intentionally separate.
    prepareChat: async (page, text) => {
      if (typeof text !== 'string' || !text.trim()) fail('chat text must be nonempty');
      const box = await one(exact(page, 'textbox', 'Query box'), 'chat query box');
      await box.fill(text, {timeout: 10000});
      return await snapshot(page, {interactive: true});
    },
    sendChat: async page => {
      const box = await one(exact(page, 'textbox', 'Query box'), 'chat query box');
      if (!(await box.inputValue()).trim()) fail('chat query is empty');
      const submit = await one(page.locator('form:has(textarea[aria-label="Query box"]) button[aria-label="Submit"]'), 'chat Submit');
      if (!await submit.isEnabled()) fail('chat Submit is disabled');
      await submit.click({timeout: 10000});
      return await snapshot(page, {interactive: true});
    },
    chatState: async page => {
      const box = await one(exact(page,'textbox','Query box'),'chat query box');
      const submit = await one(page.locator('form:has(textarea[aria-label="Query box"]) button[aria-label="Submit"]'),'chat Submit');
      return {draft:await box.inputValue(),submitEnabled:await submit.isEnabled()};
    },
    // Extract only currently rendered controls, not an authoritative server inventory.
    inventory: async page => {
      await snapshot(page,{interactive:true});
      return await page.evaluate(() => ({
        url:location.href,
        title:document.title,
        notebooks:Array.from(document.querySelectorAll('a[href*="/notebook/"]')).map(a=>({title:a.textContent.trim(),url:a.href})),
        checkboxes:Array.from(document.querySelectorAll('input[type="checkbox"], [role="checkbox"]')).map(x=>({name:x.getAttribute('aria-label')||x.getAttribute('aria-labelledby')||'',checked:x.checked??x.getAttribute('aria-checked'),visible:!!x.getClientRects().length})),
        buttons:Array.from(document.querySelectorAll('button')).map(x=>({name:x.getAttribute('aria-label')||x.textContent.trim(),disabled:x.disabled,visible:!!x.getClientRects().length}))
      }));
    },
    // Fresh refs are the fallback when Aside's role resolver differs from the snapshot.
    actRef: async (page, ref, action, value) => {
      if (!/^[a-z]*\d*e\d+$/.test(ref)) fail('pass a ref from the latest snapshot');
      const target = page.locator(ref);
      if (action === 'click') await target.click({timeout:10000});
      else if (action === 'fill') await target.fill(value, {timeout:10000});
      else fail('supported ref actions: click, fill');
      return await snapshot(page, {interactive:true});
    },
    prepareTextSource: async (page, text) => {
      if (typeof text !== 'string' || !text.trim()) fail('source text must be nonempty');
      const box = await one(exact(page,'textbox','Pasted text'),'pasted source textbox');
      await box.fill(text,{timeout:10000});
      return await snapshot(page,{interactive:true});
    },
    readArtifact: async page => {
      const title = await one(exact(page,'textbox','Artifact title'),'open report title');
      const body = await one(page.locator('.artifact-viewer-container .artifact-content'),'report body');
      const text = await body.textContent({timeout:10000});
      if (!text?.trim()) fail('report body is empty or not loaded');
      return {title:await title.inputValue(),text,format:'DOM text, not Markdown',complete:false};
    },
    // Captures a small number of snapshots; the caller evaluates completion.
    observe: async (page, options = {}) => {
      const rounds = options.rounds ?? 3, intervalMs = options.intervalMs ?? 2000;
      if (!Number.isInteger(rounds) || rounds < 1 || rounds > 6 || !Number.isFinite(intervalMs) || intervalMs < 500 || intervalMs > 5000) fail('observe bounds: 1–6 rounds, 500–5000 ms');
      const states=[];
      for (let i=0;i<rounds;i++) {
        if(i) await sleep(intervalMs);
        states.push(await snapshot(page,{interactive:true}));
      }
      return states;
    }
  };
})()
