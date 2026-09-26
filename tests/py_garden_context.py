"""Context controls stay with the selected object, without scrolling to a form."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
    b = pw.chromium.launch(channel=BROWSER_CHANNEL)
    c = b.new_context(viewport={'width':390,'height':844}, has_touch=True)
    c.set_offline(True)
    p = c.new_page(); errors=[]
    p.on('pageerror', lambda e: errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate', {'rate':int(os.getenv('GOO_UI_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    p.locator('#navGarden').click()
    checks=0
    for w,h in [(320,568),(390,844),(844,390),(1280,900)]:
        p.set_viewport_size({'width':w,'height':h})
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('lang=>{gardenContextClose();GARDEN=cleanGarden({house:2,seeds:3});GARDEN_TAB="farm";applyLanguage(lang);setHubPage("garden")}',lang)
            spot=p.locator('.gardenSpot.plot[data-index="0"]')
            spot.scroll_into_view_if_needed()
            before=p.locator('#garden').evaluate('e=>e.scrollTop')
            spot.click()
            pop=p.locator('#gardenContext')
            assert pop.is_visible()
            if lang in ['en','zh-Hant','zh-Hans']:
                assert pop.locator('#gardenContextClose').inner_text()==('Cancel' if lang=='en' else '取消')
            assert abs(p.locator('#garden').evaluate('e=>e.scrollTop')-before)<2
            assert pop.locator('.gardenCropChoice:visible').count()==3
            bounds=pop.bounding_box()
            assert bounds['x']>=0 and bounds['x']+bounds['width']<=w+1
            assert bounds['y']>=p.locator('#btnHome').bounding_box()['height']-1
            assert bounds['y']+bounds['height']<=p.locator('#hubNav').bounding_box()['y']+1
            assert pop.evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            for choice in pop.locator('.gardenCropChoice:visible').all():
                assert choice.bounding_box()['height']>=44
            pop.locator('.gardenCropChoice[data-crop="2"]:visible').click()
            assert pop.locator('.gardenCropChoice[data-crop="2"]:visible').get_attribute('aria-pressed')=='true'
            # Tick updates must not silently change the chosen plant.
            p.evaluate('gardenRefreshTimers()')
            pop.locator('.gardenPlantSubmit:visible').click()
            assert p.evaluate('GARDEN.seeds===2&&GARDEN.plots[0].crop===2&&GARDEN.plots[0].duration===720')
            assert pop.is_hidden()
            spot.click();p.keyboard.press('Escape');assert pop.is_hidden()
            p.locator('#gardenKitchen').click()
            assert p.locator('#gardenViewport').is_hidden() and p.locator('#gardenQuest').is_hidden()
            assert p.locator('.gardenRecipe').first.is_visible()
            p.locator('#gardenCommunity').click()
            assert p.locator('.gardenRecipe').count()==0 and p.locator('.gardenOrder').first.is_visible()
            p.locator('#gardenArrange').click()
            assert p.locator('#gardenLife').is_hidden() and p.locator('.gardenTile').first.is_visible()
            p.locator('#gardenFarm').click()
            assert p.locator('.gardenTile').first.is_hidden() and p.locator('#gardenViewport').is_visible()
            assert p.locator('#garden').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            checks+=1
    # Another field maturing must not erase an in-progress crop choice or focus.
    p.evaluate('gardenContextClose();GARDEN=cleanGarden({house:2});GARDEN_TAB="farm";setHubPage("garden");GARDEN.plots[1]={crop:0,duration:60,readyAt:Date.now()+60000,growth:0};renderGarden()')
    p.locator('.gardenSpot.plot[data-index="0"]').click()
    p.locator('.gardenPlot').first.locator('[data-crop="2"]').click()
    p.evaluate('GARDEN.plots[1].readyAt=Date.now()-1;GARDEN_TIMER_SECOND=-1;gardenRefreshTimers()')
    assert p.locator('.gardenPlot').first.locator('[data-crop="2"]').get_attribute('aria-pressed')=='true'
    assert p.evaluate('document.activeElement.dataset.crop==="2"')
    p.locator('#gardenContextClose').click()
    p.locator('#btnHome').click()
    assert p.locator('#gardenContext').is_hidden()
    assert not errors,errors
    (ARTIFACTS/'garden76-context.json').write_text(json.dumps({'layouts':checks,'errors':errors,'offline':True,'cpu':os.getenv('GOO_UI_CPU','1'),'no_scroll_on_selection':True}),encoding='utf-8')
    b.close()
print('PASS contextual field choices, no scroll, crop persistence, Escape, focused workspaces; 44 locale/viewport cases offline')
