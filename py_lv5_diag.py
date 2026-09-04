#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真人回報「第5關過不了」的診斷：量玩家實際 DPS vs 章節 Boss 血量。

第5關是 v0.9.23 新升格的章節 Boss 關，從來沒有被真人玩過就上線了。
這支要回答：到底是 Boss 太肉、玩家太弱、還是時間不夠。
"""
import http.server, socketserver, threading, functools, json
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8830
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)

    print("=== 1. 各關的 Boss 血量結構 ===")
    r=pg.evaluate("""()=>{
        const out=[];
        for(const lv of [0,1,2,3,4,5,6,7,8,9,14,24,49]){
            const L=LEVELS[lv];
            const bs=buildBosses(L);
            const mid=bs.filter(x=>!x.superBoss), sup=bs.filter(x=>x.superBoss);
            out.push({關:lv+1, dur:L.dur, bossHp倍率:L.bossHp,
                      一般Boss數:mid.length, 一般Boss血:mid.length?mid[0].hp:0,
                      章節Boss血:sup.length?sup[0].hp:null,
                      章節Boss出場秒:sup.length?sup[0].t:null,
                      倍數:sup.length&&mid.length?+(sup[0].hp/mid[0].hp).toFixed(1):null});
        }
        return out;
    }""")
    print(f"{'關':>4} {'時長':>5} {'一般Boss血':>11} {'章節Boss血':>11} {'出場秒':>7} {'倍數':>6}")
    for x in r:
        print(f"{x['關']:>4} {x['dur']:>5} {x['一般Boss血']:>11,} "
              f"{(x['章節Boss血'] or 0):>11,} {str(x['章節Boss出場秒'] or '-'):>7} {str(x['倍數'] or '-'):>6}")

    print("\n=== 2. 玩家在各關能打出多少 DPS（實測，非估算）===")
    # 做法：直接放一隻超高血 Boss 當沙包，量固定秒數內掉多少血
    def dps(lv, plv, wep, secs=6):
        pg.evaluate("""([lv,plv,wep])=>{
            META={}; LV_IDX=lv; start(); G.hasMoved=true; DIAG.touch=3;
            G.E.length=0; G.B.length=0;
            G.P.lv=plv; G.P.wep=wep;
            // 沙包：不會動、不會攻擊、血量極高
            const cfg={...BOSS_POOL[0], hp:9e7, r:60, spd:0, dmg:0, atk:'ring', atkT:9e9, bspd:1, name:'DUMMY', skin:[]};
            spawnBoss(cfg);
            const e=G.boss; e.x=G.P.x+120; e.y=G.P.y; e.spd=0; e.shootCD=9e9;
            window.__k=setInterval(()=>{ const b=G.boss; if(b){ b.x=G.P.x+120; b.y=G.P.y; b.shootCD=9e9; } G.P.hearts=G.P.maxHearts; },100);
            window.__hp0=G.boss.hp; window.__t0=G.t;
        }""",[lv,plv,wep])
        pg.wait_for_timeout(int(secs*1000)+400)
        r=pg.evaluate("()=>{ clearInterval(window.__k); const b=G.boss; return {d:window.__hp0-(b?b.hp:0), dt:G.t-window.__t0}; }")
        return r["d"]/max(0.001,r["dt"])

    cases=[
        ("第5關 · Lv.5 · 起始武器",      4, 5,  {"bubble":1}),
        ("第5關 · Lv.8 · 主武器3級",     4, 8,  {"bubble":3}),
        ("第5關 · Lv.10 · 主武器5級",    4, 10, {"bubble":5}),
        ("第5關 · Lv.12 · 三武器都有",   4, 12, {"bubble":5,"graffiti":3,"yoyo":3}),
        ("第10關 · Lv.12 · 三武器",      9, 12, {"bubble":5,"graffiti":3,"yoyo":3}),
    ]
    res={}
    for label,lv,plv,wep in cases:
        d=dps(lv,plv,wep)
        res[label]=d
        print(f"  {label:<28} {d:>8.0f} DPS")

    print("\n=== 3. 打死第5關章節 Boss 需要多久 ===")
    hp5=[x for x in r if x['關']==5][0]['章節Boss血']
    hp10=[x for x in r if x['關']==10][0]['章節Boss血']
    print(f"  第5關章節 Boss {hp5:,} HP，出場在第 {[x for x in r if x['關']==5][0]['章節Boss出場秒']} 秒（關卡長 140 秒）")
    for label,d in res.items():
        if '第5關' in label:
            print(f"    {label:<28} 需要 {hp5/d:>6.0f} 秒")
    print(f"\n  對照：第10關章節 Boss {hp10:,} HP")
    for label,d in res.items():
        if '第10關' in label:
            print(f"    {label:<28} 需要 {hp10/d:>6.0f} 秒")

    print("\n=== 4. 笨bot 在第5關實際能練到幾級、拿到什麼武器 ===")
    pg.evaluate("""()=>{
        META={}; LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        // 自動選卡（模擬玩家一定會選），並記錄升級歷程
        window.__lvlog=[];
        window.__auto=setInterval(()=>{
            if(!cardsEl.classList.contains('hide')){
                const list=rollCards();
                if(list.length) applyCard(list[0]);
            }
            window.__lvlog.push({t:+G.t.toFixed(1), lv:G.P.lv, pend:G.pendingCards|0});
            G.P.hearts=G.P.maxHearts;      // 不死，只看成長曲線
        },250);
    }""")
    pg.wait_for_timeout(1000)
    # 加速時間：直接反覆呼叫 update 推進
    prog=pg.evaluate("""()=>new Promise(res=>{
        let n=0;
        const step=()=>{
            for(let i=0;i<40;i++){ if(!G.paused && G.running) update(0.033,0.033); }
            n++;
            if(G.t>135 || n>600 || !G.running) res({t:+G.t.toFixed(1), lv:G.P.lv, wep:JSON.parse(JSON.stringify(G.P.wep)), kills:G.kills, running:G.running});
            else setTimeout(step,0);
        };
        step();
    })""")
    pg.evaluate("()=>clearInterval(window.__auto)")
    print(f"  推進到第 {prog['t']} 秒：玩家 Lv.{prog['lv']}、武器 {prog['wep']}、擊殺 {prog['kills']}")
    d=dps(4, prog['lv'], prog['wep'])
    print(f"  這個 build 的 DPS = {d:.0f} → 打死 {hp5:,} HP 的章節 Boss 需要 {hp5/d:.0f} 秒")
    b.close()
srv.shutdown()
