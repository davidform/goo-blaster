"""Execute movement across Boss bodies, including coarse steps and invulnerability."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844})
 c.add_init_script('window.requestAnimationFrame=()=>0')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 rows=p.evaluate('''()=>{
  const rows=[];
  for(const stage of [1,5,25,50])for(const angle of [0,.7,1.57,3.14,4.3])for(const dt of [1/120,1/30,.2]){
   META={};LV_IDX=stage-1;start();G.bosses=[];G.P.wep={};G.P.crit=0;G.spawnAcc=-100;
   spawnBoss(buildBosses(CUR())[0]);const e=G.boss;e.x=0;e.y=0;e.spd=0;e.cd=999;e.laserCD=999;
   const P=G.P,r=P.r+e.r;P.x=-Math.cos(angle)*(r+20);P.y=-Math.sin(angle)*(r+20);
   P.iframe=5;const hearts=P.hearts;tryDash(Math.cos(angle),Math.sin(angle));
   let min=Infinity;
   for(let n=0;n<Math.ceil(.4/dt);n++){update(dt,dt);min=Math.min(min,Math.hypot(P.x-e.x,P.y-e.y));}
   rows.push({stage,dt,min,r,hearts:P.hearts,expected:hearts,side:P.x*Math.cos(angle)+P.y*Math.sin(angle)});
  }
  return rows;
 }''')
 for r in rows:
  assert r['min']>=r['r']-.001 and r['side']<0 and r['hearts']==r['expected'],r
 edge=p.evaluate('''()=>{
  META={};LV_IDX=0;start();G.bosses=[];G.P.wep={};G.spawnAcc=-100;
  spawnBoss(buildBosses(CUR())[0]);const e=G.boss,P=G.P;e.x=P.x;e.y=P.y;e.spd=0;e.cd=999;
  P.iframe=3;update(.016,.016);const finite=Number.isFinite(P.x)&&Math.hypot(P.x-e.x,P.y-e.y)>=P.r+e.r;
  P.x=e.x-e.r-P.r-5;P.y=e.y;P.iframe=0;const hearts=P.hearts;
  IN.active=true;IN.mag=1;IN.dx=1;IN.dy=0;update(.05,.05);endJoy();
  const damage=P.hearts===hearts-1;P.iframe=10;tryDash(-1,0);const x=P.x;update(.03,.03);
  return {finite,damage,escape:P.x<x};
 }''')
 assert all(edge.values()),edge
 assert not errors,errors
 (ARTIFACTS/'boss-solid.json').write_text(json.dumps({'rows':rows,'edge':edge,'errors':errors},indent=2))
 b.close()
print('PASS 60 swept Boss movement cases, overlap recovery, normal contact damage and escape')
