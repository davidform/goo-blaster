const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE: '+m.text());});
  await p.goto('file:///home/claude/goo/game/index.html');
  await p.evaluate(()=>{ PROGRESS=5; renderStage(); LV_IDX=3; start(); }); await p.waitForTimeout(300);

  const R={};

  // --- 1. 多點觸控：搖桿(id1) + 加速鍵(id2) 同時 ---
  R.multitouch = await p.evaluate(async ()=>{
    const cvs=document.getElementById('cv');
    const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
    const fire=(type,touches,changed)=>cvs.dispatchEvent(
      new TouchEvent(type,{touches,changedTouches:changed,bubbles:true,cancelable:true}));
    const t1=mk(1,150,500);
    fire('touchstart',[t1],[t1]);
    const t1b=mk(1,205,500);
    fire('touchmove',[t1b],[t1b]);
    await new Promise(r=>setTimeout(r,120));
    const before={joyActive:IN.active,joyId:IN.id,mag:+IN.mag.toFixed(2),dashCD:+G.P.dashCD.toFixed(2)};
    // 第二根手指按加速鍵
    const t2=mk(2,BTN.x,BTN.y);
    fire('touchstart',[t1b,t2],[t2]);
    await new Promise(r=>setTimeout(r,60));
    const after={joyActive:IN.active,joyId:IN.id,mag:+IN.mag.toFixed(2),
                 dashCD:+G.P.dashCD.toFixed(2),dashT:+G.P.dashT.toFixed(2),iframe:+G.P.iframe.toFixed(2)};
    // 放開加速鍵那根，搖桿應保持
    fire('touchend',[t1b],[t2]);
    await new Promise(r=>setTimeout(r,60));
    const afterUp={joyActive:IN.active,mag:+IN.mag.toFixed(2)};
    fire('touchend',[],[t1b]);
    await new Promise(r=>setTimeout(r,60));
    return {before,after,afterUp,joyReleased:!IN.active};
  });

  // --- 2. 冷卻時間 ---
  R.cooldown = await p.evaluate(async ()=>{
    G.P.dashCD=0; const cvs=document.getElementById('cv');
    const t=new Touch({identifier:9,target:cvs,clientX:BTN.x,clientY:BTN.y});
    cvs.dispatchEvent(new TouchEvent('touchstart',{touches:[t],changedTouches:[t],bubbles:true,cancelable:true}));
    cvs.dispatchEvent(new TouchEvent('touchend',{touches:[],changedTouches:[t],bubbles:true,cancelable:true}));
    await new Promise(r=>setTimeout(r,50));
    const justAfter=+G.P.dashCD.toFixed(2);
    // 冷卻中再按應無效
    cvs.dispatchEvent(new TouchEvent('touchstart',{touches:[t],changedTouches:[t],bubbles:true,cancelable:true}));
    cvs.dispatchEvent(new TouchEvent('touchend',{touches:[],changedTouches:[t],bubbles:true,cancelable:true}));
    await new Promise(r=>setTimeout(r,50));
    return {max:G.P.dashCDmax, justAfter, blockedStillCD:+G.P.dashCD.toFixed(2)};
  });

  // --- 3. 愛心扣減與死亡 ---
  R.hearts = await p.evaluate(async ()=>{
    const seq=[]; const P=G.P;
    P.hearts=3; P.maxHearts=3; G.over=false; G.running=true;
    for(let i=0;i<4;i++){
      P.iframe=0; hurtPlayer();
      seq.push({hearts:P.hearts,over:G.over,hurt:+G.hurt.toFixed(2),iframe:+P.iframe.toFixed(2)});
      await new Promise(r=>setTimeout(r,30));
    }
    return {seq, shown:!document.getElementById('over').classList.contains('hide'),
            title:document.getElementById('overTitle').textContent};
  });

  // --- 4. 慈悲無敵：連續碰撞只扣一顆 ---
  await p.waitForTimeout(700); await p.click('#btnAgain'); await p.waitForTimeout(300);
  R.mercy = await p.evaluate(async ()=>{
    const P=G.P; P.hearts=3; P.iframe=0;
    let n=0; for(let i=0;i<12;i++){ if(hurtPlayer())break; n++; }  // 同一瞬間連打 12 次
    return {heartsAfterBurst:P.hearts, iframe:+P.iframe.toFixed(2)};
  });

  // --- 5. 實戰：會用加速鍵的 bot ---（承接上一局，重設狀態即可）
  await p.evaluate(()=>{ G.P.hearts=G.P.maxHearts; G.P.iframe=0; G.t=0;
    G.E.length=0; G.EB.length=0; G.kills=0; G.bossDone=[false,false,false]; G.boss=null; });
  await p.waitForTimeout(200);
  await p.evaluate(()=>{
    const cvs=document.getElementById('cv');
    const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
    const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
    let cur=mk(1,195,500); fire('touchstart',[cur],[cur]);
    window.__drag=setInterval(()=>{ if(!G||!G.running)return;
      const P=G.P; let fx=0,fy=0,danger=0;
      for(const e of G.E){const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;
        if(d<300){const w=e.boss?3000:1100; fx+=dx/d/d*w; fy+=dy/d/d*w; if(d<95)danger++;}}
      for(const eb of G.EB){const dx=P.x-eb.x,dy=P.y-eb.y,d=Math.hypot(dx,dy)||1;
        if(d<160){fx+=dx/d/d*2200;fy+=dy/d/d*2200; if(d<70)danger++;}}
      const cd=Math.hypot(P.x,P.y); if(cd>740){fx-=P.x/cd*8;fy-=P.y/cd*8;}
      const m=Math.hypot(fx,fy)||1;
      cur=mk(1,195+fx/m*58,500+fy/m*58); fire('touchmove',[cur],[cur]);
      if(danger>=2&&P.dashCD<=0){                      // 危險時按加速鍵脫離
        const t2=mk(2,BTN.x,BTN.y);
        fire('touchstart',[cur,t2],[t2]); fire('touchend',[cur],[t2]);
      }
    },33);
    window.__auto=setInterval(()=>{const el=document.getElementById('cards');
      if(el.classList.contains('hide'))return;
      const cs=[...el.querySelectorAll('.card')]; let best=cs[0],bs=-1;
      for(const x of cs){const n=x.querySelector('.nm').textContent; let s=1;
        if(/水槍|噴槍|溜溜球|暴雨|地毯|黑洞/.test(n))s=4;
        else if(/活力粉紅|軟糖再生|甜甜圈|急救/.test(n))s=3;
        else if(/黏性|連鎖|腐蝕|暴走|分裂|滿心/.test(n))s=2;
        if(s>bs){bs=s;best=x;}} best.click();},70);
  });
  const runs=[];
  for(let i=0;i<7;i++){
    await p.waitForTimeout(26000);
    const s=await p.evaluate(()=>({t:+G.t.toFixed(0),hearts:G.P.hearts,max:G.P.maxHearts,
      lv:G.P.lv,kills:G.kills,E:G.E.length,boss:G.boss?G.boss.name:null,over:G.over,win:G.win}));
    runs.push(s); if(s.over) break;
  }
  R.run=runs;
  R.fpsPlay = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<2500?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  await p.evaluate(()=>{ G.running=false; G.over=false; endGame(true); });
  await p.waitForTimeout(1500);
  R.fpsWin = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<2500?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  R.fwCount = await p.evaluate(()=>G.FW.length);
  R.fps = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<2500?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  R.errs=errs;
  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
