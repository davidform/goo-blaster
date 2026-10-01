"""Victory audio must belong to the result screen, including scheduled voices."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL
with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL,args=['--autoplay-policy=no-user-gesture-required'])
    c=b.new_context(viewport={'width':393,'height':759},has_touch=True)
    c.set_offline(True)
    c.add_init_script('''window.__celebration=false;window.__cv=[];window.__fw=0;
      const AC=window.AudioContext;window.AudioContext=function(){const ac=new AC();window.__ac=ac;
      for(const key of ['createOscillator','createBufferSource']){const make=ac[key].bind(ac);ac[key]=()=>{
        const n=make();if(__celebration){const v={ended:false,disconnected:false};__cv.push(v);
          n.addEventListener('ended',()=>v.ended=true);const d=n.disconnect.bind(n);n.disconnect=(...a)=>{v.disconnected=true;return d(...a);};}
        return n;};}return ac;};''')
    p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_AUDIO_CPU','1'))})
    p.goto((Path(GAME_ROOT)/'index.html').as_uri())
    p.evaluate('''for(const key of ['fw','win']){const f=SFX[key];SFX[key]=function(...a){
      if(key==='fw')__fw++;__celebration=true;try{return f.apply(this,a);}finally{__celebration=false;}};}''')
    def win():
        p.locator('#navAdventure').click();p.locator('#btnPlay').click()
        p.evaluate('endGame(true)')
        p.wait_for_function('__fw>0 && __cv.length>0')
    rows=[]
    for dest in ['#btnMenu','#btnGarden','#btnAgain','#btnNext']:
        p.evaluate('__fw=0;__cv=[]')
        win()
        p.locator(dest).click()
        assert p.evaluate('__cv.every(v=>v.disconnected)&&celebrationTimers.size===0')
        # Sources must be stopped, not only hidden/muted; real Web Audio ended events.
        p.wait_for_function('__cv.every(v=>v.ended&&v.disconnected)',timeout=6000)
        before=p.evaluate('__fw');p.evaluate('window.__until=performance.now()+1100')
        p.wait_for_function('performance.now()>__until')
        state=p.evaluate('({fw:G.fw,particles:G.FW.length,calls:__fw,voices:__cv.length})')
        rows.append({'exit':dest,'new_fireworks_after_exit':state['calls']-before,**state})
        assert state['calls']==before and not state['fw'] and state['particles']==0,rows
        if dest in ['#btnAgain','#btnNext']:p.evaluate('endGame(false);showMenu()')
        for nav in ['#btnHome','#btnShop','#navGarden','#navSettings','#navAdventure']:
            p.locator(nav).click();assert p.evaluate('__fw')==before
        p.locator('#btnHome').click()
        for place in ['picnic','pond','stars']:
            p.locator('[data-place='+place+']').click();p.locator('#festivalStart').click()
            assert p.evaluate('__fw')==before;p.locator('#btnHome').click()
    # Old initial burst callbacks cannot attach to a different, rapidly won run.
    p.evaluate('''start();endGame(true);window.__old=G;showMenu();start();endGame(true);
      window.__new=G;showMenu();window.__at=__fw;window.__until=performance.now()+1100;''')
    p.wait_for_function('performance.now()>__until')
    assert p.evaluate('__fw===__at&&!__old.fw&&!__new.fw&&G.FW.length===0')
    # Win, suspension, leave and resume cannot resurrect scheduled fanfare.
    p.evaluate('start();endGame(true);SFX.suspend();showMenu();SFX.unlock()')
    p.wait_for_function('__ac.state==="running"&&__cv.every(v=>v.ended&&v.disconnected)',timeout=6000)
    p.evaluate('window.__at=__fw;window.__until=performance.now()+1100')
    p.wait_for_function('performance.now()>__until');assert p.evaluate('__fw===__at')
    assert not errors,errors
    (ARTIFACTS/'victory-audio.json').write_text(json.dumps({'rows':rows,'errors':errors,'offline':True,'cpu':os.getenv('GOO_AUDIO_CPU','1')},indent=2))
    b.close()
print('PASS victory exits, real audio source cleanup, all hub/theme pages, fast restart, background/resume, offline')
