"""Visible story objective and explicit existing dash upgrade, eleven locales."""
import json,sys
from pathlib import Path
ROWS={
'en':['Stage goal','Dash Training','Cooldown {1}s (−{0}s). Invincibility stays {2}s.'],
'zh-Hant':['本關目標','衝刺訓練','冷卻 {1} 秒（−{0} 秒）；無敵仍為 {2} 秒。'],
'zh-Hans':['本关目标','冲刺训练','冷却 {1} 秒（−{0} 秒）；无敌仍为 {2} 秒。'],
'ja':['今回の目標','ダッシュ訓練','クールダウン{1}秒（−{0}秒）。無敵時間は{2}秒のまま。'],
'ko':['이번 목표','돌진 훈련','재사용 대기 {1}초(−{0}초). 무적 시간은 {2}초로 유지됩니다.'],
'de':['Etappenziel','Ausweichtraining','Abklingzeit {1}s (−{0}s). Unverwundbarkeit bleibt {2}s.'],
'fr':['Objectif du niveau','Entraînement à l’esquive','Recharge : {1}s (−{0}s). Invincibilité inchangée : {2}s.'],
'es':['Objetivo del nivel','Entrenamiento de impulso','Recarga: {1}s (−{0}s). La invencibilidad sigue en {2}s.'],
'it':['Obiettivo del livello','Allenamento dello scatto','Ricarica: {1}s (−{0}s). Invincibilità invariata: {2}s.'],
'pt-BR':['Objetivo da fase','Treino de impulso','Recarga: {1}s (−{0}s). A invencibilidade continua em {2}s.'],
'ru':['Цель этапа','Тренировка рывка','Перезарядка {1}с (−{0}с). Неуязвимость остаётся {2}с.']}
if __name__=='__main__':
 p=(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])/'index.html'
 s=p.read_bytes().decode();old=next(x for x in s.splitlines() if x.startswith('const L10N='));data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,values in ROWS.items():
  for k,v in zip(['storyGoalTitle','m_dash_n','m_dash_d'],values):data[lang][k]=v
 p.write_bytes(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';').encode())
 print('PASS story goal and dash clarity x11')
