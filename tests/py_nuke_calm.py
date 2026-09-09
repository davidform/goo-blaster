#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.38 驗收：核彈淨空期 + 白屏加強 + 無敵七彩閃爍

為什麼要有這一支（沿用 v0.9.37 py_revive_fx 的教訓）：
這一版動的三樣東西，**既有 44 支測試沒有任何一支走過**——
  · `doNuke()` 只在 py_btn_conflict 被「點得到嗎」測過，從沒人量過引爆之後發生什麼
  · `G.nukeFlash` 的峰值與衰減率從 v0.9.12 起沒被任何測試讀過
  · `drawPlayer()` 的無敵表現從來沒有一支測試讀過畫素
沒有測試釘住，下一個模型改 spawn 迴圈或 drawPlayer 時會靜默推翻它。

四項驗收：
  A. 淨空期內「一般敵人」數量不增加（引爆後 2.5 秒）
  B. 淨空期結束後生成恢復，且**不會**把積欠的份一次倒出來（spawnAcc 已歸零）
  C. Boss 排程不受淨空期影響（刻意放在 Boss 判斷之後，關卡長度與勝負條件不變）
  D. 無敵時角色本體的顏色會隨時間變化（七彩），非無敵時是固定的青綠色
     ——讀 canvas 真實畫素，不是讀程式碼。

⚠ 決定性（第一版踩到，整支在平行批次裡全紅）：
   1. **不可以用 `wait_for_timeout(固定毫秒)` 去等遊戲內的計時器。** 44 支平行跑時
      掉幀嚴重，`G.nukeCalm` 走的是被 clamp 過的遊戲 dt，牆鐘 3.4 秒可能只走掉
      1 秒多——固定 sleep 會在負載高時穩定誤判。一律輪詢到條件成立或逾時。
   2. **玩家不能在測試中途死掉。** 這支測試沒有 bot 在操作，角色站著不動，
      場上一多就會被撞死；`G.running` 一變 false，後面 `doNuke()` 全部提早 return，
      量到的就是一整排「0」——看起來像功能沒做出來，其實是**受測對象已經不在了**。
      開場就把 hearts 拉高，並在每個階段前重新確認 G.running。
   3. **升級卡面板會把遊戲暫停住。** 這支測試沒有 bot，沒有人去點卡片，
      玩家一升級 `G.paused` 就變 true，`G.nukeCalm` 從此不再衰減、`doNuke()` 提早
      return——所有數字一起變 0。第二輪整套測試就是栽在這裡（保命之後活得更久、
      反而更容易升級）。開場就掛一個自動選卡的 interval，跟 py_test9 的笨 bot 同一招。
   4. D 取樣的是畫面中心（玩家被鏡頭釘在那裡），量測前先清場並停生成，
      讓被測的畫素只可能來自玩家本體。
