# -*- coding: utf-8 -*-
"""第二階段：把 tier 改成數字索引、資料表改由 applyLanguage() 就地改寫、
   所有顯示點改走 T()。每一處都用 assert 確認。"""
p='/home/claude/work/goo-blaster/index.html'
s=open(p,encoding='utf-8').read()
def rep(old,new,cnt=1,tag=""):
    global s
    n=s.count(old)
    assert n>=cnt, f"[{tag}] 找不到: {old[:90]!r}"
    s=s.replace(old,new,cnt)

# ── A. tier 改成數字索引 ──────────────────────────────────────
tiers=['新手','上手','熟練','挑戰','地獄']
for i,t in enumerate(tiers):
    rep(f"{{tier:'{t}', ", f"{{tier:{i}, ", 2, f"tier{t}")   # 每個 tier 剛好 2 關

rep("""const TIERS=['新手','上手','熟練','挑戰','地獄','深淵','噩夢','煉獄','虛無','修羅','冥界','天啟','神魔','終焉'];
const TIER_COLOR={'新手':'#7ef7c0','上手':'#8fe8ff','熟練':'#ffd23f','挑戰':'#ff9a4f','地獄':'#ff5b7f',
  '深淵':'#c04fff','噩夢':'#9a3fff','煉獄':'#ff5a3c','虛無':'#5a6cff','修羅':'#ff2f6b',
  '冥界':'#3fd0ff','天啟':'#ffe14f','神魔':'#ff8a00','終焉':'#ff1a1a'};""",
"""// v0.9.19：難度層級改用「數字索引」而不是中文字串。
// 原因：L.tier 同時被拿來當 TIER_COLOR 的查表鍵，一旦翻譯成別的語言，查表就會壞掉。
// 現在 tier 是 0~13 的索引，顏色查陣列、顯示名稱走 T('tier'+i)，兩者徹底分離。
const TIER_COLOR=['#7ef7c0','#8fe8ff','#ffd23f','#ff9a4f','#ff5b7f',
  '#c04fff','#9a3fff','#ff5a3c','#5a6cff','#ff2f6b',
  '#3fd0ff','#ffe14f','#ff8a00','#ff1a1a'];
const tierName=i=>T('tier'+i);""", 1, "TIER_COLOR")

# genExtraLevels 的 tier / 名稱 / 描述改成語言無關（顯示欄位交給 applyLanguage）
rep("""  const CH_NAMES=['深淵','噩夢','煉獄','虛無','修羅','冥界','天啟','神魔','終焉'];
  const base=LEVELS[9];""",
"""  const base=LEVELS[9];""", 1, "CH_NAMES")
rep("""        tier: CH_NAMES[c-1],
        n: isBoss ? (CH_NAMES[c-1]+'首領：'+bossName) : (CH_NAMES[c-1]+' 第'+(p+1)+'關'),""",
"""        tier: 4+c,                      // 第2~10章對應 tier 5~13
        n:'',                            // 顯示名稱由 applyLanguage() 依語言填入
        idxInCh: p+1,                    // 章節內第幾關（產生名稱用）""", 1, "genName")
rep("""        d: isBoss ? ('★ 第'+(c+1)+'章壓軸：超級大 Boss「'+bossName+'」坐鎮，血量與強度全面超越前一章。')
           : isOpener ? ('進入「'+CH_NAMES[c-1]+'」章節，難度較上一章末暫時回落，準備重新爬升。')
           : ('「'+CH_NAMES[c-1]+'」章節持續加壓，敵人血量與出怪密度持續上修。'),""",
"""        d:'', kind: isBoss?'boss':(isOpener?'opener':'mid'), ch:c,   // 描述同樣交給 applyLanguage()""", 1, "genDesc")
rep("    const bossName=BOSS_CHAPTER[c].name;\n", "", 1, "bossName")

# ── B. 顯示點改走 T() ────────────────────────────────────────
rep("""  ctx.font='800 10.5px system-ui'; ctx.fillStyle=TIER_COLOR[G.L.tier];
  ctx.fillText('第 '+(G.lvIdx+1)+' 關 · '+G.L.n+'（'+G.L.tier+'）', pad, hy+54);""",
"""  ctx.font='800 10.5px system-ui'; ctx.fillStyle=TIER_COLOR[G.L.tier];
  ctx.fillText(T('hudStage',G.lvIdx+1,G.L.n,tierName(G.L.tier)), pad, hy+54);""",1,"hudStage")
