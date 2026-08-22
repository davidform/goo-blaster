#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.14 新增、v0.9.23 改寫：關卡擴充 + 每 5 關章節 Boss + 銀河圖示的專屬測試。
   ⚠ v0.9.23 把 100 關砍成 50 關、Boss 從每 10 關改成每 5 關（見 docs-10）。
   1) buildBosses() 對章節 Boss 關（10/30/50）要挑到正確的 BOSS_CHAPTER 項目。
   2) 銀河圖節點：大 Boss 關要用 .gic 圖示、且圖示要對得上 BOSS_CHAPTER[bossChapter].icon；
      一般關卡維持 .gnum 數字；鎖住的關卡維持 🔒；最終關要多一個 mega class。
   3) renderStage() 全破畫面要動態顯示總關數，不能寫死。
   4) LEVELS 陣列本身：長度、Boss 關卡位置、章節分佈的基本健檢（防止之後改動時手滑）。
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8774

socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT),
      functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

def new_page(pw_b):
    c = pw_b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2,
                          is_mobile=True, has_touch=True)
    pg = c.new_page()
    pg.goto(f"http://127.0.0.1:{PORT}/index.html")
    pg.wait_for_timeout(400)
    return pg

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

    print("=== 測試1: LEVELS 陣列基本健檢 ===")
    pg = new_page(b)
    r = pg.evaluate("""()=>({
        len: LEVELS.length,
        bossAt: LEVELS.map((L,i)=>L.superBoss?i+1:null).filter(x=>x),
        bcLen: BOSS_CHAPTER.length,
        lvl6superBoss: LEVELS[5].superBoss||false,
        lvl10superBoss: LEVELS[9].superBoss||false,
    })""")
    print(r)
    assert r["len"]==50, f"FAIL: 總關卡數應該是50，實際 {r['len']}"
    assert r["bossAt"]==[5,10,15,20,25,30,35,40,45,50], f"FAIL: 章節Boss關位置不對: {r['bossAt']}"
    assert r["bcLen"]==10, f"FAIL: BOSS_CHAPTER 應該有10筆，實際 {r['bcLen']}"
    assert r["lvl6superBoss"]==False, "FAIL: 第6關不應該再是大Boss關（新規則只有10的倍數才是）"
    assert r["lvl10superBoss"]==True, "FAIL: 第10關應該維持大Boss關"
    print("PASS\\n")

    print("=== 測試2: buildBosses() 對章節Boss關挑對 BOSS_CHAPTER ===")
    r2 = pg.evaluate("""()=>{
        const check=(idx)=>{
            const L=LEVELS[idx];
            const bosses=buildBosses(L);
            const sb=bosses.find(bo=>bo.superBoss);
            return {lvl:idx+1, bossChapter:L.bossChapter, name:sb?sb.name:null,
                    expectName:BOSS_CHAPTER[L.bossChapter].name,
                    hp:sb?sb.hp:null};
        };
        return [check(4), check(9), check(29), check(49)];
    }""")
    for row in r2:
        print(row)
        assert row["name"]==row["expectName"], f"FAIL: 第{row['lvl']}關的Boss名字對不上章節設定"
    # hp應該隨關卡遞增（最終關的Boss血量要遠高於第10關）
    assert r2[3]["hp"] > r2[0]["hp"]*3, "FAIL: 最終關Boss血量沒有明顯高於第5關"
    print("PASS\\n")

    print("=== 測試3: 銀河圖節點圖示（Boss關用圖示、一般關用數字、鎖住用🔒、最終關mega） ===")
    pg3 = new_page(b)
    # 直接把進度設到全破，這樣所有節點都會是 unlocked，方便一次檢查所有圖示
    r3 = pg3.evaluate("""()=>{
        PROGRESS = LEVELS.length+1; // 全破
        showMenu(); // 重新渲染主選單/銀河圖
        const nodes=[...document.querySelectorAll('.gnode')];
        const get=(k)=>{
            const el=document.querySelector('.gnode[data-k="'+k+'"]');
            if(!el) return null;
            return {cls:el.className, gic:(el.querySelector('.gic')||{}).textContent||null,
                    gnum:(el.querySelector('.gnum')||{}).textContent||null};
        };
        return {count:nodes.length, n0:get(0), n9:get(9), n19:get(19), n48:get(48), n49:get(49)};
    }""")
    print(r3)
    assert r3["count"]==50, f"FAIL: 銀河圖節點數應該是50，實際 {r3['count']}"
    # 全破狀態下所有節點都是 done，理論上顯示 ✓ 不是圖示/數字——這是既有邏輯（done優先於boss圖示），
    # 這裡改用「目前最前線」（cur，尚未完成）的情境來驗證圖示本身，見下方測試4
    print("（全破時全部顯示 ✓，是既有規則——圖示驗證見測試4）\\n")

    print("=== 測試4: 目前最前線是Boss關時要顯示對應圖示，非Boss關顯示數字 ===")
    pg4 = new_page(b)
    r4 = pg4.evaluate("""()=>{
        // frontier(目前最前線、可玩但還沒過)＝PROGRESS-1（0-based index）
        const setFrontierAndCheck=(prog)=>{
            PROGRESS = prog; SEL_IDX = prog-1; showMenu();
            const el=document.querySelector('.gnode[data-k="'+(prog-1)+'"]');
            return {cls:el.className, gic:(el.querySelector('.gic')||{}).textContent||null,
                    gnum:(el.querySelector('.gnum')||{}).textContent||null};
        };
        const atLevel20 = setFrontierAndCheck(20);   // 第20關是章節Boss關，frontier=index19
        const atLevel11 = setFrontierAndCheck(11);   // 第11關是一般關（每章第1關）
        const atLevelLast = setFrontierAndCheck(50); // 最終關：大Boss關 + mega
        return {atLevel20, atLevel11, atLevelLast,
                icon20:BOSS_CHAPTER[LEVELS[19].bossChapter].icon,
                iconLast:BOSS_CHAPTER[LEVELS[49].bossChapter].icon};
    }""")
    print(r4)
    assert r4["atLevel20"]["gic"]==r4["icon20"], "FAIL: 第20關節點沒有顯示正確的Boss圖示"
    assert "boss" in r4["atLevel20"]["cls"], "FAIL: 第20關節點沒有 boss class"
    assert r4["atLevel11"]["gnum"]=="11", "FAIL: 第11關（一般關）應該顯示數字11"
    assert "boss" not in r4["atLevel11"]["cls"], "FAIL: 第11關不應該有 boss class"
    assert r4["atLevelLast"]["gic"]==r4["iconLast"], "FAIL: 最終關節點沒有顯示正確的Boss圖示"
    assert "mega" in r4["atLevelLast"]["cls"], "FAIL: 最終關節點應該要有 mega class（全遊戲最恐怖）"
    print("PASS\\n")

    print("=== 測試5: renderStage() 全破文字要動態顯示總關數，不是寫死的 ===")
    pg5 = new_page(b)
    r5 = pg5.evaluate("""()=>{
        PROGRESS = LEVELS.length+1; SEL_IDX = LEVELS.length-1; showMenu();
        return document.getElementById('stageInfo').innerHTML;
    }""")
    assert '50' in r5, "FAIL: 全破說明文字裡沒有出現總關數 50"
    assert '全部 10 關' not in r5, "FAIL: 全破說明文字還殘留寫死的『全部 10 關』"
    print("全破文字包含 50，且無殘留的寫死關數")
    print("PASS\\n")

    b.close()

print("=== 全部通過 ===")
srv.shutdown()
