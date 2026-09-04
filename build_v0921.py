# -*- coding: utf-8 -*-
"""v0.9.21：把 7 個硬寫中文的顯示字串接上 T()，並把新 key 併進 L10N 表。

⚠ 過去踩過的坑（docs-04-append 第 6 條）：
   1) 不要用字串手術改 JSON —— 一律整塊 json.dumps() 重寫
   2) 不要用 repr().replace()  —— 法文 d'attaque、西文 ¡FRENESÍ! 會被毀掉
   3) 寫檔前一定要先 assert，確認每一處都真的換到了
"""
import json, re, sys, io, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keys_v0921 import NEW

P='/home/claude/work/goo-blaster/index.html'
s=open(P, encoding='utf-8').read()
orig=s

# ── 1. 併入 L10N（整塊重寫，不做字串手術）────────────────────────────
lines=s.split('\n')
li=[i for i,l in enumerate(lines) if l.startswith('const L10N=')]
assert len(li)==1, f"找不到唯一的 L10N 行，找到 {len(li)} 個"
i=li[0]
L=json.loads(lines[i][len('const L10N='):].rstrip(';'))
assert set(L.keys())==set(NEW.keys()), f"語言集合不一致: {set(L)^set(NEW)}"
before_counts={c:len(L[c]) for c in L}
for c in L:
    for k,v in NEW[c].items():
        assert k not in L[c], f"{c} 已經有 key {k}"
        L[c][k]=v
for c in L:
    assert len(L[c])==before_counts[c]+7, c
lines[i]='const L10N='+json.dumps(L, ensure_ascii=False)+';'
s='\n'.join(lines)

# ── 2. 把 7 處硬寫中文換成 T() ──────────────────────────────────────
def rep(old,new,tag):
    global s
    assert s.count(old)==1, f"[{tag}] 預期剛好 1 處，實際 {s.count(old)} 處: {old[:70]!r}"
    s=s.replace(old,new,1)

rep("toast('遠處出現寶箱！快去拿','#ffd84f')",
    "toast(T('tChest'),'#ffd84f')", "chest")
rep("toast('☢️ 出現核彈補給！快去撿','#ff9a4f')",
    "toast(T('tNukeDrop'),'#ff9a4f')", "nukeDrop")
rep("toast('取得核彈！左下角圖示可以引爆','#ff9a4f')",
    "toast(T('tNukeGet'),'#ff9a4f')", "nukeGet")
rep("ctx.fillText('護盾 ×'+P.shieldN, pad, hy+56)",
    "ctx.fillText(T('hudShield',P.shieldN), pad, hy+56)", "shield")
rep("ctx.fillText('暴走中！', pad, hy+(P.shieldN>0?74:56))",
    "ctx.fillText(T('hudFrenzy'), pad, hy+(P.shieldN>0?74:56))", "frenzy")
rep("x.fillText('存活 '+mm+':'+String(ss).padStart(2,'0')+'   ·   LV.'+G.P.lv+'   ·   擊殺 '+G.kills, w/2, py+ph+100)",
    "x.fillText(T('shotStats', mm+':'+String(ss).padStart(2,'0'), G.P.lv, G.kills), w/2, py+ph+100)", "shotStats")
rep("x.fillText('果凍覆蓋率 '+gooPct()+'%', w/2, py+ph+132)",
    "x.fillText(T('shotGoo',gooPct()), w/2, py+ph+132)", "shotGoo")

# ── 3. 移除 ETYPE 的 name 欄位（死資料：全檔沒有任何地方讀它）────────
for zh in ["name:'軟泥',","name:'兔子',","name:'無人機',","name:'自爆',"]:
    assert s.count(zh)==1, f"ETYPE name 預期 1 處: {zh}"
    s=s.replace(zh,"",1)

# ── 4. 版號 ────────────────────────────────────────────────────────
rep("const BUILD='v0.9.20'","const BUILD='v0.9.21'","build")

# ── 5. 寫檔前的最終驗證 ────────────────────────────────────────────
assert s!=orig
CJK=re.compile(r'[぀-ヿ一-鿿가-힯]')
newL=json.loads([l for l in s.split('\n') if l.startswith('const L10N=')][0][len('const L10N='):].rstrip(';'))
assert len(newL['en'])==206, len(newL['en'])
for c in newL:
    assert set(newL[c].keys())==set(newL['en'].keys()), f"{c} key 不齊"
# 非 CJK 語言不可以有中日韓字元（防止翻譯串行/編碼毀損）
for c in ['en','de','fr','es','it','pt-BR','ru']:
    for k,v in newL[c].items():
        assert not CJK.search(str(v)), f"{c}.{k} 混進 CJK: {v!r}"
# 抽驗容易被 repr/escape 毀掉的字串
assert newL['fr']['tChest'].startswith("Un coffre"), newL['fr']['tChest']
assert newL['es']['hudFrenzy']=="¡FRENESÍ!", newL['es']['hudFrenzy']
assert newL['ru']['hudShield']=="Щит ×{0}"
open(P,'w',encoding='utf-8').write(s)
print("✅ 已寫入 index.html")
print("   en key 數:", len(newL['en']), "（原 199 + 7）")
print("   語言數:", len(newL))
