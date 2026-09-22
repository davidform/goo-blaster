"""Capture real planting choices after earning the first cottage upgrade via UI."""
import hashlib
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
build = re.search(r"const BUILD='([^']+)'", (root / 'index.html').read_text(encoding='utf8'))[1]
out = root / 'store/screenshots' / build
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch(channel='msedge')
    c = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True)
    c.set_offline(True)
    c.add_init_script('window.__captureNow=Date.now();Date.now=()=>window.__captureNow')
    p = c.new_page()
    errors = []
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.goto((root / 'index.html').as_uri())
    p.locator('#navGarden').click()
    for _ in range(4):
        p.locator('#gardenQuestAction').click()
        p.evaluate('window.__captureNow+=60000;gardenRefreshTimers()')
        p.locator('#gardenQuestAction').click()
    p.locator('#gardenQuestAction').click()
    assert p.evaluate('GARDEN.house===1&&GARDEN.petals===0')
    p.locator('#gardenQuestCrop').select_option('1')
    assert '4:30' in p.locator('#gardenQuestDetail').inner_text()
    for lang in ['en', 'zh-Hant']:
        p.evaluate('lang=>{applyLanguage(lang);renderGarden();document.getElementById("garden").scrollTop=0}', lang)
        p.screenshot(path=str(out / f'cottage-level1-{lang}.png'))
    p.locator('#gardenQuestAction').click()
    p.screenshot(path=str(out / 'cottage-level1-countdown.png'))
    assert not errors, errors
    (out / 'manifest.json').write_text(json.dumps({
        'build': p.evaluate('BUILD'),
        'sha256': hashlib.sha256((root / 'index.html').read_bytes()).hexdigest(),
        'method': 'Fresh offline browser save. Four mint cycles and first cottage restoration through UI, then berry selection. Only waiting time accelerated; no resources, upgrades or saves injected. Unretouched browser screenshots; not Pixel.',
        'errors': errors,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    b.close()
