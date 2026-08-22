# -*- coding: utf-8 -*-
"""v0.9.25：升級卡「第幾張／共幾張」的提示（11 語言）。

真人回報：「有時候剛升級選完卡，就馬上又升級可以再度選卡」。
實測不是 bug——一次吸到一團晶核會同時升好幾級（給 120 經驗 = 升 4 級 = 欠 4 張卡），
`pendingCards` 的鏈路完全正確、最後也正常解除暫停。
問題純粹是**畫面沒說**：連續四次「LV.5 UP! 選一張」，玩家只會覺得系統壞了。

修法：欠超過一張時，標題加上「(第幾張/共幾張)」。
文字直接沿用各語言既有的 cardTitle 再接括號，CJK 用全形括號、法文括號前留空格。
"""
import json, os, sys
P='/home/claude/work/goo-blaster/index.html'
s=open(P,encoding='utf-8').read(); orig=s
def rep(o,n,tag,cnt=1):
    global s
    assert s.count(o)==cnt, f"[{tag}] 預期 {cnt}，實際 {s.count(o)}"
    s=s.replace(o,n,cnt)

lines=s.split('\n')
li=[i for i,l in enumerate(lines) if l.startswith('const L10N=')]
assert len(li)==1
L=json.loads(lines[li[0]][len('const L10N='):].rstrip(';'))

# 各語言的括號樣式：CJK 用全形、法文括號前要空格
PAREN={'zh-Hant':('（','）'),'zh-Hans':('（','）'),'ja':('（','）'),'ko':(' (',')'),
       'fr':(' (',')'),'en':(' (',')'),'de':(' (',')'),'es':(' (',')'),
       'it':(' (',')'),'pt-BR':(' (',')'),'ru':(' (',')')}
for c in L:
    assert 'cardTitleN' not in L[c], c
    o,cl=PAREN[c]
    L[c]['cardTitleN']=L[c]['cardTitle']+o+'{1}/{2}'+cl
lines[li[0]]='const L10N='+json.dumps(L,ensure_ascii=False)+';'
s='\n'.join(lines)

# showCards：算出「第幾張／共幾張」
rep("""  cardsEl.innerHTML='<div class="lvtitle">'+T('cardTitle',G.P.lv)+'</div>';""",
"""  // v0.9.25：一次升好幾級時會連續跳好幾張卡。真人回報這看起來像 bug
  // （「剛選完馬上又能選」），實際上是 pendingCards 正常運作——問題是畫面沒說。
  // 欠超過一張時，標題補上「第幾張／共幾張」，玩家就知道這是預期行為。
  if(!G.cardTotal || G.cardTotal < (G.pendingCards|0)) G.cardTotal=Math.max(1,G.pendingCards|0);
  const cTot=G.cardTotal|0, cIdx=cTot-(G.pendingCards|0)+1;
  const cTitle = cTot>1 ? T('cardTitleN',G.P.lv,cIdx,cTot) : T('cardTitle',G.P.lv);
  cardsEl.innerHTML='<div class="lvtitle">'+cTitle+'</div>';""","title")

# 卡片全部選完 / 卡池空 → 歸零
rep("""  if(G.pendingCards>0) G.pendingCards--;
  if(G.pendingCards>0) showCards();               // 還欠卡：直接接著跳下一組，不恢復遊戲
  else { cardsEl.classList.add('hide'); G.paused=false; }""",
"""  if(G.pendingCards>0) G.pendingCards--;
  if(G.pendingCards>0) showCards();               // 還欠卡：直接接著跳下一組，不恢復遊戲
  else { G.cardTotal=0; cardsEl.classList.add('hide'); G.paused=false; }""","apply")
rep("""    const owed=Math.max(1,G.pendingCards|0);
    G.pendingCards=0;""",
"""    const owed=Math.max(1,G.pendingCards|0);
    G.pendingCards=0; G.cardTotal=0;""","empty")

rep("const BUILD='v0.9.24'","const BUILD='v0.9.25'","build")

newL=json.loads([l for l in s.split('\n') if l.startswith('const L10N=')][0][len('const L10N='):].rstrip(';'))
assert len(newL['en'])==208, len(newL['en'])
for c in newL:
    assert set(newL[c])==set(newL['en']), c
    assert '{1}/{2}' in newL[c]['cardTitleN'], c
assert newL['en']['cardTitleN']=='LV.{0} UP! Pick one (1/2)'.replace('1/2','{1}/{2}')
assert newL['zh-Hant']['cardTitleN']=='LV.{0} 升級！選一張（{1}/{2}）'
open(P,'w',encoding='utf-8').write(s)
print('✅ v0.9.25 已寫入，en key 數：',len(newL['en']))
