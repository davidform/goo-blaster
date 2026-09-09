"""Exercise the real victory button, downloaded PNG, and native bridge outcomes."""
import base64,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL

with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL)
    page=browser.new_page(viewport={'width':390,'height':844},accept_downloads=True)
    page.context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_REPORT_CPU','1'))})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    page.evaluate('LV_IDX=0;META={};start();G.t=G.winT;endGame(true)')
    page.locator('#btnSave').wait_for(state='visible')
    png=base64.b64decode(page.locator('#shot').get_attribute('src').split(',')[1])
    with page.expect_download() as info:page.locator('#btnSave').click()
    download=info.value
    assert download.suggested_filename=='goo-blaster-L1.png'
    assert Path(download.path()).read_bytes()==png and png[:8]==b'\x89PNG\r\n\x1a\n'
    # A WebView cannot use a browser download. The actual button must call native code.
    page.evaluate('''()=>{window.nativeCalls=[];window.Capacitor={getPlatform:()=> 'android',Plugins:{BattleReport:{
      saveImage:options=>{nativeCalls.push(options);return new Promise((resolve,reject)=>{window.finishSave=resolve;window.failSave=reject;});}
    }}};}''')
    page.locator('#btnSave').click()
    page.wait_for_function('nativeCalls.length===1',timeout=5000)
    assert page.locator('#btnSave').is_disabled()
    assert base64.b64decode(page.evaluate('nativeCalls[0].base64'))==png
    assert page.evaluate('nativeCalls[0].filename')=='goo-blaster-L1.png'
    page.evaluate("document.getElementById('btnSave').click()")
    assert page.evaluate('nativeCalls.length')==1
    for outcome,key in [('saved','shotSaved'),('cancelled','shotCancelled'),('error','shotSaveFailed')]:
        if outcome!='saved':page.locator('#btnSave').click()
        page.evaluate("failSave(new Error('storage unavailable'))" if outcome=='error' else 'finishSave({status:'+json.dumps(outcome)+'})')
        page.wait_for_function('(key)=>document.getElementById("shotStatus").textContent===T(key)',arg=key)
        assert page.locator('#btnSave').is_enabled()
    page.evaluate('delete Capacitor.Plugins.BattleReport')
    page.locator('#btnSave').click()
    page.wait_for_function('document.getElementById("shotStatus").textContent===T("shotSaveFailed")')
    # Long translations fit the actual outcome area on a small phone.
    page.set_viewport_size({'width':320,'height':568})
    for lang in page.evaluate('Object.keys(L10N)'):
        page.evaluate('lang=>applyLanguage(lang)',lang)
        page.locator('#btnSave').click()
        page.wait_for_function('document.getElementById("shotStatus").textContent===T("shotSaveFailed")')
        assert page.locator('#shotStatus').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
    page.evaluate("applyLanguage('zh-Hant');shotEl.src=makePolaroid(true)")
    page.locator('#btnSave').click()
    page.locator('#shotStatus').scroll_into_view_if_needed()
    page.screenshot(path=str(ARTIFACTS/'report-export-error-zh-Hant.png'))
    page.evaluate("Capacitor.Plugins.BattleReport={saveImage:async()=>({status:'saved'})}")
    page.locator('#btnSave').click()
    page.wait_for_function('document.getElementById("shotStatus").textContent===T("shotSaved")')
    page.wait_for_function('getComputedStyle(document.getElementById("over")).opacity==="1"')
    page.locator('#shotStatus').scroll_into_view_if_needed()
    assert page.locator('#shotStatus').evaluate('e=>getComputedStyle(e).backgroundColor==="rgb(255, 249, 238)"')
    page.screenshot(path=str(ARTIFACTS/'report-export-zh-Hant.png'))
    page.evaluate("shotEl.src='data:image/png;base64,';Capacitor.Plugins.BattleReport={saveImage:async()=>({status:'unknown'})}")
    page.locator('#btnSave').click()
    page.wait_for_function('document.getElementById("shotStatus").textContent===T("shotSaveFailed")')
    assert not errors,errors
    browser.close()
print('PASS real victory export: exact PNG, native save/cancel/error/missing bridge, duplicate taps, 11-language layout')
