#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""開機時「選取的關卡」要對齊玩家的最前線進度 —— v0.9.34 新增。

為什麼要有這支測試：
  `SEL_IDX`（銀河圖上目前選取/預覽的關卡）宣告是 `let SEL_IDX=0`，
  而唯一會把它設成 `PROGRESS-1` 的地方原本只有 `showMenu()`。
  但**開機路徑根本不會經過 showMenu()**——開機是直接 `applyLanguage()`
  → `renderStage()`。結果：玩家關掉遊戲再打開，存檔明明是好的
  （進度、糖果幣都在），主畫面卻永遠停在第 1 關、按鈕寫「重玩第一關」，
  要自己在銀河圖上一路點回去才能繼續玩。

  這個 bug **網頁版與 App 版都有**，而且從很早就存在。之所以沒被發現：
  網頁版玩家通常是「玩完一關回選單」（那條路徑有經過 showMenu()），
  很少真的把分頁關掉再重開。是 2026-09-05 真機測試才抓到的。

  更糟的是 App 重裝的情境：localStorage 是空的、進度在原生儲存裡，
  `hydrateFromNative()` 非同步讀完之後只呼叫 `renderStage()`，
  同樣沒有更新 `SEL_IDX`——玩家會看到「金幣還在但關卡回到第 1 關」，
  比完全沒存檔更令人困惑。

驗收標準：
  1. 純網頁：localStorage 有 progress=N 時，開機後 SEL_IDX == N-1
  2. 畫面上顯示的關卡編號也要是 N（不是只有變數對、畫面沒跟上）
  3. 邊界：progress=1（新玩家）→ SEL_IDX=0；progress 超過總關數 → 夾在最後一關
  4. **原生重裝情境**：localStorage 空、原生儲存有 progress=N
     → 非同步合併完成後 SEL_IDX 仍要變成 N-1

