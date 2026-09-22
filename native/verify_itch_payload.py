"""Read-only verification of this project's public itch payload; no login or upload."""
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('url')
args = parser.parse_args()
match = re.fullmatch(r'https://html-classic\.itch\.zone/html/19167726-(\d+)/index\.html(?:\?[^\s]*)?', args.url)
assert match, 'Only the existing public upload for this project is accepted'
with urllib.request.urlopen(args.url, timeout=60) as response:
    payload = response.read()
base = (root / 'index.html').read_bytes()
assert payload.startswith(base), 'Public game differs from tested source'
suffix = payload[len(base):].strip()
assert suffix == b'<script defer src="https://static.itch.io/htmlgame.js" type="text/javascript"></script>'
version = re.search(rb"const BUILD='([^']+)'", base)[1].decode()
proof = dict(build=version, page='https://davidform.itch.io/goo-blaster', url=args.url,
             channel='html5', upload_id=19167726, build_id=int(match[1]),
             game_sha256=hashlib.sha256(base).hexdigest(), public_sha256=hashlib.sha256(payload).hexdigest(),
             game_payload_identical=True, platform_suffix=suffix.decode(), browser_start_verified=False)
path = root / '_private/mobile-test' / ('itch-v' + version.split('.')[-1] + '.json')
path.write_text(json.dumps(proof, indent=2), encoding='utf8')
print(path)
print(json.dumps(proof, indent=2))
