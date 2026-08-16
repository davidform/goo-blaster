#!/usr/bin/env python3
# 用 CDP Input.dispatchTouchEvent 送出「瀏覽器層級的可信觸控」，
# 而不是 new TouchEvent() 合成事件。這比 docs/02 第四節提到的舊做法可信。
import http.server, socketserver, threading, functools, sys, time
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8731

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

results = {}

def run(scheme):
    url = (f"http://127.0.0.1:{PORT}/index.html" if scheme == "http"
           else f"file://{ROOT}/index.html")
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader"])
        ctx = b.new_context(viewport={"width": 390, "height": 844},
                            device_scale_factor=3, is_mobile=True,
                            has_touch=True,
                            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                                       "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                                       "Mobile/15E148 Safari/604.1")
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_timeout(600)
        pg.click("#btnPlay")
        pg.wait_for_timeout(800)

        cdp = ctx.new_cdp_session(pg)
        def touch(t, pts):
            cdp.send("Input.dispatchTouchEvent", {
                "type": t,
                "touchPoints": [{"x": x, "y": y, "id": 1} for x, y in pts],
            })

        start = pg.evaluate("({x:G.P.x,y:G.P.y})")
        touch("touchStart", [(150, 500)])
        for i in range(1, 21):
            touch("touchMove", [(150 + i * 4, 500 - i * 3)])
            pg.wait_for_timeout(30)
        pg.wait_for_timeout(600)
        state = pg.evaluate("({d:JSON.parse(JSON.stringify(DIAG)),"
                            "act:IN.active,mag:IN.mag,px:G.P.x,py:G.P.y,"
                            "moved:G.hasMoved})")
        touch("touchEnd", [])
        pg.wait_for_timeout(200)
        after_end = pg.evaluate("IN.active")
        b.close()

    moved = ((state["px"] - start["x"]) ** 2 + (state["py"] - start["y"]) ** 2) ** 0.5
    results[scheme] = dict(diag=state["d"], joy=state["act"], mag=round(state["mag"], 2),
                           dist=round(moved, 1), released=(not after_end), errs=errs)

for s in ("http", "file"):
    run(s)

for s, r in results.items():
    d = r["diag"]
    print(f"[{s}] touchstart={d['touch']} move={d['tmove']} end={d['tend']} "
          f"pointer={d['pointer']}/{d['pmove']} 搖桿={r['joy']} mag={r['mag']} "
          f"位移={r['dist']}px 放開後歸零={r['released']} err={d['err'] or '無'} {r['errs'] or ''}")
httpd.shutdown()
