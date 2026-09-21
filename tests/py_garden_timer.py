"""Timed crops: live UI, offline deadlines, migration, task gating and exact-once harvest."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 # Real clock + controlled offset. One live second is tested, long waits are accelerated.
 c.add_init_script('window.__offset=0;window.__realNow=Date.now.bind(Date);Date.now=()=>window.__realNow()+window.__offset')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').click();p.locator('#gardenQuestAction').click()
 assert p.locator('#gardenQuestAction').is_disabled()
 assert p.locator('#gardenQuestSteps [aria-current]').inner_text()=='Plant & harvest'
 assert p.evaluate('GARDEN.petals===0&&!gardenHarvest(0)&&gardenQuestState().kind==="grow"')
 first=p.locator('#gardenQuestAction').inner_text();p.wait_for_function('s=>document.getElementById("gardenQuestAction").textContent!==s',arg=first,timeout=10000)
 deadline=p.evaluate('GARDEN.plots[0].readyAt')
 p.reload();p.locator('#navGarden').click();assert p.evaluate('GARDEN.plots[0].readyAt')==deadline
 # Clearing a stage must not skip the countdown, and planting must not move to Adventure.
 p.evaluate('gardenClear();renderGarden()');assert p.evaluate('!gardenReady(GARDEN.plots[0])')
 assert p.locator('#garden').is_visible()
 # Partial seed inventory and repair funds cannot advance a task before its harvest.
 p.evaluate('GARDEN.petals=12;renderGarden()');assert p.locator('#gardenQuest').get_attribute('data-step')=='grow'
 p.evaluate('window.__offset=61000');p.wait_for_function('document.getElementById("gardenQuest").dataset.step==="harvest"')
 assert p.locator('#gardenQuestSteps [aria-current]').inner_text()=='Plant & harvest'
 assert p.locator('#gardenQuestAction').is_enabled()
 p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.petals===15&&GARDEN.plots.every(p=>!p)&&!gardenHarvest(0)')
 assert p.locator('#gardenQuest').get_attribute('data-step')=='repair'
 # A ready save stays ready after reload/offline, no auto-collection or loss.
 p.evaluate('window.__offset=0;GARDEN=cleanGarden({house:2,plots:[{crop:2,growth:3}]});saveGame()');p.reload();p.locator('#navGarden').click()
 assert p.evaluate('gardenReady(GARDEN.plots[0])&&GARDEN.petals===0')
 # Legacy partial growth maps proportionally; migration persists, no restart.
 r=p.evaluate('''()=>{const before=Date.now();const old={v:2,progress:9,coins:456,meta:{dmg:2},garden:{seeds:2,petals:7,house:2,plots:[{crop:1,growth:1},{crop:2,growth:3},null]}};
 applySaveObject(old);const rem=gardenRemaining(GARDEN.plots[0]);const ready=gardenReady(GARDEN.plots[1]);return {rem,ready,deadline:GARDEN.plots[0].readyAt};}''')
 assert r['rem']==90 and r['ready'],r
 p.reload();assert p.evaluate('GARDEN.plots[0].readyAt')==r['deadline'];assert p.evaluate('PROGRESS===9&&COINS===456&&META.dmg===2&&GARDEN.petals===7')
 p.evaluate('applySaveObject({v:2,progress:9,coins:456,meta:{dmg:2},garden:{plots:{broken:true}}})');assert p.evaluate('GARDEN.plots.every(p=>p===null)&&PROGRESS===9&&COINS===456')
 p.evaluate('GARDEN=cleanGarden({plots:[{crop:1,growth:1}]})')
 # Invalid/future dates are bounded; rollback cannot demand more than a full growth cycle.
 r=p.evaluate('''()=>{const x=cleanGarden({plots:[{crop:0,readyAt:Infinity},{crop:1,readyAt:-1},{crop:2,readyAt:1e99}]});return x.plots.map(gardenRemaining);}''')
 assert r==[60,180,360],r
 p.evaluate('window.__offset=-86400000');assert p.evaluate('gardenRemaining(GARDEN.plots[0])')<=180
 # Screenshot is actual runtime; setup is explicitly a controlled timer fixture.
 p.evaluate('window.__offset=0;GARDEN=cleanGarden();GARDEN_QUEST_CROP=0;applyLanguage("zh-Hant");setHubPage("garden");gardenQuestAction();GV.selected={kind:"plot",i:0};renderGarden();document.getElementById("garden").scrollTop=0')
 p.screenshot(path=str(ARTIFACTS/'garden68-countdown.png'))
 p.evaluate('window.__offset=61000');p.wait_for_function('document.getElementById("gardenQuest").dataset.step==="harvest"')
 p.screenshot(path=str(ARTIFACTS/'garden68-ready.png'))
 assert not errors,errors
 (ARTIFACTS/'garden68-timer.json').write_text(json.dumps({'live_countdown':True,'reload_deadline':True,'offline':True,'legacy_partial_seconds':90,'task_waits_for_harvest':True,'clear_does_not_skip_timer':True,'invalid_dates_bounded':True,'errors':errors}),encoding='utf-8')
 b.close()
print('PASS live countdown; persistent offline growth; migration; harvest-gated task; exact-once collection; clock bounds')
