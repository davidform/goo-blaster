#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.40 救命卡加權的同批次 A/B（診斷用，**不在** run_tests.sh 預設批次）。

要回答的問題：「剩一顆愛心時把 🍩🍬🩹 加權」對難度的影響有多大？

怎麼做到同批次：ON 組讀 v0.9.40、OFF 組讀 **v0.9.39 的 index.html**，
兩份檔案由**同一個 HTTP server 的兩個子目錄**提供，ON/OFF **交錯排程**
（每批 4 場、兩組各 2 場），所以兩組永遠處在同一個 CPU 負載環境下。
跨批次的數字不能互比（AGENTS.md 第 3 節第 5 條），這個排法就是為了繞開它。

⚠ **這個工具量到的是下界，不是玩家實際感受到的效果。**
   笨bot 選卡是 `cs[Math.floor(Math.random()*cs.length)]`——**三張隨機點一張**。
   真人在剩一顆心時會**刻意去點**那張救命卡，命中率接近 100%；
   笨bot只有 1/3。所以這裡量到的差距大約是真人效果的三分之一。
   反過來說：**bot 量得到差距，代表真人一定量得到**。

用法：
  python3 tests/py_ab_lifeline.py            # 第 7 關，每組 10 場
  python3 tests/py_ab_lifeline.py 9 8        # 第 9 關，每組 8 場

前置：
  mkdir -p /home/claude/goo/ab/on /home/claude/goo/ab/off
  cp index.html /home/claude/goo/ab/on/
  git show <v0.9.39 的 commit>:index.html > /home/claude/goo/ab/off/index.html
"""
import http.server, socketserver, threading, functools, sys, os, asyncio
from statistics import mean, median
from playwright.async_api import async_playwright

ROOT = os.environ.get('GOO_AB_ROOT', '/home/claude/goo/ab')
PORT = 8873
MAX_WALL_S = 130

# 逐字沿用 tests/py_balance.py 的笨bot——換一隻 bot 就換了尺標，A/B 會失去意義
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
    if(cs.length) cs[Math.floor(Math.random()*cs.length)].click();},80);
"""


class _Server(socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    last = None
    for port in range(PORT, PORT + 20):
        try:
            httpd = _Server(("127.0.0.1", port), handler)
        except OSError as e:
            last = e
            continue
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return httpd, port
    raise last


async def run_one(browser, port, arm, lv):
    c = await browser.new_context(viewport={"width": 390, "height": 844},
                                  device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = await c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    try:
        await pg.goto(f"http://127.0.0.1:{port}/{arm}/index.html")
        await pg.wait_for_function("typeof start === 'function'", timeout=60000)
        build = await pg.evaluate("() => BUILD")
        await pg.evaluate("(l)=>{ META={}; LV_IDX=l; start(); }", lv - 1)
        await pg.wait_for_function("G && G.running", timeout=60000)
        await pg.evaluate(DUMB)
        waited = 0
        r = None
        while waited < MAX_WALL_S * 1000:
            await pg.wait_for_timeout(1500)
            waited += 1500
            r = await pg.evaluate("""()=>({over:G.over,win:G.win,t:+G.t.toFixed(1),dur:G.winT,
                                          kills:G.kills,
                                          life:(G.P.shield|0)+(G.P.regen|0)+(G.P.panic|0)})""")
            if r["over"]:
                break
        r.update(arm=arm, lv=lv, build=build, errs=errs)
        r["pct"] = round(r["t"] / r["dur"] * 100, 1)
        return r
    finally:
        await pg.close()
        await c.close()


async def main_async(port, lv, n):
    # ⚠ 交錯排程：每批 4 場 = ON 2 場 + OFF 2 場，兩組吃到同一個負載
    plan = []
    for _ in range(n):
        plan += ["on", "off"]
    out = []
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        for i in range(0, len(plan), 4):
            batch = plan[i:i + 4]
            res = await asyncio.gather(*[run_one(b, port, a, lv) for a in batch],
                                       return_exceptions=True)
            for r in res:
                if isinstance(r, dict):
                    out.append(r)
                else:
                    print("  例外：", r)
            print(f"  ... 已完成 {len(out)}/{len(plan)} 場")
        await b.close()
    return out


def main():
    lv = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for arm in ("on", "off"):
        p = os.path.join(ROOT, arm, "index.html")
        if not os.path.exists(p):
            print(f"❌ 找不到 {p}（請照檔頭的「前置」準備兩份 index.html）")
            sys.exit(2)

    httpd, port = serve()
    try:
        rs = asyncio.run(main_async(port, lv, n))
    finally:
        httpd.shutdown()

    print(f"\n=== 第 {lv} 關 · 笨bot · 同批次交錯 A/B ===")
    print(f"{'組別':>6} {'版本':>10} {'場數':>4} {'走完%(平均)':>13} {'中位數':>8} "
          f"{'範圍':>13} {'通關':>7} {'救命卡層數(平均)':>16}")
    stat = {}
    for arm in ("off", "on"):
        g = [r for r in rs if r["arm"] == arm]
        if not g:
            continue
        p = [r["pct"] for r in g]
        stat[arm] = mean(p)
        wins = sum(1 for r in g if r["win"])
        build = g[0]["build"]
        label = "OFF（v0.9.39）" if arm == "off" else "ON （v0.9.40）"
        print(f"{label:>6} {build:>10} {len(g):>4} {mean(p):>12.1f}% {median(p):>7.1f}% "
              f"{min(p):>5.0f}~{max(p):<5.0f}% {wins}/{len(g):<5} "
              f"{mean([r['life'] for r in g]):>15.2f}")
        if any(r["errs"] for r in g):
            print(f"       ⚠ {arm} 組有 JS 錯誤：{[r['errs'] for r in g if r['errs']][:1]}")

    if "on" in stat and "off" in stat:
        d = stat["on"] - stat["off"]
        print(f"\n差異：{d:+.1f} 個百分點（相對 {d/stat['off']*100:+.1f}%）")
        print("⚠ 笨bot 是三張隨機點一張，真人會刻意去點救命卡——"
              "這個差距大約是真人效果的三分之一（下界）。")
        print("⚠ 單次笨bot成績的雜訊很大（AGENTS.md：同一份程式碼跑兩次曾差 11.5 個百分點），"
              "所以個位數的差距要當成「量不出來」，不要當成結論。")


if __name__ == "__main__":
    main()
