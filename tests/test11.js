const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const R={};

  // ── A. 關卡順序：舊版存檔殘留不可以害玩家跳關 ──
  {
    const c = await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    const p = await c.newPage();
    // 模擬「玩過舊的 5 關版」留下的存檔
    await p.addInitScript(()=>{ try{ localStorage.setItem('gooblaster_progress','5'); }catch(e){} });
    await p.goto('file:///home/claude/goo-blaster/index.html');
    await p.waitForTimeout(400);
    R.staleSave = await p.evaluate(()=>({
      progress:PROGRESS,
      playBtn:document.getElementById('btnPlay').textContent,
      oldKeyCleared: (()=>{try{return localStorage.getItem('gooblaster_progress')===null}catch(e){return 'n/a'}})(),
      newKey:(()=>{try{return localStorage.getItem(PROG_KEY)}catch(e){return 'n/a'}})()
    }));
    await c.close();
  }

  // ── B. 循序解鎖：連過三關，進度必須是 1→2→3→4，且不能跳 ──
  {
    const c = await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    const p = await c.newPage();
    await p.goto('file:///home/claude/goo-blaster/index.html');
    await p.waitForTimeout(300);
    R.sequential = await p.evaluate(()=>{
      const seq=[{start:PROGRESS}];
      for(let k=0;k<4;k++){
        LV_IDX=Math.min(PROGRESS-1,LEVELS.length-1);
        start();                                   // 開始目前這關
        const played=LV_IDX+1;
        G.over=false; endGame(true);               // 通關
        seq.push({played, progressAfter:PROGRESS, stageShown:Math.min(PROGRESS,LEVELS.length)});
      }
      return seq;
    });
    // endGame 重複呼叫不能重複推進
    R.doubleEnd = await p.evaluate(()=>{
      LV_IDX=0; start(); const before=PROGRESS;
      G.over=false; endGame(true);
      const after1=PROGRESS;
      endGame(true); endGame(true);                 // 再叫兩次
      return {before, after1, after3:PROGRESS};
    });
    // 從第 1 關重來
    R.reset = await p.evaluate(()=>{
      document.getElementById('btnReset').click();
      return {progress:PROGRESS, btn:document.getElementById('btnPlay').textContent};
    });
    await c.close();
  }

  // ── C. 觸控：模擬「touchend 被吞掉」的情境，看搖桿會不會卡死 ──
  {
    const c = await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});
    const p = await c.newPage();
    const errs=[]; p.on('pageerror',e=>errs.push(e.message));
    await p.goto('file:///home/claude/goo-blaster/index.html');
    await p.waitForTimeout(300);
    await p.click('#btnPlay'); await p.waitForTimeout(300);
    R.touchRecovery = await p.evaluate(async ()=>{
      const cvs=document.getElementById('cv');
      const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
      const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
      const out={};
      // 第一次滑動：正常
      let a=mk(7,195,600); fire('touchstart',[a],[a]);
      for(let i=0;i<15;i++){ a=mk(7,265,600); fire('touchmove',[a],[a]);
        await new Promise(r=>requestAnimationFrame(r)); }
      const x1=G.P.x;
      out.firstDrag={moved:Math.round(x1), active:IN.active, mag:+IN.mag.toFixed(2)};

      // 模擬瀏覽器「吞掉 touchend」：直接用一個全新的 identifier 重新開始，
      // 舊版會因為 IN.id 還卡在 7 而完全動不了
      let b2=mk(99,195,600); fire('touchstart',[b2],[b2]);
      for(let i=0;i<15;i++){ b2=mk(99,195,530); fire('touchmove',[b2],[b2]);
        await new Promise(r=>requestAnimationFrame(r)); }
      out.afterLostTouchEnd={dy:Math.round(G.P.y), active:IN.active, mag:+IN.mag.toFixed(2), joyId:IN.id};

      // 全部放開
      fire('touchend',[],[b2]);
      out.released={active:IN.active};
      out.diag={touch:DIAG.touch,tmove:DIAG.tmove,tend:DIAG.tend,err:DIAG.err};
      return out;
    });
    // 兩根手指：搖桿 + 加速鍵
    R.twoFinger = await p.evaluate(async ()=>{
      const cvs=document.getElementById('cv');
      const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
      const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
      G.P.dashCD=0;
      let j=mk(1,150,500); fire('touchstart',[j],[j]);
      j=mk(1,210,500); fire('touchmove',[j],[j]);
      await new Promise(r=>setTimeout(r,80));
      const t2=mk(2,BTN.x,BTN.y);
      fire('touchstart',[j,t2],[t2]);
      await new Promise(r=>setTimeout(r,60));
      const r1={dashCD:+G.P.dashCD.toFixed(2), joyActive:IN.active, mag:+IN.mag.toFixed(2)};
      fire('touchend',[j],[t2]);                  // 只放開加速鍵那根
      await new Promise(r=>setTimeout(r,60));
      const r2={joyActive:IN.active, mag:+IN.mag.toFixed(2)};
      fire('touchend',[],[j]);
      return {pressed:r1, afterBtnRelease:r2, allReleased:!IN.active};
    });
    R.errs=errs;
    await c.close();
  }

  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
