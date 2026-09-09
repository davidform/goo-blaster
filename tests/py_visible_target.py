"""A visible large boss must be targetable without widening small-enemy targeting."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL
GAME=Path(GAME_ROOT)
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL)
 rows=[]
 for width,height in [(390,844),(844,390)]:
  page=b.new_page(viewport={'width':width,'height':height});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_TARGET_CPU','1'))})
  page.add_init_script('window.requestAnimationFrame=()=>0;')
  page.goto((GAME/'index.html').as_uri())
  result=page.evaluate('''()=>{
   META={};LV_IDX=49;start();G.P.x=G.P.y=G.cam.x=G.cam.y=0;G.P.dmgEff=1;
   spawnBoss(buildBosses(CUR()).find(b=>b.superBoss));const e=G.boss,rows=[];
   for(const axis of ['x','y'])for(const sign of [-1,1])for(const visible of [true,false]){
    e.x=e.y=0;e[axis]=sign*((axis==='x'?W:H)/2+(visible?e.r/2:e.r+1));
    G.B=[];const target=nearest(0,0,2000);G.P.atkRange=2000;WEAPONS.bubble.fire(G.P,1);
    rows.push({axis,sign,visible,target:target===e,bullets:G.B.length});
   }
   G.E=[{x:W/2+43,y:0,r:15,hp:10}];const smallEdge=!!nearest(0,0,2000);
   G.E[0].x=W/2+45;const smallOutside=!!nearest(0,0,2000);
   G.E=[e];e.x=180;e.y=0;const outsideRange=!!nearest(0,0,50);
   return {rows,smallEdge,smallOutside,outsideRange};
  }''')
  assert all(r['target']==r['visible'] and (r['bullets']>0)==r['visible'] for r in result['rows']),result
  assert result['smallEdge'] and not result['smallOutside'] and not result['outsideRange'],result
  assert not errors,errors
  rows.append({'viewport':[width,height],**result});page.close()
 b.close()
(ARTIFACTS/'visible-target.json').write_text(json.dumps(rows,indent=2))
print('PASS visible boss bounds in four directions/two orientations; offscreen and range exclusions unchanged')

