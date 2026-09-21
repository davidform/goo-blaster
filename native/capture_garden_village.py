"""Unretouched v69 village UI; reachable fixture documented by py_garden_village.
This is product illustration, not a claim of human play or phone performance.
"""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'store/screenshots/v0.9.69';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((root/'index.html').as_uri())
 p.evaluate('GARDEN=cleanGarden({house:2,petals:45,projects:6,stamps:102,orders:[3,3,3],seeds:3});applyLanguage("zh-Hant");setHubPage("garden")')
 for i in range(3):
  p.locator(f'.gardenSpot[data-kind=plot][data-index="{i}"]').click();row=p.locator('.gardenPlot').nth(i);row.locator('select').select_option(str(i));row.locator('button').click()
 p.evaluate('GV.selected=null;renderGarden();document.getElementById("gardenViewport").scrollIntoView({block:"start"})')
 p.screenshot(path=str(out/'village-world-zh.png'))
 # A reachable pre-delivery inventory. All counts are obtainable from plants.
 p.evaluate('GARDEN.pantry=[3,4,2,1,0,0];GARDEN.projects=2;GARDEN.stamps=9;GARDEN.orders=[5,0,0];renderGarden()')
 p.locator('#gardenKitchen').click();p.locator('#gardenLife').scroll_into_view_if_needed();p.screenshot(path=str(out/'village-kitchen-zh.png'))
 p.locator('#gardenCommunity').click();p.locator('#gardenLife').scroll_into_view_if_needed();p.screenshot(path=str(out/'village-orders-zh.png'))
 p.evaluate('GARDEN.projects=6;GARDEN.stamps=102;GARDEN.orders=[3,3,3];GARDEN.petals=73;applyLanguage("en");GARDEN_TAB="farm";renderGarden()')
 p.set_viewport_size({'width':390,'height':844});p.evaluate('document.getElementById("gardenViewport").scrollIntoView({block:"start"})');p.screenshot(path=str(out/'village-world-en.png'))
 assert not errors,errors
 manifest={'build':p.evaluate('BUILD'),'source_sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'method':'Actual unretouched offline Canvas/DOM. Explicit reachable save fixtures; 6 projects/102 reputation/3 orders per resident proven by tests/py_garden_village.py through UI with accelerated crop time. Not a human save or phone FPS test. Planting done through UI.','files':[x.name for x in out.glob('*.png')],'selection':'Village image follows 3 real combat screenshots. Kitchen/orders illustrate the secondary loop; no invented assets or combat.','errors':errors}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(manifest));b.close()


