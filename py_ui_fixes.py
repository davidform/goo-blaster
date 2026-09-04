#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.18 四項使用者回報問題的自動驗收。

用真實的 CDP 觸控事件（Input.dispatchTouchEvent）而不是合成的 JS 事件，
才能真正驗證「多點觸控時按鈕有沒有反應」這種瀏覽器層級的行為。

1. 拖曳中要能按到加速鍵與核彈鍵
2. 右上角按鈕不能蓋住「果凍%/傷害+%/速度×」這些成長型數值
3. 糖果屋要能捲動
4. 關卡圖：第1關在最下方、最後一關在最上方；每5關一個背景色帶
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8777
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

def page(b):
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=c.new_page()
    errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(400)
    return pg, c, errs

fails=[]
def check(name, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+("  "+extra if extra else ""))
    if not cond: fails.append(name)

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

    # ---------- 1. 拖曳中按加速鍵 / 核彈鍵 ----------
    print("=== 問題1：按著螢幕滑動時，要能按到核彈與加速鍵 ===")
    pg,c,errs=page(b)
    cdp=c.new_cdp_session(pg)
    pg.evaluate("""()=>{ LV_IDX=0; start(); G.P.nukeHeld=true; G.P.dashCD=0;
        // ⚠ 這一節在高負載下會等上數十秒牆鐘。期間玩家可能被雜兵打死 →
        //   G.running 變 false → 核彈鍵被 drawHUD 藏起來 → 觸控打在空氣上。
        //   量的是「拖曳中能不能按到按鈕」，不是「能不能活著」，所以直接讓他不死。
        // 診斷確認過：高負載下這一節等到最後 G.running 已經是 false、按鈕被藏起來、
        // 觸控事件根本沒進到監聽器（touches=0）。所以要把「關卡會結束」的兩條路
        // 都堵掉：贏（時間到）跟輸（沒血）。只補血是不夠的。
        window.__alive=setInterval(()=>{
            if(!G) return;
            G.winT=1e9; G.t=0;                       // 時間到不了 → 不會通關
            G.P.hearts=G.P.maxHearts; G.P.iframe=1;  // 不會陣亡
            G.P.nukeHeld=true;
            // ⚠ 最後查出來的真兇：玩家在這 30 秒裡會一直升級 → showCards() → G.paused=true。
            //   doNuke() 第一行就是 if(G.paused) return，那一下點擊直接被吃掉。
            //   keep-alive 只是「事後把 paused 清掉」，補不回已經被丟掉的那次點擊。
            //   正解是讓它根本升不了級。
            G.P.xpNext=1e9; G.P.xp=0;
            G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
        },100);
    }""")
    # ⚠ #btnNuke / #btnPause 在 start() 當下仍是 .hide（display:none），要等 drawHUD
    # 跑過一幀才顯示；不等的話 getBoundingClientRect() 會回全 0，觸控打到 (0,0)。
    pg.wait_for_selector("#btnNuke:not(.hide)", timeout=60000)  # 33 支平行時掉幀，15s 不夠
    pg.wait_for_timeout(150)
    btn=pg.evaluate("()=>({x:BTN.x,y:BTN.y,r:BTN.r})")
    nuke=pg.evaluate("""()=>{const r=document.getElementById('btnNuke').getBoundingClientRect();
                          return {x:r.x+r.width/2,y:r.y+r.height/2};}""")

    # 第一根手指：在畫面中間開始拖曳（搖桿）
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart",
        "touchPoints":[{"x":195,"y":430,"id":1}]})
    for dy in range(0,40,8):
        cdp.send("Input.dispatchTouchEvent",{"type":"touchMove",
            "touchPoints":[{"x":195+dy,"y":430+dy,"id":1}]})
    pg.wait_for_timeout(120)
    joy=pg.evaluate("()=>({active:IN.active,mag:+IN.mag.toFixed(2)})")
    check("拖曳中搖桿有啟動", joy["active"] and joy["mag"]>0, str(joy))

    # 第二根手指：在拖曳的同時點加速鍵
    dashBefore=pg.evaluate("()=>G.P.dashCD")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart",
        "touchPoints":[{"x":195+32,"y":430+32,"id":1},{"x":btn["x"],"y":btn["y"],"id":2}]})
    pg.wait_for_timeout(120)
    dashAfter=pg.evaluate("()=>({cd:G.P.dashCD,dashT:G.P.dashT})")
    check("拖曳中按加速鍵有觸發衝刺", dashAfter["cd"]>dashBefore or dashAfter["dashT"]>0,
          f"按之前cd={dashBefore} 按之後={dashAfter}")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd",
        "touchPoints":[{"x":195+32,"y":430+32,"id":1}]})
    pg.wait_for_timeout(80)

    # 第二根手指點核彈鍵（DOM 按鈕，多點觸控下 click 可能不會被合成）
    pg.evaluate("()=>{ G.P.nukeHeld=true; }")
    pg.wait_for_timeout(80)
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart",
        "touchPoints":[{"x":195,"y":430,"id":1}]})
    for dy in range(0,30,10):
        cdp.send("Input.dispatchTouchEvent",{"type":"touchMove",
            "touchPoints":[{"x":195+dy,"y":430+dy,"id":1}]})
    # 診斷：這一項在高負載下連續失敗，猜了兩次原因都不對。裝一個監聽器把
    # 「事件到底有沒有進到按鈕」量出來——⚠ 必須裝在送觸控「之前」，
    # 裝在之後的話 touches 恆為 0，那個診斷等於什麼都沒量到（我第一版就是這樣）。
    dbg=pg.evaluate("""()=>{
        const el=document.getElementById('btnNuke');
        const r=el.getBoundingClientRect();
        window.__nukeTouch=0;
        // 事件真的有到（touches=1），但核彈沒炸 → 一定是 doNuke() 的四道 guard
        // 其中一道擋掉了。在 touchstart 當下把四個值都記下來，直接看是哪一道。
        // （這個監聽器是後註冊的，在 target 階段會排在 bindTapBtn 之後 →
        //   讀到的是 doNuke 執行「之後」的狀態，正好可以判斷它有沒有真的跑完。）
        window.__at=null; window.__at2=null; window.__maxFlash=0;
        // 決定性的量法：用 16ms 的 interval 記下 nukeFlash 的最大值。
        // 只要炸過一次就一定 >0，完全不受 Python 端輪詢節奏影響
        // （Python 每 150ms 問一次，閃光可能整段落在兩次詢問之間）。
        window.__fk=setInterval(()=>{ if(G&&G.nukeFlash>window.__maxFlash) window.__maxFlash=G.nukeFlash; },16);
        // 再掛一個「冒泡階段」的監聽器：它一定排在 bindTapBtn 的之後，
        // 所以讀到的是 doNuke() 執行完的狀態。跟上面 capture 的那個對照，
        // 就能分辨「doNuke 沒被呼叫」還是「被呼叫但被 guard 擋掉」。
        el.addEventListener('touchstart',()=>{
            window.__at2={running:!!(G&&G.running), paused:!!(G&&G.paused),
                          held:!!(G&&G.P.nukeHeld), flash:G?+G.nukeFlash.toFixed(3):null};
        },{capture:false});
        el.addEventListener('touchstart',()=>{ window.__nukeTouch++;
            window.__at={running:!!(G&&G.running), paused:!!(G&&G.paused),
                         held:!!(G&&G.P.nukeHeld), flash:G?+G.nukeFlash.toFixed(3):null};
        },{capture:true});
        return {hidden:el.classList.contains('hide'), rect:[r.x|0,r.y|0,r.width|0,r.height|0],
                running:!!(G&&G.running), held:G&&G.P.nukeHeld, inActive:IN.active};
    }""")
    # ⚠ 同步點，不是等待：第二根手指一定要在「第一根已經被遊戲收下」之後才送。
    #   高負載時頁面來不及處理，兩個 touchStart 擠在一起，核彈鍵那一下就掉了。
    #   靠 sleep 猜時間會偶發失敗——改成等遊戲自己說搖桿已經啟動。
    for _ in range(200):
        if pg.evaluate("()=>IN.active===true"): break
        pg.wait_for_timeout(100)
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart",
        "touchPoints":[{"x":195+20,"y":430+20,"id":1},{"x":nuke["x"],"y":nuke["y"],"id":3}]})
    # 固定睡 200ms 在高負載掉幀時，處理引爆的那一幀可能還沒跑到。改成輪詢。
    nk=None
    for _ in range(200):            # 最多等 30 秒牆鐘（37 支平行時掉幀很嚴重）
        pg.wait_for_timeout(150)
        nk=pg.evaluate("()=>({held:G.P.nukeHeld,flash:G.nukeFlash})")
        if nk["flash"]>0 or pg.evaluate("()=>window.__maxFlash>0"): break
    dbg2=pg.evaluate("""()=>{
        const el=document.getElementById('btnNuke');
        const r=el.getBoundingClientRect();
        return {hidden:el.classList.contains('hide'), rect:[r.x|0,r.y|0,r.width|0,r.height|0],
                running:!!(G&&G.running), touches:window.__nukeTouch,
                at:window.__at, at2:window.__at2, maxFlash:+window.__maxFlash.toFixed(3)};
    }""")
    pg.evaluate("()=>{ clearInterval(window.__fk); }")
    # 真相：核彈其實「每一次都有炸」——at2（doNuke 執行後的狀態）是 held:False、flash:1，
    # maxFlash 也一路都 >0。之前連續四次「失敗」全都是量法的錯：Python 每 150ms 問一次，
    # 爆炸閃光整段落在兩次詢問之間，而 keep-alive 又立刻把 nukeHeld 設回 true，
    # 把另一個訊號也蓋掉了。遊戲從頭到尾沒有問題，壞的是測試。
    ok = nk["flash"]>0 or dbg2["maxFlash"]>0
    check("拖曳中按核彈鍵有引爆（看 nukeFlash 的最大值，不是抽樣瞬間值）", ok,
          "" if ok else f"{nk}  送觸控前={dbg}  送觸控後={dbg2}  觸控目標座標={nuke}")
    pg.evaluate("()=>{ clearInterval(window.__alive); }")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
    check("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()

    # ---------- 2. 右上按鈕不蓋住成長數值 ----------
    print("\n=== 問題2：右上角按鈕不能蓋住成長型數值 ===")
    pg,c,errs=page(b)
    pg.evaluate("()=>{ LV_IDX=0; start(); }")
    pg.wait_for_timeout(300)
    geo=pg.evaluate("""()=>{
        const p=document.getElementById('btnPause').getBoundingClientRect();
        return {pauseTop:p.top,pauseBottom:p.bottom,
                muteBottom:(MUTE.y+MUTE.r),
                rightHudY:SAFE_TOP+112, safeTop:SAFE_TOP};
    }""")
    print(f"  暫停鍵佔 y {geo['pauseTop']:.0f}~{geo['pauseBottom']:.0f}，靜音鍵到 y {geo['muteBottom']:.0f}")
    print(f"  右側數值畫在 y {geo['rightHudY']:.0f}")
    check("成長數值在暫停鍵下方", geo["rightHudY"] > geo["pauseBottom"])
    check("成長數值在靜音鍵下方", geo["rightHudY"] > geo["muteBottom"])
    pg.close(); c.close()

    # ---------- 3. 糖果屋可捲動 ----------
    print("\n=== 問題3：糖果屋要能捲動 ===")
    pg,c,errs=page(b)
    r=pg.evaluate("""()=>{
        COINS=200; showShop();
        const el=document.getElementById('shopList');
        const cs=getComputedStyle(el);
        return {touchAction:cs.touchAction, overflowY:cs.overflowY,
                scrollH:el.scrollHeight, clientH:el.clientHeight};
    }""")
    print(f"  {r}")
    check("shopList 的 touch-action 允許直向捲動", r["touchAction"] in ("pan-y","pan-y pinch-zoom"), r["touchAction"])
    check("內容確實超出容器（有東西可捲）", r["scrollH"]>r["clientH"], f"{r['scrollH']}>{r['clientH']}")
    # 真的用觸控滑一下看 scrollTop 有沒有變
    cdp=c.new_cdp_session(pg)
    box=pg.evaluate("""()=>{const r=document.getElementById('shopList').getBoundingClientRect();
                         return {x:r.x+r.width/2,y:r.y+r.height/2};}""")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":box["x"],"y":box["y"],"id":1}]})
    for i in range(1,9):
        cdp.send("Input.dispatchTouchEvent",{"type":"touchMove",
            "touchPoints":[{"x":box["x"],"y":box["y"]-i*18,"id":1}]})
        pg.wait_for_timeout(16)
    cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
    pg.wait_for_timeout(400)
    st=pg.evaluate("()=>document.getElementById('shopList').scrollTop")
    check("實際觸控滑動後有捲動", st>0, f"scrollTop={st}")
    pg.close(); c.close()

    # ---------- 4. 關卡圖反轉 + 每5關背景 ----------
    print("\n=== 問題4：第1關在最下方、最後一關在最上方，每5關一個背景 ===")
    pg,c,errs=page(b)
    r=pg.evaluate("""()=>{
        PROGRESS=LEVELS.length+1; showMenu();
        const inner=document.getElementById('galaxyInner');
        const g=k=>{const e=inner.querySelector('.gnode[data-k="'+k+'"]');return e?parseFloat(e.style.top):null;};
        return {第1關y:g(0), 第2關y:g(1), 第25關y:g(24), 最終關y:g(LEVELS.length-1),
                內層高度:parseFloat(inner.style.height),
                背景帶數:inner.querySelectorAll('.gband').length,
                銜接線數:inner.querySelectorAll('.gbandline').length,
                節點數:inner.querySelectorAll('.gnode').length};
    }""")
    for k,v in r.items(): print(f"  {k}: {v}")
    check("第1關在最下方（y最大）", r["第1關y"]>r["最終關y"])
    check("最終關在最上方（y最小）", r["最終關y"]<r["第25關y"]<r["第1關y"])
    check("順序單調（第2關在第1關上方）", r["第2關y"]<r["第1關y"])
    nLv=r["節點數"]
    check("背景帶數＝總關數/5", r["背景帶數"]==-(-nLv//5), str(r["背景帶數"]))
    check("銜接線數＝帶數-1", r["銜接線數"]==r["背景帶數"]-1, str(r["銜接線數"]))
    check("所有節點都在（＝總關數）", r["節點數"]==50, str(r["節點數"]))
    # 進度為第1關時，畫面應該捲到最底部（第1關的位置）
    r2=pg.evaluate("""()=>{
        PROGRESS=1; SEL_IDX=0; showMenu();
        const w=document.getElementById('galaxyWrap');
        return new Promise(res=>requestAnimationFrame(()=>requestAnimationFrame(()=>
            res({scrollTop:w.scrollTop, max:w.scrollHeight-w.clientHeight}))));
    }""")
    print(f"  新玩家開啟選單: scrollTop={r2['scrollTop']:.0f} / 最大={r2['max']:.0f}")
    check("新玩家開選單時自動捲到底部（第1關）", r2["scrollTop"] > r2["max"]*0.8,
          f"{r2['scrollTop']:.0f}/{r2['max']:.0f}")
    check("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()
    b.close()

srv.shutdown()
print()
if fails:
    print("❌ 失敗項目："+", ".join(fails)); sys.exit(1)
print("=== 全部通過 ===")
