"""Real one-minute countdown capture; no clock overrides or save injection."""
import json,time,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'store/screenshots/v0.9.68'
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((root/'index.html').as_uri());p.evaluate('applyLanguage("zh-Hant")');p.locator('#navGarden').click();start=time.monotonic();p.locator('#gardenQuestAction').click()
 p.screenshot(path=str(out/'garden-countdown-zh.png'))
 p.wait_for_function('document.getElementById("gardenQuest").dataset.step==="harvest"',timeout=120000)
 elapsed=time.monotonic()-start;assert 59<=elapsed<120,elapsed
 p.screenshot(path=str(out/'garden-ready-zh.png'));assert p.evaluate('GARDEN.petals===0')
 p.locator('#gardenQuestAction').click();assert p.evaluate('GARDEN.petals===3&&GARDEN.plots.every(p=>!p)')
 manifest={'build':p.evaluate('BUILD'),'source_sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'method':'Unretouched live Canvas/DOM. Isolated fresh save; real Plant/Harvest buttons; real elapsed minute, no time override or save injection. Not a phone performance test.','elapsed_seconds':round(elapsed,2),'viewport':[390,844],'device_scale_factor':2,'errors':errors,'files':['garden-countdown-zh.png','garden-ready-zh.png'],'selection':'Countdown image after three unchanged combat images; shows planting activity and clear timer.'}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');assert not errors;print(json.dumps(manifest));b.close()
