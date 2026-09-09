"""Dashing must preserve protection from a hit, shield, or revival."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL
GAME=Path(GAME_ROOT)
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_DASH_CPU','1'))})
 page.goto((GAME/'index.html').as_uri())
 rows=page.evaluate('''()=>{const rows=[];for(const source of ['none','short','hurt','panic','shield','revive']){
   META={revive:source==='revive'?1:0};LV_IDX=0;start();G.P.crit=0;
   if(!['none','short'].includes(source)){
     G.P.hearts=source==='revive'?1:3;G.P.panic=source==='panic'?1:0;G.P.shieldN=source==='shield'?1:0;
     hurtPlayer();
   }else G.P.iframe=source==='short'?.2:0;
   const before=G.P.iframe;tryDash(1,0);
   rows.push({source,before,after:G.P.iframe,duration:G.P.dashT,cooldown:G.P.dashCD});
 }return rows;}''')
 for row in rows:
  assert row['after']==max(row['before'],.42) and row['duration']==.32 and row['cooldown']==3,row
 # Actual two-finger input, followed by a projectile after the short dash window.
 page.evaluate('''()=>{META={revive:1,dash:3};LV_IDX=0;start();G.P.hearts=1;hurtPlayer();
   G.hasMoved=true;DIAG.touch=3;
   const cv=document.querySelector('#cv');
   const touch=(id,x,y)=>new Touch({identifier:id,target:cv,clientX:x,clientY:y});
   const move=touch(1,195,480),dash=touch(2,BTN.x,BTN.y);
   cv.dispatchEvent(new TouchEvent('touchstart',{touches:[move],changedTouches:[move],bubbles:true}));
   cv.dispatchEvent(new TouchEvent('touchstart',{touches:[move,dash],changedTouches:[dash],bubbles:true}));
   cv.dispatchEvent(new TouchEvent('touchend',{touches:[move],changedTouches:[dash],bubbles:true}));
   endJoy();
 }''')
 page.wait_for_function('G.t>.7&&G.P.dashT<=0',timeout=20000)
 before=page.evaluate('''()=>{const before={hearts:G.P.hearts,iframe:G.P.iframe,t:G.t};shootE(G.P.x,G.P.y,0,0,1,5);return before;}''')
 page.wait_for_function('(t)=>G.t>t+.1',arg=before['t'])
 after=page.evaluate('({hearts:G.P.hearts,iframe:G.P.iframe,revives:G.revives})')
 assert before['iframe']>1 and after['hearts']==before['hearts'] and 0<after['iframe']<before['iframe'],(before,after)
 assert not errors,errors
 (ARTIFACTS/'dash-protection.json').write_text(json.dumps({'rows':rows,'before':before,'after':after,'errors':errors},indent=2));b.close()
print('PASS unchanged dash duration/cooldown, protection sources and real two-finger revival escape')
