"""Offline packaged HTML, CPU 4x, fresh save, and real browser restart.

This validates the web payload only; it is not Android device verification.
"""
from pathlib import Path
import json
import tempfile
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL


def main():
    url = (Path(GAME_ROOT) / 'index.html').as_uri()
    errors, network = [], []
    result = dict(status='failed', phase='launch', cpu_slowdown=4)
    # The profile is disposable even when a browser assertion fails. Do not
    # upload profiles: only the explicit logs, result JSON and screenshots.
    with tempfile.TemporaryDirectory(prefix='release-profile-', dir=ARTIFACTS) as profile:
        with sync_playwright() as pw:
            context, page = None, None

            def launch():
                nonlocal context, page
                context = pw.chromium.launch_persistent_context(
                    profile, channel=BROWSER_CHANNEL, headless=True,
                    viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
                context.set_offline(True)
                context.on('request', lambda request: network.append(request.url)
                           if request.url.startswith(('http:', 'https:')) else None)
                page = context.pages[0]
                page.on('pageerror', lambda error: errors.append(str(error)))
                session = context.new_cdp_session(page)
                session.send('Emulation.setCPUThrottlingRate', {'rate': 4})
                page.goto(url)
                page.wait_for_function("typeof BUILD !== 'undefined' && typeof PROGRESS !== 'undefined' && document.querySelector('#btnPlay').textContent.length > 0")

            try:
                launch()
                result['phase'] = 'fresh-save'
                initial = page.evaluate('({build:BUILD, progress:PROGRESS, coins:COINS, meta:META})')
                result['initial'] = initial
                assert initial['progress'] == 1 and initial['coins'] == 0 and not initial['meta'], initial
                page.screenshot(path=str(ARTIFACTS / 'release-offline-menu.png'))
                result['phase'] = 'gameplay'
                # The current hub opens on Home; follow the same route as a player.
                page.click('#navAdventure')
                page.click('#btnPlay')
                page.mouse.move(195, 500)
                page.mouse.down()
                page.mouse.move(250, 500, steps=8)
                page.wait_for_function('G.running && G.t >= 3', timeout=120000)
                page.mouse.up()
                result['game_time'] = page.evaluate('G.t')
                page.screenshot(path=str(ARTIFACTS / 'release-offline-game.png'))
                result['phase'] = 'save-restart'
                page.evaluate('PROGRESS=9; COINS=456; META={dmg:2}; saveGame()')
                context.close()
                context, page = None, None
                launch()
                restored = page.evaluate('({progress:PROGRESS, coins:COINS, meta:META, selection:SEL_IDX})')
                result['restored'] = restored
                assert restored == dict(progress=9, coins=456, meta={'dmg': 2}, selection=8), restored
                context.close()
                context, page = None, None
                assert not errors, errors
                assert not network, network
                result.update(status='passed', phase='complete')
            except Exception as error:
                result['failure'] = str(error)
                if page is not None and not page.is_closed():
                    try:
                        page.screenshot(path=str(ARTIFACTS / 'release-offline-failure.png'), timeout=5000)
                    except Exception as screenshot_error:
                        result['screenshot_error'] = str(screenshot_error)
                raise
            finally:
                try:
                    if context is not None:
                        context.close()
                finally:
                    result.update(errors=errors, external_requests=network)
                    (ARTIFACTS / 'release-smoke-result.json').write_text(
                        json.dumps(result, indent=2) + '\n', encoding='utf-8')
                    print(json.dumps(result, indent=2), flush=True)
    print('PASS offline payload, fresh save, CPU 4x and persistent browser restart')


if __name__ == '__main__':
    main()
