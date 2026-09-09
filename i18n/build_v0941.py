"""Add the soft-world navigation labels in all 11 languages, idempotently."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KEYS=['navAdventure','navUpgrades','navSettings','languageLabel','soundOn','soundOff','settingsHint','chapterLabel']
ROWS={
 'en':['Adventure','Upgrades','Settings','Language','Sound: on','Sound: off','Sound, language and your save backup.','Chapter {0}'],
 'zh-Hant':['冒險','強化','設定','語言','音效：開啟','音效：關閉','調整音效、語言，並備份你的進度。','第 {0} 章'],
 'zh-Hans':['冒险','强化','设置','语言','音效：开启','音效：关闭','调整音效、语言，并备份你的进度。','第 {0} 章'],
 'ja':['冒険','強化','設定','言語','サウンド：オン','サウンド：オフ','サウンド、言語、セーブデータのバックアップ。','チャプター {0}'],
 'ko':['모험','강화','설정','언어','소리: 켜짐','소리: 꺼짐','소리와 언어를 설정하고 진행 상황을 백업하세요.','챕터 {0}'],
 'de':['Abenteuer','Verbessern','Optionen','Sprache','Ton: an','Ton: aus','Ton, Sprache und Sicherung deines Spielstands.','Kapitel {0}'],
 'fr':['Aventure','Améliorer','Réglages','Langue','Son : activé','Son : coupé','Son, langue et sauvegarde de votre progression.','Chapitre {0}'],
 'es':['Aventura','Mejoras','Ajustes','Idioma','Sonido: sí','Sonido: no','Sonido, idioma y copia de tu partida.','Capítulo {0}'],
 'it':['Avventura','Potenziamenti','Opzioni','Lingua','Audio: sì','Audio: no','Audio, lingua e backup dei tuoi progressi.','Capitolo {0}'],
 'pt-BR':['Aventura','Melhorias','Ajustes','Idioma','Som: ligado','Som: desligado','Som, idioma e backup do seu progresso.','Capítulo {0}'],
 'ru':['Приключение','Улучшения','Настройки','Язык','Звук: вкл.','Звук: выкл.','Звук, язык и резервная копия прогресса.','Глава {0}'],
}

def main():
    path=ROOT/'index.html'
    text=path.read_text(encoding='utf-8')
    line=next(l for l in text.splitlines() if l.startswith('const L10N='))
    data=json.loads(line[len('const L10N='):-1])
    assert set(ROWS)==set(data)
    for lang,values in ROWS.items():
        assert len(values)==len(KEYS)
        data[lang].update(dict(zip(KEYS,values)))
    text=text.replace(line,'const L10N='+json.dumps(data,ensure_ascii=False)+';')
    path.write_text(text,encoding='utf-8')
    print(f'Updated {len(KEYS)} labels in {len(data)} languages')

if __name__=='__main__':
    main()
