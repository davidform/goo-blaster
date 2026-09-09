# GitHub Pages 同步流程

2026-09-10 使用者授權：先同步已驗證的 v0.9.55，往後每次通過驗證後，與 APK、itch.io 及 Devlog 一起更新 Pages，不需逐次詢問。這是代理的發版流程，不是背景排程。

公開入口：https://davidform.github.io/goo-blaster/

1. 完成既定遊戲驗證、APK 稽核與 itch 公開內容／實際啟動驗證，保存同版本收據。失敗版本不可發布。
2. 指定包含已驗證 HTML 的確切 commit；不是直接推目前開發 HEAD。先不加 `--publish` 審核：

   ```powershell
   .venv/Scripts/python.exe native/publish_pages.py --commit <commit> --artifact <已驗證index.html> --itch-receipt <itch.json> --tests <完整results.json>
   ```

   有補跑時加 `--retry <results.json>`，保留原失敗。工具使用指定 commit 的套件清單，驗證全部結果、完整 HTML SHA、版本及 itch 收據一致。
3. 同一命令加 `--publish`，以遠端main為父提交，只更新網站白名單檔案；用隔離Git index保留已測HTML原始位元組，不讓換行過濾改變SHA。驗證產物與來源commit僅允許CRLF／LF差異。保留main其他檔案，不合併開發HEAD、不force push；遠端若同時更新，push會安全失敗，須重新核對。
4. `.github/workflows/pages.yml` 在 main push 後自動部署，只發 index、manifest、icons、privacy 等既有白名單。等待該 commit 的 Actions 成功；失敗先查日誌，不當成已發布。
5. 以公開 URL 下載完整 HTML，比對 SHA 與 BUILD，再用瀏覽器實際開始一關、暫停；保存 Actions URL、版本、SHA 與啟動證據到 `_private/mobile-test/pages-<version>.json`，更新 HANDOFF。不要以登入 GitHub 或 push 成功代替部署驗證。

保留開發分支的未發布工作。若重試相同產物而 main 已有相同HTML，push 不會再觸發工作流程；先查既有部署，必要時手動重跑該版本的 Pages workflow。

此授權只涵蓋本作既有 Pages 網站，不含其他遊戲、商店送審、售價或簽章變更。
