// Prepare: node tools/publish_itch.cjs
// Publish only after the required game tests pass for this exact SHA256:
// node tools/publish_itch.cjs --push --verified-sha256 <tested index.html SHA256>
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const push = args.includes('--push');
const hashIndex = args.indexOf('--verified-sha256');
const verified = hashIndex >= 0 ? args[hashIndex + 1] : '';
const source = fs.readFileSync(path.join(root, 'index.html'));
const hash = crypto.createHash('sha256').update(source).digest('hex');
const version = source.toString('utf8').match(/const BUILD='(v[\d.]+)'/)[1];
const target = 'davidform/goo-blaster:html5';
if (push && (!verified || verified.toLowerCase() !== hash)) {
  console.error('STOP: provide the SHA256 of index.html that passed the required game tests.');
  process.exit(1);
}
// A fresh directory containing only the game prevents accidental document/key uploads.
const outputRoot = path.join(root, '_private', 'itch-builds');
fs.mkdirSync(outputRoot, { recursive: true });
const output = fs.mkdtempSync(path.join(outputRoot, version + '-'));
fs.writeFileSync(path.join(output, 'index.html'), source);
const stagedHash = crypto.createHash('sha256').update(fs.readFileSync(path.join(output, 'index.html'))).digest('hex');
if (stagedHash !== hash) throw new Error('Staged content differs from source');
console.log(JSON.stringify({ version, sha256: hash, target, directory: output, files: fs.readdirSync(output) }, null, 2));
if (!push) {
  console.log('Prepared only. No upload performed; game tests not run by this script.');
  process.exit(0);
}
const butler = path.join(root, '_private', 'butler', 'butler.exe');
if (!fs.existsSync(butler)) throw new Error('Install official butler in _private/butler first.');
const result = spawnSync(butler, ['push', output, target, '--userversion', version], { stdio: 'inherit' });
if (result.error) throw result.error;
process.exit(result.status ?? 1);
