"""Visible objectives, honest dash ranks, and bounded ground-layer ink."""
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_READ_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 goals=[]
 for lang in p.evaluate('Object.keys(L10N)'):
  p.set_viewport_size({'width':320,'height':568})
  rows=p.evaluate('''lang=>{applyLanguage(lang);PROGRESS=50;return LEVELS.map((_,i)=>{SEL_IDX=i;renderStage();const e=document.querySelector('.storyGoal');return {text:e.textContent,expected:T('storyStep'+(i%5)),fits:e.scrollWidth<=e.clientWidth+1,label:document.querySelector('#storyGoalLabel').textContent,scene:!!document.querySelector('.storyScene svg'),collapsed:!document.querySelector('#stageInfo details').open};});}''',lang)
  assert all(r['text']==r['expected'] and r['fits'] and r['scene'] and r['collapsed'] and r['label']!='storyGoalTitle' for r in rows),lang
  p.locator('#btnPlay').scroll_into_view_if_needed();assert p.locator('#btnPlay').is_visible()
  p.locator('#stageInfo summary').click();assert p.locator('.storyText').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
  p.evaluate('document.querySelector("#stageInfo details").open=false');goals.append(lang)
 p.set_viewport_size({'width':390,'height':844})
 for stage in [8,49]:
  p.evaluate('i=>{applyLanguage("zh-Hant");PROGRESS=50;SEL_IDX=i;renderStage();document.querySelector("#menu").scrollTop=0;}',stage)
  p.wait_for_function('''i=>{const w=document.querySelector('#galaxyWrap'),n=document.querySelectorAll('.gnode')[i];return Math.abs(w.scrollTop-Math.min(w.scrollHeight-w.clientHeight,Math.max(0,n.offsetTop-w.clientHeight/2)))<2;}''',arg=stage)
  p.screenshot(path=str(ARTIFACTS/f'story58-stage{stage+1}.png'))
 c.close();c=b.new_context(viewport={'width':390,'height':844});c.add_init_script('window.requestAnimationFrame=()=>0');p=c.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_READ_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 ranks=p.evaluate('''()=>{applyLanguage('en');const u=META_UPGRADES.find(x=>x.id==='dash');return [0,1,2,3].map(n=>{META={dash:n};LV_IDX=8;start();const before=G.P.dashCDmax;tryDash(1,0);return {n,cooldown:before,iframe:G.P.iframe,description:n?u.d(n-1):'',max:u.max};});}''')
 assert [round(x['cooldown'],2) for x in ranks]==[3,2.65,2.3,1.95],ranks
 assert all(x['iframe']==.42 and x['max']==3 for x in ranks),ranks
 assert all(format(x['cooldown'],'.2f') in x['description'] and '0.42' in x['description'] for x in ranks[1:]),ranks
 repeat=p.evaluate('''()=>{META={dash:3};start();G.bosses=[];G.nukeCalm=999;G.P.wep={};const u=UPGRADES.find(x=>x.id==='cd');u.f(G.P);u.f(G.P);let protectedFrames=0,dashes=0;for(let i=0;i<1800;i++){const before=G.P.dashCD;tryDash(1,0);if(before<=0&&G.P.dashCD>0)dashes++;update(1/60,1/60);if(G.P.iframe>0)protectedFrames++;}return {cooldown:G.P.dashCDmax,ratio:protectedFrames/1800,dashes};}''')
 assert repeat['cooldown']==1.2 and repeat['ratio']<=.36 and 20<=repeat['dashes']<=26,repeat
 p.evaluate('''()=>{showMenu();applyLanguage('zh-Hant');COINS=200;META={dash:1};showShop();}''')
 p.locator('.mrow').filter(has_text='衝刺訓練').scroll_into_view_if_needed()
 p.screenshot(path=str(ARTIFACTS/'dash-shop58.png'))
 ink=p.evaluate('''()=>{showMenu();LV_IDX=8;start();G.paused=true;const bg=[207,216,192];const sample=n=>{G.GOO=Array.from({length:n},()=>({x:0,y:0,r:50,hue:140,life:7.5,max:7.5,burn:0,wob:0}));const before=JSON.stringify(G.GOO);ctx.setTransform(DPR,0,0,DPR,0,0);ctx.fillStyle='rgb('+bg.join(',')+')';ctx.fillRect(0,0,W,H);drawGooGround(W/2,H/2);const px=Array.from(ctx.getImageData(W/2*DPR,H/2*DPR,1,1).data);return {px,unchanged:before===JSON.stringify(G.GOO)};};return {one:sample(1),many:sample(64),bg,size:[gooSurface.width,gooSurface.height,W,H]};}''')
 assert ink['one']['px']==ink['many']['px'] and ink['one']['unchanged'] and ink['many']['unchanged'],ink
 assert max(abs(a-z) for a,z in zip(ink['bg'],ink['many']['px']))<=52,ink
 assert ink['size'][:2]==ink['size'][2:],ink
 p.evaluate('''()=>{G.GOO=Array.from({length:64},(_,i)=>({x:(i%8-4)*28,y:(Math.floor(i/8)-4)*28,r:50,hue:100+i*3,life:7.5,max:7.5,burn:i%11===0?1:0,wob:0}));G.E=[];G.cam={...G.cam,x:0,y:0,shake:0};G.P.x=0;G.P.y=0;G.P.iframe=0;G.hasMoved=true;DIAG.touch=3;draw();}''')
 p.screenshot(path=str(ARTIFACTS/'goo58-dense.png'))
 p.set_viewport_size({'width':640,'height':360});p.evaluate('resize();draw()');assert p.evaluate('gooSurface.width===W&&gooSurface.height===H')
 assert not errors,errors
 (ARTIFACTS/'readability58.json').write_text(json.dumps({'locales':goals,'dash_ranks':ranks,'repeated_dash':repeat,'ink':ink,'errors':errors},indent=2));b.close()
print('PASS 550 visible objectives/11 locales, exact existing dash ranks and 1.2s floor, bounded 64-puddle ink and resize')
