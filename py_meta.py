#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""局外成長系統測試（v0.9.17 新增）

涵蓋：
  1) 舊存檔（純數字格式）自動遷移，破關進度不能歸零
  2) 糖果幣結算：輸也要給、通關有加成、後期關卡給更多、有保底也有上限
  3) 購買永久強化 → 寫入存檔 → 重新載入後仍在
  4) 永久強化真的套用到玩家的起始狀態上（而且沒買時完全不影響原本數值）
  5) 重生蠟燭真的會復活，用完之後才真的結束遊戲
  6) 經濟平衡防呆：單場收益不能高到「一場就買滿商店」
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

ROOT="/home/claude/goo/game"; PORT=8776
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

def page(b, init=None):
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True)
    pg=c.new_page()
    if init: pg.add_init_script(init)
    pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(400)
    return pg

with sync_playwright() as pw:
    b=pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

    print("=== 測試1：舊存檔（純數字）自動遷移 ===")
    pg=page(b, "localStorage.setItem('gooblaster_progress_v2','47');")
    r=pg.evaluate("()=>({P:PROGRESS,C:COINS,M:META,raw:localStorage.getItem('gooblaster_save_v3')})")
    print(f"  舊存檔『47』→ PROGRESS={r['P']} COINS={r['C']} 新存檔={r['raw']}")
    assert r['P']==47, "FAIL: 舊存檔的破關進度沒有正確遷移（老玩家進度會歸零）"
    print("  PASS\n")

    print("=== 測試2：糖果幣結算規則 ===")
    pg=page(b)
    r=pg.evaluate("""()=>({
        第1關陣亡: runCoins(false,0,60,40,70),
        第1關通關: runCoins(true ,0,125,60,70),
        第30關半途: runCoins(false,29,600,140,282),
        第50關通關: runCoins(true,49,2000,313,313),
        第100關通關: runCoins(true,99,4300,323,323),
        零表現保底: runCoins(false,0,0,0,70)
    })""")
    for k,v in r.items(): print(f"  {k}: {v} 幣")
    assert r['零表現保底']>0, "FAIL: 完全沒表現也該有保底（死掉沒收穫＝留存迴圈斷掉）"
    assert r['第1關通關']>r['第1關陣亡'], "FAIL: 通關沒有額外獎勵"
    assert r['第30關半途']>r['第1關陣亡'], "FAIL: 後期關卡沒給更多（玩家會去刷第1關最有效率）"
    print("  PASS\n")

    print("=== 測試3：經濟平衡防呆——單場收益不能一場就買滿商店 ===")
    r=pg.evaluate("""()=>{
        let total=0;
        for(const u of META_UPGRADES) for(let i=0;i<u.max;i++) total+=u.cost(i);
        const best=runCoins(true,99,10000,323,323)*(1+4*0.15);
        return {買滿總成本:total, 單場最高收益:Math.round(best), 佔比:+(best/total*100).toFixed(1)};
    }""")
    print(f"  {r}")
    assert r['佔比']<20, f"FAIL: 單場最高收益佔買滿成本的 {r['佔比']}%，太高會讓進程瞬間崩掉"
    print("  PASS\n")

    print("=== 測試4：購買 → 存檔 → 重載後仍在 ===")
    pg=page(b)
    pg.evaluate("""()=>{ COINS=5000; saveGame(); showShop();
        document.querySelectorAll('#shopList .mrow')[0].querySelector('.mbuy').click(); }""")
    pg.reload(); pg.wait_for_timeout(400)
    r=pg.evaluate("()=>({M:JSON.stringify(META),C:Math.round(COINS)})")
    print(f"  重載後: META={r['M']} COINS={r['C']}")
    assert 'hearts' in r['M'], "FAIL: 買的強化沒有存進去"
    print("  PASS\n")

    print("=== 測試5：永久強化套用到玩家、且沒買時完全不影響原本數值 ===")
    pg=page(b)
    r=pg.evaluate("""()=>{
        LV_IDX=0; META={}; start();
        const b={hearts:G.P.hearts,dmg:+G.P.dmg.toFixed(2),atkSpd:+G.P.atkSpd.toFixed(2),
                 pickup:G.P.pickup,dashCDmax:G.P.dashCDmax,wep:G.P.wep.bubble,revives:G.revives};
        META={hearts:2,dmg:5,aspd:5,wep:3,range:3,xp:4,pickup:3,dash:3,revive:2,coin:4};
        start(); update(0.001,0.001);
        const a={hearts:G.P.hearts,dmg:+G.P.dmg.toFixed(2),atkSpd:+G.P.atkSpd.toFixed(2),
                 pickup:G.P.pickup,dashCDmax:+G.P.dashCDmax.toFixed(2),wep:G.P.wep.bubble,
                 revives:G.revives,atkRange:G.P.atkRange,metaXP:+G.P.metaXP.toFixed(2)};
        return {無:b, 滿:a};
    }""")
    print(f"  無強化: {r['無']}")
    print(f"  滿強化: {r['滿']}")
    n=r['無']
    # 沒買任何強化時，必須跟 v0.9.16 之前的原始數值一模一樣（第1關基準線不能被動到）
    assert n=={'hearts':3,'dmg':1,'atkSpd':1,'pickup':110,'dashCDmax':3,'wep':1,'revives':0}, \
        "FAIL: 沒買強化時的起始數值被改動了——第1關基準線會失效"
    a=r['滿']
    assert a['hearts']==5 and a['dmg']>n['dmg'] and a['atkSpd']>n['atkSpd'] \
       and a['wep']>n['wep'] and a['revives']==2 and a['dashCDmax']<n['dashCDmax'], \
        "FAIL: 永久強化沒有正確套用"
    print("  PASS\n")

    print("=== 測試6：重生蠟燭 ===")
    pg=page(b)
    r=pg.evaluate("""()=>{
        LV_IDX=0; META={revive:1}; start();
        const out=[];
        G.P.hearts=1; G.P.iframe=0; hurtPlayer();
        out.push({階段:'第1次歸零',hearts:G.P.hearts,over:G.over,revives:G.revives});
        G.P.hearts=1; G.P.iframe=0; hurtPlayer();
        out.push({階段:'第2次歸零',hearts:G.P.hearts,over:G.over,revives:G.revives});
        return out;
    }""")
    for x in r: print(f"  {x}")
    assert r[0]['over']==False and r[0]['hearts']>0, "FAIL: 有蠟燭卻沒復活"
    assert r[1]['over']==True, "FAIL: 蠟燭用完了還沒結束遊戲"
    print("  PASS\n")

    b.close()
srv.shutdown()
print("=== 全部通過 ===")
