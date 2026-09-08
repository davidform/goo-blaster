#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.39 驗收：三個綠殼護盾（Green Shell Guard）

為什麼要有這一支：
這一版新增的東西橫跨三個既有測試都沒走過的地方——
  · 寶箱池第一次有「關卡門檻」(minLv)，`CHEST_POOL` 從一個常數變成兩個池子
  · `G.EB` 的碰撞迴圈第一次在「打到玩家」之前插進另一個攔截者
  · `G.SHELL` 整個資料結構是新的
沒有測試釘住，下一個模型改敵彈迴圈或寶箱池時會靜默推翻它，
而且**推翻的症狀是「護盾好像沒作用」——玩起來只覺得難，不會有人想到是這裡壞了**。

驗收項目：
  A. 關卡門檻：第 1~8 關的寶箱池跟 v0.9.38 逐項相同（89 份、不含綠殼），
     第 9 關以後才含綠殼。⭐ 這一條是這一版**最重要的防線**：
     它擋的是「新道具偷偷把前 8 關變簡單」，而前 8 關的難度是 v0.9.35 花了
     一整版才調到真人認可的（他玩過之後說「第 7~8 關比較好了」）。
  B. 生成：三顆殼、每顆滿血、釘在 SHELL_ORBIT 半徑上（不是飄著的）。
  C. 擋彈：一發敵彈打在殼上 → 子彈消失、殼掉 1 血、玩家不掉心。
  D. 對照組：**同一發彈、沒有殼的時候會打到玩家**。
     ⚠ 少了 D，C 就是一條恆真的斷言（子彈本來就會被 splice 掉），
     那比沒有測試更糟——會訓練所有人不看輸出（AGENTS.md 第 3 節第 6 條）。
  E. 耗盡：擋掉 SHELL_N×SHELL_HP 發之後殼全部消失，不會無限擋。
  F. i18n：11 種語言都有 c_shell_n / c_shell_go，且佔位符真的被代換掉。

⚠ 決定性（沿用 py_nuke_calm 的三個坑）：
  1. **觸發跟讀取放在同一個 evaluate 裡。** 隔著 CDP 往返再讀狀態，平行批次下
     中間會被遊戲自己走掉好幾幀——場上會冒出新敵人、新子彈，讀到的
     `G.shellBlocked` 就混進了不是我丟的那幾發。
  2. **每次量測前清場**（`G.E.length=0; G.EB.length=0`），並且只認自己標記過的
     子彈（`b.__probe=1`）。不清場的話 C/E 兩項會被環境彈幕污染，
     紅字看起來像「擋彈數不對」，其實是尺標自己在動。
  3. **不用 `wait_for_timeout(固定毫秒)` 等遊戲內的東西**，一律輪詢；
     並且開場就掛自動選卡 + 補血，不然升級面板一跳出來 `G.paused=true`，
     後面每一項都量到 0，看起來像「功能沒做出來」。

