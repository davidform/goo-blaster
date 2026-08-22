# -*- coding: utf-8 -*-
"""v0.9.23：100 關 → 50 關，章節 Boss 從「每 10 關」改成「每 5 關」。

依據：docs-10-關卡數量評估.md（實測第 61-100 關設定完全相同、第 7 關之後
沒有新敵人、enemyTier 第 9 關封頂、相鄰關差異第 51 關後只剩 1.03%）。

設計原則：**難度範圍完全不縮水**——把舊第 100 關的終點原封不動搬到新第 50 關。
所有「以章節 c 為索引」的參數（startWep / xpMul / atkSlow / Boss 造型 / 難度頂點）
全部不動，只把「每章 10 關」改成「每章 5 關」。需要重算的只有以關卡編號
為索引的三個：dur / maxE / chest。

新結構：10 章 × 5 關 = 50 關，章節 Boss 在第 5/10/15/…/50 關。
  ch0 = 第 1-5 關   （手調，原本的第 1-5 關，第 5 關新增章節 Boss）
  ch1 = 第 6-10 關  （手調，原本的第 6-10 關，章節 Boss 改用 BOSS_CHAPTER[1]）
  ch2..ch9 = 第 11-50 關（公式生成，每章 5 關）
"""
import json, re, sys, os
P='/home/claude/work/goo-blaster/index.html'
s=open(P,encoding='utf-8').read(); orig=s
def rep(o,n,tag,cnt=1):
    global s
    assert s.count(o)==cnt, f"[{tag}] 預期 {cnt} 處，實際 {s.count(o)}"
    s=s.replace(o,n,cnt)

# ── 1. 手調關卡：補上 ch，第 5 關升格為章節 Boss 關 ──────────────────
for i,ch in [(0,0),(1,0),(2,0),(3,0)]:
    pass
rep(""" {tier:0, n:'果凍幼幼園',   dur:70 , hearts:3, rate:0.40, hp:0.30, espd:0.70,
  bossHp:0.20, nboss:1, types:['slime'], bspd:0.60, atkSlow:1.80, chest:8 , maxE:40,
  d:'學會拖曳移動。怪物慢、血少，不會反擊。'},""",
""" {tier:0, n:'果凍幼幼園',   dur:70 , hearts:3, rate:0.40, hp:0.30, espd:0.70,
  bossHp:0.20, nboss:1, types:['slime'], bspd:0.60, atkSlow:1.80, chest:8 , maxE:40,
  ch:0, idxInCh:1,
  d:'學會拖曳移動。怪物慢、血少，不會反擊。'},""","lv1")
rep(""" {tier:0, n:'軟糖草原',     dur:85 , hearts:3, rate:0.50, hp:0.40, espd:0.76,
  bossHp:0.28, nboss:1, types:['slime'], bspd:0.65, atkSlow:1.70, chest:9 , maxE:50,""",
""" {tier:0, n:'軟糖草原',     dur:85 , hearts:3, rate:0.50, hp:0.40, espd:0.76,
  bossHp:0.28, nboss:1, types:['slime'], bspd:0.65, atkSlow:1.70, chest:9 , maxE:50,
  ch:0, idxInCh:2,""","lv2")
rep("""  bossHp:0.36, nboss:2, types:['slime','bunny'], bspd:0.70, atkSlow:1.60, chest:10, maxE:58,""",
"""  bossHp:0.36, nboss:2, types:['slime','bunny'], bspd:0.70, atkSlow:1.60, chest:10, maxE:58,
  ch:0, idxInCh:3,""","lv3")
rep("""  bossHp:0.46, nboss:2, types:['slime','bunny'], bspd:0.76, atkSlow:1.45, chest:11, maxE:68,""",
"""  bossHp:0.46, nboss:2, types:['slime','bunny'], bspd:0.76, atkSlow:1.45, chest:11, maxE:68,
  ch:0, idxInCh:4,""","lv4")
