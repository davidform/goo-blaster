# -*- coding: utf-8 -*-
"""第三階段：applyLanguage() 就地改寫資料表 + HTML、語言選單、存檔語言偏好。"""
p='/home/claude/work/goo-blaster/index.html'
s=open(p,encoding='utf-8').read()
def rep(old,new,cnt=1,tag=""):
    global s
    assert s.count(old)>=cnt, f"[{tag}] 找不到: {old[:90]!r}"
    s=s.replace(old,new,cnt)

# 1) 資料表的顯示欄位：改寫成 key（applyLanguage 會填入實際文字）
for wid in ['bubble','graffiti','yoyo']:
    pass
rep("  bubble:{name:'泡泡加壓水槍',ic:'💧',hue:190,\n    desc:l=>`高射速直線彈 · 傷害 ${20+l*13}`,",
    "  bubble:{name:'',ic:'💧',hue:190,\n    desc:l=>T('w_bubble_d',20+l*13),",1,"w1")
rep("  graffiti:{name:'七彩塗鴉噴槍',ic:'🎨',hue:300,\n    desc:l=>`扇形散彈 · ${2+l} 發 · 命中留果凍`,",
    "  graffiti:{name:'',ic:'🎨',hue:300,\n    desc:l=>T('w_graffiti_d',2+l),",1,"w2")
rep("  yoyo:{name:'迴旋發光溜溜球',ic:'🪀',hue:55,\n    desc:l=>`環繞拋射 · 貫穿全部敵人`,",
    "  yoyo:{name:'',ic:'🪀',hue:55,\n    desc:l=>T('w_yoyo_d'),",1,"w3")
rep("""const EVOS={
  bubble:{name:'霓虹果凍暴雨',ic:'🌩️',desc:'全螢幕降下果凍雨，敵人減速'},
  graffiti:{name:'彩虹果凍地毯',ic:'🌈',desc:'噴出的果凍會自動延燒連鎖'},
  yoyo:{name:'引力黑洞溜溜球',ic:'🕳️',desc:'吸附雜兵與晶核到中心絞殺'}
};""",
"""const EVOS={
  bubble:{name:'',ic:'🌩️',desc:''},
  graffiti:{name:'',ic:'🌈',desc:''},
  yoyo:{name:'',ic:'🕳️',desc:''}
};""",1,"evos")

# 2) applyLanguage() — 放在 loadSave() 之前
rep("loadSave();",
"""// v0.9.19：把目前語言的文字「就地寫回」所有資料表與 HTML。
// 之所以用就地改寫而不是到處包 T()，是因為顯示這些欄位的程式碼散落在幾十個地方
// （卡片、HUD、商店、戰報、銀河圖…），逐一改動風險高；改寫來源欄位則只有這一個進入點。
function applyLanguage(code){
  if(code) LANG=code;
  // 武器與進化
  const wk={bubble:'w_bubble',graffiti:'w_graffiti',yoyo:'w_yoyo'};
  for(const k in wk) WEAPONS[k].name=T(wk[k]+'_n');
  const ek={bubble:'e_bubble',graffiti:'e_graffiti',yoyo:'e_yoyo'};
  for(const k in ek){ EVOS[k].name=T(ek[k]+'_n'); EVOS[k].desc=T(ek[k]+'_d'); }
  // 升級卡
  for(const u of UPGRADES){
    if(u.w){ u.n=WEAPONS[u.w].name; u.d=WEAPONS[u.w].desc(Math.max(1,(G&&G.P?G.P.wep[u.w]:1))); continue; }
    u.n=T('u_'+u.id+'_n'); u.d=T('u_'+u.id+'_d');
    const k2='u_'+u.id+'_d2';
    if(L10N.en[k2]!==undefined) u.d2=T(k2);
  }
  // 永久強化（描述是「下一級會變成什麼」的函式，數字照算、只換文字）
  const MD={hearts:n=>[n+1,3+n+1], dmg:n=>[(n+1)*10], aspd:n=>[(n+1)*8], wep:n=>[n+1],
            range:n=>[(n+1)*90], xp:n=>[(n+1)*12], pickup:n=>[(n+1)*45],
            dash:n=>[((n+1)*0.35).toFixed(2)], revive:n=>[n+1], coin:n=>[(n+1)*15]};
  for(const m of META_UPGRADES){
    m.n=T('m_'+m.id+'_n');
    const f=MD[m.id];
    m.d=(n)=>T.apply(null,['m_'+m.id+'_d'].concat(f(n)));
  }
  // Boss
  BOSS_POOL.forEach((b,i)=>{ b.name=T('b'+(i+1)); });
  BOSS_CHAPTER.forEach((b,i)=>{ b.name=T('sb'+i); });
  // 寶箱
  for(const c of CHEST_TYPES) c.n=T('c_'+c.id+'_n');
  // 關卡：前 10 關是手寫的，第 11 關之後用樣板組出來
  LEVELS.forEach((L,i)=>{
    if(i<10){ L.n=T('lv'+(i+1)+'n'); L.d=T('lv'+(i+1)+'d'); return; }
    const chName=T('tier'+L.tier);
    if(L.kind==='boss'){
      L.n=T('genBossName',chName,BOSS_CHAPTER[L.bossChapter||0].name);
      L.d=T('genDescBoss',L.ch+1,BOSS_CHAPTER[L.bossChapter||0].name);
    }else{
      L.n=T('genName',chName,L.idxInCh);
      L.d=(L.kind==='opener')?T('genDescOpener',chName):T('genDescMid',chName);
    }
  });
  // HTML 靜態文字
  const setTxt=(id,v)=>{const e=document.getElementById(id); if(e) e.textContent=v;};
  setTxt('btnShopBack',T('back')); setTxt('btnResetCancel',T('cancel'));
  setTxt('btnResetConfirm',T('resetOk')); setTxt('btnReset',T('resetBtn'));
  setTxt('btnResume',T('resume')); setTxt('btnQuitToMenu',T('toMenu'));
  setTxt('btnNext',T('next')); setTxt('btnAgain',T('again'));
  setTxt('btnSave',T('saveShot')); setTxt('btnMenu',T('toMenu'));
  const q=(sel,v)=>{const e=document.querySelector(sel); if(e) e.textContent=v;};
  q('#confirmBox .msg',T('resetQ')); q('#confirmBox .sub2',T('resetSub'));
  q('#pauseOverlay .msg',T('pauseMsg'));
  q('#shop h1',T('shopTitle')); q('#shopHint',T('shopHint'));
  q('#cards .lvtitle',T('cardTitle',1));
  const bs=document.getElementById('btnShop');
  if(bs) bs.innerHTML='🍬 '+T('shop')+' <span id="coinTag">'+Math.round(COINS)+'</span>';
  document.documentElement.lang=LANG;
}
loadSave();""",1,"applyLanguage")

