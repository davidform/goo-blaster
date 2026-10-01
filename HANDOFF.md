# GOO BLASTER 精簡交接

## 目前任務（2026-10-01）
- Google Play 上架準備；使用者定價 US$1.99、目標 9 歲以上與成人。尚未送審／正式發布。
- 使用者會自行完成商家帳戶；不可代填收款／稅務／身分。Console 價格尚未儲存。
- 分支 codex/soft-world-ui；遊戲 commit 8edd22063eccf79e2d24fc3bd95a64997c963d3c 已 push。
- Summary：v0.9.80: add a privacy policy entry in settings。
- HTML SHA a70daa8c6c507d3584a414152220e4141d25a81fab7253ec0271b9a335f79217。
- 附件 .codex-remote-attachments 不提交；私人產物只放 _private。勿重做已完成的 v79／v80 發布。

## v80 範圍與驗證
- 設定新增隱私政策網站入口，11 語言；另頁開啟、原遊戲保留。政策補庭院存檔與 9+ 定位。
- 不改玩法、倒數、存檔格式與預設英文。i18n/build_v0980.py；tests/py_privacy_entry.py 已納入全測。
- 完整 87/87 PASS：_private/test-runs/20260929-194400-848598-privacy80-full/results.json。
- 命令：.venv/Scripts/python.exe run_tests.py --jobs 2 --label privacy80-full。
- 環境 PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- test9 第 1／2／3 關 57／60／89 秒通關；效能獨立 49.2→52.3 FPS（+6.4% 量測波動）。
- CPU4 privacy／bottomnav 兩項 PASS：_private/test-runs/20260929-200922-480275-privacy80-cpu4/results.json。
- 離線／新存檔／真實關閉重開 PASS：_private/play-preparation/release-smoke-v80.log；0 錯誤、0 外部請求。
- 新隱私測試 44 版面、真實點擊、48px／無溢位／存檔不變；v79 對照實跑缺入口 FAIL，_private/baseline79-privacy/regression.log。
- 截圖 store/screenshots/v0.9.80 已目視；本機 popup fixture 不冒充原生實機。

## 已交付
- APK 98000／0.9.80-test.0，既有簽章不變，公開重新下載核對。
- APK SHA 915aa00110f0c441259dc70f1ef8e9a98e1e32ce53e776fecb3713fef23d4858。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test。
- itch build2035680／upload19167726 Active；公開完整 HTML 與平台附加腳本核對，開始／暫停 PASS；itch-v80.json。
- Pages 3db64d5350080c98ad89035f86f876a5e2738a0c、Actions36568248919 成功；公開 SHA／開始暫停／另頁政策 PASS；pages-v80.json。
- Pages 初次載入逾時，reload 後成功；原始紀錄保留。
- Devlog1682276 已 Published、record、工作流程9項 PASS；store/devlogs/v0.9.80/。
- 商店／原論壇公告17090045／profile 已更新，兩連結及七圖完整；store/page-sync/v0.9.80.json。
- cleanup dry-run 後 Apply：移除2項釋放13,480,216 bytes；0失敗、25 AccessDenied略過。保留v80／v79 APK、進度與證據。

## Google Play 實際狀態
- 既有草稿 app4976029382108915574／com.demjastudio.gooblaster；不要重建。
- 已存隱私、存取／無廣告／非政府／非金融／非健康、Action分類與公開信箱及HTTPS網址。
- EN-US／zh-TW商店全文、圖示、主視覺、四張手機截圖已存草稿；六視覺素材AI標記已存，未送審。
- 資料安全不收集／不分享已存草稿，最終完成受目標對象設定阻擋。
- 使用者確認9–12／13–15／16–17／18+；先前9–12停用提示已不作現況依據，IARC已完成後以Console實際儲存結果核對。
- 使用者截圖確認IARC於10月1日10:04已完成、信箱demjaholding@gmail.com；不要重填。目標對象／資料安全有填寫及預覽圖，但最終儲存待核對。
- Google已管理App簽章、Console尚無上傳憑證；不要更換App簽章或使用debug金鑰當上傳金鑰。
- 未簽AAB：_private/play-preparation/goo-blaster-v0.9.80-98001-unsigned.aab，98001／0.9.80-rc.1。
- AAB SHA 7d8f7be37fd1ff5a5517a0d85e422ac2783b5f2601d47bd6f408e97e6a5416d6；candidate.json／candidate-manifest.xml。
- bundletool1.18.3 validate PASS；實際API36、debug=false、full、HTML一致、無.so／簽署，測試Gradle已還原。
- 使用者10月1日明確授權金鑰／簽署，native/sign_play_candidate.ps1已實跑；未上傳。金鑰在使用者目錄.goo-blaster-signing，PKCS12／DPAPI／限定ACL，異地備份尚未完成，見其中BACKUP-README.txt。
- 已簽_private/play-preparation/v0.9.80-98001-play-signed.aab；SHA948b7409f4680a8bdaffc6c7891676ed817fabbf0c0a7793867aa9b04958bef5。
- 憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；jarsigner strict／bundletool／manifest與原始ZIP逐項比對PASS，只新增三簽章檔。signed-candidate.json記錄。
- 詳細素材、證據及後續步驟：store/google-play/README.md、listing.json、testing-plan.md。

## 未執行與下一步
- 下一步上傳已簽AAB核對Console憑證與內部測試安裝，再既有Alpha封測；不是正式發布。商家帳戶／US$1.99待核對，不能從填寫截圖推定已儲存。
- 客服改用demjaholding@gmail.com；商店／公開隱私政策同步尚未完成。不得將使用者截圖內私人電話／地址寫入Git。
- 此個人帳戶Console實際要求12名測試者持續14天，目前0位；自動測試／GitHub APK不替代。
- ADB無裝置，Pixel未覆蓋更新；需真機政策連結／離線／進度與手感驗證，不卸載或清資料。
- Surface依既定限制未全平行，CPU4不冒充全平行；市場與母語潤稿未驗證。
- 單代理，不新增玩法／投廣告／招募私訊／正式送審；以已保存草稿接續，不重做發布。
