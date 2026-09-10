"""Nuke icon: rendered disc centering across sizes/DPR and real touch activation."""
import base64
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

proof=[]
errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL)
    for width,height,dpr in [(320,568,1),(390,844,2),(412,915,3),(844,390,2),(834,1194,2)]:
        context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=dpr,has_touch=True)
        page=context.new_page()
        page.on('pageerror',lambda e:errors.append(str(e)))
        context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))})
        page.goto((Path(GAME_ROOT)/'index.html').as_uri())
        page.click('#btnPlay')
        page.wait_for_function('G.running && G.t>0',timeout=60000)
        page.evaluate('G.P.nukeHeld=true;G.P.iframe=999')
        page.locator('#btnNuke').wait_for(state='visible')
        bounds=page.evaluate('''()=>{
          const n=document.getElementById('btnNuke'),r=n.getBoundingClientRect();
          return {x:r.x,y:r.y,w:r.width,h:r.height,dashTop:BTN.y-BTN.r,label:n.getAttribute('aria-label')};
        }''')
        # Measure actual colored pixels, not the CSS box (emoji boxes can be centered
        # while their ink is not). The disc color excludes the pale button itself.
        png=page.locator('#btnNuke').screenshot()
        (ARTIFACTS/f'nuke60-button-{width}.png').write_bytes(png)
        ink=page.evaluate('''async data=>{
          const image=new Image();image.src='data:image/png;base64,'+data;await image.decode();
          const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
          const ctx=c.getContext('2d');ctx.drawImage(image,0,0);
          const p=ctx.getImageData(0,0,c.width,c.height).data;
          let l=c.width,r=-1,t=c.height,b=-1;
          // Exclude gameplay visible outside the round button's corners.
          for(let y=Math.ceil(c.height*.15);y<c.height*.85;y++)for(let x=Math.ceil(c.width*.15);x<c.width*.85;x++){
            const i=(y*c.width+x)*4;
            if(p[i]>220&&p[i+1]>170&&p[i+1]<215&&p[i+2]<130){l=Math.min(l,x);r=Math.max(r,x);t=Math.min(t,y);b=Math.max(b,y);}
          }
          return {l,r,t,b,w:c.width,h:c.height};
        }''',base64.b64encode(png).decode())
        assert ink['r']>=0,'Radiation disc missing'
        dx=abs((ink['l']+ink['r']+1-ink['w'])/2)/dpr
        dy=abs((ink['t']+ink['b']+1-ink['h'])/2)/dpr
        ratio=(ink['r']-ink['l']+1)/ink['w']
        assert dx<=1 and dy<=1,(width,height,dx,dy,ink,bounds)
        assert .46<ratio<.56,ratio  # Inner disc excludes both the button and disc borders.
        assert bounds['x']>=0 and bounds['y']>=0 and bounds['y']+bounds['h']<bounds['dashTop'],bounds
        assert bounds['label'],bounds
        if width==390:
            page.screenshot(path=str(ARTIFACTS/'nuke60-game.png'))
            (ARTIFACTS/'nuke60-button.png').write_bytes(png)
        page.touchscreen.tap(bounds['x']+bounds['w']/2,bounds['y']+bounds['h']/2)
        page.wait_for_function('!G.P.nukeHeld && G.nukeLaunch',timeout=30000)
        proof.append({'viewport':[width,height],'dpr':dpr,'center_error_css_px':[dx,dy],'disc_ratio':ratio,'touch_launch':True})
        context.close()
    browser.close()
assert not errors,errors
(ARTIFACTS/'nuke60-icon.json').write_text(json.dumps(proof,indent=2))
print('PASS rendered icon centering, size, dash separation, accessible label, actual touch',json.dumps(proof))
