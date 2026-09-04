#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.27 兩個新功能的驗收：糖果援軍（同伴寶箱）＋ 免費/付費切點。

測試循環 1：功能本身照規格運作嗎？
  1. 糖果援軍：3 個、15 秒、55% 傷害、60% 射速、只用主武器、不繼承進化
  2. 寶箱權重：其餘 8 種的相對比例跟 v0.9.26 完全一樣（沒有偷偷調平衡）
  3. EDITION='full'（線上版）：任何一關都不該被鎖
  4. EDITION='demo'：第 16 關起鎖住、面板文字 11 語言都放得下、解鎖後全開
  5. 存檔：prem 旗標讀寫正確，full 版不寫 prem=1
"""
import http.server, socketserver, threading, functools, sys, json
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8861
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

# demo 版：用 route 攔截把 EDITION 換掉，不需要另外維護一份檔案。
# ⚠ 第一版在 handler 裡用 urllib 再打一次同一台 HTTP server——37 支平行時
#   那台 server 的執行緒被搶滿，request 卡住，導致 page.goto 整個逾時。
#   直接讀磁碟就沒有這個相依。
import os
_SRC = open(os.path.join(ROOT,'index.html'), encoding='utf-8').read()
assert "const EDITION='full';" in _SRC
_DEMO = _SRC.replace("const EDITION='full';","const EDITION='demo';",1)
def demo_route(route):
    route.fulfill(status=200, content_type="text/html; charset=utf-8", body=_DEMO)

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page(demo=False):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); pg.set_default_navigation_timeout(120000)
        pg.set_default_timeout(60000); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        if demo: pg.route(f"http://127.0.0.1:{PORT}/index.html", demo_route)
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
        return pg,c,errs

    # ═══════════ 1. 糖果援軍 ═══════════
    print("=== 1. 糖果援軍：規格 ===")
    pg,c,errs=page()
    spec=pg.evaluate("()=>({n:ALLY_N,t:ALLY_T,dmg:ALLY_DMG,rate:ALLY_RATE,orbit:ALLY_ORBIT})")
    print(f"  常數：{spec}")
    ck("3 個同伴", spec['n']==3, spec['n'])
    ck("持續 15 秒", spec['t']==15, spec['t'])
    ck("傷害 55%", abs(spec['dmg']-0.55)<1e-9, spec['dmg'])
    ck("射速 60%", abs(spec['rate']-0.60)<1e-9, spec['rate'])

    r=pg.evaluate("""()=>{
        META={}; LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        G.E.length=0; G.B.length=0;
        G.P.wep={bubble:2, yoyo:4};          // 主武器應該挑等級最高的 yoyo
        const w=allyWeapon();
        const t=CHEST_TYPES.find(x=>x.id==='ally');
        t.go(G.P);
        return {mainWep:w, n:G.ALLY.length, life:G.ALLY[0].life,
                dist:Math.round(Math.hypot(G.ALLY[0].x-G.P.x,G.ALLY[0].y-G.P.y))};
    }""")
    print(f"  開箱後：{r}")
    ck("主武器＝等級最高的那把（yoyo Lv.4）", r['mainWep']=='yoyo', r['mainWep'])
    ck("生成 3 個同伴", r['n']==3, r['n'])
    ck("初始壽命 15 秒", abs(r['life']-15)<0.01, r['life'])
    ck("環繞在玩家附近（不是疊在身上）", 60<r['dist']<160, r['dist'])

    print("\n=== 1b. 同伴真的會射擊，且傷害是玩家的 55% ===")
    # ⚠ P.dmgEff 是在 update() 裡每幀算出來的。start() 之後不等一幀就直接呼叫
    #   WEAPONS.fire()，dmgEff 還是 undefined → 傷害會是 NaN。第一版就是這樣假失敗的。
    pg.evaluate("""()=>{
        META={}; LV_IDX=4; start(); G.hasMoved=true; DIAG.touch=3;
        G.P.wep={bubble:3}; G.P.x=0; G.P.y=0;
    }""")
    pg.wait_for_timeout(300)                      # 讓 update() 至少跑過一幀，算出 dmgEff
    # ⚠ 目標敵人要在「開火的同一個 evaluate 裡」現生。上一版先生好再等 300ms，
    #   等的期間玩家的自動攻擊已經把它打死了 → nearest() 找不到目標 → 根本沒開火。
    r=pg.evaluate("""()=>{
        if(!(G.P.dmgEff>0)) return {err:'dmgEff 還沒算出來', dmgEff:G.P.dmgEff};
        G.E.length=0; G.B.length=0; G.ALLY.length=0;
        spawnEnemy('slime',1); const e=G.E[0];
        e.x=140; e.y=0; e.hp=e.maxhp=1e9;         // 打不死，才不會中途消失
        WEAPONS.bubble.fire(G.P,3);
        if(!G.B.length) return {err:'玩家沒開火（nearest 找不到目標？）'};
        const playerDmg=G.B[G.B.length-1].dmg;
        G.B.length=0;
        CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
        for(const a of G.ALLY){ a.cd=0; a.x=G.P.x+20; a.y=G.P.y; }   // 讓同伴也看得到那隻敵人
        updateAllies(0.016);
        const allyDmg = G.B.length ? G.B[0].dmg : null;
        return {playerDmg:+playerDmg.toFixed(2), allyDmg:allyDmg&&+allyDmg.toFixed(2),
                bullets:G.B.length};
    }""")
    assert not r.get('err'), r
    print(f"  玩家一發 {r['playerDmg']} 傷害 ／ 同伴一發 {r['allyDmg']} 傷害（共 {r['bullets']} 顆）")
    ck("同伴有射出子彈", r['bullets']>0, r['bullets'])
    ck("同伴傷害 = 玩家 × 0.55",
       r['allyDmg'] is not None and abs(r['allyDmg']/r['playerDmg']-0.55)<0.02,
       r['allyDmg'] and round(r['allyDmg']/r['playerDmg'],3))

    print("\n=== 1c. 邊角：沒有武器 / 玩家死亡 / 關卡結束 ===")
    r=pg.evaluate("""()=>{
        const out={};
        META={}; LV_IDX=0; start(); G.E.length=0; G.B.length=0;
        G.P.wep={};                                   // 一把武器都沒有
        CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
        out.noWepAlly=G.ALLY.length;
        for(const a of G.ALLY) a.cd=0;
        updateAllies(0.016);
        out.noWepBullets=G.B.length;                  // 不該噴子彈，也不該當掉
        out.noWepPick=allyWeapon();
        // 連開兩次寶箱：同伴數量不可以疊加到 6 個
        G.P.wep={bubble:1};
        CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
        CHEST_TYPES.find(x=>x.id==='ally').go(G.P);
        out.twice=G.ALLY.length;
        // 壽命耗盡要自己消失
        for(const a of G.ALLY) a.life=0.001;
        updateAllies(0.02);
        out.afterExpire=G.ALLY.length;
        // 換一關要清空（G 是全新物件）
        LV_IDX=1; start();
        out.newLevel=G.ALLY.length;
        return out;
    }""")
    print(f"  {r}")
    ck("沒有武器時不會當掉、也不噴子彈", r['noWepBullets']==0 and r['noWepPick'] is None, r)
    ck("連開兩次寶箱仍然只有 3 個（不疊加）", r['twice']==3, r['twice'])
    ck("壽命歸零後自動消失", r['afterExpire']==0, r['afterExpire'])
    ck("換關後同伴清空", r['newLevel']==0, r['newLevel'])

    print("\n=== 2. 寶箱權重：其餘 8 種的相對比例沒有被動到 ===")
    r=pg.evaluate("""()=>{
        const cnt={};
        for(const t of CHEST_POOL) cnt[t.id]=(cnt[t.id]||0)+1;
        return {cnt, total:CHEST_POOL.length};
    }""")
    cnt=r['cnt']; tot=r['total']
    print(f"  池子共 {tot} 份：{cnt}")
    # v0.9.26 的比例：heart1 nuke2 rain2 gold2 ice2 fire2 speed3 power3（共17）
    OLD={'heart':1,'nuke':2,'rain':2,'gold':2,'ice':2,'fire':2,'speed':3,'power':3}
    base=cnt['heart']
    same=all(cnt[k]==v*base for k,v in OLD.items())
    ck("8 種舊寶箱的相對比例與 v0.9.26 完全相同", same,
       {k:cnt[k]/base for k in OLD})
    p_ally=cnt.get('ally',0)/tot
    print(f"  糖果援軍出現率：{p_ally*100:.1f}% ／個寶箱")
    ck("援軍稀有度落在 3%~6%（docs-11：一關約 0~1 次）", 0.03<=p_ally<=0.06, round(p_ally,4))
    ck("援軍比任何一種舊寶箱都稀有", cnt['ally']<min(cnt[k] for k in OLD), cnt['ally'])

    print("\n=== 3. EDITION='full'（現在線上的版本）：一關都不能被鎖 ===")
    r=pg.evaluate("""()=>{
        const locked=[];
        for(let i=0;i<LEVELS.length;i++) if(isLocked(i)) locked.push(i+1);
        return {edition:EDITION, premium:isPremium(), locked,
                demoLevels:DEMO_LEVELS, boxHidden:document.getElementById('lockBox').classList.contains('hide')};
    }""")
    print(f"  {r}")
    ck("EDITION 預設是 full", r['edition']=='full', r['edition'])
    ck("full 版沒有任何一關被鎖", r['locked']==[], r['locked'][:5])
    ck("解鎖面板預設不顯示", r['boxHidden'])

    print("\n=== 3b. full 版不可以在存檔寫 prem=1 ===")
    r=pg.evaluate("""()=>{ PROGRESS=8; saveGame();
        return JSON.parse(localStorage.getItem(PROG_KEY)); }""")
    print(f"  存檔：{r}")
    ck("full 版存檔的 prem 是 0", r.get('prem')==0, r.get('prem'))
    ck("無 JS 錯誤（full）", not errs, errs[:2])
    pg.close(); c.close()

    # ═══════════ 4. demo 版 ═══════════
    print("\n=== 4. EDITION='demo'：第 16 關起鎖住 ===")
    pg,c,errs=page(demo=True)
    r=pg.evaluate("""()=>{
        const locked=[];
        for(let i=0;i<LEVELS.length;i++) if(isLocked(i)) locked.push(i+1);
        return {edition:EDITION, premium:isPremium(),
                first:locked[0], last:locked[locked.length-1], n:locked.length};
    }""")
    print(f"  {r}")
    ck("EDITION 已切成 demo", r['edition']=='demo')
    ck("第 1~15 關不鎖、第 16 關起鎖", r['first']==16, r['first'])
    ck("一路鎖到第 50 關", r['last']==50 and r['n']==35, r)

    print("\n=== 4b. 鎖住的關卡按「開始」不會進關，而是跳解鎖面板 ===")
    r=pg.evaluate("""()=>{
        PROGRESS=50; SEL_IDX=19; renderStage();      // 假裝進度已經很前面
        const before=!!(G&&G.running);
        document.getElementById('btnPlay').click();
        return {startedGame:!!(G&&G.running)&&!before,
                boxShown:!document.getElementById('lockBox').classList.contains('hide'),
                title:document.getElementById('lockTitle').textContent,
                sub:document.getElementById('lockSub').textContent,
                body:document.getElementById('lockBody').textContent,
                buyHidden:document.getElementById('btnLockBuy').classList.contains('hide')};
    }""")
    print(f"  面板：{r['title']} / {r['sub']}")
    print(f"        {r['body']}")
    ck("沒有偷偷把鎖住的關卡開起來", not r['startedGame'])
    ck("解鎖面板有跳出來", r['boxShown'])
    ck("面板提到正確的關號（第 20 關）", '20' in r['sub'], r['sub'])
    ck("面板寫出免費關數與總關數", '15' in r['body'] and '50' in r['body'], r['body'])
    ck("沒有商店連結時不顯示購買鍵（避免按了沒反應）", r['buyHidden'])

    print("\n=== 4c. 銀河圖：付費鎖節點可以點，進度鎖節點不能點 ===")
    r=pg.evaluate("""()=>{
        PROGRESS=50; SEL_IDX=0; renderStage();
        const q=n=>document.querySelectorAll(n).length;
        const n16=document.querySelector('.gnode[data-k="15"]');
        const n14=document.querySelector('.gnode[data-k="13"]');
        return {plock:q('.gnode.plock'), progLock:q('.gnode.locked'),
                n16Plock:n16&&n16.classList.contains('plock'),
                n16Clickable:!!(n16&&n16.onclick),
                n14Plock:n14&&n14.classList.contains('plock')};
    }""")
    print(f"  {r}")
    ck("35 個節點是付費鎖", r['plock']==35, r['plock'])
    ck("第 16 關節點是付費鎖", r['n16Plock'])
    ck("第 16 關節點可以點（點了跳面板）", r['n16Clickable'])
    ck("第 14 關節點不是付費鎖", not r['n14Plock'])

    print("\n=== 4d. 通關第 15 關的結算畫面：下一關變成「取得完整版」 ===")
    r=pg.evaluate("""()=>{
        META={}; LV_IDX=14; start(); G.hasMoved=true;
        G.t=G.winT+1; G.kills=120;
        endGame(true);
        const nx=document.getElementById('btnNext');
        return {label:nx.textContent, hidden:nx.classList.contains('hide'),
                flag:nx.dataset.demoEnd,
                sub:document.getElementById('overSub').textContent};
    }""")
    print(f"  按鈕：「{r['label']}」  結算文字：{r['sub'][:70]}")
    ck("按鈕有顯示", not r['hidden'])
    ck("按鈕文字是「取得完整版」而不是「下一關」", r['flag']=='1' and 'Full' in r['label'], r['label'])
    ck("結算文字說明免費關卡結束", 'free' in r['sub'].lower(), r['sub'][:60])

    print("\n=== 4e. 切語言不會把那顆按鈕變回「下一關」 ===")
    r=pg.evaluate("""()=>{
        applyLanguage('zh-Hant');
        const nx=document.getElementById('btnNext');
        const a={lang:LANG, label:nx.textContent};
        applyLanguage('en');
        return a;
    }""")
    print(f"  切成 {r['lang']} 後按鈕：「{r['label']}」")
    ck("切語言後仍然是購買文案", '完整版' in r['label'], r['label'])

    print("\n=== 4f. 通關第 14 關（還在免費範圍）→ 正常顯示下一關 ===")
    r=pg.evaluate("""()=>{
        META={}; LV_IDX=13; start(); G.t=G.winT+1; G.kills=90;
        endGame(true);
        const nx=document.getElementById('btnNext');
        return {label:nx.textContent, flag:nx.dataset.demoEnd, hidden:nx.classList.contains('hide')};
    }""")
    print(f"  {r}")
    ck("第 14 關通關仍是正常的「下一關」", r['flag']!='1' and not r['hidden'], r)

    print("\n=== 5. 解鎖：GOO_UNLOCK() 之後全開，而且會存進存檔 ===")
    r=pg.evaluate("""()=>{
        window.GOO_UNLOCK();
        const locked=[];
        for(let i=0;i<LEVELS.length;i++) if(isLocked(i)) locked.push(i+1);
        const save=JSON.parse(localStorage.getItem(PROG_KEY));
        return {locked, prem:save.prem, boxHidden:document.getElementById('lockBox').classList.contains('hide')};
    }""")
    print(f"  {r}")
    ck("解鎖後沒有任何一關被鎖", r['locked']==[], r['locked'][:5])
    ck("解鎖狀態有寫進存檔", r['prem']==1, r['prem'])
    ck("解鎖後面板自動關閉", r['boxHidden'])

    print("\n=== 5b. 重新載入之後解鎖狀態要留著（付費玩家不能重開就沒了）===")
    pg.reload(); pg.wait_for_timeout(600)
    r=pg.evaluate("()=>({edition:EDITION, prem:PREM_OWNED, premium:isPremium(), locked16:isLocked(15)})")
    print(f"  {r}")
    ck("重新載入後仍是 demo 版", r['edition']=='demo')
    ck("重新載入後仍然解鎖", r['prem'] and r['premium'] and not r['locked16'], r)

    print("\n=== 6. 解鎖面板文字：11 種語言都要放得下 390px ===")
    langs=pg.evaluate("()=>LANGS.map(x=>x.c)")
    for code in langs:
        r=pg.evaluate("""(code)=>{
            applyLanguage(code);
            PREM_OWNED=false; PROGRESS=50; SEL_IDX=19; renderStage();
            showLockBox(19);
            const ids=['lockTitle','lockSub','lockBody','btnLockLater','btnLockBuy'];
            const out={};
            for(const id of ids){
                const el=document.getElementById(id);
                const r=el.getBoundingClientRect();
                out[id]={txt:el.textContent, l:Math.round(r.left), r:Math.round(r.right),
                         over:r.right>390.5||r.left<-0.5, empty:!el.textContent.trim()};
            }
            document.getElementById('lockBox').classList.add('hide');
            return out;
        }""",code)
        over=[k for k,v in r.items() if v['over']]
        empty=[k for k,v in r.items() if v['empty'] and k!='btnLockBuy']
        ck(f"[{code}] 解鎖面板沒有超出畫面、沒有空字串", not over and not empty,
           (over+empty) or r['lockTitle']['txt'])

    ck("無 JS 錯誤（demo）", not errs, errs[:2])
    pg.close(); c.close()
    b.close()
srv.shutdown()
print()
if fails:
    print(f"❌ 失敗 {len(fails)} 項：{fails}"); sys.exit(1)
print("=== v0.9.27 全部通過 ===")
