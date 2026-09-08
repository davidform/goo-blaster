# GOO BLASTER — 目前交接
更新：2026-09-09；本檔只保留現況，不複製完整對話。

## 接手方式
- 先完整讀 AGENTS.md 與本檔，再核對 git status、git log、BUILD 與本次任務。
- 修改前先檢查未提交差異，再安全同步；禁止 reset/覆寫消除差異。
- 只有評估對話長度過長、確實需要換新對話時才提醒，不因階段完成提醒。
- 需要換對話時，在同一專案貼上：
  > 依 AGENTS.md 與 HANDOFF.md 接手，先核對實際狀態，再完成目前任務。回報測試證據、未完成項目與 commit Summary。

## 已確認方向與授權
- 兒童可離線遊戲；US$2.99 一次付費下載完整遊戲，不含廣告/訂閱/消耗型購買，尚未接原生內購。
- 家長是購買決策者；9–12 歲只是體驗研究方向，正式商店年齡與資料申報尚未定案。
- 單一代理；遊戲改動三輪實跑，效能必須單獨跑；回報區分已驗證、失敗、未執行。
- Git 可在授權範圍自動 commit/push，只提交本次檔案；商店送審/發布、定價與敏感簽章操作需另行授權。
- itch.io 已明確授權：遊戲改版通過規定測試後自動更新 davidform/goo-blaster 的網頁遊戲；不含價格或商店文案。
- Chrome/GitHub Desktop/Android Studio 不必常開；執行工作需此專案工具環境、連網及電腦不睡眠。

## 目前任務與發布阻擋
- 最新需求：Pixel 10 Pro卡頓、參考圖式柔和配色、研究市場後豐富介面。建議先實機定位/單項最佳化，再分版配色與介面；本輪尚未改正式遊戲。
- docs-15-performance-and-art-direction.md 記錄3款案例、色彩/介面規格與效能診斷；對話已有奶油鼠尾草/霧藍薰衣草互動概念，尚非正式設計驗收。
- adb devices 本輪無裝置；已詢問卡頓對應新/舊App或網頁、版本/關卡/場景，尚未收到答案。下一步接Pixel錄實際長幀；不拿桌機通過否定真機回報。
- 本次已處理 Windows 測試相容、Android 套件修正、實際 APK/AAB 與真機驗證；index.html 沒有修改。
- 上輪 Windows 全套為 46/47；2026-09-09 原 py_v0927_perf 單獨重跑已通過：無同伴42.7、有同伴42.6 FPS、損失0.2%，原門檻未改。不是新一輪全套47/47。
- 48 工全平行壓力造成電腦嚴重失去回應與多項導頁逾時，已中止並清理；不得宣稱三輪全綠。
- 同批固定亂數 v0.9.31/v0.9.40 重場景對照平均均約19.47 FPS；只是診斷，不能取代門檻或證明真機效能。
- itch.io 尚未首次推送或切換檔案；不能把工具授權成功當作已發布。
- 本機採已完整跑完的4工；48工不再重試。全平行壓力驗收需較充足的測試主機，仍未完成，不為發布放寬驗收。

