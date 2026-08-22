#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.21 新增 7 個 key 的逐語言驗收（第 2 輪：主動找邊角案例）。

檢查項目：
  1. 11 種語言都有這 7 個 key，且不是回退成 key 名稱本身
  2. 佔位符 {0}/{1}/{2} 全部被代換掉，畫面上不會出現裸的 {0}
  3. 非 CJK 語言不含中日韓字元；CJK 語言確實含該語系字元（防止整批漏翻成英文而沒被發現）
  4. 執行中切換語言，HUD 與 toast 立刻跟著換（不是只有重載才生效）
  5. 數值代換正確（護盾層數、擊殺數、果凍%）
"""
import http.server, socketserver, threading, functools, sys, re, json
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8797
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

NEWKEYS=["tChest","tNukeDrop","tNukeGet","hudShield","hudFrenzy","shotStats","shotGoo"]
CJK=re.compile(r'[぀-ヿ一-鿿가-힯]')
HAN=re.compile(r'[一-鿿]'); KANA=re.compile(r'[぀-ヿ]'); HANGUL=re.compile(r'[가-힯]')
CYR=re.compile(r'[А-Яа-яЁё]')
LATIN_ONLY=['en','de','fr','es','it','pt-BR']

fails=[]
def ck(name,cond,extra=""):
    print(("  PASS  " if cond else "  FAIL  ")+name+(("  "+str(extra)) if extra else ""))
    if not cond: fails.append(name)

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(600)

    langs=pg.evaluate("()=>LANGS.map(x=>x.c)")
    print("=== 1~3. 逐語言檢查 7 個新 key ===")
    for code in langs:
        r=pg.evaluate("""(code)=>{
            const old=LANG; applyLanguage(code);
            const out={};
            out.tChest=T('tChest'); out.tNukeDrop=T('tNukeDrop'); out.tNukeGet=T('tNukeGet');
            out.hudShield=T('hudShield',3); out.hudFrenzy=T('hudFrenzy');
            out.shotStats=T('shotStats','1:23',12,180); out.shotGoo=T('shotGoo',47);
            applyLanguage(old);
            return out;
        }""", code)
        vals=list(r.values())
        ck(f"[{code}] 7 個 key 都有翻譯（沒有回退成 key 名）",
           all(r[k]!=k for k in NEWKEYS),
           [k for k in NEWKEYS if r[k]==k])
        ck(f"[{code}] 沒有殘留的 {{n}} 佔位符",
           not any(re.search(r'\{\d\}',v) for v in vals),
           [v for v in vals if re.search(r'\{\d\}',v)])
        ck(f"[{code}] 數值有代進去（3 / 12 / 180 / 47）",
           '3' in r['hudShield'] and '12' in r['shotStats'] and '180' in r['shotStats'] and '47' in r['shotGoo'],
           [r['hudShield'],r['shotStats'],r['shotGoo']])
        if code in LATIN_ONLY:
            ck(f"[{code}] 不含中日韓字元", not any(CJK.search(v) for v in vals),
               [v for v in vals if CJK.search(v)])
        if code=='ru':
            ck("[ru] 確實是俄文（含西里爾字母）", all(CYR.search(v) for v in vals[:5]))
            ck("[ru] 不含中日韓字元", not any(CJK.search(v) for v in vals))
        if code in ('zh-Hant','zh-Hans'):
            ck(f"[{code}] 確實是中文（含漢字）", all(HAN.search(v) for v in vals))
        if code=='ja':
            ck("[ja] 確實是日文（含假名）", any(KANA.search(v) for v in vals))
        if code=='ko':
            ck("[ko] 確實是韓文（含諺文）", all(HANGUL.search(v) for v in vals))

    print("\n=== 4. 執行中切換語言，畫面立刻跟著換 ===")
    pg.evaluate("""()=>{
        window.__drawn=[];
        for(const fn of ['fillText']){
          const o=CanvasRenderingContext2D.prototype[fn];
          CanvasRenderingContext2D.prototype[fn]=function(t,...a){
            if(t!=null) window.__drawn.push(String(t)); return o.call(this,t,...a); };
        }
        LV_IDX=0; start(); G.hasMoved=true; DIAG.touch=3;
        G.P.shieldN=2; G.P.frenzyT=5;
    }""")
    pg.wait_for_timeout(500)
    def hud_has(sub):
        d=pg.evaluate("()=>{const d=window.__drawn.slice(); window.__drawn.length=0; return d;}")
        return any(sub in t for t in d)
    pg.evaluate("()=>{ window.__drawn.length=0; }"); pg.wait_for_timeout(300)
    ck("英文時 HUD 顯示 Shield", hud_has("Shield"))
    pg.evaluate("()=>applyLanguage('ja')"); pg.wait_for_timeout(400)
    pg.evaluate("()=>{ window.__drawn.length=0; }"); pg.wait_for_timeout(300)
    ck("切成日文後 HUD 立刻變成シールド（不必重載）", hud_has("シールド"))
    pg.evaluate("()=>applyLanguage('ru')"); pg.wait_for_timeout(400)
    pg.evaluate("()=>{ window.__drawn.length=0; }"); pg.wait_for_timeout(300)
    ck("切成俄文後 HUD 立刻變成 Щит", hud_has("Щит"))
    pg.evaluate("()=>applyLanguage('en')"); pg.wait_for_timeout(300)

    print("\n=== 5. toast 走的是 T()（切語言後內容跟著變）===")
    for code,expect in [('en','chest'),('ja','宝箱'),('de','Truhe'),('pt-BR','baú')]:
        got=pg.evaluate("""(code)=>{ const o=LANG; applyLanguage(code);
            const s=T('tChest'); applyLanguage(o); return s; }""", code)
        ck(f"[{code}] tChest 內容正確", expect.lower() in got.lower(), got[:50])

    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
print()
if fails:
    print(f"❌ 失敗 {len(fails)} 項：{fails[:8]}"); sys.exit(1)
print("=== 全部通過 ===")
