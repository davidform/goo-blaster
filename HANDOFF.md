# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者認為庭院單調，要求繼續發揮並讓不同主題顯示不同且相關的動態圖示。
- v0.9.70已實作三主題挑戰／成就／場景與動態入口；完整78/78、CPU4、offline與獨立效能已過，正在發布。
- 分支codex/soft-world-ui，接手eeb28a0，pull已最新；附件.codex-remote-attachments不可提交。
- 來源SHA c4f376c1544f42c955e10ee334f5b4e8ba34c04ce2bcdf8333f0b72257df2aa1。
- 預定Summary：`v0.9.70: add themed village challenges and animated icons`。

## 已實作／固定決策
- 村莊小冒險：野餐記憶3/4/5道料理；池塘5×5三珍珠到旗幟，步數最短路＋4/2/0；星光3×3相鄰翻轉、無步數限制。
- 三種玩法各三階，成功後重玩改序列／旋轉／打散；免費、失敗不扣材料、不加戰力、不限每日次數。
- medals/outings/theme存檔，舊存檔零／原庭院；徽章解鎖主題，更多徽章增加裝飾，完成防重複領取。
- 野餐旗幟與餐盤／游魚池／星燈夜色；種植搖葉、廚房蒸氣、建設小槌、居民跳動、游魚與星光SVG。
- 遵守減少動態設定，單檔離線；29key×11語言，預設英文。
- 新挑戰無被動等待；作物倒數、建設即時完成、料理／修屋成本保留。戰鬥段逐字比對相同。
- 既有v69生產／訂單／六建設不改，全部等待顯示时间規範見AGENTS第20節。
- 不是農場動物／地圖擴張，不能宣稱已證明長期留存或付費吸引力。

## 測試證據
- 初輪timer/i18n 2/2，festival-loop九挑戰21.1s；舊SHA，僅歷史。
- 最終SHA edges5/5：cjk12.6/world12.2/layout27.1/village25.8/festival24.2秒。
- 完整回歸_private/test-runs/20260921-224139-214971-festival70-final/results.json，78/78 PASS無補跑。
- CPU4 _private/test-runs/20260921-224444-799807-festival70-cpu4/results.json：3/3過，world124.2/timer26.0/festival431.0秒。
- offline smoke已過：0JS錯誤/0外部請求，CPU4、重開progress9/coins456/dmg2/selection8保留；_private/festival70/offline.log。
- 新test py_garden_festival：九次UI解題、免費重試/錯誤輸入/重複完成、保存/重開/備份/合併、99語系尺寸版面、減少動態。
- 新手py_test9第1關58秒2/3心通關、第2關58秒滿心；第3關102秒陣亡，非硬門檻；0JS錯誤。
- 截圖native/capture_garden_festival.py與store/screenshots/v0.9.70。明示可達成fixture，真實操作後畫面，非真人紀錄／Pixel測試。
- 全平行未跑（Surface限制），ADB空，Pixel未安裝／效能未驗證。彙整_private/festival70/verification.json。

## 待交付
- 完整78/78與獨立perf66.6s通過：單局58.5FPS、同伴-1.0%；非Pixel。已可commit/push與封裝。
- Android固定測試通道同簽章；itch html5公開完整payload/啟動；Pages指定commit/Actions/公開SHA/啟動。
- store/page-sync/v0.9.70-description.html與store/devlogs/v0.9.70-notes.json已備妥。
- Chrome編輯tab1912753951已填v70介紹且未Save；勿操作使用者舊編輯tab1912753587。完整驗證後才發布。
- 新pond-play-en.png放第4張，保留前三戰鬥與历史相簿；尚未上傳。Devlog查文章/草稿再發布。
- 最後依白名單清理、更新收據、交接與文件commit。

## 其他未完成
- 原論壇首文v65自動核准拒絕仍待明確授權，未重試。
- 動物／更多料理／多區域／居民生活AI、母語潤稿、真機長時FPS及玩家耐玩性驗收未完成。
- 舊25個拒絕存取測試profile保持原狀，不改ACL；玩家進度、簽章與備份不可刪。
