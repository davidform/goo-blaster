"""Short home destination label for the persistent five-item navigation."""
import json
from pathlib import Path
DATA={'en':'Home','zh-Hant':'主畫面','zh-Hans':'主画面','ja':'ホーム','ko':'홈','de':'Start','fr':'Accueil','es':'Inicio','it':'Home','pt-BR':'Início','ru':'Главная'}
if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'index.html';s=p.read_text(encoding='utf-8')
    old=next(x for x in s.splitlines() if x.startswith('const L10N='));d=json.loads(old[11:-1]);assert set(d)==set(DATA)
    for lang,text in DATA.items():d[lang]['navHome']=text
    p.write_text(s.replace(old,'const L10N='+json.dumps(d,ensure_ascii=False)+';'),encoding='utf-8')
