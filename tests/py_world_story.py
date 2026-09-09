"""All chapter art, 550 localized scenes, chapter boss silhouettes and launch frames."""
import hashlib,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);p=b.new_page(viewport={'width':390,'height':844})
 errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 p.context.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_WORLD_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 for lang in p.evaluate('Object.keys(L10N)'):
  texts=p.evaluate('lang=>{applyLanguage(lang);return LEVELS.map((_,i)=>stageStory(i));}',lang)
  assert len(set(texts))==50 and all(len(s)>30 for s in texts),(lang,texts)
  assert not any('undefined' in s or 'storyCh' in s for s in texts)
  p.set_viewport_size({'width':320,'height':568})
  p.evaluate('PROGRESS=51;SEL_IDX=49;renderStage()')
  p.locator('#stageInfo summary').click()
  if not p.locator('#stageInfo details').evaluate('e=>e.open'):p.locator('#stageInfo summary').click()
  assert p.locator('.storyText').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),lang
  p.locator('#btnPlay').scroll_into_view_if_needed()
  assert p.locator('#btnPlay').is_visible()
 p.set_viewport_size({'width':390,'height':844})
 p.evaluate("applyLanguage('zh-Hant');PROGRESS=50")
 for i in [0,14,24,49]:
  p.evaluate('i=>{SEL_IDX=i;showMenu();SEL_IDX=i;renderStage();document.querySelector("#stageInfo details").open=true;}',i)
  p.wait_for_function('''i=>{const w=document.querySelector('#galaxyWrap'),n=document.querySelectorAll('.gnode')[i];return Math.abs(w.scrollTop-Math.min(w.scrollHeight-w.clientHeight,Math.max(0,n.offsetTop-w.clientHeight/2)))<2;}''',arg=i)
  p.locator('#galaxyWrap').scroll_into_view_if_needed()
  p.screenshot(path=str(ARTIFACTS/f'world-stage-{i+1}.png'))
  p.locator('#stageInfo').screenshot(path=str(ARTIFACTS/f'story-stage-{i+1}.png'))
 scenes=p.evaluate('CHAPTER_WORLD.map((_,i)=>chapterScene(i))');assert len(set(scenes))==10
 art=b.new_page(viewport={'width':300,'height':180})
 for chapter,scene in enumerate(scenes):
  art.set_content('<style>html,body{margin:0}svg{display:block;width:300px;height:180px}</style>'+scene)
  art.screenshot(path=str(ARTIFACTS/f'world-scene-{chapter+1}.png'))
 art.close()
 # Freeze the RAF only in a new test context; paint the real rendering functions.
 c=b.new_context(viewport={'width':240,'height':240});c.add_init_script('window.requestAnimationFrame=()=>0')
 q=c.new_page();q.on('pageerror',lambda e:errors.append(str(e)));q.goto((Path(GAME_ROOT)/'index.html').as_uri())
 specs=[];hashes=[]
 for lv in range(5,51,5):
  spec=q.evaluate('''lv=>{
   LV_IDX=lv-1;META={};start();G.t=1;G.hasMoved=true;DIAG.touch=3;
   const cfg=buildBosses(CUR()).find(b=>b.superBoss);spawnBoss(cfg);const e=G.boss;
   const actual={lv,name:e.name,skin:e.skin,chapter:e.chIdx,hp:e.hp,r:e.r};
   e.x=120;e.y=133;e.r=42;e.wob=0;G.cam.shake=0;
   ctx.fillStyle=CHAPTER_WORLD[worldChapter(lv-1)].ground;ctx.fillRect(0,0,W,H);drawBlob(e,true);
   document.getElementById('btnPause').classList.add('hide');return actual;
  }''',lv)
  shot=q.screenshot(path=str(ARTIFACTS/f'boss-world-{lv}.png'))
  hashes.append(hashlib.sha256(shot).hexdigest());specs.append(spec)
 assert len(set(hashes))==10 and len({tuple(s['skin']) for s in specs})==10
 assert [s['chapter'] for s in specs]==list(range(10))
 q.set_viewport_size({'width':390,'height':844})
 nuke=q.evaluate('''()=>{
   resize();LV_IDX=49;start();G.hasMoved=true;DIAG.touch=3;G.E=[];G.P.nukeHeld=true;
   window.__blasts=0;SFX.nukeBlast=()=>window.__blasts++;
   spawnEnemy('slime',1);spawnBoss(buildBosses(CUR()).find(x=>x.superBoss));const hp=G.boss.hp;
   G.TXT=[];doNuke();return {held:G.P.nukeHeld,age:G.nukeLaunch.age,calm:G.nukeCalm,regular:G.E.filter(e=>!e.boss).length,bossHP:G.boss.hp,before:hp};
 }''')
 assert nuke=={'held':False,'age':0,'calm':2.5,'regular':0,'bossHP':nuke['before'],'before':nuke['before']},nuke
 assert q.evaluate('__blasts')==0
 assert q.evaluate('()=>{for(let i=0;i<10;i++)loop(lastT+50);return __blasts;}')==1
 frames=[]
 for age in [0,.20,.40,.60,1.20]:
  q.evaluate('age=>{G.nukeLaunch.age=age;G.nukeFlash=age<.9?1.5:Math.max(0,1.5*(1-(age-.9)/.9));G.cam.shake=0;draw();}',age)
  shot=q.screenshot(path=str(ARTIFACTS/f'nuke-launch-{age:.2f}.png'));frames.append(hashlib.sha256(shot).hexdigest())
 assert len(set(frames))==5
 q.evaluate('G.nukeLaunch.age=NUKE_FX_END-.01;loop(lastT+50)')
 assert q.evaluate('G.nukeLaunch===null')
 assert q.evaluate('__blasts')==1
 assert not errors,errors
 (ARTIFACTS/'world-story.json').write_text(json.dumps({'locales':11,'unique_scenes_per_locale':50,'bosses':specs,'nuke':nuke,'frames':frames},ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
print('PASS 550 localized stage stories, 10 distinct chapter scenes and actual boss portraits, PNG launch timeline; immediate clear/calm/Boss HP preserved')