## 已驗證：測試環境
- .venv Python Playwright 1.62.0；Node Playwright 在 _private/test-node；官方 Chromium 下載逾時，改用已安裝 Edge。
- tests/README.md 有完整指令；run_tests.py 讀取 run_tests.sh 原套件清單，支援 Windows，逐項保存結果與程序 PID。
- 預設套件改為可攜路徑/可選瀏覽器；部分非預設診斷腳本仍有 Linux 路徑。
- py_ab_base 固定提取 Git 50b166b 的真實 v0.9.20；修正兩處漏報失敗。py_test9 失敗會回傳非零，小圖示請求回204避免無關404。
- 最終完整紀錄：_private/test-runs/20260908-234507-833719-final-functional/results.json（46/47、已完整結束）。
- 第一輪紀錄：20260908-231458-436732-baseline（45/47，小圖示與效能）；壓力紀錄：20260908-233202-939857-stress（中止、只有逐支 log）。
- 最終笨 bot 第1–3關通關且無 JS 錯誤；第5關CPU4x、零永久強化壓測通過；其他語系、排版、存檔、卡池等通過。
- py_release_smoke.py：全新瀏覽器資料、離線、CPU4x、真實關閉重開存檔通過，外部請求0、pageerror0。
- py_perf_baseline.py 僅做同批診斷；_private/test-artifacts/perf-baseline.json 有逐輪數字及GPU啟用狀態。
- 本輪原效能證據：_private/test-runs/20260909-063939-575652-perf-handoff/results.json（exit0、原SHA不變）。
- 新增 tests/py_perf_capacity.py：固定亂數、交替單頁/雙頁三輪，只做測試負載診斷，不取代原門檻或真機。
- 三輪平均單頁無/有同伴59.47/53.47 FPS，雙頁34.11/35.17；12次pageerror皆0，證據_private/test-artifacts/perf-capacity-20260909-064053.json。
- 新增py_render_profile.py：原版/關shadowBlur/DPR1，各3輪；原版54.94/55.44/43.19，其餘55.43–56.55 FPS，9次pageerror0。波動未定位，不宣稱降畫質有效。
- 證據_private/test-artifacts/render-profile-20260909-065755.json；概念稿736/360/320px互動/排版驗證通過；正式遊戲11語系/三輪與真機美術可讀性未測。

## 已驗證：Android
- 使用已安裝 JDK21（C:/Users/Surface/.jdks/jbr-21.0.11）、Gradle8.14.3、SDK36；Android Studio 隨附 JDK25，CLI本次未用它建置。
- native/prepare_android.py 修正 MainActivity 與 strings 的舊識別值、同步webDir，保留備份；不修改遊戲。
- cap sync android 成功；Preferences7.0.4、SplashScreen7.0.5；assembleDebug + bundleRelease 成功，332 tasks。
- native/audit_artifacts.py 驗證實際 APK/AAB 內含遊戲與根目錄 SHA256 完全一致：
  CC7E50FCB9D87979BE694C413C0B6173AF0435C4647A2166B599AEF10E267D6B（BUILD v0.9.40）。
- appId/MainActivity 為 com.demjastudio.gooblaster；release merged Manifest allowBackup=true、debuggable=false、minSdk23/targetSdk36。
- debug APK 4,261,164 bytes；release AAB 3,112,351 bytes，未簽署；詳細 hash 在 native/audit_artifacts.py 輸出及歷史。
- Pixel 真機原有 io.itch.davidform.gooblaster；新套件並存安裝，未覆蓋舊版或舊存檔。
- 真機在飛航1、Wifi disabled下，真實Preferences存檔、強制停止後冷啟動、進度保留與再次開局通過；保留使用者實際第3關/23金幣/強化/語言。
- native/test_device.cjs 可重跑；_private/test-artifacts/android-device.json 與 android-offline-*.png 為證據。
- 測試手機已可恢復網路；最後檢查時已拔除USB。不要假設仍連線或仍離線。
- native/BUILD-WINDOWS.md 有建置/稽核/備份指令；native/backup_android.py 已產出73檔來源ZIP（_private/android-backups），不含快取、產物、機器設定與憑證。
- 原生 android/ 仍被Git忽略；重做腳本已提交，本機ZIP不是異機備份，原生獨立遠端repo尚未建立。

## 其他現況與未完成
- butler v15.31.0 在 _private/butler，授權已成功；憑證僅存標準本機位置，不讀出、不提交。
- itch project 4906809 已是HTML，目前檔名 goo-blaster-v0.9.31.html；尚無butler頻道，預定html5。
- tools/publish_itch.cjs 預設僅打包；--push 要附通過測試之SHA256，參數只核對bytes，不代表測試自動通過。
- 隱私政策 https://davidform.github.io/goo-blaster/privacy.html 已驗證HTTP200、與本機一致；政策已說明Preferences/平台備份/客服。
- 尚未執行：release簽章與AAB派生安裝、升版/移除重裝/系統備份恢復、完整網路行為稽核、Play Console申報、iOS。
- Android真機曾有non-cancelable touchmove的console警告，未證實影響；不等同pageerror，也未修改遊戲消除它。
- 本次提交：build: verify Android package and offline save persistence（485821c）；測試提交以git log核對。
- 本輪 Commit Summary：test: profile render cost and document soft visual direction
