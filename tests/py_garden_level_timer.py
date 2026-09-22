"""Level-scaled planting, frozen deadlines, old saves and offline cold reopen."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
    b = pw.chromium.launch(channel=BROWSER_CHANNEL)
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True)
    c.set_offline(True)
    c.add_init_script('window.__now=Date.now();Date.now=()=>window.__now')
    p = c.new_page()
    errors = []
    p.on('pageerror', lambda e: errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate', {'rate': int(os.getenv('GOO_UI_CPU', '1'))})
    url = (Path(GAME_ROOT) / 'index.html').as_uri()
    p.goto(url)
    p.locator('#navGarden').click()
    expected = [[60, 180, 360], [90, 270, 540], [120, 360, 720], [150, 450, 900]]
    for level, times in enumerate(expected):
        for crop in range(min(2, level) + 1):
            seconds = times[crop]
            p.evaluate('level=>{GARDEN=cleanGarden({house:level});GARDEN_QUEST_CROP=0;renderGarden()}', level)
            p.locator('#gardenQuestCrop').select_option(str(crop))
            clock = f'{seconds//60}:{seconds%60:02}'
            assert clock in p.locator('#gardenQuestDetail').inner_text(), (level, crop)
            p.locator('.gardenSpot.plot[data-index="0"]').click()
            row = p.locator('.gardenPlot').first
            row.locator('select').select_option(str(crop))
            assert clock in row.locator('p').inner_text(), (level, crop)
            row.locator('button').click()
            r = p.evaluate('({duration:GARDEN.plots[0].duration,remaining:gardenRemaining(GARDEN.plots[0]),growth:gardenGrowth(GARDEN.plots[0])})')
            assert r == {'duration': seconds, 'remaining': seconds, 'growth': 0}, (level, crop, r)
            p.evaluate('seconds=>{window.__now+=seconds*500;gardenRefreshTimers()}', seconds)
            assert p.evaluate('gardenRemaining(GARDEN.plots[0])') == seconds / 2
            assert not p.evaluate('gardenHarvest(0)')
    # Upgrade while growing: no retroactive extension, only later planting is longer.
    r = p.evaluate('''()=>{GARDEN=cleanGarden({petals:12});gardenPlant(0,0);
      const first={...GARDEN.plots[0]};gardenUpgrade();gardenPlant(1,0);
      return {first,after:GARDEN.plots[0],second:GARDEN.plots[1]};}''')
    assert r['first'] == r['after'] and r['first']['duration'] == 60 and r['second']['duration'] == 90
    # v71/earlier plots retain original deadlines at every cottage level.
    r = p.evaluate('''()=>{const now=Date.now();return [0,1,2,3].map(house=>{
      const g=cleanGarden({house,plots:[{crop:0,growth:0,readyAt:now+42000},{crop:2,growth:3,readyAt:now-1}]});
      return [gardenRemaining(g.plots[0]),g.plots[0].duration,gardenReady(g.plots[1])];});}''')
    assert r == [[42, 60, True]] * 4, r
    # Malformed duration/clock bounds, including numeric strings and infinity.
    r = p.evaluate('''()=>[undefined,null,-1,0,"900",Infinity,NaN,1e99,900].map(duration=>{
      const p=cleanGarden({plots:[{crop:2,duration,readyAt:1e99}]}).plots[0];return [p.duration,gardenRemaining(p)];})''')
    assert r == [[360, 360]] * 7 + [[900, 900]] * 2, r
    # Backup and native merge preserve a running high-level crop's exact duration.
    r = p.evaluate('''()=>{GARDEN=cleanGarden({house:3,rev:100});gardenPlant(0,2);const initial=JSON.stringify(GARDEN);
      const code=saveCodeEncode();GARDEN=cleanGarden();importSaveCode(code);
      const backup=JSON.parse(JSON.stringify(GARDEN));
      const merged=pickBetterSave({progress:1,coins:0,garden:GARDEN},{progress:1,coins:0,garden:{rev:0}});
      return {initial:JSON.parse(initial),backup,merge:merged.garden};}''')
    assert r['initial'] == r['backup'] == r['merge'], r
    # Shut down the entire browser; offline reopen advances the clock by two minutes.
    state = p.evaluate('({raw:localStorage.getItem(PROG_KEY),now:Date.now(),deadline:GARDEN.plots[0].readyAt})')
    b.close()
    b = pw.chromium.launch(channel=BROWSER_CHANNEL)
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True)
    c.set_offline(True)
    c.add_init_script('localStorage.setItem("gooblaster_save_v3",'+json.dumps(state['raw'])+');window.__now='+str(state['now']+120000)+';Date.now=()=>window.__now')
    p = c.new_page()
    p.on('pageerror', lambda e: errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate', {'rate': int(os.getenv('GOO_UI_CPU', '1'))})
    p.goto(url)
    assert p.evaluate('GARDEN.plots[0].readyAt') == state['deadline']
    assert p.evaluate('gardenRemaining(GARDEN.plots[0])') == 780
    p.locator('#navGarden').click()
    p.wait_for_function('document.querySelector(".gardenSpot.plot").dataset.mark==="13:00"')
    p.evaluate('window.__now+=780000;gardenRefreshTimers()')
    assert p.evaluate('gardenReady(GARDEN.plots[0])&&gardenHarvest(0)&&!gardenHarvest(0)')
    # Current multiplier and next planting time fit all supported locale/phone widths.
    for width, height in [(320, 568), (390, 844), (844, 390)]:
        p.set_viewport_size({'width': width, 'height': height})
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('lang=>{applyLanguage(lang);setHubPage("garden");GARDEN_QUEST_CROP=2;renderGarden()}', lang)
            assert '15:00' in p.locator('#gardenQuestDetail').inner_text()
            assert p.locator('#gardenQuest').evaluate('e=>e.scrollWidth<=e.clientWidth+1'), (width, lang)
            assert p.locator('#gardenPace').evaluate('e=>e.getBoundingClientRect().width>0')
    p.set_viewport_size({'width': 390, 'height': 844})
    p.evaluate('applyLanguage("zh-Hant");renderGarden();document.getElementById("garden").scrollTop=0')
    p.screenshot(path=str(ARTIFACTS / 'garden72-level3-preview.png'))
    p.locator('#gardenQuestAction').click()
    p.screenshot(path=str(ARTIFACTS / 'garden72-level3-countdown.png'))
    assert not errors, errors
    (ARTIFACTS / 'garden72-level-timer.json').write_text(json.dumps({'expected_seconds': expected, 'old_deadlines_preserved': True, 'cold_offline_remaining': 780, 'layouts': 33, 'errors': errors}), encoding='utf-8')
    b.close()
print('PASS level 0–3 crop times; preview; upgrade isolation; legacy saves; bounds; backup/native merge; cold offline reopen; exact-once harvest; 33 layouts')
