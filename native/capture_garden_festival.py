"""Actual v70 themed village and puzzle screenshots; explicit attainable fixture."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1];out=root/'store/screenshots/v0.9.70';out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((root/'index.html').as_uri())
 p.evaluate('GARDEN=cleanGarden({house:2,petals:45,projects:6,stamps:102,orders:[3,3,3],medals:[3,3,3],outings:[3,3,3],theme:0,seeds:3});applyLanguage("zh-Hant");setHubPage("garden")')
 for theme in range(3):
  p.evaluate('i=>{GARDEN.theme=i;GF=null;GARDEN_TAB="farm";renderGarden();document.getElementById("gardenViewport").scrollIntoView({block:"start"})}',theme)
  p.screenshot(path=str(out/f'world-{theme}-zh.png'))
  p.locator('#gardenPlay').click();p.locator(f'.festivalTheme[data-theme="{theme}"]').click();p.locator('#festivalStart').click()
  if theme==0:
   p.screenshot(path=str(out/'picnic-study-zh.png'));first=p.evaluate('GF.seq[0]');p.locator('#festivalReady').click();p.locator(f'[data-answer="{first}"]').click()
  elif theme==1:
   for cell in [21,22,23,24]:p.locator(f'[data-cell="{cell}"]').click()
  else:p.locator('[data-cell="4"]').click()
  p.screenshot(path=str(out/f'play-{theme}-zh.png'))
 p.evaluate('GF=null;GF_PICK=1;applyLanguage("en");GARDEN_TAB="play";renderGarden()');p.locator('#festivalStart').click()
 for cell in [21,22,23,24]:p.locator(f'[data-cell="{cell}"]').click()
 p.screenshot(path=str(out/'pond-play-en.png'))
 p.evaluate('GF=null;GF_PICK=2;applyLanguage("zh-Hant");GARDEN_TAB="play";renderGarden();document.getElementById("gardenLife").scrollIntoView({block:"start"})');p.screenshot(path=str(out/'themes-zh.png'))
 assert not errors,errors
 m={'build':p.evaluate('BUILD'),'source_sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'method':'Unretouched offline game Canvas/DOM. Explicit reachable fixture: village 6/6 and medals 3/3/3 separately proven by UI tests. Not a player save or Pixel test. Challenges opened using actual UI; four legal pond moves collect the first pearl, one picnic answer and one star move show active play.','files':[f.name for f in out.glob('*.png')],'errors':errors}
 (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(m));b.close()
