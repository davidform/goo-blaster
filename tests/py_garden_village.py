"""Play the production chain from a fresh save to six projects, offline.
Only crop time is accelerated; ingredients, food, orders and buildings use UI actions.
"""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 c.add_init_script('window.__villageNow=Date.now();Date.now=()=>window.__villageNow')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').click()
 assert p.evaluate('GARDEN.pantry.every(n=>n===0)&&GARDEN.projects===0')
 def farm(crop,cycles):
  for _ in range(cycles):
   p.locator('#gardenFarm').click()
   # Plant individual beds to keep the choice independent of repair-ready tasks.
   for i in range(3):
    p.locator(f'.gardenSpot[data-kind=plot][data-index="{i}"]').click()
    row=p.locator('.gardenPlot').nth(i);row.locator('select').select_option(str(crop));row.locator('button').click()
   p.evaluate('window.__villageNow+=360001;gardenRefreshTimers()')
   p.locator('#gardenQuestAction').click()
 farm(0,1)
 p.locator('#gardenKitchen').click()
 assert p.locator('[data-craft="0"]').is_enabled()
 p.locator('[data-craft="0"]').click()
 p.evaluate('applyLanguage("zh-Hant")');assert '薄荷茶' in p.locator('.gardenLifeNotice').inner_text() and 'Mint tea' not in p.locator('.gardenLifeNotice').inner_text()
 p.evaluate('applyLanguage("en")');p.locator('#gardenCommunity').click();p.locator('[data-deliver="0"]').click()
 assert p.evaluate('GARDEN.orders[0]===1&&GARDEN.stamps===1&&GARDEN.pantry[0]===2')
 assert not p.evaluate('gardenDeliver(0,0)')
 p.locator('#gardenKitchen').click()
 for _ in range(2):p.locator('[data-craft="0"]').click()
 p.locator('#gardenCommunity').click();p.locator('[data-deliver="0"]').click();p.locator('#gardenBuildAction').click()
 assert p.evaluate('GARDEN.projects===1&&GARDEN.stamps===3&&gardenBuildingLevel(0)===1')
 assert not p.evaluate('gardenBuild(0)')
 farm(0,3);p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.house===1')
 p.locator('#gardenKitchen').click();assert p.locator('[data-craft="1"]').is_disabled()
 # The recipe's missing-ingredient action points back to a usable farm.
 p.locator('[data-recipe="1"] button').last.click();assert p.evaluate('GARDEN_TAB==="farm"&&GARDEN_QUEST_CROP===1')
 farm(1,5);p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.house===2')
 farm(2,2);farm(1,1)
 p.locator('#gardenKitchen').click()
 for food,n in [(0,3),(1,6),(2,6)]:
  for _ in range(n):p.locator(f'[data-craft="{food}"]').click()
 p.locator('#gardenCommunity').click();p.locator('[data-deliver="0"]').click()
 for food in [1,2]:
  for _ in range(3):p.locator(f'[data-deliver="{food}"]').click()
 for _ in range(5):p.locator('#gardenBuildAction').click()
 assert p.evaluate('GARDEN.projects===6&&GARDEN.orders.every(n=>n===3)&&GARDEN.stamps===102&&[0,1,2].every(i=>gardenBuildingLevel(i)===2)')
 assert p.locator('#gardenBuildAction').count()==0
 earned=p.evaluate('JSON.stringify(GARDEN)');p.reload();p.locator('#navGarden').click();assert p.evaluate('JSON.stringify(GARDEN)')==earned
 result=p.evaluate('''()=>{
 const old=GARDEN,code=saveCodeEncode();GARDEN=cleanGarden();importSaveCode(code);const backup=JSON.stringify(GARDEN)===JSON.stringify(old);
 const newer=cleanGarden(old);newer.rev++;newer.pantry[0]=7;const merged=pickBetterSave({v:2,progress:9,coins:50,garden:old},{v:2,progress:2,coins:0,garden:newer});
 const merge=merged.progress===9&&merged.garden.pantry[0]===7;
 const bad=cleanGarden({pantry:[-1,Infinity,'3.9'],orders:[NaN,-5,1e20],stamps:9,projects:99});
 const sanitize=bad.pantry.join(',')==='0,0,3,0,0,0'&&bad.orders.join(',')==='0,0,9999'&&bad.projects===2;
 GARDEN=cleanGarden({house:0,pantry:[9,9,9,9,9,9],stamps:999});const locked=!gardenCraft(1)&&!gardenDeliver(2,0);
 GARDEN.projects=2;const gate=!gardenBuild(2);GARDEN=cleanGarden({house:3,pantry:[9999,9999,9999,9999,9999,9999]});const full=!gardenCraft(0);
 const invalid=!gardenCraft(-1)&&!gardenCraft(3)&&!gardenDeliver(99,0)&&!gardenBuild(-1);
 GARDEN=old;return {backup,merge,sanitize,locked,gate,full,invalid};}''')
 assert all(result.values()),result
 # 11 locales, 3 phone shapes, both panels, nonempty/locked/complete states.
 layouts=0
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   for tab in ['kitchen','community']:
    p.evaluate('a=>{applyLanguage(a[0]);GARDEN_TAB=a[1];renderGarden()}',[lang,tab])
    assert p.locator('#gardenLife').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(lang,w,tab)
    for button in p.locator('#gardenLife button').all():assert button.bounding_box()['height']>=44
    layouts+=1
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");GARDEN_TAB="community";renderGarden();document.getElementById("gardenLife").scrollIntoView()')
 p.screenshot(path=str(ARTIFACTS/'village69-complete.png'))
 p.evaluate('GARDEN_TAB="farm";renderGarden();document.getElementById("gardenViewport").scrollIntoView()');p.screenshot(path=str(ARTIFACTS/'village69-world.png'))
 assert not errors,errors
 (ARTIFACTS/'village69.json').write_text(json.dumps(dict(result,projects=6,orders=[3,3,3],stamps=102,layouts=layouts,offline=True,time_accelerated=True,errors=errors),indent=2),encoding='utf-8')
 b.close()
print('PASS fresh-save UI farm/craft/orders/6 village builds; offline reload/backup/merge; caps/gates; 66 locale layouts')
