const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE: '+m.text());});
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.waitForTimeout(400);
  const R={};

  // 關卡清單 + 鎖定狀態
  R.levels = await p.evaluate(()=>{
    const btns=[...document.querySelectorAll('.lvbtn')];
    return {count:btns.length, progress:PROGRESS,
      locked:btns.map(b=>b.classList.contains('locked')),
      names:LEVELS.map(L=>L.n+'/'+L.diff+'/'+L.dur+'s/♥'+L.hearts+'/boss'+L.nboss)};
  });

  // 各關實際生成出來的波次與 Boss 參數
  R.tuning = await p.evaluate(()=>{
    return LEVELS.map((L,i)=>{
      const w=buildWaves(L), bs=buildBosses(L);
      const first=w[0], last=w[w.length-1];
      return {lv:i+1, n:L.n,
        firstRate:+first.rate.toFixed(2), lastRate:+last.rate.toFixed(2),
        firstHp:+first.mult.toFixed(2), lastHp:+last.mult.toFixed(2),
        types:Object.keys(last.mix),
        bosses:bs.map(b=>b.name+'@'+b.t+'s/'+b.hp+'hp/'+b.kind)};
    });
  });

  // 第 1 關實跑：小朋友難度驗證（bot 用很笨的策略：只會繞圈，不閃彈幕）
  await p.evaluate(()=>{ LV_IDX=0; start(); });
  await p.waitForTimeout(300);
  await p.evaluate(()=>{
    const cvs=document.getElementById('cv');
    const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
    const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
    let cur=mk(1,195,500); fire('touchstart',[cur],[cur]); let i=0;
    window.__drag=setInterval(()=>{ if(!G||!G.running)return;
      i++; const a=i*0.055;                       // 只會繞圈的笨 bot
      cur=mk(1,195+Math.cos(a)*58,500+Math.sin(a)*58); fire('touchmove',[cur],[cur]);
    },33);
    window.__auto=setInterval(()=>{const el=document.getElementById('cards');
      if(el.classList.contains('hide'))return;
      const cs=[...el.querySelectorAll('.card')]; cs[Math.floor(Math.random()*cs.length)].click();},80);
  });
  const trace=[];
  for(let i=0;i<10;i++){
    await p.waitForTimeout(11000);
    const s=await p.evaluate(()=>({t:+G.t.toFixed(0),hearts:G.P.hearts,max:G.P.maxHearts,
      lv:G.P.lv,kills:G.kills,E:G.E.length,chest:G.CHEST.length,chests:G.chests,
      boss:G.boss?G.boss.name+' '+Math.round(G.boss.hp/G.boss.maxhp*100)+'%':null,
      over:G.over,win:G.win}));
    trace.push(s); if(s.over) break;
  }
  R.level1DumbBot=trace;
  R.progressAfter = await p.evaluate(()=>PROGRESS);
  R.nextBtnShown = await p.evaluate(()=>!document.getElementById('btnNext').classList.contains('hide'));

  // 寶箱：生成距離、效果、拾取
  await p.evaluate(()=>{ clearInterval(window.__drag); LV_IDX=3; start(); });
  await p.waitForTimeout(400);
  R.chest = await p.evaluate(async ()=>{
    G.CHEST.length=0; spawnChest();
    const c=G.CHEST[0];
    const dist=Math.round(Math.hypot(c.x-G.P.x,c.y-G.P.y));
    const inArena=Math.hypot(c.x,c.y)<=ARENA;
    // 每種效果都跑一次，確認不會爆
    const results=[];
    for(const t of CHEST_TYPES){
      G.P.hearts=1; G.P.maxHearts=3; G.EB.length=0;
      for(let i=0;i<5;i++) shootE(G.P.x+80,G.P.y,3.14,120,10,8);
      G.E.length=0; for(let i=0;i<6;i++) spawnEnemy('slime',1);
      G.GOO.length=0; for(let i=0;i<5;i++) addGoo(G.P.x+rnd(-100,100),G.P.y+rnd(-100,100),40,140);
      let msg=null,err=null;
      try{ msg=t.go(G.P); }catch(e){ err=e.message; }
      results.push({n:t.n,msg,err});
    }
    return {spawnDist:dist, inArena, results, minRequired:430};
  });
  // 拾取流程
  R.chestPickup = await p.evaluate(async ()=>{
    G.CHEST.length=0; G.chests=0; spawnChest();
    const c=G.CHEST[0];
    G.P.x=c.x; G.P.y=c.y;                    // 直接走到寶箱上
    await new Promise(r=>setTimeout(r,120));
    return {remaining:G.CHEST.length, collected:G.chests};
  });

  R.errs=errs;
  R.fps = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<2500?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
