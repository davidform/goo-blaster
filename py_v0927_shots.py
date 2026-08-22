#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.27 的 UI 截圖：糖果援軍的戰鬥畫面、demo 版銀河圖的付費鎖、解鎖面板。
（專案規則：UI 改動一定要看圖確認，不能只看程式碼。）"""
import http.server, socketserver, threading, functools, os, urllib.request
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8865
OUT="/home/claude/work/goo-blaster/store"
os.makedirs(OUT, exist_ok=True)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

def demo_route(route):
    body=urllib.request.urlopen(f"http://127.0.0.1:{PORT}/index.html").read().decode('utf-8')
    body=body.replace("const EDITION='full';","const EDITION='demo';",1)
    route.fulfill(status=200, content_type="text/html; charset=utf-8", body=body)

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page(demo=False, lang="en-US"):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale=lang)
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        if demo: pg.route(f"http://127.0.0.1:{PORT}/index.html", demo_route)
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
        return pg,c,errs

    # ── 1. 糖果援軍的戰鬥畫面 ──────────────────────────────
    pg,c,errs=page()
    pg.evaluate("""()=>{
        META={hearts:2,dmg:2,aspd:2,range:1,xp:1,pickup:1,dash:1,wep:2,coin:1};
        LV_IDX=19; start(); G.hasMoved=true; DIAG.touch=3;
        G.P.lv=16; G.P.wep={bubble:4,graffiti:3};
        for(let i=0;i<26;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.1);
        window.__k=setInterval(()=>{
            G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
            G.P.hearts=G.P.maxHearts; G.P.iframe=1; G.hasMoved=true; DIAG.touch=3;
            if(G.ALLY.length<3) CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
            for(const a of G.ALLY) a.life=99;
            if(G.E.length<24){ for(let i=0;i<8;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.1); }
        },200);
    }""")
    pg.wait_for_timeout(4000)
    pg.evaluate("()=>{ clearInterval(window.__k); G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false; }")
    pg.wait_for_timeout(250)
    n=pg.evaluate("()=>G.ALLY.length")
    pg.screenshot(path=f"{OUT}/v0927-ally.png")
    print(f"v0927-ally.png  同伴 {n} 個，JS 錯誤 {errs[:1]}")
    pg.close(); c.close()

    # ── 2. demo 版銀河圖：付費鎖的節點 ─────────────────────
    pg,c,errs=page(demo=True)
    pg.evaluate("()=>{ PROGRESS=50; SEL_IDX=12; renderStage(); }")
    pg.wait_for_timeout(400)
    pg.evaluate("""()=>{
        const w=document.getElementById('galaxyWrap');
        const el=document.querySelector('.gnode[data-k="15"]');
        if(el&&w) w.scrollTop=Math.max(0, el.offsetTop - w.clientHeight/2);
    }""")
    pg.wait_for_timeout(500)
    pg.screenshot(path=f"{OUT}/v0927-lockmap.png")
    print(f"v0927-lockmap.png  JS 錯誤 {errs[:1]}")

    # ── 3. 解鎖面板（英文 / 繁中）──────────────────────────
    for code,tag in [('en','en'),('zh-Hant','zh')]:
        pg.evaluate("""(code)=>{ applyLanguage(code); PREM_OWNED=false;
            PROGRESS=50; SEL_IDX=19; renderStage(); showLockBox(19); }""",code)
        pg.wait_for_timeout(400)
        pg.screenshot(path=f"{OUT}/v0927-lockbox-{tag}.png")
        print(f"v0927-lockbox-{tag}.png")
    pg.evaluate("()=>{ document.getElementById('lockBox').classList.add('hide'); applyLanguage('en'); }")

    # ── 4. demo 版通關第 15 關的結算畫面 ────────────────────
    pg.evaluate("""()=>{
        META={}; LV_IDX=14; start(); G.hasMoved=true; DIAG.touch=3;
        G.t=G.winT+1; G.kills=143; endGame(true);
    }""")
    pg.wait_for_timeout(2200)
    pg.screenshot(path=f"{OUT}/v0927-demoend.png")
    print(f"v0927-demoend.png  JS 錯誤 {errs[:1]}")
    assert not errs, errs
    pg.close(); c.close()
    b.close()
srv.shutdown()
print("完成")
