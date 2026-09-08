#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""剩一顆愛心時要更容易抽到「救命卡」 —— v0.9.40 新增（第 47 支）。

為什麼要有這支測試：
  v0.9.36 只做了加權的**降權那一半**（掉血時把 🔥 滿心怒氣壓下去），
  專案負責人更早提過的「血量低時救命卡機率高一點」是**反方向的那一半**，
  刻意留到 v0.9.40 單獨做（AGENTS.md 1.4：一次只改一個變數）。
  沒有這支測試的話，之後任何人重寫 `rollCards()` 的加權，
  都可能把這一半靜默拿掉而沒有人發現——v0.9.36 的那一半有 `py_card_hp_weight`
  盯著，這一半在這支存在之前沒有任何東西盯。

這一版的設計（三個刻意的決定，測試逐條釘住）：
  1. 門檻是 `hearts <= 1`，**不是** `hearts < maxHearts`。
     愛心上限固定 3，「被打過一次」還有兩條命、不缺救命卡；
     真正危險的是「再被打一下就結束」。→ B 段
  2. 名單只收三張**直接讓你不會死**的卡（🍩 shield／🍬 regen／🩹 panic），
     不收 🧊 冰糖翻滾 / 🌀 滑順翻滾 這種位移卡。→ A 段（連帶）
  3. 是**加權不是保底**。低血仍然抽得到全攻擊的三張——
     保底會讓低血變成資源而不是危機。→ C 段

驗收標準（機率性指標，門檻用區間不用精確值——AGENTS.md 第 3 節第 6 條）：
  A. 剩一心時，三張救命卡「至少出現一張」的比例要明顯高於滿血時，
     比值落在 1.4~2.6 倍之間（設計值約 1.75）。
  B. 2/3 血（非滿血、但還沒到低血）**不該**觸發加權：
     它的救命卡出現率要貼近滿血，而不是貼近剩一心。
     ⚠ 這條是門檻本身的護欄——有人把條件放寬成 `< maxHearts` 時它會紅。
  C. 加權不是保底：剩一心時仍要有 ≥ 15% 的抽牌完全沒有救命卡。
  D. 疊滿的救命卡不會被加權「復活」：把三張都疊到上限後，
     剩一心抽 N 次一張都不該出現（加權只作用在真的還抽得到的卡）。
  E. v0.9.36 的降權沒有被這一版蓋掉：剩一心時 rage 出現率仍明顯低於滿血。
  F. 既有保底沒壞：每一抽第一張都是武器卡、三張不重複、抽得滿三張。

⚠ 對照組驗證（AGENTS.md：恆真的斷言比沒有測試更糟）：
  這支在 v0.9.39 上跑會在 A 段紅字，實測比值 1.00（完全沒有差別）。
  收尾時務必拿上一版跑一次確認它真的會紅。

