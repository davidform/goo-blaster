#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.20 稽核修正的自動驗收。

A-1 永久強化「愛用武器」必須在每一個關卡都完整生效
    （舊版被 startWep 事先吃掉額度，第91-100關買了等於 +0，形同白花 1070 幣）
A-2 死碼必須真的移除（.lvbtn 那組 CSS、G.best、P.heart、P.vx/vy）
A-3 開發診斷預設隱藏，連點版本號 5 下才顯示；但「偵測不到觸控」的警告不受影響
"""
import http.server, socketserver, threading, functools, sys, re
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8781
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+("  "+extra if extra else ""))
    if not cond: fails.append(name)

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page():
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(500)
        return pg,c,errs

    print("=== A-1：永久強化「愛用武器」在每一關都要完整生效 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        const out=[];
        for(let lv=0; lv<LEVELS.length; lv+=5){
            META={}; LV_IDX=lv; start();
            const before=G.P.wep.bubble;
            META={wep:3}; start();
            const after=G.P.wep.bubble;
            out.push({關卡:lv+1, 無強化:before, 買滿後:after, 實際獲得:after-before});
        }
        META={};
        return out;
    }""")
    for x in r:
        ck(f"第{x['關卡']:>3}關 愛用武器 +3 完整生效",
           x["實際獲得"]==3, f"{x['無強化']}→{x['買滿後']} (+{x['實際獲得']})")
    # 起始總戰力不能因為這個修正而暴增或暴跌
    r2=pg.evaluate("""()=>{
        const out=[];
        for(const lv of [10,24,49]){
            META={}; LV_IDX=lv; start();
            out.push({關卡:lv+1, 總等級:G.P.wep.bubble+G.P.wep.graffiti+G.P.wep.yoyo});
        }
        return out;
    }""")
    exp={11:3, 25:6, 50:12}   # v0.9.23：每章 5 關後，關卡→章節的對應改變
    for x in r2:
        ck(f"第{x['關卡']}關 起始武器總等級 = {exp[x['關卡']]}",
           x["總等級"]==exp[x["關卡"]], str(x["總等級"]))
    ck("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()

    print("\n=== A-2：死碼必須真的移除 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        LV_IDX=0; start();
        return {
            P有vx: 'vx' in G.P, P有vy: 'vy' in G.P,
            P有heart: 'heart' in G.P,
            G有best: 'best' in G,
            // .lvbtn 那組 CSS 規則是否還在樣式表裡
            lvbtn規則數: [...document.styleSheets[0].cssRules]
                .filter(r=>r.selectorText && /\\.lvbtn|\\.stat\\b|\\.tag\\b/.test(r.selectorText)).length
        };
    }""")
    print(f"  {r}")
    ck("P.vx 已移除", not r["P有vx"])
    ck("P.vy 已移除", not r["P有vy"])
    ck("P.heart 已移除", not r["P有heart"])
    ck("G.best 已移除", not r["G有best"])
    ck(".lvbtn/.stat/.tag 的 CSS 規則已移除", r["lvbtn規則數"]==0, str(r["lvbtn規則數"]))
    ck("移除後遊戲仍正常運作（無 JS 錯誤）", not errs, str(errs[:2]))
    pg.close(); c.close()

    print("\n=== A-3：開發診斷預設隱藏、連點 5 下才顯示 ===")
    pg,c,errs=page()
    r=pg.evaluate("()=>({on:DIAG_ON, txt:document.getElementById('diag').textContent})")
    print(f"  預設: DIAG_ON={r['on']} 內容={r['txt']!r}")
    ck("預設關閉", r["on"]==False)
    ck("預設只顯示版本號、不顯示 touch/pointer/audio",
       "touch" not in r["txt"] and "audio" not in r["txt"], r["txt"])
    ck("版本號仍看得到", "v0.9." in r["txt"], r["txt"])
    # ⚠ 五次點擊必須在「同一個 JS 回合」內送出。
    #   舊版是 Python 端每點一次 sleep 30ms，17 支測試平行搶 CPU 時那個 30ms 會被
    #   拉長到超過 1.2 秒的重置門檻，計數歸零 → 測試偶發失敗（實測平行時必掛、
    #   單獨跑必過）。照方法論第 9 條：不要再補等待時間，從結構上消除時序依賴。
    pg.evaluate("""()=>{ const el=document.getElementById('diag');
        for(let i=0;i<5;i++) el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }""")
    pg.wait_for_timeout(900)
    r2=pg.evaluate("()=>({on:DIAG_ON, txt:document.getElementById('diag').textContent})")
    print(f"  連點5下後: DIAG_ON={r2['on']}")
    ck("連點 5 下後開啟", r2["on"]==True)
    ck("開啟後看得到 touch/audio 診斷", "touch" in r2["txt"] and "audio" in r2["txt"], r2["txt"][:80])
    # 再連點 5 下要能關掉（同樣一次送出）
    pg.evaluate("""()=>{ const el=document.getElementById('diag');
        for(let i=0;i<5;i++) el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }""")
    pg.wait_for_timeout(900)
    ck("再連點 5 下可以關掉", pg.evaluate("()=>DIAG_ON")==False)
    # 間隔太久不應該累積
    pg.evaluate("()=>{ diagTaps=0; }")
    tap3="""()=>{ const el=document.getElementById('diag');
        for(let i=0;i<3;i++) el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); }"""
    pg.evaluate(tap3)
    pg.wait_for_timeout(1400)   # 超過 1200ms 的重置門檻（這一項就是在測時序，保留真實等待）
    pg.evaluate(tap3)
    ck("點擊間隔超過 1.2 秒會重新計數（不會誤觸）", pg.evaluate("()=>DIAG_ON")==False)
    ck("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()
    b.close()
srv.shutdown()
print()
if fails: print("❌ 失敗："+", ".join(fails)); sys.exit(1)
print("=== 全部通過 ===")
