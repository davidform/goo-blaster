const { test } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, writeFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');
const { spawnSync } = require('node:child_process');

const cases = [
  ['valid script is parsed, not executed', '<script>throw new Error("do not execute")</script>', 0],
  ['case and whitespace', '<SCRIPT >const x = 1;</SCRIPT >', 0],
  ['multiple scripts', '<script>let x=1</script><script>let y=2</script>', 0],
  ['syntax error', '<script>const x = ;</script>', 1],
  ['top-level return', '<script>return 1;</script>', 1],
  ['no script', '<html>missing game</html>', 1],
  ['empty script', '<script>  </script>', 1],
  ['unclosed script', '<script>let x=1', 1],
  ['attributed script cannot be skipped', '<script type="text/javascript">const x = ;</script>', 1],
  ['mixed forms cannot hide a bad script', '<script>let x=1</script><script type="text/javascript">const y = ;</script>', 1],
  ['external script is unsupported', '<script src="game.js"></script>', 1],
  ['module script is unsupported', '<script type="module">export const x=1</script>', 1],
];

for (const [name, html, status] of cases) {
  test(name, () => {
    const dir = mkdtempSync(join(tmpdir(), 'goo-syntax-'));
    try {
      const file = join(dir, 'index.html');
      writeFileSync(file, html);
      const result = spawnSync(process.execPath, [join(__dirname, 'syntax_check.js'), file],
        { encoding: 'utf8', timeout: 5000 });
      assert.ifError(result.error);
      assert.equal(result.status, status, result.stdout + result.stderr);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
}
