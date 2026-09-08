# Windows 原生建置與驗證

2026-09-08 已在此電腦建出 debug APK 與 **未簽署** release AAB。
Android Studio 不需要保持開啟。使用已安裝的 JDK 21；本機 Android Studio 隨附的是 JDK 25，不拿它替代這次驗證的環境。

從專案根目錄執行：

```powershell
python native/prepare_android.py
Push-Location native
node node_modules/@capacitor/cli/bin/capacitor sync android
Pop-Location
$env:JAVA_HOME = 'C:/Users/Surface/.jdks/jbr-21.0.11'
Push-Location native/android
./gradlew.bat --no-daemon --max-workers=2 assembleDebug bundleRelease
Pop-Location
```

Java 路徑為本機實測位置，其他電腦請改為自己的 JDK 21。
`native/android/local.properties` 指向本機 Android SDK，不能提交。
不要在瀏覽器效能測試期間建置 Android。

產物：

- `native/android/app/build/outputs/apk/debug/app-debug.apk`：開發簽章，供真機測試。
- `native/android/app/build/outputs/bundle/release/app-release.aab`：目前沒有 release 簽章，不可直接送審。

每次檢查 APK 的 `assets/public/index.html`、AAB 的 `base/assets/public/index.html` SHA256 是否等於根目錄遊戲。
同時核對封裝的 `capacitor.config.json`、Manifest 的 applicationId 與 MainActivity；不能只看原始碼或 BUILD SUCCESSFUL。
可執行 `python native/audit_artifacts.py`，結果寫入 `_private/test-artifacts/android-artifacts.json`。

原生存檔真機檢查（只針對新套件 `com.demjastudio.gooblaster`）：

```powershell
$env:NODE_PATH = (Join-Path (Get-Location) '_private/test-node/node_modules')
node native/test_device.cjs <adb-device-serial>
```

須先經使用者同意將測試手機設為飛航且關閉 Wi-Fi。腳本先確認狀態，保存實際進度，
核對真實 Preferences 寫入，再強制關閉、重新啟動並核對進度；不清除資料或卸載 App。
這只驗證 debug APK 與當次情境，不代表已測 AAB 安裝、升版、移除重裝或系統雲端備份恢復。
測試後由使用者恢復手機網路。

備份：`python native/backup_android.py` 會把原生來源與套件鎖檔存入 `_private/android-backups/`。
排除快取、建置產物、機器設定與憑證；這是本機備份，尚不是異機或雲端備份。
復原時解壓到獨立目錄，執行 `npm ci`，重建指向本機 SDK 的 `android/local.properties`，
再使用上述同步與建置流程。不要把備份直接覆蓋正在使用的專案。
依 AGENTS.md，原生專案的正式遠端版本管理仍應使用獨立 repo；本次未建立新遠端。
