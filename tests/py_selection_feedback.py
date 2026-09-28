"""Rendered selection feedback across destinations, not just DOM state."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL)
    c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
    c.set_offline(True)
    p=c.new_page(); errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    def colours(selector):
        return p.locator(selector).evaluate_all('(es)=>es.map(e=>({pressed:e.getAttribute("aria-pressed"),bg:getComputedStyle(e).backgroundColor}))')
    def selected(selector):
        state=colours(selector);on=[x for x in state if x['pressed']=='true']
        assert len(on)==1,state
        assert all(x['bg']!=on[0]['bg'] for x in state if x['pressed']=='false'),state
    checks=0
    # Fixture unlocks difficulty choices; clicks, rather than assignment, choose difficulty.
    p.evaluate('GARDEN.medals=[3,3,3]')
    for w,h in [(390,844),(320,568),(844,390),(1280,900)]:
        p.set_viewport_size({'width':w,'height':h})
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('v=>applyLanguage(v)',lang)
            for place in ['picnic','pond','stars']:
                p.locator('[data-place="'+place+'"]').click()
                for level in [2,3,1]:
                    p.locator('.festivalLevels [data-level="'+str(level)+'"]').click()
                    selected('.festivalLevels button')
                    assert p.locator('.festivalLevels [aria-pressed=true]').get_attribute('data-level')==str(level)
                    checks+=1
                home=p.locator('#btnHome')
                box=home.bounding_box()
                assert box['height']>=44 and box['x']>=0 and box['x']+box['width']<=w
                assert home.evaluate('e=>e.scrollWidth<=e.clientWidth && e.scrollHeight<=e.clientHeight')
                assert home.evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(63, 99, 78)'
                assert p.locator('#garden').bounding_box()['y']>=box['y']+box['height']
                home.click();assert p.locator('#townHome').is_visible()
    # Other groups: all tools, visitors, crops, navigation and native selects.
    p.set_viewport_size({'width':390,'height':844})
    p.locator('#navGarden').click();p.locator('#gardenArrange').click()
    for selector in ['.gardenTools button','.gardenWishTabs button']:
        for i in range(p.locator(selector).count()):
            p.locator(selector).nth(i).click();selected(selector)
    p.locator('#gardenFarm').click()
    p.evaluate('GARDEN.house=2;renderGarden()')
    p.locator('.gardenSpot.plot[data-index="0"]').click()
    for i in range(3):
        p.locator('.gardenCropChoice:visible').nth(i).click();selected('.gardenCropChoice:visible')
    p.locator('#gardenContextClose').click()
    for nav,panel in [('navAdventure','#menu'),('btnShop','#shop'),('navGarden','#garden'),('navSettings','#settings')]:
        p.locator('#'+nav).click()
        assert p.locator('#hubNav [aria-current=page]').get_attribute('id')==nav
        assert p.locator(panel).is_visible()
        p.locator('#btnHome').click();assert p.locator('#townHome').is_visible()
    p.locator('#navSettings').click()
    before=colours('#btnSound');p.locator('#btnSound').click();after=colours('#btnSound')
    assert before[0]['pressed']!=after[0]['pressed'] and before[0]['bg']!=after[0]['bg']
    p.locator('#btnSound').click()
    for i in [0,3,6]:
        p.locator('#btnLang').click();p.locator('.lrow').nth(i).click()
        p.locator('#btnLang').click()
        assert p.locator('.lrow.on').count()==1
        assert p.locator('.lrow').nth(i).get_attribute('class')=='lrow on'
        assert p.locator('.lrow.on').evaluate('e=>getComputedStyle(e).backgroundColor')!=p.locator('.lrow:not(.on)').first.evaluate('e=>getComputedStyle(e).backgroundColor')
        p.locator('.lrow.on').click()
    p.evaluate('PROGRESS=10;setHubPage("adventure")')
    for k in [1,8,0]:
        p.locator('.gnode[data-k="'+str(k)+'"]').click()
        assert p.locator('.gnode.sel').get_attribute('data-k')==str(k)
        assert p.locator('.gnode.sel').evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(63, 99, 78)'
    p.evaluate('SEL_IDX=49;renderStage()')
    for weapon in ['yoyo','graffiti']:
        p.locator('#startingWeapon').select_option(weapon)
        assert p.locator('#startingWeapon').input_value()==weapon
        assert p.evaluate('SECONDARY_WEAPON')==weapon
    # Locked difficulties cannot change selection; theme identity survives selected styling.
    p.evaluate('GARDEN.medals=[0,0,0];setHubPage("home")')
    p.locator('[data-place="pond"]').click()
    assert p.locator('.festivalLevels [data-level="2"]').is_disabled()
    selected('.festivalLevels button')
    assert not errors,errors
    (ARTIFACTS/'selection-feedback.json').write_text(json.dumps({'checks':checks,'errors':errors,'offline':True,'cpu':os.getenv('GOO_UI_CPU','1')}),encoding='utf-8')
    b.close()
print('PASS: 396 difficulty clicks, return buttons in 44 layouts, tools/visitors/crops/navigation/sound/stage selection, locked difficulty, offline')