rep("""  x.fillText('第 '+(G.lvIdx+1)+' 關 · '+G.L.n+'（'+G.L.tier+'）',w/2,py+ph+30);""",
"""  x.fillText(T('hudStage',G.lvIdx+1,G.L.n,tierName(G.L.tier)),w/2,py+ph+30);""",1,"polaroid")
rep("""    '<div class="st" style="color:'+c+'">'+(showCleared?'全部通關':'第 '+(i+1)+' 關 / '+LEVELS.length+'　·　'+L.tier)+'</div>'+
    '<div class="nm">'+(showCleared?'恭喜全破！':L.n)+'</div>'+
    '<div class="ds">'+(showCleared?('你已經打穿全部 '+LEVELS.length+' 關。再玩一次挑戰更快的紀錄。'):L.d)+'</div>'+
    '<div class="mt">'+Math.floor(L.dur/60)+':'+String(L.dur%60).padStart(2,'0')+
      '　·　♥'+L.hearts+'　·　Boss ×'+L.nboss+'</div>';""",
"""    '<div class="st" style="color:'+c+'">'+(showCleared?T('allClear'):(T('stageOf',i+1,LEVELS.length)+'　·　'+tierName(L.tier)))+'</div>'+
    '<div class="nm">'+(showCleared?T('congrats'):L.n)+'</div>'+
    '<div class="ds">'+(showCleared?T('allClearDesc',LEVELS.length):L.d)+'</div>'+
    '<div class="mt">'+Math.floor(L.dur/60)+':'+String(L.dur%60).padStart(2,'0')+
      '　·　♥'+L.hearts+'　·　'+T('bossCount',L.nboss)+'</div>';""",1,"stageInfo")
rep("""  document.getElementById('btnPlay').textContent =
    i<frontier ? '重玩 · 第 '+(i+1)+' 關' :
    (PROGRESS>1 ? (showCleared?'再玩最後一關':'第 '+(i+1)+' 關') : '開始遊戲');""",
"""  document.getElementById('btnPlay').textContent =
    i<frontier ? T('replayLv',i+1) :
    (PROGRESS>1 ? (showCleared?T('playLast'):T('playLv',i+1)) : T('play'));""",1,"btnPlay")

# HUD 其餘
rep("""  if(over0){ tt='擊倒 BOSS！';""","""  if(over0){ tt=T('killBoss');""",1,"killBoss")
rep("""  ctx.fillText('LV.'+P.lv, pad, hy+38);""","""  ctx.fillText(T('hudLv',P.lv), pad, hy+38);""",1,"hudLv")
rep("""  ctx.fillText('擊殺 '+G.kills, pad+46, hy+38);""","""  ctx.fillText(T('hudKills',G.kills), pad+46, hy+38);""",1,"hudKills")
rep("""  const gt='果凍 '+gp+'%  傷害 +'+Math.round(gp*0.30)+'%';""",
    """  const gt=T('hudGoo',gp,Math.round(gp*0.30));""",1,"hudGoo")
rep("""    const st2='速度 ×'+sc.toFixed(2);""","""    const st2=T('hudSpeed',sc.toFixed(2));""",1,"hudSpeed")
rep("""    const warnTxt='⚠ '+(G.bossWarnName||'BOSS')+' 即將出現';""",
    """    const warnTxt=T('bossWarn',G.bossWarnName||'BOSS');""",1,"bossWarn")
rep("""    ctx.fillText((G.boss.superBoss?'⚠️ 超級大 BOSS · ':'')+G.boss.name, W/2, by-7);""",
    """    ctx.fillText((G.boss.superBoss?T('superBossTag'):'')+G.boss.name, W/2, by-7);""",1,"superBossTag")
rep("""    const msg='按住螢幕任意處，然後拖曳手指來移動';""","""    const msg=T('hintMove');""",1,"hintMove")
rep("""    const msg2='左下 » 鍵 = 點一下往移動方向加速（無敵幀）';""","""    const msg2=T('hintDash');""",1,"hintDash")
rep("""    const msg3='愛心用完就結束 — 靠閃避活下來';""","""    const msg3=T('hintHearts');""",1,"hintHearts")
rep("""    const msg4='看到箭頭就往那邊跑，那裡有寶箱';""","""    const msg4=T('hintChest');""",1,"hintChest")
rep("""      ctx.strokeText('⚠ 偵測不到任何觸控事件',W/2,H*0.44);
      ctx.fillText('⚠ 偵測不到任何觸控事件',W/2,H*0.44);""",
"""      ctx.strokeText(T('noTouch'),W/2,H*0.44);
      ctx.fillText(T('noTouch'),W/2,H*0.44);""",1,"noTouch")

# toast / pop
rep("""    pop(P.x,P.y-30,'護盾擋下！','#8fd8ff',18); SFX.dash();""",
    """    pop(P.x,P.y-30,T('tShield'),'#8fd8ff',18); SFX.dash();""",1,"tShield")
rep("""      if(P.shieldN<cap){ P.shieldN++; pop(P.x,P.y-34,'護盾','#8fd8ff',18); SFX.heal(); } }""",
    """      if(P.shieldN<cap){ P.shieldN++; pop(P.x,P.y-34,T('tShieldGain'),'#8fd8ff',18); SFX.heal(); } }""",1,"tShieldGain")