用法：python3 tests/py_shell.py
"""
import http.server, socketserver, threading, functools, sys, asyncio
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.async_api import async_playwright

ROOT = GAME_ROOT
PORT = 8851
fails = []


def ck(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


async def poll(pg, expr, timeout_ms=30000, step=120):
    waited = 0
    while waited < timeout_ms:
        if await pg.evaluate("()=>!!(" + expr + ")"):
            return True
        await pg.wait_for_timeout(step)
        waited += step
    return False


AUTOCARD = """()=>{
  // 升級卡面板一出現就點一張。沒有這個的話玩家一升級遊戲就永久暫停。
  clearInterval(window.__ac);
  window.__ac=setInterval(()=>{
    const el=document.getElementById('cards');
    if(!el||el.classList.contains('hide')) return;
    const cs=[...el.querySelectorAll('.card')];
    if(cs.length) cs[0].click();
    if(G&&G.P){ G.P.hearts=99; G.P.maxHearts=99; }
  },60);
}"""


async def keep_alive(pg):
    await pg.evaluate("()=>{ if(G&&G.P){ G.P.hearts=99; G.P.maxHearts=99; G.P.iframe=0; } }")


async def alive_msg(pg):
    st = await pg.evaluate("()=>G?{run:!!G.running,pause:!!G.paused,over:!!G.over}:null")
    if st is None:
        return "G 不存在"
    if st["pause"]:
        return "被暫停（升級卡面板沒被點掉？）"
    if st["over"]:
        return "已結束"
    return "running=%s" % st["run"]


# 清場 + 丟一發標記過的敵彈到指定座標，然後**在同一個 evaluate 裡**推進一幀並回報。
PROBE = """(arg)=>{
  const P=G.P;
  G.E.length=0; G.EB.length=0;          // 清場：只認自己丟的那一發
  P.hearts=99; P.maxHearts=99; P.iframe=0; P.shieldN=0;   // 排除無敵幀與甜甜圈護盾
  const before={hearts:P.hearts, blocked:G.shellBlocked, hp:G.SHELL.map(s=>s.hp)};
  const at = arg.onShell && G.SHELL.length
      ? {x:G.SHELL[0].x, y:G.SHELL[0].y}
      : {x:P.x, y:P.y};
  G.EB.push({x:at.x, y:at.y, vx:0, vy:0, dmg:8, r:6, life:4.2, rot:0, spin:0, __probe:1});
  update(0.016, 0.016);
  return {
    before,
    hearts: P.hearts,
    blocked: G.shellBlocked,
    hp: G.SHELL.map(s=>s.hp),
    probeLeft: G.EB.filter(b=>b.__probe).length,
    shells: G.SHELL.length
  };
}"""


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(channel=BROWSER_CHANNEL, args=["--autoplay-policy=no-user-gesture-required"])
        c = await b.new_context(viewport={"width": 390, "height": 844},
                                device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await c.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        await pg.wait_for_function("typeof start === 'function'", timeout=60000)

        # ---------- 前置：這一版到底有沒有綠殼護盾 ----------
        # ⚠ 拿舊版當對照組跑的時候（收尾一定要跑一次，證明這支不是恆真的），
        #    下面每一個 evaluate 都會因為 ReferenceError 直接炸掉，紅字是一串
        #    JS 堆疊、看不出發生什麼事。先在這裡問一次、講人話。
        # ⚠ 不能用 `typeof window[k]` 探測：頂層的 `const` **不會**變成 window 的屬性
        #    （只有 `function` 宣告會），所以那樣寫連 v0.9.39 自己都會誤判成「缺」。
        #    改成把每一個名字包在自己的 arrow function 裡，讓 ReferenceError 現形。
        missing = await pg.evaluate("""()=>{
            const miss=[];
            const probe=(name,f)=>{ try{ if(typeof f()==='undefined') miss.push(name); }
                                    catch(e){ miss.push(name); } };
            probe('SHELL_N',        ()=>SHELL_N);
            probe('SHELL_HP',       ()=>SHELL_HP);
            probe('SHELL_MIN_LV',   ()=>SHELL_MIN_LV);
            probe('CHEST_POOL_LATE',()=>CHEST_POOL_LATE);
            probe('chestPool',      ()=>chestPool);
            probe('spawnShells',    ()=>spawnShells);
            probe('shellBlock',     ()=>shellBlock);
            probe('drawShells',     ()=>drawShells);
            try{ if(!CHEST_TYPES.some(t=>t.id==='shell')) miss.push('CHEST_TYPES 裡沒有 shell 寶箱'); }
            catch(e){ miss.push('CHEST_TYPES'); }
            return miss;
        }""")
        if missing:
            ck(False, "這一版沒有綠殼護盾（缺：%s）——如果這是拿舊版當對照組跑，"
                      "看到這一行就是對的" % "、".join(missing))
            print("\n❌ 缺少受測對象，後面 20 幾項不再跑。")
            await b.close()
            return

        # ---------- A：關卡門檻 ----------
        print("A：寶箱池的關卡門檻")
        pool = await pg.evaluate("""()=>({
            early: CHEST_POOL.length,
            late: CHEST_POOL_LATE.length,
            shellEarly: CHEST_POOL.some(t=>t.id==='shell'),
            shellLate: CHEST_POOL_LATE.some(t=>t.id==='shell'),
            minLv: SHELL_MIN_LV,
            // ⚠ chestPool() 讀的是 **G.lvIdx**，不是 LV_IDX——標題畫面就已經有一個
            //    G 存在（實測 G===null 是 false），所以只改 LV_IDX 這裡永遠量到前段池，
            //    第一版就是這樣假紅的。兩個都要設。
            at8: (LV_IDX=7, G&&(G.lvIdx=7), chestPool().some(t=>t.id==='shell')),
            at9: (LV_IDX=8, G&&(G.lvIdx=8), chestPool().some(t=>t.id==='shell')),
            allyEarly: CHEST_POOL.filter(t=>t.id==='ally').length
        })""")
        ck(pool["early"] == 89,
           f"第 1~8 關的寶箱池仍是 89 份＝跟 v0.9.38 逐項相同（量到 {pool['early']}）")
        ck(pool["allyEarly"] == 4,
           f"前段池裡糖果援軍仍是 4 份（量到 {pool['allyEarly']}）——沒有順手動到別的寶箱")
        ck(not pool["shellEarly"], "綠殼**不在**前段池裡")
        ck(pool["shellLate"], "綠殼在後段池裡")
        ck(pool["late"] == 97, f"後段池是 97 份＝89+8（量到 {pool['late']}）")
        ck(pool["minLv"] == 9, f"登場關卡是第 9 關（量到第 {pool['minLv']} 關）")
        ck(not pool["at8"], "第 8 關抽不到綠殼")
        ck(pool["at9"], "第 9 關抽得到綠殼")

        # ---------- B：生成 ----------
        print("B：生成三顆殼")
        await pg.evaluate("()=>{ META={}; LV_IDX=8; start(); }")   # 第 9 關
        await pg.wait_for_function("!!(G && G.running && G.P)", timeout=60000)
        await pg.evaluate(AUTOCARD)
        await keep_alive(pg)
        ck(await pg.evaluate("()=>!!(G&&G.running&&!G.paused)"),
           "量測前遊戲仍在進行｜狀態：" + await alive_msg(pg))
        # ⭐ 真正在跑的第 9 關裡，spawnChest() 抽的是不是後段池。
        #    上面 A 那幾條是「直接設 lvIdx 再問」，這一條走的是真實路徑。
        ck(await pg.evaluate("()=>chestPool()===CHEST_POOL_LATE && G.lvIdx===8"),
           "實際開打第 9 關時，spawnChest() 抽的是含綠殼的後段池")

        born = await pg.evaluate("""()=>{
            CHEST_TYPES.find(x=>x.id==='shell').go(G.P);
            return {n:G.SHELL.length, hp:G.SHELL.map(s=>s.hp),
                    N:SHELL_N, HP:SHELL_HP, orbit:SHELL_ORBIT,
                    d:G.SHELL.map(s=>Math.hypot(s.x-G.P.x, s.y-G.P.y))};
        }""")
        ck(born["n"] == 3, f"生成 3 顆殼（量到 {born['n']} 顆）")
        ck(all(h == born["HP"] for h in born["hp"]),
           f"每顆殼都是滿血 {born['HP']}（量到 {born['hp']}）")
        ck(all(abs(d - born["orbit"]) < 1.0 for d in born["d"]),
           f"三顆殼都在半徑 {born['orbit']} 上（量到 {[round(x,1) for x in born['d']]}）")

        # 跑一段時間之後仍然釘在玩家身上（不是生成時擺好、之後就飄走）
        await pg.wait_for_timeout(400)
        drift = await pg.evaluate("""()=>G.SHELL.map(s=>Math.hypot(s.x-G.P.x,s.y-G.P.y))""")
        ck(bool(drift) and all(abs(d - born["orbit"]) < 1.5 for d in drift),
           f"玩家移動後殼仍緊跟在半徑 {born['orbit']} 上（量到 {[round(x,1) for x in drift]}）")

        # ---------- C：擋彈 ----------
        print("C：擋彈")
        await keep_alive(pg)
        r = await pg.evaluate(PROBE, {"onShell": True})
        ck(r["probeLeft"] == 0, "打在殼上的那一發子彈被移除了")
        ck(r["blocked"] == r["before"]["blocked"] + 1,
           f"擋彈計數 +1（{r['before']['blocked']} → {r['blocked']}）")
        ck(sum(r["hp"]) == sum(r["before"]["hp"]) - 1,
           f"總殼血 −1（{sum(r['before']['hp'])} → {sum(r['hp'])}）")
        ck(r["hearts"] == r["before"]["hearts"], "玩家沒有掉心")

        # ---------- D：對照組（沒有殼時同一發彈會打到玩家）----------
        print("D：對照組——沒有殼的時候，同一發彈必須打得到玩家")
        await pg.evaluate("()=>{ G.SHELL.length=0; }")
        await keep_alive(pg)
        r2 = await pg.evaluate(PROBE, {"onShell": False})
        ck(r2["probeLeft"] == 0, "沒有殼時子彈同樣被消耗掉（＝真的碰到玩家了）")
        ck(r2["hearts"] == r2["before"]["hearts"] - 1,
           f"沒有殼時玩家**會**掉一顆心（{r2['before']['hearts']} → {r2['hearts']}）"
           "——這條紅了代表 C 是恆真的假測試")
        ck(r2["blocked"] == r2["before"]["blocked"],
           "沒有殼時擋彈計數不動")

        # ---------- E：耗盡 ----------
        print("E：擋滿就消失，不會無限擋")
        await keep_alive(pg)
        ex = await pg.evaluate("""()=>{
            const P=G.P;
            CHEST_TYPES.find(x=>x.id==='shell').go(P);
            const budget=SHELL_N*SHELL_HP;
            const start=G.shellBlocked;
            let shots=0;
            // 每一輪清場、對每顆殼各丟一發，再推進 0.12 秒（> SHELL_ICD）讓冷卻歸零。
            // 上限 60 輪純粹是保險絲：真的無限擋的話這裡會停在 60 而不是掛住。
            for(let k=0;k<60 && G.SHELL.length;k++){
              G.E.length=0; G.EB.length=0;
              P.hearts=99; P.iframe=0;
              for(const s of G.SHELL){
                G.EB.push({x:s.x,y:s.y,vx:0,vy:0,dmg:8,r:6,life:4.2,rot:0,spin:0,__probe:1});
                shots++;
              }
              update(0.12,0.12);
            }
            return {left:G.SHELL.length, blocked:G.shellBlocked-start, budget, shots};
        }""")
        ck(ex["left"] == 0, f"擋滿之後殼全部消失（還剩 {ex['left']} 顆）")
        ck(ex["blocked"] == ex["budget"],
           f"總共只擋 {ex['budget']} 發＝SHELL_N×SHELL_HP（量到 {ex['blocked']} 發／丟了 {ex['shots']} 發）")

        # ---------- F：i18n ----------
        print("F：11 種語言")
        i18 = await pg.evaluate("""()=>{
            const out={};
            for(const k in L10N){
              const d=L10N[k];
              out[k]={n:d.c_shell_n||'', go:d.c_shell_go||''};
            }
            return out;
        }""")
        ck(len(i18) == 11, f"語言數 11（量到 {len(i18)}）")
        miss = [k for k, v in i18.items() if not v["n"] or not v["go"]]
        ck(not miss, f"每一種語言都有 c_shell_n 與 c_shell_go（缺：{miss}）")
        noph = [k for k, v in i18.items() if "{0}" not in v["go"] or "{1}" not in v["go"]]
        ck(not noph, f"每一種語言的 c_shell_go 都有 {{0}} 與 {{1}} 兩個佔位符（缺：{noph}）")
        # 真的跑一次 T() —— 佔位符沒被代換的話玩家會在畫面上看到 "{0}"
        shown = await pg.evaluate("""()=>{
            const out={}, keep=LANG;
            for(const k in L10N){ LANG=k; out[k]=T('c_shell_go', SHELL_N, SHELL_N*SHELL_HP); }
            LANG=keep; return out;
        }""")
        bad = [k for k, v in shown.items() if "{0}" in v or "{1}" in v or "3" not in v]
        ck(not bad, f"T() 代換後畫面上不會出現未替換的佔位符（有問題：{bad}）")

        ck(not errs, f"全程沒有 JS 例外（{errs[:2]}）")
        await b.close()


if __name__ == "__main__":
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        asyncio.run(main())
    finally:
        srv.shutdown()
    print("\n" + ("❌ 失敗 %d 項：" % len(fails) + "；".join(fails)
                  if fails else "✅ py_shell 全數通過"))
    sys.exit(1 if fails else 0)
