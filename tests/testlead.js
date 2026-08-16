const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.evaluate(()=>{ PROGRESS=5; renderLevels(); LV_IDX=3; start(); }); await p.waitForTimeout(300);
  const r = await p.evaluate(async ()=>{
    const cvs=document.getElementById('cv');
    const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
    const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
    let cur=mk(1,195,600); fire('touchstart',[cur],[cur]);
    const ramp=[];
    // 往右移動 1 秒
    for(let i=0;i<30;i++){ cur=mk(1,265,600); fire('touchmove',[cur],[cur]);
      await new Promise(r=>requestAnimationFrame(r));
      if(i%5===0) ramp.push(+(G.P.leadX||0).toFixed(1)); }
    const rightMax=+(G.P.leadX||0).toFixed(1);
    // 突然反向：舊版會瞬間甩鏡頭，新版應平滑過渡
    const flip=[];
    for(let i=0;i<30;i++){ cur=mk(1,125,600); fire('touchmove',[cur],[cur]);
      await new Promise(r=>requestAnimationFrame(r));
      flip.push(+(G.P.leadX||0).toFixed(1)); }
    // 相鄰兩幀最大跳動量（越小越不暈）
    let maxJump=0; for(let i=1;i<flip.length;i++) maxJump=Math.max(maxJump,Math.abs(flip[i]-flip[i-1]));
    return {ramp, rightMax, flipStart:flip[0], flipEnd:flip[flip.length-1],
            maxFrameJump:+maxJump.toFixed(2), leadCap:52};
  });
  console.log(JSON.stringify({errs,...r},null,1));
  await b.close();
})();
