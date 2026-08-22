#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.24：<html lang> 要跟著遊戲語言換（原本寫死 zh-Hant）+ 版權聲明存在。"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8815
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[]
def ck(n,c,e=""):
    print(("  PASS  " if c else "  FAIL  ")+n+(("  "+str(e)) if e else ""))
    if not c: fails.append(n)
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="zh-TW")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
    ck("預設 <html lang> = en", pg.evaluate("()=>document.documentElement.lang")=="en",
       pg.evaluate("()=>document.documentElement.lang"))
    for code in pg.evaluate("()=>LANGS.map(x=>x.c)"):
        got=pg.evaluate("(c)=>{ applyLanguage(c); return document.documentElement.lang; }",code)
        ck(f"切成 {code} 後 <html lang> = {code}", got==code, got)
    pg.evaluate("()=>applyLanguage('en')")
    src=pg.evaluate("()=>document.documentElement.outerHTML.length")
    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
import re
html=open("/home/claude/goo/game/index.html",encoding="utf-8").read()
ck("原始碼開頭有版權聲明", "All rights reserved" in html[:900], html[:60])
ck("版權聲明有中文版", "未經授權" in html[:900])
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails[:5]}"); sys.exit(1)
print("=== 全部通過 ===")