# 3) 存檔加入語言偏好
rep("""      PROGRESS=+o.progress||1; COINS=Math.max(0,+o.coins||0); META=o.meta||{};""",
    """      PROGRESS=+o.progress||1; COINS=Math.max(0,+o.coins||0); META=o.meta||{};
      if(o.lang && L10N[o.lang]) LANG=o.lang;              // 玩家選過的語言優先
      else LANG=detectLang();""",1,"loadLang")
rep("""      if(old){ PROGRESS=+old||1; COINS=0; META={}; saveGame(); }""",
    """      if(old){ PROGRESS=+old||1; COINS=0; META={}; LANG=detectLang(); saveGame(); }
      else LANG=detectLang();""",1,"migrateLang")
rep("""  try{ localStorage.setItem(PROG_KEY, JSON.stringify({progress:PROGRESS, coins:Math.round(COINS), meta:META})); }catch(e){}""",
    """  try{ localStorage.setItem(PROG_KEY, JSON.stringify({progress:PROGRESS, coins:Math.round(COINS), meta:META, lang:LANG})); }catch(e){}""",1,"saveLang")

# 4) 語言選單（主選單按鈕 + 覆蓋層）
rep("""        <button class="btn alt" id="btnShop">🍬 糖果屋 <span id="coinTag">0</span></button>""",
    """        <button class="btn alt" id="btnShop">🍬 <span id="coinTag">0</span></button>
        <button class="btn small" id="btnLang" title="Language">🌐</button>""",1,"btnLang")
rep("""      <div id="confirmBox" class="overlayBox hide">""",
    """      <div id="langBox" class="overlayBox hide">
        <div class="box">
          <div class="ic">🌐</div>
          <div class="msg">Language</div>
          <div id="langList"></div>
        </div>
      </div>
      <div id="confirmBox" class="overlayBox hide">""",1,"langBox")
rep("""  #stageInfo .mt{font-size:11px;color:#7e70ab;margin-top:6px;}""",
    """  #stageInfo .mt{font-size:11px;color:#7e70ab;margin-top:6px;}
  /* v0.9.19：語言選單 */
  #btnLang{padding:10px 12px;font-size:17px;}
  #langList{display:flex;flex-direction:column;gap:6px;max-height:56vh;overflow-y:auto;
     touch-action:pan-y;-webkit-overflow-scrolling:touch;padding:2px;}
  #langList *{touch-action:pan-y;}
  .lrow{border:2px solid #402c78;background:linear-gradient(160deg,#2a1a52,#1b1138);
     border-radius:12px;padding:9px 14px;font-family:inherit;font-weight:900;font-size:14px;
     color:#fff;cursor:pointer;}
  .lrow.on{border-color:#7ef7c0;color:#7ef7c0;}""",1,"langCss")
rep("""document.getElementById('btnShop').onclick=showShop;""",
"""document.getElementById('btnShop').onclick=showShop;
// v0.9.19：語言選單。切換後立刻套用並存檔，不需要重開遊戲。
const langBoxEl=document.getElementById('langBox');
document.getElementById('btnLang').onclick=()=>{
  const list=document.getElementById('langList');
  list.innerHTML='';
  for(const l of LANGS){
    const b=document.createElement('button');
    b.className='lrow'+(l.c===LANG?' on':'');
    b.textContent=l.n;
    b.onclick=()=>{ applyLanguage(l.c); saveGame(); langBoxEl.classList.add('hide');
                    renderStage(); SFX.level(); };
    list.appendChild(b);
  }
  langBoxEl.classList.remove('hide');
};
langBoxEl.onclick=e=>{ if(e.target===langBoxEl) langBoxEl.classList.add('hide'); };""",1,"langMenu")
# showMenu 要收掉語言視窗
rep("""  document.getElementById('confirmBox').classList.add('hide');   // 保險：不要帶著上次沒關掉的確認彈窗回來""",
    """  document.getElementById('confirmBox').classList.add('hide');   // 保險：不要帶著上次沒關掉的確認彈窗回來
  document.getElementById('langBox').classList.add('hide');""",1,"hideLang")
# 啟動時套用語言（renderStage 之前）
rep("""renderStage();

G=newGame(); G.running=false;""",
"""applyLanguage();          // v0.9.19：套用偵測/存檔的語言，再畫主選單
renderStage();

G=newGame(); G.running=false;""",1,"bootApply")

open(p,'w',encoding='utf-8').write(s)
print("第三階段完成")
