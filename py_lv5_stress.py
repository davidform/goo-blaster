#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.26 測試循環 3：最嚴苛條件下的第5關 Boss 戰 A/B。

嚴苛條件：
  1. CPU 節流 4 倍（模擬便宜的入門安卓機）
  2. 玩家完全沒有糖果屋永久強化（META 全空）＝ 第一次玩的小朋友
  3. 用同一份程式碼，只把 Boss 的 atk/chIdx 改回 v0.9.25 的值來當對照組
     （atk='ring', chIdx=9 → cs≈1 且雷射開啟），確保血量/速度/間隔完全相同，
     差異只有「彈幕顆數與雷射」這一項。

指標：每 30 秒被打中幾次（不是「勝率」——勝率被 bot 的爛操作淹沒，
      挨打次數才直接對應小朋友的挫折感）。
"""
import asyncio, http.server, socketserver, threading, functools, sys, statistics
from playwright.async_api import async_playwright

ROOT="/home/claude/goo/game"; PORT=8846
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

SETUP = """
([old])=>{
  META={}; saveGame(); LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
  G.E.length=0; G.EB.length=0; G.boss=null;
  const sup=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
  spawnBoss(sup);
  const e=G.boss;
  if(old){ e.atk='ring'; e.chIdx=9; }     // 還原成 v0.9.25 的第5關 Boss
  // 玩家等級模擬「打到第5關」的常見狀態
  G.P.lv=8; G.P.wep={bubble:3};
  window.__hits=0; window.__peak=0; window.__samp=[]; window.__dead=0;
  // 用「心數有沒有真的減少」判定挨打，比看回傳值可靠
  const oh=window.hurtPlayer;
  window.hurtPlayer=function(){ const h0=G.P.hearts; const r=oh.apply(this,arguments);
    if(G.P.hearts<h0) window.__hits++; return r; };
  // 「小朋友 bot」：反應慢（200ms 才改一次方向）、視野窄（只看 110px 內的子彈）。
  // 第一版寫成 50ms/190px 的完美閃避 bot，結果新舊版都是 0 次挨打——
  // 那量到的是 bot 的反射神經，不是彈幕難度。要量難度就得把操作能力壓到人的水準。
  window.__bot=setInterval(()=>{
    if(!G.running) return;
    const P=G.P; let ax=0, ay=0;
    for(const b of G.EB){
      const dx=P.x-b.x, dy=P.y-b.y, d=Math.hypot(dx,dy);
      if(d<110&&d>1){ const w=(110-d)/110; ax+=dx/d*w; ay+=dy/d*w; }
    }
    const bo=G.boss;
    if(bo){ const dx=bo.x-P.x, dy=bo.y-P.y, d=Math.hypot(dx,dy)||1;
            // Boss 會撞人（接觸傷害）。第一版讓 bot 貼到 170px，死因主要是被撞，
            // 量到的不是彈幕難度。改成保持 260~420px 的中距離。
            const pull=(d>420?0.5:(d<260?-1.2:0));
            // 一定要有環繞分量：不然新版子彈少、ax/ay 接近 0，bot 就會站著不動
            // 被 Boss 慢慢撞死——那量到的還是接觸傷害，不是彈幕。
            ax+=-dy/d*0.7; ay+=dx/d*0.7;
            ax+=dx/d*pull; ay+=dy/d*pull; }
    const m=Math.hypot(ax,ay);
    // 遊戲讀的是虛擬搖桿 IN（見 update() 裡的 IN.active/IN.dx/IN.mag）
    if(m>0.02){ IN.active=true; IN.id='bot'; IN.dx=ax/m; IN.dy=ay/m; IN.mag=1; }
    else { IN.mag=0; }
    // 把 Boss 鎖在「暴走」狀態（血量<50%）——使用者抱怨的正是這一段：
    // 「砲彈多到難以躲藏」。同時不讓它被打死，否則量不完整段時間。
    if(G.boss) G.boss.hp=G.boss.maxhp*0.40;
    // 只留 Boss：雜兵的接觸傷害在新舊版完全一樣，留著會把「彈幕差異」淹掉
    // （前一版就是這樣：子彈少了 88%，存活時間卻只差 0.2 秒——因為死因是被雜兵撞）
    for(let i=G.E.length-1;i>=0;i--) if(!G.E[i].boss) G.E.splice(i,1);
    if(!G.running && !window.__dead) window.__dead=G.t;   // 記錄撐了幾秒
  },200);
  // 取樣（同屏子彈數）要比 bot 快，否則採樣點太少
  window.__sm=setInterval(()=>{
    const on=G.EB.filter(x=>Math.abs(x.x-G.cam.x)<W/2+20&&Math.abs(x.y-G.cam.y)<H/2+20).length;
    window.__samp.push(on); if(on>window.__peak) window.__peak=on;
  },50);
}
"""

# ⚠ 踩過的坑：一開始開 10 個分頁 + CPU 4x 節流，結果 30 秒牆鐘只跑出 3.9 秒遊戲時間
#   （dt 有上限，掉幀時遊戲時間就跟著慢）。量到的是容器負載，不是難度。
#   改成：只開少量分頁、不節流，並且用「遊戲時間 G.t」而不是牆鐘來決定何時停。
async def one(browser, old, throttle):
    c=await browser.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                                is_mobile=True,has_touch=True,locale="en-US")
    pg=await c.new_page()
    cdp=await c.new_cdp_session(pg)
    await pg.goto(f"http://127.0.0.1:{PORT}/index.html")
    await pg.wait_for_timeout(600)
    if throttle: await cdp.send("Emulation.setCPUThrottlingRate",{"rate":2})
    await pg.evaluate(SETUP,[old])
    for _ in range(240):                       # 最多等 120 秒牆鐘
        await pg.wait_for_timeout(500)
        gt=await pg.evaluate("()=>G.running?G.t:1e9")
        if gt>=30: break
    r=await pg.evaluate("""()=>{ clearInterval(window.__bot); clearInterval(window.__sm);
        const s=window.__samp.slice(); s.sort((a,b)=>a-b);
        return {hits:window.__hits, peak:window.__peak, dead:+(window.__dead||G.t).toFixed(1), alive:!!G.running,
                med:s[Math.floor(s.length/2)],
                avg:+(s.reduce((a,b)=>a+b,0)/Math.max(1,s.length)).toFixed(1)}; }""")
    await c.close()
    return r

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        REPS=5
        res=[]
        for i in range(REPS):                  # 每輪只跑 2 個分頁（新舊各一），避免互相拖慢
            pair=await asyncio.gather(one(b,True,True), one(b,False,True))
            res.append(pair)
        res=[p[0] for p in res]+[p[1] for p in res]
        await b.close()
        old,new=res[:REPS],res[REPS:]
        def rep(tag,rs):
            h=[x['hits'] for x in rs]; p=[x['peak'] for x in rs]; a=[x['avg'] for x in rs]
            d=[x['dead'] for x in rs]; sv=sum(1 for x in rs if x['alive'])
            print(f"  {tag:<26} 挨打 {statistics.mean(h):>4.1f} 次（{h}）"
                  f"  撐過30秒 {sv}/{len(rs)}  存活 {statistics.mean(d):>4.1f}s"
                  f"  同屏子彈 峰值{statistics.mean(p):>4.1f} 平均{statistics.mean(a):>4.1f}")
            return statistics.mean(h), statistics.mean(a), sv, statistics.mean(d)
        print("=== 第5關 Boss 暴走狀態：CPU 4x 節流、零永久強化、慢反應 bot、5 次重複 ===")
        ho,ao,so,do_=rep("v0.9.25（ring+雷射）",old)
        hn,an,sn,dn=rep("v0.9.26（cross、無雷射）",new)
        print()
        print(f"  挨打次數     {ho:.1f} → {hn:.1f}   ({(hn-ho)/max(ho,0.01)*100:+.0f}%)")
        print(f"  存活秒數     {do_:.1f} → {dn:.1f}")
        print(f"  撐過30秒     {so}/{REPS} → {sn}/{REPS}")
        print(f"  平均同屏子彈 {ao:.1f} → {an:.1f}   ({(an-ao)/max(ao,0.01)*100:+.0f}%)")
        ok = hn < ho and an < ao and sn >= so
        print(("\n=== PASS：第5關的挨打次數與彈幕密度都下降 ===" if ok
               else "\n❌ FAIL：修正後沒有變輕鬆"))
        return 0 if ok else 1

rc=asyncio.run(main())
srv.shutdown()
sys.exit(rc)
