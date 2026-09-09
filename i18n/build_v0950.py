"""Keep stage-nine rule text consistent with the strength/movement tradeoff."""
import json
from pathlib import Path
ROWS={
'en':'Tougher enemies move a little slower, but their shots come faster.',
'zh-Hant':'敵人更耐打，移動稍慢，但射擊更加頻繁。',
'zh-Hans':'敌人更耐打，移动稍慢，但射击更加频繁。',
'ja':'敵は打たれ強くなり、動きは少し遅くなるが、射撃は速くなる。',
'ko':'적이 더 튼튼해지고 조금 느려지지만, 더 자주 사격해요.',
'de':'Zähere Gegner bewegen sich etwas langsamer, schießen aber häufiger.',
'fr':'Les ennemis sont plus résistants et un peu plus lents, mais tirent plus souvent.',
'es':'Los enemigos son más resistentes y algo más lentos, pero disparan más a menudo.',
'it':'I nemici sono più resistenti e un po’ più lenti, ma sparano più spesso.',
'pt-BR':'Os inimigos ficam mais resistentes e um pouco mais lentos, mas atiram com mais frequência.',
'ru':'Враги становятся выносливее и чуть медленнее, но стреляют чаще.'}
p=Path(__file__).resolve().parents[1]/'index.html'
with p.open(encoding='utf-8',newline='') as f:s=f.read()
old=next(x for x in s.splitlines() if x.startswith('const L10N='));data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
for lang,value in ROWS.items():data[lang]['lv9d']=value
with p.open('w',encoding='utf-8',newline='') as f:f.write(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';'))
