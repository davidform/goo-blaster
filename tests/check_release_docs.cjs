// Run from any directory: node tests/check_release_docs.cjs
// Documentation checks only; this is not the game's three-round test suite.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8').replace(/\r\n/g, '\n');
const md = read('PRIVACY.md');
const html = read('privacy.html');
const agents = read('AGENTS.md');
const handoff = read('HANDOFF.md');
let checks = 0;
function check(name, fn) { fn(); checks++; console.log('PASS ' + name); }
check('AGENTS and CLAUDE stay identical', () => assert.equal(agents, read('CLAUDE.md')));
check('handoff stays compact', () => assert.ok(handoff.trim().split('\n').length <= 80));
check('exact new-conversation prompt in both instructions and handoff', () => {
  const prompt = '依 AGENTS.md 與 HANDOFF.md 接手，先核對實際狀態，再完成目前任務。回報測試證據、未完成項目與 commit Summary。';
  assert.ok(agents.includes(prompt) && handoff.includes(prompt));
});
check('every policy heading and paragraph appears in HTML', () => {
  const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  for (const block of md.trim().split(/\n\n+/)) {
    if (block === '---' || block.startsWith('- ')) continue;
    const content = block.replace(/^#{1,2} /, '');
    assert.ok(html.includes(escape(content)), 'Missing from HTML: ' + content.slice(0, 100));
  }
});
check('policy links synchronized', () => {
  for (const match of md.matchAll(/\]\((https:\/\/[^)]+)\)/g)) {
    assert.ok(html.includes('href="' + match[1] + '"'));
  }
});
check('no obsolete blanket SDK/deletion/network promises', () => {
  for (const content of [md, html]) {
    assert.ok(!/no third-party\s+SDK of any kind|沒有任何第三方 SDK|makes no network requests at all|erase all of it/i.test(content));
    assert.ok(content.includes('Capacitor Preferences') && content.includes('allowBackup=true'));
    assert.ok(content.includes('resets stage progress only') && content.includes('只重設關卡進度'));
  }
});
check('language anchor targets exist', () => {
  assert.ok(html.includes('id="top"') && html.includes('id="zh"'));
  assert.ok(html.includes('lang="zh-Hant"'));
});
check('Pages publishes policy but not handoff', () => {
  const workflow = read('.github/workflows/pages.yml');
  assert.match(workflow, /cp .*privacy\.html _site\//);
  assert.ok(!/cp .*HANDOFF/.test(workflow));
});
console.log(`${checks} documentation checks passed. Game/runtime/release tests NOT run.`);
