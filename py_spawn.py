#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""針對 v0.9.19 把 spawnEnemy() 裡的區域變數 T 改名成 ET 做專門驗證：
   四種敵人的每一個屬性都必須正確從 ETYPE 帶過來，不能有 undefined/NaN。"""
import http.server, socketserver, threading, functools, json, sys
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8780
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(500)
    r=pg.evaluate("""()=>{
        const out={};
        for(const lv of [0, 6, 24, 49]){
            LV_IDX=lv; start(); G.E.length=0;
            const per={};
            for(const t of ['slime','bunny','drone','bomber']){
                spawnEnemy(t,1);
                const e=G.E[G.E.length-1];
                const src=ETYPE[t];
                per[t]={
                    r:e.r, hp:+e.hp.toFixed(1), spd:+e.spd.toFixed(1), dmg:e.dmg, hue:e.hue,
                    xp:e.xp, boom:!!e.boom, kite:!!e.kite, ranged:!!e.ranged,
                    shootRange:e.shootRange, cdMin:+e.cdMin.toFixed(2), tier:e.tier,
                    // 屬性必須真的來自 ETYPE（改名後最容易壞的就是這裡）
                    r對得上:e.r===src.r, dmg對得上:e.dmg===src.dmg,
                    hue對得上:e.hue===src.hue, xp對得上:e.xp===src.xp,
                    shootRange對得上:e.shootRange===src.shootRange,
                    有NaN:[e.r,e.hp,e.spd,e.dmg,e.hue,e.xp,e.shootRange,e.cdMin,e.cdMax,e.shootCD].some(v=>!isFinite(v)),
                    有undefined:[e.r,e.hp,e.spd,e.dmg,e.hue,e.xp,e.shootRange].some(v=>v===undefined)
                };
            }
            out['第'+(lv+1)+'關']=per;
        }
        return out;
    }""")
    for lvl,per in r.items():
        print(f"  {lvl}:")
        for t,v in per.items():
            bad = v["有NaN"] or v["有undefined"] or not all([v["r對得上"],v["dmg對得上"],v["hue對得上"],v["xp對得上"],v["shootRange對得上"]])
            mark = "❌" if bad else "✅"
            print(f"    {mark} {t:<7} r={v['r']} hp={v['hp']} spd={v['spd']} dmg={v['dmg']} xp={v['xp']} range={v['shootRange']} tier={v['tier']} ranged={v['ranged']}")
            if bad: fails.append(f"{lvl}/{t}")
    print("  pageerrors:", errs)
    if errs: fails.append("JS錯誤")
    b.close()
srv.shutdown()
print()
print("❌ 失敗: "+", ".join(fails) if fails else "=== spawnEnemy() 改名後屬性全部正確 ===")
sys.exit(1 if fails else 0)
