"""Capture v71 actual UI feedback; isolated fresh save, no gameplay fixture."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'store/screenshots/v0.9.71';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((root/'index.html').as_uri());p.evaluate('applyLanguage("zh-Hant")')
 p.locator('#navGarden').click();p.locator('#gardenPlay').click()
 for theme in range(3):
  p.locator(f'[data-theme="{theme}"]').click();p.locator('#festivalStart').click()
  if theme==0:
   foods=p.evaluate('[0,1,2].map(i=>T("gardenFood"+i))');seq=p.locator('.festivalSequence>span').evaluate_all('(es)=>es.map(e=>e.getAttribute("aria-label"))');p.locator('#festivalReady').click();p.locator(f'[data-answer="{foods.index(seq[0])}"]').click()
  elif theme==1:
   p.locator('[data-cell="1"]').click();p.locator('[data-cell="2"]').click()
  else:p.locator('[data-cell="4"]').click()
  p.locator('#gardenLife').scroll_into_view_if_needed();p.screenshot(path=str(out/f'feedback-{theme}-zh.png'))
  p.locator('.festivalPanel').screenshot(path=str(out/f'panel-{theme}-zh.png'))
  p.locator('#festivalChoose').click()
 assert not errors,errors
 (out/'manifest.json').write_text(json.dumps({'build':p.evaluate('BUILD'),'sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'method':'Unretouched offline browser, fresh save. Chinese language selection only; challenges started and progressed through UI from displayed order/board. No resources, medals or puzzle state injected. Not a Pixel test.','errors':errors},ensure_ascii=False,indent=2),encoding='utf-8');b.close()
