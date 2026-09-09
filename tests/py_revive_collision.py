"""Exercise revival from the real enemy-bullet loop, including remaining indices."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL
GAME=Path(GAME_ROOT)
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_REVIVE_CPU','1'))})
 page.goto((GAME/'index.html').as_uri());rows=[]
 stale=page.evaluate('''()=>{
   const raf=window.requestAnimationFrame;window.requestAnimationFrame=()=>0;
   META={revive:1};LV_IDX=0;start();G.P.hearts=1;G.P.iframe=0;
   for(let i=0;i<3;i++)shootE(G.P.x,G.P.y,0,0,1,5);
   const anchor=lastT;let error=null;
   try{loop(anchor-50);}catch(e){error=String(e);}
   window.requestAnimationFrame=raf;
   return {error,time:G.t,clockUnchanged:lastT===anchor,radii:G.SHOCK.map(s=>s.r)};
 }''')
 assert stale['error'] is None and stale['time']==0 and stale['clockUnchanged'] and all(r>=0 for r in stale['radii']),stale
 for count in [1,3,100]:
  for hit in sorted(set([0,count//2,count-1])):
   before=page.evaluate('''([count,hit])=>{META={revive:1};LV_IDX=0;start();
     G.P.hearts=1;G.P.iframe=0;G.hasMoved=true;DIAG.touch=3;
     for(let i=0;i<count;i++)shootE(i===hit?G.P.x:G.P.x+160,G.P.y,0,0,1,5);
     return G.t;}''',[count,hit])
   page.wait_for_function('(t)=>G.revives===0&&G.t>t+.25',arg=before,timeout=20000)
   row=page.evaluate('({hearts:G.P.hearts,max:G.P.maxHearts,bullets:G.EB.length,running:G.running,invincible:G.P.iframe>0})')
   assert row['hearts']==row['max'] and row['bullets']==0 and row['running'] and row['invincible'],row
   assert not errors,errors
   rows.append({'count':count,'hitIndex':hit,**row})
 for mode in ['hurt','shield','dead']:
  page.evaluate('''(mode)=>{META={revive:mode==='dead'?0:1};LV_IDX=0;start();
    G.P.hearts=mode==='hurt'?3:1;G.P.shieldN=mode==='shield'?1:0;G.P.iframe=0;
    G.hasMoved=true;DIAG.touch=3;for(let i=0;i<3;i++)shootE(G.P.x,G.P.y,0,0,1,5);
  }''',mode)
  if mode=='dead':page.wait_for_function('G.over&&!G.running')
  else:page.wait_for_function('G.t>.25')
  row=page.evaluate('({hearts:G.P.hearts,revives:G.revives,shield:G.P.shieldN,running:G.running})')
  assert row=={'hearts':{'hurt':2,'shield':1,'dead':0}[mode],'revives':0 if mode=='dead' else 1,'shield':0,'running':mode!='dead'},row
  assert not errors,errors
  rows.append({'mode':mode,**row})
 result={'build':page.evaluate('BUILD'),'staleFrame':stale,'rows':rows,'errors':errors}
 (ARTIFACTS/'revive-collision.json').write_text(json.dumps(result,indent=2));b.close()
print('PASS real projectile collision revival, all index positions, continued game loop')
