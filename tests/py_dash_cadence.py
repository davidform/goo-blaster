"""Dash rhythm must not accelerate with level or permanent shop purchases."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844})
 c.add_init_script('window.requestAnimationFrame=()=>0');p=c.new_page()
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 rows=p.evaluate('''()=>{
  const rows=[];
  for(const shop of [0,1,2,3])for(const cards of [0,1,2])for(const level of [1,25]){
   META={dash:shop};LV_IDX=0;start();G.bosses=[];G.nukeCalm=999;G.P.wep={};G.P.lv=level;
   for(let i=0;i<cards;i++)UPGRADES.find(u=>u.id==='cd').f(G.P);
   const times=[];let protectedFrames=0;
   for(let i=0;i<1800;i++){
    if(G.P.dashCD<=0){tryDash(1,0);times.push(i/60);}
    update(1/60,1/60);if(G.P.iframe>0)protectedFrames++;
   }
   rows.push({shop,cards,level,cooldown:G.P.dashCDmax,reach:G.P.dashReach,times,protectedRatio:protectedFrames/1800});
  }
  return rows;
 }''')
 for row in rows:
  expected=3-.4*row['cards']
  assert abs(row['cooldown']-expected)<1e-6,row
  assert abs(row['reach']-(1+row['shop']*.04))<1e-6,row
  gaps=[b-a for a,b in zip(row['times'],row['times'][1:])]
  assert gaps and all(expected-.001<=x<=expected+.034 for x in gaps),row
  assert row['protectedRatio']<=.21,row
 (ARTIFACTS/'dash-cadence62.json').write_text(json.dumps(rows,indent=2));b.close()
print('PASS 24 shop/card/level combinations: 3.0 / 2.6 / 2.2s intervals and <=21% dash protection')
