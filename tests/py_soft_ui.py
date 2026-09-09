"""Actual hub interactions, responsive translated labels, and gameplay isolation."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

errors = []
rate = int(os.environ.get('GOO_UI_CPU', '1'))
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=BROWSER_CHANNEL)
    context = browser.new_context(viewport={'width':390, 'height':844}, has_touch=True)
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate', {'rate':rate})
    page.goto((Path(GAME_ROOT) / 'index.html').as_uri())
    page.wait_for_function("typeof BUILD !== 'undefined' && document.querySelector('.gnode')")
    assert page.evaluate('LANG') == 'en'
    assert page.locator('.gnode').count() == 50
    initial = page.evaluate('JSON.stringify({META,COINS,PROGRESS})')
    page.screenshot(path=str(ARTIFACTS / 'soft-menu.png'))
    # Select an unlocked earlier stage; returning through navigation must not jump to frontier.
    page.evaluate('PROGRESS=12; showMenu(); SEL_IDX=3; renderStage()')
    selected = page.evaluate('SEL_IDX')
    map_y = page.locator('#galaxyWrap').evaluate('(el)=>el.scrollTop')
    page.locator('#btnShop').click()
    assert page.locator('#btnShop').get_attribute('aria-current') == 'page'
    page.locator('#shopList').evaluate('(el)=>el.scrollTop=120')
    shop_y = page.locator('#shopList').evaluate('(el)=>el.scrollTop')
    assert shop_y > 0
    page.locator('#navSettings').click()
    page.screenshot(path=str(ARTIFACTS / 'soft-settings.png'))
    sound = page.locator('#btnSound').inner_text()
    page.locator('#btnSound').click()
    assert page.locator('#btnSound').inner_text() != sound
    page.locator('#btnSound').click()
    page.locator('#btnCode').click()
    assert page.locator('#codeBox').is_visible()
    page.evaluate("document.querySelector('#codeBox').classList.add('hide')")
    page.locator('#btnLang').click()
    assert page.locator('#langBox').is_visible()
    page.evaluate("document.querySelector('#langBox').classList.add('hide')")
    page.locator('#btnShop').click()
    assert page.locator('#shopList').evaluate('(el)=>el.scrollTop') == shop_y
    page.screenshot(path=str(ARTIFACTS / 'soft-upgrades.png'))
    page.locator('#navAdventure').click()
    assert page.evaluate('SEL_IDX') == selected
    assert page.locator('#galaxyWrap').evaluate('(el)=>el.scrollTop') == map_y
    page.locator('#btnShop').click()
    page.locator('#btnShopBack').click()
    assert page.evaluate('SEL_IDX') == selected, 'Shop Back must preserve selected stage too'
    # Every new label is contained at narrow, short landscape, mobile and tablet sizes.
    checks = 0
    for width, height in [(320,568),(390,844),(844,390),(768,1024)]:
        page.set_viewport_size({'width':width,'height':height})
        for lang in page.evaluate('Object.keys(L10N)'):
            page.evaluate('(lang)=>applyLanguage(lang)', lang)
            for tab, panel in [('navAdventure','menu'),('btnShop','shop'),('navSettings','settings')]:
                page.locator('#'+tab).click()
                assert page.locator('#'+panel).is_visible(), (lang, tab)
                assert page.locator('#hubNav [aria-current="page"]').count() == 1
                overflow = page.locator('#hubNav').evaluate('''el=>[...el.querySelectorAll('button')].some(b=>{
                    const r=b.getBoundingClientRect(); return b.scrollWidth>b.clientWidth+1 ||
                    r.left<0 || r.right>innerWidth || r.bottom>innerHeight+1;})''')
                assert not overflow, (lang, width, tab)
                assert page.locator('#'+panel).evaluate('(el)=>el.scrollWidth<=el.clientWidth+1'), (lang, width, panel)
                checks += 1
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate("applyLanguage('en'); PROGRESS=1; showMenu()")
    assert page.evaluate('JSON.stringify({META,COINS,PROGRESS})') == initial
    page.locator('#btnPlay').click()
    assert page.locator('#hubNav').is_hidden()
    assert page.locator('#settings').is_hidden()
    page.touchscreen.tap(195,450)
    page.mouse.move(195,450); page.mouse.down(); page.mouse.move(230,430,steps=5)
    page.wait_for_function('G.running && G.t>=3',timeout=120000)
    page.mouse.up()
    assert page.evaluate('Object.keys(META).length') == 0
    page.screenshot(path=str(ARTIFACTS / 'soft-game.png'))
    page.evaluate('showCards()')
    page.wait_for_selector('.card')
    page.screenshot(path=str(ARTIFACTS / 'soft-cards.png'))
    contrast = page.evaluate('''()=>{
        const rgb=s=>s.match(/[\\d.]+/g).slice(0,3).map(Number);
        const luminance=c=>c.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;})
          .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
        const fg=luminance(rgb(getComputedStyle(document.querySelector('.lvtitle')).color));
        const bg=luminance(rgb(getComputedStyle(document.querySelector('#cards')).backgroundColor));
        return (Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05);
    }''')
    assert contrast >= 4.5, ('Upgrade heading contrast', contrast)
    assert not errors, errors
    browser.close()
print(json.dumps({'layout_checks':checks,'cpu_rate':rate,'heading_contrast':contrast,'page_errors':errors}))
print('PASS hub navigation, state preservation, settings, 11 languages, zero-meta combat')
