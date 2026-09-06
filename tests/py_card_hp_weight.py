#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""升級卡池要依玩家血量調整權重 —— v0.9.36 新增。

為什麼要有這支測試：
  `rollCards()` 的後兩格原本是 `Math.floor(Math.random()*cp.length)`——
  **完全均勻亂抽，從來不看玩家狀態**。🔥 滿心怒氣（rage）的效果是
  「愛心全滿時傷害 +45%，被打掉就失效」，玩家掉血時抽到它等於白卡，
  而掉血正是最需要有用選項的時候。真人 2026-09-06 回報：
  非滿血連升兩級，兩次都出現這張卡。

驗收標準（機率性指標，門檻刻意放寬——AGENTS.md 第 3 節第 6 條）：
  1. 滿血時 rage 的出現率要「明顯高於」非滿血時
  2. 兩者比值落在 2~8 倍之間（設計值是 4 倍；抽樣雜訊不該讓它誤報）
  3. 非滿血時 rage **仍然抽得到**（是降權不是排除——愛心糖能補回滿血）
  4. v0.9.25 的保底沒被破壞：每一抽第一張一定是武器卡
  5. 一次抽出來的三張不能重複

⚠ 這支測試會抽好幾千次來壓低抽樣雜訊。門檻用「比值區間」而不是
  「精確機率」，因為精確門檻在機率性指標上必然週期性誤報。

用法：python3 tests/py_card_hp_weight.py
"""
import http.server, socketserver, threading, functools, sys, os
from playwright.sync_api import sync_playwright

# ⚠ 逾時刻意放到 60 秒：這些 wait_for_function 都是「輪詢到條件成立為止」，
#   機器閒置時毫秒級就回來，長逾時不會讓測試變慢。但 run_tests.sh 是 43 支
#   平行跑，開 43 個 Chromium 時光是把頁面載完就可能超過 15 秒——
#   短逾時在那個情境下必定假紅字（AGENTS.md 第 3 節第 1 條）。


ROOT = os.environ.get('GOO_ROOT', '/home/claude/goo/game')
PORT = 8807
N = 4000          # 每種狀態抽幾次


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


SAMPLE = """
([hearts, n]) => {
  META = {}; LV_IDX = 6; start();
  G.paused = true;
  const P = G.P;
  P.maxHearts = 3;
  P.hearts = hearts;
  let rage = 0, firstNotWeapon = 0, dup = 0, short3 = 0;
  for (let i = 0; i < n; i++) {
    const cards = rollCards();
    if (cards.length < 3) short3++;
    if (!cards[0] || !cards[0].w) firstNotWeapon++;
    const ids = cards.map(c => (c.evo ? 'evo:' : '') + (c.w || c.id));
    if (new Set(ids).size !== ids.length) dup++;
    if (cards.some(c => !c.w && c.id === 'rage')) rage++;
  }
  return { rage, firstNotWeapon, dup, short3, n };
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
            pg.wait_for_function("typeof rollCards === 'function'", timeout=60000)

            full = pg.evaluate(SAMPLE, [3, N])
            hurt = pg.evaluate(SAMPLE, [1, N])

            fr = full["rage"] / N
            hr = hurt["rage"] / N
            print(f"  滿血 3/3    → rage 出現 {full['rage']:>4}/{N}（{fr*100:.1f}%）")
            print(f"  非滿血 1/3  → rage 出現 {hurt['rage']:>4}/{N}（{hr*100:.1f}%）")

            if hurt["rage"] == 0:
                fails.append("非滿血時 rage 完全抽不到——應該是降權不是排除"
                             "（愛心糖／軟糖再生都能補回滿血，它不是廢卡）")
            elif hr >= fr:
                fails.append(f"非滿血的 rage 出現率沒有比較低（滿血 {fr*100:.1f}%／"
                             f"非滿血 {hr*100:.1f}%）")
            else:
                ratio = fr / hr
                print(f"  比值：滿血是非滿血的 {ratio:.2f} 倍（設計值 4，允收 2~8）")
                if not (2.0 <= ratio <= 8.0):
                    fails.append(f"降權幅度偏離設計值太多（{ratio:.2f} 倍，允收 2~8）")

            # 沒被這次改動破壞的既有行為
            for label, r in (("滿血", full), ("非滿血", hurt)):
                if r["firstNotWeapon"]:
                    fails.append(f"{label}：有 {r['firstNotWeapon']} 次第一張不是武器卡"
                                 "（v0.9.25 的保底被破壞了）")
                if r["dup"]:
                    fails.append(f"{label}：有 {r['dup']} 次抽出重複的卡")
                if r["short3"]:
                    fails.append(f"{label}：有 {r['short3']} 次抽不滿 3 張")

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_card_hp_weight 全過")


if __name__ == "__main__":
    main()
