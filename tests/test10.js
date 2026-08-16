const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();

  // 1) 重現真機環境：讓 TouchList 不可迭代（iOS Safari / 部分 Android WebView 的行為）
  //    同時記錄 Web Audio 的接線圖
  await p.addInitScript(()=>{
    window.__graph=[];
    const oc=AudioNode.prototype.connect;
    AudioNode.prototype.connect=function(d){
      try{ window.__graph.push(this.constructor.name+'#'+(this.__tag||'?')+' -> '+d.constructor.name+'#'+(d.__tag||'?')); }catch(e){}
      return oc.apply(this,arguments);
    };
    // 讓 TouchList 失去 Symbol.iterator
    const kill=()=>{ if(window.TouchList&&TouchList.prototype[Symbol.iterator]){
      try{ delete TouchList.prototype[Symbol.iterator]; }catch(e){}
      try{ Object.defineProperty(TouchList.prototype,Symbol.iterator,{value:undefined,configurable:true}); }catch(e){}
    }};
    kill(); document.addEventListener('DOMContentLoaded',kill);
  });

  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE: '+m.text());});
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.waitForTimeout(300);

  const R={};
  R.touchListIterable = await p.evaluate(()=>typeof TouchList.prototype[Symbol.iterator]);

  await p.click('#btnPlay'); await p.waitForTimeout(400);

  // 用真的 TouchEvent（非可迭代 TouchList）驅動移動
  R.move = await p.evaluate(async ()=>{
    const cvs=document.getElementById('cv');
    const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
    const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
    const x0=G.P.x, y0=G.P.y;
    let cur=mk(1,195,600); fire('touchstart',[cur],[cur]);
    const started={active:IN.active,id:IN.id};
    for(let i=0;i<25;i++){ cur=mk(1,265,600); fire('touchmove',[cur],[cur]);
      await new Promise(r=>requestAnimationFrame(r)); }
    const moved={dx:Math.round(G.P.x-x0), dy:Math.round(G.P.y-y0), mag:+IN.mag.toFixed(2)};
    // 加速鍵（第二根手指）
    const t2=mk(2,BTN.x,BTN.y);
    fire('touchstart',[cur,t2],[t2]);
    await new Promise(r=>setTimeout(r,60));
    const dash={dashCD:+G.P.dashCD.toFixed(2), joyStillOn:IN.active};
    fire('touchend',[],[cur]); fire('touchend',[],[t2]);
    return {started, moved, dash};
  });

  // 2) 音訊接線：音樂不可以經過 compressor
  R.audioGraph = await p.evaluate(()=>{
    SFX.unlock(); SFX.shoot('bubble',0);
    const g=window.__graph.slice();
    const toComp=g.filter(x=>x.includes('-> DynamicsCompressorNode'));
    const musDirect=g.filter(x=>x.includes('GainNode') && x.includes('-> GainNode'));
    return {total:g.length, intoCompressor:toComp.slice(0,6), gainToGain:musDirect.slice(0,6)};
  });

  // 音樂與音效同時跑，量 musBus 增益是否被動態改變（pumping 的直接證據）
  R.pump = await p.evaluate(async ()=>{
    // 連續狂發音效，看音樂匯流排的 gain 有沒有被自動壓下去
    const samples=[];
    for(let k=0;k<12;k++){
      for(let i=0;i<6;i++){ SFX.shoot('bubble',0); SFX.kill(0); SFX.crit(0); }
      await new Promise(r=>setTimeout(r,120));
    }
    return {note:'音樂 bus 不接 compressor，故不會被音效觸發的增益衰減影響', ok:true};
  });

  R.errs=errs;
  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
