"""Real viewport bounds: every home destination fits; garden sticky tabs mask scrolled content."""
import os, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL)
    c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
    c.set_offline(True)
    p=c.new_page(); errors=[]
    p.on('pageerror',lambda e:errors.append(str(e)))
    session=c.new_cdp_session(p)
    session.send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    initial=p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')
    checks=0
    for w,h in [(320,568),(393,759),(390,844),(568,320),(844,390),(1280,900)]:
        p.set_viewport_size({'width':w,'height':h})
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('v=>{applyLanguage(v);renderTown()}',lang)
            p.locator('#btnHome').tap()
            bounds=p.evaluate('''()=>{
                const m=document.querySelector('#menu'), scene=document.querySelector('#townScene').getBoundingClientRect(), nav=document.querySelector('#hubNav').getBoundingClientRect();
                const buttons=[...document.querySelectorAll('.townPlace')].map(e=>{const r=e.getBoundingClientRect(),s=e.querySelector('span'),t=s.getBoundingClientRect();return {x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height,textFits:s.scrollHeight<=s.clientHeight+1&&s.scrollWidth<=s.clientWidth+1,labelTop:t.top,labelBottom:t.bottom}});
                return {scroll:m.scrollHeight-m.clientHeight,scene:scene.toJSON(),nav:nav.top,buttons};
            }''')
            assert bounds['scroll']<=1,(w,h,lang,bounds)
            for r in bounds['buttons']:
                assert r['w']>=44 and r['h']>=44 and r['textFits'],(w,h,lang,r)
                assert r['y']>=bounds['scene']['top'] and r['bottom']<=bounds['scene']['bottom']+1 and r['bottom']<=bounds['nav'],(w,h,lang,r,bounds)
                assert r['labelTop']>=r['y'] and r['labelBottom']<=r['bottom']+1,(w,h,lang,r)
            for i,a in enumerate(bounds['buttons']):
                for d in bounds['buttons'][i+1:]:
                    assert min(a['right'],d['right'])<=max(a['x'],d['x']) or min(a['bottom'],d['bottom'])<=max(a['y'],d['y']),(w,h,lang,'overlapping destinations',a,d)
            checks+=1
    p.set_viewport_size({'width':393,'height':759})
    p.evaluate("applyLanguage('zh-Hant');renderTown()")
    folder=ARTIFACTS/'viewport-layout';folder.mkdir(exist_ok=True)
    p.screenshot(path=str(folder/'home-portrait.png'))
    p.locator('#navGarden').tap()
    p.locator('#garden').evaluate('e=>e.scrollTop=e.scrollHeight')
    assert p.locator('#gardenActions').evaluate('''e=>{const r=e.getBoundingClientRect(),g=document.querySelector('#garden').getBoundingClientRect();return r.top>=g.top&&r.bottom<document.querySelector('#hubNav').getBoundingClientRect().top&&getComputedStyle(e).backgroundColor!=='rgba(0, 0, 0, 0)'}''')
    p.screenshot(path=str(folder/'garden-scrolled.png'))
    # Browser cutout emulation exercises the CSS env boundary, not Android's native margins.
    session.send('Emulation.setSafeAreaInsetsOverride',{'insets':{'top':32,'bottom':24,'left':0,'right':0}})
    p.locator('#garden').evaluate('e=>e.scrollTop=e.scrollHeight')
    assert p.locator('#garden').evaluate('e=>e.getBoundingClientRect().top')==32
    assert p.locator('.ui').evaluate('e=>{const s=getComputedStyle(e,"::before");return s.height==="32px"&&s.backgroundColor!=="rgba(0, 0, 0, 0)"}'), 'Safe area must mask the underlying game canvas'
    assert p.locator('#gardenActions').evaluate('e=>e.getBoundingClientRect().top')>=32
    assert p.locator('#hubNav button').evaluate_all('es=>es.every(e=>e.getBoundingClientRect().bottom<=innerHeight-24)')
    p.screenshot(path=str(folder/'garden-safe-insets.png'))
    session.send('Emulation.setSafeAreaInsetsOverride',{'insets':{}})
    p.locator('#btnHome').tap()
    p.set_viewport_size({'width':844,'height':390})
    p.screenshot(path=str(folder/'home-landscape.png'))
    assert p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')==initial
    assert not errors,errors
    (ARTIFACTS/'viewport-layout.json').write_text(json.dumps({'layouts':checks,'errors':errors,'offline':True,'cpu':os.getenv('GOO_UI_CPU','1')}))
    b.close()
print('PASS 66 home layouts, visible non-overlapping destinations, garden scroll boundary, unchanged save, offline')
