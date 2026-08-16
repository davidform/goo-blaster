#!/usr/bin/env python3
"""右下角/正中央/左下角起手拖曳，各自會發生什麼"""
import http.server, socketserver, threading, functools
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"; PORT = 8751
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT),
      functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

CASES = [("右下角（右手拇指自然位置）", 322, 742),
         ("正中央", 195, 420),
         ("左下角", 70, 742),
         ("右下但再往左一點", 250, 742)]

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, sx, sy in CASES:
        c = b.new_context(viewport={"width":390,"height":844}, is_mobile=True, has_touch=True)
        pg = c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        pg.wait_for_timeout(400); pg.click("#btnPlay"); pg.wait_for_timeout(700)
        geo = pg.evaluate("({bx:BTN.x,by:BTN.y,br:BTN.r,hit:BTN.r*1.3})")
        cdp = c.new_cdp_session(pg)
        t = lambda ty, pts: cdp.send("Input.dispatchTouchEvent",
              {"type":ty, "touchPoints":[{"x":x,"y":y,"id":1} for x,y in pts]})
        st = pg.evaluate("({x:G.P.x,y:G.P.y,cd:G.P.dashCD})")
        t("touchStart", [(sx, sy)])
        for i in range(1, 16):
            t("touchMove", [(sx - i*6, sy - i*6)]); pg.wait_for_timeout(28)
        pg.wait_for_timeout(400)
        r = pg.evaluate("({act:IN.active,mag:IN.mag,x:G.P.x,y:G.P.y,cd:G.P.dashCD})")
        t("touchEnd", []); 
        d = ((r["x"]-st["x"])**2 + (r["y"]-st["y"])**2) ** .5
        print(f"{label:24} 搖桿={'ON ' if r['act'] else 'off'} "
              f"mag={r['mag']:.2f} 位移={d:7.1f}px "
              f"衝刺觸發={'是' if r['cd']>0 else '否'}")
        c.close()
    print(f"\nBTN 中心=({geo['bx']:.0f},{geo['by']:.0f}) 畫出的半徑={geo['br']:.1f} "
          f"實際判定半徑={geo['hit']:.1f}")
    b.close()
srv.shutdown()
