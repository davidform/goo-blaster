# Google Play 上架準備

核對日期：2026-09-29。沿用既有草稿 `com.demjastudio.gooblaster`，**未送審、未正式發布**。

## 已完成
- 使用者定價 US$1.99，一次付費下載完整遊戲；商家帳戶尚待本人完成，Console 價格尚未儲存。
- 預定對象為 9–12、13–15、16–17、18+，不是 IARC 內容分級。Console 年齡尚未完成。
- Console 已存隱私網址、無廣告、不需登入／特殊存取、非政府／金融／健康 App 聲明。
- 資料安全「不收集、不分享」已存草稿；最終完成受目標對象設定阻擋。
- 遊戲／動作分類、公開聯絡信箱與 HTTPS 網址已儲存。
- 英文與繁中商店名稱、短介、全文及圖像已存草稿；圖像順序為三張戰鬥，再一張小鎮。
- 已如實標記六張 AI 製作視覺素材（圖示、主視覺、四張截圖）；沒有按送交審查。
- `listing.json` 是本機文案來源；`assets/manifest.json` 與 `combat-manifest.json` 記錄素材來源及檢視。

## 候選產物與證據
- 遊戲 v0.9.80，commit `8edd22063eccf79e2d24fc3bd95a64997c963d3c`。
- HTML SHA256：`a70daa8c6c507d3584a414152220e4141d25a81fab7253ec0271b9a335f79217`。
- AAB：`_private/play-preparation/goo-blaster-v0.9.80-98001-unsigned.aab`，versionCode 98001、versionName 0.9.80-rc.1。
- AAB SHA256：`7d8f7be37fd1ff5a5517a0d85e422ac2783b5f2601d47bd6f408e97e6a5416d6`。
- bundletool 1.18.3 validate 通過；實際 manifest API 36、debuggable=false、正確套件名；內嵌 HTML 一致、full 版、無 .so、無簽署。
- `native/build_play_candidate.py` 已實跑，完成後測試版 Gradle 設定逐位元組還原；**尚未簽署及上傳 AAB**。
- 瀏覽器完整 87/87 PASS：`_private/test-runs/20260929-194400-848598-privacy80-full/results.json`。
- CPU4 邊角：`_private/test-runs/20260929-200922-480275-privacy80-cpu4/results.json`；離線／新存檔／重開：`_private/play-preparation/release-smoke-v80.log`。
- 瀏覽器通過不等於 Play 最終交付 APK 或真機驗收；Surface 未跑全平行。

## 必須接續完成
1. 使用者完成商家帳戶後，設定 US$1.99 與銷售地區並核對。
2. 等待使用者確認 IARC 條款，才能開始問卷；不要猜測分級。問卷完成後解決 9–12 選項目前受 ESRB Teen 提示阻擋的狀態。
3. 等待使用者同意建立專用上傳金鑰與簽署。Console 已有 Google 管理的 App 簽章，但尚未登記上傳憑證；不要更換 App 簽章，也不要拿 debug 金鑰充當上傳金鑰。
4. 經授權簽署後核對最終 AAB，再上傳測試草稿。金鑰／密碼不得進 Git、Release 或交接文。
5. 測試 Google Play 實際交付、原生隱私連結、離線與存檔持久性。先備份現有進度，不能靠卸載／清資料解決不同簽章。
6. 此個人帳戶 Console 實際要求 **12 位測試者持續加入封閉測試 14 天**；目前 0 位，GitHub APK 與機器人測試不能取代。計畫見 `testing-plan.md`。
7. 收集真人回饋並處理問題，再另行確認正式送審。技術測試不等於市場需求或購買意願驗證。

## 官方依據
- [封閉測試要求](https://support.google.com/googleplay/android-developer/answer/14151465?hl=en)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756?hl=en)
- [AI 素材標記](https://support.google.com/googleplay/android-developer/answer/17262077?hl=en)
- [商店素材規格](https://support.google.com/googleplay/android-developer/answer/9866151?hl=en)
- [bundletool 1.18.3](https://github.com/google/bundletool/releases/tag/1.18.3)
