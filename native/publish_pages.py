"""Promote the verified itch release to main; GitHub Actions deploys Pages."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/davidform/goo-blaster.git'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def validate(commit, receipt, reports, payload):
    source = git('rev-parse', '--verify', commit + '^{commit}').decode().strip()
    tracked = git('show', source + ':index.html')
    if tracked.replace(b'\r\n', b'\n') != payload.replace(b'\r\n', b'\n'):
        raise ValueError('Artifact differs from the specified source commit')
    digest = hashlib.sha256(payload).hexdigest()
    build = re.search(rb"const BUILD='([^']+)'", payload)[1].decode()
    if not (receipt.get('page') == 'https://davidform.itch.io/goo-blaster'
            and receipt.get('channel') == 'html5'
            and receipt.get('build') == build
            and receipt.get('game_sha256') == digest
            and receipt.get('game_payload_identical') is True
            and receipt.get('browser_start_verified') is True):
        raise ValueError('Verified itch release must match the exact commit payload')
    shell = git('show', source + ':run_tests.sh').decode().split('\nelse\n', 1)[1]
    required = {n for key in ['PY', 'JS', 'SOLO'] for n in
                re.search(r'\b' + key + r'="([^"]*)"', shell)[1].replace('\\\n', ' ').split()}
    if not reports or set(reports[0]['planned']) != required:
        raise ValueError('Full suite for the release commit is required')
    merged = {}
    for report in reports:
        if not (report['complete'] and report['source_unchanged'] and report['sha256'] == digest):
            raise ValueError('Report payload differs or run is incomplete')
        names = [r['test'] for r in report['results']]
        if len(names) != len(set(names)) or set(names) != set(report['planned']) or not set(names) <= required:
            raise ValueError('Invalid result list')
        merged.update({r['test']: r['passed'] and r['exit_code'] == 0 and not r['printed_failure']
                       for r in report['results']})
    if set(merged) != required or not all(merged.values()):
        raise ValueError('Every release test must pass')
    return {'source_commit': source, 'build': build, 'sha256': digest, 'tests': len(required)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--itch-receipt', type=Path, required=True)
    parser.add_argument('--tests', type=Path, required=True)
    parser.add_argument('--retry', type=Path, action='append', default=[])
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    if git('remote', 'get-url', 'origin').decode().strip() != REPO:
        raise ValueError('Unexpected repository')
    config = json.loads((ROOT / 'studio.project.json').read_text(encoding='utf-8'))
    if config['authorization'].get('pages_distribution') is not True:
        raise ValueError('Pages publication is not authorized')
    read = lambda p: json.loads(p.read_text(encoding='utf-8'))
    payload = args.artifact.read_bytes()
    proof = validate(args.commit, read(args.itch_receipt), [read(p) for p in [args.tests, *args.retry]], payload)
    if args.publish:
        git('fetch', 'origin', 'main')
        parent = git('rev-parse', 'origin/main').decode().strip()
        old = git('show', parent + ':index.html')
        old_version = re.search(rb"const BUILD='v([\d.]+)'", old)[1].decode()
        if tuple(map(int, proof['build'][1:].split('.'))) < tuple(map(int, old_version.split('.'))):
            raise ValueError('Refusing a version downgrade')
        if old == payload:
            proof['deployment_commit'] = parent
        else:
            # Isolated Git index: preserve the working tree and upload the tested bytes
            # exactly, including Windows mixed line endings. Never run clean filters.
            with tempfile.TemporaryDirectory() as directory:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
                def staging(*command, data=None):
                    return subprocess.check_output(['git', *command], input=data, cwd=ROOT, env=env)
                staging('read-tree', parent)
                files = ['index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'privacy.html', '.nojekyll']
                for name in files:
                    content = payload if name == 'index.html' else (b'' if name == '.nojekyll' else git('show', proof['source_commit'] + ':' + name))
                    blob = staging('hash-object', '-w', '--stdin', data=content).decode().strip()
                    staging('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + name)
                tree = staging('write-tree').decode().strip()
                message = 'build: publish verified ' + proof['build'] + ' to GitHub Pages\n\nSource: ' + proof['source_commit'] + '\nSHA256: ' + proof['sha256'] + '\n'
                deployment = staging('commit-tree', tree, '-p', parent, data=message.encode()).decode().strip()
            git('push', 'origin', deployment + ':refs/heads/main')
            proof['deployment_commit'] = deployment
    proof['pushed'] = args.publish
    print(json.dumps(proof, indent=2))
    # Push is not deployment evidence: verify Actions and the public payload separately.

if __name__ == '__main__':
    main()