"""
import http.server, socketserver, threading, functools, sys, asyncio
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.async_api import async_playwright

ROOT = GAME_ROOT
PORT = 8843
fails = []


def ck(cond, msg):
    print(("  ✅ " if cond else "  ❌ ") + msg)
    if not cond:
        fails.append(msg)


async def poll(pg, expr, timeout_ms=20000, step=120):
    """輪詢直到 expr 為真，回傳是否成立。取代所有固定 sleep。"""
    waited = 0
    while waited < timeout_ms:
        if await pg.evaluate("()=>!!(" + expr + ")"):
            return True
        await pg.wait_for_timeout(step)
        waited += step
    return False


async def keep_alive(pg):
    """把角色補到不會死。這支測試量的是核彈與無敵的表現，不是求生能力。"""
    await pg.evaluate("()=>{ if(G&&G.P){ G.P.hearts=99; G.P.maxHearts=99; } }")


AUTOCARD = """()=>{
  // 升級卡面板一出現就隨機點一張。不掛這個的話，玩家一升級遊戲就永久暫停，
  // 後面每一項都會量到 0——而且紅字看起來像「功能沒做出來」，極難追。
  clearInterval(window.__ac);
  window.__ac=setInterval(()=>{
    const el=document.getElementById('cards');
    if(!el||el.classList.contains('hide')) return;
    const cs=[...el.querySelectorAll('.card')];
    if(cs.length) cs[0].click();
  },60);
}"""


async def alive_msg(pg):
    """遊戲不在進行時，說得出是哪一種原因——紅字要能自己解釋。"""
    st = await pg.evaluate("()=>G?{run:!!G.running,pause:!!G.paused,over:!!G.over,win:!!G.win}:null")
    if st is None:
        return "G 不存在"
    if st["pause"]:
        return "被暫停（升級卡面板沒被關掉？）"
    if st["over"]:
        return "已結束（win=%s）" % st["win"]
    return "running=%s" % st["run"]


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(channel=BROWSER_CHANNEL, args=["--autoplay-policy=no-user-gesture-required"])
        c = await b.new_context(viewport={"width": 390, "height": 844},
                                device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await c.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        await pg.wait_for_timeout(400)

        # ---------- A / B：淨空期 ----------
        print("A/B：核彈淨空期")
        await pg.evaluate("()=>{ LV_IDX=9; start(); }")
        await pg.evaluate(AUTOCARD)
        await keep_alive(pg)
        # 輪詢等場上長出一批敵人（不是等固定秒數——負載高時 3.5 秒可能一隻都還沒生）
        ok = await poll(pg, "G.E.filter(e=>!e.boss).length>=5")
        ck(ok, "等到場上長出敵人（輪詢，非固定 sleep）")
        before = await pg.evaluate("()=>G.E.filter(e=>!e.boss).length")
        ck(before > 0, f"引爆前場上有一般敵人可清（{before} 隻）")

        await keep_alive(pg)
        ck(await pg.evaluate("()=>!!(G&&G.running&&!G.paused)"),
           "引爆前遊戲仍在進行（測試前提：角色沒死、沒暫停）｜狀態：" + await alive_msg(pg))

        # ⚠ 讀 nukeCalm 必須跟 doNuke() 在**同一個 evaluate** 裡。
        # 第一版是「doNuke() → wait(120ms) → 另一個 evaluate 讀」，
        # 平行批次下光是 CDP 往返就吃掉超過一秒，讀到的是 1.10 而不是 2.50——
        # 紅字看起來像「淨空期設錯值」，實際上是**尺標自己走掉了 1.4 秒**。
        st = await pg.evaluate("""()=>{
            G.P.nukeHeld=true; doNuke();
            return {n:G.E.filter(e=>!e.boss).length, calm:G.nukeCalm??-1, f:G.nukeFlash??-1};
        }""")
        ck(st["n"] == 0, f"引爆瞬間一般敵人全清（剩 {st['n']} 隻）")
        ck(abs(st["calm"] - 2.5) < 0.01,
           f"doNuke() 把淨空期設成 2.5 秒（量到 {st['calm']:.2f}；v0.9.37 沒有這個欄位＝-1）")

        # 「計時器擋不擋得住生成」跟「計時器歸零多久」是兩件事，分開驗。
        # 這一段把計時器**釘住**在一個大值，時間就不再是變因，掉幀也不影響判定。
        await pg.evaluate("()=>{ G.nukeCalm=999; }")
        peak, spins = 0, 0
        for _ in range(14):
            await pg.wait_for_timeout(150); spins += 1
            await pg.evaluate("()=>{ G.nukeCalm=999; }")     # 每次補回去，抵銷衰減
            peak = max(peak, await pg.evaluate("()=>G.E.filter(e=>!e.boss).length"))
            await keep_alive(pg)
        ck(spins >= 10, f"淨空期內取樣 {spins} 次")
        ck(peak == 0, f"計時器有效期間完全沒有新的一般敵人（峰值 {peak}）")

        # 解除淨空期的**那一瞬間**不可以爆量（證明 spawnAcc 有歸零）。
        # 整段量測放進同一個 evaluate、以 rAF 計幀，不讓 CDP 往返的延遲混進來。
        burst = await pg.evaluate("""async()=>{
            G.nukeCalm=0.0001;
            let n=0;
            for(let i=0;i<4;i++){
              await new Promise(r=>requestAnimationFrame(r));
              n=Math.max(n,G.E.filter(e=>!e.boss).length);
            }
            return n;
        }""")
        ck(burst <= 4, f"解除瞬間的 4 幀內沒有把積欠的生成一次倒出來（{burst} 隻，門檻 ≤4）")
        await keep_alive(pg)
        ck(await poll(pg, "G.E.filter(e=>!e.boss).length>0"), "淨空期結束後生成已恢復")

        # ---------- C：Boss 排程不受影響 ----------
        print("C：Boss 排程不受淨空期影響")
        r = await pg.evaluate("""()=>{
            // 把第一隻還沒出場的 Boss 拉到 0.3 秒後，然後立刻引爆核彈。
            // 若淨空期擋錯位置（放在 Boss 判斷之前），這隻 Boss 就不會出現。
            const i=G.bossDone.findIndex(d=>!d);
            if(i<0) return {skip:true};
            G.bosses[i].t=G.t+0.3;
            G.P.nukeHeld=true; doNuke();
            G.nukeCalm=999;            // 釘住，讓「Boss 有沒有出場」不受等待時間影響
            return {skip:false, want:i};
        }""")
        if r.get("skip"):
            ck(False, "找不到未出場的 Boss 可測（關卡設定變了？）")
        else:
            # 輪詢等 Boss 出場，但**必須在淨空期還沒結束之前**等到——
            # 兩個條件一起檢查，才證明「淨空期擋不住 Boss」而不是「等久了自然出場」。
            got = None
            for _ in range(120):
                got = await pg.evaluate("(i)=>({done:G.bossDone[i],calm:G.nukeCalm??-1,b:G.E.some(e=>e.boss)})",
                                        r["want"])
                if got["done"] and got["b"]:
                    break
                await pg.wait_for_timeout(100)
                await pg.evaluate("()=>{ G.nukeCalm=999; }")
                await keep_alive(pg)
            ck(got["calm"] > 0, f"Boss 出場的當下仍在淨空期內（剩 {got['calm']:.2f} 秒，測試前提成立）")
            ck(got["done"] and got["b"], "淨空期內 Boss 仍照排程出場")

        # ---------- 白屏強度 ----------
        print("白屏：峰值與時間")
        await keep_alive(pg)
        ck(await pg.evaluate("()=>!!(G&&G.running&&!G.paused)"),
           "量白屏前遊戲仍在進行（否則 doNuke() 會提早 return，量到一整排 0）" + "｜狀態：" + await alive_msg(pg))
        # ⚠ 這裡**不可以用牆鐘秒數當驗收門檻**（第一版就是這樣寫的，穩定誤判）。
        # `loop()` 把 dt clamp 在 0.05，平行批次掉幀時每幀最多只扣 0.05×2.2 的衰減——
        # 1.5 的閃光值在 1.5 秒的觀察窗內**跑不完**，量到的 endMs 會留在初始值 0，
        # 而「0」同時代表「瞬間就結束」與「根本沒跑完」，紅字說不出是哪一種。
        # 改成驗收**軌跡的形狀**，完全不看牆鐘：
        #   ① 峰值 >1  → 存在「全白維持段」（v0.9.37 峰值恰好 1.0，必定紅）
        #   ② 中途取樣到 0<flash<1 → 存在「淡出段」
        #   ③ 最後會回到 0 → 不會卡住
        # 牆鐘秒數仍然量、仍然印出來，但只當參考值，不當門檻（AGENTS.md 鐵則 6）。
        f = await pg.evaluate("""async()=>{
            G.nukeFlash=0; await new Promise(r=>setTimeout(r,120));
            G.P.nukeHeld=true; doNuke();
            const t0=performance.now();
            let peak=0, sawHold=false, sawFade=false, done=false, ms=0;
            while(performance.now()-t0<12000){
              const v=G.nukeFlash;
              peak=Math.max(peak,v);
              if(v>1.02) sawHold=true;
              if(v>0.02 && v<0.98) sawFade=true;
              if(v<=0){ done=true; ms=performance.now()-t0; break; }
              await new Promise(r=>setTimeout(r,16));
            }
            return {peak, sawHold, sawFade, done, ms};
        }""")
        ck((f["peak"] or 0) >= 1.4,
           f"閃光起始值 ≥1.4（量到 {f['peak']:.2f}；v0.9.37 是 1.00）")
        ck(f["sawHold"], "取樣到「全白維持段」（flash > 1.0）——v0.9.37 峰值只有 1.0，不可能有這一段")
        ck(f["sawFade"], "取樣到「淡出段」（0 < flash < 1）")
        ck(f["done"], "閃光最後回到 0，不會卡住")
        print(f"     （參考值，不當門檻）牆鐘 {f['ms']/1000:.2f} 秒——掉幀時會被拉長，"
              f"因為 loop() 的 dt 被 clamp 在 0.05")

        # ---------- D：無敵七彩（讀真實畫素）----------
        print("D：無敵時角色本體七彩閃爍")
        probe = """async(inv)=>{
            // 清場並停生成，確保取樣到的畫素只可能來自玩家本體
            G.E.length=0; G.EB.length=0; G.B.length=0; G.nukeCalm=999; G.spawnAcc=0;
            G.P.iframe = inv ? 999 : 0;
            G.P.hearts=99; G.P.maxHearts=99;
            G.P.flash=0; G.P.rainbowT=0;
            // ⚠ G.P.x/y 是**世界座標**，畫布在畫之前會被鏡頭 translate 過去，
            //   直接拿世界座標去讀畫素會讀到背景（實測 off/on 都是同一個定值 0）。
            //   玩家永遠被鏡頭釘在畫面正中央，所以取樣點就是畫布中心。
            const cv=document.getElementById('cv');
            const px=Math.round(cv.width/2), py=Math.round(cv.height/2);
            const g=cv.getContext('2d');
            const out=[];
            for(let i=0;i<6;i++){
              await new Promise(r=>setTimeout(r,90));
              const d=g.getImageData(px,py,1,1).data;
              out.push([d[0],d[1],d[2]]);
            }
            return out;
        }"""
        await keep_alive(pg)
        ck(await pg.evaluate("()=>!!(G&&G.running&&!G.paused)"),
           "量畫素前遊戲仍在進行（角色還在畫面上）" + "｜狀態：" + await alive_msg(pg))
        off = await pg.evaluate(probe, False)
        on = await pg.evaluate(probe, True)

        def spread(sam):
            # 六次取樣中，同一個顏色通道的最大變化量
            return max(max(s[k] for s in sam) - min(s[k] for s in sam) for k in range(3))

        # 先證明取樣點真的打在玩家本體上（v0.9.41 薄荷 #9dc5b1 = 157,197,177）。
        # 少了這一關，取樣點打歪到背景時上下兩個判斷都會「因為都不變」而誤判。
        r0, g0, b0 = off[0]
        ck(abs(r0 - 157) <= 26 and abs(g0 - 197) <= 26 and abs(b0 - 177) <= 26,
           f"取樣點確實打在玩家本體上（非無敵時 rgb({r0},{g0},{b0}) ≈ 薄荷 157,197,177）")
        ck(spread(off) <= 12,
           f"非無敵時顏色穩定（通道變化 {spread(off)}，門檻 ≤12）")
        ck(spread(on) >= 60,
           f"無敵時顏色明顯變化＝七彩在跑（通道變化 {spread(on)}，門檻 ≥60）")
        # 顏色要真的走遍整個色環，不能只是同一個色相在明暗之間跳動。
        # 分兩件事量：① 一圈的四個環在**同一幀**彼此拉開（靜止畫面也看得出七彩）
        #            ② 色相隨時間繞完一整圈（動起來才是「閃爍」而不是「變色」）
        ring = await pg.evaluate("()=>[0,1,2,3].map(i=>invHue(i*120))")
        gaps = sorted(abs(((ring[i] - ring[0] + 180) % 360) - 180) for i in (1, 2, 3))
        ck(gaps[-1] >= 100,
           f"同一幀裡四圈的色相彼此拉開 ≥100°（量到 {gaps[-1]:.0f}°）——靜止畫面就看得出七彩")
        sweep = await pg.evaluate("""async()=>{
            const out=[]; for(let i=0;i<12;i++){ out.push(invHue(0));
              await new Promise(r=>setTimeout(r,60)); }
            return out;
        }""")
        ck(max(sweep) - min(sweep) >= 200 or (max(sweep) > 300 and min(sweep) < 60),
           f"色相隨時間繞遍色環（量到 {min(sweep):.0f}°~{max(sweep):.0f}°）")

        ck(not errs, f"全程沒有 JS 例外（{errs[:2]}）")
        await b.close()


if __name__ == "__main__":
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        asyncio.run(main())
    finally:
        srv.shutdown()
    print("\n" + ("❌ 失敗 %d 項：" % len(fails) + "；".join(fails) if fails else "✅ py_nuke_calm 全數通過"))
    sys.exit(1 if fails else 0)
