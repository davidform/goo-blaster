"""Real world-view input and farming, camera bounds, animation lifecycle and saves."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').click()
 assert not p.locator('#gardenWorkshop').get_attribute('open')
 assert p.locator('#gardenViewport').is_visible()
 before=p.evaluate('GV.time');p.wait_for_function('t=>GV.time>t+.15',arg=before)
 # Dragging from a field must pan without selecting/planting it.
 box=p.locator('.gardenSpot[data-kind=plot]').first.bounding_box();a=box['x']+box['width']/2;d=box['y']+box['height']/2
 p.mouse.move(a,d);p.mouse.down();p.mouse.move(a-45,d+35,steps=8);p.mouse.up()
 assert p.evaluate('GV.panX<-30&&GV.panY>20&&GARDEN.seeds===3&&GV.selected===null')
 pos=p.evaluate('[GV.panX,GV.panY]');p.mouse.move(a+20,d+60);assert p.evaluate('[GV.panX,GV.panY]')==pos
 p.locator('#gardenHome').click();assert p.evaluate('GV.panX===0&&GV.panY===0&&GV.zoom===1')
 for _ in range(8):p.locator('#gardenZoomIn').click()
 assert p.evaluate('GV.zoom===1.8')
 for _ in range(10):p.locator('#gardenZoomOut').click()
 assert p.evaluate('GV.zoom===.8');p.locator('#gardenHome').click()
 box=p.locator('.gardenSpot[data-kind=plot]').first.bounding_box();a=box['x']+box['width']/2;d=box['y']+box['height']/2
 touch=c.new_cdp_session(p)
 touch.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':a,'y':d}]})
 touch.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':a-50,'y':d+30}]})
 touch.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 assert p.evaluate('GV.panX<-35&&GARDEN.seeds===3&&GV.selected===null')
 p.locator('#gardenHome').click();box=p.locator('.gardenSpot[data-kind=plot]').first.bounding_box();p.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2);assert p.locator('.gardenPlot').first.is_visible();assert p.locator('.gardenPlot').nth(1).is_hidden()
 p.locator('.gardenPlot button').first.click();assert p.evaluate('GARDEN.seeds===2&&GARDEN.plots[0].growth===0')
 # Existing real settlement route, no new wall-clock growth or resource shortcut.
 p.evaluate('LV_IDX=0;start();endGame(true)');p.locator('#btnGarden').click()
 p.locator('.gardenSpot[data-kind=plot]').first.click();assert p.evaluate('GARDEN.plots[0]===null&&GARDEN.petals===1&&GARDEN.seeds===4')
 p.locator('.gardenSpot[data-kind=house]').click();assert p.locator('#gardenUpgrade').is_visible() and p.locator('#gardenUpgrade').is_disabled()
 p.evaluate('GARDEN.petals=12;saveGarden()');p.locator('#gardenUpgrade').click();assert p.evaluate('GARDEN.house===1&&GARDEN.petals===0')
 p.locator('#gardenArrange').click();assert p.locator('.gardenTile').count()==16 and p.locator('.gardenTool').first.is_visible()
 p.locator('#gardenArrange').click();assert p.locator('.gardenTile').first.is_hidden()
 # The ranger is an ambient host even before the first resident moves in.
 p.locator('.gardenSpot[data-kind=guest]').first.click();assert p.evaluate('GV.cheerUntil>GV.time')
 p.locator('#navAdventure').click();before=p.evaluate('GV.time');p.wait_for_function('t=>performance.now()>t+200',arg=p.evaluate('performance.now()'))
 assert p.evaluate('GV.time')==before
 p.reload();assert p.evaluate('GARDEN.house===1&&GARDEN.petals===0&&GARDEN.seeds===4')
 p.emulate_media(reduced_motion='reduce');p.locator('#navGarden').click()
 a=p.evaluate('GV.targets.filter(t=>t.kind==="guest").map(t=>[t.x,t.y])');p.evaluate('gardenWorldPaint(1)');assert p.evaluate('GV.targets.filter(t=>t.kind==="guest").map(t=>[t.x,t.y])')==a
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('lang=>{applyLanguage(lang);setHubPage("garden");GV.panX=GV.panY=0;GV.zoom=1;gardenWorldPaint(0)}',lang)
   assert p.locator('#garden').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(w,lang)
   for spot in p.locator('.gardenSpot[data-kind=plot]').all():
    assert spot.is_visible(),(w,lang,spot.get_attribute('aria-label'))
    bb=spot.bounding_box();assert bb['width']>=44 and bb['height']>=44
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");document.querySelector("#garden").scrollTop=0')
 p.screenshot(path=str(ARTIFACTS/'garden66-world.png'))
 assert not errors,errors
 (ARTIFACTS/'garden66-world.json').write_text(json.dumps({'errors':errors,'camera_input':True,'farming':True,'upgrade':True,'reload':True,'offline':True,'layouts':33,'reduced_motion':True,'hidden_animation_stopped':True}),encoding='utf-8');b.close()
print('PASS garden world actual pointer input; bounded zoom; no hover drift; farming/clear/harvest; cottage; save; 33 layouts; offline; reduced motion; hidden animation stopped')
