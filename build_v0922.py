# -*- coding: utf-8 -*-
"""v0.9.22：Boss 名稱重做（11 語言）＋ Boss 外觀特徵系統（尖刺／盔甲／角／冠／翼／光環）。

⚠ 一律遵守既有的三條血淚教訓：
   1) 不做 JSON 字串手術 → 整塊 json.dumps() 重寫
   2) 不用 repr().replace() → 一律 json.dumps()
   3) 寫檔前先 assert 每一處都真的換到了
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from keys_v0922 import NEW

P='/home/claude/work/goo-blaster/index.html'
s=open(P,encoding='utf-8').read(); orig=s
def rep(o,n,tag,cnt=1):
    global s
    assert s.count(o)==cnt, f"[{tag}] 預期 {cnt} 處，實際 {s.count(o)}: {o[:70]!r}"
    s=s.replace(o,n,cnt)

# ── 1. L10N：覆寫 13 個 Boss 名稱、新增 tArmorBreak ─────────────────
lines=s.split('\n')
li=[i for i,l in enumerate(lines) if l.startswith('const L10N=')]
assert len(li)==1
L=json.loads(lines[li[0]][len('const L10N='):].rstrip(';'))
assert set(L)==set(NEW)
for c in L:
    for k,v in NEW[c].items():
        if k=='tArmorBreak': assert k not in L[c], f'{c}.{k} 已存在'
        else: assert k in L[c], f'{c}.{k} 應該已存在（是覆寫不是新增）'
        L[c][k]=v
lines[li[0]]='const L10N='+json.dumps(L,ensure_ascii=False)+';'
s='\n'.join(lines)

# ── 2. 銀河圖上的章節 Boss 圖示：換成跟新名字對得上、且逐章升級的一組 ──
ICONS=['🦷','👹','💀','🧊','🔥','🗿','👻','😈','☄️','🐉']
OLD_ICONS=['👹','👺','💀','☠️','👻','🧟','😈','👿','🐲','🔥']
for old,new in zip(OLD_ICONS,ICONS):
    o="icon:'"+old+"'"
    assert s.count(o)==1, f"icon {old} 出現 {s.count(o)} 次"
for i,(old,new) in enumerate(zip(OLD_ICONS,ICONS)):
    s=s.replace("icon:'"+old+"'","icon:'@@%d@@'"%i,1)
for i,new in enumerate(ICONS):
    s=s.replace("icon:'@@%d@@'"%i,"icon:'"+new+"'",1)

# ── 3. Boss 外觀特徵表 ────────────────────────────────────────────
rep("function buildBosses(L){",
"""// ── v0.9.22：Boss 外觀特徵（可混搭）────────────────────────────────────
// 使用者回饋「關卡的魔王外型設計太陽春了」。原本 Boss 只是一顆比較大的果凍球
// 加一圈光暈——第 10 關的 Boss 跟第 100 關的長得一模一樣，只有數字不同。
// 玩家對「越打越深、敵人越來越強」完全沒有視覺回饋，這是白白丟掉的成就感。
//
// 六種可混搭的裝飾：
//   spike 尖刺 ／ armor 盔甲 ／ horn 巨角 ／ crown 尖冠 ／ wing 翼 ／ aura 光環
// 盔甲在血量掉到 50% 時碎裂，露出底下更長更多的尖刺——這是一個免費的
// 「階段轉換」：玩家打到一半會得到一個明確的「我打壞它了」的回饋，
// 而 Boss 反而看起來更兇了（張力不掉）。
//
// ⚠ 全部純視覺，不改任何數值。難度平衡完全不動（由 py_ab_2122.py 逐項證明）。
// 之所以刻意不讓盔甲減傷：那會改變難度曲線，必須重跑整套平衡測試；
// 而「階段轉換的爽感」光靠視覺 + 震動 + 音效就拿得到，風險 0。
const BOSS_SKIN_CH=[
  ['spike'],                                             // 第 1 章（第10關）
  ['armor'],                                             // 第 2 章
  ['spike','horn'],                                      // 第 3 章
  ['armor','horn'],                                      // 第 4 章
  ['spike','armor','crown'],                             // 第 5 章
  ['spike','horn','aura'],                               // 第 6 章
  ['armor','crown','wing'],                              // 第 7 章
  ['spike','armor','horn','wing'],                       // 第 8 章
  ['spike','armor','crown','wing','aura'],               // 第 9 章
  ['spike','armor','horn','crown','wing','aura']         // 第 10 章（第100關）
];
// 一般 Boss（每關都會出現的那幾隻）也要跟著章節長裝備，
// 但永遠比同章的章節 Boss 樸素一階，維持「章節 Boss 才是頭目」的階層感。
const MID_SKIN_CH=[
  [],                                                    // 第 1 章：完全樸素（新手期不要視覺噪音）
  ['spike'],
  ['spike'],
  ['armor'],
  ['spike','armor'],
  ['spike','armor'],
  ['spike','armor','horn'],
  ['armor','horn','crown'],
  ['spike','armor','horn','crown'],
  ['spike','armor','horn','crown','wing']
];
const skinHas=(e,k)=>!!e.skin && e.skin.indexOf(k)>=0;

