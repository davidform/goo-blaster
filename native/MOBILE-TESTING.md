# 固定手機測試入口

使用者於 2026-09-09 要求：手機經常遠端操作電腦，不會一直用 USB 連線；往後都透過固定方式取得測試版。

固定入口：[Android 手機測試版](https://github.com/davidform/goo-blaster/releases/tag/android-test)。這是 **Prerelease 測試通道**，不更新正式 Pages、itch.io 或商店版本。入口不依賴這台電腦開機。

## 手機怎麼測

1. 在 **Pixel 本機的瀏覽器**開啟上方連結並加入書籤，不必透過遠端桌面玩。
2. 按頁面最上方「下載 Android 測試版 APK」，下載後開啟；首次依 Android 提示允許瀏覽器安裝。
3. 已安裝時選「更新」，**不要先解除安裝舊版**。首次更新前可在遊戲設定保留一份備份碼。
4. 開啟遊戲並核對畫面版本。安裝後遊戲可離線；未來更新仍從同一頁下載。
5. 回報版本、關卡、聲音／卡頓／難度情況即可。簽章與版本核對通過不等於已完成手機上的覆蓋更新實測。

Android 仍需使用者確認安裝；這個流程不會偷偷更新 App，也不要求關閉 Play Protect。

## 後續開發預設流程

每次本次範圍的遊戲改動驗證完成後，自動更新此測試通道，無需再問一次是否提供手機測試版。使用者的授權限於測試 APK，不含正式上架、價格或更換簽章。

1. 完成並提交遊戲改動；取得同一份 `index.html` 的完整通過測試報告。保留首輪失敗與補驗證證據，不將未完成算通過。
2. 效能測試全部結束後才建置 Android，不讓 Gradle 與效能測試競爭 CPU。
3. 執行下列建置，再檢查 `_private/mobile-test/latest.json`：

   ```powershell
   $env:GOO_BROWSER_CHANNEL='msedge'
   $env:PYTHONUTF8='1'
   .venv/Scripts/python.exe native/build_test_apk.py --tests _private/test-runs/<已通過的批次>/results.json
   ```

   若完整批次有失敗，修正並完成針對性重跑後，可加 `--retry <重跑批次>/results.json`（可重複）。完整批次仍必須涵蓋目前所有測試，全部報告須對應同一遊戲 SHA，合併後每項均通過；不得刪除原失敗。遊戲原始碼若改變，須重新跑完整套件，不能沿用舊報告。

4. 將本次給玩家看的改動寫入 `_private/mobile-test/notes.md`；核對 APK、文案與未完成驗證後執行：

   ```powershell
   .venv/Scripts/python.exe native/publish_test_apk.py --publish
   ```

5. 確認 `_private/mobile-test/published.json` 的 `public_download_verified` 為 true；回報固定入口、版本、證據與仍未做的真機項目。

建置會增加 Android `versionCode`，檢查 APK 內實際遊戲 SHA256、applicationId、versionName、簽章與前一 APK。`native/test-channel.json` 只固定公開簽章指紋，不含私鑰；簽章不一致就停止，不能要求玩家卸載來掩蓋問題。私鑰不得放進 Git 或 Release。

GitHub 使用現有 Git 登入，憑證只留在程序記憶體，不寫入報告。`android-test` 是此工具管理的可前進測試標籤；只有帶管理標記的 Prerelease 可更新。每個 APK 使用包含遊戲版本與 Android 版本號的獨立檔名，舊資產不刪除／不覆寫；標籤只允許沿原提交歷史前進。來源 commit 與 APK SHA256 明列在下載頁。正式標籤及 `main` 不受此流程修改。

原始碼驗證、APK 內容與簽章驗證、實際手機安裝是三件事。全平行壓測與新 APK 的真機覆蓋更新若仍未完成，測試通道必須明示，不能宣稱正式驗收完成。

參考：[Android 版本管理](https://developer.android.com/studio/publish/versioning)、[APK 簽章驗證](https://developer.android.com/tools/apksigner)、[GitHub Release API](https://docs.github.com/en/rest/releases/releases)。
