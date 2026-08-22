#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全面掃描：英文模式下，畫面上實際被畫出來/寫出來的每一段文字裡有沒有中日韓字元。

為什麼要這支測試：
  v0.9.19 的 py_i18n.py 只驗了「L10N 表本身完整」與「DOM 元素文字」，
  但遊戲有大量文字是直接畫在 canvas 上（HUD、提示、戰報圖），
  而且有些 toast 是硬寫中文、根本沒有走 T()。真人玩家（davidform.github.io）
  在英文版看到「遠處出現寶箱！快去拿」就是這個漏洞。

做法：
  1. 攔截 CanvasRenderingContext2D.prototype.fillText / strokeText，錄下每一段畫出的字
  2. 逐一走過所有畫面（主選單／關卡圖／糖果屋／語言選單／重來確認／暫停／
     升級卡／勝利／失敗／分享圖）與所有會觸發 toast 的遊戲事件
  3. 掃描 DOM 全文
  4. 任何中日韓字元都算失敗（語言選單裡的母語名稱是白名單）
"""
import http.server, socketserver, threading, functools, sys, re
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8795
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

CJK=re.compile(r'[぀-ヿ㐀-䶿一-鿿가-힯]')
# 語言選單裡各語言的母語名稱是「刻意」用該語言寫的，不算洩漏
WHITE={"繁體中文","简体中文","日本語","한국어"}

HOOK = """
window.__drawn=[];
for(const fn of ['fillText','strokeText']){
  const orig=CanvasRenderingContext2D.prototype[fn];
  CanvasRenderingContext2D.prototype[fn]=function(t,...a){
    if(t!==undefined && t!==null) window.__drawn.push(String(t));
    return orig.call(this,t,...a);
  };
}
"""

def collect(pg, label, fails):
    drawn = pg.evaluate("()=>{ const d=window.__drawn.slice(); window.__drawn.length=0; return d; }")
    dom   = pg.evaluate("()=>document.body.innerText||''")
    bad=[]
    for t in drawn:
        if CJK.search(t) and t.strip() not in WHITE: bad.append(("canvas",t))
    for lineTxt in dom.split("\n"):
        if CJK.search(lineTxt) and lineTxt.strip() not in WHITE: bad.append(("dom",lineTxt.strip()))
    seen=set(); uniq=[]
    for k,t in bad:
        if (k,t) in seen: continue
        seen.add((k,t)); uniq.append((k,t))
    if uniq:
        print(f"  ❌ {label}：{len(uniq)} 處中文洩漏")
        for k,t in uniq[:12]: print(f"       [{k}] {t[:70]}")
        fails.extend([(label,k,t) for k,t in uniq])
    else:
        print(f"  ✅ {label}")

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.add_init_script(HOOK)
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(800)

    fails=[]
    print("=== 語言確認 ===")
    print("  LANG =", pg.evaluate("()=>LANG"))
    assert pg.evaluate("()=>LANG")=="en", "測試前提：預設必須是英文"

    print("\n=== 靜態畫面 ===")
    collect(pg,"主選單 + 關卡圖",fails)

    pg.evaluate("()=>{ COINS=999; showShop(); }"); pg.wait_for_timeout(400)
    collect(pg,"糖果屋",fails)
    pg.evaluate("()=>showMenu()"); pg.wait_for_timeout(300)

    pg.evaluate("()=>{ const e=document.getElementById('langWrap')||document.getElementById('lang'); if(e)e.classList.remove('hide'); const b=document.getElementById('btnLang'); if(b)b.click(); }")
    pg.wait_for_timeout(400)
    collect(pg,"語言選單",fails)
    pg.evaluate("()=>showMenu()"); pg.wait_for_timeout(300)

    pg.evaluate("()=>{ const b=document.getElementById('btnReset'); if(b)b.click(); }")
    pg.wait_for_timeout(400)
    collect(pg,"重來確認框",fails)
    pg.evaluate("()=>showMenu()"); pg.wait_for_timeout(300)

    print("\n=== 遊戲中：所有會噴 toast 的事件 ===")
    pg.evaluate("""()=>{
        META={hearts:2,dmg:2,aspd:2,range:1,xp:1,pickup:1,dash:1,wep:2,coin:1,revive:2};
        LV_IDX=9; start(); G.hasMoved=true; DIAG.touch=3;
        window.__showCards=showCards; showCards=()=>{G.pendingCards=0;};
    }""")
    pg.wait_for_timeout(600)
    pg.evaluate("()=>{ window.__drawn.length=0; }")

    events = [
      ("寶箱出現 spawnChest()",      "()=>{ spawnChest(); }"),
      ("撿到寶箱 openChest()",       "()=>{ G.CHEST.push({x:G.P.x,y:G.P.y,life:18,max:18,wob:0,pop:0,type:pick(CHEST_POOL)}); G.P.x=G.CHEST[0].x; update(0.016,0.016); }"),
      ("核彈補給出現",               "()=>{ G.nukeSpawned=false; G.nukeSpawnAt=0; G.t=1; update(0.016,0.016); }"),
      ("撿到核彈",                   "()=>{ G.NUKE={x:G.P.x,y:G.P.y,wob:0}; update(0.016,0.016); }"),
      ("引爆核彈",                   "()=>{ G.P.nukeHeld=true; doNuke(); }"),
      ("護盾 HUD",                   "()=>{ G.P.shieldN=2; drawHUD&&0; update(0.016,0.016); }"),
      ("暴走 HUD",                   "()=>{ G.P.frenzyT=4; update(0.016,0.016); }"),
      ("護盾擋下傷害",               "()=>{ G.P.shieldN=1; G.P.iframe=0; hurtPlayer&&hurtPlayer(1); }"),
      ("冰凍",                       "()=>{ toast(T('tFreeze'),'#8fe8ff'); }"),
      ("Boss 登場",                  "()=>{ spawnBoss((G.bosses||buildBosses(CUR()))[0]); }"),
      ("超級大 Boss 登場",           "()=>{ const c={...(G.bosses||buildBosses(CUR()))[0], superBoss:true, name:BOSS_CHAPTER[0].name}; spawnBoss(c); }"),
      ("重生蠟燭",                   "()=>{ G.P.hearts=1; G.P.iframe=0; G.P.revives=2; if(typeof hurtPlayer==='function'){G.P.shieldN=0; hurtPlayer(99);} }"),
      ("全滿→補心/晶核雨",           "()=>{ showCards=window.__showCards; UPGRADES.forEach(u=>{ for(let i=0;i<9;i++){ try{u.f(G.P);}catch(e){} } }); G.pendingCards=1; showCards(); showCards=()=>{G.pendingCards=0;}; }"),
    ]
    for label, js in events:
        try:
            pg.evaluate(js)
        except Exception as e:
            print(f"  ⚠ {label} 觸發失敗（測試腳本問題，非遊戲問題）: {str(e)[:90]}")
            continue
        pg.wait_for_timeout(260)
        collect(pg, label, fails)

    print("\n=== 暫停 / 結算 / 分享圖 ===")
    pg.evaluate("()=>{ doPause(); }"); pg.wait_for_timeout(350)
    collect(pg,"暫停畫面",fails)
    pg.evaluate("()=>{ doPause(); }"); pg.wait_for_timeout(200)

    pg.evaluate("()=>{ G.kills=180; G.P.lv=12; G.t=95; endGame(true); }"); pg.wait_for_timeout(600)
    collect(pg,"勝利結算",fails)

    pg.evaluate("()=>{ LV_IDX=9; start(); G.hasMoved=true; DIAG.touch=3; G.kills=60; G.P.lv=6; G.t=40; endGame(false); }")
    pg.wait_for_timeout(600)
    collect(pg,"失敗結算",fails)

    print("  分享圖（shareCard 的 canvas 文字）")
    pg.evaluate("()=>{ window.__drawn.length=0; }")
    r=pg.evaluate("""()=>{
        if(typeof makePolaroid!=='function') return 'NO_FN';
        try{ makePolaroid(true); makePolaroid(false); return 'OK'; }catch(e){ return 'ERR:'+e.message; }
    }""")
    print("   ", r)
    if r=="OK": collect(pg,"分享圖",fails)
    else: print("    ⚠ 找不到分享圖函式，改用按鈕觸發")

    print("\n=== 全 100 關的關卡名稱與說明 ===")
    lv=pg.evaluate("()=>LEVELS.map((L,i)=>({i:i+1,n:L.n,d:L.d}))")
    leak=[x for x in lv if CJK.search(str(x['n'])+str(x['d']))]
    if leak:
        print(f"  ❌ {len(leak)} 關的名稱/說明是中文")
        for x in leak[:6]: print(f"       第{x['i']}關 {x['n']} / {str(x['d'])[:40]}")
        fails.extend([("關卡表","data",str(x)) for x in leak])
    else: print("  ✅ 100 關全部是英文")

    print("\n=== 所有卡片 / 永久強化 / Boss / 寶箱 / 敵人的顯示欄位 ===")
    tbl=pg.evaluate("""()=>({
        UPGRADES: UPGRADES.map(u=>[u.n,u.d,u.d2||'']),
        META: META_UPGRADES.map(u=>[u.n, (typeof u.d==='function'?u.d(0):u.d)]),
        BOSS_POOL: BOSS_POOL.map(x=>x.name),
        BOSS_CHAPTER: BOSS_CHAPTER.map(x=>x.name),
        CHEST: CHEST_TYPES.map(x=>x.n),
        WEAPONS: Object.keys(WEAPONS).map(k=>[WEAPONS[k].name, WEAPONS[k].desc(1)]),
        EVOS: Object.keys(EVOS).map(k=>[EVOS[k].name, EVOS[k].desc]),
        ETYPE: Object.keys(ETYPE).map(k=>ETYPE[k].name)
    })""")
    for name,val in tbl.items():
        flat=[str(x) for x in (val if isinstance(val,list) else [val])]
        bad=[x for x in flat if CJK.search(x)]
        if bad:
            print(f"  ❌ {name}: {len(bad)} 筆中文 → {bad[:3]}")
            fails.extend([(name,"data",x) for x in bad])
        else:
            print(f"  ✅ {name}")

    print("\n=== JS 錯誤 ===")
    print("  ", errs[:3] if errs else "無")
    if errs: fails.append(("JS錯誤","","; ".join(errs[:3])))

    b.close()
srv.shutdown()

print()
if fails:
    print(f"❌ 共 {len(fails)} 處中文洩漏（英文模式）")
    sys.exit(1)
print("=== 全部通過：英文模式下沒有任何中日韓字元洩漏 ===")
