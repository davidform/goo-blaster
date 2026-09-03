#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真人回報「第5關Boss彈幕多到躲不掉，小朋友會信心崩潰」——量實際的彈幕密度。

390px 寬的手機螢幕上，同時有幾顆子彈是「看得懂」的？
這支量：每一波齊射幾顆、間隔多久、螢幕上同時最多幾顆、以及有沒有雷射。
"""
import http.server, socketserver, threading, functools, sys

fails=[]
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8834
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)

    print("=== 1. 各種 Boss 攻擊型態一次齊射幾顆 ===")
    print("   cross  正常 8 顆 / 暴走 12 顆")
    print("   spiral 正常 3+3=6 顆 / 暴走 4+3=7 顆")
    print("   ring   正常 14+5=19 顆 / 暴走 20+5=25 顆   ← 章節Boss用這個")

    print("\n=== 2. 各章節 Boss 的實際攻擊參數 ===")
    r=pg.evaluate("""()=>{
        const out=[];
        for(const lv of [4,9,14,24,49]){
            const L=LEVELS[lv];
            const bs=buildBosses(L);
            const sup=bs.filter(x=>x.superBoss)[0];
            const mid=bs.filter(x=>!x.superBoss)[0];
            out.push({關:lv+1,
                章節Boss:{atk:sup.atk, 間隔:+sup.atkT.toFixed(2), 暴走間隔:+(sup.atkT*0.62).toFixed(2),
                          彈速:Math.round(sup.bspd), 雷射:(sup.chIdx|0)>=5},
                一般Boss:{atk:mid.atk, 間隔:+mid.atkT.toFixed(2), 彈速:Math.round(mid.bspd)}});
        }
        return out;
    }""")
    for x in r:
        s=x['章節Boss']; m=x['一般Boss']
        cs = min(1, 0.45+(x['關']//5-1)*0.061)
        def sc(v,m): return max(m, round(v*cs))
        n  = (sc(14,6)+2*sc(2,0)+1) if s['atk']=='ring' else (sc(8,4) if s['atk']=='cross' else sc(3,2)+2*sc(1,0)+1)
        nr = (sc(20,6)+2*sc(2,0)+1) if s['atk']=='ring' else (sc(12,4) if s['atk']=='cross' else sc(4,2)+2*sc(1,0)+1)
        print(f"  第{x['關']:>2}關 章節Boss[{s['atk']:<6}] 每 {s['間隔']}s 射 {n} 顆"
              f"（血量<50%後每 {s['暴走間隔']}s 射 {nr} 顆）彈速{s['彈速']} 雷射={s['雷射']}")
        print(f"          一般Boss[{m['atk']:<6}] 每 {m['間隔']}s 射 "
              f"{8 if m['atk']=='cross' else 6} 顆  彈速{m['彈速']}")

    print("\n=== 3. 實測：第5關章節Boss戰時，螢幕上同時有幾顆敵方子彈 ===")
    def measure(lv, tag, rage=False):
        pg.evaluate("""([lv,rage])=>{
            META={}; LV_IDX=lv; start(); G.hasMoved=true; DIAG.touch=3;
            G.E.length=0; G.B.length=0; G.EB.length=0;
            const cfgs=G.bosses||buildBosses(CUR());
            const sup=cfgs.filter(x=>x.superBoss)[0];
            spawnBoss(sup);
            const e=G.boss; e.x=G.P.x; e.y=G.P.y-200; e.spd=0;
            if(rage) e.hp=e.maxhp*0.4;
            window.__peak=0; window.__samp=[];
            window.__k=setInterval(()=>{
                G.P.hearts=G.P.maxHearts; G.P.iframe=1;
                const b=G.boss; if(b){ b.x=G.P.x; b.y=G.P.y-200; if(rage) b.hp=b.maxhp*0.4; }
                // 只算「在畫面上」的敵方子彈
                const on=G.EB.filter(x=>Math.abs(x.x-G.cam.x)<W/2+20&&Math.abs(x.y-G.cam.y)<H/2+20).length;
                window.__samp.push(on);
                if(on>window.__peak) window.__peak=on;
            },100);
        }""",[lv,rage])
        pg.wait_for_timeout(9000)
        r=pg.evaluate("""()=>{ clearInterval(window.__k); const s=window.__samp.slice(); s.sort((a,b)=>a-b);
            return {峰值:window.__peak, 中位:s[Math.floor(s.length/2)],
                    平均:+(s.reduce((a,b)=>a+b,0)/s.length).toFixed(1)}; }""")
        print(f"  {tag:<34} 峰值 {r['峰值']:>3} 顆   中位 {r['中位']:>3} 顆   平均 {r['平均']:>5}")
        return r
    measure(4,"第5關 章節Boss（正常）")
    measure(4,"第5關 章節Boss（血量<50% 暴走）",True)
    measure(49,"第50關 章節Boss（正常）")

    print("\n=== 4. 雷射：v0.9.26 起限制在第 6 章（第30關）以後 ===")
    r=pg.evaluate("""()=>{
        const out={sup:[],laser:[]};
        for(let i=0;i<LEVELS.length;i++){
            const bs=buildBosses(LEVELS[i]);
            const sup=bs.filter(x=>x.superBoss)[0];
            if(!sup) continue;
            out.sup.push(i+1);
            if((sup.chIdx|0)>=5) out.laser.push(i+1);
        }
        return out;
    }""")
    print(f"  章節Boss 關卡：{r['sup']}")
    print(f"  會發射雷射的關卡：{r['laser']}")
    ok = r['laser']==[30,35,40,45,50]
    print(("  PASS  " if ok else "  FAIL  ")+"雷射只出現在第30關以後（第6章起）")
    if not ok: fails.append("laser gate")

    b.close()
srv.shutdown()

if True:
    print()
    if fails:
        print(f"❌ 失敗 {len(fails)} 項: {fails}"); sys.exit(1)
    print("=== 全部通過 ===")
