#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""量測 Boss 從出現到死亡花多久（笨bot自動打），用來決定血量要調到多少才不會秒殺。"""
import http.server, socketserver, threading, functools, sys, time
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8772
LV = int(sys.argv[1]) if len(sys.argv) > 1 else 0

DUMB = r"""
  const cvs=document.getElementById('cv');
  const mk=(id,x,y)=>new Touch({identifier:id,target:cvs,clientX:x,clientY:y});
  const fire=(t,tt,ch)=>cvs.dispatchEvent(new TouchEvent(t,{touches:tt,changedTouches:ch,bubbles:true,cancelable:true}));
  let cur=mk(1,195,500); fire('touchstart',[cur],[cur]); let i=0;
  window.__drag=setInterval(()=>{ if(!G||!G.running)return;
    i++;
    const P=G.P; let fx=0,fy=0;
    for(const e of G.E){const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;
      if(d<170){fx+=dx/d/d*700;fy+=dy/d/d*700;}}
    const cd=Math.hypot(P.x,P.y); if(cd>700){fx-=P.x/cd*5;fy-=P.y/cd*5;}
    if(Math.hypot(fx,fy)<0.05){ const a=i*0.03; fx=Math.cos(a); fy=Math.sin(a); }
    const m=Math.hypot(fx,fy)||1;
    cur=mk(1,195+fx/m*58,500+fy/m*58); fire('touchmove',[cur],[cur]);
    if(i%140===0 && P.dashCD<=0){ const t2=mk(2,BTN.x,BTN.y);
      fire('touchstart',[cur,t2],[t2]); fire('touchend',[cur],[t2]); }
  },33);
  window.__auto=setInterval(()=>{const el=document.getElementById('cards');
    if(el.classList.contains('hide'))return;
    const cs=[...el.querySelectorAll('.card')];
    cs[Math.floor(Math.random()*cs.length)].click();},80);
"""

socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT),
      functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c = b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2,
                      is_mobile=True, has_touch=True)
    pg = c.new_page()
    pg.goto(f"http://127.0.0.1:{PORT}/index.html")
    pg.wait_for_timeout(400)
    pg.evaluate("""(l)=>{ LV_IDX=l; start(); }""", LV)
    pg.wait_for_timeout(300)
    pg.evaluate(DUMB)

    dur = pg.evaluate("G.winT")
    seenBoss = False
    bossAppearT = None
    bossDieT = None
    t0 = time.time()
    while time.time() - t0 < dur + 60:
        pg.wait_for_timeout(300)
        r = pg.evaluate("""({t:+G.t.toFixed(2), over:G.over, win:G.win,
                             bossAlive: !!G.boss, bossHp: G.boss? G.boss.hp:null,
                             bossMax: G.boss? G.boss.maxhp:null})""")
        if r["bossAlive"] and not seenBoss:
            seenBoss = True
            bossAppearT = r["t"]
            print(f"Boss 出現 t={r['t']}s  hp={r['bossMax']}")
        if seenBoss and not r["bossAlive"] and bossDieT is None:
            bossDieT = r["t"]
            print(f"Boss 消失 t={r['t']}s  (fight took {bossDieT-bossAppearT:.1f}s)")
        if r["over"]:
            print("game over", r)
            break
    b.close()
srv.shutdown()
