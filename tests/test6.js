const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  const c = await b.newContext({ viewport:{width:390,height:844}, deviceScaleFactor:2, isMobile:true, hasTouch:true });
  const p = await c.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push('PAGEERROR: '+e.message));
  p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE: '+m.text());});
  await p.goto('file:///home/claude/goo-blaster/index.html');
  await p.evaluate(()=>{ PROGRESS=5; renderLevels(); LV_IDX=3; start(); }); await p.waitForTimeout(300);
  const R={};

  // 音效系統存在且可切換
  R.audio = await p.evaluate(()=>{ SFX.unlock();
    const before=SFX.isMuted(); const a=SFX.toggle(); const bk=SFX.toggle();
    SFX.shoot();SFX.kill();SFX.hurt();SFX.level();SFX.evo();SFX.bossIn();SFX.win();SFX.fw();
    return {before,muted:a,back:bk,fnCount:Object.keys(SFX).length}; });

  // 果凍覆蓋率 → 傷害加成
  R.goo = await p.evaluate(()=>{ const a={pct0:gooPct(),bonus0:+gooBonus().toFixed(3)};
    for(let i=0;i<40;i++) addGoo(G.P.x+rnd(-300,300),G.P.y+rnd(-300,300),50,140);
    G.gooArea=0; for(const g of G.GOO) G.gooArea+=Math.PI*g.r*g.r;
    return {...a, pctFull:gooPct(), bonusFull:+gooBonus().toFixed(3), n:G.GOO.length}; });

  // 升級卡：不重複、疊滿會消失、描述會換
  R.cards = await p.evaluate(()=>{
    const seen=new Set(), samples=[];
    for(let i=0;i<40;i++){ for(const u of rollCards()){ seen.add(u.id);
      if(samples.length<6) samples.push({id:u.id,n:u.n,d:u.d,stack:u.stack}); } }
    const P=G.P;
    P.sticky=2; P.freeze=1;                       // 疊滿後應該不再出現
    let stickySeen=false, freezeSeen=false;
    for(let i=0;i<60;i++) for(const u of rollCards()){
      if(u.id==='sticky')stickySeen=true; if(u.id==='freeze')freezeSeen=true; }
    P.sticky=0; P.freeze=0;
    return {distinct:[...seen], samples, maxedStillOffered:{sticky:stickySeen,freeze:freezeSeen}};
  });

  // 遊戲速度隨等級
  R.speed = await p.evaluate(()=>{ const o=[]; const L=G.P.lv;
    for(const lv of [1,5,10,15,20,30]){ G.P.lv=lv; o.push({lv,scale:+speedScale().toFixed(3)}); }
    G.P.lv=L; return o; });

  // 各張卡的機制真的有作用
  R.mech = await p.evaluate(async ()=>{
    const P=G.P, out={};
    // sticky
    G.E.length=0; spawnEnemy('slime',1); P.sticky=1;
    hurtEnemy(G.E[0],1,true); out.sticky={slowT:+(G.E[0].slowT||0).toFixed(2)}; P.sticky=0;
    // freeze
    G.E.length=0; for(let i=0;i<5;i++) spawnEnemy('slime',1);
    G.E.forEach(e=>{e.x=P.x+20;e.y=P.y+20;});
    P.freeze=1; P.dashT=0.01; P.dashDX=1; P.dashDY=0;
    await new Promise(r=>setTimeout(r,120));
    out.freeze={frozen:G.E.filter(e=>e.frozen>0).length,total:G.E.length}; P.freeze=0;
    // shield
    P.shieldN=1; P.hearts=3; P.iframe=0; hurtPlayer();
    out.shield={heartsKept:P.hearts,shieldLeft:P.shieldN};
    // split
    P.split=2; G.B.length=0; G.E.length=0; spawnEnemy('slime',1);
    let got=0; for(let i=0;i<40;i++){ G.B.length=0; G.E.length=0; spawnEnemy('slime',1);
      killEnemy(G.E[0]); if(G.B.length>0)got++; }
    out.split={triggeredOutOf40:got}; P.split=0;
    // greed
    P.greed=2; G.E.length=0; spawnEnemy('slime',1); G.GEM.length=0; killEnemy(G.E[0]);
    out.greed={gemXp:G.GEM[0]&&G.GEM[0].xp}; P.greed=0;
    // magnet
    P.magnet=1; G.GEM.length=0; G.GEM.push({x:P.x+900,y:P.y,vx:0,vy:0,xp:1,hue:1,r:5,wob:0});
    const d0=Math.hypot(G.GEM[0].x-P.x,G.GEM[0].y-P.y);
    await new Promise(r=>setTimeout(r,300));
    out.magnet={before:Math.round(d0),after:G.GEM[0]?Math.round(Math.hypot(G.GEM[0].x-P.x,G.GEM[0].y-P.y)):'collected'};
    P.magnet=0;
    // rage
    P.rage=1; P.hearts=P.maxHearts; const withRage=P.dmg*gooBonus()*1.45;
    out.rage={full:+withRage.toFixed(2)}; P.rage=0;
    return out;
  });

  // XP 曲線
  R.xp = await p.evaluate(()=>{ const o=[]; let tot=0;
    for(let lv=1;lv<=18;lv++){ const n=Math.round(6+lv*5.5+lv*lv*0.5); tot+=n;
      if([1,3,5,8,12,15,18].includes(lv)) o.push({lv,need:n,cum:tot}); } return o; });

  // 花火
  R.fw = await p.evaluate(async ()=>{
    G.FW.length=0; G.fw=true; G.fwT=0; spawnFirework();
    const n0=G.FW.length; await new Promise(r=>setTimeout(r,900));
    return {afterOneBurst:n0, after900ms:G.FW.length, gravityWorks:G.FW.some(x=>x.vy>0)};
  });

  R.errs=errs;
  R.fps = await p.evaluate(()=>new Promise(r=>{let n=0;const t0=performance.now();
    const f=()=>{n++;performance.now()-t0<2000?requestAnimationFrame(f):r(Math.round(n/((performance.now()-t0)/1000)));};requestAnimationFrame(f);}));
  console.log(JSON.stringify(R,null,1));
  await b.close();
})();
