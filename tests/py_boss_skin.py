#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.22：Boss 外觀特徵系統 + 新名稱 + 預設語言的驗收。"""
import http.server, socketserver, threading, functools, sys, re
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8807
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

    print("=== 1. 預設語言：不管手機語系是什麼，一律英文 ===")
    for loc in ["zh-TW","zh-CN","ja-JP","de-DE","ru-RU","en-US","pt-BR"]:
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale=loc)
        pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(500)
        r=pg.evaluate("()=>({lang:LANG, play:document.getElementById('btnPlay').textContent.trim()})")
        ck(f"手機語系 {loc} → 預設英文", r["lang"]=="en" and r["play"]=="START GAME", r)
        pg.close(); c.close()

    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="zh-TW")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(600)

    print("\n=== 2. 玩家自己選過語言之後要記住（重載仍是他選的） ===")
    pg.evaluate("()=>{ applyLanguage('ja'); saveGame(); }")
    pg.reload(); pg.wait_for_timeout(600)
    ck("選了日文 → 重載後仍是日文", pg.evaluate("()=>LANG")=="ja", pg.evaluate("()=>LANG"))
    pg.evaluate("()=>{ localStorage.clear(); }")
    pg.reload(); pg.wait_for_timeout(600)
    ck("清掉存檔 → 回到英文", pg.evaluate("()=>LANG")=="en")

    print("\n=== 3. 13 個 Boss 名稱：11 語言都有、且沒有舊的上班族名稱 ===")
    OLD=['加班文件','未讀訊息','奪魂鬧鐘','業績KPI','週一晨會','無限加班','已讀不回',
         '年終考核','信箱爆炸','責任制','交接怨靈','沉默審判','終極KPI',
         'Overtime','Unread','Alarm','KPI']
    langs=pg.evaluate("()=>LANGS.map(x=>x.c)")
    for code in langs:
        names=pg.evaluate("""(code)=>{ const o=LANG; applyLanguage(code);
            const r={mid:BOSS_POOL.map(x=>x.name), ch:BOSS_CHAPTER.map(x=>x.name)};
            applyLanguage(o); return r; }""",code)
        alln=names["mid"]+names["ch"]
        ck(f"[{code}] 13 個名稱都有值", len(alln)==13 and all(n and len(n)>1 for n in alln), alln[:2])
        ck(f"[{code}] 沒有舊的上班族名稱", not any(o in n for n in alln for o in OLD),
           [n for n in alln if any(o in n for o in OLD)][:2])
        ck(f"[{code}] 13 個名稱互不重複", len(set(alln))==13)

    print("\n=== 4. 外觀特徵：逐章升級、混搭正確 ===")
    r=pg.evaluate("""()=>{
        const out=[];
        for(let ch=0; ch<10; ch++){
            const lv=(ch+1)*5-1;              // v0.9.23：每章 5 關，最後一關＝章節 Boss 關
            LV_IDX=lv; start();
            const bs=G.bosses;
            const fin=bs[bs.length-1];
            out.push({ch:ch+1, lv:lv+1, superBoss:!!fin.superBoss,
                      chSkin:fin.skin||[], midSkin:(bs[0]&&bs[0].skin)||[]});
        }
        return out;
    }""")
    prev=0
    for x in r:
        ck(f"第{x['ch']}章（第{x['lv']}關）章節 Boss 有外觀特徵",
           x["superBoss"] and len(x["chSkin"])>0, x["chSkin"])
        prev=len(x["chSkin"])
    ck("章節 Boss 的裝飾件數整體遞增（第1章 1 件 → 第10章 6 件）",
       len(r[0]["chSkin"])==1 and len(r[9]["chSkin"])==6,
       (len(r[0]["chSkin"]), len(r[9]["chSkin"])))
    ck("第1章的一般 Boss 完全樸素（新手期不要視覺噪音）", len(r[0]["midSkin"])==0, r[0]["midSkin"])
    ck("一般 Boss 的裝飾永遠不多於同章的章節 Boss",
       all(len(x["midSkin"])<=len(x["chSkin"]) for x in r),
       [(x['ch'],len(x['midSkin']),len(x['chSkin'])) for x in r if len(x['midSkin'])>len(x['chSkin'])])
    ck("六種特徵都有被用到",
       set(sum([x["chSkin"] for x in r],[]))=={'spike','armor','horn','crown','wing','aura'},
       sorted(set(sum([x["chSkin"] for x in r],[]))))

    print("\n=== 5. 盔甲碎裂：血量 50% 觸發，且只觸發一次 ===")
    r=pg.evaluate("""()=>{
        applyLanguage('en');
        LV_IDX=9; start(); G.hasMoved=true; DIAG.touch=3;    // 第2章（第10關）：章節 Boss 有 armor
        const cfg=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
        spawnBoss(cfg);
        const e=G.boss;
        // ⭐ 真兇（裝了儀器才量出來的）：hurtEnemy() 內部會擲 5% 的爆擊，
        //   爆擊傷害 ×2 → 打「45% 血」實際上打掉 90% → 盔甲提早碎。
        //   也就是這一項**從 v0.9.22 起就有 5% 的機率會失敗**，
        //   跟平行負載一點關係都沒有，只是機率低到之前每次都剛好躲過。
        //   驗「50% 門檻」要的是確定的傷害，所以先把爆擊關掉。
        G.P.crit=0;
        const before={armor:e.armor, broken:e.armorBroken, skin:e.skin,
                      hpPct:+(e.hp/e.maxhp*100).toFixed(1)};
        G.TXT.length=0;
        hurtEnemy(e, e.maxhp*0.45);            // 打到 55% → 還不該碎
        const mid={broken:e.armorBroken, txt:G.TXT.length,
                   hpPct:+(e.hp/e.maxhp*100).toFixed(1)};
        hurtEnemy(e, e.maxhp*0.10);            // 打到 45% → 應該碎
        const after={broken:e.armorBroken, txt:G.TXT.map(x=>x.txt)};
        const n1=G.TXT.length;
        hurtEnemy(e, e.maxhp*0.10);            // 再打 → 不該再碎一次
        return {before, mid, after, again:G.TXT.length-n1<=1 ? 'no-repeat':'REPEATED',
                txtCount:G.TXT.filter(x=>/ARMOR/.test(x.txt||'')).length};
    }""")
    print("   ",r)
    ck("第2章章節 Boss 帶盔甲", r["before"]["armor"] and 'armor' in r["before"]["skin"])
    ck("血量 55% 時盔甲還在", r["mid"]["broken"]==False,
       f'打之前 {r["before"]["hpPct"]}% → 打之後 {r["mid"]["hpPct"]}%')
    ck("血量 45% 時盔甲碎裂", r["after"]["broken"]==True)
    ck("碎裂提示是英文的 ARMOR SHATTERED!",
       any('ARMOR SHATTERED' in str(t) for t in r["after"]["txt"]), r["after"]["txt"])
    ck("盔甲只會碎一次（不會每次受傷都噴提示）", r["txtCount"]==1, r["txtCount"])

    print("\n=== 6. 碎裂後尖刺要露出來（沒有 spike 的盔甲 Boss 也要長刺） ===")
    r=pg.evaluate("""()=>{
        LV_IDX=9; start();
        const cfg=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
        spawnBoss(cfg); const e=G.boss;
        const hadSpike=skinHas(e,'spike');
        const beforeSpiked = skinHas(e,'spike') || (skinHas(e,'armor') && e.armorBroken);
        hurtEnemy(e, e.maxhp*0.6);
        const afterSpiked = skinHas(e,'spike') || (skinHas(e,'armor') && e.armorBroken);
        return {hadSpike, beforeSpiked, afterSpiked};
    }""")
    print("   ",r)
    ck("第2章 Boss 原本沒有外露尖刺", r["beforeSpiked"]==False)
    ck("盔甲碎裂後長出尖刺", r["afterSpiked"]==True)

    print("\n=== 7. 真的有畫出來（攔截 canvas 呼叫計數） ===")
    r=pg.evaluate("""()=>{
        window.__q=0; window.__arc=0;
        const oq=CanvasRenderingContext2D.prototype.quadraticCurveTo;
        CanvasRenderingContext2D.prototype.quadraticCurveTo=function(){ window.__q++; return oq.apply(this,arguments); };
        LV_IDX=49; start(); G.hasMoved=true; DIAG.touch=3;
        const cfg=(G.bosses||buildBosses(CUR())).filter(x=>x.superBoss)[0];
        spawnBoss(cfg);
        return {skin:G.boss.skin};
    }""")
    pg.wait_for_timeout(700)
    q=pg.evaluate("()=>window.__q")
    # ⚠ 這是「700ms 內畫了幾次」的速率量測，14 支測試平行搶 CPU 時幀數會少很多。
    #   門檻只要能證明「真的有畫」就夠，不要卡在一個會隨負載浮動的數字上。
    print("    最終關 Boss 特徵:", r["skin"], " quadraticCurveTo 呼叫數:", q)
    ck("最終關 Boss 六種特徵全開", len(r["skin"])==6, r["skin"])
    ck("翼／角真的有被繪製（quadraticCurveTo 有被呼叫）", q>20, q)

    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails[:6]}"); sys.exit(1)
print("=== 全部通過 ===")
