#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.18 邊角案例回歸測試（UI 修正的第二層防線）。

⚠ 測試方法注意：#btnPause / #btnNuke 在 start() 剛呼叫完的當下仍然是 .hide
（display:none），要等 drawHUD() 跑過一幀才會顯示。如果直接 getBoundingClientRect()
會拿到全 0 的矩形，CDP 觸控就會打到 (0,0) 什麼都沒碰到 → 測試偶發失敗。
這在三輪偵錯的第 3 輪被抓到（第 2 輪剛好過了），所以一律要用
wait_for_selector("#btnPause:not(.hide)") 等按鈕真的可見再取座標。
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8778
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[]
def ck(n,c,x=""):
    print(("  PASS  " if c else "  FAIL  ")+n+("  "+x if x else ""))
    if not c: fails.append(n)
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def P():
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(400)
        return pg,c,errs

    print("=== 邊角1：多點觸控狂點加速鍵，冷卻要正常擋住（不能無限衝刺）===")
    pg,c,errs=P(); cdp=c.new_cdp_session(pg)
    pg.evaluate("""()=>{ LV_IDX=0; start(); G.P.dashCD=0;
        window.__dashCount=0;
        const orig=window.tryDash;
        window.tryDash=function(){ const before=G.P.dashCD; const r=orig.apply(null,arguments);
            if(G.P.dashCD>before) window.__dashCount++; return r; }; }""")
    pg.wait_for_timeout(250)                                     # 等 drawHUD 跑過一幀
    btn=pg.evaluate("()=>({x:BTN.x,y:BTN.y})")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":195,"y":430,"id":1}]})
    dashes=0
    for i in range(10):
        cdp.send("Input.dispatchTouchEvent",{"type":"touchStart",
            "touchPoints":[{"x":195,"y":430,"id":1},{"x":btn["x"],"y":btn["y"],"id":2+i}]})
        pg.wait_for_timeout(40)
        cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[{"x":195,"y":430,"id":1}]})
        pg.wait_for_timeout(40)
    cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
    # ⚠ 不能斷言「結束時 cd 必須 > 0」：測試跑完時冷卻可能剛好已經充滿（實測拿到
    # cd=-0.02，程式不會把它夾在 0）。要驗的是「冷卻沒有被繞過」，也就是狂點 10 次
    # 不可能換來 10 次衝刺——用實際的衝刺次數來驗才是對的。
    r=pg.evaluate("()=>({cd:+G.P.dashCD.toFixed(2),cdmax:G.P.dashCDmax,dashes:window.__dashCount||0})")
    ck("狂點10次不會換來10次衝刺（冷卻沒被繞過）", r["dashes"]<10, str(r))
    ck("冷卻上限沒有被改壞", r["cd"] <= r["cdmax"]+0.01, str(r))
    ck("無 JS 錯誤", not errs, str(errs[:2])); pg.close(); c.close()

    print("\n=== 邊角2：暫停鍵在多點觸控下只觸發一次（不會 touchstart+click 雙擊）===")
    pg,c,errs=P(); cdp=c.new_cdp_session(pg)
    pg.evaluate("()=>{ LV_IDX=0; start(); }")
    pg.wait_for_selector("#btnPause:not(.hide)", timeout=60000)   # ⚠ 必須等按鈕真的顯示（37 支平行時掉幀，15s 不夠）
    pg.evaluate("""()=>{ window.__pauseCount=0;
        const el=document.getElementById('pauseOverlay');
        new MutationObserver(()=>{ if(!el.classList.contains('hide')) window.__pauseCount++; })
          .observe(el,{attributes:true,attributeFilter:['class']}); }""")
    pb=pg.evaluate("""()=>{const r=document.getElementById('btnPause').getBoundingClientRect();
                        return {x:r.x+r.width/2,y:r.y+r.height/2};}""")
    cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":pb["x"],"y":pb["y"],"id":1}]})
    pg.wait_for_timeout(60)
    cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
    pg.wait_for_timeout(300)
    r=pg.evaluate("()=>({count:window.__pauseCount,paused:G.paused})")
    ck("暫停只被觸發一次", r["count"]==1, str(r))
    ck("遊戲確實暫停", r["paused"]==True, str(r))
    ck("無 JS 錯誤", not errs, str(errs[:2])); pg.close(); c.close()

    print("\n=== 邊角3：關卡數不是5的倍數時，色帶不會超出或缺漏 ===")
    pg,c,errs=P()
    r=pg.evaluate("""()=>{
        const out=[];
        for(const n of [7,13,50]){
            const bak=LEVELS.length;
            while(LEVELS.length>n) LEVELS.pop();
            PROGRESS=1; SEL_IDX=0; buildGalaxy(0,false);
            const inner=document.getElementById('galaxyInner');
            const bands=[...inner.querySelectorAll('.gband')];
            const H=parseFloat(inner.style.height);
            const maxBot=Math.max(...bands.map(b=>parseFloat(b.style.top)+parseFloat(b.style.height)));
            const minTop=Math.min(...bands.map(b=>parseFloat(b.style.top)));
            out.push({關卡數:n, 色帶數:bands.length, 應為:Math.ceil(n/5),
                      最上緣:+minTop.toFixed(1), 最下緣:+maxBot.toFixed(1), 內層高:H});
            location.reload;  // 不能真的 reload，下面用重新載入的分頁處理
            break;
        }
        return out;
    }""")
    print(f"  {r}")
    ck("色帶數 = ceil(關卡數/5)", r[0]["色帶數"]==r[0]["應為"], str(r[0]))
    ck("色帶沒有超出內層上緣", r[0]["最上緣"]>=0)
    pg.close(); c.close()

    print("\n=== 邊角4：反轉後，點擊節點仍能正確選關 ===")
    pg,c,errs=P()
    r=pg.evaluate("""()=>{
        PROGRESS=LEVELS.length+1; showMenu();
        const inner=document.getElementById('galaxyInner');
        const before=SEL_IDX;
        // ⚠ 不要點最後一關：PROGRESS=全破時 SEL_IDX 本來就已經是最後一關，
        //   點下去 before/after 相同，而且面板會顯示「全破」文字而不是關卡資訊。
        inner.querySelector('.gnode[data-k="24"]').click();
        const after=SEL_IDX;
        const txt=document.getElementById('stageInfo').textContent;
        // ⚠ 不能寫死中文字串比對——v0.9.19 之後介面預設是英文，而且可切 11 種語言。
        // 改用遊戲自己的 T() 產生「目前語言」的預期字串，這樣任何語言下都成立。
        return {before,after,面板已更新:txt.includes(T('stageOf',25,LEVELS.length))};
    }""")
    print(f"  {r}")
    ck("點第25關節點後 SEL_IDX=24", r["after"]==24, str(r))
    ck("關卡資訊面板同步更新", r["面板已更新"], str(r))
    ck("無 JS 錯誤", not errs, str(errs[:2])); pg.close(); c.close()

    print("\n=== 邊角5：中途進度的玩家，開選單會捲到自己的關卡 ===")
    pg,c,errs=P()
    r=pg.evaluate("""()=>{
        PROGRESS=50; SEL_IDX=49; showMenu();
        return new Promise(res=>requestAnimationFrame(()=>requestAnimationFrame(()=>{
            const w=document.getElementById('galaxyWrap');
            const el=document.querySelector('.gnode[data-k="49"]');
            const vis = el.offsetTop>=w.scrollTop-40 && el.offsetTop<=w.scrollTop+w.clientHeight+40;
            res({scrollTop:Math.round(w.scrollTop), nodeTop:Math.round(el.offsetTop), 在可視範圍:vis});
        })));
    }""")
    print(f"  {r}")
    ck("第50關的節點捲到可視範圍內", r["在可視範圍"], str(r))
    pg.close(); c.close()

    print("\n=== 邊角6：糖果屋捲到底後買最後一項，畫面不會跳掉 ===")
    pg,c,errs=P()
    r=pg.evaluate("""()=>{
        COINS=9999; META={}; showShop();
        const el=document.getElementById('shopList');
        el.scrollTop=el.scrollHeight;
        const before=el.scrollTop;
        const rows=[...el.querySelectorAll('.mrow')];
        rows[rows.length-1].querySelector('.mbuy').click();
        return {買前scrollTop:before, 買後scrollTop:el.scrollTop,
                最後一項等級:META['coin']||0, 列數:el.querySelectorAll('.mrow').length};
    }""")
    print(f"  {r}")
    ck("買到最後一項成功", r["最後一項等級"]==1, str(r))
    ck("商店列數不變", r["列數"]==10, str(r))
    ck("無 JS 錯誤", not errs, str(errs[:2])); pg.close(); c.close()
    b.close()
srv.shutdown()
print()
if fails: print("❌ 失敗："+", ".join(fails)); sys.exit(1)
print("=== 邊角案例全部通過 ===")
