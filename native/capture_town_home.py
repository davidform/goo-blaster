"""Capture the real fresh-save town hub without injecting resources or progress."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,BROWSER_CHANNEL
from playwright.sync_api import sync_playwright
root=Path(GAME_ROOT)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);manifest=[]
 for lang,w,h in [('en',390,844),('zh-Hant',390,844),('en',1280,900)]:
  c=b.new_context(viewport={'width':w,'height':h});p=c.new_page();p.goto((root/'index.html').as_uri());p.evaluate('(l)=>{applyLanguage(l);renderStage()}',lang)
  build=p.evaluate('BUILD');folder=root/'store/screenshots'/build;folder.mkdir(parents=True,exist_ok=True)
  name=f'town-{lang}-{w}.png';p.screenshot(path=str(folder/name))
  manifest.append({'file':name,'build':build,'sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'viewport':[w,h],'language':lang,'setup':'Fresh save; only language changed; no progress/resources injected.'})
  if lang=='zh-Hant':
   for place in ['gate','house','picnic','pond','stars']:
    p.locator('[data-place="'+place+'"]').click()
    if place in ['picnic','pond','stars']:p.locator('#festivalStart').click()
    page_name=f'page-{place}-{lang}-{w}.png'
    p.screenshot(path=str(folder/page_name))
    manifest.append({'file':page_name,'build':build,'sha256':hashlib.sha256((root/'index.html').read_bytes()).hexdigest(),'viewport':[w,h],'language':lang,'setup':'Fresh save; entered '+place+' through its landmark; started challenge where available; no progress/resources injected.'})
    p.locator('#btnHome').click()
  c.close()
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');b.close()
