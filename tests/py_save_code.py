#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.29：存檔備份碼面板。

背景：itch.io 玩家回饋（真人審過我們的商店頁與程式，指出「單一 HTML 檔 + 零相依」
沒有解決網頁版本身的儲存持久性——玩家是在第三方 iframe 裡玩，Safari 的 ITP 之類
機制可能回收久沒造訪的網站的 localStorage）。v0.9.28 的 NATIVE_STORE 只解決包成
App 之後的持久性，網頁版仍然可能無聲遺失進度。這支測試驗證存檔備份碼這個「玩家
自救出口」：

  1. 主選單有備份碼按鈕，點開會顯示一段 GOO1- 開頭的碼
  2. 匯出的碼能正確匯入回同一個分頁（round-trip）
  3. 匯入「進度更高」的碼會把玩家救回來（這是這支功能存在的唯一理由）
  4. 匯入「進度更低」的碼不會讓玩家倒退（pickBetterSave 的保證要延續到這裡）
  5. 格式錯誤 / checksum 對不上的碼要顯示錯誤，不能讓遊戲當掉或誤把壞資料寫進存檔
  6. 面板文字要跟著語言切換（不能有寫死的英文殘留在某個語言模式下）
"""
import http.server, socketserver, threading, functools, sys, json, os
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.sync_api import sync_playwright

ROOT = GAME_ROOT; PORT=8873
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

# v0.9.37：把「載入後固定 sleep 800ms」換成輪詢。
# 這支測試在 44 支平行跑時連續兩輪紅字（Page.click("#btnCode") 逾時 60 秒，
# 而且單獨跑一定是綠的）——根因就是 AGENTS.md 第 3 節第 1 條講的那件事：
# 45 個 Chromium 同時開起來，光把頁面載到「按鈕存在且腳本跑完」就不只 800ms，
# 固定 sleep 一過期，後面每一步都在對還沒準備好的頁面操作。
# 正確處置是改成輪詢到條件成立，不是把逾時調長（那只會讓紅字晚一點出現）。
def ready(pg):
    pg.wait_for_function(
        "() => typeof saveCodeDecode === 'function' && !!document.getElementById('btnCode')",
        timeout=60000)


with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL, args=["--autoplay-policy=no-user-gesture-required"])
    def page(locale="en-US"):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale=locale)
        pg=c.new_page(); pg.set_default_timeout(60000)
        errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        ready(pg)
        return pg,c,errs

    # ═══ 1. 按鈕存在、點開會出現合法格式的碼 ═══
    print("=== 1. 開啟面板、匯出碼格式 ===")
    pg,c,errs=page()
    pg.evaluate("()=>{ PROGRESS=9; COINS=456; META={dmg:2,hearts:1}; PREM_OWNED=false; saveGame(); }")
    pg.click("#btnCode")
    visible = pg.eval_on_selector("#codeBox", "el=>!el.classList.contains('hide')")
    ck("面板打開", visible)
    code = pg.eval_on_selector("#codeExportArea", "el=>el.value")
    print(f"  code={code}")
    fmt_ok = pg.evaluate("(c)=>{ const r=saveCodeDecode(c); return r.ok; }", code)
    ck("匯出的碼自己解得回來", fmt_ok)
    decoded = pg.evaluate("(c)=>saveCodeDecode(c).data", code)
    ck("內容跟目前狀態一致", decoded["progress"]==9 and decoded["coins"]==456 and decoded["meta"]=={"dmg":2,"hearts":1}, decoded)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 2. round-trip：匯出 → 清掉存檔 → 匯入 → 應該救回來 ═══
    print("\n=== 2. round-trip（模擬「進度不見了」的情境）===")
    pg,c,errs=page()
    pg.evaluate("()=>{ PROGRESS=23; COINS=999; META={wep:3,aspd:2}; PREM_OWNED=false; saveGame(); }")
    pg.click("#btnCode")
    code = pg.eval_on_selector("#codeExportArea", "el=>el.value")
    # 模擬「localStorage 被系統清掉」：直接清掉存檔、重新整理頁面（回到全新玩家狀態）
    pg.evaluate("()=>localStorage.clear()")
    pg.reload(); ready(pg)
    fresh = pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS)})")
    ck("重新整理後確實變成新玩家（前提條件）", fresh["p"]==1 and fresh["c"]==0, fresh)
    pg.click("#btnCode")
    pg.fill("#codeImportArea", code)
    pg.click("#btnCodeImport")
    restored = pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS),m:META})")
    ck("進度救回來了", restored["p"]==23 and restored["c"]==999 and restored["m"]=={"wep":3,"aspd":2}, restored)
    status_txt = pg.eval_on_selector("#codeStatus", "el=>el.textContent")
    ck("狀態列顯示成功訊息（不是空的）", bool(status_txt.strip()), status_txt)
    is_err = pg.eval_on_selector("#codeStatus", "el=>el.classList.contains('err')")
    ck("成功訊息不是錯誤樣式", not is_err)
    # 存檔也要確實寫回 localStorage（不是只活在記憶體裡，重整一次要還在）
    pg.reload(); ready(pg)
    persisted = pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS)})")
    ck("重整後持久化（不是只在記憶體裡）", persisted["p"]==23 and persisted["c"]==999, persisted)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 3. 匯入「進度較低」的碼不能讓玩家倒退（pickBetterSave 的保證）═══
    print("\n=== 3. 匯入舊碼不能倒退 ===")
    pg,c,errs=page()
    pg.evaluate("()=>{ PROGRESS=30; COINS=5000; PREM_OWNED=true; saveGame(); }")
    # 產生一段「進度很低」的舊碼（模擬玩家不小心貼到很久以前存的碼）
    old_code = pg.evaluate("()=>{ const cur={progress:PROGRESS,coins:COINS,meta:META,lang:LANG,v:SAVE_VER,prem:1}; PROGRESS=2; COINS=10; const c=saveCodeEncode(); PROGRESS=cur.progress; COINS=cur.coins; saveGame(); return c; }")
    pg.click("#btnCode")
    pg.fill("#codeImportArea", old_code)
    pg.click("#btnCodeImport")
    after = pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS),prem:PREM_OWNED})")
    ck("進度沒有倒退", after["p"]==30 and after["c"]==5000, after)
    ck("買斷狀態沒有被舊碼(沒買斷)蓋掉——OR 邏輯保留", after["prem"]==True, after)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 4. 壞碼要有清楚的錯誤、不能當掉、不能污染存檔 ═══
    print("\n=== 4. 壞掉的碼要顯示錯誤，不能悄悄接受 ===")
    pg,c,errs=page()
    pg.evaluate("()=>{ PROGRESS=5; COINS=100; saveGame(); }")
    bad_codes = ["", "not a code at all", "GOO1-XXXXXX-", "GOO1-XXXXXX-Ym9ndXM=", "GOO2-000000-"+"A"*20]
    for bc in bad_codes:
        pg.click("#btnCode")
        pg.fill("#codeImportArea", bc)
        pg.click("#btnCodeImport")
        st = pg.eval_on_selector("#codeStatus", "el=>el.classList.contains('err')")
        unchanged = pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS)})")
        ck(f"壞碼 {bc[:24]!r} 顯示錯誤且沒有動到存檔",
           st and unchanged["p"]==5 and unchanged["c"]==100, unchanged)
        pg.click("#btnCodeClose")
    # 手動改一個字元讓 checksum 對不上（模擬複製貼上漏字/貼壞）
    good = pg.evaluate("()=>saveCodeEncode()")
    tampered = good[:-3] + ("Z" if good[-1]!="Z" else "Y") + good[-2:]
    pg.click("#btnCode")
    pg.fill("#codeImportArea", tampered)
    pg.click("#btnCodeImport")
    st_err = pg.eval_on_selector("#codeStatus", "el=>el.classList.contains('err')")
    ck("checksum 對不上時也算壞碼", st_err)
    ck("無 JS 錯誤（壞輸入不能丟例外炸到主執行緒）", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 5. 語言切換：面板文字要跟著換，不能有寫死的英文殘留 ═══
    print("\n=== 5. 多語系：面板文字跟著切換 ===")
    pg,c,errs=page()
    pg.click("#btnCode")
    en_title = pg.eval_on_selector("#codeTitle", "el=>el.textContent")
    pg.click("#btnCodeClose")
    pg.evaluate("()=>{ applyLanguage('zh-Hant'); saveGame(); }")
    pg.click("#btnCode")
    zh_title = pg.eval_on_selector("#codeTitle", "el=>el.textContent")
    zh_btn_label = pg.eval_on_selector("#btnCodeImport", "el=>el.textContent")
    ck("標題跟著語言變了（不是還停在英文）", zh_title != en_title and "存檔" in zh_title, zh_title)
    ck("按鈕文字也跟著換了", zh_btn_label=="還原", zh_btn_label)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 6. 複製按鈕不能丟例外（clipboard API 在無權限環境常常會被拒絕）═══
    print("\n=== 6. 複製按鈕在 clipboard 權限被拒時不能當掉 ===")
    pg,c,errs=page()
    pg.evaluate("""()=>{
        // 模擬「Clipboard API 存在但被瀏覽器拒絕」的情境（itch.io iframe 常見）
        navigator.clipboard.writeText = () => Promise.reject(new Error('denied'));
    }""")
    pg.click("#btnCode")
    pg.click("#btnCodeCopy")
    # 同樣不要固定 sleep：輪詢到狀態列真的有字為止。
    # 包 try 是為了「功能真的壞掉」時仍然走到下面的 ck() 給出可讀的失敗訊息，
    # 而不是在這裡丟一個 Playwright 逾時例外、看不出是哪一條驗收沒過。
    try:
        pg.wait_for_function(
            "() => { const e = document.getElementById('codeStatus');"
            "        return !!e && e.textContent.trim().length > 0; }",
            timeout=30000)
    except Exception:
        pass
    status_txt = pg.eval_on_selector("#codeStatus", "el=>el.textContent")
    ck("被拒絕時仍然給出提示文字（不是靜默失敗）", bool(status_txt.strip()), status_txt)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    b.close()

srv.shutdown()
print()
if fails:
    print(f"❌ {len(fails)} 項失敗：")
    for f in fails: print("  -", f)
    sys.exit(1)
print("✅ 全部通過")
