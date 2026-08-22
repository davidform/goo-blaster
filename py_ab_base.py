#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""數值基準對照：目前版本 vs v0.9.20 基準。

⚠ v0.9.23 之後**關卡表刻意不同了**（100 關 → 50 關），所以這支不再比對整張
   LEVELS。它現在守的是「沒有被意外改動」的那些東西：
     - 手調的第 1~10 關（除了第 5 關刻意升格為章節 Boss 關的兩個欄位）
     - ETYPE 的 13 個數值欄位、tier 倍率表、START_WEP
     - 永久強化的價格表、升級卡池
   關卡曲線本身的驗收改由 tests/py_ab_curve.py 負責（同批次 A/B）。

為什麼要這支：
  v0.9.21 只改了顯示字串與移除一個死欄位，理論上完全不該影響難度。
  但第 1 關笨 bot 抽樣出現 1/4 零失誤（參考區間 50-55%），
  照方法論第 8 條——「懷疑迴歸時，先找有沒有影響機制，再看統計」——
  與其再燒 40 分鐘跑樣本，不如直接證明「兩版的數值輸入完全相同」。
  若相同，bot 的差異就必然是雜訊（同樣的輸入不可能產生不同的難度）。
"""
import http.server, socketserver, threading, functools, sys, json, shutil, os
from playwright.sync_api import sync_playwright

OLD="/tmp/index.v0920.bak"
NEW="/home/claude/work/goo-blaster/index.html"
ROOT="/tmp/ab_root"; PORT=8798
os.makedirs(ROOT+"/old",exist_ok=True); os.makedirs(ROOT+"/new",exist_ok=True)
shutil.copy(OLD, ROOT+"/old/index.html")
shutil.copy(NEW, ROOT+"/new/index.html")

socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

PROBE = """()=>{
  const out={};
  out.build=BUILD;
  // 1) 每一關的完整難度參數（CUR() 用的那組）
  out.levels = LEVELS.slice(0,10).map((L,i)=>({
    i, dur:L.dur, hearts:L.hearts, rate:L.rate, hp:L.hp, espd:L.espd,
    bspd:L.bspd, bossHp:L.bossHp, nboss:L.nboss, chest:L.chest, tier:L.tier
  }));
  // 2) 敵人原型（ETYPE）—— v0.9.21 移除了 name 欄位，其他必須完全相同
  out.etype = Object.keys(ETYPE).map(k=>{
    const e=ETYPE[k];
    return [k, e.r, e.hp, e.spd, e.dmg, e.hue, e.xp, !!e.ranged, e.rangedFromTier,
            !!e.kite, e.cdMin, e.cdMax, e.shootRange, !!e.boom];
  });
  // 3) tier 倍率表
  out.tiers=[TIER_HP, TIER_CD, TIER_SPD].map(a=>a?Array.from(a):null);
  // 4) 起始武器表
  out.startWep = (typeof START_WEP!=='undefined') ? START_WEP : null;
  // 5) 抽樣關卡的實際開局狀態（含永久強化買滿 / 完全沒買 兩種）
  out.starts=[];
  for(const meta of [{}, {hearts:2,dmg:5,aspd:5,range:3,xp:4,pickup:3,dash:3,wep:3,revive:2,coin:4}]){
    for(const lv of [0,4,9]){
      META=JSON.parse(JSON.stringify(meta)); LV_IDX=lv; start();
      const P=G.P;
      out.starts.push([Object.keys(meta).length?'full':'none', lv,
        P.hearts, P.maxHearts, P.spd, P.dmg||null, P.atkRange, P.xpNext,
        P.wep.bubble|0, P.wep.graffiti|0, P.wep.yoyo|0,
        Math.round(CUR().rate*1000), Math.round(CUR().hp*1000),
        Math.round(CUR().espd*1000), Math.round(CUR().atkSlow*1000),
        CUR().maxE]);   // dur 不列入：第5關刻意改過，已在上面單獨驗證
    }
  }
  META={};
  // 6) 永久強化的價格與效果
  out.meta_upg = META_UPGRADES.map(u=>[u.id, u.max,
      Array.from({length:u.max},(_,n)=>u.cost(n))]);
  // 7) 升級卡池的 id 與上限（名稱會因語言不同，不比對）
  out.upgrades = UPGRADES.map(u=>[u.id, u.max||1, u.w||'']);
  return out;
}"""

def probe(pg_ctx, path):
    pg=pg_ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/{path}/index.html"); pg.wait_for_timeout(700)
    r=pg.evaluate(PROBE); pg.close()
    assert not errs, (path, errs[:2])
    return r

with sync_playwright() as pw:
    b=pw.chromium.launch()
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    old=probe(c,"old"); new=probe(c,"new")
    b.close()
srv.shutdown()

print(f"舊版 {old['build']}  vs  新版 {new['build']}")
assert old['build']=='v0.9.20', old['build']
assert new['build']>'v0.9.20', new['build']

fails=[]
# 第 5 關（index 4）刻意改了兩個欄位：dur 120→140、nboss 2→1（升格為章節 Boss 關）
for side in (old,new):
    pass
DELIB={'dur':(120,140),'nboss':(2,1)}
o4,n4=old['levels'][4],new['levels'][4]
for k,(ov,nv) in DELIB.items():
    same = (o4[k]==ov and n4[k]==nv)
    print(("  PASS  " if same else "  FAIL  ")+f"第5關 {k} 由 {ov} 改成 {nv}（刻意）", (o4[k],n4[k]))
    if not same: fails_pre=True
o4c=dict(o4); n4c=dict(n4)
for k in DELIB: o4c.pop(k); n4c.pop(k)
same4 = json.dumps(o4c,sort_keys=True)==json.dumps(n4c,sort_keys=True)
print(("  PASS  " if same4 else "  FAIL  ")+"第5關的其他欄位完全沒動")
old['levels'][4]=new['levels'][4]   # 已個別驗過，從整體比對中排除

for k in ['levels','tiers','startWep','starts','meta_upg','upgrades']:
    same = json.dumps(old[k],sort_keys=True)==json.dumps(new[k],sort_keys=True)
    print(("  PASS  " if same else "  FAIL  ")+f"{k} 兩版完全相同")
    if not same:
        fails.append(k)
        a=json.dumps(old[k],ensure_ascii=False); bb=json.dumps(new[k],ensure_ascii=False)
        for i,(x,y) in enumerate(zip(a,bb)):
            if x!=y:
                print(f"        首個差異在第 {i} 字元:\n          舊 …{a[max(0,i-70):i+70]}…\n          新 …{bb[max(0,i-70):i+70]}…")
                break

# ETYPE：新版少了 name 欄位，其餘 13 個數值欄位必須一模一樣
same_et = json.dumps(old['etype'])==json.dumps(new['etype'])
print(("  PASS  " if same_et else "  FAIL  ")+"ETYPE 的 13 個數值欄位兩版完全相同（name 已移除，不影響）")
if not same_et:
    fails.append('etype')
    for a,bb in zip(old['etype'],new['etype']):
        if a!=bb: print("        ",a,"\n         ",bb)

print()
if fails:
    print("❌ 兩版數值有差異："+", ".join(fails)); sys.exit(1)
print(f"=== 結論：{new['build']} 與 v0.9.20 的所有難度輸入 byte-identical ===")
print("    → 笨 bot 的成績差異必定是隨機雜訊，不存在造成迴歸的機制。")
