"""Real loop: nuclear slow motion, white hold, pause/resume and single blast."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844})
 c.add_init_script('window.requestAnimationFrame=()=>0');p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_NUKE_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 initial=p.evaluate('''()=>{LV_IDX=8;META={};start();G.hasMoved=true;DIAG.touch=3;G.P.wep={};G.P.iframe=999;G.bosses=[];
   spawnBoss(buildBosses(CUR())[0]);const hp=G.boss.hp;spawnEnemy('slime',1);G.P.nukeHeld=true;
   window.__blasts=0;SFX.nukeBlast=()=>__blasts++;doNuke();
   window.__motion=[];const realUpdate=update;update=(dt,raw)=>{__motion.push([dt,raw]);realUpdate(dt,raw);};
   return {hp,boss:G.boss.hp,minions:G.E.filter(e=>!e.boss).length,held:G.P.nukeHeld,calm:G.nukeCalm,scale:nukeTimeScale()};}''')
 assert p.evaluate('G.TXT.filter(t=>t.big).length')==1
 assert initial['hp']==initial['boss'] and initial['minions']==0 and not initial['held'] and initial['calm']==2.5 and initial['scale']==.16
 frames=[]
 for target in [.2,.5,.85,1.2,1.65,2.2]:
  row=p.evaluate('''target=>{for(let i=0;i<150&&(G.nukeLaunch?G.nukeLaunch.age:NUKE_FX_END)<target;i++){loop(lastT+1000/60);if(!G.nukeLaunch)break;}
    G.cam.shake=0;draw();const pixel=Array.from(ctx.getImageData(Math.round(W*.73*DPR),Math.round(H*.70*DPR),1,1).data);
    return {target,age:G.nukeLaunch?.age||null,flash:G.nukeFlash,scale:nukeTimeScale(),blasts:__blasts,pixel};}''',target)
  frames.append(row);p.screenshot(path=str(ARTIFACTS/f'nuke57-{target:.2f}.png'))
  if target==.85:
   paused=p.evaluate('''()=>{G.paused=true;const before=JSON.stringify([G.nukeLaunch,G.nukeFlash,G.t]);for(let i=0;i<60;i++)loop(lastT+50);const same=before===JSON.stringify([G.nukeLaunch,G.nukeFlash,G.t]);G.paused=false;return same;}''');assert paused
 assert frames[0]['blasts']==0 and all(x['blasts']==1 for x in frames[1:])
 assert frames[1]['flash']>=1 and frames[2]['flash']>=1 and frames[3]['flash']>.9
 assert min(frames[2]['pixel'][:3])>230,frames
 assert frames[0]['scale']==.16 and .16<frames[3]['scale']<frames[4]['scale']<1
 assert frames[-1]['age'] is None and frames[-1]['flash']==0 and frames[-1]['scale']==1
 motion=p.evaluate('__motion');assert any(abs(dt/raw-.16)<1e-6 for dt,raw in motion if raw>0)
 assert abs(motion[-1][0]/motion[-1][1]-1)<1e-6
 reset=p.evaluate('''()=>{G.P.nukeHeld=true;doNuke();start();return {fx:G.nukeLaunch||null,flash:G.nukeFlash,scale:nukeTimeScale()};}''');assert reset=={'fx':None,'flash':0,'scale':1}
 assert not errors,errors
 (ARTIFACTS/'nuke-cinematic.json').write_text(json.dumps({'initial':initial,'frames':frames,'pause_freezes_effect':paused,'reset':reset,'errors':errors},indent=2));b.close()
print('PASS actual loop slow motion/white hold/recovery/pause/single blast; immediate clear and Boss HP preserved')
