// Zero-dependency check for this project's plain inline classic scripts.
// Reject missing/unrecognized script forms instead of silently checking zero
// blocks. This is deliberately not a general HTML parser: adding attributes,
// modules or external scripts requires an explicit update to this checker.
const fs = require('fs');
const vm = require('node:vm');
const src = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const blocks = [...src.matchAll(/<script\s*>([\s\S]*?)<\/script\s*>/gi)].map(m => m[1]);
const openings = [...src.matchAll(/<script(?=[\s>/])/gi)].length;
if (!blocks.length || blocks.length !== openings || blocks.every(b => !b.trim())) {
  console.error('SCRIPT ERROR: expected nonempty plain inline <script> blocks; missing, unclosed or unsupported script tag');
  process.exit(1);
}
let ok = true;
blocks.forEach((b, i) => {
  // Parse as a script (without executing), not a function body: top-level
  // return is invalid in the browser even though new Function accepts it.
  try { new vm.Script(b, { filename: 'inline-script-' + i + '.js' }); }
  catch (e) { ok = false; console.log('SYNTAX ERROR in block ' + i + ': ' + e.message); }
});
console.log(ok ? '語法 OK (' + blocks.length + ' 個 script 區塊)' : '語法有錯');
process.exit(ok ? 0 : 1);
