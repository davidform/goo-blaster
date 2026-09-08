"""Diagnostic only: same-batch v0.9.31/current worst-scene comparison.

Does not replace or relax py_v0927_perf acceptance thresholds. Run alone.
"""
import ast
import asyncio
import functools
import http.server
import json
from pathlib import Path
import socketserver
import subprocess
import threading
from playwright.async_api import async_playwright
from test_paths import REPO, ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

tree = ast.parse((REPO / 'tests/py_v0927_perf.py').read_text(encoding='utf-8'))
worst = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'WORST' for t in n.targets))
root = ARTIFACTS / 'perf-baseline'
for version in ['old','current']:
    (root / version).mkdir(parents=True, exist_ok=True)
(root / 'old/index.html').write_bytes(subprocess.check_output(['git','show','bc1951a:index.html'],cwd=REPO))
(root / 'current/index.html').write_bytes((Path(GAME_ROOT)/'index.html').read_bytes())
socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(('127.0.0.1',0), functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(channel=BROWSER_CHANNEL)
        gpu = await (await browser.new_browser_cdp_session()).send('SystemInfo.getInfo')
        async def sample(version):
            context = await browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
            await context.add_init_script('let seed=12345; Math.random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);')
            page = await context.new_page()
            await page.goto(f'http://127.0.0.1:{server.server_address[1]}/{version}/index.html')
            await page.evaluate(worst,[True])
            # A sampling window, not a fixed delay used to assert game state.
            await page.wait_for_timeout(2000)
            initial = await page.evaluate('({frames:__frames,time:performance.now()})')
            await page.wait_for_timeout(12000)
            result = await page.evaluate('s=>({build:BUILD,frames:__frames-s.frames,seconds:(performance.now()-s.time)/1000,enemies:G.E.length,allies:G.ALLY.length})', initial)
            result['fps'] = round(result['frames']/result['seconds'],2)
            await context.close()
            return result
        rounds = []
        for _ in range(3):
            rounds.append(await asyncio.gather(sample('old'),sample('current')))
        await browser.close()
        report = dict(rounds=rounds,gpu=gpu['gpu']['featureStatus'],diagnostic_only=True)
        (ARTIFACTS/'perf-baseline.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2))
try:
    asyncio.run(main())
finally:
    server.shutdown()
