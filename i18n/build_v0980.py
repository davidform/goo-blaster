"""An explicit external privacy-policy entry in every supported language."""
import json
from pathlib import Path

DATA = {
    'en': 'Privacy policy (website)',
    'zh-Hant': '隱私權政策（開啟網站）',
    'zh-Hans': '隐私权政策（打开网站）',
    'ja': 'プライバシーポリシー（ウェブサイト）',
    'ko': '개인정보 처리방침 (웹사이트)',
    'de': 'Datenschutzerklärung (Website)',
    'fr': 'Politique de confidentialité (site web)',
    'es': 'Política de privacidad (sitio web)',
    'it': 'Informativa sulla privacy (sito web)',
    'pt-BR': 'Política de privacidade (site)',
    'ru': 'Политика конфиденциальности (сайт)',
}

if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'index.html'
    source = path.read_text(encoding='utf-8')
    old = next(line for line in source.splitlines() if line.startswith('const L10N='))
    dictionary = json.loads(old[11:-1])
    assert set(dictionary) == set(DATA)
    for lang, text in DATA.items():
        dictionary[lang]['privacyPolicy'] = text
    path.write_text(source.replace(old, 'const L10N=' + json.dumps(dictionary, ensure_ascii=False) + ';'), encoding='utf-8')
