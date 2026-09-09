"""Real Web Audio routing, gameplay RNG isolation and rapid music transitions."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL,args=['--autoplay-policy=no-user-gesture-required'])
    page=browser.new_page()
    rate=int(os.environ.get('GOO_AUDIO_CPU','1'))
    page.context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':rate})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.add_init_script('''(()=>{
      const AC=window.AudioContext;
      window.__audio={created:0,active:0,peak:0,disconnected:0};
      window.AudioContext=function(...args){
        const c=new AC(...args);window.__ac=c;
        for(const method of ['createOscillator','createBufferSource']){
          const create=c[method].bind(c);
          c[method]=()=>{const source=create();__audio.created++;
            const disconnect=source.disconnect.bind(source);
            source.disconnect=(...a)=>{__audio.disconnected++;return disconnect(...a);};
            const start=source.start.bind(source);
            source.start=(...a)=>{__audio.active++;__audio.peak=Math.max(__audio.peak,__audio.active);return start(...a);};
            source.addEventListener('ended',()=>__audio.active--);return source;};
        }
        return c;
      };
      // Exercise actual audio timers while isolating them from the combat RNG and rAF.
      window.requestAnimationFrame=()=>0;
    })();''')
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    rng=page.evaluate('''()=>{const original=Math.random;let calls=0;
      Math.random=()=>{calls++;return original();};
      try{SFX.unlock();SFX.shoot('bubble');SFX.hit();SFX.crit();SFX.kill();SFX.pickup();SFX.dash();SFX.hurt();}
      finally{Math.random=original;}return calls;}''')
    assert rng==0, f'Audio consumed gameplay RNG {rng} times'
    page.wait_for_function('__ac.currentTime>=.3',polling=50)
    weapons=page.evaluate('''()=>{const result={};for(const w of ['bubble','graffiti','yoyo']){
      const before=__audio.created;SFX.shoot(w);result[w]=__audio.created-before;}return result;}''')
    assert all(n>0 for n in weapons.values()),weapons
    transition=page.evaluate('''()=>{start();const normal=SFX.musicDebug();
      spawnBoss(buildBosses(CUR())[0]);const boss=SFX.musicDebug();
      G.P.crit=0;hurtEnemy(G.boss,1e9);return {normal,boss,after:SFX.musicDebug()};}''')
    assert transition['normal']['theme']=='cute',transition
    assert transition['boss']['theme']=='boss',transition
    assert transition['after']['theme']=='cute',transition
    assert transition['boss']['bpm']>transition['normal']['bpm'],transition
    # A pending fade-out must never stop music started by a subsequent screen/run.
    page.evaluate('SFX.musicStop(true);SFX.musicStart();window.__restartAt=__ac.currentTime')
    page.wait_for_function('__ac.currentTime>__restartAt+1.55',polling=50,timeout=15000)
    assert page.evaluate('SFX.isMusicOn()'), 'Old stop timer stopped new music'
    page.evaluate('SFX.musicStop(false)')
    page.wait_for_function('!SFX.isMusicOn() && __audio.active===0',polling=50,timeout=15000)
    muted=page.evaluate('''()=>{if(!SFX.isMuted())SFX.toggle();const before=__audio.created;
      SFX.shoot('bubble');SFX.shoot('graffiti');SFX.shoot('yoyo');SFX.hurt();
      return {before,after:__audio.created,muted:SFX.isMuted(),active:__audio.active};}''')
    assert muted['muted'] and muted['before']==muted['after'] and muted['active']==0,muted
    page.evaluate('SFX.musicStart();window.__quietAt=__ac.currentTime;window.__quietCount=__audio.created')
    page.wait_for_function('__ac.currentTime>__quietAt+.35',polling=50,timeout=15000)
    assert page.evaluate('__audio.created===__quietCount'), 'Muted music still creates sources'
    page.evaluate('SFX.musicStop(false)')
    page.wait_for_function('!SFX.isMusicOn()',polling=50,timeout=15000)
    nodes=page.evaluate('__audio')
    assert nodes['disconnected']==nodes['created'],nodes
    assert not errors,errors
    result={'build':page.evaluate('BUILD'),'cpu_rate':rate,'gameplay_rng_calls':rng,'weapon_sources':weapons,
            'transitions':transition,'muted':muted,'nodes':nodes,'errors':errors}
    (ARTIFACTS/'audio-quality.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    browser.close()
print(json.dumps(result,indent=2))
print('PASS independent weapon audio, boss transitions, restart, mute and RNG isolation')
