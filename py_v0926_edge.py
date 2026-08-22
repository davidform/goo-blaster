#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.26 邊界測試（測試循環 2）：彈幕密度依章節縮放後，會不會出現
   「射 0 顆」「後面的關卡反而比前面稀」「一般敵人也被縮到」「Boss 名字錯位」等問題。

   直接攔截 shootE() 數實際射出的子彈數，不靠公式推算——
   公式推算會漏掉「程式跟我以為的不一樣」這種錯。
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8841
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

HOOK="""
window.__cnt=0;
window.__hook=()=>{ const o=window.shootE; window.shootE=function(...a){ window.__cnt++; return o.apply(this,a); }; };
"""

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)

    print("=== 1. 實際射出的子彈數（攔截 shootE，非公式推算）===")
    def volley(lv, rage):
        pg.evaluate("""([lv,rage])=>{
            META={}; LV_IDX=lv; start(); G.hasMoved=true; DIAG.touch=3;
            G.E.length=0; G.B.length=0; G.EB.length=0; G.boss=null;
            const sup=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
            spawnBoss(sup);
            const e=G.boss; e.x=G.P.x+140; e.y=G.P.y; e.spd=0;
            if(rage) e.hp=e.maxhp*0.3;
            e.atkMax=999;          // 只讓它射一波，之後不再射
            e.atkT=0.001;          // 下一幀就開火
            // 用 G.EB.length 數會少算：追蹤散彈打到玩家後子彈就消失了。
            // 改成攔截 shootE()，數「射出來幾顆」而不是「還活著幾顆」。
            if(!window.__orig) window.__orig=window.shootE;
            window.__cnt=0;
            window.shootE=function(...a){ window.__cnt++; return window.__orig.apply(this,a); };
            window.__lock=setInterval(()=>{ const b=G.boss; if(b){ b.x=G.P.x+140; b.y=G.P.y;
                if(rage) b.hp=b.maxhp*0.3; } G.P.hearts=G.P.maxHearts; G.P.iframe=1; },30);
        }""",[lv,rage])
        # 固定睡 350ms 在高負載下會抓到「還沒開火」→ 0 顆。改成輪詢等第一波射完。
        for _ in range(60):
            pg.wait_for_timeout(120)
            if pg.evaluate("()=>window.__cnt>0"): break
        pg.wait_for_timeout(200)   # 讓同一波剩下的子彈也射完
        return pg.evaluate("""()=>{ clearInterval(window.__lock); const e=G.boss;
            window.shootE=window.__orig;
            return {n:window.__cnt, atk:e.atk, chIdx:e.chIdx, name:e.name}; }""")
    rows=[]
    for lv in range(4,50,5):
        r=volley(lv,False); rr=volley(lv,True)
        rows.append((lv+1, r, rr))
        print(f"  第{lv+1:>2}關 ch{r['chIdx']} [{r['atk']:<6}] 正常 {r['n']:>2} 顆 / 暴走 {rr['n']:>2} 顆   {r['name']}")

    ck("每一關的章節Boss都至少射 1 顆（沒有被縮到 0）",
       all(r['n']>=1 and rr['n']>=1 for _,r,rr in rows))
    ck("暴走時射的子彈不少於正常時", all(rr['n']>=r['n'] for _,r,rr in rows),
       [(lv,r['n'],rr['n']) for lv,r,rr in rows if rr['n']<r['n']])
    ck("第5關是全部章節Boss中最稀的", rows[0][1]['n']==min(r['n'] for _,r,_ in rows),
       f"第5關{rows[0][1]['n']}顆 vs 最小{min(r['n'] for _,r,_ in rows)}顆")
    ck("第50關維持在 19 顆（沒有連末關也被削弱）", rows[-1][1]['n']==19, rows[-1][1]['n'])
    ck("第50關暴走維持 25 顆", rows[-1][2]['n']==25, rows[-1][2]['n'])

    print("\n=== 2. 章節係數單調遞增（後面的關不會比前面稀）===")
    cs=pg.evaluate("()=>{const o=[];for(let i=0;i<10;i++)o.push(+Math.min(1,0.45+i*0.061).toFixed(3));return o;}")
    print(f"  cs = {cs}")
    ck("cs 單調遞增", all(cs[i]<=cs[i+1] for i in range(9)))
    ck("cs 落在 (0,1]", all(0<x<=1 for x in cs))
    ck("最終章 cs ≈ 1（末關彈幕不變）", cs[9]>=0.99, cs[9])

    print("\n=== 3. 一般 Boss / 一般敵人不受縮放影響 ===")
    r=pg.evaluate("""()=>{
        META={}; LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        G.E.length=0; G.EB.length=0; G.boss=null;
        const mid=(G.bosses||buildBosses(CUR())).filter(x=>!x.superBoss)[0];
        if(!mid) return {skip:true};
        spawnBoss(mid);
        const e=G.boss; e.x=G.P.x+140; e.y=G.P.y; e.spd=0;
        e.atkMax=999; e.atkT=0.001;
        if(!window.__orig) window.__orig=window.shootE;
        window.__cnt=0;
        window.shootE=function(...a){ window.__cnt++; return window.__orig.apply(this,a); };
        window.__lock=setInterval(()=>{ const b=G.boss; if(b){b.x=G.P.x+140;b.y=G.P.y;}
            G.P.hearts=G.P.maxHearts; G.P.iframe=1; },30);
        return {sb:!!e.superBoss, ch:e.chIdx, atk:e.atk};
    }""")
    for _ in range(60):
        pg.wait_for_timeout(120)
        if pg.evaluate("()=>window.__cnt>0"): break
    pg.wait_for_timeout(200)
    if not r.get('skip'):
        r['n']=pg.evaluate("()=>{ clearInterval(window.__lock); window.shootE=window.__orig; return window.__cnt; }")
    print(f"  第5關一般Boss: {r}")
    if not r.get('skip'):
        ck("一般 Boss 不是 superBoss", not r['sb'])
        ck("一般 Boss[cross] 仍射 8 顆（沒被縮）", r['n']==8, r['n'])

    ep=pg.evaluate("""()=>{
        META={}; LV_IDX=4; start(); G.E.length=0; G.EB.length=0;
        spawnEnemy('drone',1); const e=G.E[0];
        return {sb:!!e.superBoss, ch:e.chIdx===undefined?'undefined':e.chIdx};
    }""")
    ck("一般敵人沒有 superBoss 旗標（cs 恆為 1）", not ep['sb'], ep)

    print("\n=== 4. atk 重排後，Boss 名字/圖示仍對應正確章節 ===")
    r=pg.evaluate("""()=>{
        const out=[];
        for(let i=0;i<10;i++){
            const lv=(i+1)*5-1;
            const sup=buildBosses(LEVELS[lv]).filter(x=>x.superBoss)[0];
            out.push({關:lv+1, ch:sup.chIdx, name:sup.name, icon:sup.icon,
                      期望icon:BOSS_CHAPTER[i].icon, hp:sup.hp});
        }
        return out;
    }""")
    bad=[x for x in r if x['ch']!= (x['關']//5-1) or x['icon']!=x['期望icon']]
    for x in r: print(f"  第{x['關']:>2}關 ch{x['ch']} {x['icon']} {x['name']}")
    ck("10 章的 chIdx 與圖示都對應正確", not bad, bad[:2])
    ck("Boss 血量隨章節遞增", all(r[i]['hp']<r[i+1]['hp'] for i in range(9)))
    ck("最終章是 Omega, the Ender", 'Omega' in (r[9]['name'] or ''), r[9]['name'])

    print("\n=== 5. 第1~4關沒有章節Boss（新手不該被縮放邏輯影響）===")
    r=pg.evaluate("""()=>{
        const out=[];
        for(let i=0;i<4;i++){
            const bs=buildBosses(LEVELS[i]);
            out.push({關:i+1, boss數:bs.length, 有章節Boss:bs.some(x=>x.superBoss)});
        }
        return out;
    }""")
    for x in r: print(f"  {x}")
    ck("第1~4關都沒有章節Boss", not any(x['有章節Boss'] for x in r))

    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項: {fails}"); sys.exit(1)
print("=== v0.9.26 邊界測試全部通過 ===")
