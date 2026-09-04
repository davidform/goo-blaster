#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.21 新增：11 種語言下，畫在 canvas 上的文字有沒有「超出畫面」或「互相重疊」。

為什麼需要這支：
  v0.9.19 做完多語系後，只驗了「翻譯有沒有齊」，沒有驗「翻完放不放得下」。
  結果英文版的寶箱提示兩端被切出畫面、德文的關卡名壓到右上角數值、
  護盾指示跟關卡名只差 2px 直接疊在一起。
  「翻譯正確」跟「版面放得下」是兩件事——這支測後者。

做法：攔截 fillText，用當下的 ctx.font 量出每段文字的實際寬度，
      依 textAlign 算出左右邊界，逐項檢查：
      1. 不可以超出畫布左右邊
      2. 左上角 HUD 那幾行（LV/擊殺、關卡名、護盾、暴走）彼此不可以重疊
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8803
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

HOOK="""
window.__box=[];
(function(){
  const o=CanvasRenderingContext2D.prototype.fillText;
  CanvasRenderingContext2D.prototype.fillText=function(t,x,y,...a){
    if(t!=null && this.canvas && this.canvas.id!=='shot'){
      try{
        const w=this.measureText(String(t)).width;
        const al=this.textAlign;
        const left = al==='center' ? x-w/2 : al==='right' ? x-w : x;
        const m=/(\\d+(?:\\.\\d+)?)px/.exec(this.font||'');
        const fs=m?parseFloat(m[1]):12;
        window.__box.push({t:String(t),left,right:left+w,y,fs,cw:this.canvas.width/(window.devicePixelRatio||1)});
      }catch(e){}
    }
    return o.call(this,t,x,y,...a);
  };
})();
"""

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
    pg.add_init_script(HOOK)
    pg.goto(f"http://{'127.0.0.1'}:{PORT}/index.html"); pg.wait_for_timeout(700)

    langs=pg.evaluate("()=>LANGS.map(x=>x.c)")
    W=390

    print("=== 1. 所有 toast 提示在 11 種語言下都要放得進畫面 ===")
    TOASTS=[("tChest",[]),("tNukeDrop",[]),("tNukeGet",[]),("tFrenzy",[]),
            ("tShield",[]),("tRevive",[2]),("tNuke",[38]),("tAllMaxHeart",[]),
            ("tAllMaxGem",[]),("tMidBoss",[]),("tFreeze",[]),
            ("tBossIn",["Annual Review Asura"]),("tSuperBossIn",["Final KPI Judgment"]),
            ("noTouch",[])]
    for code in langs:
        over=[]
        for key,args in TOASTS:
            expect=pg.evaluate("""([code,key,args])=>{
                applyLanguage(code);
                if(!G||!G.running){ LV_IDX=0; start(); G.hasMoved=true; DIAG.touch=3; }
                G.TXT.length=0; window.__box.length=0;
                const s=T.apply(null,[key].concat(args));
                toast(s,'#fff');
                return s;
            }""",[code,key,args])
            pg.wait_for_timeout(90)
            boxes=pg.evaluate("()=>{const b=window.__box.slice(); window.__box.length=0; return b;}")
            # 只看「這段 toast 的整句或其中一行」——世界座標的粒子文字（emoji、傷害數字）
            # 也會經過 fillText，但它們的 x/y 是世界座標，拿來判斷出界毫無意義。
            for bx in boxes:
                if bx["t"] in expect and len(bx["t"])>=3 and (bx["left"]<-1 or bx["right"]>W+1):
                    over.append((key,bx["t"][:40],round(bx["left"]),round(bx["right"])))
        ck(f"[{code}] 14 種提示全部沒有超出畫面", not over, over[:3])

    print("\n=== 2. 最長關卡名 + 護盾 + 暴走：左上角 HUD 不重疊、不超寬 ===")
    for code in langs:
        r=pg.evaluate("""(code)=>{
            applyLanguage(code);
            // 找出這個語言最長的關卡名
            let worst=0, wi=0;
            for(let i=0;i<LEVELS.length;i++){
                const s=T('hudStage',i+1,LEVELS[i].n,tierName(LEVELS[i].tier));
                if(s.length>worst){ worst=s.length; wi=i; }
            }
            LV_IDX=wi; start(); G.hasMoved=true; DIAG.touch=3;
            G.P.shieldN=2; G.P.frenzyT=6; G.kills=99999; G.P.lv=99;
            G.TXT.length=0;
            return {lv:wi+1, name:LEVELS[wi].n};
        }""",code)
        pg.evaluate("()=>{ window.__box.length=0; }")
        pg.wait_for_timeout(260)
        boxes=pg.evaluate("()=>{const b=window.__box.slice(); window.__box.length=0; return b;}")
        # 只看左上角 HUD 區（y 在 60~180、左半邊起頭）
        hud=[bx for bx in boxes if 55<bx["y"]<190 and bx["left"]<W*0.75]
        # 去重（每幀都會畫）。
        # ⚠ 不能用原文當 key：果凍% / 傷害+% 每幀數值都在變，
        #   同一行會被當成兩行、y 又完全相同 → 誤判成「疊字」。
        #   把數字抽掉再當 key，同一行不管數值多少都收斂成一筆。
        import re as _re
        uniq={}
        for bx in hud: uniq[_re.sub(r"\d+", "#", bx["t"])]=bx
        hud=list(uniq.values())
        over=[bx for bx in hud if bx["left"]<-1 or bx["right"]>W+1]
        ck(f"[{code}] 左上角 HUD 沒有超出畫面（最長關名：第{r['lv']}關）",
           not over, [(x['t'][:34],round(x['right'])) for x in over[:2]])
        # 兩兩檢查：y 差 < 字高 且 x 有重疊 → 視為疊字
        clash=[]
        for i in range(len(hud)):
            for j in range(i+1,len(hud)):
                a,bb=hud[i],hud[j]
                if abs(a["y"]-bb["y"]) < max(a["fs"],bb["fs"])*0.85 \
                   and a["left"] < bb["right"]-1 and bb["left"] < a["right"]-1:
                    clash.append((a["t"][:26],bb["t"][:26],round(a["y"]),round(bb["y"])))
        ck(f"[{code}] 左上角 HUD 沒有兩行疊在一起", not clash, clash[:2])

    print("\n=== 3. 右上角數值不會被關卡名撞到 ===")
    for code in ['en','de','ru','pt-BR']:
        pg.evaluate("""(code)=>{
            applyLanguage(code);
            let worst=0,wi=0;
            for(let i=0;i<LEVELS.length;i++){
                const s=T('hudStage',i+1,LEVELS[i].n,tierName(LEVELS[i].tier));
                if(s.length>worst){worst=s.length;wi=i;}
            }
            LV_IDX=wi; start(); G.hasMoved=true; DIAG.touch=3; G.TXT.length=0;
        }""",code)
        # 固定睡 260ms 在高負載掉幀時可能一幀都沒畫到 → 抓不到要比對的兩行。
        # 改成輪詢累積，直到兩行都出現為止。
        want0=pg.evaluate("""()=>({
            stage: T('hudStage',G.lvIdx+1,G.L.n,tierName(G.L.tier)),
            goo:   T('hudGoo',gooPct(),Math.round(gooPct()*0.30))
        })""")
        pg.evaluate("()=>{ window.__box.length=0; }")
        boxes=[]
        for _ in range(40):
            pg.wait_for_timeout(150)
            boxes+=pg.evaluate("()=>{const b=window.__box.slice(); window.__box.length=0; return b;}")
            ts=set(b["t"] for b in boxes)
            if any(t==want0["stage"] or t.endswith("…") for t in ts) and \
               any(t.split()[0]==want0["goo"].split()[0] for t in ts if t.strip()):
                break
        uniq={}
        for bx in boxes: uniq[bx["t"]]=bx
        boxes=list(uniq.values())
        want=pg.evaluate("""()=>({
            stage: T('hudStage',G.lvIdx+1,G.L.n,tierName(G.L.tier)),
            goo:   T('hudGoo',gooPct(),Math.round(gooPct()*0.30))
        })""")
        # 關卡名可能已被截斷成「前綴…」，所以用前綴比對
        pref=want["stage"][:14]
        stage=[bx for bx in boxes if bx["t"]==want["stage"] or
               (bx["t"].endswith("…") and bx["t"][:14]==pref)]
        right=[bx for bx in boxes if bx["t"]==want["goo"]]
        clash=[]
        if not stage or not right:
            clash.append(("找不到要比對的兩行", str(want)[:60]))
        for a in stage:
            for bb in right:
                # 兩行都在畫面上方、y 很接近時，水平方向必須完全分開
                if abs(a["y"]-bb["y"])<max(a["fs"],bb["fs"]) and a["right"]>bb["left"]-6:
                    clash.append((a["t"][:36]+f' →{round(a["right"])}',
                                  bb["t"][:24]+f' ←{round(bb["left"])}'))
        ck(f"[{code}] 關卡名沒有壓到右上角的果凍%/傷害+%", not clash, clash[:2])

    ck("無 JS 錯誤", not errs, errs[:2])
    b.close()
srv.shutdown()
print()
if fails:
    print(f"❌ 失敗 {len(fails)} 項"); sys.exit(1)
print("=== 全部通過：11 種語言的版面都放得下、沒有疊字 ===")
