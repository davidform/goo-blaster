# GOO BLASTER 精簡交接

## 目前任務（2026-10-01）
- 修正使用者Pixel截圖：首頁六入口完整顯示、不需捲動；庭院捲動不侵入頂部安全區。
- 分支codex/soft-world-ui；BUILD v0.9.81。本版只改畫面邊界，玩法／時間／存檔／翻譯不變。
- Summary：v0.9.81: fit home and garden pages within screen bounds。
- HTML SHA b5eb47b19ab8924ac111944237eda0ade7a058629a428db05def1780fe3dd89e。
- 首頁改剩餘高度自適應，橫向兩排；庭院分類列與安全區不透明遮罩。
- Android adjustMarginsForEdgeToEdge=force；APK／AAB建置均檢查實際封裝設定。
- 單代理；附件.codex-remote-attachments及_private不提交；v80發布與Pixel遷移已完成勿重做。

## v81 已驗證
- 完整88/88 PASS：_private/test-runs/20261001-185753-386699-viewport81-final/results.json。
- 命令 .venv/Scripts/python.exe run_tests.py --jobs 2 --label viewport81-final。
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- py_test9第1關52秒／3心通關、第2關60秒／2心通關；第3關53秒失敗是觀察值，未當成全關通過。
- 獨立效能52.9 FPS有同伴、同批差+11.4%為量測波動，0 JS錯誤；不是Pixel效能。
- CPU4三項PASS：_private/test-runs/20261001-192128-638059-viewport81-cpu4/results.json（viewport_layout、bottom_nav、garden_context）。
- 離線／新存檔／實際關閉重開PASS，0錯誤／0外部請求：_private/play-preparation/release-smoke-v81.log。
- 新測試66版面＝6尺寸×11語言，零溢出、44px入口、無重疊、32／24px安全區、存檔不變。
- v80對照FAIL首頁溢出7px，新版0px；_private/baseline80-layout/regression.log。
- 初次舊87名單及第二次補遮罩前批次均中止且保留，不拿它們替代最終報告。
- store/screenshots/v0.9.81/viewport-manifest.json記錄真實新存檔瀏覽器截圖，非Pixel。
- Surface依既定限制未全平行；CPU4不冒充全平行。最新adb清單無手機，v81真機待驗。

## v81 已交付
- 遊戲commit 5471adf45c3499a080510b4054444f6412ada8f6已push；Summary見上方。
- APK98100／0.9.81-test.0，原debug簽章不變；實際HTML及原生force邊界設定PASS。
- APK SHA de036d65a6753190645c5c303d425dcf6a00a8c9942a3484aadde8c01fc3e067；公開重新下載核對PASS。
- 固定測試入口 https://github.com/davidform/goo-blaster/releases/tag/android-test。
- itch build2046126／upload19167726 Active，公開完整payload＋平台suffix核對、實際開始／暫停PASS；_private/mobile-test/itch-v81.json。
- Pages378329b07a3b11cf943969d0df776f5e3f331080，Actions36855904052成功；公開SHA／開始暫停PASS；pages-v81.json。
- 中英Devlog1685212已Published與record，工作流程9項PASS；store/devlogs/v0.9.81/。
- 商店／原公告17090045／profile正文同步；三張戰鬥主圖後放新版首頁／庭院；保留歷史圖片，論壇與profile各8張已載入。store/page-sync/v0.9.81.json。
- cleanup dry-run後Apply移除2項／13,481,330 bytes，0失敗／25拒絕存取略過。保留v81／v80 APK、進度、金鑰及證據。

## Google Play 實際狀態
- app4976029382108915574／com.demjastudio.gooblaster；不要重建。售價US$1.99、目標9歲以上成人。
- 商家帳戶由本人完成；Console價格最終儲存仍待核對，不代填收款／稅務／身分。
- IARC使用者截圖確認10月1日10:04完成，通知信箱demjaholding@gmail.com；不重填。
- 目標9–12／13–15／16–17／18+、資料安全不收集／不分享已有填寫截圖，最終儲存待核對。
- EN-US／zh-TW商店素材、隱私／存取／無廣告等草稿已準備；客服政策仍需同步新信箱。詳store/google-play/。
- Play管理App簽章；沿用使用者已授權的既有上傳金鑰，未更換任何簽章或建立新金鑰。
- v81已簽AAB98101／0.9.81-rc.1：_private/play-preparation/v0.9.81-98101-play-signed.aab。
- AAB SHA 973d7f134539c7108de5db5ce47c27e7201211186e4bc886ec78f05d55a89db5；HTML同上、API36／debug=false／full／force邊界，strict簽章與bundletool／manifest／原ZIP逐項比對PASS。
- 上傳憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；金鑰在使用者目錄.goo-blaster-signing，異地備份仍未完成。
- 10月1日19:33 Console已顯示0.9.81-rc.1 Internal Test有效／提供給內部測試人員，track4701357753096403615／release2；簽署收據signed-candidate.json、play-v81-console.txt／published.png。
- 唯一提示未提供去混淆檔；minifyEnabled=false，沒有阻擋錯誤、裝置支援數不變。未正式上架或開始12人封測。
- 原內測連結 https://play.google.com/apps/internaltest/4701357753096403615。
- 首次v81憑證檢查因PowerShell未引號包住-J參數失敗；簽署與strict已成功，保留失敗日誌後修正引號，直接驗證原簽包PASS，未重新簽署或換key。

## Pixel與未完成項目
- Pixel私人空間97100/debug簽章阻擋Play，先備份與隔離還原PASS；使用者明確同意一次性移除後改由Play安裝98001。不得擴及日後卸載更新。
- v80 Play實機啟動／重開匯出碼與舊備份相同；證據_private/pixel-play-migration/。備份與碼不得提交。
- Play交付簽章SHA 57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9，與debug／uploadkey均不同。
- 本次adb清單無手機，v81 Play交付APK、覆蓋更新存檔及真機狀態列／首頁手感尚未驗證；不要用debug APK覆蓋Play版，不卸載／清資料。
- 個人帳戶要求12人持續14天，既有Alpha4700117103530327117尚未啟動；內部名單1位不等於封測。商家／價格與正式上架仍未完成。
- 已完成v80發版及遷移不重做。Surface未全平行；市場／母語潤稿未驗證。單代理、不新增玩法／招募私訊／正式送審。
