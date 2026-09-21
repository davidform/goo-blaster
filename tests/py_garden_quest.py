"""A new player can finish the first restoration using the visible task board."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 c.add_init_script('window.__gardenNow=Date.now();Date.now=()=>window.__gardenNow');p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').click()
 assert p.locator('#gardenQuest').get_attribute('data-step')=='plant'
 assert p.locator('#gardenQuestAction').is_visible() and p.locator('#gardenQuestAction').bounding_box()['y']<500
 assert p.locator('#gardenQuestDetail').inner_text()=='Use 3 seeds. Harvest 3 petals in 1:00.'
 # Four farming cycles, unchanged first repair cost 12. Advance an explicit test clock.
 for cycle in range(4):
  p.locator('#gardenQuestAction').click()
  assert p.evaluate('GARDEN.plots.every(p=>p&&p.crop===0&&p.growth===0)')
  assert p.locator('#gardenQuest').get_attribute('data-step')=='grow'
  assert p.locator('#gardenQuestAction').is_disabled()
  assert p.locator('#gardenQuestSteps [aria-current]').inner_text()=='Plant & harvest'
  p.evaluate('window.__gardenNow+=60000;gardenRefreshTimers()')
  assert p.locator('#gardenQuest').get_attribute('data-step')=='harvest'
  p.locator('#gardenQuestAction').click()
  assert p.evaluate('GARDEN.petals')==(cycle+1)*3
  assert '+3' in p.locator('#gardenNotice').inner_text()
 assert p.locator('#gardenQuest').get_attribute('data-step')=='repair'
 p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.house===1&&GARDEN.petals===0')
 assert 'level 1' in p.locator('#gardenNotice').inner_text()
 p.locator('#gardenQuestCrop').select_option('1');assert '3:00' in p.locator('#gardenQuestDetail').inner_text()
 p.reload();p.locator('#navGarden').click();assert p.evaluate('GARDEN.house===1&&GARDEN.petals===0')
 # Limited seeds, mixed readiness, zero seeds, cap and completed home.
 p.evaluate('GARDEN=cleanGarden({seeds:1});renderGarden()');p.locator('#gardenQuestAction').click()
 assert p.evaluate('GARDEN.seeds===0&&GARDEN.plots.filter(Boolean).length===1')
 p.evaluate('GARDEN=cleanGarden({seeds:0});renderGarden()');assert p.locator('#gardenQuest').get_attribute('data-step')=='seed'
 p.evaluate('GARDEN=cleanGarden({house:2,plots:[{crop:0,growth:1},{crop:1,growth:0},{crop:2,growth:3}]});renderGarden()')
 p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.petals===7&&GARDEN.plots[1].growth===0&&GARDEN.plots.filter(Boolean).length===1')
 p.evaluate('GARDEN=cleanGarden({house:3,seeds:999,petals:999998,plots:[{crop:2,growth:3},{crop:2,growth:3},{crop:2,growth:3}]});renderGarden()')
 p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.petals===999999&&GARDEN.seeds===999&&GARDEN.house===3')
 assert '+1' in p.locator('#gardenNotice').inner_text()
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   for fixture in [{},{'plots':[{'crop':0,'growth':0}]*3},{'house':2,'petals':120},{'house':3,'seeds':0}]:
    p.evaluate('x=>{GARDEN=cleanGarden(x[0]);applyLanguage(x[1]);setHubPage("garden");document.getElementById("garden").scrollTop=0}',[fixture,lang])
    assert p.locator('#gardenQuest').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(lang,w,fixture)
    assert p.locator('#gardenQuestAction').bounding_box()['height']>=44
 p.set_viewport_size({'width':390,'height':844});p.evaluate('GARDEN=cleanGarden();applyLanguage("zh-Hant");document.getElementById("garden").scrollTop=0')
 p.screenshot(path=str(ARTIFACTS/'garden67-start.png'))
 assert not errors,errors
 (ARTIFACTS/'garden67-quest.json').write_text(json.dumps({'first_restoration_cycles':4,'house':1,'offline':True,'layouts':132,'errors':errors}),encoding='utf-8');b.close()
print('PASS first restoration through task board; timed crops; choice/feedback; save; caps; 132 state/locale/size checks')
