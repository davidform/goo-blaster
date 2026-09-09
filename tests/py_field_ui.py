"""Real touch controls, changing insets, and crowded off-screen supplies."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL

with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL)
    page=browser.new_page(viewport={'width':390,'height':844},has_touch=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    page.evaluate('META={};LV_IDX=0;start()')
    checks=[]
    for w,h in [(320,568),(390,844),(844,390),(768,1024)]:
      page.set_viewport_size({'width':w,'height':h})
      for inset in [0,52]:
        page.evaluate('start();G.spawnT=1e9;G.P.iframe=1e9')
        # Simulate a late WebView inset update without a window resize.
        page.locator('#playControls').evaluate('(e,n)=>e.style.top=(n+14)+"px"',inset)
        page.wait_for_function('!document.getElementById("playMute").classList.contains("hide")')
        boxes=[page.locator('#'+x).bounding_box() for x in ['btnPause','playMute']]
        assert boxes[1]['x']-(boxes[0]['x']+boxes[0]['width'])>=11,boxes
        muted=page.evaluate('SFX.isMuted()')
        page.locator('#playMute').tap()
        assert page.evaluate('SFX.isMuted()')!=muted and not page.evaluate('G.paused')
        page.locator('#btnPause').tap()
        assert page.evaluate('G.paused') and page.locator('#pauseOverlay').is_visible()
        page.locator('#btnResume').tap()
        checks.append([w,h,inset,boxes])
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#playControls').evaluate('e=>e.style.top="14px"')
    result=page.evaluate('''()=>{
      start();G.spawnT=1e9;G.P.iframe=1e9;G.CHEST=[];G.cam.x=G.P.x;G.cam.y=G.P.y;
      for(let i=0;i<8;i++)for(let j=0;j<3;j++)G.CHEST.push({x:G.cam.x+Math.cos(i*Math.PI/4)*(1400+j*20),y:G.cam.y+Math.sin(i*Math.PI/4)*(1400+j*20),life:20,wob:0,type:CHEST_TYPES[0]});
      const grouped=chestMarkers();
      G.CHEST.push({x:G.cam.x,y:G.cam.y,life:20,type:CHEST_TYPES[0]});
      const visible=chestMarkers().length;
      return {grouped,visible};}''')
    assert len(result['grouped'])==8 and result['visible']==8
    assert all(m['count']==3 for m in result['grouped'])
    assert len({(m['x'],m['y']) for m in result['grouped']})==8
    page.evaluate('G.CHEST=G.CHEST.filter(c=>Math.hypot(c.x-G.P.x,c.y-G.P.y)>100);document.getElementById("cards").classList.add("hide");G.paused=false;G.nukeCalm=1e9;G.X=[];G.hurt=0;G.bossWarnT=-1;G.t=15;draw()')
    page.screenshot(path=str(ARTIFACTS/'field-ui-v49.png'))
    assert not errors,errors
    (ARTIFACTS/'field-ui.json').write_text(json.dumps({'controls':checks,'markers':result},ensure_ascii=False,indent=2),encoding='utf-8')
    browser.close()
print('PASS: separate actual touch targets at four viewports / two insets; 24 off-screen chests remain represented by eight count badges; on-screen chest excluded')
