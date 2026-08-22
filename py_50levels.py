#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v0.9.23：100 關 → 50 關重構的結構驗收（不含難度平衡，那個交給 py_balance.py）。"""
import http.server, socketserver, threading, functools, sys, json
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8811
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
    def page(store=None):
        c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                        is_mobile=True,has_touch=True,locale="en-US")
        pg=c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e)))
        if store:
            pg.add_init_script("localStorage.setItem('%s',%s)"%(store[0],json.dumps(json.dumps(store[1]))))
        pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(600)
        return pg,c,errs

    pg,c,errs=page()
    key=pg.evaluate("()=>PROG_KEY")
    print("=== 1. 關卡總數與章節結構 ===")
    r=pg.evaluate("""()=>{
        const out=LEVELS.map((L,i)=>({i:i+1, ch:L.ch, idx:L.idxInCh, superBoss:!!L.superBoss,
            bc:(L.bossChapter===undefined?null:L.bossChapter), dur:L.dur, tier:L.tier,
            nboss:L.nboss, kind:L.kind||''}));
        return out;
    }""")
    ck("總關卡數 = 50", len(r)==50, len(r))
    boss=[x for x in r if x["superBoss"]]
    ck("章節 Boss 共 10 關", len(boss)==10, len(boss))
    ck("章節 Boss 落在第 5,10,15,…,50 關",
       [x["i"] for x in boss]==[5,10,15,20,25,30,35,40,45,50], [x["i"] for x in boss])
    ck("bossChapter 依序 0..9", [x["bc"] for x in boss]==list(range(10)), [x["bc"] for x in boss])
    ck("每一關都有 ch（0..9），且每章剛好 5 關",
       all(x["ch"] is not None for x in r) and
       all(sum(1 for x in r if x["ch"]==k)==5 for k in range(10)),
       [sum(1 for x in r if x['ch']==k) for k in range(10)])
    ck("章節內編號 idxInCh 都是 1..5",
       all(sorted(x["idx"] for x in r if x["ch"]==k)==[1,2,3,4,5] for k in range(10)))
    durs=[x["dur"] for x in r]
    ck("單關時長 70~240 秒（原本最長 323）", min(durs)==70 and max(durs)==240, (min(durs),max(durs)))
    ck("全破一次的純遊玩時間 < 200 分鐘", sum(durs)/60 < 200, f"{sum(durs)/60:.0f} 分鐘")
    ck("最後一關獨佔 tier 13（終焉）", r[49]["tier"]==13, r[49]["tier"])

    print("\n=== 2. 難度終點必須跟舊版第 100 關完全相同 ===")
    r2=pg.evaluate("()=>{ const L=LEVELS[49]; return {rate:L.rate,hp:L.hp,espd:L.espd,bspd:L.bspd,bossHp:L.bossHp,atkSlow:L.atkSlow,maxE:L.maxE,xpMul:L.xpMul,startWep:L.startWep}; }")
    print("   新第50關:",r2)
    EXPECT={"rate":3.036,"hp":4.048,"espd":1.85,"bspd":2.3,"bossHp":4.301,"atkSlow":0.64,"maxE":150,"xpMul":5.95}
    for k,v in EXPECT.items():
        ck(f"第50關 {k} = 舊第100關的 {v}", abs(r2[k]-v)<0.002, r2[k])
    ck("第50關起始武器 = 舊第100關的 {bubble:2,graffiti:5,yoyo:5}",
       r2["startWep"]=={"bubble":2,"graffiti":5,"yoyo":5}, r2["startWep"])

    print("\n=== 3. Boss 造型：10 種全部用得上、逐章升級 ===")
    r3=pg.evaluate("""()=>{
        const out=[];
        for(const lv of [4,9,14,19,24,29,34,39,44,49]){
            LV_IDX=lv; start();
            const bs=G.bosses, fin=bs[bs.length-1];
            out.push({lv:lv+1, name:fin.name, skin:fin.skin||[], mid:(bs[0].skin||[]), n:bs.length});
        }
        return out;
    }""")
    for x in r3:
        print(f"    第{x['lv']:>2}關  {x['name']:<24} {'+'.join(x['skin'])}   （場上共 {x['n']} 隻 Boss）")
    ck("10 個章節 Boss 名稱全部不同", len(set(x["name"] for x in r3))==10)
    ck("造型件數 1 → 6 遞增", len(r3[0]["skin"])==1 and len(r3[9]["skin"])==6,
       [len(x["skin"]) for x in r3])
    ck("六種特徵都有用到",
       set(sum([x["skin"] for x in r3],[]))=={'spike','armor','horn','crown','wing','aura'})
    ck("第5關（第一個章節 Boss 關）場上總 Boss 數 = 2（不要一開始就 3 隻）",
       r3[0]["n"]==2, r3[0]["n"])
    ck("無 JS 錯誤", not errs, errs[:2])
    pg.close(); c.close()

    print("\n=== 4. 舊存檔遷移（100 關進度 → 50 關）===")
    CASES=[(1,1),(2,2),(11,6),(21,11),(51,26),(100,51),(101,51)]
    for oldp,wantp in CASES:
        pg,c,_=page((key,{"progress":oldp,"coins":1234,"meta":{"dmg":2},"lang":"ja"}))
        got=pg.evaluate("()=>({p:PROGRESS,c:COINS,m:META,l:LANG,raw:localStorage.getItem(PROG_KEY)})")
        ck(f"舊進度 {oldp:>3} → 新進度 {wantp}", got["p"]==wantp, got["p"])
        if oldp==11:
            ck("  糖果幣不受影響", got["c"]==1234, got["c"])
            ck("  永久強化不受影響", got["m"]=={"dmg":2}, got["m"])
            ck("  語言偏好不受影響", got["l"]=="ja", got["l"])
            ck("  遷移後有寫入版本標記 v=2", '"v":2' in (got["raw"] or ""), got["raw"])
        pg.close(); c.close()

    print("\n=== 5. 遷移只做一次（重載不會越切越小）===")
    pg,c,_=page((key,{"progress":51,"coins":0,"meta":{},"lang":"en"}))
    p1=pg.evaluate("()=>PROGRESS"); pg.reload(); pg.wait_for_timeout(600)
    p2=pg.evaluate("()=>PROGRESS"); pg.reload(); pg.wait_for_timeout(600)
    p3=pg.evaluate("()=>PROGRESS")
    ck("重載兩次進度都不變", p1==p2==p3==26, (p1,p2,p3))
    pg.close(); c.close()

    print("\n=== 6. 新存檔（已是 v2）不會再被遷移 ===")
    pg,c,_=page((key,{"progress":40,"coins":0,"meta":{},"lang":"en","v":2}))
    ck("v=2 的存檔進度原封不動", pg.evaluate("()=>PROGRESS")==40, pg.evaluate("()=>PROGRESS"))
    pg.close(); c.close()

    print("\n=== 7. 糖果幣：關卡加成隨新編號重算 ===")
    pg,c,_=page()
    r7=pg.evaluate("""()=>({
        新第50關通關:runCoins(true,49,900,240,240),
        新第25關通關:runCoins(true,24,500,215,215),
        第1關通關:runCoins(true,0,120,70,70),
        上限:runCoins(true,49,99999,240,240)
    })""")
    print("   ",r7)
    ck("最終關的單場收益仍在上限 520 以內", r7["上限"]<=520, r7["上限"])
    r7b=pg.evaluate("()=>META_UPGRADES.reduce((s,u)=>s+Array.from({length:u.max},(_,n)=>u.cost(n)).reduce((a,b)=>a+b,0),0)")
    ck(f"單場最高收益 < 買滿商店總價（{r7b}）的 20%", r7["上限"]/r7b<0.20, f"{100*r7['上限']/r7b:.1f}%")
    pg.close(); c.close()
    b.close()
srv.shutdown()
print()
if fails: print(f"❌ 失敗 {len(fails)} 項：{fails[:8]}"); sys.exit(1)
print("=== 全部通過 ===")
