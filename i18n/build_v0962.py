"""Dash distance training and bounded in-run cooldown choices, eleven locales."""
import json,sys
from pathlib import Path
ROWS={
'en':['Dash distance +{0}%. Cooldown is reduced by upgrade cards only.','Dash cooldown -0.4s','Another -0.4s and a longer dash'],
'zh-Hant':['衝刺距離 +{0}%；冷卻只能透過局內升級卡縮短。','衝刺冷卻縮短 0.4 秒','再縮短 0.4 秒，並增加衝刺距離'],
'zh-Hans':['冲刺距离 +{0}%；冷却只能通过局内升级卡缩短。','冲刺冷却缩短 0.4 秒','再缩短 0.4 秒，并增加冲刺距离'],
'ja':['ダッシュ距離+{0}%。クールダウン短縮はプレイ中の強化カードのみ。','ダッシュのクールダウンを0.4秒短縮','さらに0.4秒短縮し、ダッシュ距離も延長'],
'ko':['돌진 거리 +{0}%. 재사용 대기시간은 게임 중 강화 카드로만 줄어듭니다.','돌진 재사용 대기시간 0.4초 감소','0.4초 추가 감소 및 돌진 거리 증가'],
'de':['Ausweichdistanz +{0}%. Nur Upgrade-Karten im Lauf verkürzen die Abklingzeit.','Ausweich-Abklingzeit um 0,4s kürzer','Weitere 0,4s kürzer und längere Ausweichdistanz'],
'fr':['Distance d’esquive +{0} %. Seules les cartes en partie réduisent la recharge.','Recharge de l’esquive réduite de 0,4 s','Encore 0,4 s de moins et une esquive plus longue'],
'es':['Distancia de impulso +{0} %. Solo las cartas de la partida reducen la recarga.','Recarga del impulso reducida en 0,4 s','Otros 0,4 s menos y mayor distancia de impulso'],
'it':['Distanza dello scatto +{0}%. Solo le carte della partita riducono la ricarica.','Ricarica dello scatto ridotta di 0,4 s','Altri 0,4 s in meno e scatto più lungo'],
'pt-BR':['Distância do impulso +{0}%. Só as cartas da partida reduzem a recarga.','Recarga do impulso reduzida em 0,4 s','Mais 0,4 s de redução e impulso mais longo'],
'ru':['Дальность рывка +{0}%. Перезарядку сокращают только карты в забеге.','Перезарядка рывка короче на 0,4 с','Ещё на 0,4 с короче, дальность рывка увеличена']}
if __name__=='__main__':
 p=(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])/'index.html'
 s=p.read_bytes().decode();old=next(x for x in s.splitlines() if x.startswith('const L10N='));data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,values in ROWS.items():
  for key,value in zip(['m_dash_d','u_cd_d','u_cd_d2'],values):data[lang][key]=value
 p.write_bytes(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';').encode())
