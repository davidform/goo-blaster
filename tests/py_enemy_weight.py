"""Same-seed actual spawned enemies: strength/speed tradeoff and real travel."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);p=b.new_page()
 p.context.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_WEIGHT_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 rows=p.evaluate('''()=>{
   const random=Math.random;Math.random=()=>.5;
   const rows=[];
   try{for(const type of Object.keys(ETYPE))for(const lv of [0,2,4,6,8,29,49])for(const mult of [1,2,10,100]){
     LV_IDX=lv;META={};start();spawnEnemy(type,mult);const e=G.E.at(-1);
     rows.push({type,lv,mult,hp:e.hp,spd:e.spd,base:ETYPE[type].spd,player:G.P.spd,tier:e.tier,cd:e.cdMin});
   }}finally{Math.random=random;}
   return rows;
 }''')
 for kind in ['slime','bunny','drone','bomber']:
  r=[x for x in rows if x['type']==kind]
  for x in r:assert .7*.7*x['base']*1.01-1e-6<=x['spd']<=min(.7*1.01*x['base'],x['player']*.6)+1e-6,x
  for mult in [1,2,10,100]:
   a=[x for x in r if x['mult']==mult]
   assert all(y['spd']<=x['spd']+1e-7 for x,y in zip(a,a[1:])),a
  first=next(x for x in r if x['lv']==0 and x['mult']==1)
  last=next(x for x in r if x['lv']==49 and x['mult']==10)
  assert last['hp']>first['hp'] and last['spd']<first['spd'],(first,last)
 assert next(x for x in rows if x['type']=='bunny' and x['lv']==0 and x['mult']==1)['spd']>next(x for x in rows if x['type']=='slime' and x['lv']==0 and x['mult']==1)['spd']
 travel=p.evaluate('''()=>{
   const random=Math.random;Math.random=()=>.5;
   try{return [1,10].map(mult=>{
     LV_IDX=8;META={};start();G.bosses=[];G.nukeCalm=999;G.P.iframe=999;
     G.P.wep={};G.E=[];spawnEnemy('slime',mult);const e=G.E[0];e.x=G.P.x+250;e.y=G.P.y;e.ranged=false;
     const before=e.x;for(let i=0;i<20;i++)update(.016,.016);
     return {mult,distance:before-e.x,spd:e.spd};
   });}finally{Math.random=random;}
 }''')
 assert 0<travel[1]['distance']<travel[0]['distance'],travel
 (ARTIFACTS/'enemy-weight.json').write_text(json.dumps({'rows':rows,'travel':travel},indent=2),encoding='utf-8')
 b.close()
print('PASS 112 spawned enemy cases: stronger tiers/multipliers slow down, type identity/cap preserved, real update-loop travel decreases')
