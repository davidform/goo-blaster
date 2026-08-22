#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 關基準線在 v0.9.27 之後兩次「零失誤」沒過 → 這支查是不是真的迴歸。

方法論第 8 條：懷疑迴歸先找機制、再看統計；第 17 條：證明輸入相同勝過多跑幾次。
機制上 v0.9.27 對第 1 關的唯一接觸點是「寶箱池多了糖果援軍」——而援軍是幫玩家的，
理論上只會更簡單。但 pick() 的抽樣序列變了，每一場的隨機軌跡就不一樣，
笨 bot 本來就是機率性的，單次結果不能下結論。

所以做同批次 A/B：現版 vs「把援軍從池子拿掉」的對照版，各跑 N 場，比零失誤率。
"""
import asyncio, http.server, socketserver, threading, functools, sys, os
from playwright.async_api import async_playwright

ROOT="/home/claude/goo/game"; PORT=8867
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

REPS=6
fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

# 對照版：把援軍從寶箱池拿掉（其餘 8 種的比例完全不動）
_SRC=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
assert "ally:4 };" in _SRC
_NOALLY=_SRC.replace("ally:4 };","ally:0 };",1)
async def noally_route(route):        # async API 的 route handler 必須是 coroutine
    await route.fulfill(status=200, content_type="text/html; charset=utf-8", body=_NOALLY)

# 跟 py_test9 同一隻笨 bot：只看 170px 內的敵人、不看子彈、升級卡隨機點。
BOT = """
()=>{
  META={}; LV_IDX=0; start(); DIAG.touch=3;
  window.__done=null;
  window.__bot=setInterval(()=>{
    if(!G) return;
    if(!G.running){ if(!window.__done) window.__done={win:!!G.win, hearts:G.P.hearts,
                                                      max:G.P.maxHearts, t:+G.t.toFixed(0),
                                                      lv:G.P.lv, kills:G.kills};
                    return; }
    if(G.pendingCards>0 || !cardsEl.classList.contains('hide')){
      const cs=cardsEl.querySelectorAll('.card');
      if(cs.length) cs[Math.floor(Math.random()*cs.length)].click();
      return;
    }
    // 只感知 170px 內的敵人，往反方向跑；沒有敵人就朝中心靠
    const P=G.P; let ax=0, ay=0, n=0;
    for(const e of G.E){ const dx=P.x-e.x, dy=P.y-e.y, d=Math.hypot(dx,dy);
      if(d<170&&d>1){ ax+=dx/d; ay+=dy/d; n++; } }
    if(!n){ ax=-P.x; ay=-P.y; }
    const m=Math.hypot(ax,ay);
    if(m>0.01){ IN.active=true; IN.id='bot'; IN.dx=ax/m; IN.dy=ay/m; IN.mag=1; }
    G.hasMoved=true;
  },80);
}
"""

async def one(browser, noally):
    c=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                is_mobile=True,has_touch=True,locale="en-US")
    pg=await c.new_page(); pg.set_default_navigation_timeout(120000)
    errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    if noally: await pg.route(f"http://127.0.0.1:{PORT}/index.html", noally_route)
    await pg.goto(f"http://127.0.0.1:{PORT}/index.html"); await pg.wait_for_timeout(600)
    await pg.evaluate(BOT)
    for _ in range(600):                       # 最多等 60 秒牆鐘
        await pg.wait_for_timeout(500)
        if await pg.evaluate("()=>!!window.__done"): break
    r=await pg.evaluate("()=>{ clearInterval(window.__bot); return window.__done; }")
    await c.close()
    return r or {"win":False,"hearts":0,"max":3,"t":-1,"lv":0,"kills":0}

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        cur,ctl=[],[]
        print(f"=== 第 1 關 同批次 A/B（各 {REPS} 場）===")
        for i in range(REPS):
            a,c2=await asyncio.gather(one(b,False), one(b,True))
            cur.append(a); ctl.append(c2)
            f=lambda x: ("通關" if x["win"] else "陣亡")+f' {x["hearts"]}/{x["max"]}心 {x["t"]}秒 LV.{x["lv"]}'
            print(f"  第{i+1}場  有援軍：{f(a):<28} 無援軍（對照）：{f(c2)}")
        await b.close()
        def rate(rs):
            win=sum(1 for x in rs if x["win"])
            perfect=sum(1 for x in rs if x["win"] and x["hearts"]==x["max"])
            return win,perfect
        w1,p1=rate(cur); w2,p2=rate(ctl)
        print()
        print(f"  有援軍（v0.9.27）  通關 {w1}/{REPS}   零失誤 {p1}/{REPS}")
        print(f"  無援軍（對照組）    通關 {w2}/{REPS}   零失誤 {p2}/{REPS}")
        print()
        ck("第 1 關通關率沒有比對照組低", w1>=w2, f"{w1} vs {w2}")
        ck("第 1 關零失誤率沒有比對照組低（容許 1 場的隨機差）", p1>=p2-1, f"{p1} vs {p2}")
        ck("第 1 關一定會通關（掉不掉心是機率，通不通關不是）", w1==REPS, f"{w1}/{REPS}")
        return 0

rc=asyncio.run(main())
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails}"); sys.exit(1)
print("=== 第 1 關沒有迴歸 ===")