rep("""      if(n){ burst(P.x,P.y,26,195,1.6); shake(3); toast('冰凍！','#8fe8ff'); SFX.heal(); }""",
    """      if(n){ burst(P.x,P.y,26,195,1.6); shake(3); toast(T('tFreeze'),'#8fe8ff'); SFX.heal(); }""",1,"tFreeze")
rep("""      toast('🕯️ 重生！剩餘 '+G.revives+' 次','#ffd84f'); SFX.evo();""",
    """      toast(T('tRevive',G.revives),'#ffd84f'); SFX.evo();""",1,"tRevive")
rep("""    if(P.hearts<P.maxHearts){ P.hearts++; toast('全能力已滿 → 回復愛心！','#ff7aa2'); SFX.heal(); }
    else { gemBurst(P.x,P.y,12*owed); toast('全能力已滿 → 晶核大放送！','#ffd84f'); SFX.pickup(); }""",
"""    if(P.hearts<P.maxHearts){ P.hearts++; toast(T('tAllMaxHeart'),'#ff7aa2'); SFX.heal(); }
    else { gemBurst(P.x,P.y,12*owed); toast(T('tAllMaxGem'),'#ffd84f'); SFX.pickup(); }""",1,"tAllMax")
rep("""  toast('☢️ 核彈引爆！清空 '+n+' 隻小怪','#ff9a4f');""",
    """  toast(T('tNuke',n),'#ff9a4f');""",1,"tNuke")
rep("""    toast('⚠️ 超級大 BOSS：'+cfg.name+'！','#ff2a6b'); shake(14); hitstop(.12);""",
    """    toast(T('tSuperBossIn',cfg.name),'#ff2a6b'); shake(14); hitstop(.12);""",1,"tSuperBossIn")
rep("""    toast(cfg.name+' 出現！','#ff6b6b'); shake(7);""",
    """    toast(T('tBossIn',cfg.name),'#ff6b6b'); shake(7);""",1,"tBossIn")
rep("""  cardsEl.innerHTML='<div class="lvtitle">LV.'+G.P.lv+' 升級！選一張</div>';""",
    """  cardsEl.innerHTML='<div class="lvtitle">'+T('cardTitle',G.P.lv)+'</div>';""",1,"cardTitle")
rep("""    const lvTag = u.w ? (u.evo?'<div class="lv">超載進化</div>'
                        :'<div class="lv">'+(G.P.wep[u.w]===0?'新武器':'Lv.'+(G.P.wep[u.w]+1))+'</div>')
                      : (u.stack>0?'<div class="lv">強化</div>':'');""",
"""    const lvTag = u.w ? (u.evo?'<div class="lv">'+T('evolve')+'</div>'
                        :'<div class="lv">'+(G.P.wep[u.w]===0?T('newWeapon'):T('lvTag',G.P.wep[u.w]+1))+'</div>')
                      : (u.stack>0?'<div class="lv">'+T('upgradeTag')+'</div>':'');""",1,"lvTag")
# 結算
rep("""  if(win) sub='通關！擊殺 '+G.kills+' 隻';
  else if(pct>=60) sub='走到 '+pct+'%，再撐 '+remain+' 秒就過關了！';
  else sub='走到 '+pct+'%，擊殺 '+G.kills+' 隻';""",
"""  if(win) sub=T('nmWin',G.kills);
  else if(pct>=60) sub=T('nmClose',pct,remain);
  else sub=T('nmFar',pct,G.kills);""",1,"nearmiss")
rep("""    '<div class="coingain">🍬 +'+earned+' 糖果幣　<span class="tot">（共 '+Math.round(COINS)+'）</span></div>';""",
    """    '<div class="coingain">🍬 '+T('coinGain',earned)+'　<span class="tot">'+T('coinTotal',Math.round(COINS))+'</span></div>';""",1,"coingain")
rep("""  overTitle.textContent = win?'CLEAR!':'GAME OVER';""",
    """  overTitle.textContent = win?T('clear'):T('gameover');""",1,"overTitle")
# 商店
rep("""  document.getElementById('shopCoins').textContent='🍬 '+Math.round(COINS)+' 糖果幣';""",
    """  document.getElementById('shopCoins').textContent='🍬 '+T('shopCoins',Math.round(COINS));""",1,"shopCoins")
rep("""    btn.textContent=maxed?'MAX':('🍬'+price);""",
    """    btn.textContent=maxed?T('max'):('🍬'+price);""",1,"maxBtn")
rep("""      '<div class="md">'+(maxed?('已滿級 · '+u.d(u.max-1)):u.d(lv))+'</div>'+""",
    """      '<div class="md">'+(maxed?(T('max')+' · '+u.d(u.max-1)):u.d(lv))+'</div>'+""",1,"shopMd")
rep("""      toast(c.type.n+'：'+msg, c.type.c);""","""      toast(c.type.n+' · '+msg, c.type.c);""",1,"chestToast")

open(p,'w',encoding='utf-8').write(s)
print("第二階段完成")
