"""Render store artwork using the game's own Canvas hero, not fabricated gameplay.

Run after performance testing. The feature artwork is promotional, while the
settings and town images are actual UI captures from a fresh isolated save.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'store/google-play/assets'
OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'index.html').read_bytes()
with sync_playwright() as pw:
    b=pw.chromium.launch(channel=os.getenv('GOO_BROWSER_CHANNEL','msedge'))
    c=b.new_context(viewport={'width':540,'height':960},device_scale_factor=2,has_touch=True)
    c.set_offline(True)
    p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
    p.goto((ROOT/'index.html').as_uri())
    p.screenshot(path=str(OUT/'town-1080x1920.png'))
    p.locator('#navSettings').tap()
    p.screenshot(path=str(OUT/'settings-1080x1920.png'))
    for kind in ['feature','icon']:
        data=p.evaluate('''kind=>{
          const c=document.createElement('canvas');c.width=kind==='icon'?512:1024;c.height=kind==='icon'?512:500;
          const x=c.getContext('2d',{alpha:false});x.fillStyle='#f4efdf';x.fillRect(0,0,c.width,c.height);
          if(kind==='icon'){
            x.fillStyle='#c5dac4';x.beginPath();x.arc(256,256,235,0,Math.PI*2);x.fill();
            drawSoftHero(x,256,248,185);
          }else{
            x.fillStyle='#dde7c6';x.beginPath();x.ellipse(820,290,245,275,-.4,0,Math.PI*2);x.fill();
            x.fillStyle='#c5dac4';x.beginPath();x.ellipse(825,410,240,66,0,0,Math.PI*2);x.fill();
            x.strokeStyle='#91b9ae';x.lineWidth=5;
            for(const [cx,cy,r] of [[639,142,21],[940,135,26],[966,257,15],[616,339,13]]){
              x.fillStyle='#e5f1e6';x.beginPath();x.arc(cx,cy,r,0,Math.PI*2);x.fill();x.stroke();
              x.fillStyle='#fffdf3';x.beginPath();x.arc(cx-r*.25,cy-r*.25,r*.25,0,Math.PI*2);x.fill();
            }
            drawSoftHero(x,797,272,147);
            x.fillStyle='#3e6052';x.font='900 76px "Arial Black",Arial,sans-serif';
            x.fillText('GOO',64,189);x.fillText('BLASTER',64,274);
            x.font='bold 26px Arial,sans-serif';x.fillText('DODGE. DASH. GROW.',68,341);
            x.font='22px Arial,sans-serif';x.fillStyle='#677762';x.fillText('50 stages • A little garden between battles',68,388);
          }
          return c.toDataURL('image/png').split(',')[1];
        }''',kind)
        (OUT/(kind+('-1024x500.png' if kind=='feature' else '-512x512.png'))).write_bytes(base64.b64decode(data))
    assert not errors,errors
    build=p.evaluate('BUILD');b.close()
assert source==(ROOT/'index.html').read_bytes()
(OUT/'manifest.json').write_text(json.dumps({'build':build,'source_sha256':hashlib.sha256(source).hexdigest(),
 'artwork':'Original Canvas promotional composition with the unchanged in-game drawSoftHero; not a gameplay screenshot.',
 'screenshots':'Fresh save, English, 540x960 @2x, actual town/settings navigation; no injected progress.',
 'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')},'errors':errors},indent=2),encoding='utf-8')
print('PASS Play artwork and actual UI captures generated; visual review required')
