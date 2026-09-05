#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🍬 軟糖再生（regen）的每關回血上限 —— v0.9.33 新增。

為什麼要有這支測試：
  v0.9.32 之前這張卡**完全沒有上限**。愛心上限固定 3 顆，中後期關卡長
  140~240 秒，Lv.2（每 25 秒）等於整關白拿 5~9 顆愛心 = 實際血量翻 2~3 倍。
  整套測試沒有任何一支檢查過回血次數，所以這個平衡漏洞從 v0.9.6
  （愛心上限固定成 3 顆那一版）之後就一直存在。

驗收標準（全部驅動真的遊戲迴圈，不是讀原始碼）：
  1. Lv.1 整關最多回 2 顆、Lv.2 最多 4 顆
  2. **滿血時空轉不能扣扣打**——滿血狀態下讓計時器跑很多輪，之後受傷了
     仍然要能回滿 cap 顆（否則會變成「越會閃的人懲罰越重」）
  3. 上限是「每關」：重開一關之後扣打要歸零
  4. 沒拿這張卡（regen=0）時完全不會回血
  5. 過程中不能有 JS 錯誤

⚠ 測試手法：直接推進遊戲的 update() 迴圈（`step()`），不是用 wait_for_timeout
  等真實時間——240 秒的關卡不可能真的等（AGENTS.md 第 3 節第 1 條）。
  同時 `G.P.crit=0`、不生怪，確保餵進去的輸入完全確定、沒有機率成分
  （第 3 節第 9 條）。

用法：python3 tests/py_regen_cap.py
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8801


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


# 在一個「乾淨的實驗室」裡跑：不生怪、不爆擊、玩家不會被打，
# 只手動控制愛心與時間推進，把 regen 這一條路徑單獨隔離出來。
SETUP = """
([lvIdx, regenLv]) => {
  window.__errs = [];
  window.onerror = (m) => window.__errs.push(String(m));
  META = {}; LV_IDX = lvIdx; start();
  G.paused = false;
  G.P.crit = 0;
  G.P.regen = regenLv;
  G.P.regenT = 0;
  G.P.regenN = 0;
  // 停止生怪，確保沒有任何外力改動愛心。
  // ⚠ 不能把 G.waves 清成空陣列——updateSpawn() 會去讀 w.rate，
  //    空陣列會噴 "Cannot read properties of undefined"。改成把每一波的
  //    生怪速率歸零、敵人上限歸零，效果一樣但不破壞資料結構。
  G.E.length = 0; G.EB.length = 0;
  for (const w of G.waves) w.rate = 0;
  G.L.maxE = 0;
  G.bosses = []; G.bossDone = [];
  return { hearts: G.P.hearts, maxHearts: G.P.maxHearts, waves: G.waves.length };
}
"""

# 推進 n 秒的遊戲時間。用固定 dt=1/60 一格一格餵，避免單次超大 dt
# 讓 regenT 一次跨過好幾個間隔（那不是真實遊玩會發生的情況）。
STEP = """
(secs) => {
  const dt = 1/60;
  for (let i = 0; i < Math.round(secs * 60); i++) update(dt, dt);
  return { hearts: G.P.hearts, regenN: G.P.regenN, errs: window.__errs.slice() };
}
"""

SET_HEARTS = "(h) => { G.P.hearts = h; return G.P.hearts; }"

# ⚠ 關鍵：愛心上限是 3，所以「掉到 1 顆之後一路跑到底」最多只可能回 2 顆——
#    那是撞到愛心上限，不是撞到 regen 的次數上限，用那種跑法永遠測不到 cap=4。
#    真實玩家是「被打→回血→又被打→again」，所以這裡每一輪都先把愛心壓回 1，
#    確保永遠有回血空間，這樣 regenN 停在哪裡才真的反映次數上限。
DRAIN_AND_RUN = """
([secs, rounds]) => {
  const dt = 1/60;
  for (let r = 0; r < rounds; r++) {
    G.P.hearts = 1;                       // 模擬又被打掉兩顆
    for (let i = 0; i < Math.round(secs * 60); i++) update(dt, dt);
  }
  return { hearts: G.P.hearts, regenN: G.P.regenN, errs: window.__errs.slice() };
}
"""


def main():
    httpd, port = serve()
    fails = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 420, "height": 820})
            pg.goto(f"http://127.0.0.1:{port}/index.html")
            pg.wait_for_function("typeof update === 'function'", timeout=15000)

            # ── 1. 上限本身：Lv.1 = 2 顆、Lv.2 = 4 顆 ──────────────────
            for regen_lv, cap, iv in ((1, 2, 40), (2, 4, 25)):
                pg.evaluate(SETUP, [0, regen_lv])
                # 跑「上限 + 3」輪，每輪都先被打回 1 顆愛心 → 永遠有回血空間
                r = pg.evaluate(DRAIN_AND_RUN, [iv + 1, cap + 3])
                got = r["regenN"]
                print(f"  Lv.{regen_lv}：{cap+3} 輪（每輪 {iv+1}s、每輪先被打回 1 顆）"
                      f"→ 實際回 {got} 顆（上限 {cap}）")
                if got != cap:
                    fails.append(f"Lv.{regen_lv}：回了 {got} 顆，應該剛好卡在上限 {cap}")
                if r["errs"]:
                    fails.append(f"Lv.{regen_lv}：JS 錯誤 {r['errs']}")

            # ── 2. 滿血空轉不能扣扣打 ─────────────────────────────────
            pg.evaluate(SETUP, [0, 2])
            pg.evaluate(SET_HEARTS, 3)              # 滿血
            r = pg.evaluate(STEP, 25 * 6)           # 滿血狀態空轉 6 個週期
            if r["regenN"] != 0:
                fails.append(f"滿血空轉竟然扣了扣打（regenN={r['regenN']}）")
            print(f"  滿血空轉 150s → regenN={r['regenN']}（必須是 0）")
            r = pg.evaluate(DRAIN_AND_RUN, [26, 7])  # 現在才開始被打
            print(f"  空轉後才受傷 → 回了 {r['regenN']} 顆（額度必須完整還在）")
            if r["regenN"] != 4:
                fails.append(f"滿血空轉後只回得了 {r['regenN']} 顆，應該還有完整的 4 顆額度")

            # ── 3. 上限是「每關」，重開要歸零 ─────────────────────────
            pg.evaluate(SETUP, [4, 2])              # 換第 5 關重開
            r = pg.evaluate(DRAIN_AND_RUN, [26, 7])
            print(f"  重開一關後 → 回了 {r['regenN']} 顆（額度必須重新給滿）")
            if r["regenN"] != 4:
                fails.append(f"重開一關後只回了 {r['regenN']} 顆，額度沒有歸零重給")

            # ── 4. 沒拿這張卡就完全不該回血 ───────────────────────────
            pg.evaluate(SETUP, [0, 0])
            pg.evaluate(SET_HEARTS, 1)
            r = pg.evaluate(STEP, 300)
            print(f"  沒拿卡跑 300s → 愛心 {r['hearts']}/3、regenN={r['regenN']}（都不該變）")
            if r["hearts"] != 1 or r["regenN"] != 0:
                fails.append(f"沒拿 regen 卻回血了（愛心 {r['hearts']}、regenN {r['regenN']}）")
            if r["errs"]:
                fails.append(f"JS 錯誤 {r['errs']}")

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_regen_cap 全過")


if __name__ == "__main__":
    main()