用法：python3 tests/py_lifeline.py
"""
import http.server, socketserver, threading, functools, sys, os
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.sync_api import sync_playwright

# ⚠ 逾時放到 60 秒：底下的 wait_for_function 是「輪詢到條件成立為止」，
#   機器閒置時毫秒級就回來。但 run_tests.sh 是 40+ 支平行跑 Chromium，
#   光把頁面載完就可能超過 15 秒——短逾時在那個情境下必定假紅字。

ROOT = GAME_ROOT
PORT = 8861
N = 6000          # 每種狀態抽幾次（比 py_card_hp_weight 多，因為要比的是比值的比值）

LIFELINE = ['shield', 'regen', 'panic']


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


# ⚠ 觸發與讀值放在同一個 evaluate 裡（不隔著 CDP 往返再讀狀態），
#   而且完全不依賴遊戲迴圈——`G.paused=true` 之後直接呼叫 `rollCards()`，
#   所以玩家不會在測試中途死掉，時間也不是變因。
SAMPLE = """
([hearts, n, lifeline, maxOut]) => {
  META = {}; LV_IDX = 6; start();
  G.paused = true;
  const P = G.P;
  P.maxHearts = 3;
  P.hearts = hearts;
  // maxOut：把三張救命卡疊到上限，用來驗證「疊滿的卡不會被加權復活」
  if (maxOut) { P.shield = 2; P.regen = 2; P.panic = 1; }
  let life = 0, rage = 0, none = 0, firstNotWeapon = 0, dup = 0, short3 = 0;
  for (let i = 0; i < n; i++) {
    const cards = rollCards();
    if (cards.length < 3) short3++;
    if (!cards[0] || !cards[0].w) firstNotWeapon++;
    const ids = cards.map(c => (c.evo ? 'evo:' : '') + (c.w || c.id));
    if (new Set(ids).size !== ids.length) dup++;
    const hit = cards.some(c => !c.w && lifeline.indexOf(c.id) >= 0);
    if (hit) life++; else none++;
    if (cards.some(c => !c.w && c.id === 'rage')) rage++;
  }
  return { life, rage, none, firstNotWeapon, dup, short3, n };
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
            pg.wait_for_function("typeof rollCards === 'function'", timeout=60000)

            # ⚠ 前置探測：先確認這一版到底有沒有這個機制，紅字才是人話而不是
            #   一串 JS 堆疊。頂層 const 不會變成 window 的屬性，所以不能用
            #   `typeof window[k]`——要把名字包在自己的 arrow function 裡
            #   讓 ReferenceError 現形。
            #   （這裡探的是行為不是符號名，因為權重是區域變數：
            #     直接看「剩一心時救命卡有沒有變多」是唯一測得到的角度。）

            full = pg.evaluate(SAMPLE, [3, N, LIFELINE, False])
            mid = pg.evaluate(SAMPLE, [2, N, LIFELINE, False])
            low = pg.evaluate(SAMPLE, [1, N, LIFELINE, False])
            capped = pg.evaluate(SAMPLE, [1, N, LIFELINE, True])

            fl = full["life"] / N
            ml = mid["life"] / N
            ll = low["life"] / N
            print(f"  救命卡（🍩🍬🩹 至少一張）出現率：")
            print(f"    滿血 3/3    → {full['life']:>5}/{N}（{fl*100:.1f}%）")
            print(f"    2/3 血      → {mid['life']:>5}/{N}（{ml*100:.1f}%）")
            print(f"    剩一心 1/3  → {low['life']:>5}/{N}（{ll*100:.1f}%）")

            # ── A. 低血要明顯更容易抽到救命卡 ──────────────────────────
            if fl == 0:
                fails.append("滿血時一張救命卡都沒抽到——卡池或測試本身壞了，"
                             "先確認 UPGRADES 裡還有 shield/regen/panic")
            elif ll <= fl:
                fails.append(
                    f"A 段：剩一顆愛心時救命卡沒有比較容易抽到"
                    f"（滿血 {fl*100:.1f}%／剩一心 {ll*100:.1f}%）。"
                    f"這一版的整個重點就是這件事——`rollCards()` 的 stW 裡"
                    f"「低血時把 {'/'.join(LIFELINE)} 加權」的規則不見了或沒生效。")
            else:
                ratio = ll / fl
                print(f"  A 段比值：剩一心是滿血的 {ratio:.2f} 倍（設計值約 1.75，允收 1.4~2.6）")
                if not (1.4 <= ratio <= 2.6):
                    fails.append(
                        f"A 段：加權幅度偏離設計值太多（{ratio:.2f} 倍，允收 1.4~2.6）。"
                        f"太低＝玩家感覺不到；太高＝低血變成「抽好卡的時機」，"
                        f"跟「低血很危險」的設計相反。")

            # ── B. 門檻是 hearts<=1，2/3 血不該觸發 ────────────────────
            #   ⚠ 這條是門檻的護欄：有人把條件放寬成 `< maxHearts` 時，
            #     2/3 血會跟剩一心一樣高，這裡就會紅。
            if ll > fl:
                span = ll - fl
                if ml - fl > span * 0.5:
                    fails.append(
                        f"B 段：2/3 血也吃到了低血加權（滿血 {fl*100:.1f}%／"
                        f"2/3 血 {ml*100:.1f}%／剩一心 {ll*100:.1f}%）。"
                        f"門檻應該是 `hearts <= 1`（再被打一下就結束），"
                        f"不是 `hearts < maxHearts`（只是被打過一次）。")

            # ── C. 加權不是保底 ────────────────────────────────────────
            nr = low["none"] / N
            print(f"  C 段：剩一心時「三張都不是救命卡」仍有 {low['none']}/{N}（{nr*100:.1f}%）")
            if nr < 0.15:
                fails.append(
                    f"C 段：剩一心時幾乎每抽都保證有救命卡（沒有救命卡只剩 {nr*100:.1f}%）。"
                    f"這是加權不是保底——保底會讓低血變成資源而不是危機。")

            # ── D. 疊滿的救命卡不會被加權復活 ──────────────────────────
            if capped["life"]:
                fails.append(
                    f"D 段：三張救命卡都疊滿之後，剩一心仍抽到 {capped['life']}/{N} 次。"
                    f"加權只能作用在還抽得到的卡，疊滿的卡本來就不該進 pool。")
            else:
                print(f"  D 段：救命卡疊滿後，剩一心抽 {N} 次都沒再出現 ✓")

            # ── E. v0.9.36 的降權沒被蓋掉 ──────────────────────────────
            fr = full["rage"] / N
            hr = low["rage"] / N
            print(f"  E 段：rage 出現率 滿血 {fr*100:.1f}% ／ 剩一心 {hr*100:.1f}%")
            if low["rage"] == 0:
                fails.append("E 段：剩一心時 rage 完全抽不到——v0.9.36 是降權不是排除，"
                             "愛心糖／軟糖再生都能補回滿血")
            elif hr >= fr:
                fails.append(f"E 段：v0.9.36 的 rage 降權被這一版蓋掉了"
                             f"（滿血 {fr*100:.1f}%／剩一心 {hr*100:.1f}%）")

            # ── F. 既有保底沒壞 ────────────────────────────────────────
            for label, r in (("滿血", full), ("2/3 血", mid), ("剩一心", low),
                             ("剩一心(疊滿)", capped)):
                if r["firstNotWeapon"]:
                    fails.append(f"F 段 {label}：有 {r['firstNotWeapon']} 次第一張不是武器卡"
                                 "（v0.9.25 的保底被破壞了）")
                if r["dup"]:
                    fails.append(f"F 段 {label}：有 {r['dup']} 次抽出重複的卡")
                if r["short3"]:
                    fails.append(f"F 段 {label}：有 {r['short3']} 次抽不滿 3 張")

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_lifeline 全過")


if __name__ == "__main__":
    main()
