#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""難度平衡測試工具（v0.9.16 新增）

為什麼要有這個工具：v0.9.14 生成 90 個新關卡時，只驗證了「數值沒有 NaN、
能正常跑起來」，從來沒有驗證過「這些關卡打得贏嗎」——結果做出 90 個實質上
打不過的關卡卻宣稱測試通過。這個工具就是要把「打得贏嗎」變成可以自動驗收的項目。

兩種模式：
  bot  — 用 tests/py_test9.py 裡逐字相同的笨bot實際玩，量存活比例
  god  — 給滿等滿裝（三武器Lv5+全進化+所有數值卡疊滿），量「理論最強build」
         能不能通關。這是難度的數學下限：如果連滿裝都打不過，這關就是不可能的。

關鍵設計：多個關卡「同時」跑（asyncio + 多個瀏覽器分頁），把驗證時間從十幾分鐘
壓到一兩分鐘，才有辦法反覆迭代調參數。
※ 必須用 async API：Playwright 的同步 API 不能跨執行緒使用（實測會噴
   "Cannot switch to a different thread"），所以平行化只能走 asyncio 這條路。

用法：
  python3 tests/py_balance.py bot 1 5 10 20 50 100
  python3 tests/py_balance.py god 50 100
"""
import http.server, socketserver, threading, functools, sys, asyncio
from playwright.async_api import async_playwright

ROOT = "/home/claude/goo/game"
PORT = 8820

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

GOD = """
  const P=G.P;
  P.wep={bubble:5,graffiti:5,yoyo:5};
  P.evo={bubble:true,graffiti:true,yoyo:true};
  P.sticky=2;P.chain=2;P.mine=2;P.freeze=1;P.shield=2;P.frenzy=2;P.split=2;
  P.rage=1;P.panic=1;P.greed=2;P.cd=2;P.regen=2;P.rangeUp=2;
  P.dashCDmax=1.2;
"""

async def run_one(browser, lv, mode, max_wall_s):
    c = await browser.new_context(viewport={"width":390,"height":844}, device_scale_factor=2,
                                  is_mobile=True, has_touch=True)
    pg = await c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    try:
        await pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        await pg.wait_for_timeout(350)
        await pg.evaluate("(l)=>{ LV_IDX=l; start(); }", lv-1)
        if mode == "god":
            await pg.evaluate(GOD)
        await pg.wait_for_timeout(200)
        await pg.evaluate(DUMB)
        waited = 0
        r = None
        while waited < max_wall_s*1000:
            await pg.wait_for_timeout(1500); waited += 1500
            r = await pg.evaluate("""()=>({over:G.over,win:G.win,t:+G.t.toFixed(1),dur:G.winT,
                                     hearts:G.P.hearts,plv:G.P.lv,kills:G.kills,
                                     e:G.E.length,paused:G.paused})""")
            if r["over"]: break
        r["lv"] = lv; r["errs"] = errs
        r["pct"] = round(r["t"]/r["dur"]*100, 1)
        return r
    finally:
        await pg.close(); await c.close()

async def main_async(mode, levels, max_wall):
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        results = await asyncio.gather(*[run_one(b, lv, mode, max_wall) for lv in levels],
                                       return_exceptions=True)
        await b.close()
    return results

def main():
    # 用法：py_balance.py <mode> [-nN] <關卡...>   -nN = 每關重複跑 N 次取平均
    # 為什麼要重複：笨bot本身有隨機成分（升級卡隨機點、沒敵人時隨機繞圈），
    # 單次結果的雜訊很大——實測過同一份程式碼跑兩次，第10關的成績從 86.9%
    # 掉到 75.4%。只跑一次就調參數，等於在對雜訊調校。
    args = sys.argv[1:]
    mode = args[0] if args else "bot"
    reps = 1
    rest = []
    for a in args[1:]:
        if a.startswith("-n"): reps = int(a[2:])
        else: rest.append(int(a))
    levels = rest or [1,5,10,20,50,100]
    levels = [lv for lv in levels for _ in range(reps)]
    max_wall = 360 if mode == "god" else 130

    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT),
          functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    results = asyncio.run(main_async(mode, levels, max_wall))
    srv.shutdown()

    ok = [r for r in results if isinstance(r, dict)]
    for r in results:
        if not isinstance(r, dict): print("  例外:", r)
    ok.sort(key=lambda r: r["lv"])

    label = "笨bot（一般玩家基準）" if mode=="bot" else "滿等滿裝（理論最強build）"
    print(f"\n=== 難度測試：{label} ===")
    # 依關卡分組取平均，避免被單次雜訊誤導
    from statistics import mean
    groups = {}
    for r in ok: groups.setdefault(r["lv"], []).append(r)
    print(f"{'關卡':>5} {'次數':>4} {'走完%(平均)':>13} {'範圍':>15} {'通關':>6} {'擊殺(平均)':>11}")
    for lv in sorted(groups):
        rs = groups[lv]
        pcts = [r["pct"] for r in rs]
        wins = sum(1 for r in rs if r["win"])
        flag = ""
        if any(r["paused"] for r in rs): flag += " ⚠凍結"
        if any(r["errs"] for r in rs): flag += " ⚠JS錯誤"
        rng = f"{min(pcts):.0f}~{max(pcts):.0f}%" if len(rs) > 1 else "-"
        print(f"{lv:>5} {len(rs):>4} {mean(pcts):>12.1f}% {rng:>15} {wins}/{len(rs):<4} {mean([r['kills'] for r in rs]):>10.0f}{flag}")

    if mode == "god":
        print()
        ref = groups.get(10)
        if ref:
            refpct = mean([r["pct"] for r in ref])
            print(f"參考基準：第10關（使用者原本調好、未改動的最終關）平均走完 {refpct:.1f}%")
            print("驗收原則：第11關之後的關卡不應該比第10關難太多——這個測試的笨bot完全不閃")
            print("          子彈，所以就算是設計良好的關卡也不會 100% 通關，要看的是「相對」值。")

if __name__ == "__main__":
    main()
