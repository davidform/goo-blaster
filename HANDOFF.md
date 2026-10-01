# GOO BLASTER 精簡交接

## 目前任務（2026-10-01）
- 使用者影片：庭院標題上滑被裁掉；最新要求所有遊戲頁面免上下捲動，內容放不下改用自然的分頁／視窗。
- 分支codex/soft-world-ui；接手時v81已完成交付，git pull --ff-only已同步。
- v82準備提交／未發布，BUILD v0.9.82；只改排版，戰鬥、資源、作物倒數與存檔不變。
- 預定Summary：v0.9.82: keep game screens fixed with adaptive page navigation。
- 最新HTML SHA 0e00482770105e320d9f44d59bd96772ceeacf2797c814dff4948dbcff0b0d77。
- 根因及中途失敗見docs-14-history.md v82節；AGENTS第29節更新免捲動要求，取代舊商店捲動規格。
- 單代理；Surface最多2個測試工作，效能單獨跑，不與Android建置競爭。不要另開代理。

## v82 實作與現況
- 固定標題／分類／底部導覽；長清單按高度翻頁；冒險10章、每頁5關；故事／補充說明另開同風格視窗。
- 庭院種植任務與場景自適應分頁；佈置工具與放置區在同頁；小場景田地按鈕分開避免重疊。
- 短橫向分類在左側；挑戰進行／完成／失敗分別排版；已套用主題的還原鍵留在挑戰說明頁。
- showFolioItem讓套用主題直接看到場景，從料理前往種植直接看到操作卡；修正保留舊頁碼的跨頁問題。
- i18n/build_v0982.py產生11語言頁碼／說明與短分類文字；預設英文不變。
- 新tests/py_no_scroll.py與py_screen_states.py列入完整90項；ui_pages.reveal透過真實頁碼按鈕取得項目。
- 多支既有UI測試改為翻頁操作，保留功能斷言。py_ui_fixes舊捲動規格改為頁面固定、所有強化與50關可達。
- store/screenshots/v0.9.82/bounded-screens-manifest.json：14張實際離線新存檔瀏覽器UI截圖、393×759／2倍像素，同上述SHA；非Pixel。
- 已目視冒險、田地旁選單、池塘、庭院／強化；正式宣傳仍保留既有三張真實戰鬥主圖優先。
- 已準備store/devlogs/v0.9.82-notes.json及store/google-play/release-notes-v0.9.82.txt，尚未發布。

## 驗證狀態
- 最終完整90/90 PASS，source_unchanged=true：_private/test-runs/20261001-232659-044921-pages82-final/results.json；不可把未完成當PASS。
- 命令 .venv/Scripts/python.exe run_tests.py --jobs 2 --label pages82-final。
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- 同SHA針對性2/2 PASS：20261001-232424-352982-pages82-target-fix（py_ui_fixes／py_screen_states）。
- v81對照實跑在Garden page scrolls and loses its heading失敗：_private/baseline81-pages/regression.log。
- 第一完整診斷20261001-230512-599900-pages82-full已停止，因跨頁定位修正使HTML變更；不能用於發版。87項PASS、py_ui_fixes舊規格FAIL，test9及獨立效能未結束；保留原紀錄。
- 更早prototype／flow／interaction／review／edges診斷均保留；曾有來源在跑測試時變動，不能當最終門檻。
- CPU4四項4/4 PASS：20261001-235137-009774-pages82-cpu4；no_scroll 373秒，來源未变。離線新存檔／重開PASS：_private/test-artifacts/release-smoke-v82.log。APK-AAB／公開平台驗證待執行。

## 既有交付與下一步
- v81已交付勿重做：遊戲5471adf、建置修正c9d3eff均已push；完整88/88及CPU4／離線證據見歷史。
- v81 APK98100，固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test；公開SHA與原debug簽章已核對。
- v81 itch2046126／upload19167726 Active；Pages378329b／Actions36855904052已成功，公開SHA及啟動／暫停已驗。
- v81 Devlog1685212、商店／原公告17090045／profile正文及圖片同步完成，收據store/page-sync/v0.9.81.json。
- 等最終90項完成，針對失敗查根因；同SHA可retry，HTML變更必須重跑整套。再CPU4、離線重開與最後截圖確認。
- 更新本檔／歷史，審diff後commit/push本次檔案；附件.codex-remote-attachments、_private、金鑰／存檔不得提交。
- 按native文件建置並稽核APK／AAB，固定Android測試通道、itch、Pages、Devlog、介紹／截圖／原論壇及profile同步。
- v81候選／簽署與APK發布收據已複製至_private/play-preparation/v0.9.81-receipts及_private/mobile-test/v0.9.81-receipts，避免新建置覆蓋證據。
- 完成公開驗證後才cleanup dry-run／Apply；保留最新與上一版APK、進度／私鑰／備份／證據。

## Google Play 與 Pixel
- app4976029382108915574／com.demjastudio.gooblaster；US$1.99、目標9歲以上成人，不重建App或換簽章。
- IARC使用者10月1日10:04截圖確認完成；通知demjaholding@gmail.com。商家由本人處理，價格最終儲存／客服政策同步仍待核對。
- v81 AAB98101／0.9.81-rc.1已簽署、驗簽／bundletool／manifest／ZIP比對PASS；signed-candidate.json archived。
- v81簽包SHA973d7f134539c7108de5db5ce47c27e7201211186e4bc886ec78f05d55a89db5。
- 沿用既有上傳金鑰，憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；異地備份未完成。不得建立新key。
- Console目前0.9.81-rc.1 Internal Test有效／提供給內部測試人員，track4701357753096403615／release2；本次只讀重新確認。
- 內測連結 https://play.google.com/apps/internaltest/4701357753096403615。
- 未正式上架；Alpha4700117103530327117的12人持續14天尚未開始，內部名單1位不等於封測。
- Pixel私人空間debug版曾阻擋Play，經一次性明確授權／備份還原驗證後已改由Play安裝98001，詳_private/pixel-play-migration；不得重做卸載。
- Play交付憑證57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9，與debug／upload憑證不同。
- 本次adb清單無裝置；不得把debug APK覆蓋Pixel的Play版，不卸載／清資料。v81／v82 Play真機版面與更新存檔尚未驗證。
- 手機未連線仍交付固定測試入口；已有Play安裝者須走Play內測更新，不能用GitHub debug APK混裝。
