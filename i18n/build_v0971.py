"""v71 contextual feedback for all three garden activities."""
import json
from pathlib import Path
KEYS='festivalServed festivalLit festivalSwimHint festivalLinkHint'.split()
DATA={
'en':'Served {0}/{1}|Stars lit {0}/9|Follow the arrows to swim. Collect three pearls, then reach the flag.|Outlined stars changed together on your last tap.',
'zh-Hant':'已送餐 {0}/{1}|已亮起 {0}/9 顆星|沿箭頭游動，收齊三顆珍珠後前往旗幟。|框線標出上次點按一起切換的星星。',
'zh-Hans':'已送餐 {0}/{1}|已亮起 {0}/9 颗星|沿箭头游动，收齐三颗珍珠后前往旗帜。|边框标出上次点击一起切换的星星。',
'ja':'配膳済み {0}/{1}|点灯 {0}/9|矢印に沿って泳ぎ、真珠3個を集めて旗へ。|枠は直前のタップで一緒に切り替わった星です。',
'ko':'서빙 {0}/{1}|켜진 별 {0}/9|화살표를 따라 헤엄쳐 진주 세 개를 모은 뒤 깃발로 가세요.|테두리는 방금 함께 바뀐 별을 나타내요.',
'de':'Serviert {0}/{1}|Leuchtende Sterne {0}/9|Folge den Pfeilen. Sammle drei Perlen und erreiche die Flagge.|Umrandete Sterne wurden beim letzten Tippen gemeinsam umgeschaltet.',
'fr':'Plats servis {0}/{1}|Étoiles allumées {0}/9|Suivez les flèches. Ramassez trois perles, puis rejoignez le drapeau.|Les étoiles encadrées ont changé ensemble au dernier toucher.',
'es':'Platos servidos {0}/{1}|Estrellas encendidas {0}/9|Sigue las flechas. Reúne tres perlas y llega a la bandera.|Las estrellas con borde cambiaron juntas en el último toque.',
'it':'Piatti serviti {0}/{1}|Stelle accese {0}/9|Segui le frecce. Raccogli tre perle e raggiungi la bandiera.|Le stelle con il bordo sono cambiate insieme all’ultimo tocco.',
'pt-BR':'Pratos servidos {0}/{1}|Estrelas acesas {0}/9|Siga as setas. Pegue três pérolas e chegue à bandeira.|As estrelas contornadas mudaram juntas no último toque.',
'ru':'Подано {0}/{1}|Зажжено звёзд {0}/9|Плывите по стрелкам. Соберите три жемчужины и доберитесь до флага.|Рамкой отмечены звёзды, изменившиеся вместе при последнем нажатии.'}
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'index.html';s=p.read_text(encoding='utf-8');old=next(x for x in s.splitlines() if x.startswith('const L10N='));d=json.loads(old[11:-1]);assert set(d)==set(DATA)
 for lang,row in DATA.items():
  values=row.split('|');assert len(values)==len(KEYS);d[lang].update(zip(KEYS,values))
 p.write_text(s.replace(old,'const L10N='+json.dumps(d,ensure_ascii=False)+';'),encoding='utf-8')
