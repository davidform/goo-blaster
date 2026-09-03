#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""關卡數量評估用的實測：100 關之間到底有多少「真的不一樣」。

不是憑感覺講「太多了」，是把每一關的實際輸入抓出來比對：
  - 玩家會遇到的敵人種類組合（波次 mix）
  - 敵人分層（tier）——決定「這隻怪有沒有變強」
  - 難度參數的逐關變化幅度
  - 全破一次要花多少時間
"""
import http.server, socketserver, threading, functools, json, statistics
from playwright.sync_api import sync_playwright
ROOT="/home/claude/goo/game"; PORT=8810
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(("127.0.0.1",PORT),
    functools.partial(http.server.SimpleHTTPRequestHandler,directory=ROOT))
threading.Thread(target=srv.serve_forever,daemon=True).start()

with sync_playwright() as pw:
    b=pw.chromium.launch()
    c=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,
                    is_mobile=True,has_touch=True,locale="en-US")
    pg=c.new_page(); pg.goto(f"http://127.0.0.1:{PORT}/index.html"); pg.wait_for_timeout(700)
    D=pg.evaluate("""()=>{
        const out=[];
        for(let i=0;i<LEVELS.length;i++){
            const L=LEVELS[i];
            const waves=buildWaves(L);
            const mixes=waves.map(w=>Object.keys(w.mix).filter(k=>w.mix[k]>0).sort().join('+'));
            out.push({
              i:i+1, dur:L.dur, hearts:L.hearts, rate:L.rate, hp:L.hp, espd:L.espd,
              bspd:L.bspd, bossHp:L.bossHp, atkSlow:L.atkSlow, maxE:L.maxE,
              nboss:L.nboss, tier:L.tier, superBoss:!!L.superBoss, chest:L.chest,
              mixes:[...new Set(mixes)].sort().join(' | '),
              // ⚠ enemyTier() 不吃參數，讀的是全域 G.lvIdx——直接呼叫會全部回 0（我第一版就踩到）。
              //   這裡照它的公式自己算：Math.min(4, floor(關index/2))
              tiers:String(Math.min(4, Math.floor(i/2)))
            });
        }
        return out;
    }""")
    b.close()
srv.shutdown()

print(f"總關卡數：{len(D)}")
print(f"全破一次的純遊玩時間：{sum(x['dur'] for x in D)/60:.0f} 分鐘"
      f"（不含失敗重玩；平均每關 {statistics.mean([x['dur'] for x in D]):.0f} 秒）")

mixes={}
for x in D: mixes.setdefault(x["mixes"],[]).append(x["i"])
print(f"\n【敵人組合】全 {len(D)} 關只有 {len(mixes)} 種不同的敵人組合：")
for m,lv in sorted(mixes.items(), key=lambda kv:-len(kv[1])):
    rng=f"{lv[0]}-{lv[-1]}" if len(lv)>3 else ",".join(map(str,lv))
    print(f"   {len(lv):>3} 關  [{rng}]  {m[:78]}")

tiers={}
for x in D: tiers.setdefault(x["tiers"],[]).append(x["i"])
print(f"\n【敵人分層 enemyTier】只有 {len(tiers)} 種：")
for t,lv in sorted(tiers.items(), key=lambda kv: kv[1][0]):
    print(f"   第{lv[0]}-{lv[-1]}關（{len(lv)} 關） → tier {t}")

print("\n【難度參數的逐關變化幅度】")
KEYS=['rate','hp','espd','bspd','bossHp','atkSlow','maxE','dur']
for k in KEYS:
    v=[x[k] for x in D]
    d=[abs(v[i+1]-v[i])/max(1e-9,abs(v[i]))*100 for i in range(len(v)-1)]
    half=len(v)//2
    late=[abs(v[i+1]-v[i])/max(1e-9,abs(v[i]))*100 for i in range(half,len(v)-1)]
    print(f"   {k:<8} 第1→100關 {v[0]:>8.3f} → {v[-1]:>8.3f}"
          f"   逐關平均變化 {statistics.mean(d):5.2f}%   後半段 {statistics.mean(late):5.2f}%")

print("\n【第 51 關之後，相鄰兩關的「總體差異」】")
def vec(x): return [x['rate'],x['hp'],x['espd'],x['bspd'],x['bossHp'],x['atkSlow'],x['maxE']/100,x['dur']/100]
diffs=[]
for i in range(len(D)-1):
    a,bv=vec(D[i]),vec(D[i+1])
    diffs.append(sum(abs(p-q)/max(1e-9,abs(p)) for p,q in zip(a,bv))/len(a)*100)
H=len(diffs)//2
print(f"   前半段（第 2-{H+1} 關）：相鄰差異平均 {statistics.mean(diffs[:H]):.2f}%")
print(f"   後半段（第 {H+2}-{len(D)} 關）：相鄰差異平均 {statistics.mean(diffs[H:]):.2f}%")
under=[i+2 for i,d in enumerate(diffs) if d<1.0]
print(f"   相鄰差異 < 1% 的關卡數：{len(under)} 關（＝玩家幾乎感覺不到跟上一關的差別）")

print("\n【章節結構】")
CH=len(D)//10
for ch in range(10):
    seg=D[ch*CH:(ch+1)*CH]
    print(f"   第{ch+1:>2}章（第{seg[0]['i']:>3}-{seg[-1]['i']:>3}關）"
          f" 時長 {seg[0]['dur']}-{seg[-1]['dur']}秒  maxE {seg[0]['maxE']}-{seg[-1]['maxE']}"
          f"  Boss數 {seg[0]['nboss']}-{seg[-1]['nboss']}  tier {seg[0]['tiers']}")
