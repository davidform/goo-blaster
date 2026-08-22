#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.25 驗收：卡池保底武器卡 + 連續升級的「第幾張/共幾張」提示。"""
import http.server, socketserver, threading, functools, sys, re
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8833
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()
fails=[]
def ck(n,c,e=""):
    print(("  PASS  " if c else "  FAIL  ")+n+(("  "+str(e)) if e else ""))
    if not c: fails.append(n)
with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(600)

    print("=== 1. 每一抽都保底有武器卡（武器沒滿時）===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start();
        let noWep=0, n=8000, mainSeen=0;
        for(let i=0;i<n;i++){
            const l=rollCards();
            if(!l.some(x=>x.w)) noWep++;
            if(l.some(x=>x.w==='bubble'&&!x.evo)) mainSeen++;
        }
        return {沒有武器卡的次數:noWep, 主武器出現率:+(100*mainSeen/n).toFixed(1), 抽樣:n};
    }""")
    print(f"   {r}")
    ck("8000 次抽牌沒有任何一次缺武器卡", r["沒有武器卡的次數"]==0, r["沒有武器卡的次數"])
    ck("主武器出現率 > 55%（原本 18.6%）", r["主武器出現率"]>55, f"{r['主武器出現率']}%")

    print("\n=== 2. 每一抽仍然是 3 張、且不重複 ===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start();
        let bad=0, dup=0;
        for(let i=0;i<3000;i++){
            const l=rollCards();
            if(l.length!==3) bad++;
            const key=l.map(x=>x.id+(x.evo?'#evo':''));
            if(new Set(key).size!==key.length) dup++;
        }
        return {張數不對:bad, 有重複:dup};
    }""")
    print(f"   {r}")
    ck("永遠是 3 張", r["張數不對"]==0, r["張數不對"])
    ck("同一抽不會出現重複的卡", r["有重複"]==0, r["有重複"])

    print("\n=== 3. 武器全滿後不會壞掉（卡池只剩數值卡）===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start();
        G.P.wep={bubble:5,graffiti:5,yoyo:5}; G.P.evo={bubble:1,graffiti:1,yoyo:1};
        const l=rollCards();
        let ok=true;
        for(let i=0;i<500;i++){ const x=rollCards(); if(x.some(c=>c.w)) ok=false; }
        return {張數:l.length, 還會出武器卡:!ok===false};
    }""")
    print(f"   {r}")
    ck("武器全滿後仍抽得到 3 張數值卡", r["張數"]==3)

    print("\n=== 4. 進化卡優先權（Lv.4 以上時應該常出現）===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start(); G.P.wep={bubble:4,graffiti:0,yoyo:0};
        let evo=0; for(let i=0;i<4000;i++){ if(rollCards().some(x=>x.evo)) evo++; }
        return +(100*evo/4000).toFixed(1);
    }""")
    print(f"   主武器 Lv.4 時，抽到進化卡的機率：{r}%")
    ck("進化卡機率 > 40%（它是最大回報，不該被埋掉）", r>40, f"{r}%")

    print("\n=== 5. 連續升級的「第幾張/共幾張」提示 ===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        gainXP(120);
        const seq=[];
        let guard=0;
        while(!cardsEl.classList.contains('hide') && guard++<20){
            seq.push({標題:document.querySelector('#cards .lvtitle').textContent,
                      欠:G.pendingCards|0, 總:G.cardTotal|0});
            const l=rollCards(); if(!l.length) break;
            applyCard(l[0]);
        }
        return {seq, 結束後暫停:G.paused, 結束後總數:G.cardTotal|0, lv:G.P.lv};
    }""")
    for x in r["seq"]: print(f"   {x['標題']:<28} 欠 {x['欠']} / 總 {x['總']}")
    ck("一次給 120 經驗確實升了多級", r["lv"]>=4, r["lv"])
    ck("標題有標示 (n/總數)", all(re.search(r'\(\d+/\d+\)|（\d+/\d+）',x["標題"]) for x in r["seq"]),
       [x["標題"] for x in r["seq"]][:2])
    ck("編號是遞增的 1,2,3...",
       [int(re.search(r'[（(](\d+)/',x["標題"]).group(1)) for x in r["seq"]]==list(range(1,len(r["seq"])+1)))
    ck("全部選完後解除暫停", r["結束後暫停"]==False)
    ck("全部選完後 cardTotal 歸零", r["結束後總數"]==0)

    print("\n=== 6. 只欠一張時不要顯示 (1/1) ===")
    r=pg.evaluate("""()=>{
        LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        gainXP(G.P.xpNext);   // 剛好升一級
        const t=document.querySelector('#cards .lvtitle').textContent;
        return {標題:t, 欠:G.pendingCards|0};
    }""")
    print(f"   {r}")
    ck("單張時標題不含 (n/m)", not re.search(r'[（(]\d+/\d+[）)]', r["標題"]), r["標題"])

    print("\n=== 7. 11 種語言都有 cardTitleN 且格式正確 ===")
    r=pg.evaluate("""()=>{
        const out={};
        for(const l of LANGS){ const o=LANG; applyLanguage(l.c);
            out[l.c]=T('cardTitleN',7,2,4); applyLanguage(o); }
        return out;
    }""")
    for k,v in r.items(): print(f"   {k:<8} {v}")
    ck("每種語言都代入了等級與 2/4", all(('7' in v and '2/4' in v) for v in r.values()),
       [k for k,v in r.items() if not('7' in v and '2/4' in v)])
    ck("沒有殘留 {n} 佔位符", not any(re.search(r'\{\d\}',v) for v in r.values()))
    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails[:6]}"); sys.exit(1)
print("=== 全部通過 ===")
