"""Battle-report export feedback in every supported locale."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEYS=['shotSaving','shotSaved','shotCancelled','shotDownload','shotSaveFailed']
ROWS={
'en':['Choose where to save the image…','Report saved.','Save cancelled. You can try again.','Download started. Check your browser downloads.','Could not save. Please try again with the latest app version.'],
'zh-Hant':['請選擇圖片儲存位置…','戰報已儲存。','已取消儲存，可以再試一次。','已開始下載，請查看瀏覽器下載項目。','無法儲存，請使用最新版遊戲再試一次。'],
'zh-Hans':['请选择图片保存位置…','战报已保存。','已取消保存，可以再试一次。','已开始下载，请查看浏览器下载项。','无法保存，请使用最新版游戏再试一次。'],
'ja':['画像の保存先を選んでください…','戦績画像を保存しました。','保存をキャンセルしました。再試行できます。','ダウンロードを開始しました。ブラウザのダウンロード一覧を確認してください。','保存できませんでした。最新版のゲームで再試行してください。'],
'ko':['이미지를 저장할 위치를 선택하세요…','전투 기록 이미지를 저장했습니다.','저장을 취소했습니다. 다시 시도할 수 있습니다.','다운로드를 시작했습니다. 브라우저의 다운로드 목록을 확인하세요.','저장하지 못했습니다. 최신 버전의 게임에서 다시 시도하세요.'],
'de':['Wähle einen Speicherort für das Bild…','Spielbericht gespeichert.','Speichern abgebrochen. Du kannst es erneut versuchen.','Download gestartet. Prüfe die Downloads deines Browsers.','Speichern fehlgeschlagen. Versuche es mit der neuesten Spielversion erneut.'],
'fr':['Choisissez où enregistrer l’image…','Bilan enregistré.','Enregistrement annulé. Vous pouvez réessayer.','Téléchargement lancé. Consultez les téléchargements de votre navigateur.','Enregistrement impossible. Réessayez avec la dernière version du jeu.'],
'es':['Elige dónde guardar la imagen…','Informe guardado.','Guardado cancelado. Puedes volver a intentarlo.','Descarga iniciada. Revisa las descargas de tu navegador.','No se pudo guardar. Inténtalo de nuevo con la última versión del juego.'],
'it':['Scegli dove salvare l’immagine…','Resoconto salvato.','Salvataggio annullato. Puoi riprovare.','Download avviato. Controlla i download del browser.','Salvataggio non riuscito. Riprova con l’ultima versione del gioco.'],
'pt-BR':['Escolha onde salvar a imagem…','Relatório salvo.','Salvamento cancelado. Você pode tentar novamente.','Download iniciado. Confira os downloads do navegador.','Não foi possível salvar. Tente novamente com a versão mais recente do jogo.'],
'ru':['Выберите, куда сохранить изображение…','Отчёт сохранён.','Сохранение отменено. Можно попробовать снова.','Загрузка началась. Проверьте загрузки браузера.','Не удалось сохранить. Попробуйте ещё раз в последней версии игры.'],
}
path=ROOT/'index.html'
with path.open(encoding='utf-8',newline='') as source:s=source.read()
old=next(line for line in s.splitlines() if line.startswith('const L10N='))
d=json.loads(old[len('const L10N='):-1]);assert set(d)==set(ROWS)
for lang,row in ROWS.items():
    assert len(row)==len(KEYS)
    d[lang].update(zip(KEYS,row))
path.write_text(s.replace(old,'const L10N='+json.dumps(d,ensure_ascii=False)+';'),encoding='utf-8',newline='')
print('Updated report feedback: 5 keys x 11 languages')
