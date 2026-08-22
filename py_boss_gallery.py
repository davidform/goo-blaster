#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 10 章的 Boss 外觀拼成一張對照圖（含盔甲碎裂前後），用來人眼驗收。"""
import http.server, socketserver, threading, functools, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont
ROOT="/home/claude/goo/game"; PORT=8808
OUT="/home/claude/work/goo-blaster/store"; os.makedirs(OUT,exist_ok=True)
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

SETUP="""([ch,broke])=>{
  applyLanguage('en');
  LV_IDX=(ch+1)*5-1; start();   // v0.9.23：每章 5 關
  G.hasMoved=true; DIAG.touch=3;
  G.E.length=0; G.B.length=0; G.PT.length=0; G.TXT.length=0;
  // ⚠ 第一版拍出來每一隻 Boss 都是純白的——因為玩家的武器會自動開火，
  //   hurtEnemy() 每次命中都設 e.flash=.09，Boss 等於一直處在受擊閃白狀態。
  //   拍外觀圖必須把玩家的武器關掉、並把玩家挪開。
  G.P.wep={}; G.P.atkRange=0;
  G.P.x=0; G.P.y=300;
  const cfg=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
  spawnBoss(cfg);
  const e=G.boss;
  e.x=0; e.y=G.P.y-210; e.spd=0; e.shootCD=999; e.atkT=999; e.flash=0;
  if(broke){ e.armorBroken=true; }
  G.cam.x=G.P.x; G.cam.y=G.P.y; G.cam.zoom=1;
  G.TXT.length=0; G.PT.length=0;
  G.paused=false;
  return {name:e.name, skin:e.skin, r:e.r};
}"""

tiles=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
    for ch in range(10):
        for broke in ([False,True] if ch in (1,3,4,9) else [False]):
            info=pg.evaluate(SETUP,[ch,broke])
            pg.wait_for_timeout(700)
            # Boss 不會動，但相機要幾幀才追上玩家——每幀把 Boss 釘回原位
            pg.evaluate("()=>{ const e=G.boss; if(e){ e.x=0; e.y=G.P.y-210; e.flash=0; } }")
            pg.wait_for_timeout(250)
            path=f"{OUT}/_bs_{ch}_{int(broke)}.png"
            # 相機跟著玩家走，玩家被挪到 y=1400，所以 Boss 在畫面上的位置要現算
            pos=pg.evaluate("()=>({x:G.boss.x-G.cam.x+W/2, y:G.boss.y-G.cam.y+H/2, r:G.boss.r})")
            half=170
            cx=max(half,min(390-half,pos["x"])); cy=max(half,min(844-half,pos["y"]))
            pg.screenshot(path=path, clip={"x":cx-half,"y":cy-half,"width":half*2,"height":half*2})
            tiles.append((path, f"Ch{ch+1} · {info['name']}",
                          ("+".join(info['skin']))+(" [ARMOR BROKEN]" if broke else "")))
    print("errs:",errs)
    b.close()
srv.shutdown()

COLS=4; TW=240; LH=42
rows=(len(tiles)+COLS-1)//COLS
sheet=Image.new("RGB",(COLS*TW, rows*(TW+LH)), (10,7,24))
d=ImageDraw.Draw(sheet)
F1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",15)
F2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",11)
for i,(p,t1,t2) in enumerate(tiles):
    x=(i%COLS)*TW; y=(i//COLS)*(TW+LH)
    sheet.paste(Image.open(p).convert("RGB").resize((TW,TW)),(x,y))
    d.text((x+7,y+TW+4), t1, font=F1, fill=(255,232,120))
    d.text((x+7,y+TW+22), t2, font=F2, fill=(160,200,255))
sheet.save(f"{OUT}/boss-gallery.png")
for p,_,_ in tiles: os.remove(p)
print("→", f"{OUT}/boss-gallery.png", sheet.size)
