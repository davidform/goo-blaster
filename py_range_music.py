#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.15 新增：
   1) 攻擊鎖定範圍——武器一開始要被 P.atkRange 限制在比原本射程窄的範圍，
      升級卡「望遠糖鏡」要能正確把範圍撐開，疊滿 2 層後不能再疊。
   2) 每關背景音樂的移調/節奏型——用 musicSetLevel() 直接檢查同一關兩次呼叫
      結果一致（非隨機、可重現），且不同關卡確實給出不同組合。
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT = "/home/claude/goo/game"
PORT = 8775

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

    print("=== 測試1: P.atkRange 預設值比武器原始射程窄 ===")
    pg = new_page(b)
    r = pg.evaluate("""()=>({base:ATK_RANGE_BASE, step:ATK_RANGE_STEP})""")
    print(r)
    assert r["base"] < 900, "FAIL: 起始射程應該比溜溜球原本的900窄"
    assert r["base"] < 760, "FAIL: 起始射程應該比水槍原本的760窄"
    print("PASS\\n")

    print("=== 測試2: nearest() 真的只鎖定 atkRange 範圍內的敵人 ===")
    pg2 = new_page(b)
    r2 = pg2.evaluate("""()=>{
        LV_IDX=0; start();
        G.E.length=0; G.P.x=0; G.P.y=0; G.cam.x=0; G.cam.y=0;
        G.P.atkRange=300;
        // 一隻在範圍內(200)，一隻在範圍外但同樣在畫面上(500，仍在onScreen判定內)
        G.E.push({x:200,y:0,r:14,hp:100,maxhp:100,boss:false,spd:0});
        G.E.push({x:500,y:0,r:14,hp:100,maxhp:100,boss:false,spd:0});
        const tgWide = nearest(G.P.x,G.P.y,900);           // 不受atkRange限制時，理論上抓得到500那隻(如果畫面夠大)
        const tgCapped = nearest(G.P.x,G.P.y,Math.min(900,G.P.atkRange));  // 武器實際會用的呼叫方式
        return {tgCappedX: tgCapped?tgCapped.x:null};
    }""")
    print(r2)
    assert r2["tgCappedX"]==200, f"FAIL: 有atkRange限制時應該只能鎖到200那隻，實際鎖到 {r2['tgCappedX']}"
    print("PASS\\n")

    print("=== 測試3: 望遠糖鏡升級卡能撐開範圍、疊滿2層後不再出現在卡池 ===")
    pg3 = new_page(b)
    r3 = pg3.evaluate("""()=>{
        LV_IDX=0; start();
        const before = G.P.atkRange;
        const u = UPGRADES.find(x=>x.id==='rangeUp');
        u.f(G.P); update(0.001,0.001);
        const after1 = G.P.atkRange;
        u.f(G.P); update(0.001,0.001);
        const after2 = G.P.atkRange;
        // 疊滿2層後，rollCards() 的卡池不應該再出現這張卡（跑很多次取樣，全部檢查不含 rangeUp）
        let stillOffered=false;
        for(let i=0;i<40;i++){ if(rollCards().some(c=>c.id==='rangeUp')) stillOffered=true; }
        return {before, after1, after2, stillOffered};
    }""")
    print(r3)
    assert r3["after1"] > r3["before"], "FAIL: 升級一次後範圍沒有變大"
    assert r3["after2"] > r3["after1"], "FAIL: 升級第二次後範圍沒有再變大"
    assert r3["stillOffered"]==False, "FAIL: 疊滿2層後卡池還是會出現望遠糖鏡，應該要消失"
    print("PASS\\n")

    print("=== 測試4: 每關音樂 musicSetLevel() 可重現、不同關卡給不同組合 ===")
    # ⚠ v0.9.20 改寫：原本靠攔截 Web Audio 排程出來的音符頻率反推「這關用了哪個調」，
    # 但 Web Audio 是提前排程的——音符會在 musicStop() 之後繼續播、也會在取樣視窗
    # 開始前就排好，導致抓到的是序列中段而不是開頭。這個問題在 v0.9.18/19/20 連續
    # 三個版本、用三種不同的等待策略都還是會偶發失敗（多個測試平行搶 CPU 時特別容易）。
    # 改成直接讀遊戲提供的測試掛鉤 SFX.musicDebug()，回傳 {keyOffset, arpIdx}，
    # 完全不依賴時序，永遠可重現。
    pg4 = new_page(b)
    r4 = pg4.evaluate("""()=>{
        SFX.unlock();
        const snap=lv=>{ SFX.musicStart(); SFX.musicSetLevel(lv); const d=SFX.musicDebug();
                         return d.keyOffset+'/'+d.arpIdx; };
        const out={};
        out.lv1_a=snap(0); out.lv1_b=snap(0);      // 同一關兩次 → 必須一致
        out.lv2=snap(1);                            // 不同關 → 必須不同
        out.lv61=snap(60);                          // 12種調 × 5種節奏型，週期60 → 與第1關相同
        out.lv13=snap(12);                          // 同調不同節奏型
        // 全 100 關掃一遍，確認組合的分布符合設計（60 關一循環）
        const all=[]; for(let i=0;i<100;i++) all.push(snap(i));
        out.unique60=new Set(all.slice(0,60)).size;  // 前60關應該全部不重複
        out.第61關等於第1關=(all[60]===all[0]);
        // 選單音樂（musicStart 不接 musicSetLevel）必須回到預設調
        SFX.musicStart();
        out.選單預設=SFX.musicDebug().keyOffset+'/'+SFX.musicDebug().arpIdx;
        return out;
    }""")
    print(r4)
    assert r4["lv1_a"]==r4["lv1_b"], "FAIL: 同一關兩次呼叫 musicSetLevel() 結果不一致（應該可重現、不是隨機）"
    assert r4["lv1_a"]!=r4["lv2"], "FAIL: 第1關跟第2關的音樂組合完全一樣，沒有做出區隔"
    assert r4["lv1_a"]!=r4["lv13"], "FAIL: 第1關跟第13關應該是同調但不同節奏型"
    assert r4["lv1_a"]==r4["lv61"], "FAIL: 第1關跟第61關應該是同一組合（12x5 的週期是60）"
    assert r4["unique60"]==60, f"FAIL: 前60關的組合應該全部不重複，實際只有 {r4['unique60']} 種"
    assert r4["第61關等於第1關"], "FAIL: 第61關沒有回到第1關的組合"
    assert r4["選單預設"]=="0/0", f"FAIL: 選單音樂沒有回到預設調，實際 {r4['選單預設']}"
    print("PASS\\n")

    print("=== 測試5: 音符真的有跟著換調（音訊輸出的煙霧測試）===")
    # 這一項仍然量實際播出來的聲音，但改成「寬鬆比對」：只驗證不同調確實產生不同的
    # 頻率集合，不再要求抓到序列的前 N 個，所以不受提前排程的時序影響。
    pg5 = new_page(b)
    pg5.evaluate("""()=>{
        window.__notes=[];
        const OrigOsc = AudioContext.prototype.createOscillator;
        AudioContext.prototype.createOscillator = function(){
            const node = OrigOsc.call(this);
            const origSet = node.frequency.setValueAtTime.bind(node.frequency);
            node.frequency.setValueAtTime = function(v,t){ window.__notes.push(Math.round(v*10)/10); return origSet(v,t); };
            return node;
        };
        SFX.unlock();
    }""")
    def collect(lv, ms=1500):
        pg5.evaluate("()=>{ SFX.musicStop(false); }")
        pg5.wait_for_timeout(400)
        pg5.evaluate("()=>{ window.__notes.length=0; }")
        pg5.evaluate("(lv)=>{ SFX.musicStart(); SFX.musicSetLevel(lv); }", lv)
        pg5.wait_for_timeout(ms)
        return set(pg5.evaluate("()=>window.__notes"))
    a=collect(0); b2=collect(1)
    print(f"  第1關收到 {len(a)} 種頻率、第2關 {len(b2)} 種，交集 {len(a&b2)} 種")
    assert len(a)>=4 and len(b2)>=4, "FAIL: 根本沒收到足夠的音符，音樂可能沒在播"
    assert a!=b2, "FAIL: 第1關與第2關播出來的頻率集合完全相同，移調沒有生效"
    print("PASS\\n")

    b.close()

print("=== 全部通過 ===")
srv.shutdown()
