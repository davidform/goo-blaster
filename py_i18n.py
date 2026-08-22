#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.19 多語系測試。

1. 預設語言必須是英文（沒有存檔、瀏覽器語言不支援時）
2. 瀏覽器語言自動偵測（含 zh 繁簡細分、pt→pt-BR）
3. 11 種語言全部沒有缺 key、沒有殘留未翻譯的中文
4. 切換語言後，資料表（關卡/武器/升級卡/永久強化/Boss/寶箱）全部跟著換
5. 語言偏好會存檔，重新載入後保持
6. tier 改成數字索引後，TIER_COLOR 查表仍然正確（不會因翻譯而壞掉）
"""
import http.server, socketserver, threading, functools, sys, re
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8779
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+("  "+extra if extra else ""))
    if not cond: fails.append(name)

CJK=re.compile(r'[一-鿿]')

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page(locale="en-US"):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale=locale)
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(500)
        return pg,c,errs

    print("=== 測試1：預設語言是英文 ===")
    pg,c,errs=page("en-US")
    r=pg.evaluate("()=>({lang:LANG,btn:document.getElementById('btnPlay').textContent,lv1:LEVELS[0].n})")
    print(f"  {r}")
    ck("預設語言 = en", r["lang"]=="en", r["lang"])
    ck("第1關名稱是英文", not CJK.search(r["lv1"]), r["lv1"])
    ck("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()

    print("\n=== 測試2：預設語言一律英文（v0.9.22 起）===")
    # ⚠ 這一項在 v0.9.22 反轉了。舊版是「跟著手機語系自動切換」，
    #   結果使用者的 zh-TW 手機一打開就是中文版——與「預設語言為英文」的需求相反。
    #   現在不管手機語系是什麼，第一次進遊戲一律英文；detectLang() 本身保留，
    #   但只是備用（未來要做「偵測到你的語言，要不要切換？」提示），不再決定預設值。
    for loc in ["ja-JP","ko-KR","de-DE","fr-FR","es-ES","it-IT","ru-RU",
                "zh-TW","zh-HK","zh-CN","pt-PT","pt-BR","th-TH","en-US"]:
        pg,c,_=page(loc)
        got=pg.evaluate("()=>LANG")
        ck(f"手機語系 {loc} → 預設 en", got=="en", f"實際 {got}")
        pg.close(); c.close()

    print("\n=== 測試2b：detectLang() 本身仍然正確（保留備用）===")
    for loc,want in [("ja-JP","ja"),("ko-KR","ko"),("de-DE","de"),("fr-FR","fr"),
                     ("es-ES","es"),("it-IT","it"),("ru-RU","ru"),
                     ("zh-TW","zh-Hant"),("zh-HK","zh-Hant"),("zh-CN","zh-Hans"),
                     ("pt-PT","pt-BR"),("pt-BR","pt-BR"),("th-TH","en")]:
        pg,c,_=page(loc)
        got=pg.evaluate("()=>detectLang()")
        ck(f"detectLang() {loc} → {want}", got==want, f"實際 {got}")
        pg.close(); c.close()

    print("\n=== 測試3：11 種語言都沒有缺 key、也沒有殘留中文 ===")
    pg,c,errs=page("en-US")
    r=pg.evaluate("""()=>{
        const en=Object.keys(L10N.en), out=[];
        for(const l of LANGS){
            const d=L10N[l.c];
            const miss=en.filter(k=>d[k]===undefined);
            out.push({code:l.c, name:l.n, total:Object.keys(d).length, miss:miss.length, missKeys:miss.slice(0,3)});
        }
        return out;
    }""")
    for x in r:
        ck(f"{x['code']:<8} {x['name']:<14} {x['total']} keys 無缺漏", x["miss"]==0, str(x["missKeys"]))
    # 非中文語言不得出現漢字（日文的漢字是正常的，所以排除 ja/zh）
    r2=pg.evaluate("""()=>{
        const bad={};
        const cjk=/[\\u4e00-\\u9fff]/;
        for(const l of LANGS){
            if(l.c.startsWith('zh')||l.c==='ja') continue;
            const hit=Object.entries(L10N[l.c]).filter(([k,v])=>cjk.test(v)).map(([k])=>k);
            if(hit.length) bad[l.c]=hit.slice(0,5);
        }
        return bad;
    }""")
    ck("非中日語言沒有殘留漢字", not r2, str(r2))
    pg.close(); c.close()

    print("\n=== 測試4：切換語言後所有資料表跟著換 ===")
    pg,c,errs=page("en-US")
    r=pg.evaluate("""()=>{
        const snap=()=>({lv1:LEVELS[0].n, lv25:LEVELS[24].n, lvLast:LEVELS[LEVELS.length-1].n,
                         wep:WEAPONS.bubble.name, evo:EVOS.yoyo.name,
                         card:UPGRADES.find(u=>u.id==='sticky').n,
                         meta:META_UPGRADES[0].n, metaD:META_UPGRADES[0].d(0),
                         boss:BOSS_CHAPTER[9].name, chest:CHEST_TYPES[0].n,
                         tier:tierName(LEVELS[LEVELS.length-1].tier),
                         btn:document.getElementById('btnPlay').textContent});
        const out={};
        for(const code of ['en','ja','de','ru','zh-Hant']){ applyLanguage(code); renderStage(); out[code]=snap(); }
        applyLanguage('en');
        return out;
    }""")
    for code,v in r.items(): print(f"  {code:<8} {v['lv1'][:22]:<24}{v['card'][:18]:<20}{v['boss'][:20]}")
    vals=[tuple(v.values()) for v in r.values()]
    ck("五種語言的資料表內容彼此都不同", len(set(vals))==len(vals))
    ck("日文的最終關名稱有換掉", r["ja"]["lvLast"]!=r["en"]["lvLast"])
    ck("俄文的永久強化描述有換掉", r["ru"]["metaD"]!=r["en"]["metaD"], r["ru"]["metaD"])
    ck("德文的開始鈕有換掉", r["de"]["btn"]!=r["en"]["btn"], r["de"]["btn"])
    ck("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()

    print("\n=== 測試5：語言偏好會存檔並在重新載入後保持 ===")
    pg,c,errs=page("en-US")
    pg.evaluate("()=>{ applyLanguage('ko'); saveGame(); }")
    pg.reload(); pg.wait_for_timeout(500)
    r=pg.evaluate("()=>({lang:LANG, lv1:LEVELS[0].n})")
    print(f"  {r}")
    ck("重新載入後語言仍是 ko", r["lang"]=="ko", r["lang"])
    pg.close(); c.close()

    print("\n=== 測試6：tier 改數字索引後，顏色查表仍正確 ===")
    pg,c,errs=page("en-US")
    r=pg.evaluate("""()=>{
        const t=LEVELS.map(L=>L.tier);
        return {全是數字:t.every(x=>typeof x==='number'),
                第1關:t[0], 第10關:t[9], 第11關:t[10], 最終關:t[t.length-1],
                顏色數:TIER_COLOR.length,
                顏色全有效:t.every(x=>typeof TIER_COLOR[x]==='string'&&TIER_COLOR[x][0]==='#'),
                名稱範例:tierName(0)+' / '+tierName(13)};
    }""")
    print(f"  {r}")
    ck("所有關卡的 tier 都是數字", r["全是數字"])
    ck("tier 對應正確（第1關0、第10關4、第11關5、最終關13）",
       [r["第1關"],r["第10關"],r["第11關"],r["最終關"]]==[0,4,5,13], str(r))
    ck("每個 tier 都查得到顏色", r["顏色全有效"])
    ck("無 JS 錯誤", not errs, str(errs[:2]))
    pg.close(); c.close()
    b.close()
srv.shutdown()
print()
if fails: print("❌ 失敗："+", ".join(fails)); sys.exit(1)
print("=== 全部通過 ===")
