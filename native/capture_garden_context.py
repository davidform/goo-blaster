"""Capture actual contextual garden UI; fixtures are explicitly labelled."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,BROWSER_CHANNEL
from playwright.sync_api import sync_playwright
root=Path(GAME_ROOT)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);manifest=[]
 for lang,w,h,house in [('zh-Hant',390,844,0),('zh-Hant',390,844,2),('en',320,568,2),('de',844,390,2),('en',1280,900,2)]:
  c=b.new_context(viewport={'width':w,'height':h});p=c.new_page();p.goto((root/'index.html').as_uri())
  p.evaluate('x=>{GARDEN=cleanGarden({house:x[1]});applyLanguage(x[0]);setHubPage("garden")}',[lang,house])
  build=p.evaluate('BUILD');folder=root/'store/screenshots'/build;folder.mkdir(parents=True,exist_ok=True)
  for view in ['farm','plant','kitchen','community','decorate']:
   if p.locator('#gardenContext').is_visible():p.locator('#gardenContextClose').click()
   if view=='plant':p.locator('.gardenSpot.plot').first.click()
   elif view!='farm':p.locator('#garden'+{'kitchen':'Kitchen','community':'Community','decorate':'Arrange'}[view]).click()
   name=f'garden-{view}-{lang}-{w}-house{house}.png';p.screenshot(path=str(folder/name))
   manifest.append({'file':name,'build':build,'sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'viewport':[w,h],'language':lang,'setup':f'QA fixture: clean save with cottage level {house}. No inventory injected. Real clicks for each view.'})
  c.close()
 (folder/'context-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');b.close()
