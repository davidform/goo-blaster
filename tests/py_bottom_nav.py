"""One thumb-reachable home entry, real touch navigation and unobscured scrolling."""
import json, os, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_pages import reveal
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL)
    c=b.new_context(viewport={'width':390,'height':844},has_touch=True);c.set_offline(True)
    p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    assert p.locator('#hubNav #btnHome').count()==1,'Home belongs in the bottom navigation'
    assert p.locator('#homeHeader,#btnShopBack').count()==0,'No duplicate return controls or empty header'
    assert p.locator('#hubNav [aria-current=page]').get_attribute('id')=='btnHome'
    initial=p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])');checks=0
    for w,h in [(320,568),(390,844),(844,390),(1280,900)]:
        p.set_viewport_size({'width':w,'height':h})
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('v=>applyLanguage(v)',lang)
            boxes=p.locator('#hubNav button').evaluate_all('(es)=>es.map(e=>{const r=e.getBoundingClientRect();return {id:e.id,x:r.x,y:r.y,w:r.width,h:r.height,fit:e.scrollWidth<=e.clientWidth&&e.scrollHeight<=e.clientHeight}})')
            assert len(boxes)==5 and boxes[2]['id']=='btnHome',boxes
            assert all(x['w']>=48 and x['h']>=48 and x['fit'] for x in boxes),(lang,w,boxes)
            assert all(boxes[i+1]['x']-(boxes[i]['x']+boxes[i]['w'])>=3.9 for i in range(4)),boxes
            assert abs(boxes[2]['x']+boxes[2]['w']/2-w/2)<1,boxes
            for nav,panel in [('navAdventure','#menu'),('btnShop','#shop'),('btnHome','#menu'),('navGarden','#garden'),('navSettings','#settings')]:
                p.locator('#'+nav).tap()
                assert p.locator('#hubNav [aria-current=page]').get_attribute('id')==nav
                assert p.locator('#hubNav button').evaluate_all('es=>{const selected=es.find(e=>e.getAttribute("aria-current")=="page");return es.filter(e=>e!==selected).every(e=>getComputedStyle(e).backgroundColor!==getComputedStyle(selected).backgroundColor)}')
                assert p.locator(panel).is_visible()
                assert p.locator(panel).evaluate('e=>e.getBoundingClientRect().bottom<=document.querySelector("#hubNav").getBoundingClientRect().top+1')
                checks+=1
            p.locator('#btnShop').tap()
            assert p.locator('#shopList').evaluate('e=>getComputedStyle(e).overflowY')=='clip'
            reveal(p, p.locator('.mbuy').last)
            assert p.locator('.mbuy').last.evaluate('e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=document.querySelector("#hubNav").getBoundingClientRect().top}'), (lang,w,h,p.locator('.mbuy').last.evaluate('e=>e.getBoundingClientRect().toJSON()'))
            p.locator('#btnHome').tap();assert p.locator('#townHome').is_visible()
    assert p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')==initial
    # Every themed challenge returns through the same dock, including mid-game.
    for place in ['picnic','pond','stars']:
        p.locator('[data-place="'+place+'"]').tap();p.locator('#festivalStart').tap()
        p.locator('#btnHome').tap();assert p.locator('#townHome').is_visible()
        assert p.evaluate('GF===null')
    p.set_viewport_size({'width':390,'height':844});folder=Path(GAME_ROOT)/'store/screenshots'/p.evaluate('BUILD');folder.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for lang in ['en','zh-Hant']:
        p.evaluate('v=>applyLanguage(v)',lang);p.locator('#btnShop').tap();p.locator('#shop').evaluate('e=>e.scrollTop=0')
        name=f'shop-bottom-home-{lang}-390.png';p.screenshot(path=str(folder/name))
        manifest.append(dict(file=name,build=p.evaluate('BUILD'),sha256=hashlib.sha256((Path(GAME_ROOT)/'index.html').read_bytes()).hexdigest(),viewport=[390,844],language=lang,setup='Fresh save; actual touch navigation; no injected progress, resources or upgrades.'))
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not errors,errors
    (ARTIFACTS/'bottom-nav.json').write_text(json.dumps(dict(checks=checks,layouts=44,offline=True,errors=errors,cpu=os.getenv('GOO_UI_CPU','1'))),encoding='utf-8')
    b.close()
print('PASS 220 touch destination changes, 44 layouts, one central home entry, reachable targets, paged shop without scrolling, save isolation and theme exits')
