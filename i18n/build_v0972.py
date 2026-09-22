"""Cottage level crop timing; update all eleven locales together."""
import json
from pathlib import Path
DATA = {
    'en': 'Cottage Lv.{0} · New crops take ×{1} as long. Planted crops keep their timers.',
    'zh-Hant': '小屋 Lv.{0} · 新種作物需時 ×{1}；已種作物的時間不變。',
    'zh-Hans': '小屋 Lv.{0} · 新种作物耗时 ×{1}；已种作物的时间不变。',
    'ja': '家 Lv.{0} · 新しく植える作物の時間は{1}倍。植えた作物の時間は変わりません。',
    'ko': '집 Lv.{0} · 새로 심는 작물의 성장 시간은 {1}배. 이미 심은 작물의 시간은 그대로예요.',
    'de': 'Haus Lv.{0} · Neue Pflanzen brauchen {1}× so lange. Laufende Zeiten bleiben gleich.',
    'fr': 'Maison niv.{0} · Durée des nouvelles cultures : ×{1}. Les délais en cours restent inchangés.',
    'es': 'Casa niv.{0} · Las nuevas plantas tardan ×{1}. Las ya plantadas conservan su tiempo.',
    'it': 'Casa liv.{0} · Le nuove piante richiedono ×{1} tempo. I tempi già avviati non cambiano.',
    'pt-BR': 'Casa nv.{0} · Novas plantas levam ×{1} de tempo. As já plantadas mantêm seus prazos.',
    'ru': 'Дом ур.{0} · Новые растения растут в {1} раза дольше. Сроки уже посаженных не меняются.',
}
if __name__ == '__main__':
    p = Path(__file__).resolve().parents[1] / 'index.html'
    s = p.read_text(encoding='utf-8')
    old = next(x for x in s.splitlines() if x.startswith('const L10N='))
    d = json.loads(old[11:-1])
    assert set(d) == set(DATA)
    for lang, value in DATA.items():
        d[lang]['gardenPace'] = value
    p.write_text(s.replace(old, 'const L10N=' + json.dumps(d, ensure_ascii=False) + ';'), encoding='utf-8')
