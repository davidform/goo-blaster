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

## v81 交付進度
- 原始碼測試完成；正在建立APK／已授權簽署的Play候選及同步既有通道。
- 尚未宣稱v81 Play／APK／itch／Pages／Devlog已發布；完成後補實際收據。
- Chrome既有Play內部測試建立版本頁已填v81名稱與中英說明，尚未上傳AAB。
- itch編輯頁及原論壇17090045有未儲存v81文字，待公開payload完成後再存。
- Pixel已是Play簽章版本；不可用debug APK覆蓋，不卸載／不清除資料。
- 已完成v80交付：APK98000、itch2035680、Pages3db64d5、Devlog1682276；詳歷史，勿重做。

## Google Play 實際狀態
- 既有草稿 app4976029382108915574／com.demjastudio.gooblaster；不要重建。
- 已存隱私、存取／無廣告／非政府／非金融／非健康、Action分類與公開信箱及HTTPS網址。
- EN-US／zh-TW商店全文、圖示、主視覺、四張手機截圖已存草稿；六視覺素材AI標記已存，未送審。
- 資料安全不收集／不分享已存草稿，最終完成受目標對象設定阻擋。
- 使用者確認9–12／13–15／16–17／18+；先前9–12停用提示已不作現況依據，IARC已完成後以Console實際儲存結果核對。
- 使用者截圖確認IARC於10月1日10:04已完成、信箱demjaholding@gmail.com；不要重填。目標對象／資料安全有填寫及預覽圖，但最終儲存待核對。
- Google已管理App簽章；已簽AAB上傳成功並發布內部測試，勿更換App簽章或使用debug金鑰當上傳金鑰。
- 未簽AAB：_private/play-preparation/goo-blaster-v0.9.80-98001-unsigned.aab，98001／0.9.80-rc.1。
- AAB SHA 7d8f7be37fd1ff5a5517a0d85e422ac2783b5f2601d47bd6f408e97e6a5416d6；candidate.json／candidate-manifest.xml。
- bundletool1.18.3 validate PASS；實際API36、debug=false、full、HTML一致、無.so／簽署，測試Gradle已還原。
- 使用者10月1日明確授權金鑰／簽署，native/sign_play_candidate.ps1已實跑；已上傳。金鑰在使用者目錄.goo-blaster-signing，PKCS12／DPAPI／限定ACL，異地備份尚未完成，見其中BACKUP-README.txt。
- 已簽_private/play-preparation/v0.9.80-98001-play-signed.aab；SHA948b7409f4680a8bdaffc6c7891676ed817fabbf0c0a7793867aa9b04958bef5。
- 憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；jarsigner strict／bundletool／manifest與原始ZIP逐項比對PASS，只新增三簽章檔。signed-candidate.json記錄。
- 詳細素材、證據及後續步驟：store/google-play/README.md、listing.json、testing-plan.md。

## 未執行與下一步
- 使用者截圖確認10月1日10:50發布0.9.80-rc.1 Internal Test；名單1位，Pixel已從Play安裝98001。下一步既有Alpha封測；不是正式發布。商家帳戶／US$1.99仍待核對。
- 客服改用demjaholding@gmail.com；商店／公開隱私政策同步尚未完成。不得將使用者截圖內私人電話／地址寫入Git。
- 此個人帳戶Console實際要求12名測試者持續14天，目前0位；自動測試／GitHub APK不替代。
- Pixel私人空間舊97100/debug簽章阻擋Play安裝；使用者明確允許本次移除，先備份及隔離還原PASS後才移除。此例外不擴及日後更新。
- Pixel Play98001實測啟動／關閉重開後匯出碼與舊備份逐字相同（第1關、0幣）；實際APK內HTML SHA同v80。證據_private/pixel-play-migration/migration-verification.json；完整資料及備份碼同目錄勿提交。
- Play實機簽章SHA256 57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9；不同於debug及uploadkey。真機離線／政策連結／完整手感尚未驗證。
- Surface依既定限制未全平行，CPU4不冒充全平行；市場與母語潤稿未驗證。
- 單代理，不新增玩法／投廣告／招募私訊／正式送審；以已保存草稿接續，不重做發布。
