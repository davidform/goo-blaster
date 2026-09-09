"""Bounded fire candy: real update, contact damage, pause/reset and visible trail."""
import sys,os,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
 c.add_init_script('window.requestAnimationFrame=()=>0')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_FIRE_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 p.evaluate('''()=>{window.setupFireTest=()=>{META={};LV_IDX=0;start();G.nukeCalm=1e9;G.winT=1e9;G.bosses=[];G.hasMoved=true;DIAG.touch=3;G.P.wep={bubble:0,graffiti:0,yoyo:0};G.P.crit=0;G.P.iframe=1e9;G.E=[];G.GOO=[];G.P.x=G.P.y=0;};setupFireTest();}''')
 empty=p.evaluate("()=>{const message=CHEST_TYPES.find(t=>t.id==='fire').go(G.P);return {patches:G.FIRE.length,remaining:G.P.fireTrailT,message};}")
 assert empty['patches']==1 and empty['remaining']==6 and '{0}' not in empty['message'],empty
 damage=p.evaluate('''()=>{
   spawnEnemy('slime',1);const e=G.E[0];e.x=e.y=0;e.spd=0;e.hp=e.maxhp=1000;e.shootCD=1e9;
   spawnBoss(buildBosses(LEVELS[4]).find(x=>x.superBoss));const boss=G.boss;boss.x=boss.y=0;boss.spd=0;boss.atkT=1e9;const bh=boss.hp;
   G.FIRE.push({...G.FIRE[0]});
   for(let i=0;i<60;i++)update(1/60,1/60);
   return {damage:1000-e.hp,bossDamage:bh-boss.hp,patches:G.FIRE.length};
 }''')
 assert abs(damage['damage']-24)<1e-6 and damage['bossDamage']==0,damage
 movement=p.evaluate('''()=>{setupFireTest();CHEST_TYPES.find(t=>t.id==='fire').go(G.P);let max=0;for(let i=0;i<210;i++){if(i%15===0)G.P.x+=24;update(1/60,1/60);max=Math.max(max,G.FIRE.length);}G.cam.x=G.P.x;G.cam.y=G.P.y;G.winT=70;G.P.iframe=0;draw();return {max,count:G.FIRE.length,remaining:G.P.fireTrailT,spread:Math.max(...G.FIRE.map(f=>f.x))-Math.min(...G.FIRE.map(f=>f.x))};}''')
 assert movement['count']>=3 and movement['spread']>60 and movement['max']<=16,movement
 p.screenshot(path=str(ARTIFACTS/'fire-trail-v54.png'))
 paused=p.evaluate('''()=>{G.paused=true;const before=JSON.stringify([G.P.fireTrailT,G.FIRE]);loop(lastT+50);const same=before===JSON.stringify([G.P.fireTrailT,G.FIRE]);G.paused=false;return same;}''')
 assert paused
 refresh=p.evaluate('''()=>{CHEST_TYPES.find(t=>t.id==='fire').go(G.P);for(let i=0;i<80;i++){G.P.x=i*50;dropFireCandy();}return {time:G.P.fireTrailT,max:G.FIRE.length};}''')
 assert refresh=={'time':6,'max':16},refresh
 expired=p.evaluate('''()=>{for(let i=0;i<510;i++)update(1/60,1/60);return {time:G.P.fireTrailT,count:G.FIRE.length};}''')
 assert expired=={'time':0,'count':0},expired
 reset=p.evaluate("()=>{CHEST_TYPES.find(t=>t.id==='fire').go(G.P);start();return {time:G.P.fireTrailT,count:G.FIRE.length};}")
 assert reset=={'time':0,'count':0},reset
 # Same weight and level gates; no new XP/candy reward source or permanent rank.
 weights=p.evaluate('({early:CHEST_POOL.length,late:CHEST_POOL_LATE.length,fire:CHEST_W.fire,rank:UPGRADES.some(u=>u.id==="fire")})')
 assert weights=={'early':89,'late':97,'fire':10,'rank':False},weights
 for lang in p.evaluate('Object.keys(L10N)'):
  msg=p.evaluate("lang=>{applyLanguage(lang);return T('c_fire_go',FIRE_CANDY_T);}",lang)
  assert '6' in msg and '{' not in msg,(lang,msg)
 assert not errors,errors
 (ARTIFACTS/'fire-trail.json').write_text(json.dumps({'empty':empty,'damage':damage,'movement':movement,'refresh':refresh,'expired':expired,'reset':reset,'weights':weights},ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
print('PASS empty arena effect, one non-stacking 24 DPS ordinary-enemy trail, Boss immune, six-second refresh/pause/expiry/reset, 16 cap and unchanged pools')
