"""Privacy is reachable from settings in every locale without replacing the game."""
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

POLICY = 'https://davidform.github.io/goo-blaster/privacy.html'
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=BROWSER_CHANNEL)
    context = browser.new_context(viewport={'width':390,'height':844}, has_touch=True)
    context.set_offline(True)
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate', {'rate':int(os.getenv('GOO_UI_CPU','1'))})
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    initial = page.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')
    checks = 0
    for width,height in [(320,568),(390,844),(844,390),(1280,900)]:
        page.set_viewport_size({'width':width,'height':height})
        for lang in page.evaluate('Object.keys(L10N)'):
            page.evaluate('lang=>applyLanguage(lang)',lang)
            page.locator('#navSettings').tap()
            link = page.locator('#btnPrivacy')
            assert link.count()==1 and link.is_visible()
            assert link.inner_text()==page.evaluate("T('privacyPolicy')")
            assert link.get_attribute('href')==POLICY
            assert link.get_attribute('target')=='_blank'
            assert {'noopener','noreferrer'}<=set(link.get_attribute('rel').split())
            link.scroll_into_view_if_needed()
            assert link.evaluate('e=>{const r=e.getBoundingClientRect(),n=document.querySelector("#hubNav").getBoundingClientRect();return r.height>=48&&r.width>=48&&r.top>=0&&r.bottom<=n.top+1&&e.scrollWidth<=e.clientWidth}'),(lang,width,height)
            assert page.locator('#hubNav [aria-current="page"]').get_attribute('id')=='navSettings'
            page.locator('#btnHome').tap()
            assert page.locator('#townHome').is_visible()
            checks+=1
    # Real click opens a separate context. Serve a deterministic policy fixture;
    # public URL contents and Android external-browser behavior are separate checks.
    context.route(POLICY, lambda route: route.fulfill(status=200,content_type='text/html',body='<title>Privacy test destination</title><p>Privacy policy</p>'))
    page.locator('#navSettings').tap()
    with context.expect_page() as opened:
        page.locator('#btnPrivacy').tap()
    policy = opened.value
    policy.wait_for_url(POLICY)
    policy.wait_for_load_state()
    assert policy.title()=='Privacy test destination'
    assert policy.evaluate('window.opener===null')
    policy.close()
    assert page.locator('#settings').is_visible()
    assert page.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')==initial
    folder=Path(GAME_ROOT)/'store/screenshots'/page.evaluate('BUILD');folder.mkdir(parents=True,exist_ok=True)
    shots=[]
    page.set_viewport_size({'width':390,'height':844})
    for lang in ['en','zh-Hant']:
        page.evaluate('lang=>applyLanguage(lang)',lang)
        page.locator('#settings').evaluate('e=>e.scrollTop=0')
        name=f'privacy-settings-{lang}-390.png'
        page.screenshot(path=str(folder/name))
        shots.append({'file':name,'language':lang,'viewport':[390,844],'setup':'Fresh save; real settings navigation; no injected resources','sha256':hashlib.sha256((Path(GAME_ROOT)/'index.html').read_bytes()).hexdigest()})
    (folder/'privacy-manifest.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2),encoding='utf-8')
    assert not errors,errors
    (ARTIFACTS/'privacy-entry.json').write_text(json.dumps({'layouts':checks,'offline_navigation':True,'external_destination_fixture':True,'save_unchanged':True,'errors':errors,'cpu':os.getenv('GOO_UI_CPU','1')}),encoding='utf-8')
    browser.close()
print('PASS privacy entry: 44 layouts, real popup, noopener, offline navigation and unchanged saves')
