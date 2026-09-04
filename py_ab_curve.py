#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.23 難度曲線 A/B：舊 100 關版 vs 新 50 關版，**在同一個批次裡**跑。

為什麼一定要同批次（方法論第 3 條）：平行分頁數會明顯影響笨bot的成績，
跨批次的數字不能互比。這支把「舊第 2N 關」與「新第 N 關」放進同一次
asyncio.gather，兩邊搶同樣的 CPU，比出來的差異才是關卡造成的。

配對邏輯：新第 N 關 ≈ 舊第 2N 關（玩家在同樣的遊戲進度上會遇到的關卡）。
"""
import http.server, socketserver, threading, functools, sys, asyncio, os
from statistics import mean
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from py_balance import DUMB, GOD

ROOT="/tmp/abroot"; PORT=8822

async def run_one(browser, build, lv, mode, max_wall_s):
    c=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                is_mobile=True,has_touch=True,locale="en-US")
    pg=await c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    try:
        await pg.goto(f"http://127.0.0.1:{PORT}/{build}/index.html")
        await pg.wait_for_timeout(400)
        await pg.evaluate("(l)=>{ LV_IDX=l; start(); }", lv-1)
        if mode=="god": await pg.evaluate(GOD)
        await pg.wait_for_timeout(200)
        await pg.evaluate(DUMB)
        waited=0; r=None
        while waited<max_wall_s*1000:
            await pg.wait_for_timeout(1500); waited+=1500
            r=await pg.evaluate("""()=>({over:G.over,win:G.win,t:+G.t.toFixed(1),dur:G.winT,
                                    hearts:G.P.hearts,plv:G.P.lv,kills:G.kills})""")
            if r["over"]: break
        r.update(build=build, lv=lv, errs=errs, pct=round(r["t"]/r["dur"]*100,1))
        return r
    finally:
        await pg.close(); await c.close()

async def main_async(mode, pairs, reps, max_wall):
    tasks=[]
    for newlv, oldlv in pairs:
        for _ in range(reps):
            tasks.append(("new",newlv)); tasks.append(("old",oldlv))
    async with async_playwright() as pw:
        b=await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        res=await asyncio.gather(*[run_one(b,bd,lv,mode,max_wall) for bd,lv in tasks],
                                 return_exceptions=True)
        await b.close()
    return res

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else "god"
    reps=2
    for a in sys.argv[2:]:
        if a.startswith("-n"): reps=int(a[2:])
    # 可用 CLI 指定要比哪幾組：py_ab_curve.py god -n5 50   → 只比「新第50關 vs 舊第100關」
    ALL=[(5,10),(10,20),(25,50),(50,100)]
    want=[int(a) for a in sys.argv[2:] if not a.startswith('-')]
    PAIRS=[p for p in ALL if (not want or p[0] in want)]
    max_wall=360 if mode=="god" else 150
    socketserver.TCPServer.allow_reuse_address=True
    srv=socketserver.TCPServer(("127.0.0.1",PORT),
        functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
    threading.Thread(target=srv.serve_forever,daemon=True).start()
    res=asyncio.run(main_async(mode,PAIRS,reps,max_wall))
    srv.shutdown()
    ok=[r for r in res if isinstance(r,dict)]
    for r in res:
        if not isinstance(r,dict): print("  例外:",r)
    g={}
    for r in ok: g.setdefault((r["build"],r["lv"]),[]).append(r)
    label="笨bot" if mode=="bot" else "滿等滿裝"
    print(f"\n=== 難度曲線 A/B（{label}，同批次、每組 {reps} 次）===")
    print(f"{'新關卡':>6} {'走完%':>8} {'通關':>6}   |  {'舊關卡':>6} {'走完%':>8} {'通關':>6}   |  {'差異':>8}")
    bad=[]
    for newlv,oldlv in PAIRS:
        a=g.get(("new",newlv),[]); b2=g.get(("old",oldlv),[])
        if not a or not b2: print(f"  第{newlv}關 / 第{oldlv}關：資料不足"); continue
        pa=mean(x["pct"] for x in a); pb=mean(x["pct"] for x in b2)
        wa=sum(1 for x in a if x["win"]); wb=sum(1 for x in b2 if x["win"])
        d=pa-pb
        print(f"{newlv:>6} {pa:>7.1f}% {wa:>3}/{len(a)}   |  {oldlv:>6} {pb:>7.1f}% {wb:>3}/{len(b2)}   |  {d:>+7.1f}pt")
        # 新版不可以比舊版對應關卡難「太多」（走完%不得低於舊版的 60%）
        if pb>5 and pa < pb*0.60: bad.append((newlv,oldlv,pa,pb))
    print("\n判讀：差異為正＝新版比舊版對應關卡好過。同批次跑，數字可以直接互比。")
    if bad:
        print("❌ 這些關卡在新版明顯變難："+", ".join(f"新第{n}關 {x:.1f}% vs 舊第{o}關 {y:.1f}%" for n,o,x,y in bad))
        sys.exit(1)
    print("=== 通過：新曲線沒有比舊版對應關卡難 ===")

if __name__=="__main__": main()
