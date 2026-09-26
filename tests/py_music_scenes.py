"""Actual Web Audio and UI routing for combat, garden and village activities."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL
with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL,args=['--autoplay-policy=no-user-gesture-required'])
    c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
    c.set_offline(True)
    c.add_init_script('''const AC=window.AudioContext;window.__voices=0;window.__created=0;
      window.AudioContext=function(){const ac=new AC();window.__ac=ac;
      for(const kind of ['createOscillator','createBufferSource']){const make=ac[kind].bind(ac);ac[kind]=()=>{
        const n=make();__created++;const start=n.start.bind(n);n.start=(...a)=>{__voices++;start(...a);};
        n.addEventListener('ended',()=>__voices--);return n;};}return ac;};''')
    p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_AUDIO_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    p.locator('#navGarden').click()
    assert p.evaluate('SFX.musicDebug().theme')=='garden'
    garden_bpm=p.evaluate('SFX.musicDebug().bpm')
    p.wait_for_function('__created>4',timeout=15000)
    p.locator('#btnHome').click();p.locator('[data-place=picnic]').click()
    scenes=[]
    for theme,name in enumerate(['picnic','pond','starlight']):
        p.locator("#btnHome").click();p.locator('[data-place="'+["picnic","pond","stars"][theme]+'"]').click();p.locator('#festivalStart').click()
        assert p.evaluate('SFX.musicDebug().theme')==name
        scenes.append(p.evaluate('SFX.musicDebug()'))
        before=p.evaluate('__created');p.wait_for_function('n=>__created>n',arg=before,timeout=15000)
        p.locator('#festivalChoose').click()
        assert p.evaluate('SFX.musicDebug().theme')==name
    p.locator('#navAdventure').click();assert p.evaluate('SFX.musicDebug().theme')=='cute'
    p.locator('#btnPlay').click()
    assert p.evaluate('SFX.musicDebug().theme')=='battle'
    assert p.evaluate('SFX.musicDebug().bpm')>garden_bpm
    p.evaluate('G.paused=true;spawnBoss(buildBosses(CUR())[0])')
    assert p.evaluate('SFX.musicDebug().theme')=='boss'
    p.evaluate('G.P.crit=0;hurtEnemy(G.boss,1e9)')
    assert p.evaluate('SFX.musicDebug().theme')=='battle'
    p.evaluate('showMenu();setHubPage("garden")');assert p.evaluate('SFX.musicDebug().theme')=='garden'
    # Repeated navigation must neither grow an unbounded queue nor use gameplay randomness.
    calls=p.evaluate('''()=>{const rand=Math.random;let n=0;Math.random=()=>{n++;return .5;};
      try{for(let i=0;i<30;i++)SFX.musicScene(['garden','picnic','pond','starlight'][i%4]);}
      finally{Math.random=rand;}return n;}''')
    assert calls==0
    p.evaluate('SFX.musicStop(false)');p.wait_for_function('!SFX.isMusicOn()&&__voices===0',timeout=15000)
    p.evaluate('SFX.musicStart("garden");SFX.suspend()');p.wait_for_function('__ac.state==="suspended"')
    p.evaluate('SFX.unlock()');p.wait_for_function('__ac.state==="running"')
    p.evaluate('if(!SFX.isMuted())SFX.toggle();window.__count=__created;SFX.musicScene("pond");window.__t=__ac.currentTime')
    p.wait_for_function('__ac.currentTime>__t+.5',timeout=15000)
    assert p.evaluate('__count===__created&&SFX.isMuted()')
    p.evaluate('SFX.musicStop(false)');p.wait_for_function('!SFX.isMusicOn()&&__voices===0',timeout=15000)
    assert not errors,errors
    (ARTIFACTS/'music73-scenes.json').write_text(json.dumps({'scenes':scenes,'garden_bpm':garden_bpm,'offline':True,'gameplay_rng_calls':calls,'remaining_voices':0,'errors':errors},indent=2),encoding='utf8')
    b.close()
print('PASS actual scene routing, distinct tempos, boss return, rapid switching, cleanup, mute, suspend/resume and offline audio')
