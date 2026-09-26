"""v71 action feedback: real UI, edges, reduced motion and localized play states."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('[data-place=picnic]').click();p.locator('#festivalStart').click()
 seq=p.locator('.festivalSequence>span').evaluate_all('(es)=>es.map(e=>e.getAttribute("aria-label"))')
 foods=p.evaluate('[0,1,2].map(i=>T("gardenFood"+i))');answers=[foods.index(x) for x in seq]
 p.locator('#festivalReady').click();p.locator(f'[data-answer="{answers[0]}"]').click()
 assert p.locator('.picnicTable [data-served=true] svg').count()==1
 assert p.locator('.picnicTable [data-served=false] svg').count()==0,'future answers leaked'
 p.locator(f'[data-answer="{(answers[1]+1)%3}"]').click()
 assert p.locator('[data-mistake=true] svg').count()==1
 assert p.evaluate('GF.phase==="retry"&&GARDEN.medals[0]===0')
 p.locator('#festivalRetry').click();p.locator('#festivalReady').click()
 for a in answers:p.locator(f'[data-answer="{a}"]').click()
 assert p.locator('.picnicTable [data-served=true] svg').count()==3
 assert p.locator('[data-answer]').count()==0
 assert p.evaluate('GARDEN.outings[0]===1')
 p.evaluate('gardenFestivalAct(0);gardenFestivalWin()');assert p.evaluate('GARDEN.outings[0]===1')
 p.screenshot(path=str(ARTIFACTS/'feedback71-picnic.png'))
 p.locator('#festivalChoose').click();p.locator("#btnHome").click();p.locator('[data-place="pond"]').click();p.locator('#festivalStart').click()
 assert p.locator('[data-reachable=true]').count()==2
 assert p.locator('.festivalGrid .pearl').count()==3
 assert p.evaluate('JSON.stringify(GF)')==p.evaluate('(()=>{gardenFestivalAct(24);return JSON.stringify(GF)})()')
 p.locator('[data-cell="1"]').click();p.locator('[data-cell="2"]').click()
 assert p.locator('.festivalPearls [data-collected=true]').count()==1
 assert p.locator('[data-catch=true]').count()==1
 for i in [7,12,17,22,23,24]:p.locator(f'[data-cell="{i}"]').click()
 assert p.evaluate('GF.phase==="won"&&GARDEN.outings[1]===1')
 assert p.locator('.festivalCell').count()==25 and p.locator('.festivalCell:enabled').count()==0
 assert p.locator('.festivalPearls [data-collected=true]').count()==3
 p.screenshot(path=str(ARTIFACTS/'feedback71-pond.png'))
 p.locator('#festivalChoose').click();p.locator("#btnHome").click();p.locator('[data-place="stars"]').click();p.locator('#festivalStart').click()
 p.locator('[data-cell="0"]').click()
 assert p.locator('[data-linked=true]').count()==3
 assert p.locator('.festivalStatus').inner_text()==p.evaluate('T("festivalLit",GF.lights.filter(Boolean).length)')
 p.locator('[data-cell="4"]').click()
 assert p.evaluate('GF.phase==="won"') and p.locator('[data-linked=true]').count()==5
 assert p.locator('[aria-pressed=true].festivalCell').count()==9
 assert p.locator('.festivalCell:enabled').count()==0
 p.screenshot(path=str(ARTIFACTS/'feedback71-stars.png'))
 # Persistent outlines explain causality even after animation expires.
 p.wait_for_function('performance.now()-GF.feedback.at>950')
 p.evaluate('gardenLifeRender()');assert p.locator('.starSwitch').count()==0
 assert p.locator('[data-linked=true]').count()==5
 p.emulate_media(reduced_motion='reduce');p.locator('#festivalRetry').click();p.locator('[data-cell="4"]').click()
 assert p.locator('.starSwitch .gardenMotion').first.evaluate('e=>getComputedStyle(e).animationName')=='none'
 assert p.locator('[data-linked=true]').count()==5
 # Fresh-save assets and gameplay remain untouched; transient feedback is not saved.
 assert p.evaluate('COINS===0&&GARDEN.seeds===3&&GARDEN.petals===0&&GARDEN.pantry.every(v=>v===0)')
 saved=p.evaluate('JSON.stringify(GARDEN)');p.reload();assert p.evaluate('JSON.stringify(GARDEN)')==saved
 assert p.evaluate('GF===null')
 # Actual active/completed layouts, including smallest phone and landscape.
 layouts=0
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   for theme in range(3):
    p.evaluate('a=>{applyLanguage(a[0]);setHubPage("garden");gardenFestivalStart(a[1],1);if(a[1]===0){GF.phase="play";gardenFestivalAct(GF.seq[0]);}else gardenFestivalAct(a[1]===1?1:4);}',[lang,theme])
    assert p.locator('#gardenLife').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(w,lang,theme)
    assert p.locator('.festivalPanel').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(w,lang,theme)
    layouts+=1
 assert not errors,errors
 (ARTIFACTS/'feedback71.json').write_text(json.dumps({'layouts':layouts,'offline':True,'errors':errors,'reduced_motion':True}),encoding='utf-8')
 b.close()
print('PASS v71 served dishes, hidden answers, reachable arrows, pearl collection, linked stars, final boards, no double award, reduced motion, 99 layouts')
