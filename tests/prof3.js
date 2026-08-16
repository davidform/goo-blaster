const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  await p.goto('file:///home/claude/goo-blaster/index.html');
  const gpu = await p.evaluate(()=>{
    const cv=document.createElement('canvas');
    const gl=cv.getContext('webgl')||cv.getContext('experimental-webgl');
    if(!gl) return 'no webgl';
    const d=gl.getExtension('WEBGL_debug_renderer_info');
    return d? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'no debug info';
  });
  await p.evaluate(()=>{ PROGRESS=5; renderLevels(); LV_IDX=3; start(); });
  // 快轉到最終 Boss 狂暴階段（真實遊戲中最重的一刻）
  await p.evaluate(()=>{ window.__a=setInterval(()=>{const x=document.querySelector('#cards .card');
    if(x&&!document.getElementById('cards').classList.contains('hide'))x.click();},60); });
  await p.evaluate(()=>{ G.t=149; G.bossDone=[true,true,false]; G.P.lv=15;
    G.P.wep={bubble:5,graffiti:5,yoyo:5}; G.P.evo={bubble:1,graffiti:1,yoyo:1}; G.P.hearts=99; G.P.maxHearts=99; });
  await p.waitForTimeout(9000);
  await p.evaluate(()=>{ const bs=G.E.find(e=>e.kind==='final'); if(bs) bs.hp=bs.maxhp*0.35; });
  await p.waitForTimeout(3000);
  const peak = await p.evaluate(()=>({E:G.E.length,EB:G.EB.length,B:G.B.length,GOO:G.GOO.length,PT:G.PT.length,
    boss:G.boss?Math.round(G.boss.hp/G.boss.maxhp*100)+'%':null}));
  const fps = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<3000?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  await p.screenshot({path:'/home/claude/shots/peak.png'});
  console.log(JSON.stringify({gpu,peak,fpsAtPeak:fps}));
  await b.close();
})();
