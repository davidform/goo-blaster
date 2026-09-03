#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.27 測試循環 2／3：糖果援軍的效能與邊角。

docs-11 明確標了這個風險：
  「同伴會產生額外子彈，第 50 關已經有 150 隻敵人 + 4 隻 Boss」
所以這支專門量最壞情況：**第 50 關、敵人塞滿、玩家用最會噴子彈的武器（彩虹塗鴉
Lv.5，一次 7 發）、3 個同伴全開**，跟同一批次的「沒有同伴」對照。

同批次 A/B，因為跨批次的 FPS 不能互比（平行分頁數會影響結果）。
"""
import asyncio, http.server, socketserver, threading, functools, sys, statistics
from playwright.async_api import async_playwright

ROOT="/home/claude/goo/game"; PORT=8863
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

WORST = """
([withAlly])=>{
  META={hearts:3,dmg:3,aspd:3,range:2,xp:2,pickup:2,dash:1,wep:3,coin:2};
  LV_IDX=49; start(); G.hasMoved=true; DIAG.touch=3;
  G.P.lv=22; G.P.wep={graffiti:5, bubble:5, yoyo:5};   // 三把全滿＝子彈量最大
  G.P.evo={};                                          // 同伴不繼承進化，玩家也先不開，變因才單純
  window.__frames=0; window.__ally=0;
  const raf=window.requestAnimationFrame;
  window.requestAnimationFrame=function(cb){ return raf(function(t){ window.__frames++; return cb(t); }); };
  window.__k=setInterval(()=>{
    G.P.hearts=G.P.maxHearts; G.P.iframe=1;            // 不死，量的是穩態負載
    G.pendingCards=0; cardsEl.classList.add('hide'); G.paused=false;
    // 把場面塞到上限
    if(G.E.length<140){ for(let i=0;i<14;i++) spawnEnemy(['slime','bunny','drone','bomber'][i%4],1.2); }
    if(withAlly){
      if(G.ALLY.length<ALLY_N) CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
      for(const a of G.ALLY) a.life=99;                // 全程都在，量最壞情況
    }
    window.__ally=Math.max(window.__ally,G.ALLY.length);
  },200);
}
"""

async def one(browser, with_ally):
    c=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                is_mobile=True,has_touch=True,locale="en-US")
    pg=await c.new_page(); errs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(f"http://127.0.0.1:{PORT}/index.html"); await pg.wait_for_timeout(600)
    await pg.evaluate(WORST,[with_ally])
    await pg.wait_for_timeout(1500)                    # 暖機，不算進去
    t0=await pg.evaluate("()=>({f:window.__frames, t:performance.now()})")
    await pg.wait_for_timeout(8000)
    r=await pg.evaluate("""([f0,t0])=>{ clearInterval(window.__k);
        const fps=(window.__frames-f0)/((performance.now()-t0)/1000);
        return {fps:+fps.toFixed(1), enemies:G.E.length, bullets:G.B.length,
                ebullets:G.EB.length, ally:window.__ally}; }""",
        [t0["f"], t0["t"]])
    r["errs"]=errs
    await c.close()
    return r

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        print("=== 1. 第50關最壞情況：有同伴 vs 沒同伴（同批次 A/B、3 次重複）===")
        off,on=[],[]
        for i in range(3):
            a,c2=await asyncio.gather(one(b,False), one(b,True))
            off.append(a); on.append(c2)
            print(f"  第{i+1}輪  無同伴 {a['fps']:>5} fps（敵{a['enemies']} 我彈{a['bullets']}）"
                  f"   ／ 有同伴 {c2['fps']:>5} fps（敵{c2['enemies']} 我彈{c2['bullets']} 同伴{c2['ally']}）")
        await b.close()
        f_off=statistics.mean(x['fps'] for x in off)
        f_on =statistics.mean(x['fps'] for x in on)
        b_off=statistics.mean(x['bullets'] for x in off)
        b_on =statistics.mean(x['bullets'] for x in on)
        print()
        print(f"  平均 FPS    {f_off:.1f} → {f_on:.1f}   （{(f_on-f_off)/f_off*100:+.1f}%）")
        print(f"  場上我方子彈 {b_off:.0f} → {b_on:.0f}")
        ck("有同伴時確實有 3 個", all(x['ally']==3 for x in on), [x['ally'] for x in on])
        ck("同伴確實增加了子彈量（功能真的有在跑）", b_on>b_off, (round(b_off),round(b_on)))
        # ⚠ 對照組本身就跑不動的時候，連相對值都沒有解析度
        #   （2.6 fps vs 1.6 fps 在 8 秒裡只差兩幀）。這種情況要明說量不出來，
        #   不能拿一個看起來像結論的百分比出來——那比沒有數字更危險。
        if f_off < 20:
            print(f"  ⚠ 量不到：對照組只有 {f_off:.1f} fps，代表這支正在跟其他測試搶 CPU。")
            print(f"    效能測試請單獨跑（run_tests.sh 已經把它排在平行批次之後）。")
            ck("環境足夠安靜、量得到效能", False, f"對照組 {f_off:.1f} fps")
        else:
            ck("同伴造成的 FPS 損失 < 20%（同批次相對值）",
               f_on > f_off*0.80, f"{(f_on-f_off)/f_off*100:+.1f}%")
            # ⚠ 這個容器本身的天花板就在 46 fps 左右（無同伴的對照組也只有這個數字），
            #   所以「≥45」等於是在跟容器的上限比，不是在測遊戲。
            #   絕對門檻只用來抓「明顯掉到不能玩」，真正的判準是上面那個相對值。
            #   ⚠⚠ 這裡量的是雲端容器，**不是真實手機**。真機效能只能靠實機驗證。
            ck("有同伴時 FPS 仍 ≥ 30（容器天花板約 46，這條只抓明顯的崩潰）",
               f_on>=30, round(f_on,1))
        # ⚠ 絕對 FPS 只有「單獨跑這一支」時才有意義。35 支平行時整台機器的
        #   絕對值會掉到個位數——那量到的是容器負載，不是遊戲效能。
        #   （這正是專案方法論第 3 條：跨批次的數字不能互比。）
        #   所以絕對門檻只在明顯沒有被搶資源時才檢查。
        ck("無 JS 錯誤", not any(x['errs'] for x in off+on),
           [x['errs'][:1] for x in off+on if x['errs']][:2])
        return 0

rc=asyncio.run(main())
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails}"); sys.exit(1)
print("=== 效能測試通過 ===")
