#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Boss 壓力曲線量測（診斷工具，不進 run_tests.sh 預設批次）。

起因：2026-09-05 使用者真機試玩回報「第 6 關之後難度變得太高，我玩到第 8 關，
也用糖果幣做了很多增強，依舊難以過關，尤其是 boss 發射的子彈又多又快又密集」。
在此之前 itch.io 玩家 CoderGenius72 也是玩到第 8 關卡住——**兩個獨立的人
撞到同一面牆**。

為什麼不用笨 bot 跑通關率：bot 在第 3 關左右就會陣亡，根本走不到第 6~8 關，
量不到那一段。所以改成量「**同一時間畫面上有多少顆敵方子彈**」這個
玩家真正在對抗的東西，直接對應使用者說的「又多又快又密集」。

量測方法（每一關都一樣，確定性）：
  1. 開該關，關掉雜兵生成（只留 Boss），避免雜兵干擾讀數
  2. 把時間直接推進到最後一隻 Boss 出場
  3. 固定推進 25 秒遊戲時間，每幀記錄 G.EB.length（敵方子彈數）
  4. 回報：峰值 / 平均 / 同時存活的 Boss 數 / Boss 總血量

⚠ 玩家不參與（不移動、不攻擊），所以這是「純火力輸出」的比較，
  不是通關難度本身。跨關卡比較才有意義，絕對值不要拿去對真機體感。

用法：python3 tests/py_boss_pressure.py [起始關] [結束關]
      預設 1~10
"""
import http.server, socketserver, threading, functools, sys, os
from playwright.sync_api import sync_playwright

ROOT = os.environ.get('GOO_ROOT', '/home/claude/goo/game')
PORT = 8805
LV_FROM = int(sys.argv[1]) if len(sys.argv) > 1 else 1
LV_TO = int(sys.argv[2]) if len(sys.argv) > 2 else 10


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


MEASURE = """
(lvIdx) => {
  META = {}; LV_IDX = lvIdx; start();
  G.paused = false;
  G.P.crit = 0;
  // 只留 Boss：關掉雜兵生成，清場
  for (const w of G.waves) w.rate = 0;
  G.L.maxE = 0;
  G.E.length = 0; G.EB.length = 0;

  const info = { name: G.L.n, dur: G.L.dur, nboss: G.bosses.length,
                 bossT: G.bosses.map(b => b.t),
                 bossHp: G.bosses.map(b => b.hp),
                 atkT: G.bosses.map(b => +b.atkT.toFixed(2)) };

  // 直接把時間推到最後一隻 Boss 出場的前一刻
  const last = G.bosses[G.bosses.length - 1].t;
  const dt = 1/60;
  G.t = Math.max(0, last - 1);
  // 先跑到所有 Boss 都出場
  for (let i = 0; i < 120; i++) update(dt, dt);

  // 玩家不動、不被打死：每幀把愛心補滿並清無敵，純粹量火力
  let peak = 0, sum = 0, n = 0, bossPeak = 0;
  for (let i = 0; i < Math.round(25 * 60); i++) {
    G.P.hearts = G.P.maxHearts;
    update(dt, dt);
    const b = G.EB.length;
    peak = Math.max(peak, b); sum += b; n++;
    bossPeak = Math.max(bossPeak, G.E.filter(e => e.boss).length);
  }
  return { ...info, peak, avg: +(sum / n).toFixed(1), bossPeak,
           totalBossHp: info.bossHp.reduce((a, b) => a + b, 0) };
}
"""


def main():
    httpd, port = serve()
    rows = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 420, "height": 820})
            pg.goto(f"http://127.0.0.1:{port}/index.html")
            pg.wait_for_function("typeof update === 'function'", timeout=15000)
            print(f"{'關':>3} {'名稱':<22} {'Boss數':>5} {'同時':>4} "
                  f"{'總血量':>8} {'攻擊間隔':>9} {'子彈峰值':>8} {'平均':>6}")
            print("-" * 78)
            for lv in range(LV_FROM - 1, LV_TO):
                r = pg.evaluate(MEASURE, lv)
                rows.append((lv + 1, r))
                print(f"{lv+1:>3} {r['name'][:20]:<22} {r['nboss']:>5} {r['bossPeak']:>4} "
                      f"{r['totalBossHp']:>8} {str(r['atkT']):>9} "
                      f"{r['peak']:>8} {r['avg']:>6}")
            b.close()
    finally:
        httpd.shutdown()

    # relative jump 分析：哪一關的壓力跳最兇
    print("\n每一關相對前一關的子彈峰值變化：")
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1][1]['peak'], rows[i][1]['peak']
        d = (cur - prev) / max(1, prev) * 100
        mark = '  ← 跳最兇' if d >= 50 else ''
        print(f"  第{rows[i-1][0]}關 {prev:>3} → 第{rows[i][0]}關 {cur:>3}   {d:+6.1f}%{mark}")


if __name__ == "__main__":
    main()