# 第 5 關升格為第 1 章的章節 Boss 關：
#   - 加 superBoss / bossChapter:0（Molar Crusher，造型＝尖刺）
#   - 一般 Boss 由 2 隻減為 1 隻（總 Boss 數維持 2 隻，不讓這關突然變成 3 隻）
#   - 時長 120→140 秒，讓章節 Boss（在 93% 時出場）有合理的作戰時間
rep(""" {tier:2, n:'黏黏果醬工廠', dur:120, hearts:3, rate:0.54, hp:0.68, espd:0.88,
  bossHp:0.56, nboss:2, types:['slime','bunny','drone'], bspd:0.82, atkSlow:1.35, chest:12, maxE:76,
  d:'★ 無人機登場：會從遠處射擊。學會用加速鍵的無敵幀穿過子彈。'},""",
""" {tier:2, n:'黏黏果醬工廠', dur:140, hearts:3, rate:0.54, hp:0.68, espd:0.88,
  bossHp:0.56, nboss:1, types:['slime','bunny','drone'], bspd:0.82, atkSlow:1.35, chest:12, maxE:76,
  ch:0, idxInCh:5, superBoss:true, bossChapter:0,
  d:'★ 無人機登場：會從遠處射擊。學會用加速鍵的無敵幀穿過子彈。'},""","lv5")
rep("""  bossHp:0.68, nboss:2, types:['slime','bunny','drone'], bspd:0.88, atkSlow:1.22, chest:13, maxE:88,""",
"""  bossHp:0.68, nboss:2, types:['slime','bunny','drone'], bspd:0.88, atkSlow:1.22, chest:13, maxE:88,
  ch:1, idxInCh:1,""","lv6")
rep("""  bossHp:0.80, nboss:3, types:['slime','bunny','drone','bomber'], bspd:0.92, atkSlow:1.12, chest:14, maxE:96,""",
"""  bossHp:0.80, nboss:3, types:['slime','bunny','drone','bomber'], bspd:0.92, atkSlow:1.12, chest:14, maxE:96,
  ch:1, idxInCh:2,""","lv7")
rep("""  bossHp:0.95, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.00, atkSlow:1.00, chest:15, maxE:106,""",
"""  bossHp:0.95, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.00, atkSlow:1.00, chest:15, maxE:106,
  ch:1, idxInCh:3,""","lv8")
rep("""  bossHp:1.25, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.08, atkSlow:0.92, chest:16, maxE:118,""",
"""  bossHp:1.25, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.08, atkSlow:0.92, chest:16, maxE:118,
  ch:1, idxInCh:4,""","lv9")
rep("""  bossHp:1.70, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.20, atkSlow:0.82, chest:17, maxE:130,
  superBoss:true, bossChapter:0,""",
"""  bossHp:1.70, nboss:3, types:['slime','bunny','drone','bomber'], bspd:1.20, atkSlow:0.82, chest:17, maxE:130,
  ch:1, idxInCh:5, superBoss:true, bossChapter:1,""","lv10")

