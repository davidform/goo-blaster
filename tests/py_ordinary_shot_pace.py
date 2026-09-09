"""Pin ordinary shot pacing to the v55 baseline; preserve every other spawn/Boss field."""
import json,subprocess,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL,REPO
base=ARTIFACTS/'shot-pace-v55.html';base.write_bytes(subprocess.check_output(['git','show','3244ce3:index.html'],cwd=REPO))
SNAP="""()=>{const out=[];for(let i=0;i<50;i++){LV_IDX=i;META={};start();let seed=117;Math.random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};out.push({boss:buildBosses(CUR()),enemies:Object.keys(ETYPE).map(t=>{spawnEnemy(t,2.1);return {...G.E.at(-1)};})});}return out;}"""
FIRE="""lv=>{LV_IDX=lv-1;META={};start();G.P.iframe=1e9;G.P.wep={bubble:0,graffiti:0,yoyo:0};G.bosses=[];G.nukeCalm=1e9;G.E=[];let seed=117;Math.random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return(seed>>>0)/4294967296;};for(const t of Object.keys(ETYPE)){spawnEnemy(t,1);const e=G.E.at(-1);e.x=250;e.y=0;e.spd=0;}let shots=0;const push=G.EB.push;G.EB.push=function(...xs){shots+=xs.length;return push.apply(this,xs);};for(let i=0;i<1200;i++)update(1/60,1/60);return shots;}"""
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context();c.add_init_script('window.requestAnimationFrame=()=>0');p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_SHOT_CPU','1'))})
 results=[]
 for path in [base,Path(GAME_ROOT)/'index.html']:
  p.goto(path.resolve().as_uri());results.append({'snap':p.evaluate(SNAP),'shots':{lv:p.evaluate(FIRE,lv) for lv in [6,9,20]}})
 before,after=results
 for i,(old,new) in enumerate(zip(before['snap'],after['snap'])):
  assert old['boss']==new['boss'],i
  pace=1+2*(19-i)/13 if 6<=i<19 else 1
  for a,z in zip(old['enemies'],new['enemies']):
   for k in a:
    if k in ['cdMin','cdMax','shootCD']:assert abs(z[k]-a[k]*pace)<1e-8,(i,k,a[k],z[k])
    else:assert a[k]==z[k],(i,k,a[k],z[k])
 assert before['shots'][6]==after['shots'][6] and before['shots'][20]==after['shots'][20]
 assert after['shots'][9]<before['shots'][9]*.7,(before['shots'],after['shots'])
 assert not errors,errors
 proof={'before_shots':before['shots'],'after_shots':after['shots'],'stage9_interval_multiplier':1+22/13,'other_spawn_fields_and_bosses_unchanged':True,'errors':errors}
 (ARTIFACTS/'ordinary-shot-pace.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof));b.close()
print('PASS 200 actual spawns, only ordinary shot timers changed at stages7-19; actual shots counted, Boss/HP/speed/XP preserved')