function buildBosses(L){""","skin_tables")

# ── 4. buildBosses：把 skin 掛上去 ────────────────────────────────
rep("""      atkT: b.atkT*L.atkSlow,
      kind: (!L.superBoss && i===at.length-1) ? 'final' : ('b'+(i+1))
    };""",
"""      atkT: b.atkT*L.atkSlow,
      kind: (!L.superBoss && i===at.length-1) ? 'final' : ('b'+(i+1)),
      skin: MID_SKIN_CH[Math.min(9, L.ch||0)]            // v0.9.22 外觀，純視覺
    };""","mid_skin")
rep("""      atkT: b.atkT*L.atkSlow,
      kind:'final', superBoss:true
    });""",
"""      atkT: b.atkT*L.atkSlow,
      kind:'final', superBoss:true,
      skin: BOSS_SKIN_CH[Math.min(9, L.bossChapter||0)]  // v0.9.22 外觀，純視覺
    });""","ch_skin")

# ── 5. spawnBoss：把 skin / armor 帶進實體 ────────────────────────
rep("""    superBoss:!!cfg.superBoss,""",
"""    superBoss:!!cfg.superBoss,
    // v0.9.22 外觀特徵（純視覺）。armor 為 true 時，血量掉到 50% 會碎裂露出尖刺。
    skin:cfg.skin||[], armor:!!(cfg.skin&&cfg.skin.indexOf('armor')>=0), armorBroken:false,""","spawn_skin")

# ── 6. hurtEnemy：盔甲碎裂 ────────────────────────────────────────
rep("""  e.hp-=d; e.flash=.09;""",
"""  e.hp-=d; e.flash=.09;
  // v0.9.22：盔甲在血量掉到 50% 時碎裂，露出底下的尖刺。
  // 這是純視覺 + 音效 + 震動的階段轉換，不動任何數值。
  if(e.armor && !e.armorBroken && e.hp<=e.maxhp*0.5){
    e.armorBroken=true;
    burst(e.x,e.y,26,(e.hue+200)%360,1.9);               // 金屬碎片
    burst(e.x,e.y,14,e.hue,1.2);
    shake(9); hitstop(.07);
    toast(T('tArmorBreak'),'#dfe9ff');
    SFX.evo();
  }""","armor_break")

# ── 7. 繪製 ───────────────────────────────────────────────────────
rep("""// 不使用 save()/restore()：那兩個呼叫在 80+ 敵人時是實測最大的單一開銷
function drawBlob(e,detail){""",
"""// ── v0.9.22：Boss 裝飾的繪製 ─────────────────────────────────────────
// 分成「身體之前」與「身體之後」兩段，讓尖刺/翼的內側被身體蓋住、
// 盔甲與角冠壓在身體之上，看起來才有前後層次。
// 場上 Boss 最多 3 隻，所以這裡可以畫得比一般小怪細緻很多。
function drawBossBack(e,R){
  if(!e.skin||!e.skin.length) return;
  const t=G.t;
  if(skinHas(e,'aura')){
    for(let i=0;i<3;i++){
      const rr=R*(1.46+i*0.15)+Math.sin(t*2.2+i*1.3)*3;
      ctx.strokeStyle='hsla('+((e.hue+i*26)%360)+',95%,66%,'+(0.26-i*0.07).toFixed(2)+')';
      ctx.lineWidth=3.4-i*0.8;
      ctx.beginPath(); ctx.arc(e.x,e.y,rr,0,6.283); ctx.stroke();
    }
    ctx.fillStyle='hsla('+e.hue+',95%,74%,.5)';
    for(let i=0;i<6;i++){
      const a=t*1.15+i*1.0472, rr=R*1.66;
      ctx.beginPath(); ctx.arc(e.x+Math.cos(a)*rr,e.y+Math.sin(a)*rr,3.2,0,6.283); ctx.fill();
    }
  }
  if(skinHas(e,'wing')){
    const flap=Math.sin(t*2.6)*0.16;
    ctx.fillStyle='hsla('+((e.hue+300)%360)+',65%,30%,.85)';
    ctx.strokeStyle='hsla('+e.hue+',90%,72%,.75)'; ctx.lineWidth=2;
    for(let si=0;si<2;si++){
      const sg=si?1:-1;
      ctx.beginPath();
      ctx.moveTo(e.x+sg*R*0.50, e.y-R*0.15);
      ctx.quadraticCurveTo(e.x+sg*R*1.75, e.y-R*(1.05+flap), e.x+sg*R*1.95, e.y-R*0.02);
      ctx.quadraticCurveTo(e.x+sg*R*1.50, e.y+R*(0.28+flap), e.x+sg*R*1.06, e.y+R*0.50);
      ctx.quadraticCurveTo(e.x+sg*R*1.00, e.y+R*0.05,        e.x+sg*R*0.50, e.y-R*0.15);
      ctx.closePath(); ctx.fill(); ctx.stroke();
    }
  }
  // 尖刺：有盔甲的 Boss 平常把刺藏在甲底下，甲碎了才露出來，而且更多更長
  const spiked = skinHas(e,'spike') || (skinHas(e,'armor') && e.armorBroken);
  if(spiked){
    const broke=e.armorBroken;
    const n=broke?14:10, len=(broke?0.55:0.40)*R;
    ctx.fillStyle='hsla('+e.hue+',55%,'+(broke?88:78)+'%,.95)';
    ctx.beginPath();
    for(let i=0;i<n;i++){
      const a=t*0.35+i*(6.283/n), bw=0.10;
      ctx.moveTo(e.x+Math.cos(a-bw)*R*0.94, e.y+Math.sin(a-bw)*R*0.94);
      ctx.lineTo(e.x+Math.cos(a)*(R+len),   e.y+Math.sin(a)*(R+len));
      ctx.lineTo(e.x+Math.cos(a+bw)*R*0.94, e.y+Math.sin(a+bw)*R*0.94);
    }
    ctx.fill();
  }
}
function drawBossFront(e,R){
  if(!e.skin||!e.skin.length) return;
  const t=G.t;
  if(skinHas(e,'armor') && !e.armorBroken){
    const hueA=(e.hue+200)%360;
    ctx.strokeStyle='hsla('+hueA+',22%,84%,.95)';
    ctx.lineWidth=Math.max(3,R*0.13);
    for(let i=0;i<4;i++){
      const a0=t*0.22+i*1.5708+0.18;
      ctx.beginPath(); ctx.arc(e.x,e.y,R*0.84,a0,a0+1.20); ctx.stroke();
    }
    ctx.strokeStyle='hsla('+hueA+',28%,52%,.9)'; ctx.lineWidth=Math.max(1.4,R*0.05);
    for(let i=0;i<4;i++){
      const a0=t*0.22+i*1.5708+0.18;
      ctx.beginPath(); ctx.arc(e.x,e.y,R*0.66,a0,a0+1.20); ctx.stroke();
    }
    ctx.fillStyle='hsla('+hueA+',18%,93%,.9)';
    for(let i=0;i<4;i++){
      const a=t*0.22+i*1.5708+0.78;
      ctx.beginPath();
      ctx.arc(e.x+Math.cos(a)*R*0.84,e.y+Math.sin(a)*R*0.84,Math.max(1.6,R*0.055),0,6.283);
      ctx.fill();
    }
  }
  if(skinHas(e,'horn')){
    ctx.fillStyle='hsla('+((e.hue+40)%360)+',32%,89%,.96)';
    for(let si=0;si<2;si++){
      const sg=si?1:-1;
      ctx.beginPath();
      ctx.moveTo(e.x+sg*R*0.52, e.y-R*0.66);
      ctx.quadraticCurveTo(e.x+sg*R*1.16, e.y-R*1.30, e.x+sg*R*0.86, e.y-R*1.70);
      ctx.quadraticCurveTo(e.x+sg*R*0.94, e.y-R*1.06, e.x+sg*R*0.30, e.y-R*0.80);
      ctx.closePath(); ctx.fill();
    }
  }
  if(skinHas(e,'crown')){
    const cy=e.y-R*(skinHas(e,'horn')?1.20:0.94), cw=R*0.86;
    ctx.fillStyle='#ffd24a';
    ctx.beginPath();
    ctx.moveTo(e.x-cw, cy);
    ctx.lineTo(e.x-cw*0.62, cy-R*0.42);
    ctx.lineTo(e.x-cw*0.24, cy-R*0.08);
    ctx.lineTo(e.x,         cy-R*0.58);
    ctx.lineTo(e.x+cw*0.24, cy-R*0.08);
    ctx.lineTo(e.x+cw*0.62, cy-R*0.42);
    ctx.lineTo(e.x+cw,      cy);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle='#a8791a';
    ctx.fillRect(e.x-cw, cy, cw*2, Math.max(2,R*0.10));
  }
}
// 不使用 save()/restore()：那兩個呼叫在 80+ 敵人時是實測最大的單一開銷
function drawBlob(e,detail){""","draw_fns")

# 掛進 drawBlob
rep("""  if(e.boss){ ctx.shadowColor='hsl('+e.hue+',90%,55%)'; ctx.shadowBlur=26; }""",
"""  if(e.boss) drawBossBack(e,R);                 // v0.9.22：翼／光環／尖刺畫在身體之後
  if(e.boss){ ctx.shadowColor='hsl('+e.hue+',90%,55%)'; ctx.shadowBlur=26; }""","hook_back")
rep("""    ctx.beginPath(); ctx.arc(e.x+R*.3,e.y-R*.05,es,0,6.283); ctx.fill();
  }""",
"""    ctx.beginPath(); ctx.arc(e.x+R*.3,e.y-R*.05,es,0,6.283); ctx.fill();
  }
  if(e.boss) drawBossFront(e,R);                // v0.9.22：盔甲／角／冠壓在身體之上""","hook_front")

