#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.28：原生儲存層。

上架前的第一風險（docs-12）：包成 WebView App 之後 localStorage 可能被 OS 清掉，
付費玩家的進度、糖果幣、買斷解鎖狀態會全部消失。

這支用「假的 Capacitor Preferences 外掛」把原生環境模擬出來，驗證：
  1. 純網頁版（沒有 Capacitor）行為與 v0.9.27 完全相同 —— 這條最重要
  2. 有原生外殼時，存檔會同時寫進原生儲存
  3. localStorage 被清掉之後，原生儲存還救得回來 ← 這就是整件事的目的
  4. 兩份存檔打架時，玩家不會倒退（進度取高、買斷狀態 OR）
  5. 第一次在原生外殼裡跑，既有的網頁存檔會被搬進去（一次性遷移）
  6. 原生外掛壞掉/丟例外時，遊戲不會當掉（降級成純 localStorage）
"""
import http.server, socketserver, threading, functools, sys, json, os
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8871
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

# 假的 Capacitor Preferences。用 window.name 當儲存體——它是這個分頁裡
# 唯一「清掉 localStorage 也不會跟著消失」的地方，正好模擬原生儲存的特性。
FAKE_NATIVE = """
(()=>{
  window.__nativeDB = {};
  window.__nativeFail = false;          // 測試 6 用：讓外掛開始丟例外
  window.Capacitor = { Plugins: { Preferences: {
    get({key}){
      if(window.__nativeFail) return Promise.reject(new Error('boom'));
      return Promise.resolve({value: window.__nativeDB[key] ?? null});
    },
    set({key,value}){
      if(window.__nativeFail) return Promise.reject(new Error('boom'));
      window.__nativeDB[key]=value; return Promise.resolve();
    }
  }}};
})();
"""

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    def page(native=False, init=None):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); pg.set_default_timeout(60000)
        errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        # ⚠ 一定要用 add_init_script：外掛必須在遊戲程式跑之前就存在，
        #   不然 hydrateFromNative() 偵測不到，測到的就是純網頁路徑。
        if native: pg.add_init_script(FAKE_NATIVE)
        if init: pg.add_init_script(init)
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(800)
        return pg,c,errs

    # ═══ 1. 純網頁版：行為必須跟 v0.9.27 一模一樣 ═══
    print("=== 1. 純網頁版（沒有 Capacitor）===")
    pg,c,errs=page(native=False)
    r=pg.evaluate("""()=>{
        PROGRESS=7; COINS=333; META={dmg:2}; PREM_OWNED=false; saveGame();
        return {nativeAvail:NATIVE_STORE.available(), ready:NATIVE_READY,
                ls:JSON.parse(localStorage.getItem(PROG_KEY)),
                hasCapacitor:!!window.Capacitor};
    }""")
    print(f"  {r['ls']}")
    ck("偵測不到原生外殼", not r['nativeAvail'] and not r['hasCapacitor'])
    ck("hydrate 立刻結束、沒有卡住", r['ready'])
    ck("localStorage 照常寫入", r['ls']['progress']==7 and r['ls']['coins']==333)
    pg.reload(); pg.wait_for_timeout(700)
    r=pg.evaluate("()=>({p:PROGRESS,c:Math.round(COINS),m:META})")
    ck("重新載入後讀得回來", r['p']==7 and r['c']==333 and r['m']=={'dmg':2}, r)
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 2. 原生外殼：存檔要同時寫進原生儲存 ═══
    print("\n=== 2. 有原生外殼時，存檔同時寫兩邊 ===")
    pg,c,errs=page(native=True)
    r=pg.evaluate("""()=>{
        PROGRESS=12; COINS=880; META={hearts:3}; PREM_OWNED=true; saveGame();
        return {avail:NATIVE_STORE.available()};
    }""")
    ck("偵測到原生外殼", r['avail'])
    pg.wait_for_timeout(400)                 # 原生寫入是非同步的，等它落地
    r=pg.evaluate("""()=>({
        native: window.__nativeDB[PROG_KEY] ? JSON.parse(window.__nativeDB[PROG_KEY]) : null,
        web: JSON.parse(localStorage.getItem(PROG_KEY))
    })""")
    print(f"  原生：{r['native']}")
    ck("原生儲存有寫入", r['native'] is not None)
    ck("原生與 localStorage 內容一致",
       r['native']==r['web'], (r['native'], r['web']))
    ck("買斷狀態有存進原生", r['native'] and r['native']['prem']==1)
    ck("無 JS 錯誤", not errs, errs[:2])

    # ═══ 3. ⭐ 核心情境：localStorage 被 OS 清掉 ═══
    print("\n=== 3. ⭐ localStorage 被清掉，原生儲存救得回來 ===")
    saved=pg.evaluate("()=>window.__nativeDB[PROG_KEY]")
    # 模擬 OS 清掉 WebView 快取：只清 localStorage，原生儲存留著
    pg.evaluate("()=>{ localStorage.clear(); }")
    r=pg.evaluate("()=>({ls:localStorage.getItem(PROG_KEY)})")
    ck("localStorage 確實被清空了", r['ls'] is None)
    pg.close(); c.close()

    # 重開一個分頁，把剛才那份原生存檔塞回去（模擬 App 重新啟動）
    pg,c,errs=page(native=True, init=f"""
        window.addEventListener('DOMContentLoaded',()=>{{}});
        (()=>{{ const wait=setInterval(()=>{{
            if(window.__nativeDB){{ window.__nativeDB[{json.dumps('gooblaster_save_v3')}]={json.dumps(saved)}; clearInterval(wait); }}
        }},0); }})();
    """)
    pg.wait_for_timeout(1200)                # 等 hydrateFromNative() 跑完
    r=pg.evaluate("""()=>({p:PROGRESS, c:Math.round(COINS), m:META, prem:PREM_OWNED,
                           ready:NATIVE_READY,
                           ls:localStorage.getItem(PROG_KEY)?JSON.parse(localStorage.getItem(PROG_KEY)):null})""")
    print(f"  救回來的狀態：進度 {r['p']} 糖果幣 {r['c']} 買斷 {r['prem']}")
    ck("進度救回來了", r['p']==12, r['p'])
    ck("糖果幣救回來了", r['c']==880, r['c'])
    ck("永久強化救回來了", r['m']=={'hearts':3}, r['m'])
    ck("⭐ 買斷解鎖狀態救回來了（這是付費玩家最在意的）", r['prem'] is True, r['prem'])
    ck("localStorage 也被重新填回去", r['ls'] and r['ls']['progress']==12, r['ls'])
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 4. 兩份打架：玩家不可以倒退 ═══
    print("\n=== 4. 原生與 localStorage 不一致時，取對玩家有利的那份 ===")
    pg,c,errs=page(native=False)
    r=pg.evaluate("""()=>{
        const A={progress:20,coins:100,prem:0,v:2};
        const B={progress:5, coins:900,prem:1,v:2};
        const r1=pickBetterSave(A,B), r2=pickBetterSave(B,A);
        const T={progress:9,coins:50,prem:0,v:2}, U={progress:9,coins:70,prem:0,v:2};
        return {r1,r2, tie:pickBetterSave(T,U),
                nullA:pickBetterSave(null,B), nullB:pickBetterSave(A,null)};
    }""")
    print(f"  進度20/幣100/未買斷  vs  進度5/幣900/已買斷 → {r['r1']}")
    ck("進度高的那份贏", r['r1']['progress']==20 and r['r2']['progress']==20, r['r1'])
    ck("⭐ 買斷狀態只要有一邊是 true 就保留（付過的錢不能消失）",
       r['r1']['prem']==1 and r['r2']['prem']==1, r['r1'])
    ck("糖果幣取兩邊的最大值（不讓玩家倒扣）",
       r['r1']['coins']==900 and r['r2']['coins']==900, r['r1'])
    ck("進度平手時比糖果幣", r['tie']['coins']==70, r['tie'])
    ck("其中一邊是 null 時回傳另一邊", r['nullA']['progress']==5 and r['nullB']['progress']==20)
    pg.close(); c.close()

    # ═══ 5. 一次性遷移：第一次在原生外殼裡跑 ═══
    print("\n=== 5. 第一次在原生外殼裡跑，網頁存檔要搬進原生儲存 ===")
    pg,c,errs=page(native=True, init="""
        window.addEventListener('load',()=>{});
        localStorage.setItem('gooblaster_save_v3',
          JSON.stringify({progress:31,coins:1500,meta:{dmg:4},lang:'en',v:2,prem:1}));
    """)
    pg.wait_for_timeout(1200)
    r=pg.evaluate("""()=>({
        native: window.__nativeDB[PROG_KEY] ? JSON.parse(window.__nativeDB[PROG_KEY]) : null,
        p:PROGRESS, prem:PREM_OWNED })""")
    print(f"  搬過去的內容：{r['native']}")
    ck("網頁存檔已經搬進原生儲存", r['native'] is not None and r['native']['progress']==31, r['native'])
    ck("買斷狀態一起搬過去", r['native'] and r['native']['prem']==1)
    ck("遊戲內的進度沒有被改動", r['p']==31 and r['prem'] is True, (r['p'],r['prem']))
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 6. 原生外掛壞掉時要降級，不可以當掉 ═══
    print("\n=== 6. 原生外掛丟例外時，遊戲要能繼續（降級成純 localStorage）===")
    pg,c,errs=page(native=True, init="""
        window.addEventListener('load',()=>{});
    """)
    r=pg.evaluate("""()=>{
        window.__nativeFail=true;                  // 從現在開始所有原生呼叫都失敗
        PROGRESS=17; COINS=42; saveGame();         // 不可以丟例外
        return {ls:JSON.parse(localStorage.getItem(PROG_KEY))};
    }""")
    pg.wait_for_timeout(400)
    ck("原生失敗時 localStorage 仍然寫得進去", r['ls']['progress']==17, r['ls'])
    r2=pg.evaluate("()=>hydrateFromNative().then(v=>({ok:true,v})).catch(e=>({ok:false,e:String(e)}))")
    ck("hydrate 遇到例外會自己吞掉、不會炸出去", r2.get('ok') is True, r2)
    ck("遊戲仍然可以開始", pg.evaluate("()=>{ LV_IDX=0; start(); return !!(G&&G.running); }"))
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # ═══ 7. 測試循環 2：邊角 ═══
    print("\n=== 7. 邊角案例 ===")

    # 7a. 原生儲存裡是壞掉的 JSON
    pg,c,errs=page(native=True, init="""
        (()=>{ const w=setInterval(()=>{ if(window.__nativeDB){
            window.__nativeDB['gooblaster_save_v3']='{這不是合法的JSON';
            clearInterval(w);} },0); })();
        localStorage.setItem('gooblaster_save_v3',
          JSON.stringify({progress:6,coins:60,meta:{},lang:'en',v:2,prem:0}));
    """)
    pg.wait_for_timeout(1200)
    r=pg.evaluate("()=>({p:PROGRESS, ready:NATIVE_READY, running:!!(G&&G.running)})")
    ck("[7a] 原生存檔壞掉時，退回用 localStorage 的那份", r['p']==6, r['p'])
    ck("[7a] hydrate 有正常結束", r['ready'])
    ck("[7a] 無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 7b. hydrate 還沒跑完，玩家就按了開始
    pg,c,errs=page(native=True, init="""
        (()=>{ const w=setInterval(()=>{ if(window.__nativeDB){
            window.__nativeDB['gooblaster_save_v3']=JSON.stringify(
              {progress:40,coins:5000,meta:{dmg:5},lang:'en',v:2,prem:1});
            clearInterval(w);} },0); })();
    """)
    # 不等 hydrate，直接開一局
    r=pg.evaluate("""()=>{ LV_IDX=0; start(); return {running:!!(G&&G.running)}; }""")
    ck("[7b] 遊戲開得起來", r['running'])
    pg.wait_for_timeout(1200)                # 讓 hydrate 在遊戲進行中完成
    r=pg.evaluate("""()=>({running:!!(G&&G.running), p:PROGRESS, prem:PREM_OWNED,
                           menuHidden:document.getElementById('menu').classList.contains('hide')})""")
    print(f"  [7b] hydrate 在遊戲中完成後：{r}")
    ck("[7b] ⭐ 不會把玩家踢回主選單", r['running'] and r['menuHidden'], r)
    ck("[7b] 原生存檔仍然有被套用", r['p']==40 and r['prem'] is True, (r['p'],r['prem']))
    ck("[7b] 無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 7c. 玩家在 hydrate 完成前就存了更新的進度 → 不可以被舊的原生存檔蓋掉
    pg,c,errs=page(native=True, init="""
        (()=>{ const w=setInterval(()=>{ if(window.__nativeDB){
            window.__nativeDB['gooblaster_save_v3']=JSON.stringify(
              {progress:3,coins:10,meta:{},lang:'en',v:2,prem:0});   // 原生是舊的
            clearInterval(w);} },0); })();
    """)
    pg.evaluate("()=>{ PROGRESS=25; COINS=2000; PREM_OWNED=true; saveGame(); }")
    pg.wait_for_timeout(1200)
    r=pg.evaluate("()=>({p:PROGRESS, c:Math.round(COINS), prem:PREM_OWNED})")
    print(f"  [7c] 本機進度 25 vs 原生進度 3 → {r}")
    ck("[7c] ⭐ 新的本機進度不會被舊的原生存檔蓋掉", r['p']==25, r['p'])
    ck("[7c] 糖果幣沒有倒退", r['c']==2000, r['c'])
    ck("[7c] 買斷狀態保留", r['prem'] is True)
    ck("[7c] 無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 7d. 更早的舊存檔格式（純數字）在原生外殼裡也要能遷移
    # ⚠ key 是 OLD_PROG_KEY='gooblaster_progress_v2'。
    #   第一版我隨手寫成 'gooblaster_lv'，結果什麼都沒遷移 → 假失敗。
    #   碰到常數就去程式裡查實際值，不要憑印象打。
    pg,c,errs=page(native=True, init="""
        localStorage.setItem('gooblaster_progress_v2','9');
    """)
    pg.wait_for_timeout(1200)
    r=pg.evaluate("""()=>({p:PROGRESS,
        ls:localStorage.getItem(PROG_KEY)?JSON.parse(localStorage.getItem(PROG_KEY)):null,
        nat:window.__nativeDB[PROG_KEY]?JSON.parse(window.__nativeDB[PROG_KEY]):null})""")
    print(f"  [7d] 舊格式遷移：{r}")
    ck("[7d] 舊格式存檔沒有把遊戲弄壞", r['p']>=1 and r['ls'] is not None, r)
    ck("[7d] 遷移後的內容也進了原生儲存", r['nat'] is not None, r['nat'])
    ck("[7d] 無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    # 7e. 存檔被頻繁呼叫時不能拖慢遊戲（saveGame 不 await 原生寫入）
    pg,c,errs=page(native=True)
    r=pg.evaluate("""()=>{
        const t0=performance.now();
        for(let i=0;i<300;i++){ PROGRESS=(i%40)+1; saveGame(); }
        return {ms:+(performance.now()-t0).toFixed(1)};
    }""")
    print(f"  [7e] 連續存檔 300 次耗時 {r['ms']}ms")
    ck("[7e] 300 次存檔在 1 秒內（沒有 await 原生寫入）", r['ms']<1000, r['ms'])
    ck("[7e] 無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    b.close()
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails}"); sys.exit(1)
print("=== 原生儲存層全部通過 ===")
