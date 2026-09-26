# GOO BLASTER 精簡交接

## 任務與現況（2026-09-26）
- 使用者要求依參考圖，把遊戲主頁改成俯視小鎮感覺；v0.9.74已完成實作、驗證與三平台交付。
- 分支codex/soft-world-ui；只修改首頁視覺與既有入口，不改戰鬥／倒數／存檔格式／價格。
- HTML SHA 9dd5e83dab40cc196e9767d430abcd7413965dec3fd86c610c16e0e1b9c27f15。
- 單一代理；.codex-remote-attachments為使用者附件，禁止提交。存檔／憑證／精確後台數字僅_private。

## v74首頁
- 原創單檔SVG場景：道路、河流、橋、田地、房舍與6位散步居民。
- 六入口：冒險城門→關卡詳情、糖果屋→強化、庭院→種植、野餐／池塘／星光→相應挑戰選擇。
- 金幣／種子／花瓣讀真實存檔；原關卡路線、故事、開始遊戲及底部導覽保留。
- 使用既有11語言字典，CSS動態不消耗戰鬥RNG，離開首頁暫停，支援減少動態。
- 範圍是6地標小鎮，不宣稱達到參考圖建物數量／像素精度，未新增經營系統。
- 截圖store/screenshots/v0.9.74；native/capture_town_home.py可再產生，原圖／縮圖已目視。
- 語言截圖需applyLanguage後renderStage，符合實際語言按鈕；單改字典不會重畫首頁。

## 測試證據
- 全套82項：_private/test-runs/20260926-081927-994272-town74-full/results.json，jobs2，完整／同SHA。
- 初輪73PASS／9FAIL：1項l10n滑動的旧第一屏假設，8項Node缺NODE_PATH未啟動；原紀錄保留。
- 滑動修正測試先定位實際說明文字，驗證真實touch增量>20與開始按鈕可見；083036-town74-swipe-retry PASS。
- Node補驗：_private/test-runs/20260926-083510-437346-town74-node-retry/results.json，8/8 PASS；與原完整＋滑動補驗合併82/82。
- NODE_PATH須設為本專案_private/test-node/node_modules；GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1。
- 新tests/py_town_home.py：六入口／導航不改存檔／44語言尺寸／44px區域／最大值／減少動態，已列入全套。
- focused：082454-town74-translated-edges PASS；CPU4：082550-town74-translated-cpu4 PASS。
- tests/py_release_smoke.py PASS：新progress1／coins0／meta{}，CPU4、離線、重開還原，0JS錯誤／0外部請求。
- 效能最後單獨PASS：無同伴42.7／有同伴44.5FPS；未降低門檻，不把當批+4.3%宣稱為優化。
- py_test9第1／2／3關48／62／113秒通關；第1關仍為硬門檻。
- Surface不跑全平行（曾無回應），CPU4不取代全平行；建置不能與效能並行。

## 交付進度
- v74已公開，合併82/82；遊戲commit 2d0e2a3已push：v0.9.74: turn the home screen into an interactive candy town。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test
- APK97400／同簽章／公開下載SHA 3a1631475f8e9763e3c21d7e3a3fcec0b72d63d50d311cc01b1f5a919f9c8ba2。
- itch build2017752／upload19167726，原遊戲payload完全一致（僅平台附加script），實際開始／暫停通過。
- Pages 0c486a55b64130e8b8d3560671cde39ec2e82d0d，Actions36205898857成功；完整SHA與開始／暫停通過。
- 中英Devlog1677436已Published並record；tests/test_devlog_workflow.py九項PASS。
- 收據_private/mobile-test/itch-v74.json、pages-v74.json、published.json、devlog-v74-receipt.json。
- 公開介紹v74／六地標已核對；新圖30261011排第四，前三戰鬥及歷史圖片保留；store/page-sync/v0.9.74.json。
- Pixel本次adb devices沒有裝置；最後驗證v71／97100。不卸載／清資料，不宣稱手機已更新。
- 論壇原首文17090045及個人頁引用仍v64；本次select/type替換仍插在舊字前，重新載入還原未存。未完成，不發新回覆取代。
- cleanup_local.ps1盤點及Apply完成，釋放13,488,053 bytes；保留v74與v73回退、全部存檔及簽章。25個AccessDenied未清理，不改ACL。
- 合併收據／核對／清理命令曾被自動核准拒絕（只給blocked by policy）；改成明確檔案patch與分開核對／盤點後完成，沒有繞過權限。

## 後續限制
- AGENTS第24節記錄新授權；首頁工作取代第23節對本項的停工，不擴及其他新功能。
- 市場需求仍未驗證；docs-19-market-review.md與store/research/player-study-kit.md已備妥，不生成假訪談。
- 未招募／發訊息／投廣告／改價／啟用多代理；真人聽感、真機長時效能、回訪／付費意願與母語潤稿未驗收。
- 原先25個AccessDenied暫存保留，不改ACL；不能宣稱全部清理完成。