# ── 8. 版號 ───────────────────────────────────────────────────────
rep("const BUILD='v0.9.21'","const BUILD='v0.9.22'","build")

# ── 9. 寫檔前驗證 ─────────────────────────────────────────────────
assert s!=orig
CJK=re.compile(r'[぀-ヿ一-鿿가-힯]')
newL=json.loads([l for l in s.split('\n') if l.startswith('const L10N=')][0][len('const L10N='):].rstrip(';'))
assert len(newL['en'])==207, len(newL['en'])
for c in newL:
    assert set(newL[c])==set(newL['en']), f'{c} key 不齊'
for c in ['en','de','fr','es','it','pt-BR','ru']:
    for k,v in newL[c].items():
        assert not CJK.search(str(v)), f'{c}.{k} 混進 CJK: {v!r}'
assert newL['en']['sb9']=='Omega, the Ender'
assert newL['fr']['sb7']=="Archidémon de l'Abîme"
assert newL['es']['tArmorBreak']=='¡ARMADURA DESTROZADA!'
assert newL['ru']['sb9']=='Омега, Погибель Миров'
# 資料表裡的中文名稱本來就是「來源預設值」，applyLanguage() 會就地覆寫。
# 但既然現在名字全部改掉了，留著舊的中文只會誤導維護——清成空字串，
# 跟 WEAPONS/EVOS 的做法一致（真正的文字一律來自 L10N）。
OLDN=['加班文件怪','未讀訊息怪','奪魂鬧鐘怪','業績KPI巨獸','週一晨會惡魔','無限加班幽靈',
      '已讀不回怪','年終考核修羅','信箱爆炸魔王','責任制黑洞','交接怨靈','沉默審判者','終極KPI審判神']
for zh in OLDN:
    o="name:'"+zh+"'"
    assert s.count(o)==1, f'{zh}: {s.count(o)}'
    s=s.replace(o,"name:''",1)
# 註解裡提到舊名字的地方也一併更新，免得未來讀到對不上的名詞
rep("// index 0 完全沿用舊版業績KPI巨獸的數值不變（第10關已經被笨bot測過很多次，",
    "// index 0 完全沿用第 1 章 Boss（現名 Molar Crusher）的數值不變（第10關已經被笨bot測過很多次，","cmt")
for zh in OLDN:
    assert zh not in s, zh
open(P,'w',encoding='utf-8').write(s)
print('✅ v0.9.22 已寫入')
print('   en key:', len(newL['en']))
