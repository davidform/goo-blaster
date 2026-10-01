"""Fixed-screen edges: unlocked themes and all challenge/overlay states."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL
import os
issues=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.context.set_offline(True);p.context.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))});p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 def check(label):
  p.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  bad=p.evaluate('''()=>{const root=document.querySelector('.overlayBox:not(.hide) .box')||document.querySelector('.panel:not(.hide)'),r=root.getBoundingClientRect();return [...root.querySelectorAll('button,p,h1,h2,.festivalSequence,.festivalGrid')].filter(e=>e.getClientRects().length).map(e=>({id:e.id||e.className,r:e.getBoundingClientRect().toJSON()})).filter(e=>e.r.top<Math.max(0,r.top)-1||e.r.bottom>Math.min(innerHeight,r.bottom)+1||e.r.left<r.left-1||e.r.right>r.right+1)}''')
  if bad:issues.append([label,size,lang,bad])
 for size in [(320,568),(568,320),(393,759),(844,390)]:
  p.set_viewport_size(dict(zip(('width','height'),size)))
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('l=>{applyLanguage(l);GARDEN.medals=[3,3,3];GARDEN.theme=1;setHubPage("garden");}',lang)
   p.evaluate('GF=null;GF_PICK=1;gardenOpen("play")')
   p.locator('#festivalStyle').click()
   assert p.locator('#gardenViewport').is_visible(), 'Applying a theme must reveal the scene page'
   p.evaluate('gardenNeedCrop(1)')
   assert p.locator('#gardenQuestAction').is_visible(), 'Grow action must reveal the planting page'
   for theme in range(3):
    p.evaluate('t=>{GF=null;GF_PICK=t;gardenOpen("play")}',theme);check(f'{theme}/unlocked-brief')
    for phase in ['study','play','retry','won']:
     if phase=='study' and theme!=0:continue
     p.evaluate('a=>{gardenFestivalStart(a[0],2);GF.phase=a[1];if(GF.phase==="retry"&&GF.theme===0)GF.feedback={dish:1};gardenLifeRender()}',[theme,phase])
     check(f'{theme}/{phase}')
   p.evaluate('setHubPage("settings")')
   for selector in ['#btnLang','#btnCode']:
    p.locator(selector).click();check(selector)
    p.evaluate("document.querySelectorAll('.overlayBox').forEach(e=>e.classList.add('hide'))")
   p.evaluate('showReading(T("storyTitle"),stageStory(0))');check('reading')
   p.evaluate("document.querySelectorAll('.overlayBox').forEach(e=>e.classList.add('hide'))")
 (ARTIFACTS/'screen-states.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
assert not issues,json.dumps(issues[:4],ensure_ascii=False)
assert not errors,errors
print('PASS 11 languages x 4 sizes: challenge phases, theme restore, language/code/story overlays, offline')
