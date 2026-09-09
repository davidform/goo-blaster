"""Explain stacked upgrade rewards without changing XP or rewards."""
import json
from pathlib import Path
ROWS={
'en':'XP and Boss rewards can stack. Choices remaining: {0}.',
'zh-Hant':'經驗值與 Boss 獎勵可累積選卡次數，還可選 {0} 張。',
'zh-Hans':'经验值与 Boss 奖励可累积选卡次数，还可选 {0} 张。',
'ja':'経験値とボス報酬で選択回数がたまります。あと{0}回選べます。',
'ko':'경험치와 보스 보상으로 선택 횟수가 쌓입니다. 남은 선택: {0}회.',
'de':'EP und Bossbelohnungen können mehrere Wahlen ergeben. Noch {0} übrig.',
'fr':'Les récompenses d’EXP et de boss se cumulent. Choix restants : {0}.',
'es':'Las recompensas de EXP y jefes se acumulan. Quedan {0} elecciones.',
'it':'Le ricompense di ESP e boss si accumulano. Scelte rimaste: {0}.',
'pt-BR':'Recompensas de EXP e chefes se acumulam. Escolhas restantes: {0}.',
'ru':'Награды за опыт и боссов суммируются. Осталось выборов: {0}.'}
if __name__=='__main__':
 p=Path(__file__).resolve().parents[1]/'index.html'
 s=p.read_bytes().decode();old=next(x for x in s.splitlines() if x.startswith('const L10N='))
 data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,value in ROWS.items():data[lang]['cardQueueHint']=value
 p.write_bytes(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';').encode())
 print('PASS card queue explanation x 11 locales')
