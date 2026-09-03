#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""補三張 itch.io 商店頁截圖：升級卡選擇、糖果屋、Boss 戰。
（py_cover.py 已產生主選單與一般戰鬥兩張）"""
import http.server, socketserver, threading, functools, os
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8793
OUT="/home/claude/work/goo-blaster/store"
os.makedirs(OUT, exist_ok=True)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

def clean(pg):
    """把開場教學提示與『偵測不到觸控』警告消掉，不然截圖會有開發者訊息"""
    pg.evaluate("()=>{ G.hasMoved=true; DIAG.touch=DIAG.touch||3; }")

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page():
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
        return pg,errs

    # ── 1. 升級卡選擇畫面（roguelite 的核心鉤子，最該放在商店頁）
    pg,errs=page()
    pg.evaluate("""()=>{
        META={hearts:2,dmg:2,aspd:2,range:1,xp:1,pickup:1,dash:1,wep:2,coin:1};
        LV_IDX=24; start();
        G.P.lv=14; G.P.wep={bubble:4,graffiti:3,yoyo:3};
        for(let i=0;i<22;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.1);
    }""")
    pg.wait_for_timeout(900); clean(pg)
    pg.evaluate("()=>{ G.P.lv++; showCards(); }")
    pg.wait_for_timeout(700)
    pg.screenshot(path=f"{OUT}/shot-cards.png")
    assert not errs, errs
    print("shot-cards.png", pg.evaluate("()=>document.querySelectorAll('#cards .card').length"), "張卡")
    pg.close()

    # ── 2. 糖果屋（局外成長＝留存與未來付費的載體）
    pg,errs=page()
    pg.evaluate("""()=>{
        COINS=1840; META={hearts:2,dmg:3,aspd:1,xp:2,coin:1}; saveGame();
        showShop();
    }""")
    pg.wait_for_timeout(700)
    pg.evaluate("()=>{ const s=document.getElementById('shop'); if(s) s.scrollTop=0; }")
    pg.wait_for_timeout(300)
    pg.screenshot(path=f"{OUT}/shot-shop.png")
    assert not errs, errs
    print("shot-shop.png ok")
    pg.close()

    # ── 3. Boss 戰
    pg,errs=page()
    pg.evaluate("""()=>{
        META={hearts:3,dmg:3,aspd:3,range:2,xp:2,pickup:2,dash:1,wep:3,coin:2};
        LV_IDX=49; start();
        G.P.lv=22; G.P.wep={bubble:5,graffiti:4,yoyo:4};
    }""")
    pg.wait_for_timeout(600); clean(pg)
    r=pg.evaluate("""()=>{
        // ⚠ spawnBoss(cfg) 收的是「Boss 設定物件」不是索引；傳 0 進去會讓 cfg.name
        //   變成 undefined，畫面上的 Boss 名稱就會顯示 "undefined"（我第一次就踩到）。
        //   正確做法是拿這一關 buildBosses() 產生的設定。
        // v0.9.23：每章 5 關之後，cfgs[0] 是一般 Boss（Gumdrop Brute）。
        // 商店截圖要放最終章節 Boss（六種造型全開的 Omega, the Ender）才有說服力。
        const cfgs = G.bosses || buildBosses(CUR());
        spawnBoss(cfgs.filter(x=>x.superBoss)[0] || cfgs[cfgs.length-1]);
        // 升級卡面板會蓋掉整個畫面，直接把它停掉再拍
        window.__showCards = showCards; showCards = ()=>{ G.pendingCards=0; };
        return {bossName: G.boss && G.boss.name, bosses:G.E.filter(e=>e.boss).length};
    }""")
    print("boss 生成:", r)
    pg.evaluate("""()=>{
        window.__k=setInterval(()=>{
            G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
            G.P.hearts=G.P.maxHearts; G.hasMoved=true; DIAG.touch=DIAG.touch||3;
            const bs=G.E.filter(e=>e.boss); if(bs.length) bs.forEach(e=>{ if(e.hp<e.maxhp*0.45) e.hp=e.maxhp*0.62; });
            if(G.E.length<26){ for(let i=0;i<8;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.2); }
        },250);
    }""")
    pg.wait_for_timeout(6000)
    pg.evaluate("()=>{ clearInterval(window.__k); G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false; }")
    pg.wait_for_timeout(300)
    print("截圖前 boss 數:", pg.evaluate("()=>G.E.filter(e=>e.boss).length"))
    pg.screenshot(path=f"{OUT}/shot-boss.png")
    assert not errs, errs
    pg.close()
    b.close()
srv.shutdown()
print("完成")
