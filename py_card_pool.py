#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卡池統計：玩家想升主武器，每次升級有多少機率看得到那張卡？
   順便驗證「選完卡馬上又能選」到底是 bug 還是 pendingCards 的正常行為。"""
import http.server, socketserver, threading, functools
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8832
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
with sync_playwright() as pw:
    b=pw.chromium.launch()
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(600)

    print("=== 1. 卡池組成（開局時）===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start();
        const P=G.P, pool=[];
        for(const u of UPGRADES){
            if(u.w){ const lv=P.wep[u.w];
                     if(lv>=4&&!P.evo[u.w]) pool.push('進化:'+u.w);
                     if(lv<5) pool.push('武器:'+u.w); }
            else { if((P[u.id]|0)>=(u.max||1)) continue; pool.push('數值:'+u.id); }
        }
        return {總數:pool.length,
                武器卡:pool.filter(x=>x.startsWith('武器')).length,
                數值卡:pool.filter(x=>x.startsWith('數值')).length,
                明細:pool};
    }""")
    print(f"  卡池總共 {r['總數']} 張：武器卡 {r['武器卡']} 張、數值卡 {r['數值卡']} 張")
    print(f"  → 每次抽 3 張")

    print("\n=== 2. 實測：抽 20000 次，主武器升級卡出現的機率 ===")
    r2=pg.evaluate("""()=>{
        LV_IDX=4; start();
        const N=20000; let hitBubble=0, hitAnyWep=0, hitNewWep=0;
        for(let i=0;i<N;i++){
            const list=rollCards();
            if(list.some(c=>c.w==='bubble'&&!c.evo)) hitBubble++;
            if(list.some(c=>c.w&&!c.evo)) hitAnyWep++;
            if(list.some(c=>c.w&&!c.evo&&G.P.wep[c.w]===0)) hitNewWep++;
        }
        return {主武器:100*hitBubble/N, 任一武器:100*hitAnyWep/N, 新武器:100*hitNewWep/N};
    }""")
    print(f"  三張裡出現「升級主武器（水槍）」的機率：{r2['主武器']:.1f}%")
    print(f"  三張裡出現「任何一張武器卡」的機率　：{r2['任一武器']:.1f}%")
    print(f"  （其中是『解鎖新武器』而不是升級既有武器：{r2['新武器']:.1f}%）")

    print("\n=== 3. 把主武器從 1 級練到 5 級，期望要升幾次等級 ===")
    r3=pg.evaluate("""()=>{
        const runs=3000; let tot=0, fail=0;
        for(let r=0;r<runs;r++){
            LV_IDX=4; start();
            let n=0;
            while(G.P.wep.bubble<5){
                n++;
                if(n>300){ fail++; break; }
                const list=rollCards();
                const w=list.find(c=>c.w==='bubble'&&!c.evo);
                if(w) G.P.wep.bubble=Math.min(5,G.P.wep.bubble+1);
                else { // 玩家沒得選主武器，只好拿別的（模擬：拿第一張）
                       const o=list[0]; if(o&&!o.w&&o.f){ try{o.f(G.P);}catch(e){} } }
            }
            tot+=n;
        }
        return {平均升級次數:tot/runs, 失敗:fail};
    }""")
    print(f"  平均需要升 **{r3['平均升級次數']:.1f} 級** 才能把主武器點滿（每次都優先選它）")

    print("\n=== 4. 「選完卡馬上又能選」是 bug 還是設計 ===")
    r4=pg.evaluate("""()=>{
        LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        const P=G.P;
        const before={lv:P.lv, xp:P.xp, xpNext:P.xpNext, pend:G.pendingCards|0};
        // 一次給一大包經驗（模擬吸到一團晶核），看會不會一次升好幾級
        gainXP(120);
        const after={lv:P.lv, xp:P.xp, xpNext:P.xpNext, pend:G.pendingCards|0,
                     卡片視窗開著:!cardsEl.classList.contains('hide')};
        // 逐張選掉，記錄每張選完之後視窗還開不開
        const seq=[];
        let guard=0;
        while(!cardsEl.classList.contains('hide') && guard++<20){
            const list=rollCards();
            if(!list.length) break;
            applyCard(list[0]);
            seq.push({剩餘欠卡:G.pendingCards|0, 視窗還開著:!cardsEl.classList.contains('hide')});
        }
        return {before, after, seq, 最後暫停狀態:G.paused};
    }""")
    print(f"  升級前：{r4['before']}")
    print(f"  一次給 120 經驗後：{r4['after']}")
    print(f"  逐張選卡的過程：")
    for i,s in enumerate(r4['seq']):
        print(f"    第 {i+1} 張選完 → 還欠 {s['剩餘欠卡']} 張，視窗{'還開著' if s['視窗還開著'] else '已關閉'}")
    print(f"  全部選完後 G.paused = {r4['最後暫停狀態']}（必須是 False）")

    print("\n=== 5. 各等級升級所需經驗 vs 一顆晶核給多少 ===")
    r5=pg.evaluate("""()=>{
        LV_IDX=4; start();
        const out=[];
        for(let lv=1;lv<=12;lv++) out.push({lv, need:Math.round(6+lv*5.5+lv*lv*0.5)});
        return {表:out, 一般晶核:1, 兔子:2, 無人機:3, 自爆:4, xpMul:(CUR().xpMul||1)};
    }""")
    print(f"  晶核經驗：軟泥1 / 兔子2 / 無人機3 / 自爆4，第5關 xpMul={r5['xpMul']}")
    print("  " + "  ".join(f"Lv{x['lv']}→{x['lv']+1}:{x['need']}" for x in r5['表'][:8]))
    b.close()
srv.shutdown()
