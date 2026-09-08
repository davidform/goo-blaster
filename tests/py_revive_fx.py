#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🕯️ 重生蠟燭「復活演出」—— v0.9.37 新增（第 44 支）。

為什麼要有這支測試：
  復活這條路徑（`hurtPlayer()` 裡 `G.revives>0` 的那個分支）從 v0.9.17 上線到
  v0.9.36，**整套 43 支測試沒有任何一支走過它**——連「愛心歸零時有蠟燭就不會
  結束遊戲」這種最基本的行為都沒被釘住。v0.9.37 要在這條路徑上加演出，
  所以先把「機制」與「演出」兩件事一起釘死：

  A. 機制（這一版**逐字沒有動**，這裡是回歸防護網，不是新功能的驗收）
     1. 有蠟燭時愛心歸零 → 不結束遊戲、原地回滿血、次數 -1
     2. 無敵時間 3.2 秒、場上敵彈全部清空
     3. 沒有蠟燭時愛心歸零 → 正常結束遊戲，而且不能留下任何復活演出狀態
     4. 蠟燭用完之後再死一次 → 要真的死

  B. 演出（v0.9.37 新增的部分）
     5. 復活瞬間 reviveFlash=1、reviveT=無敵秒數、SHOCK 至少多 3 圈
     6. **光環跟無敵同進同出**：reviveT 與 P.iframe 走同一個 dt，
        推進遊戲迴圈之後兩者的差必須小於一格（1/60 秒）。
        ⚠ 這一條是這支測試最有價值的地方：reviveFlash 走真實時間、
        reviveT 走遊戲時間，兩者**故意不同**，很容易在之後某一版被
        「順手統一」而讓光環在慢動作時比無敵先消失，變成說謊的 UI。
     7. 慢動作（擦彈）時 reviveT 仍然跟 iframe 同步（上面那條的實戰版）
     8. 真的畫得出來：**畫面靜置收斂後**，只開/關 `G.reviveFlash` 這一個變因，
        四個角落的金色程度（R-B）必須跳 20 以上（讀真實畫素，不是讀原始碼）

⚠ 手法：全程用 `update(dt,dt)` 一格一格推進，不用 wait_for_timeout 等真實時間
   （AGENTS.md 第 3 節第 1 條）；同時關掉爆擊、停掉生怪，
   確保餵進去的輸入完全確定、沒有機率成分（第 3 節第 9 條）。

