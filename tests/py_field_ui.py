"""Real touch controls, changing insets, and crowded off-screen supplies."""
import json,os,math
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
    for w,h in [(320,480),(320,568),(390,844),(844,390),(568,320),(768,1024)]:
      page.set_viewport_size({'width':w,'height':h})
      for inset in [0,52]:
        page.evaluate('n=>{start();safeProbe.style.height=n+"px";resize();G.nukeCalm=1e9;G.P.iframe=1e9;G.P.nukeHeld=true;G.hasMoved=true;DIAG.touch=3;drawHUD();}',inset)
        # Simulate a late WebView inset update without a window resize.
        page.locator('#playControls').evaluate('(e,n)=>e.style.top=(n+14)+"px"',inset)
        page.wait_for_function('!document.getElementById("playMute").classList.contains("hide")')
        boxes=[page.locator('#'+x).bounding_box() for x in ['btnPause','playMute']]
        assert boxes[1]['x']-(boxes[0]['x']+boxes[0]['width'])>=11,boxes
        layout=page.evaluate('''()=>{
          G.CHEST=[];
          for(let i=0;i<8;i++)for(let j=0;j<3;j++)G.CHEST.push({x:G.cam.x+Math.cos(i*Math.PI/4)*(1400+j*20),y:G.cam.y+Math.sin(i*Math.PI/4)*(1400+j*20),life:20,wob:0,type:CHEST_TYPES[0]});
          const markers=chestMarkers(),nuke=document.getElementById('btnNuke').getBoundingClientRect().toJSON();G.CHEST=[];
          return {markers,nuke};
        }''')
        for i,m in enumerate(layout['markers']):
          extent=33*m['scale'];r=layout['nuke']
          assert m['x']-extent>=-1 and m['x']+extent<=w+1 and m['y']-extent>=inset and m['y']+extent<=h+1,(w,h,inset,m)
          dx=m['x']-max(r['left'],min(r['right'],m['x']));dy=m['y']-max(r['top'],min(r['bottom'],m['y']))
          assert math.hypot(dx,dy)>=extent,(w,h,inset,m,r)
          for other in layout['markers'][i+1:]:
            assert math.hypot(m['x']-other['x'],m['y']-other['y'])>=33*(m['scale']+other['scale'])-.5,(w,h,inset,m,other)
        muted=page.evaluate('SFX.isMuted()')
        page.locator('#playMute').tap()
        assert page.evaluate('SFX.isMuted()')!=muted and not page.evaluate('G.paused')
        page.locator('#btnPause').tap()
        assert page.evaluate('G.paused') and page.locator('#pauseOverlay').is_visible()
        page.locator('#btnResume').tap()
        checks.append([w,h,inset,boxes])
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#playControls').evaluate('e=>e.style.top="14px"');page.evaluate('safeProbe.style.height="0px";resize()')
    result=page.evaluate('''()=>{
      start();G.nukeCalm=1e9;G.P.iframe=1e9;G.P.nukeHeld=true;G.CHEST=[];G.cam.x=G.P.x;G.cam.y=G.P.y;
      for(let i=0;i<8;i++)for(let j=0;j<3;j++)G.CHEST.push({x:G.cam.x+Math.cos(i*Math.PI/4)*(1400+j*20),y:G.cam.y+Math.sin(i*Math.PI/4)*(1400+j*20),life:20,wob:0,type:CHEST_TYPES[0]});
      const grouped=chestMarkers();
      G.CHEST.push({x:G.cam.x+90,y:G.cam.y+120,life:20,wob:0,type:CHEST_TYPES[0]});
      const visible=chestMarkers().length;
      return {grouped,visible};}''')
    assert len(result['grouped'])==8 and result['visible']==8
    assert all(m['count']==3 for m in result['grouped'])
    assert len({(m['x'],m['y']) for m in result['grouped']})==8
    rare=page.evaluate('''()=>{G.P.nukeHeld=false;G.NUKE={x:G.cam.x+1800,y:G.cam.y};const marks=chestMarkers();G.P.nukeHeld=true;const held=chestMarkers();G.NUKE=null;return {marks,held};}''')
    assert len(rare['marks'])==8 and sum(m['count'] for m in rare['marks'])==25
    assert sum(m['kind']=='nuke' for m in rare['marks'])==1
    assert sum(m['count'] for m in rare['held'])==24
    page.evaluate('G.CHEST=G.CHEST.filter(c=>Math.hypot(c.x-G.P.x,c.y-G.P.y)>300);document.getElementById("cards").classList.add("hide");G.paused=false;G.nukeCalm=1e9;G.X=[];G.P.iframe=0;G.hasMoved=true;DIAG.touch=3;G.hurt=0;G.bossWarnT=-1;G.t=15;draw()')
    page.screenshot(path=str(ARTIFACTS/('field-ui-'+page.evaluate('BUILD')+'.png')))
    assert not errors,errors
    (ARTIFACTS/'field-ui.json').write_text(json.dumps({'controls':checks,'markers':result},ensure_ascii=False,indent=2),encoding='utf-8')
    browser.close()
print('PASS: separate actual touch targets at six viewports / two insets, with held nuke and no marker collisions; 24 off-screen chests remain represented by eight count badges; on-screen chest excluded')
