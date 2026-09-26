# GOO BLASTER 精簡交接

## 目前任務（2026-09-26，進行中）
- 使用者要求重新研究雜亂介面：點田地後植物選項要就近出现，其他工作也需重新排版。
- v0.9.76已實作，尚未發布；分支codex/soft-world-ui，單一代理。
- 最終HTML SHA 62af7c7fa665bdb0da759d8d565d83176381ba50746e98f9160c0a91785b72cc。
- v75已完成三平台交付，不重做；遊戲基準3b76d1b。
- .codex-remote-attachments為使用者附件，禁止提交；私密收據／存檔／憑證仅_private。

## 本次實作
- 田地／小屋操作改為就地popover，作物圖示＋時間／產量；取消／外側／Escape關閉。
- 廚房／委託／佈置為聚焦工作頁，固定分類列；主題挑战由首頁地標進入。
- 寬螢幕任務與村莊並排，鏡頭初始比例適配；保留11語言／原音樂／存檔／倒數及所有平衡。
- 其他田地成熟時保留所選植物與焦點。關閉文字使用既有cancel，避免back繁中誤為回主畫面。
- docs-20-garden-layout.md記研究、實際操作與量測；AGENTS新增26節。
- 同條件390×844：v75點田地自捲477px且種植鍵被底導覽遮住；v76自捲0px，按鈕可見。
- 前後量測_private/test-artifacts/context76-comparison.json，基準從git 3b76d1b取出。
- native/capture_garden_context.py產25張QA圖，manifest逐張標fixture／SHA；高屋等級不是玩家進度。
- store/screenshots/v0.9.76另有8張首頁／主題圖；兩manifest均已核對最終SHA。
- 真實Chrome本機實際點田地→種植→倒數／焦點返回，已通過；也檢查商店和設定，無同類遠距操作問題。

## 測試進行狀態
- 新增py_garden_context，44語言／尺寸、無選取捲頁、界線／44px／Escape／頁面隔離／離線／成熟邊界焦點。
- 既有庭院測試改用作物按鈕；festival／feedback／music測試入口改首頁地標。原機制門檻保留。
- 早期131827三FAIL已修手機分類排版與倍率說明，131941三項PASS。
- 132252診斷全項PASS但中途改SHA，不當驗收。
- 132500完整批次因取消文字修正中止，已終止該批次程序樹；不拼接其結果。
- 最終完整83項：_private/test-runs/20260926-133204-906479-context76-verified-full/results.json。
- jobs2；py_ui_fixes初輪HUD項FAIL：300ms時pause0×0、MUTE初始化114。測試改等可見非零HUD，135414-140336-context76-hud-retry已PASS，遊戲SHA未改。
- validate_reports已合併83/83，保留初輪82PASS／1FAIL；最後獨立效能44.0→43.7FPS（-0.7%）PASS。
- CPU4 135430-623550-context76-cpu4四項全PASS；release_smoke離線／新存檔／真實瀏覽器重開還原PASS，0JS錯誤／外部請求。
- py_test9第一關46秒、第二關59秒通關，第三關85秒陣亡為觀察；第一關硬門檻通過。
- 環境GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。
- Surface不跑全平行；CPU4不替代全平行。效能單独、勿與Android建置並行。

## 下一步與交付
- 程式／截圖／測試已核對，接著提交及建置APK；尚未發布。
- 檢查diff，commit Summary：v0.9.76: keep garden actions beside their objects。
- 已授權完成APK→itch公開→Pages→中英Devlog→介紹／截圖／原論壇首文→清理。
- 待發布文案_private/mobile-test/notes76-draft.json；不要在公開遊戲前宣稱已上線。
- 論壇原首文17090045仍v64；本次診斷找到安全替換：contenteditable先Control+Home、Control+Shift+End，確認選取全文，再Backspace，DOM只剩1字元且hidden body空，再paste HTML。fill空字串無法清除，勿沿用。
- 論壇診斷未Save，已reload還原公開原文；須v76公開後再原地更新，不另發留言。原文有3張combat圖需保留。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test，目前仍97500；本次adb devices沒有裝置。
- 既有25個AccessDenied清理殘留不更改ACL；先盤點再Apply，保留最新與上一版、存檔、簽章和證據。

## 範圍限制
- 真人易用性、聽感、市場需求、母語潤稿、真機長時效能尚未驗證。
- 不招募／發訊息／投廣告／改價／啟用多代理；不以自動化測試宣稱市場驗收。