# ── 2. 關卡產生器：8 章 × 5 關 = 第 11-50 關 ──────────────────────────
old_loop = s[s.index("  for(let c=1;c<=9;c++){"): s.index("})();\n\n// ⚠ 一定要等 genExtraLevels()")]
new_loop = """  // ── v0.9.23：每章 5 關（原本 10 關）────────────────────────────────
  // 難度頂點刻意重新內插，讓「舊第 100 關的終點」原封不動落在「新第 50 關」：
  //   舊：peakMul(c)=1+c*0.17，c=0..9 分別對應第 10/20/…/100 關，終點 2.53
  //   新：第 1、2 章是手調的第 1-10 關（頂點 = 第 10 關 = 1.0），
  //       生成的是第 3~10 章（c=2..9），8 章要走完 1.0 → 2.53
  //       ⇒ 每章 +0.19125（= 0.17 × 9/8），終點完全相同
  // 以「章節 c」為索引的參數（startWep / xpMul / atkSlow / Boss 造型）全部不動，
  // 需要重算的只有以「關卡編號」為索引的三個：dur / maxE / chest。
  for(let c=2;c<=9;c++){
    const pk=+(1+(c-1)*0.19125).toFixed(4);
    const st=+((1+(c-2)*0.19125)*0.93).toFixed(4);   // 本章開頭＝上一章頂點回落 7%
    for(let p=0;p<5;p++){
      const lvlNum=10+(c-2)*5+p+1;   // 第 11 ~ 50 關
      const f=p/4;                   // 章節內進度 0~1
      const mul=st+(pk-st)*f;
      const isBoss=p===4, isOpener=p===0;
      LEVELS.push({
        // 難度層級名稱：第 3~10 章對應 tier 5~12，最後一關獨佔 tier 13「終焉」
        tier: (lvlNum===50) ? 13 : (3+c),
        n:'',
        idxInCh: p+1,
        // v0.9.23：關卡時長從「最長 323 秒」壓到「最長 240 秒」。
        // 手機是零碎時間在玩的，單場 5 分半會逼玩家在「還沒打完但要下車」時直接放棄。
        dur: Math.round(200+(lvlNum-10)/40*40),      // 第11關 201 秒 → 第50關 240 秒
        hearts:3,
        rate: Math.min(6.0, +(base.rate*mul).toFixed(3)),
        hp: +(base.hp*mul).toFixed(3),
        espd: Math.min(1.85, +(base.espd*mul).toFixed(3)),
        bossHp: +(base.bossHp*mul).toFixed(3),
        nboss: 3,
        types: ['slime','bunny','drone','bomber'],
        bspd: Math.min(2.3, +(base.bspd*mul).toFixed(3)),
        atkSlow: +Math.max(0.62, base.atkSlow-c*0.02).toFixed(3),
        chest: Math.min(32, 17+Math.floor((lvlNum-10)*0.375)),
        maxE: Math.min(150, 130+Math.floor((lvlNum-10)*0.5)),
        startWep: START_WEP[c],
        xpMul: +(1+c*0.55).toFixed(2),
        d:'', kind: isBoss?'boss':(isOpener?'opener':'mid'), ch:c,
        superBoss: isBoss,
        ...(isBoss?{bossChapter:c}:{})
      });
    }
  }
"""
s=s.replace(old_loop,new_loop,1)

# ── 3. 糖果幣：關卡加成隨「新的關卡編號」重算 ─────────────────────
rep("  const lvBonus = 1 + lvIdx*0.025;",
"""  // v0.9.23：關卡數砍半後，同樣的「遊戲進度」對應到一半的 lvIdx，
  // 係數不跟著加倍的話，全破一次能拿到的糖果幣會少掉快一半，
  // 局外成長會追不上被壓縮的難度曲線。0.025 → 0.05，等於維持原本的
  // 「每推進一格進度給多少加成」。
  const lvBonus = 1 + lvIdx*0.05;""","coins")

# ── 4. 存檔遷移：舊的 100 關進度換算成新的 50 關 ────────────────────
rep("""      if(o.lang && L10N[o.lang]) LANG=o.lang;
      else LANG=DEFAULT_LANG;""",
"""      if(o.lang && L10N[o.lang]) LANG=o.lang;
      else LANG=DEFAULT_LANG;
      // v0.9.23：100 關 → 50 關的存檔遷移。新第 N 關 ≈ 舊第 2N 關，
      // 所以「已破關數」除以 2（無條件進位，寧可多給不要倒扣）。
      // 用 o.v 標記已遷移，避免重複執行把進度越切越小。
      if(!(o.v>=2)){
        const cleared=Math.max(0,(+o.progress||1)-1);
        PROGRESS=Math.min(LEVELS.length+1, Math.ceil(cleared/2)+1);
        SAVE_V=2; saveGame();
      }""","migrate")
rep("const PROG_KEY","const SAVE_VER=2;\nlet SAVE_V=SAVE_VER;\nconst PROG_KEY","savever")
rep("localStorage.setItem(PROG_KEY, JSON.stringify({progress:PROGRESS, coins:Math.round(COINS), meta:META, lang:LANG}))",
    "localStorage.setItem(PROG_KEY, JSON.stringify({progress:PROGRESS, coins:Math.round(COINS), meta:META, lang:LANG, v:SAVE_VER}))","savefmt")

rep("const BUILD='v0.9.22'","const BUILD='v0.9.23'","build")

assert s!=orig
open(P,'w',encoding='utf-8').write(s)
print("✅ v0.9.23 已寫入")
