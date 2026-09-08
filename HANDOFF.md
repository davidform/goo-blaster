# GOO BLASTER — 目前交接
更新：2026-09-08；本檔只保留現況，不複製完整對話。

## 接手方式
- 先讀 AGENTS.md，再讀本檔；核對 git status --short、git log -3 --oneline 與 BUILD。
- 修改前先檢查未提交差異，再安全同步；不假設 Claude 的歷史測試仍適用。
- 本次工作前的已同步基準：7c9c053；最新提交請用 git log 查，不用本檔自指 SHA。
- 換對話時提醒使用者在同一專案貼上：
  > 依 AGENTS.md 與 HANDOFF.md 接手，先核對實際狀態，再完成目前任務。回報測試證據、未完成項目與 commit Summary。

## 已確認方向
- 目標：兒童可離線遊戲，Google Play 與 Apple App Store；不含廣告/訂閱/消耗型購買。
- 定價基準 US$2.99，一次付費下載完整遊戲；目前未接原生內購。
- 家長是購買決策者；9–12 歲為初步體驗研究方向，不是已定案的商店年齡申報。
- 正式年齡組、內容分級與資料安全申報，要依真實內容及 SDK/產物稽核決定。
- 日常可用 5.6 Terra 中；核心/存檔/跨系統疑難與發行稽核用 6 Astra 高。
- 這是工作分配建議，不是保證品質/節省比例；不自動更改使用者的模型或用量設定。
- 遊戲三輪實跑；文件採相應檢查。效能獨立跑，測試證據必須區分未執行。
- 每次回報 commit Summary；授權內可自動同步，商店送審/發布需另外授權。

## 目前任務
- 已建立交接規則；已修正 PRIVACY.md 與 privacy.html 的中英文說明。
- 本次不改 index.html、原生設定或產生 AAB，不提交 Play Console 聲明。
- 同步收尾已完成：2026-09-08 實查本機與遠端 main 同為 f0ef768，git pull --ff-only 無更新。
- 公開政策 HTTP 200；8614 字元與本機 privacy.html 完全一致（統一換行後比較）。
- 本次 commit Summary：docs: confirm privacy deployment and handoff verification
- 政策網址：https://davidform.github.io/goo-blaster/privacy.html

## 本機已核對的事實（2026-09-08）
- index.html：v0.9.40；本次修改前 SHA256：
  CC7E50FCB9D87979BE694C413C0B6173AF0435C4647A2166B599AEF10E267D6B
- native/package.json 使用 Capacitor core/android/ios、Preferences、Splash Screen。
- NATIVE_STORE 使用 Preferences 加 localStorage；不能聲稱「沒有第三方 SDK」。
- btnResetConfirm 只重設 PROGRESS/SEL_IDX，不清除金幣/強化/語言/解鎖。
- AndroidManifest.xml allowBackup=true；作業系統可能備份/移轉資料。
- 原生 applicationId/namespace 已為 com.demjastudio.gooblaster。
- 但 MainActivity.java package 和 strings.xml 的 package_name/custom_url_scheme 仍是舊值。
- native/android 被忽略；GitHub 乾淨不代表本機原生專案已備份或封裝正確。
- 本次尚未對新套件名稱完成 release AAB 與真機驗證，不能拿舊套件測試代替。

## 驗證範圍與限制
- 本次重跑 node tests/check_release_docs.cjs：8/8 通過；git diff --check 通過。
- 上一輪 Playwright / Edge headless：1280×900 與 390×844 無橫向溢出/頁面錯誤並檢視截圖；本次未重跑。
- index.html 修改後 SHA256 與上述基準相同；詳細檢查紀錄見 docs-14-history.md。
- 本次核對存檔/重設/匯出程式、原生依賴及備份設定；並非完整網路行為稽核。
- 政策說明客服郵件、平台託管/付款/備份，不再宣稱所有情境皆零資料。
- 完整遊戲三輪、Windows 測試環境、原生 release 與 iOS 真機：本次未執行。
- 舊紀錄 cap sync 曾出現 uv_os_get_passwd ENOMEM，原因未證實，不可直接歸因記憶體不足。
- 舊紀錄 Gradle CLI 找不到 JAVA_HOME/java；可先檢查 Android Studio JBR，勿盲目重裝。
- Android Studio 桌面控制在當前工具未啟用；檔案/命令操作與瀏覽器能力分開核對。
- 不把 BUILD SUCCESSFUL 畫面當作 signed release AAB 已產生的證據。

## 下一步（按順序）
1. 政策 Git 同步與公開部署已驗證完成；後續政策有修改時須重新核對。
2. 修正/驗證原生套件名稱殘留，確認 webDir、三份遊戲內容 hash 與打包入口一致。
3. 稽核 release 的 SDK/Manifest、離線網路與存檔備份/重啟行為；再決定商店申報。
4. 政策與實際產物一致後，填入 Play Console 隱私政策網址；不要直接送審發布。
5. 補齊測試環境與不含密鑰的原生重建/備份流程，另排 iOS 封裝。
