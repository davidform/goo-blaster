"""Diagnostic: same-batch previous committed build versus current art, run alone.

Does not replace py_v0927_perf or actual phone profiling.
"""
import ast
import asyncio
import datetime
import functools
import hashlib
import http.server
import json
import socketserver
import subprocess
import threading
from pathlib import Path
from playwright.async_api import async_playwright
from test_paths import ARTIFACTS, REPO, GAME_ROOT, BROWSER_CHANNEL

tree=ast.parse((REPO/'tests/py_v0927_perf.py').read_text(encoding='utf-8'))
worst=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name) and t.id=='WORST' for t in n.targets))
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
root=ARTIFACTS/('art-perf-'+stamp)
sources={'old':subprocess.check_output(['git','show','8c5bebd:index.html'],cwd=REPO),
         'current':(Path(GAME_ROOT)/'index.html').read_bytes()}
for name,source in sources.items():
    (root/name).mkdir(parents=True,exist_ok=True)
    (root/name/'index.html').write_bytes(source)
server=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start()

async def main():
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(channel=BROWSER_CHANNEL)
        async def sample(name):
            context=await browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
            try:
                await context.add_init_script('let seed=12345; Math.random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);')
                page=await context.new_page()
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                await page.goto(f'http://127.0.0.1:{server.server_address[1]}/{name}/index.html')
                await page.evaluate(worst,[True])
                await page.wait_for_function('G.E.length>=100 && G.ALLY.length===3')
                await page.evaluate('''()=>{window.__cost={d:[],u:[]};const d=draw,u=update;
                    draw=function(){const t=performance.now();d();__cost.d.push(performance.now()-t);};
                    update=function(...args){const t=performance.now();u(...args);__cost.u.push(performance.now()-t);};}''')
                initial=await page.evaluate('({frames:__frames,time:performance.now()})')
                # Fixed window is for FPS measurement, never a state assertion.
                await page.wait_for_timeout(8000)
                result=await page.evaluate('''s=>({build:BUILD,frames:__frames-s.frames,seconds:(performance.now()-s.time)/1000,
                    draw_ms:__cost.d.reduce((a,b)=>a+b,0)/__cost.d.length,
                    update_ms:__cost.u.reduce((a,b)=>a+b,0)/__cost.u.length,allies:G.ALLY.length})''',initial)
                result.update(fps=round(result['frames']/result['seconds'],2),errors=errors)
                assert not errors and result['allies']==3,result
                return result
            finally:
                await context.close()
        single=[];paired=[]
        for i in range(3):
            order=['old','current'] if i%2==0 else ['current','old']
            single.append({name:await sample(name) for name in order})
            paired.append(dict(zip(['old','current'],await asyncio.gather(sample('old'),sample('current')))))
        await browser.close()
    result={'single':single,'paired':paired,'sha256':{k:hashlib.sha256(v).hexdigest() for k,v in sources.items()},'diagnostic_only':True}
    (root/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));print('Evidence:',root/'results.json')
try:
    asyncio.run(main())
finally:
    server.shutdown()