用法：python3 tests/py_revive_fx.py
"""
import http.server, socketserver, threading, functools, sys
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.sync_api import sync_playwright

ROOT = GAME_ROOT
PORT = 8880          # 起始埠；被佔用就往上找（43 支平行跑時一定會撞）


class _Server(socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    last = None
    for port in range(PORT, PORT + 20):
        try:
            httpd = _Server(("127.0.0.1", port), handler)
        except OSError as e:
            last = e
            continue
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return httpd, port
    raise last


# 乾淨的實驗室：不生怪、不爆擊，愛心與死亡完全由測試控制。
SETUP = """
(revives) => {
  window.__errs = [];
  window.onerror = (m) => window.__errs.push(String(m));
  META = {}; LV_IDX = 0; start();
  G.paused = false;
  G.P.crit = 0;
  G.revives = revives;
  G.E.length = 0; G.EB.length = 0;
  for (const w of G.waves) w.rate = 0;
  G.L.maxE = 0;
  G.bosses = []; G.bossDone = [];
  return { hearts: G.P.hearts, revives: G.revives, reviveT: G.reviveT };
}
"""

# 把玩家打到愛心歸零。iframe 歸零確保這一擊一定生效（受擊後有無敵時間）。
# 順手在場上放 12 顆假敵彈，才驗得到「復活會清空彈幕」。
KILL = """
() => {
  for (let i = 0; i < 12; i++) G.EB.push({x: 100 + i, y: 100, vx: 0, vy: 0, r: 6, dmg: 1});
  const before = { shock: G.SHOCK.length, eb: G.EB.length };
  G.P.hearts = 1; G.P.iframe = 0; G.P.shieldN = 0;
  const dead = hurtPlayer();
  return {
    dead, before,
    hearts: G.P.hearts, maxHearts: G.P.maxHearts, iframe: G.P.iframe,
    revives: G.revives, running: G.running, over: G.over,
    eb: G.EB.length, shock: G.SHOCK.length,
    reviveFlash: G.reviveFlash, reviveT: G.reviveT, reviveMax: G.reviveMax,
    errs: window.__errs.slice()
  };
}
"""

# ⚠⚠ 把畫面的 rAF 主迴圈**凍結**。這支測試對時間極度敏感（要比較 P.iframe 與
#   G.reviveT 這兩個秒數），而遊戲的 loop() 是靠 requestAnimationFrame 一直在背景
#   跑的——每一次 pg.evaluate() 之間流掉的真實時間，都會被 loop() 拿去推進遊戲。
#   機器閒置時每次呼叫只差幾十毫秒、看不出來；44 支平行跑時一次呼叫可能過了好幾秒，
#   3.2 秒的無敵在做畫素檢查之前就已經跑完了（實測負載下量到 iframe = -0.05）。
#   把 requestAnimationFrame 換成不排程的版本，loop() 最多再跑一幀就完全停住，
#   之後遊戲只在測試自己呼叫 update()／draw() 時前進——完全確定性
#   （AGENTS.md 第 3 節第 9 條：餵進去的東西每次都要一樣）。
FREEZE = "() => { window.requestAnimationFrame = () => 0; return true; }"
# 輪詢用：連續兩次讀到同一個 G.t 就代表 loop() 真的停了。
# ⚠ 這裡一定要用毫秒輪詢，不能用 Playwright 預設的 raf 輪詢——rAF 已經被我們關掉了。
STABLE = "() => { const a = G.t; const ok = (window.__prevT === a); window.__prevT = a; return ok; }"

# 推進 n 秒的遊戲時間（固定 dt，不用真實時間）。slow=true 時模擬擦彈慢動作。
STEP = """
([secs, slow]) => {
  const dt = 1/60;
  for (let i = 0; i < Math.round(secs * 60); i++) {
    const scale = slow ? 0.32 : 1;
    if (slow) G.slowmo = 1;
    update(dt * scale, dt);
  }
  return { iframe: G.P.iframe, reviveT: G.reviveT, errs: window.__errs.slice() };
}
"""

# 讀真實畫素：畫一幀，量「畫面四個角落」的平均 R-B（偏金的程度）。
# ⚠ 為什麼是角落、不是整張畫面的平均：v0.9.36 本來就有金色粒子噴發與金色衝擊波，
#   整張平均的 R-B 在對照版也會跳 +67，用整張平均等於量不到新東西
#   （這支測試第一次寫出來時就踩到，對照版照樣「通過」）。
#   全螢幕閃光的定義就是**連離玩家最遠的角落都會變色**，粒子與衝擊波做不到這件事，
#   所以角落才是能分辨兩者的取樣點（AGENTS.md 第 3 節第 2 條：量測工具本身也要被驗證）。
# 把畫面「靜置」到收斂：清掉復活噴出來的粒子／衝擊波／飄字與受擊紅閃，
# 震動歸零，然後連畫 8 幀。
# ⚠ 為什麼需要這一步：畫面用的是半透明覆蓋的拖尾畫法，**光是連續呼叫 draw()
#   畫面就會一幀比一幀淡**（實測同一個遊戲狀態連畫 6 幀，角落 R-B 從 76 一路
#   掉到 32）。所以「畫兩幀相減」這種 A/B 在這個引擎上根本不成立，
#   一定要先讓畫面收斂到穩定值，再開/關單一變因量一幀。
SETTLE = """
() => {
  G.PT.length = 0; G.SHOCK.length = 0; G.TXT.length = 0;
  G.hurt = 0; G.reviveFlash = 0;
  G.cam.shake = 0; G.cam.x = 0; G.cam.y = 0;
  for (let i = 0; i < 8; i++) draw();
  return true;
}
"""

SET_FLASH = "(v) => { G.reviveFlash = v; return G.reviveFlash; }"

PIXEL = """
() => {
  G.cam.shake = 0; G.cam.x = 0; G.cam.y = 0;
  draw();
  const S = 70, W0 = cv.width, H0 = cv.height;
  const boxes = [[0,0],[W0-S,0],[0,H0-S],[W0-S,H0-S]];
  let r = 0, b = 0, n = 0;
  for (const [bx, by] of boxes) {
    const d = ctx.getImageData(bx, by, S, S).data;
    for (let i = 0; i < d.length; i += 4 * 7) { r += d[i]; b += d[i+2]; n++; }
  }
  return { rb: (r - b) / n };
}
"""



def main():
    httpd, port = serve()
    fails = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel=BROWSER_CHANNEL)
            pg = b.new_page(viewport={"width": 420, "height": 820})
            pg.goto(f"http://127.0.0.1:{port}/index.html")
            pg.wait_for_function("typeof update === 'function'", timeout=60000)

            # ── A. 機制：有蠟燭時復活（這一版沒動，純回歸防護）──────────
            pg.evaluate(SETUP, 2)
            pg.evaluate(FREEZE)
            pg.wait_for_function(STABLE, polling=100, timeout=60000)
            base = pg.evaluate(PIXEL)
            r = pg.evaluate(KILL)
            print(f"  復活：愛心 {r['hearts']}/{r['maxHearts']}、無敵 {r['iframe']}s、"
                  f"剩 {r['revives']} 次、敵彈 {r['before']['eb']}→{r['eb']}")
            if r["dead"] or not r["running"] or r["over"]:
                fails.append("有蠟燭卻結束了遊戲")
            if r["hearts"] != r["maxHearts"]:
                fails.append(f"復活沒有回滿血（{r['hearts']}/{r['maxHearts']}）")
            if abs(r["iframe"] - 3.2) > 1e-6:
                fails.append(f"復活無敵時間變成 {r['iframe']}，應該是 3.2")
            if r["revives"] != 1:
                fails.append(f"蠟燭次數沒有扣（剩 {r['revives']}，應該剩 1）")
            if r["eb"] != 0:
                fails.append(f"復活沒有清空敵彈（還剩 {r['eb']} 顆）")

            # ── B. 演出：狀態真的被設起來 ──────────────────────────────
            print(f"  演出：reviveFlash={r['reviveFlash']}、reviveT={r['reviveT']}、"
                  f"衝擊波 {r['before']['shock']}→{r['shock']} 圈")
            # ⚠ 欄位可能整個不存在（例如有人把 v0.9.37 的演出整段回退掉），
            #   那時 evaluate() 回來的是 None——先擋一次，才不會變成 TypeError
            #   崩在這裡、看不出真正的原因（AGENTS.md 第 3 節第 3 條）。
            if r["reviveT"] is None or r["reviveMax"] is None or r["reviveFlash"] is None:
                fails.append("復活演出的狀態欄位不存在（reviveFlash/reviveT/reviveMax）")
                r["reviveT"] = r["reviveMax"] = r["reviveFlash"] = 0
            if r["reviveFlash"] != 1:
                fails.append(f"reviveFlash 沒有被點亮（={r['reviveFlash']}）")
            if abs(r["reviveT"] - r["iframe"]) > 1e-6 or abs(r["reviveMax"] - 3.2) > 1e-6:
                fails.append(f"reviveT/reviveMax 沒有跟無敵秒數對齊"
                             f"（{r['reviveT']}/{r['reviveMax']} vs {r['iframe']}）")
            if r["shock"] - r["before"]["shock"] < 3:
                fails.append(f"衝擊波沒有加上去（{r['before']['shock']}→{r['shock']}）")
            if r["errs"]:
                fails.append(f"復活當下有 JS 錯誤 {r['errs']}")

            # ── B-8. 真的畫得出來：全螢幕金色閃光的「單一變因」A/B ─────
            # 先把畫面靜置到收斂（見 SETTLE 的註解），再開/關 G.reviveFlash 各畫一幀。
            # 兩幀之間**只有這一個變因**：粒子、衝擊波、飄字、震動都已經清乾淨，
            # 復活光環兩邊都在。所以差值就是「全螢幕閃光」一個人的貢獻，
            # 對照版（沒有這段程式碼）必定是 0，矇混不過去。
            # 取樣點是四個角落而不是整張畫面：全螢幕閃光的定義就是連離玩家最遠的
            # 角落都會變色，粒子與衝擊波做不到（AGENTS.md 第 3 節第 2 條）。
            pg.evaluate(SETTLE)
            off = pg.evaluate(PIXEL)
            off2 = pg.evaluate(PIXEL)
            pg.evaluate(SET_FLASH, 1)
            lit = pg.evaluate(PIXEL)
            print(f"  畫素（角落）：閃光關 R-B={off['rb']:.1f}（再畫一幀 {off2['rb']:.1f}，"
                  f"證明已收斂）→ 閃光開 {lit['rb']:.1f}，差 {lit['rb']-off2['rb']:.1f}")
            if abs(off["rb"] - off2["rb"]) > 3:
                fails.append(f"畫面沒有收斂，這個 A/B 不可信"
                             f"（連兩幀就差了 {abs(off['rb']-off2['rb']):.1f}）")
            if lit["rb"] - off2["rb"] < 20:
                fails.append(f"全螢幕金色閃光沒有畫出來"
                             f"（開/關只差 {lit['rb']-off2['rb']:.1f}）")

            # ── B-6. 光環與無敵同進同出（正常速度）─────────────────────
            r2 = pg.evaluate(STEP, [1.0, False])
            if r2["reviveT"] is None: r2["reviveT"] = -1
            print(f"  推進 1.0s：無敵剩 {r2['iframe']:.4f}s、光環剩 {r2['reviveT']:.4f}s")
            if abs(r2["iframe"] - r2["reviveT"]) > 1/60:
                fails.append(f"光環與無敵脫鉤（無敵 {r2['iframe']:.4f} vs 光環 {r2['reviveT']:.4f}）")

            # ── B-7. 慢動作（擦彈）時仍然同步 ─────────────────────────
            r3 = pg.evaluate(STEP, [1.0, True])
            if r3["reviveT"] is None: r3["reviveT"] = -1
            print(f"  慢動作 1.0s：無敵剩 {r3['iframe']:.4f}s、光環剩 {r3['reviveT']:.4f}s")
            if abs(r3["iframe"] - r3["reviveT"]) > 1/60:
                fails.append(f"慢動作時光環與無敵脫鉤"
                             f"（無敵 {r3['iframe']:.4f} vs 光環 {r3['reviveT']:.4f}）")
            if r3["errs"]:
                fails.append(f"推進過程有 JS 錯誤 {r3['errs']}")

            # ── A-4. 蠟燭用完之後要真的死 ─────────────────────────────
            r4 = pg.evaluate(KILL)              # 用掉最後一次（剩 1 → 0）
            r5 = pg.evaluate(KILL)              # 沒了，這次要死
            print(f"  用完蠟燭再死一次：dead={r5['dead']}、running={r5['running']}、"
                  f"reviveT={r5['reviveT']}")
            if r4["dead"]:
                fails.append("還剩 1 次蠟燭卻死了")
            if not r5["dead"] or r5["running"]:
                fails.append("蠟燭用完了卻沒有結束遊戲")
            # 真的死了就不該還留著「復活中」的殘值（狀態要自己收尾，
            # 不能靠 draw() 那一層的 live 判斷幫忙擋）
            if r5["reviveT"] or r5["reviveFlash"]:
                fails.append(f"死亡後還留著復活演出狀態"
                             f"（T={r5['reviveT']}、flash={r5['reviveFlash']}）")

            # ── A-3. 完全沒有蠟燭時，不能留下任何復活演出狀態 ──────────
            pg.evaluate(SETUP, 0)
            pg.evaluate(FREEZE)          # start() 之後迴圈會再被排一次，這裡要重新凍結
            pg.wait_for_function(STABLE, polling=100, timeout=60000)
            r6 = pg.evaluate(KILL)
            print(f"  零蠟燭：dead={r6['dead']}、reviveFlash={r6['reviveFlash']}、"
                  f"reviveT={r6['reviveT']}")
            if not r6["dead"]:
                fails.append("沒有蠟燭卻沒死")
            if r6["reviveFlash"] != 0 or r6["reviveT"] != 0:
                fails.append(f"沒有復活卻放了復活演出"
                             f"（flash={r6['reviveFlash']}、T={r6['reviveT']}）")
            if r6["errs"]:
                fails.append(f"JS 錯誤 {r6['errs']}")

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_revive_fx 全過")


if __name__ == "__main__":
    main()
