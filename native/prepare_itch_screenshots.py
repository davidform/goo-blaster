"""Capture real release UI in a fresh offline browser; never reads player saves."""
import hashlib
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'index.html'
before = source.read_bytes()
build = re.search(rb"const BUILD='([^']+)'", before)[1].decode()
out = ROOT / 'store' / 'screenshots' / build
out.mkdir(parents=True, exist_ok=True)
errors = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=os.environ.get('GOO_BROWSER_CHANNEL', 'msedge'))
    context = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True)
    context.set_offline(True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(source.as_uri())
    assert page.evaluate('BUILD') == build
    page.screenshot(path=str(out / 'adventure.png'))
    page.locator('#navGarden').click()
    page.locator('.gardenPlot button').first.click()
    page.screenshot(path=str(out / 'garden.png'))
    page.locator('#navAdventure').click()
    page.locator('#btnPlay').click()
    page.touchscreen.tap(195, 430)
    page.keyboard.down('ArrowRight')
    page.wait_for_function('G.running && G.t >= 4', timeout=30000)
    page.keyboard.up('ArrowRight')
    page.wait_for_function('G.running && G.t >= 20', timeout=60000)
    page.screenshot(path=str(out / 'gameplay.png'))
    state = page.evaluate('({time:G.t,hearts:G.P.hearts,stage:G.lvIdx+1})')
    browser.close()
assert not errors, errors
assert source.read_bytes() == before
manifest = {'build': build, 'source_sha256': hashlib.sha256(before).hexdigest(),
            'capture': 'Fresh offline save; planted first crop via UI; stage 1 real-time gameplay without stat changes.',
            'gameplay': state, 'page_errors': errors,
            'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.png'))}}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps(manifest, indent=2))
