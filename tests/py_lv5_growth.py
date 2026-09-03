#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用真的笨bot（會移動、會撿晶核、會選卡）量：第5關打到 Boss 出場時，玩家長成什麼樣。"""
import http.server, socketserver, threading, functools, sys, os
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from py_balance import DUMB
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8831
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

AUTOPICK = """
window.__auto=setInterval(()=>{
  if(!cardsEl.classList.contains('hide')){
    const list=rollCards();
    // 模擬一般玩家：偏好武器卡（新手直覺會拿看得懂的），但不是完美最佳解
    if(list.length){
      const wep=list.filter(c=>c.w);
      applyCard(wep.length?wep[0]:list[0]);
    }
  }
}, 120);
"""

def run(pg, lv, immortal=True):
    pg.evaluate("(lv)=>{ META={}; LV_IDX=lv; start(); }", lv)
    pg.wait_for_timeout(200)
    pg.evaluate(DUMB)
    pg.evaluate(AUTOPICK)
    if immortal:
        pg.evaluate("()=>{ window.__im=setInterval(()=>{ G.P.hearts=G.P.maxHearts; },100); }")
    snaps=[]
    for _ in range(110):
        pg.wait_for_timeout(2500)
        s=pg.evaluate("""()=>({t:+G.t.toFixed(1),lv:G.P.lv,wep:JSON.parse(JSON.stringify(G.P.wep)),
                              evo:JSON.parse(JSON.stringify(G.P.evo||{})),kills:G.kills,
                              boss:G.boss?+(G.boss.hp/G.boss.maxhp*100).toFixed(0):null,
                              over:G.over,win:G.win,dur:G.winT})""")
        snaps.append(s)
        if s["over"]: break
    pg.evaluate("()=>{ clearInterval(window.__auto); if(window.__im) clearInterval(window.__im); }")
    return snaps

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)

    for lvidx,label in [(4,"第5關")]:
        print(f"\n=== {label}：笨bot（不死模式，只看成長與能不能打死 Boss）===")
        snaps=run(pg,lvidx)
        for s in snaps:
            if s["t"]<1: continue
            w=s["wep"]; ws="/".join(str(w.get(k,0)) for k in ["bubble","graffiti","yoyo"])
            evo=",".join(k for k,v in (s["evo"] or {}).items() if v) or "-"
            bh=f"Boss {s['boss']}%" if s["boss"] is not None else ""
            print(f"   t={s['t']:>6}  Lv.{s['lv']:<3} 武器 {ws:<8} 進化 {evo:<10} 擊殺 {s['kills']:<4} {bh}")
            if s["over"]: print(f"   → 結束：{'通關' if s['win'] else '失敗'}（關卡長 {s['dur']} 秒）")
        last=snaps[-1]
        if not last["over"]:
            print(f"   → 取樣結束仍未打完，最後 Boss 剩 {last['boss']}%")
    b.close()
srv.shutdown()
