"""World-view controls in the game's eleven locales."""
import json
from pathlib import Path
KEYS='gardenWorldHint gardenArrange gardenFarm gardenZoomIn gardenZoomOut gardenHome'.split()
DATA={
'en':'Drag to explore · Tap a field or cottage|Decorations & visitors|Tend the fields|Zoom in|Zoom out|Centre village',
'zh-Hant':'拖曳探索 · 點田地或小屋互動|布置與訪客|照顧田地|放大|縮小|回到村莊中央',
'zh-Hans':'拖动探索 · 点田地或小屋互动|布置与访客|照顾田地|放大|缩小|回到村庄中央',
'ja':'ドラッグで探索 · 畑や家をタップ|飾りと訪問者|畑の手入れ|拡大|縮小|村の中心に戻る',
'ko':'드래그하여 둘러보기 · 밭이나 집을 누르세요|장식과 방문객|밭 돌보기|확대|축소|마을 중앙으로',
'de':'Ziehen zum Erkunden · Feld oder Haus antippen|Deko und Besucher|Felder pflegen|Vergrößern|Verkleinern|Dorf zentrieren',
'fr':'Faites glisser pour explorer · Touchez un champ ou la maison|Décorations et visiteurs|Cultiver les champs|Zoom avant|Zoom arrière|Centrer le village',
'es':'Arrastra para explorar · Toca un campo o la casa|Adornos y visitantes|Cuidar los cultivos|Acercar|Alejar|Centrar la aldea',
'it':'Trascina per esplorare · Tocca un campo o la casa|Decorazioni e visitatori|Cura i campi|Ingrandisci|Riduci|Centra il villaggio',
'pt-BR':'Arraste para explorar · Toque no campo ou na casa|Enfeites e visitantes|Cuidar dos campos|Ampliar|Reduzir|Centralizar a vila',
'ru':'Перетаскивайте для обзора · Нажмите на грядку или дом|Украшения и гости|Ухаживать за грядками|Приблизить|Отдалить|В центр деревни'
}
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'index.html';s=p.read_text(encoding='utf-8');old=next(x for x in s.splitlines() if x.startswith('const L10N='));d=json.loads(old[11:-1]);assert set(d)==set(DATA)
 for lang,text in DATA.items():
  row=text.split('|');assert len(row)==len(KEYS);d[lang].update(zip(KEYS,row))
 p.write_text(s.replace(old,'const L10N='+json.dumps(d,ensure_ascii=False)+';'),encoding='utf-8')
