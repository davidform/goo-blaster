"""Rounded render pass: real pixels, bounded cache, no simulation mutation, input smoke."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL)
    context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=2,has_touch=True)
    page=context.new_page()
    page.on('pageerror',lambda e:errors.append(str(e)))
    context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_UI_CPU','1'))})
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    page.click('#btnPlay')
    page.keyboard.down('ArrowRight')
    page.wait_for_function('G.running && G.t>1',timeout=60000)
    page.keyboard.up('ArrowRight')
    page.click('#btnPause')
    proof=page.evaluate('''() => {
      const c=clayBody('#9dc5b1'),x=c.getContext('2d');
      const top=Array.from(x.getImageData(66,42,1,1).data),bottom=Array.from(x.getImageData(84,105,1,1).data);
      const same=c===clayBody('#9dc5b1');
      for(let i=0;i<300;i++)clayBody('hsl('+i+',30%,50%)');
      const bounded=CLAY_CACHE.size<=CLAY_CACHE_MAX;
      const before=JSON.stringify({P:G.P,E:G.E,GEM:G.GEM,GOO:G.GOO,EB:G.EB,META,COINS,PROGRESS});
      const random=Math.random;Math.random=()=>{throw Error('Drawing consumed gameplay RNG');};
      try{for(let i=0;i<3;i++)draw();}finally{Math.random=random;}
      const unchanged=before===JSON.stringify({P:G.P,E:G.E,GEM:G.GEM,GOO:G.GOO,EB:G.EB,META,COINS,PROGRESS});
      return {top,bottom,same,bounded,unchanged,cache:CLAY_CACHE.size};
    }''')
    assert proof['same'] and proof['bounded'] and proof['unchanged'],proof
    assert sum(proof['top'][:3])-sum(proof['bottom'][:3])>80,proof
    # Actual draw paths: normal/frozen/slowed/hit, all boss chapters, invulnerable hero.
    page.evaluate('''()=>{
      G.E=[];G.P.x=0;G.P.y=0;G.cam.x=0;G.cam.y=0;
      for(const [i,type] of ['slime','bunny','drone','bomber'].entries()){
        spawnEnemy(type,1);const e=G.E[G.E.length-1];e.x=(i%2?1:-1)*95;e.y=-135+Math.floor(i/2)*250;
      }
      G.P.iframe=0;G.P.flash=0;G.P.moving=0;G.P.shieldN=0;G.paused=true;draw();
      document.getElementById('pauseOverlay').classList.add('hide');
    }''')
    page.screenshot(path=str(ARTIFACTS/'clay59-game.png'))
    for stage in range(5,51,5):
        page.evaluate('''stage=>{
          LV_IDX=stage-1;G.lvIdx=stage-1;G.L=CUR();G.E=[];
          const cfg=buildBosses(CUR()).find(b=>b.superBoss);spawnBoss(cfg);
          const e=G.boss;e.x=0;e.y=-125;
          for(const state of ['normal','frozen','slowT','flash']){
            e.frozen=e.slowT=e.flash=0;if(state!=='normal')e[state]=1;
            drawBlob(e,true);
          }
          e.frozen=e.slowT=e.flash=0;G.TXT=[];G.cam.shake=0;draw();
        }''',stage)
        if stage in [5,50]:page.screenshot(path=str(ARTIFACTS/f'clay59-boss{stage}.png'))
    page.evaluate('G.P.iframe=2;draw()')
    page.screenshot(path=str(ARTIFACTS/'clay59-invincible.png'))
    assert page.evaluate('CLAY_GROUND.size')<=10
    page.set_viewport_size({'width':844,'height':390})
    page.evaluate('resize();draw()')
    assert page.evaluate('Number.isFinite(G.P.x)&&Number.isFinite(G.P.y)')
    browser.close()
assert not errors,errors
print(json.dumps(proof))
print('PASS rounded bodies: lighting pixels, bounded/reused cache, state/RNG isolation, 10 bosses, statuses, resize and real input')
