"""Three festival games played by real UI; solver reads rendered board only."""
import json,os
from collections import deque
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL

def pond_route(cells):
 walls={i for i,c in enumerate(cells) if c=='rock'};pearls=[i for i,c in enumerate(cells) if c=='pearl'];start=cells.index('fish');goal=cells.index('goal');q=deque([(start,0,[])]);seen={(start,0)}
 while q:
  at,mask,path=q.popleft()
  if at==goal and mask==7:return path
  for j in (at-1 if at%5 else -1,at+1 if at%5<4 else -1,at-5 if at>=5 else -1,at+5 if at<20 else -1):
   if j<0 or j in walls:continue
   m=mask|(1<<pearls.index(j) if j in pearls else 0)
   if (j,m) not in seen:seen.add((j,m));q.append((j,m,path+[j]))
 raise AssertionError('Unsolvable pond')

def stars_solution(lights):
 for mask in range(512):
  v=lights[:]
  for i in range(9):
   if mask>>i&1:
    for j in (i,i-1 if i%3 else -1,i+1 if i%3<2 else -1,i-3 if i>=3 else -1,i+3 if i<6 else -1):
     if j>=0:v[j]^=1
  if all(v):return [i for i in range(9) if mask>>i&1]
 raise AssertionError('Unsolvable stars')

with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('[data-place=picnic]').click()
 assert p.evaluate('GARDEN.medals.join()==="0,0,0"&&GARDEN.theme===-1')
 assert p.locator('[data-level="2"]').is_disabled()
 old=p.evaluate('JSON.stringify([GARDEN.seeds,GARDEN.petals,GARDEN.pantry,COINS,META])')
 rounds=0
 for theme in range(3):
  p.locator("#btnHome").click();p.locator('[data-place="'+["picnic","pond","stars"][theme]+'"]').click();p.locator('#festivalStart').click()
  for level in range(1,4):
   if theme==0:
    seq=p.locator('.festivalSequence>span').evaluate_all('(es)=>es.map(e=>e.getAttribute("aria-label"))');foods=p.evaluate('[0,1,2].map(i=>T("gardenFood"+i))');answers=[foods.index(t) for t in seq]
    p.locator('#festivalReady').click()
    if level==1:
     p.locator(f'[data-answer="{(answers[0]+1)%3}"]').click();assert p.evaluate('GF.phase==="retry"&&GARDEN.medals[0]===0');p.locator('#festivalRetry').click();p.locator('#festivalReady').click()
    for a in answers:p.locator(f'[data-answer="{a}"]').click()
   elif theme==1:
    cells=p.locator('.festivalCell').evaluate_all('(es)=>es.map(e=>e.dataset.state)');route=pond_route(cells)
    for a in route:p.locator(f'[data-cell="{a}"]').click()
   else:
    lights=p.locator('.festivalCell').evaluate_all('(es)=>es.map(e=>+(e.getAttribute("aria-pressed")==="true"))')
    for a in stars_solution(lights):p.locator(f'[data-cell="{a}"]').click()
   assert p.evaluate('GF.phase==="won"'),(theme,level)
   assert p.evaluate('GARDEN.medals[GF.theme]===GF.level&&GARDEN.theme===GF.theme')
   before=p.evaluate('GARDEN.outings[GF.theme]');p.evaluate('gardenFestivalWin();gardenFestivalAct(0)');assert p.evaluate('GARDEN.outings[GF.theme]')==before
   rounds+=1
   p.locator('#gardenLife').scroll_into_view_if_needed();p.screenshot(path=str(ARTIFACTS/f'festival70-{theme}-{level}.png'))
   if level<3:p.locator('#festivalNext').click()
  # Replay changes the puzzle but retains the medal and costs no resources.
  p.locator('#festivalRetry').click();assert p.evaluate('GF.phase!=="won"&&GARDEN.medals[GF.theme]===3')
  p.locator('#festivalChoose').click()
 assert p.evaluate('JSON.stringify([GARDEN.seeds,GARDEN.petals,GARDEN.pantry,COINS,META])')==old
 earned=p.evaluate('JSON.stringify(GARDEN)');p.reload();p.locator('#navGarden').click();assert p.evaluate('JSON.stringify(GARDEN)')==earned
 result=p.evaluate('''()=>{const original=GARDEN,code=saveCodeEncode();GARDEN=cleanGarden();importSaveCode(code);const restored=JSON.stringify(GARDEN)===JSON.stringify(original);
 const a=cleanGarden({medals:[-1,99,Infinity],outings:[-2,1e15,'2.9'],theme:0});const clean=a.medals.join()==='0,3,0'&&a.outings.join()==='0,99999,2'&&a.theme===-1;
 const n=cleanGarden(original);n.rev++;n.theme=1;const merged=pickBetterSave({v:2,progress:9,garden:original},{v:2,progress:2,garden:n});
 const merge=merged.progress===9&&merged.garden.theme===1;return {restored,clean,merge};}''');assert all(result.values()),result
 # All rotations and levels have reachable pond goals and positive budgets.
 assert p.evaluate('''()=>{const g=GARDEN;for(let run=0;run<8;run++)for(let l=1;l<=3;l++){GARDEN.outings[1]=run;gardenFestivalStart(1,l);if(GF.limit<=0)return false;}GARDEN=g;return true;}''')
 # Invalid actions and locked levels cannot award progress.
 assert p.evaluate('''()=>{const g=GARDEN;GARDEN=cleanGarden();const r=!gardenFestivalStart(3,1)&&!gardenFestivalStart(0,3)&&!gardenFestivalStart(0,0);GARDEN=g;return r;}''')
 p.evaluate('GF=null;GARDEN_TAB="play";renderGarden()');layouts=0
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   for theme in range(3):
    p.evaluate('a=>{applyLanguage(a[0]);GF=null;GF_PICK=a[1];GARDEN_TAB="play";renderGarden()}',[lang,theme])
    assert p.locator('#gardenLife').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(lang,w,theme)
    for button in p.locator('#gardenLife button:visible').all():assert button.bounding_box()['height']>=44,(lang,w,theme)
    layouts+=1
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");GF=null;GF_PICK=2;GARDEN_TAB="play";renderGarden()')
 p.locator('#gardenLife').scroll_into_view_if_needed();p.screenshot(path=str(ARTIFACTS/'festival70-overview-zh.png'))
 p.emulate_media(reduced_motion='reduce');assert p.locator('.festivalHero .iconTwinkle').evaluate('e=>getComputedStyle(e).animationName')=='none'
 p.emulate_media(reduced_motion='no-preference');initial=p.locator('.festivalHero .iconTwinkle').evaluate('e=>getComputedStyle(e).opacity');p.wait_for_function('s=>getComputedStyle(document.querySelector(".festivalHero .iconTwinkle")).opacity!==s',arg=initial)
 assert not errors,errors
 (ARTIFACTS/'festival70.json').write_text(json.dumps(dict(result,rounds=rounds,layouts=layouts,offline=True,free_play=True,reduced_motion=True,errors=errors),indent=2),encoding='utf-8');b.close()
print('PASS 9 UI challenges, distinct boards, free replay, medals/themes, reload/backup/merge, 99 locale layouts, reduced motion')
