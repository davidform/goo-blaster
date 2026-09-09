"""Range upgrades must change projectile travel and hits, not only a stat label."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL
GAME=Path(GAME_ROOT)
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 c.add_init_script('window.requestAnimationFrame=()=>0;')
 page=c.new_page();c.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_RANGE_CPU','1'))});page.goto((GAME/'index.html').as_uri());errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 rows=page.evaluate('''()=>{
   const rows=[];
   for(let meta=0;meta<=3;meta++)for(let card=0;card<=2;card++)for(const weapon of ['bubble','graffiti','yoyo']){
     let seed=91;Math.random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};
     META={range:meta};LV_IDX=0;start();if(!SFX.isMuted())SFX.toggle();
     G.P.rangeUp=card;G.P.atkRange=ATK_RANGE_BASE+G.P.metaRange+card*ATK_RANGE_STEP;
     G.P.dmgEff=1;G.P.crit=0;G.P.wep={};G.waves.forEach(w=>w.rate=0);G.bosses=[];
     spawnEnemy('slime',1);const target=G.E[0];Object.assign(target,{x:0,y:-300,spd:0,ranged:false,hp:10000,maxhp:10000});
     WEAPONS[weapon].fire(G.P,1);const shots=G.B.slice(),speed=shots.map(s=>Math.hypot(s.vx,s.vy));
     const life=shots.map(s=>s.life);let distance=0;
     for(let frame=0;frame<120;frame++){update(1/60,1/60);for(const s of shots)distance=Math.max(distance,Math.hypot(s.x,s.y));}
     rows.push({meta,card,weapon,speed,life,count:shots.length,distance,damage:10000-target.hp});
   }
   return rows;
 }''')
 for row in rows:
  base={'bubble':600,'graffiti':470,'yoyo':430}[row['weapon']]
  scale=1+.1*row['meta']+.15*row['card']
  assert all(abs(s-base*scale)<1e-8 for s in row['speed']),row
  assert row['count']==(3 if row['weapon']=='graffiti' else 1),row
  assert all(abs(l-{'bubble':1.25,'graffiti':.52,'yoyo':1.5}[row['weapon']])<1e-8 for l in row['life']),row
 def get(w,m,c):return next(r for r in rows if (r['weapon'],r['meta'],r['card'])==(w,m,c))
 assert get('graffiti',0,0)['damage']==0 and get('graffiti',2,0)['damage']>0
 assert all(get('yoyo',m,0)['distance']<get('yoyo',m+1,0)['distance'] for m in range(3))
 assert get('yoyo',3,2)['distance']>get('yoyo',3,0)['distance']
 edges=page.evaluate('''()=>{
   META={range:3};LV_IDX=0;start();G.P.rangeUp=2;G.P.dmgEff=1;
   const caps=[weaponShotSpeed({},100),weaponShotSpeed({metaRange:-900,rangeUp:0},100),weaponShotSpeed({metaRange:9000,rangeUp:99},100)];
   G.B=[];shoot(0,0,0,380,1,5,0,{});const secondary=G.B[0].vx;
   G.EB=[];shootE(0,0,0,215,1,5);const hostile=G.EB[0].vx;
   G.P.wep={bubble:5};G.P.atkRange=1100;G.B=[];
   G.E=[{x:0,y:-150,r:15,hp:10000,maxhp:10000,boss:false}];spawnAllies();G.ALLY.forEach(a=>a.cd=0);updateAllies(.01);
   const ally=G.B.map(s=>Math.hypot(s.vx,s.vy));
   G.E=[{x:W/2+100,y:0,r:15,hp:10000,maxhp:10000,boss:false}];
   const offscreen=nearest(0,0,1100);
   return {caps,secondary,hostile,ally,offscreen};
 }''')
 assert edges['caps']==[100,100,160] and edges['secondary']==380 and edges['hostile']==215,edges
 assert len(edges['ally'])==9 and all(abs(s-960)<1e-7 or abs(s-928)<1e-7 for s in edges['ally']),edges
 assert edges['offscreen'] is None and not errors,(edges,errors)
 # Largest legal game step (.05 wall seconds at max 1.6 game speed).
 # Fast upgraded shots must not jump over the target between frame endpoints.
 slow=page.evaluate('''()=>{
   const rows=[];
   for(let meta=0;meta<=3;meta++)for(let card=0;card<=2;card++){
     META={range:meta};LV_IDX=0;start();G.P.lv=20;G.P.rangeUp=card;
     G.P.dmgEff=1;G.P.crit=0;G.P.wep={};G.waves.forEach(w=>w.rate=0);G.bosses=[];
     spawnEnemy('slime',1);const target=G.E[0];
     Object.assign(target,{x:0,y:-340,spd:0,ranged:false,hp:10000,maxhp:10000});
     WEAPONS.bubble.fire(G.P,1);const swept=G.B[0].sweep;
     for(let frame=0;frame<30;frame++)update(.05,.05);
     rows.push({meta,card,swept,damage:10000-target.hp});
   }
   return {rows,geometry:[shotSegmentDist2(0,0,0,0,3,4),shotSegmentDist2(0,0,10,0,5,3),shotSegmentDist2(0,0,10,0,20,0)]};
 }''')
 assert all(r['swept']==bool(r['meta'] or r['card']) and r['damage']>0 for r in slow['rows']),slow
 assert slow['geometry']==[25,9,100],slow
 (ARTIFACTS/'range-reach.json').write_text(json.dumps({'rows':rows,'edges':edges,'slow':slow,'errors':errors},indent=2))
 b.close()
print('PASS 36 combinations: real travel/hits, zero state, caps, allies and unchanged hostile shots')