用法：python3 tests/py_boot_sel.py
"""
import http.server, socketserver, threading, functools, sys, json, time
from playwright.sync_api import sync_playwright

ROOT = __import__('os').environ.get('GOO_ROOT','/home/claude/goo/game')
PORT = 8803


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


# 假的 Capacitor Preferences（做法沿用 tests/py_native_store.py）。
# 用 window.name 當儲存體：它在同一個分頁的 reload 之間會存活，
# 剛好可以模擬「App 重裝後 localStorage 沒了、但原生儲存還在」。
FAKE_NATIVE = """
window.Capacitor = { Plugins: { Preferences: {
  get: async ({key}) => {
    let db = {};
    try { db = JSON.parse(window.name || '{}'); } catch(e) {}
    return { value: (key in db) ? db[key] : null };
  },
  set: async ({key, value}) => {
    let db = {};
    try { db = JSON.parse(window.name || '{}'); } catch(e) {}
    db[key] = value; window.name = JSON.stringify(db);
  },
  remove: async ({key}) => {
    let db = {};
    try { db = JSON.parse(window.name || '{}'); } catch(e) {}
    delete db[key]; window.name = JSON.stringify(db);
  }
}}};
"""

READ = """() => ({
  sel: (typeof SEL_IDX === 'undefined') ? null : SEL_IDX,
  progress: (typeof PROGRESS === 'undefined') ? null : PROGRESS,
  coins: (typeof COINS === 'undefined') ? null : COINS,
  total: LEVELS.length,
  shown: (document.querySelector('#stageInfo .st') || {}).textContent || '',
  coinTag: (document.getElementById('coinTag') || {}).textContent || ''
})"""


def save_payload(progress, coins=1234):
    return json.dumps({"progress": progress, "coins": coins, "meta": {},
                       "lang": "en", "v": 2, "prem": 0, "cn": 0})


def main():
    httpd, port = serve()
    url = f"http://127.0.0.1:{port}/index.html"
    fails = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()

            # ── 1~3. 純網頁：localStorage 有進度，冷開機 ──────────────
            print("── 純網頁冷開機（localStorage 有進度）──")
            ctx = b.new_context(viewport={"width": 420, "height": 820})
            pg = ctx.new_page()
            pg.goto(url)
            pg.wait_for_function("typeof SEL_IDX !== 'undefined'", timeout=15000)
            total = pg.evaluate("() => LEVELS.length")

            for prog in (8, 1, 2, total, total + 1):
                pg.evaluate("(v) => localStorage.setItem('gooblaster_save_v3', v)",
                            save_payload(prog))
                pg.reload()
                pg.wait_for_function("typeof SEL_IDX !== 'undefined'", timeout=15000)
                r = pg.evaluate(READ)
                want = max(0, min(prog - 1, total - 1))
                ok = r["sel"] == want
                print(f"   progress={prog:<3} → SEL_IDX={r['sel']:<3}（預期 {want}）"
                      f"　畫面「{r['shown'].strip()}」{'' if ok else '  ❌'}")
                if not ok:
                    fails.append(f"progress={prog}：SEL_IDX={r['sel']}，預期 {want}")
                # 畫面顯示的關卡編號也要跟上，不能只有變數對。
                # ⚠ 例外：全破（progress > 總關數）且選在最後一關時，renderStage()
                #    會刻意改顯示 ALL CLEAR 而不是「Stage 50 / 50」——那是正確行為，
                #    不是畫面沒跟上。（第一版測試沒考慮到，誤報過一次。）
                all_cleared = prog > total and want == total - 1
                if not all_cleared and str(want + 1) not in r["shown"]:
                    fails.append(f"progress={prog}：畫面沒顯示第 {want+1} 關（實際「{r['shown'].strip()}」）")
            ctx.close()

            # ── 4. App 重裝：localStorage 空、原生儲存有進度 ───────────
            print("── App 重裝情境（localStorage 空、原生儲存有 progress=8）──")
            ctx = b.new_context(viewport={"width": 420, "height": 820})
            pg = ctx.new_page()
            pg.add_init_script(FAKE_NATIVE)
            pg.goto(url)
            pg.wait_for_function("typeof SEL_IDX !== 'undefined'", timeout=15000)
            # 把進度只寫進「原生儲存」，然後清掉 localStorage 模擬重裝
            pg.evaluate("(v) => { let db={}; try{db=JSON.parse(window.name||'{}');}catch(e){}"
                        "  db['gooblaster_save_v3']=v; window.name=JSON.stringify(db);"
                        "  localStorage.clear(); }", save_payload(8, 4321))
            pg.reload()
            pg.wait_for_function("typeof SEL_IDX !== 'undefined'", timeout=15000)
            # 等非同步的原生合併跑完（輪詢，不用固定 sleep）
            try:
                pg.wait_for_function("() => PROGRESS === 8", timeout=10000)
            except Exception:
                pass
            r = pg.evaluate(READ)
            print(f"   PROGRESS={r['progress']}　SEL_IDX={r['sel']}（預期 7）"
                  f"　金幣顯示「{r['coinTag']}」　畫面「{r['shown'].strip()}」")
            if r["progress"] != 8:
                fails.append(f"原生存檔沒被讀進來（PROGRESS={r['progress']}）")
            elif r["sel"] != 7:
                fails.append(f"原生合併後 SEL_IDX={r['sel']}，預期 7"
                             "（金幣回來了但關卡停在第 1 關，正是使用者回報的現象）")
            if r["progress"] == 8 and "8" not in r["shown"]:
                fails.append(f"原生合併後畫面沒顯示第 8 關（實際「{r['shown'].strip()}」）")
            if r["progress"] == 8 and r["coinTag"].strip() not in ("4321",):
                fails.append(f"原生合併後金幣顯示沒更新（「{r['coinTag']}」，預期 4321）")
            ctx.close()

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_boot_sel 全過")


if __name__ == "__main__":
    main()
