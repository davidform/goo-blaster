const { chromium } = require('playwright');

// 一個「小孩等級」的笨 bot：只會朝離自己最近的空曠方向跑，不看彈幕、不追寶箱、
// 升級卡隨機亂點，加速鍵有時候才想到要按。
const DUMB = `
  const cvs=document.getElementById('cv');
  const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
  const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
  let cur=mk(1,195,500); fire('touchstart',[cur],[cur]); let i=0;
  window.__drag=setInterval(()=>{ if(!G||!G.running)return;
    i++;
    const P=G.P; let fx=0,fy=0;
    // 只感知很近的敵人（小孩的反應範圍），完全不看子彈
    for(const e of G.E){const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;
      if(d<170){fx+=dx/d/d*700;fy+=dy/d/d*700;}}
    const cd=Math.hypot(P.x,P.y); if(cd>700){fx-=P.x/cd*5;fy-=P.y/cd*5;}
    if(Math.hypot(fx,fy)<0.05){ const a=i*0.03; fx=Math.cos(a); fy=Math.sin(a); }
    const m=Math.hypot(fx,fy)||1;
    cur=mk(1,195+fx/m*58,500+fy/m*58); fire('touchmove',[cur],[cur]);
    if(i%140===0 && P.dashCD<=0){ const t2=mk(2,BTN.x,BTN.y);
      fire('touchstart',[cur,t2],[t2]); fire('touchend',[cur],[t2]); }
  },33);
  window.__auto=setInterval(()=>{const el=document.getElementById('cards');
    if(el.classList.contains('hide'))return;
    const cs=[...el.querySelectorAll('.card')];
    cs[Math.floor(Math.random()*cs.length)].click();},80);
`;

(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE: '+m.text());});
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.waitForTimeout(400);
  const R={};

  // 選單：應該沒有關卡選擇，只有一顆「開始」
  R.menu = await p.evaluate(()=>({
    hasLevelList: !!document.getElementById('levelList'),
    lvButtons: document.querySelectorAll('.lvbtn').length,
    dots: document.querySelectorAll('.dot').length,
    playText: document.getElementById('btnPlay').textContent,
    resetHidden: document.getElementById('btnReset').classList.contains('hide'),
    info: document.getElementById('stageInfo').innerText.replace(/\n+/g,' | ')
  }));

  // 難度曲線數值：確認鋸齒（新敵種登場那關出怪率相對下降）
  R.curve = await p.evaluate(()=>LEVELS.map((L,i)=>{
    const w=buildWaves(L), bs=buildBosses(L);
    const prev=i>0?LEVELS[i-1]:null;
    const newType = prev ? L.types.filter(t=>!prev.types.includes(t)) : L.types;
    return {i:i+1, tier:L.tier, n:L.n, dur:L.dur, hearts:L.hearts,
      rate:L.rate, hp:L.hp, bossHp:L.bossHp, nboss:L.nboss,
      newType: newType.join(','),
      rateVsPrev: prev? +((L.rate/prev.rate-1)*100).toFixed(0) : null,
      hpVsPrev:   prev? +((L.hp/prev.hp-1)*100).toFixed(0) : null,
      peakRate:+w[w.length-1].rate.toFixed(2), peakHp:+w[w.length-1].mult.toFixed(2),
      bossHps:bs.map(x=>x.hp)};
  }));

  // 笨 bot 連續闖關：從第 1 關一路打，看能撐到第幾關
  const runs=[];
  for(let lv=0; lv<10; lv++){
    await p.evaluate((l)=>{ clearInterval(window.__drag); clearInterval(window.__auto);
      LV_IDX=l; start(); }, lv);
    await p.waitForTimeout(300);
    await p.evaluate(DUMB);
    const dur = await p.evaluate(()=>G.winT);
    let res=null;
    for(let k=0;k<Math.ceil((dur+40)/9);k++){
      await p.waitForTimeout(9000);
      res = await p.evaluate(()=>({t:+G.t.toFixed(0),hearts:G.P.hearts,max:G.P.maxHearts,
        lv:G.P.lv,kills:G.kills,over:G.over,win:G.win}));
      if(res.over) break;
    }
    runs.push({stage:lv+1, ...res});
    if(!res.win) break;          // 笨 bot 打不過就停
  }
  await p.evaluate(()=>{ clearInterval(window.__drag); clearInterval(window.__auto); });
  R.dumbBotRuns=runs;

  // 通關解鎖流程
  R.unlock = await p.evaluate(()=>{
    PROGRESS=1; const seq=[];
    for(let l=0;l<11;l++){
      G={lvIdx:Math.min(l,LEVELS.length-1)};
      if(G.lvIdx+2>PROGRESS){ PROGRESS=Math.min(G.lvIdx+2,LEVELS.length+1); }
      seq.push(PROGRESS);
    }
    const final=PROGRESS; PROGRESS=1;
    return {seq, maxProgress:final, levels:LEVELS.length};
  });

  R.errs=errs;
  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
