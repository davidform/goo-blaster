"""Diagnostic: measure the existing worst scene alone and in paired pages.

Run alone. This does not change or replace py_v0927_perf acceptance gates.
"""
import ast
import asyncio
import datetime
import functools
import hashlib
import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.async_api import async_playwright
from test_paths import ARTIFACTS, BROWSER_CHANNEL, GAME_ROOT, REPO

tree = ast.parse((REPO / 'tests/py_v0927_perf.py').read_text(encoding='utf-8'))
worst = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'WORST' for t in n.targets))


async def measure(browser, url, ally):
    context = await browser.new_context(viewport={'width': 390, 'height': 844},
                                        device_scale_factor=2, is_mobile=True, has_touch=True)
    try:
        await context.add_init_script('let seed=12345; Math.random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);')
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        await page.goto(url)
        await page.evaluate(worst, [ally])
        await page.wait_for_function('ally => G.E.length >= 100 && (!ally || G.ALLY.length === 3)', arg=ally)
        # Fixed duration is a measurement window, never a game-state assertion.
        await page.wait_for_timeout(1500)
        initial = await page.evaluate('({f:__frames,t:performance.now()})')
        await page.wait_for_timeout(8000)
        result = await page.evaluate('''s=>{
            clearInterval(__k);
            return {frames:__frames-s.f,seconds:(performance.now()-s.t)/1000,
                    enemies:G.E.length,bullets:G.B.length,allies:G.ALLY.length,
                    visibility:document.visibilityState,build:BUILD};
        }''', initial)
        result.update(fps=round(result['frames']/result['seconds'], 2), errors=errors, with_ally=ally)
        assert not errors, errors
        assert result['frames'] > 0 and (not ally or result['allies'] == 3), result
        return result
    finally:
        await context.close()


async def main(url):
    report = dict(diagnostic_only=True, browser_channel=BROWSER_CHANNEL,
                  sha256=hashlib.sha256((Path(GAME_ROOT)/'index.html').read_bytes()).hexdigest(), rounds=[])
    output = ARTIFACTS / ('perf-capacity-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.json')
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(channel=BROWSER_CHANNEL, args=['--autoplay-policy=no-user-gesture-required'])
        try:
            report['gpu'] = (await (await browser.new_browser_cdp_session()).send('SystemInfo.getInfo'))['gpu']['featureStatus']
            for i in range(3):
                # Reverse mode order to expose warm-up/order effects.
                row = {}
                for mode in (['single', 'paired'] if i % 2 == 0 else ['paired', 'single']):
                    if mode == 'paired':
                        row[mode] = await asyncio.gather(measure(browser, url, False), measure(browser, url, True))
                    else:
                        row[mode] = [await measure(browser, url, ally) for ally in ([False, True] if i % 2 == 0 else [True, False])]
                report['rounds'].append(row)
                output.write_text(json.dumps(report, indent=2), encoding='utf-8')
                print(json.dumps(row), flush=True)
        finally:
            await browser.close()
    print(output, flush=True)


if __name__ == '__main__':
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=GAME_ROOT)
    with socketserver.TCPServer(('127.0.0.1', 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            asyncio.run(main(f'http://127.0.0.1:{server.server_address[1]}/index.html'))
        finally:
            server.shutdown()
