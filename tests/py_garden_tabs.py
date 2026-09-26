"""Selected garden category, visible workspace and rendered colour agree."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL

tabs={'gardenFarm':'farm','gardenKitchen':'kitchen','gardenCommunity':'community','gardenArrange':'decorate'}
with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL)
    c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
    c.set_offline(True)
    p=c.new_page(); errors=[]; p.on('pageerror',lambda e:errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').click()
    checks=0
    def verify(selected):
        state=p.locator('#gardenActions button:visible').evaluate_all('(es)=>es.map(e=>({id:e.id,pressed:e.getAttribute("aria-pressed"),bg:getComputedStyle(e).backgroundColor}))')
        assert p.locator('#garden').get_attribute('data-workspace')==tabs[selected]
        assert [e['id'] for e in state if e['pressed']=='true']==[selected],state
        active=next(e['bg'] for e in state if e['id']==selected)
        inactive={e['bg'] for e in state if e['id']!=selected}
        assert len(inactive)==1 and active not in inactive,state
    for size in [(390,844),(844,390),(320,568),(1280,900)]:
        p.set_viewport_size(dict(zip(('width','height'),size)))
        for lang in p.evaluate('Object.keys(L10N)'):
            p.evaluate('lang=>applyLanguage(lang)',lang)
            for selected in ['gardenFarm','gardenKitchen','gardenCommunity','gardenArrange','gardenKitchen','gardenFarm']:
                p.locator('#'+selected).click();verify(selected)
                p.evaluate('renderGarden()');verify(selected)
                checks+=1
    p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant")')
    p.locator('#gardenArrange').click();verify('gardenArrange')
    build=p.evaluate('BUILD');folder=Path(GAME_ROOT)/'store/screenshots'/build;folder.mkdir(parents=True,exist_ok=True)
    p.screenshot(path=str(folder/'garden-selected-decorate-zh-Hant-390.png'))
    p.locator('#btnHome').click();p.locator('#navGarden').click();verify('gardenFarm')
    p.locator('.gardenSpot.building[data-index="0"]').click();verify('gardenKitchen')
    assert not errors,errors
    (ARTIFACTS/'garden-tabs.json').write_text(json.dumps({'build':build,'checks':checks,'errors':errors,'offline':True,'cpu':os.getenv('GOO_UI_CPU','1')}),encoding='utf-8')
    b.close()
print('PASS garden category selected state and actual colours: 264 clicks, redraw, home return, building shortcut, offline')
