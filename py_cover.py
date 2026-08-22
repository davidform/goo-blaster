#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 itch.io 需要的封面圖（630x500）與幾張商店用截圖。
不是遊戲功能，是上架素材產生器。"""
import http.server, socketserver, threading, functools, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT="/home/claude/goo/game"; PORT=8791
OUT="/home/claude/work/goo-blaster/store"
os.makedirs(OUT, exist_ok=True)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

shots=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    # 用較寬的視窗抓橫向素材
    c=b.new_context(viewport={"width":640,"height":508}, device_scale_factor=2,
                    is_mobile=True, has_touch=True, locale="en-US")
    pg=c.new_page()
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)

    # 場面一：中期關卡、敵人成群、玩家已升級（好看的一張）
    pg.evaluate("""()=>{
        META={hearts:3,dmg:3,aspd:3,range:2,xp:2,pickup:2,dash:1,wep:3,coin:2};
        LV_IDX=34; start();
        G.P.lv=18; G.P.wep={bubble:5,graffiti:4,yoyo:4};
        for(let i=0;i<38;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4], 1.2);
    }""")
    pg.wait_for_timeout(1200)
    # 升級卡面板會蓋掉戰鬥畫面，關掉它、恢復遊戲再抓
    pg.evaluate("""()=>{
        G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
        for(let i=0;i<20;i++) gemBurst(G.P.x+(Math.random()-.5)*520, G.P.y+(Math.random()-.5)*520, 1);
    }""")
    pg.wait_for_timeout(1000)
    # 讓開場的操作提示自然淡掉，同時保持不死、戰況熱鬧
    pg.evaluate("""()=>{
        window.__keep=setInterval(()=>{
            G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
            G.P.hearts=G.P.maxHearts; G.hasMoved=true; DIAG.touch=DIAG.touch||3;
            if(G.E.length<40){ for(let i=0;i<10;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.2); }
        },250);
    }""")
    pg.wait_for_timeout(11000)
    pg.evaluate("()=>{ clearInterval(window.__keep); G.hasMoved=true; DIAG.touch=DIAG.touch||3; G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false; }")
    pg.wait_for_timeout(400)
    p=f"{OUT}/shot-gameplay.png"; pg.screenshot(path=p); shots.append(p)

    # 場面二：關卡地圖
    pg.evaluate("()=>{ location.reload(); }"); pg.wait_for_timeout(900)
    p=f"{OUT}/shot-menu.png"; pg.screenshot(path=p); shots.append(p)
    b.close()
srv.shutdown()

# ---- 封面 630x500 ----
src=Image.open(f"{OUT}/shot-gameplay.png").convert("RGB")
W,H=630,500
sw,sh=src.size
scale=max(W/sw, H/sh)*1.15
img=src.resize((int(sw*scale),int(sh*scale)), Image.LANCZOS)
img=img.crop(((img.width-W)//2,(img.height-H)//3,(img.width-W)//2+W,(img.height-H)//3+H))

d=ImageDraw.Draw(img,"RGBA")
# 上下暗角，讓標題看得清楚
for y in range(150):
    a=int(190*(1-y/150))
    d.line([(0,y),(W,y)], fill=(8,6,20,a))
for y in range(110):
    a=int(170*(1-y/110))
    d.line([(0,H-1-y),(W,H-1-y)], fill=(8,6,20,a))

F=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)
def center(txt,y,size,fill,stroke=(20,8,40),sw_=6):
    f=F(size); w=d.textlength(txt,font=f)
    d.text(((W-w)/2,y),txt,font=f,fill=fill,stroke_width=sw_,stroke_fill=stroke)

center("GOO BLASTER",30,60,(255,241,120))
center("50 stages of sticky survival",108,21,(190,255,235),sw_=4)
center("Free in your browser  ·  No download",H-52,19,(255,190,220),sw_=4)
img.save(f"{OUT}/cover-630x500.png")
print("cover ->", f"{OUT}/cover-630x500.png", img.size)
for s in shots: print("shot ->", s, Image.open(s).size)
