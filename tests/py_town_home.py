"""Town hub: real navigation, translated hit targets, save isolation and motion."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL
errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
 p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.wait_for_function("document.querySelectorAll('.townPlace').length===6")
 initial=p.evaluate('JSON.stringify({COINS,META,PROGRESS,GARDEN})')
 assert p.evaluate('LANG')=='en'
 p.screenshot(path=str(ARTIFACTS/'town74-mobile.png'))
 for place,selector in [('shop','#shop'),('house','#gardenQuest'),('picnic','.festivalPanel.theme0'),('pond','.festivalPanel.theme1'),('stars','.festivalPanel.theme2')]:
  p.locator('[data-place="'+place+'"]').click();assert p.locator(selector).is_visible(),place
  p.locator('#navAdventure').click();assert p.locator('#townHome').is_visible()
 assert p.evaluate('JSON.stringify({COINS,META,PROGRESS,GARDEN})')==initial
 p.locator('[data-place="gate"]').click();p.locator('#btnPlay').click();p.wait_for_function('G.running && G.t>1',timeout=120000)
 assert p.locator('#townHome').is_hidden()
 p.evaluate('G.running=false;showMenu()')
 checks=0
 for w,h in [(320,568),(390,844),(844,390),(1280,900)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('(v)=>{applyLanguage(v);renderStage()}',lang)
   assert p.locator('#menu').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(lang,w)
   assert p.locator('.townPlace').evaluate_all("es=>es.every(e=>e.getBoundingClientRect().width>=44 && e.getBoundingClientRect().height>=44 && e.scrollWidth<=e.clientWidth+1 && e.querySelector('span').textContent===e.getAttribute('aria-label'))"),(lang,w)
   assert p.evaluate("[...document.querySelectorAll('.townPlace')].every(e=>L10N[LANG][e.dataset.label] && e.querySelector('span').textContent===T(e.dataset.label))"),(lang,w)
   checks+=1
 p.evaluate("applyLanguage('en');renderStage()");p.locator('#menu').evaluate('e=>e.scrollTop=0');p.screenshot(path=str(ARTIFACTS/'town74-wide.png'))
 p.emulate_media(reduced_motion='reduce')
 assert p.locator('.townResident').first.evaluate("e=>getComputedStyle(e).animationName")=='none'
 p.evaluate('PROGRESS=51;COINS=999999;GARDEN.seeds=999;GARDEN.petals=999;showMenu()')
 assert p.locator('#townResources').inner_text().count('999')==2
 p.set_viewport_size({'width':390,'height':844});p.evaluate("applyLanguage('zh-Hant');renderStage()");p.locator('#menu').evaluate('e=>e.scrollTop=0');p.screenshot(path=str(ARTIFACTS/'town74-zh.png'))
 assert not errors,errors
 print(json.dumps({'layouts':checks,'errors':errors,'cpu':os.environ.get('GOO_UI_CPU','1'),'save_unchanged_by_navigation':True}))
 b.close()
