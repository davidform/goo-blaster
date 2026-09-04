// 語法檢查：把 index.html 裡的 <script> 區塊丟給 new Function() 解析，
// 有語法錯誤就會拋例外。比人工看快也可靠。
const fs = require('fs');
const src = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const blocks = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let ok = true;
blocks.forEach((b, i) => {
  try { new Function(b); }
  catch (e) { ok = false; console.log('SYNTAX ERROR in block ' + i + ': ' + e.message); }
});
console.log(ok ? '語法 OK (' + blocks.length + ' 個 script 區塊)' : '語法有錯');
process.exit(ok ? 0 : 1);
