"""Every game screen has fixed bounds, reachable leaves, and a stationary title on swipe."""
import json, os, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL
from ui_pages import reveal

folder=ARTIFACTS/'no-scroll';folder.mkdir(exist_ok=True)
issues=[];checks=0
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':393,'height':759},has_touch=True,reduced_motion='reduce');c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 cdp=c.new_cdp_session(p);cdp.send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());p.locator('#navGarden').tap()
 title=p.locator('#garden>h1').bounding_box()
 text=p.locator('#gardenQuestDetail').bounding_box();start_y=min(600,text['y']+text['height']/2)
 cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':200,'y':start_y}]})
 for y in [max(40,start_y-d) for d in [40,80,120,160]]:cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':200,'y':y}]})
 cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
 p.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 swipe={'scrollTop':p.locator('#garden').evaluate('e=>e.scrollTop'),'titleDelta':p.locator('#garden>h1').bounding_box()['y']-title['y']}
 assert swipe['scrollTop']==0, 'Garden page scrolls and loses its heading: '+str(swipe)
 assert abs(swipe['titleDelta'])<1,'Garden heading moves on swipe: '+str(swipe)
 initial=p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')
 def settle():p.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 def inspect(label,size,lang):
  global checks
  settle()
  bad=p.evaluate('''()=>{
   const roots=[...document.querySelectorAll('.panel')].filter(e=>e.getClientRects().length);
   if(roots.length!==1)return [{reason:'overlapping screens',ids:roots.map(e=>e.id)}];
   const root=roots[0],bounds=root.getBoundingClientRect(),bad=[];
   if(root.scrollHeight>root.clientHeight+1)bad.push({id:root.id,reason:'screen overflow',height:root.clientHeight,scroll:root.scrollHeight});
   for(const e of root.querySelectorAll('h1,button,.folioBody>*:not(.folioOff),.folioNav,.festivalPanel')){
    if(!e.getClientRects().length||e.closest('#townScene,#gardenHotspots,#gardenContext'))continue;
    const r=e.getBoundingClientRect();let box=bounds;
    const leaf=e.closest('.folioBody');if(leaf)box=leaf.getBoundingClientRect();
    if(r.top<box.top-1||r.bottom>box.bottom+1||r.left<box.left-1||r.right>box.right+1)bad.push({id:e.id||e.className,reason:'clipped',rect:r.toJSON(),parent:box.toJSON()});
   }
   return bad;
  }''')
  if bad:issues.append(dict(label=label,size=size,lang=lang,bad=bad))
  checks+=1
 for size in [(320,568),(393,759),(390,844),(568,320),(844,390),(1280,900)]:
  p.set_viewport_size(dict(zip(('width','height'),size)))
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('l=>applyLanguage(l)',lang)
   cases=[('home',"setHubPage('home')"),('adventure',"setHubPage('adventure')"),('shop','showShop()'),('settings',"setHubPage('settings')"),('farm',"setHubPage('garden');gardenOpen('farm')"),('kitchen',"gardenOpen('kitchen')"),('community',"gardenOpen('community')"),('decorate',"gardenOpen('decorate')")]
   cases += [(f'theme-{theme}',f'GF=null;GF_PICK={theme};gardenOpen("play")') for theme in range(3)]
   cases += [(f'playing-{theme}',f'gardenFestivalStart({theme},1)') for theme in range(3)]
   for name,cmd in cases:
    p.evaluate(cmd);settle()
    # Every leaf is visited using its actual previous/next controls.
    for book in p.locator('.panel:visible .folio:visible').all():
     previous=book.locator(':scope>.folioNav button').first
     while previous.is_visible() and previous.is_enabled():previous.tap()
    for turn in range(30):
     inspect(f'{name}/{turn}',size,lang)
     following=p.locator('.panel:visible .folioNav:visible button:last-child:not(:disabled)').first
     if not following.count():break
     following.tap()
    else:raise AssertionError('Unbounded pagination')
    if size==(393,759) and lang in ['en','zh-Hant'] and name in ['farm','shop','decorate','playing-1']:
     p.screenshot(path=str(folder/f'{name}-{lang}.png'))
 # Navigation/challenges have not granted resources or changed a save.
 assert p.evaluate('JSON.stringify([PROGRESS,COINS,META,GARDEN])')==initial
 assert not errors,errors
 report=dict(build=p.evaluate('BUILD'),sha256=hashlib.sha256((Path(GAME_ROOT)/'index.html').read_bytes()).hexdigest(),checks=checks,issues=issues,errors=errors,swipe=swipe,cpu=os.getenv('GOO_UI_CPU','1'),offline=True)
 (folder/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
assert not issues,json.dumps(issues[:4],ensure_ascii=False)
print(f'PASS {checks} visible pages, 66 size/language combinations, stationary title on touch swipe, every page reachable, offline save unchanged')
