#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.30：itch.io 真人回饋（CoderGenius72 + 使用者自己在平板上的回報）驗收。

  1. Boss 血條交接：多 Boss 關卡（nboss 2~3）新 Boss 出場時，若前一隻還活著，
     血條不能被搶走（CoderGenius72：「stage ~7, 2 bosses overlapped」）
  2. 武器升級卡的傷害數字：不能凍結在 Lv.1，要反映「選了這張卡之後」的等級
     （CoderGenius72：「Upgrades on main weapon should show the increase in
     damage」——查證後比回報的還嚴重，見 docs-04 三十三節）
  3. 溜溜球（yoyo）武器描述本來完全沒有傷害數字，現在要有
  4. 桌機鍵盤觸發核彈（CoderGenius72：「could not reach for it on computer
     fast enough」）
  5. 存檔備份碼的一次性主動提示：第一次清掉第5關才出現，出現後不再重複
  6. 加速鍵／核彈鍵在平板大螢幕上要跟著放大、離角落更遠（使用者親自回報）
"""
import http.server, socketserver, threading, functools, sys, json
from test_paths import BROWSER_CHANNEL, GAME_ROOT
from playwright.sync_api import sync_playwright

ROOT = GAME_ROOT; PORT=8878
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

with sync_playwright() as pw:
    b=pw.chromium.launch(channel=BROWSER_CHANNEL, args=["--autoplay-policy=no-user-gesture-required"])
    def page(vp=None):
        c=b.new_context(viewport=vp or {"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); pg.set_default_timeout(60000)
        errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
        return pg,c,errs

    # ═══ 1. Boss 血條交接：前一隻還活著就不能被搶走血條 ═══
    print("=== 1. 多 Boss 關卡的血條交接 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true;
        const cfgA={r:40,hp:1000,spd:1,dmg:10,hue:0,name:'BossA',atk:1,atkT:1,bspd:1,kind:'mid'};
        const cfgB={r:40,hp:1000,spd:1,dmg:10,hue:0,name:'BossB',atk:1,atkT:1,bspd:1,kind:'mid'};
        spawnBoss(cfgA);
        const afterA = G.boss.name;
        spawnBoss(cfgB);           // A 還活著（hp 沒動）此時出場
        const afterB_stillA = G.boss.name;
        // 把 A 殺掉，模擬死亡交接分支（跟 hurtEnemy 死亡分支用一樣的判斷）
        const a=G.E.find(e=>e.name==='BossA');
        G.E.splice(G.E.indexOf(a),1);
        if(G.boss===a) G.boss=G.E.find(o=>o.boss)||null;
        const afterA_dead = G.boss ? G.boss.name : null;
        return {afterA, afterB_stillA, afterA_dead};
    }""")
    print(f"  {r}")
    ck("Boss A 出場，血條是 A", r["afterA"]=="BossA", r)
    ck("Boss B 出場但 A 還活著 → 血條仍然是 A（不能被搶走）", r["afterB_stillA"]=="BossA", r)
    ck("A 死掉之後才交接給 B", r["afterA_dead"]=="BossB", r)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 1b. 單 Boss 關卡：行為完全不變（回歸測試）═══
    print("\n=== 1b. 單 Boss 關卡不受影響（回歸）===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true;
        const cfg={r:40,hp:500,spd:1,dmg:10,hue:0,name:'SoloBoss',atk:1,atkT:1,bspd:1,kind:'mid'};
        spawnBoss(cfg);
        return {boss: G.boss.name, only1: G.E.filter(e=>e.boss).length===1};
    }""")
    ck("單 Boss 出場，血條正確指向它", r["boss"]=="SoloBoss" and r["only1"], r)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 2. 武器升級卡的傷害數字要反映「選了之後」的等級 ═══
    # 注意（AGENTS.md 第3節鐵則 9）：rollCards() 保底只保證「至少一張武器卡」，
    # 不保證一定是 bubble——保底抽的是哪一把武器本身是機率的（依權重 Math.random）。
    # 所以不能只呼叫一次就斷言 list 裡一定找得到 bubble 卡；平行跑測試時就真的抽到過
    # 全部保底都不是 bubble，導致 card 是 undefined。rollCards() 本身不改動 G.P，
    # 純函式、可以放心重複呼叫，所以用「重抽到出現目標武器卡為止」取代單抽，
    # 而不是放寬成「不驗證這件事了」。
    print("\n=== 2. 武器升級卡不能凍結在 Lv.1 的數字 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true;
        G.P.wep.bubble=3;                 // 玩家目前泡泡槍是 Lv.3
        let card=null;
        for(let i=0;i<200 && !card;i++){
            card=rollCards().find(c=>c.w==='bubble');
        }
        return {desc: card ? card.d : null,
                expectLv4: WEAPONS.bubble.desc(4),   // 卡片應該顯示「選了會變成 Lv.4」的數字
                wrongLv1: WEAPONS.bubble.desc(1)};   // 舊 bug 會顯示這個（永遠 Lv.1）
    }""")
    print(f"  {r}")
    ck("卡片顯示的是 Lv.4（選這張卡之後的等級）的數字，不是凍結的 Lv.1",
       r["desc"]==r["expectLv4"] and r["desc"]!=r["wrongLv1"], r)
    pg.close(); c.close()

    # 同時驗證「全新武器」(lv=0) 情況：卡片應該顯示 Lv.1 的數字（選了就會變 Lv.1）
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true;
        G.P.wep.graffiti=0;               // 還沒解鎖
        let card=null;
        for(let i=0;i<200 && !card;i++){
            card=rollCards().find(c=>c.w==='graffiti');
        }
        return {desc: card ? card.d : null, expectLv1: WEAPONS.graffiti.desc(1)};
    }""")
    ck("全新武器（Lv.0）的卡片顯示 Lv.1 的數字", r["desc"]==r["expectLv1"], r)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 3. 溜溜球武器描述要有傷害數字 ═══
    print("\n=== 3. 溜溜球（yoyo）武器描述要顯示傷害數字 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>({
        lv1: WEAPONS.yoyo.desc(1), lv3: WEAPONS.yoyo.desc(3),
        raw: L10N.en.w_yoyo_d
    })""")
    print(f"  {r}")
    ck("{0} 佔位符存在（不再是完全沒有數字的靜態文字）", '{0}' in r["raw"], r["raw"])
    ck("Lv.1 跟 Lv.3 顯示的數字不一樣（真的隨等級變化，不是另一個凍結值）",
       r["lv1"]!=r["lv3"], r)
    ck("Lv.1 的數字符合傷害公式 18+1*15=33", "33" in r["lv1"], r["lv1"])
    ck("Lv.3 的數字符合傷害公式 18+3*15=63", "63" in r["lv3"], r["lv3"])
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 4. 桌機鍵盤觸發核彈 ═══
    print("\n=== 4. E 鍵觸發核彈 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true; G.paused=false;
        G.P.nukeHeld=true;
        G.E.push({x:0,y:0,boss:false,hp:1,maxhp:1,type:'slime',flash:0});
        return {before: G.E.length, heldBefore: G.P.nukeHeld};
    }""")
    pg.keyboard.press('e')
    pg.wait_for_timeout(150)
    r2=pg.evaluate("()=>({after: G.E.length, heldAfter: G.P.nukeHeld})")
    print(f"  before={r} after={r2}")
    ck("按 E 之前手上有核彈可以用", r["heldBefore"], r)
    ck("按 E 之後核彈用掉了、場上非 Boss 敵人清空了",
       (not r2["heldAfter"]) and r2["after"]==0, r2)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 4b. 沒有核彈可用時，按 E 不能誤觸發（安全的 no-op）
    print("\n=== 4b. 沒有核彈時按 E 不會出事 ===")
    pg,c,errs=page()
    pg.evaluate("()=>{ G=newGame(); G.running=true; G.paused=false; G.P.nukeHeld=false; }")
    pg.keyboard.press('e')
    pg.wait_for_timeout(150)
    ck("無 JS 錯誤（沒有核彈時按鍵是安全的 no-op）", not errs, errs[:2])
    pg.close(); c.close()

    # 4c. 主選單（G 是 null）按 E 不能丟例外——這是這次順手補上的防呆
    print("\n=== 4c. 主選單時按 E 不會丟例外 ===")
    pg,c,errs=page()
    pg.keyboard.press('e')
    pg.wait_for_timeout(150)
    ck("主選單（G 是 null）按 E 沒有 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 4d. 在存檔備份碼的輸入框打字時，字母鍵不能被核彈快捷鍵攔截
    print("\n=== 4d. 在備份碼輸入框打字時，e 不會被當成遊戲操作 ===")
    pg,c,errs=page()
    pg.click("#navSettings")
    pg.click("#btnCode")
    pg.click("#codeImportArea")
    pg.keyboard.type("test e key")
    val=pg.eval_on_selector("#codeImportArea","el=>el.value")
    ck("輸入框正常打完整句話（e 沒被攔截掉）", val=="test e key", val)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 5. 存檔備份碼的一次性提示：第一次清第5關才出現 ═══
    print("\n=== 5. 第一次清掉第5關才出現備份碼提示，之後不再重複 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true; G.over=false;
        G.lvIdx=4; G.winT=1; G.t=1; G.kills=1;      // 模擬清完第5關（lvIdx 是 0-index）
        endGame(true);
        return {sub: document.getElementById('overSub').innerHTML,
                nudged: CODE_NUDGED};
    }""")
    ck("第一次清第5關，結算畫面有備份碼提示", 'codeNudge' in r["sub"], r["sub"][:200])
    ck("CODE_NUDGED 旗標被設成 true（且已存檔）", r["nudged"]==True, r)
    # 再清一次第5關（模擬重玩），這次不應該再跳提示
    r2=pg.evaluate("""()=>{
        G.over=false; G.lvIdx=4; G.winT=1; G.t=1; G.kills=1;
        endGame(true);
        return {sub: document.getElementById('overSub').innerHTML};
    }""")
    ck("第二次清第5關，不會重複跳提示", 'codeNudge' not in r2["sub"], r2["sub"][:200])
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 5b. 清其他關卡（不是第5關）不會誤觸發提示
    print("\n=== 5b. 清掉其他關卡不會誤觸發提示 ===")
    pg,c,errs=page()
    r=pg.evaluate("""()=>{
        G=newGame(); G.running=true; G.over=false;
        G.lvIdx=1; G.winT=1; G.t=1; G.kills=1;      // 第2關，不是第5關
        endGame(true);
        return {sub: document.getElementById('overSub').innerHTML, nudged: CODE_NUDGED};
    }""")
    ck("清第2關不會跳出備份碼提示", 'codeNudge' not in r["sub"], r["sub"][:200])
    ck("CODE_NUDGED 維持 false", r["nudged"]==False, r)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 6. 加速鍵／核彈鍵在平板大螢幕上要放大、離角落更遠 ═══
    print("\n=== 6. 平板大螢幕：按鈕要放大、離角落更遠 ===")
    for name, vp, minR, minMargin in [
        ("phone",  {"width":390, "height":844},  40, 15),
        ("tablet", {"width":834, "height":1194}, 58, 35),
        ("big-tablet", {"width":1366,"height":1024}, 60, 45),
    ]:
        pg,c,errs=page(vp)
        r=pg.evaluate("""()=>{
            const nk=document.getElementById('btnNuke');
            const cs=getComputedStyle(nk);
            return {btnR:BTN.r, btnX:BTN.x, nukeW:parseFloat(cs.width)};
        }""")
        print(f"  {name} {vp} -> {r}")
        ck(f"[{name}] 加速鍵半徑 >= {minR}px", r["btnR"]>=minR, r)
        ck(f"[{name}] 離左邊界 >= {minMargin}px（不是死貼在角落）", (r["btnX"]-r["btnR"])>=minMargin, r)
        ck(f"[{name}] 核彈鍵寬度跟著加速鍵等比例縮放（約 1.8 倍半徑）",
           abs(r["nukeW"] - r["btnR"]*1.8) < 1, r)
        ck(f"[{name}] 無 JS 錯誤", not errs, errs[:2])
        pg.close(); c.close()
    # 手機尺寸要跟改版前完全一樣（回歸測試，不能因為這次改動動到手機體驗）
    pg,c,errs=page({"width":390,"height":844})
    r=pg.evaluate("()=>({btnR:BTN.r, btnX:BTN.x, btnY:BTN.y})")
    ck("手機尺寸：BTN.r 跟改版前一樣是 50.7", abs(r["btnR"]-50.7)<0.1, r)
    ck("手機尺寸：BTN.x 跟改版前一樣是 70.7（50.7+20）", abs(r["btnX"]-70.7)<0.1, r)
    pg.close(); c.close()

    b.close()

srv.shutdown()
print()
if fails:
    print(f"❌ {len(fails)} 項失敗：")
    for f in fails: print("  -", f)
    sys.exit(1)
print("✅ 全部通過")
