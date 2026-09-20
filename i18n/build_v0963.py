"""Limited builds and non-recursive completion rewards, eleven locales."""
import json,sys
from pathlib import Path
ROWS={
'en':['Weapons {0}/2 · Skills {1}/4','Build complete: +{0} Candy'],
'zh-Hant':['武器 {0}/2 · 能力 {1}/4','流派已成形：糖果幣 +{0}'],
'zh-Hans':['武器 {0}/2 · 能力 {1}/4','流派已成形：糖果币 +{0}'],
'ja':['武器 {0}/2・能力 {1}/4','ビルド完成：キャンディ +{0}'],
'ko':['무기 {0}/2 · 능력 {1}/4','조합 완성: 사탕 +{0}'],
'de':['Waffen {0}/2 · Fähigkeiten {1}/4','Build komplett: +{0} Bonbons'],
'fr':['Armes {0}/2 · Capacités {1}/4','Configuration complète : +{0} bonbons'],
'es':['Armas {0}/2 · Habilidades {1}/4','Combinación completa: +{0} caramelos'],
'it':['Armi {0}/2 · Abilità {1}/4','Combinazione completa: +{0} caramelle'],
'pt-BR':['Armas {0}/2 · Habilidades {1}/4','Combinação completa: +{0} doces'],
'ru':['Оружие {0}/2 · Навыки {1}/4','Сборка завершена: +{0} конфет']}
for lang,label in dict(zip(ROWS,['Secondary weapon','本局副武器','本局副武器','今回のサブ武器','이번 게임 보조 무기','Zweitwaffe','Arme secondaire','Arma secundaria','Arma secondaria','Arma secundária','Второе оружие'])).items():ROWS[lang].append(label)
if __name__=='__main__':
 p=(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])/'index.html'
 s=p.read_bytes().decode();old=next(x for x in s.splitlines() if x.startswith('const L10N='));data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,values in ROWS.items():
  for key,value in zip(['buildSlots','buildComplete','startingWeapon'],values):data[lang][key]=value
 p.write_bytes(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';').encode())
