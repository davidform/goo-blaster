"""Offline packaged HTML, CPU 4x, fresh save, and real browser restart.

This validates the web payload only; it is not Android device verification.
"""
from pathlib import Path
import json
import tempfile
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

profile = tempfile.mkdtemp(prefix='release-profile-', dir=ARTIFACTS)
url = (Path(GAME_ROOT) / 'index.html').as_uri()
errors, network = [], []
with sync_playwright() as pw:
    def launch():
        context = pw.chromium.launch_persistent_context(profile, channel=BROWSER_CHANNEL,
            headless=True, viewport={'width':390, 'height':844}, is_mobile=True, has_touch=True)
        context.set_offline(True)
        context.on('request', lambda request: network.append(request.url)
                   if request.url.startswith(('http:', 'https:')) else None)
        page = context.pages[0]
        page.on('pageerror', lambda error: errors.append(str(error)))
        session = context.new_cdp_session(page)
        session.send('Emulation.setCPUThrottlingRate', {'rate':4})
        page.goto(url)
        page.wait_for_function("typeof BUILD !== 'undefined' && typeof PROGRESS !== 'undefined' && document.querySelector('#btnPlay').textContent.length > 0")
        return context, page
    context, page = launch()
    initial = page.evaluate('({build:BUILD, progress:PROGRESS, coins:COINS, meta:META})')
    assert initial['progress'] == 1 and initial['coins'] == 0 and not initial['meta'], initial
    page.screenshot(path=str(ARTIFACTS / 'release-offline-menu.png'))
    page.click('#btnPlay')
    page.mouse.move(195, 500)
    page.mouse.down()
    page.mouse.move(250, 500, steps=8)
    page.wait_for_function('G.running && G.t >= 3', timeout=120000)
    page.mouse.up()
    page.screenshot(path=str(ARTIFACTS / 'release-offline-game.png'))
    page.evaluate('PROGRESS=9; COINS=456; META={dmg:2}; saveGame()')
    context.close()
    context, page = launch()
    restored = page.evaluate('({progress:PROGRESS, coins:COINS, meta:META, selection:SEL_IDX})')
    assert restored == dict(progress=9, coins=456, meta={'dmg':2}, selection=8), restored
    context.close()
assert not errors, errors
assert not network, network
print(json.dumps(dict(initial=initial, restored=restored, errors=errors,
                      external_requests=network, cpu_slowdown=4), indent=2))
print('PASS offline payload, fresh save, CPU 4x and persistent browser restart')
