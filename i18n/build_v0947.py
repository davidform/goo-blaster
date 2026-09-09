"""Range upgrade descriptions, prepared for the separately validated game change."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEYS=['m_range_d','u_rangeUp_d','u_rangeUp_d2']
ROWS={
'en':['Targeting range +{0}; projectile speed +{1}%','Targeting range +140; projectile speed +15%','Total: targeting range +280; projectile speed +30%'],
'zh-Hant':['鎖定範圍 +{0}；投射物速度 +{1}%','鎖定範圍 +140，投射物速度 +15%','合計：鎖定範圍 +280，投射物速度 +30%'],
'zh-Hans':['锁定范围 +{0}；投射物速度 +{1}%','锁定范围 +140，投射物速度 +15%','合计：锁定范围 +280，投射物速度 +30%'],
'ja':['照準範囲+{0}、弾速+{1}%','照準範囲+140、弾速+15%','合計：照準範囲+280、弾速+30%'],
'ko':['조준 범위 +{0}, 발사체 속도 +{1}%','조준 범위 +140, 발사체 속도 +15%','총 효과: 조준 범위 +280, 발사체 속도 +30%'],
'de':['Zielreichweite +{0}; Projektiltempo +{1}%','Zielreichweite +140; Projektiltempo +15%','Insgesamt: Zielreichweite +280; Projektiltempo +30%'],
'fr':['Portée de visée +{0} ; vitesse des projectiles +{1}%','Portée de visée +140 ; vitesse des projectiles +15%','Au total : portée de visée +280 ; vitesse des projectiles +30%'],
'es':['Alcance de apuntado +{0}; velocidad de proyectiles +{1}%','Alcance de apuntado +140; velocidad de proyectiles +15%','Total: alcance de apuntado +280; velocidad de proyectiles +30%'],
'it':['Portata di mira +{0}; velocità dei proiettili +{1}%','Portata di mira +140; velocità dei proiettili +15%','Totale: portata di mira +280; velocità dei proiettili +30%'],
'pt-BR':['Alcance da mira +{0}; velocidade dos projéteis +{1}%','Alcance da mira +140; velocidade dos projéteis +15%','Total: alcance da mira +280; velocidade dos projéteis +30%'],
'ru':['Дальность прицеливания +{0}; скорость снарядов +{1}%','Дальность прицеливания +140; скорость снарядов +15%','Всего: дальность прицеливания +280; скорость снарядов +30%'],
}
path=ROOT/'index.html';s=path.read_text(encoding='utf-8');old=next(line for line in s.splitlines() if line.startswith('const L10N='))
d=json.loads(old[len('const L10N='):-1]);assert set(d)==set(ROWS)
for lang,row in ROWS.items():d[lang].update(zip(KEYS,row))
new='const L10N='+json.dumps(d,ensure_ascii=False)+';'
path.write_text(s.replace(old,new),encoding='utf-8')
print('Updated range descriptions in all 11 languages')
