# GOO BLASTER 精簡交接

## 目前任務（2026-10-02）
- 使用者影片：庭院標題上滑被裁掉；最新要求所有遊戲頁面免上下捲動，內容放不下改用自然的分頁／視窗。
- 分支codex/soft-world-ui；接手時v81已完成交付，git pull --ff-only已同步。
- v82已完成驗證與平台交付，BUILD v0.9.82；只改排版，戰鬥、資源、作物倒數與存檔不變。
- 遊戲commit 9e99161（已push）；Summary：v0.9.82: keep game screens fixed with adaptive page navigation。
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
- Devlog1685583已Published；商店介紹／三張新截圖／原公告17090045及profile已同步，收據store/page-sync/v0.9.82.json。

## 驗證狀態
- 最終完整90/90 PASS，source_unchanged=true：_private/test-runs/20261001-232659-044921-pages82-final/results.json；不可把未完成當PASS。
- 命令 .venv/Scripts/python.exe run_tests.py --jobs 2 --label pages82-final。
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- 同SHA針對性2/2 PASS：20261001-232424-352982-pages82-target-fix（py_ui_fixes／py_screen_states）。
- v81對照實跑在Garden page scrolls and loses its heading失敗：_private/baseline81-pages/regression.log。
- 第一完整診斷20261001-230512-599900-pages82-full已停止，因跨頁定位修正使HTML變更；不能用於發版。87項PASS、py_ui_fixes舊規格FAIL，test9及獨立效能未結束；保留原紀錄。
- 更早prototype／flow／interaction／review／edges診斷均保留；曾有來源在跑測試時變動，不能當最終門檻。
- CPU4四項4/4 PASS：20261001-235137-009774-pages82-cpu4；no_scroll 373秒，來源未变。離線新存檔／重開PASS：_private/test-artifacts/release-smoke-v82.log。APK／AAB／公開平台驗證亦完成，見下節。

## v82 交付與下一步
- v81既有發布勿重做；v82遊戲9e99161已push，HTML維持上述SHA，48檔已提交。
- APK98200／0.9.82-test.0，原debug簽章與force邊界設定核對，公開重新下載SHA PASS。
- APK SHA cd1e625b437b0cc3d314476c6efdf337bda29991b2fd0675fe1c41c10bc82101。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test；latest.json／published.json位於_private/mobile-test。
- itch2047274／upload19167726 Active；完整payload與平台suffix吻合，公開v82啟動／暫停通過，itch-v82.json。
- Pages8e009276／Actions36889382603成功，公開HTML完整SHA與開始／暫停PASS，pages-v82.json。
- Devlog https://davidform.itch.io/goo-blaster/devlog/1685583/v0982-turn-pages-keep-your-place；正文中英／Published及9項工作流程驗證PASS。
- 商店前三張戰鬥圖保留，新图30439741／30439740／30439739接於其後；論壇及profile各9張實際載入成功，舊連結／圖片保留。
- cleanup先dry-run再Apply：2項／13,446,234 bytes，0失敗、25權限拒絕略過；保留v82／v81 APK與進度／金鑰／備份／證據。
- 未執行：全平行與Pixel新版真機驗收；下一步從Play更新確認安全區、各頁翻頁及重開存檔。不卸載、不混裝debug APK。
- 本次附件.codex-remote-attachments與_private不提交。發布收據與前版備份保留，不重建key／不重做已通過測試。

## Google Play 與 Pixel
- app4976029382108915574／com.demjastudio.gooblaster；US$1.99、目標9歲以上成人，不重建App或換簽章。
- IARC使用者10月1日10:04截圖確認完成；通知demjaholding@gmail.com。商家由本人處理，價格最終儲存／客服政策同步仍待核對。
- v82 AAB98201／0.9.82-rc.1已簽署、驗簽／bundletool／manifest／ZIP比對PASS；signed-candidate.json；原ZIP內容0變更，新增3項簽章。
- v82簽包SHA749c47e030bdc6cae4074030ecafd3fcaaff6ee932af69b567458a012fb4666d。
- 沿用既有上傳金鑰，憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；異地備份未完成。不得建立新key。
- Console 10月2日00:09顯示0.9.82-rc.1 Internal Test有效／提供給內部測試人員，track4701357753096403615／release3。
- 內測連結 https://play.google.com/apps/internaltest/4701357753096403615。
- 未正式上架；Alpha4700117103530327117的12人持續14天尚未開始，內部名單1位不等於封測。
- Pixel私人空間debug版曾阻擋Play，經一次性明確授權／備份還原驗證後已改由Play安裝98001，詳_private/pixel-play-migration；不得重做卸載。
- Play交付憑證57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9，與debug／upload憑證不同。
- 本次adb清單無裝置；不得把debug APK覆蓋Pixel的Play版，不卸載／清資料。v82 Play真機版面與更新存檔尚未驗證。
- 手機未連線仍交付固定測試入口；已有Play安裝者須走Play內測更新，不能用GitHub debug APK混裝。
