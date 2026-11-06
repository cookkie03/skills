const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const src = fs.readFileSync(`${__dirname}/notebook-repl.js`, 'utf8');
const api = vm.runInNewContext(src, {snapshot:async()=>({tree:'test'}),sleep:async()=>{}});
(async()=>{
  assert.equal(typeof api.readArtifact,'function');
  await assert.rejects(api.prepareChat({},''),/nonempty/);
  await assert.rejects(api.prepareTextSource({},null),/nonempty/);
  await assert.rejects(api.observe({},{intervalMs:NaN}),/observe bounds/);
  await assert.rejects(api.observe({},{rounds:7}),/observe bounds/);
  await assert.rejects(api.openStudio({},'Mind Map'),/only Reports/);
  await assert.rejects(api.actRef({},'not-a-ref','click'),/latest snapshot/);
  const page = {getByRole:()=>({count:async()=>2})};
  await assert.rejects(api.click(page,'button','Submit'),/found 2/);
  assert.equal((await api.observe({},{rounds:1})).length,1);
  console.log('PASS: 9 adapter smoke checks; no website writes');
})().catch(e=>{console.error(e);process.exitCode=1;});
