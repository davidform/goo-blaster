# itch.io 固定同步流程

2026-09-09 使用者授權：往後遊戲改動完成驗證後，直接同步既有 itch.io 遊戲，不再逐次詢問。此流程與 Android 測試 APK 一起執行；不是背景自動排程。

- 公開頁：https://davidform.itch.io/goo-blaster
- 編輯頁：https://itch.io/game/edit/4906809
- 固定通道：`davidform/goo-blaster:html5`
- Butler：`_private/butler/butler.exe`；使用既有登入，不輸出／記錄 token。
- 只傳已驗證的單一 `index.html`。不能上傳整個 repo、`_private`、原生存檔、APK簽章或其他內部文件。

## 每次發布

1. 核對Git、BUILD及完整報告。沿用 `native/build_test_apk.py` 的 `validate_reports` 規則：完整當前套件、全部通過、同一HTML SHA，補跑必須保留原始失敗。不能拿舊版測試替新版。
2. 複製原始位元組至獨立 `_private/itch-builds/<BUILD>/index.html`，核對該資料夾只有這一個檔案且SHA相同；不得另改EDITION或翻譯。
3. 執行（替換實際BUILD）：

   ```powershell
   & _private/butler/butler.exe push _private/itch-builds/v0.9.55 davidform/goo-blaster:html5 --userversion v0.9.55
   & _private/butler/butler.exe status davidform/goo-blaster:html5
   ```

4. 等通道處理完成，開公開頁按Run game，核對版本並實際開始一關／暫停。從實際iframe取得資產網址，下載核對完整遊戲payload與測試SHA。
5. itch CDN可能在結尾追加 `https://static.itch.io/htmlgame.js`。保留原始差異與公開整檔SHA，只能在確定「原始完整payload未變，差異僅平台腳本」後通過，不能任意忽略差異。
6. 記錄upload/build ID、版本、payload SHA、公開資產網址、啟動結果至私人證據與歷史／HANDOFF，commit/push本次文件。

## 已完成的一次性設定

2026-09-09 v55首次建立html5通道；在編輯頁讓新版index.html勾選「This file will be played in the browser」。舊goo-blaster-v0.9.31.html取消網頁遊玩並勾「Hide this file and prevent it from being downloaded」，保留未刪除。之後只推同一通道，不能每版新增不同通道。

現有No payments、公開狀態、Portrait／mobile friendly均保留；使用者此次只授權同步遊戲，沒有要求改價格或其他商店。若需要重新登入或權限失效，完成本地準備並明示卡點，不聲稱發布成功。

官方工具說明：[Butler pushing](https://itch.io/docs/butler/pushing.html)。
