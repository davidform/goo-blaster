#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試 v0.9.11 超級大 Boss 新增的「雷射鎖定攻擊」：
   1) 直接用 spawnBoss() 生一隻超級大 Boss，觀察 laserWarnT/laserFireT 是否會照週期觸發。
   2) 站在雷射線上 → 開火時應該掉血。
   3) 警示期間閃到雷射線外 → 開火時不應該掉血。
   4) 一般 Boss（非超級大）不應該觸發雷射邏輯（laserWarnT 應該一直是 0）。
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8773

socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT),
      functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

def new_page(pw_b):
    c = pw_b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2,
                          is_mobile=True, has_touch=True)
    pg = c.new_page()
    pg.goto(f"http://127.0.0.1:{PORT}/index.html")
    pg.wait_for_timeout(400)
    return pg

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

    print("=== 測試1: 超級大 Boss 雷射週期 (warn -> fire -> cooldown) ===")
    pg = new_page(b)
    pg.evaluate("""()=>{ LV_IDX=0; start();
        // 清空場上一般敵人與現有 boss，只留一隻超級大 Boss，方便觀察
        G.E.length=0; G.boss=null;
        spawnBoss({...BOSS_CHAPTER[9], superBoss:true, kind:'final', chIdx:9});  // v0.9.26：雷射只在第6章(第30關)以後，用最終章 Boss 測
        // 把 Boss 拉遠一點、玩家固定在原點，方便算距離；關掉既有的環形彈幕攻擊
        // (atkT 設超大值讓它永遠不會觸發)，這樣才能純粹觀察雷射攻擊自己的週期，
        // 不會被既有攻擊打死玩家、提前結束遊戲而中斷計時。
        G.boss.x=400; G.boss.y=0; G.P.x=0; G.P.y=0; G.boss.atkT=999; G.P.hearts=99;
    }""")
    # ⚠ 原本用 Python 每 100ms 取樣去數開火次數。高負載時遊戲時間嚴重落後牆鐘，
    #   22 秒牆鐘可能只跑出幾秒遊戲時間 → 週期數不夠 → 假失敗。
    #   把計數搬進頁面內的 setInterval，Python 只負責等條件成立。
    pg.evaluate("""()=>{
        window.__warn=false; window.__cycles=0; window.__prevFire=false;
        window.__k=setInterval(()=>{
            const b=G.boss; if(!b) return;
            if(b.laserWarnT>0) window.__warn=true;
            const firing=b.laserFireT>0;
            if(firing && !window.__prevFire) window.__cycles++;
            window.__prevFire=firing;
        },16);
    }""")
    for _ in range(600):                     # 最多等 60 秒牆鐘
        pg.wait_for_timeout(100)
        if pg.evaluate("()=>window.__cycles>=2"): break
    r2=pg.evaluate("()=>{ clearInterval(window.__k); return {w:window.__warn, c:window.__cycles}; }")
    seenWarn=r2["w"]; cycles=r2["c"]
    print(f"看到警示線出現: {seenWarn}, 看到開火階段出現次數: {cycles}")
    assert seenWarn, "FAIL: 從沒看到警示線 (laserWarnT 從沒 >0)"
    assert cycles>=2, f"FAIL: 開火次數太少 ({cycles})，週期可能沒有正確重置"
    print("PASS\\n")

    print("=== 測試2: 站在雷射線上，開火時應該掉血 ===")
    pg2 = new_page(b)
    pg2.evaluate("""()=>{ LV_IDX=0; start();
        G.E.length=0; G.boss=null;
        spawnBoss({...BOSS_CHAPTER[9], superBoss:true, kind:'final', chIdx:9});  // v0.9.26：雷射只在第6章(第30關)以後，用最終章 Boss 測
        G.boss.x=0; G.boss.y=0; G.P.x=300; G.P.y=0; G.P.iframe=0; G.P.hearts=3;
        G.boss.atkT=999; G.boss.laserCD=0.3; G.boss.laserWarnT=0; G.boss.laserFireT=0;
    }""")
    startHearts = pg2.evaluate("G.P.hearts")
    # ⚠ 原本用 Python 每 100ms 去重新擺位。33 支平行時掉幀，警示階段(0.68 秒遊戲時間)
    #   可能整段落在兩次輪詢之間 → 玩家從沒被擺到雷射線上 → 假失敗。
    #   改成把「跟著雷射線站」放進頁面內的 setInterval，Python 只負責等結果。
    pg2.evaluate("""()=>{
        window.__hitDuringFire=false;
        window.__k=setInterval(()=>{
            const b=G.boss; if(!b) return;
            if(b.laserWarnT>0){
                G.P.x = b.x + Math.cos(b.laserAng)*300;
                G.P.y = b.y + Math.sin(b.laserAng)*300;
            }
            if(b.laserFireT>0 && G.P.hearts<3) window.__hitDuringFire=true;
        },16);
    }""")
    for _ in range(120):                      # 最多等 12 秒牆鐘
        pg2.wait_for_timeout(100)
        if pg2.evaluate("()=>G.P.hearts")<startHearts: break
    hitDuringFire = pg2.evaluate("()=>{ clearInterval(window.__k); return window.__hitDuringFire; }")
    endHearts = pg2.evaluate("G.P.hearts")
    print(f"起始愛心 {startHearts} -> 結束愛心 {endHearts}, 開火中掉血: {hitDuringFire}")
    assert endHearts < startHearts, "FAIL: 站在雷射線上全程沒掉血"
    print("PASS\\n")

    print("=== 測試3: 警示期間閃開雷射線，開火時不應該掉血 ===")
    pg3 = new_page(b)
    pg3.evaluate("""()=>{ LV_IDX=0; start();
        G.E.length=0; G.boss=null;
        spawnBoss({...BOSS_CHAPTER[9], superBoss:true, kind:'final', chIdx:9});  // v0.9.26：雷射只在第6章(第30關)以後，用最終章 Boss 測
        G.boss.x=0; G.boss.y=0; G.P.x=300; G.P.y=0; G.P.iframe=0; G.P.hearts=3;
        G.boss.atkT=999; G.boss.laserCD=0.3; G.boss.laserWarnT=0; G.boss.laserFireT=0;
    }""")
    startHearts3 = pg3.evaluate("G.P.hearts")
    # 同測試2：閃避動作放進頁面內，才不會被 Python 的輪詢節奏漏掉
    pg3.evaluate("""()=>{
        window.__fired=0;
        window.__k=setInterval(()=>{
            const b=G.boss; if(!b) return;
            if(b.laserWarnT>0){
                const perp=b.laserAng+Math.PI/2;
                G.P.x = b.x + Math.cos(b.laserAng)*300 + Math.cos(perp)*200;
                G.P.y = b.y + Math.sin(b.laserAng)*300 + Math.sin(perp)*200;
            }
            if(b.laserFireT>0) window.__fired++;
        },16);
    }""")
    for _ in range(120):
        pg3.wait_for_timeout(100)
        if pg3.evaluate("()=>window.__fired")>0: break   # 至少要真的開火過才有意義
    fired3 = pg3.evaluate("()=>{ clearInterval(window.__k); return window.__fired; }")
    assert fired3>0, "FAIL: 整段沒觀察到雷射開火，這次測試不成立"
    endHearts3 = pg3.evaluate("G.P.hearts")
    print(f"起始愛心 {startHearts3} -> 結束愛心 {endHearts3}")
    assert endHearts3 == startHearts3, "FAIL: 明明閃開了雷射線卻還是掉血"
    print("PASS\\n")

    print("=== 測試4: 一般 Boss（非超級大）不應觸發雷射邏輯 ===")
    pg4 = new_page(b)
    pg4.evaluate("""()=>{ LV_IDX=0; start();
        G.E.length=0; G.boss=null;
        spawnBoss(BOSS_POOL[0]);   // 一般 Boss，superBoss 應該是 false
        G.boss.atkT=999; G.P.hearts=99;   // 關掉一般攻擊，純粹看雷射欄位有沒有被誤觸發
    }""")
    everWarned=False
    for i in range(50):  # 5s，遠超過 laserWarnT 的觸發週期(2.6~3.6s)，若邏輯有洩漏到一般Boss會被抓到
        pg4.wait_for_timeout(100)
        r = pg4.evaluate("""()=>({sb:G.boss?G.boss.superBoss:null,
                                    warnT:G.boss?G.boss.laserWarnT:0,
                                    fireT:G.boss?G.boss.laserFireT:0})""")
        if r["warnT"]>0 or r["fireT"]>0: everWarned=True
    print(f"一般 Boss superBoss={r['sb']}, 是否誤觸發雷射: {everWarned}")
    assert not everWarned, "FAIL: 一般 Boss 也觸發了雷射攻擊（應該只有超級大 Boss 才有）"
    print("PASS\\n")

    print("=== 測試5(v0.9.26): 第5關章節Boss（chIdx=0）不應發射雷射 ===")
    pg5 = new_page(b)
    pg5.evaluate("""()=>{ LV_IDX=4; start();
        G.E.length=0; G.boss=null;
        const sup=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
        spawnBoss(sup);
        G.boss.atkT=999; G.P.hearts=99;
    }""")
    ever5=False; info=None
    for i in range(50):
        pg5.wait_for_timeout(100)
        r = pg5.evaluate("""()=>({sb:G.boss?G.boss.superBoss:null, ci:G.boss?G.boss.chIdx:null,
                                    warnT:G.boss?G.boss.laserWarnT:0,
                                    fireT:G.boss?G.boss.laserFireT:0})""")
        info=r
        if r["warnT"]>0 or r["fireT"]>0: ever5=True
    print(f"第5關章節Boss superBoss={info['sb']} chIdx={info['ci']}, 是否發射雷射: {ever5}")
    assert info['sb'], "第5關應該是 superBoss（章節 Boss）"
    assert not ever5, "FAIL: 第5關章節Boss 仍會發射雷射（小朋友第一次遇到 Boss 就吃雷射）"
    print("PASS\\n")

    b.close()

print("=== 全部通過 ===")
srv.shutdown()
