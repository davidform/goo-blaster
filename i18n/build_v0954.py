"""Fire candy's bounded trail and ordinary-enemy scope in all eleven locales."""
import json,sys
from pathlib import Path
ROWS={
'en':'Leave a fire trail for {0}s. Lure ordinary enemies through it!',
'zh-Hant':'{0} 秒內留下火焰路徑，引普通敵人踩上去！',
'zh-Hans':'{0} 秒内留下火焰路径，引普通敌人踩上去！',
'ja':'{0}秒間、炎の道を残す！通常の敵を誘い込もう！',
'ko':'{0}초 동안 불길을 남깁니다. 일반 적을 유인하세요!',
'de':'Hinterlasse {0}s lang eine Feuerspur. Locke normale Gegner hinein!',
'fr':'Laisse une traînée de feu pendant {0}s. Attire les ennemis ordinaires dedans !',
'es':'Deja un rastro de fuego durante {0}s. ¡Atrae a los enemigos normales!',
'it':'Lascia una scia di fuoco per {0}s. Attiraci i nemici comuni!',
'pt-BR':'Deixe um rastro de fogo por {0}s. Atraia inimigos comuns para ele!',
'ru':'Оставляй огненный след {0}с. Замани в него обычных врагов!'}
if __name__=='__main__':
 root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
 p=root/'index.html';s=p.read_bytes().decode();old=next(x for x in s.splitlines() if x.startswith('const L10N='))
 data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,value in ROWS.items():data[lang]['c_fire_go']=value
 p.write_bytes(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';').encode())
 print('PASS fire candy description x 11 locales')
