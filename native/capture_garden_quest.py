"""Unretouched task-board captures from a new save and real settlement cycles."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'store/screenshots/v0.9.67';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((ROOT/'index.html').as_uri());p.evaluate('applyLanguage("zh-Hant")');p.locator('#navGarden').click()
 def shot(name):
  p.evaluate('document.getElementById("garden").scrollTop=0');p.screenshot(path=str(OUT/name))
 shot('quest-start-zh.png');p.locator('#gardenQuestAction').click();shot('quest-grow-zh.png')
 p.evaluate('LV_IDX=0;start();endGame(true)');p.locator('#btnGarden').click();shot('quest-harvest-zh.png');p.locator('#gardenQuestAction').click()
 for _ in range(3):
  p.locator('#gardenQuestAction').click();p.evaluate('LV_IDX=0;start();endGame(true)');p.locator('#btnGarden').click();p.locator('#gardenQuestAction').click()
 shot('quest-repair-zh.png');p.locator('#gardenQuestAction').click();shot('quest-restored-zh.png');p.evaluate('applyLanguage("en")');shot('quest-restored-en.png')
 manifest={'build':p.evaluate('BUILD'),'source_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'method':'Unretouched real Canvas/DOM; isolated new save; four successful settlements simulated via endGame(true); no human win or phone performance claim','viewport':[390,844],'device_scale_factor':2,'errors':errors,'files':[x.name for x in OUT.glob('*.png')]}
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert not errors;print(json.dumps(manifest));b.close()
