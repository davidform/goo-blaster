"""Record unretouched frames from normal combat simulation, for human selection.

Uses an isolated, attainable veteran save. No health resets, invented enemies,
forced drops, direct XP, or camera repositioning. Fixed-step clock is accelerated
for capture, not an FPS benchmark or evidence of human playtesting.
"""
import hashlib, json, os, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'index.html').read_bytes()
build=re.search(rb"const BUILD='([^']+)'",source)[1].decode()
out=ROOT/'_private'/'combat-candidates'/build/'defensive-build'
out.mkdir(parents=True,exist_ok=True)
rows=[]; errors=[]
BOT=r'''() => {
 const render=draw;draw=()=>{};
 try{
 for(let frame=0;frame<60 && !G.over;frame++){
  if(G.paused){const cards=[...document.querySelectorAll('#cards .card')];
   const pick=cards.find(c=>/Regen|Shield|First Aid/.test(c.innerText))||cards[cards.length-1];
   if(pick)pick.click();else break;
  }
  const P=G.P;let fx=0,fy=0;
  const boss=G.E.find(e=>e.boss&&e.hp>0);
  let target=boss || G.GEM.reduce((a,e)=>!a||Math.hypot(e.x-P.x,e.y-P.y)<Math.hypot(a.x-P.x,a.y-P.y)?e:a,null);
  if(target){let dx=target.x-P.x,dy=target.y-P.y,d=Math.hypot(dx,dy)||1;
   if(boss){dx=target.x-P.x;dy=target.y+245-P.y;d=Math.hypot(dx,dy)||1;}
   fx=dx/d;fy=dy/d;
  }else{fx=Math.cos(G.t*.4);fy=Math.sin(G.t*.4);}
  for(const e of G.E){let dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;
   if(d<e.r+85){let force=(e.r+85-d)/30;fx+=dx/d*force;fy+=dy/d*force;}}
  for(const e of G.EB){let dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;
   if(d<75){fx+=dx/d*(75-d)/22;fy+=dy/d*(75-d)/22;}}
  const edge=Math.hypot(P.x,P.y);if(edge>700){fx-=P.x/edge*3;fy-=P.y/edge*3;}
  const mag=Math.hypot(fx,fy)||1;IN.active=true;IN.dx=fx/mag;IN.dy=fy/mag;IN.mag=1;
  if(G.E.some(e=>Math.hypot(e.x-P.x,e.y-P.y)<e.r+P.r+18)&&P.dashCD<=0)tryDash(IN.dx,IN.dy);
  loop(lastT+1000/60);
  if(G.E.some(e=>e.boss&&e.flash<=0&&Math.abs(e.x-G.cam.x)<W/2-e.r-8&&Math.abs(e.y-G.cam.y)<H/2-e.r-100)&&G.t>(window.__lastClean||0)+1){window.__lastClean=G.t;break;}
 }
 }finally{draw=render;}
 draw();
 const on=e=>Math.abs(e.x-G.cam.x)<W/2-e.r-8&&Math.abs(e.y-G.cam.y)<H/2-e.r-100;
 const bosses=G.E.filter(e=>e.boss&&on(e));
 return {time:G.t,over:G.over,hearts:G.P.hearts,level:G.P.lv,kills:G.kills,
 enemies:G.E.filter(on).length,bullets:G.EB.filter(on).length,shots:G.B.filter(on).length,
 bosses:bosses.map(e=>({name:e.name,superBoss:!!e.superBoss,hp:e.hp,flash:e.flash||0,above:e.y<G.P.y-50})),
 overlay:!document.querySelector('#cards').classList.contains('hide'),
 flash:Math.max(G.nukeFlash,G.reviveFlash,G.hurt),toast:G.TXT.filter(x=>x.big).length,weapon:G.P.wep,meta:META};
}'''
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=os.environ.get('GOO_BROWSER_CHANNEL','msedge'))
 for stage in [5,10,20]:
  c=b.new_context(viewport={'width':540,'height':900},device_scale_factor=2,has_touch=True)
  c.add_init_script('window.requestAnimationFrame=()=>0');c.set_offline(True)
  p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto((ROOT/'index.html').as_uri())
  p.evaluate('''stage=>{META={hearts:2,revive:2,pickup:1,xp:0,wep:0,dmg:1,aspd:0};
    PROGRESS=50;LV_IDX=stage-1;SECONDARY_WEAPON='graffiti';start();}''',stage)
  p.touchscreen.tap(240,450)
  best=-1;kept=0
  for tick in range(450):
   r=p.evaluate(BOT)
   if r['over']:break
   score=r['enemies']*2+min(r['bullets'],35)+min(r['shots'],12)+sum((50 if x['superBoss'] else 15)+(40 if x['flash']<=0 else 0) for x in r['bosses'])+(25 if not r['toast'] else 0)
   if r['bosses'] and any(x['flash']<=0 for x in r['bosses']) and not r['overlay'] and r['hearts']>0 and r['flash']<.05 and score>best+3:
    name=f'stage-{stage}-t{int(r["time"]):03d}.png';p.screenshot(path=str(out/name));r.update(file=name,stage=stage,score=score);rows.append(r);best=score;kept+=1
  print(json.dumps({'stage':stage,'time':r['time'],'ended':r['over'],'candidates':kept}),flush=True)
  c.close()
 b.close()
assert not errors,errors
assert (ROOT/'index.html').read_bytes()==source
(out/'manifest.json').write_text(json.dumps({'build':build,'source_sha256':hashlib.sha256(source).hexdigest(),'method':__doc__,'errors':errors,'candidates':rows},indent=2),encoding='utf-8')
assert rows, 'No combat candidates; no images approved or published'
print('PASS source unchanged; candidate frames captured, human visual selection still required')
