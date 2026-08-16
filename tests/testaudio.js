const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  // 在頁面腳本執行前掛勾，統計實際建立的音源節點
  await p.addInitScript(()=>{
    window.__cnt={osc:0,buf:0};
    const AC=window.AudioContext;
    const oo=AC.prototype.createOscillator, ob=AC.prototype.createBufferSource;
    AC.prototype.createOscillator=function(){ window.__cnt.osc++; return oo.call(this); };
    AC.prototype.createBufferSource=function(){ window.__cnt.buf++; return ob.call(this); };
  });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.evaluate(()=>{ PROGRESS=5; renderLevels(); LV_IDX=3; start(); }); await p.waitForTimeout(400);
  // 暫停遊戲讓只有音樂在跑
  await p.evaluate(()=>{ G.paused=true; });
  const t0 = await p.evaluate(()=>({...window.__cnt}));
  await p.waitForTimeout(4000);
  const t1 = await p.evaluate(()=>({...window.__cnt}));
  const musicOnly = {osc:t1.osc-t0.osc, buf:t1.buf-t0.buf, perSec:+((t1.osc-t0.osc)/4).toFixed(1)};
  // Boss 強度
  await p.evaluate(()=>SFX.musicIntensity(1));
  const t2 = await p.evaluate(()=>({...window.__cnt}));
  await p.waitForTimeout(4000);
  const t3 = await p.evaluate(()=>({...window.__cnt}));
  const boss = {osc:t3.osc-t2.osc, perSec:+((t3.osc-t2.osc)/4).toFixed(1)};
  // 靜音後應停止（musBus 靜音但排程仍跑）→ 改測 musicStop
  await p.evaluate(()=>SFX.musicStop(false));
  await p.waitForTimeout(1200);
  const t4 = await p.evaluate(()=>({...window.__cnt}));
  await p.waitForTimeout(2500);
  const t5 = await p.evaluate(()=>({...window.__cnt}));
  const stopped = {oscAfterStop:t5.osc-t4.osc};
  console.log(JSON.stringify({errs,musicOnly,boss,stopped},null,1));
  await b.close();
})();
