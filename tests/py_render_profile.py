"""Diagnostic only: single-page render-cost experiments; never a release gate.

Uses disposable browser contexts. Reduced resolution / shadow removal do not
modify the game file. Rendering call duration excludes asynchronous GPU work.
"""
import ast
import asyncio
import datetime
import functools
import hashlib
import http.server
import json
from pathlib import Path
import socketserver
import threading
from playwright.async_api import async_playwright
from test_paths import ARTIFACTS, BROWSER_CHANNEL, GAME_ROOT, REPO

tree = ast.parse((REPO/'tests/py_v0927_perf.py').read_text(encoding='utf-8'))
worst = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'WORST' for t in n.targets))

async def sample(browser, url, mode):
    context = await browser.new_context(viewport={'width':390,'height':844},
        device_scale_factor=1 if mode=='dpr1' else 2, is_mobile=True, has_touch=True)
    try:
        await context.add_init_script('let seed=12345; Math.random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);')
        if mode == 'no-shadow':
            await context.add_init_script('''const p=CanvasRenderingContext2D.prototype;
                const d=Object.getOwnPropertyDescriptor(p,'shadowBlur');
                Object.defineProperty(p,'shadowBlur',{...d,set(v){d.set.call(this,0)}});''')
        page = await context.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.goto(url)
        await page.evaluate(worst,[True])
        await page.wait_for_function('G.E.length>=100 && G.ALLY.length===3')
        await page.wait_for_timeout(1500)
        await page.evaluate('''()=>{
            window.__measure={draw:[],update:[],gaps:[],counts:[]};
            const d=draw,u=update;
            let last=performance.now();
            draw=function(){const t=performance.now();__measure.gaps.push(t-last);last=t;
                d();__measure.draw.push(performance.now()-t);
                __measure.counts.push([G.E.length,G.B.length,G.GOO.length,G.PT.length]);};
            update=function(...a){const t=performance.now();u(...a);__measure.update.push(performance.now()-t);};
            window.__start=performance.now();
        }''')
        # Measurement interval; all game-state requirements are polled above.
        await page.wait_for_timeout(8000)
        result=await page.evaluate('''()=>{
            clearInterval(__k);
            const seconds=(performance.now()-__start)/1000;
            const stats=a=>{a=a.slice().sort((x,y)=>x-y);return {mean:a.reduce((x,y)=>x+y,0)/a.length,p95:a[Math.floor(a.length*.95)],max:a[a.length-1]};};
            return {seconds,frames:__measure.draw.length,fps:__measure.draw.length/seconds,
                drawCallMs:stats(__measure.draw),updateCallMs:stats(__measure.update),
                frameGapMs:stats(__measure.gaps.slice(1)),
                meanCounts:__measure.counts[0].map((_,i)=>__measure.counts.reduce((s,c)=>s+c[i],0)/__measure.counts.length),
                countOrder:['enemies','playerBullets','goo','particles'],
                canvas:[cv.width,cv.height],allies:G.ALLY.length,build:BUILD};
        }''')
        result.update(mode=mode,errors=errors)
        assert result['frames']>0 and result['allies']==3 and not errors, result
        return result
    finally:
        await context.close()

async def main(url):
    report={'diagnostic_only':True,'sha256':hashlib.sha256((Path(GAME_ROOT)/'index.html').read_bytes()).hexdigest(),'rounds':[]}
    output=ARTIFACTS/('render-profile-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(channel=BROWSER_CHANNEL)
        try:
            report['browser']=browser.version
            report['gpu']=(await (await browser.new_browser_cdp_session()).send('SystemInfo.getInfo'))['gpu']['featureStatus']
            for modes in [('baseline','no-shadow','dpr1'),('dpr1','baseline','no-shadow'),('no-shadow','dpr1','baseline')]:
                row=[]
                for mode in modes:
                    r=await sample(browser,url,mode)
                    row.append(r)
                    print(mode,round(r['fps'],2),'FPS',flush=True)
                report['rounds'].append(row)
                output.write_text(json.dumps(report,indent=2),encoding='utf-8')
        finally:
            await browser.close()
    print(output,flush=True)

if __name__=='__main__':
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=GAME_ROOT)
    with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            asyncio.run(main(f'http://127.0.0.1:{server.server_address[1]}/index.html'))
        finally:
            server.shutdown()
