# GOO BLASTER 精簡交接

## 目前任務（2026-09-26，已交付）
- 使用者要求重新研究雜亂介面：點田地後植物選項要就近出现，其他工作也需重新排版。
- v0.9.76已實作並完成三平台交付；分支codex/soft-world-ui，單一代理。
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

## 交付與下一步
- 遊戲commit35d793ed0b16924715dbaec83b6477a0b98153e3已push；Summary：v0.9.76: keep garden actions beside their objects。
- APK97600／0.9.76-test.0，同applicationId／簽章；公開下載SHA 582dfec36b5b56ae040e1f1a69e39641d7dc1c1b1970ae904289186e7c90b146。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test；asset590052403。Pixel本次無ADB裝置，未覆蓋安裝；不卸載／清資料。
- itch build2018613/upload19167726，公開完整payload及實際種植卡／廚房／開始暫停驗證，收據_private/mobile-test/itch-v76.json。
- Pages部署d1b43724e1a619db94dc606d0ead19fb97fe02ad，Actions36222857750成功；完整HTML SHA及實際開始／暫停通過，pages-v76.json。
- 中英Devlog1677628已Published並核對完整正文／附件；store/devlogs/v0.9.76/post.json已record，工作流程9項PASS。
- store/page-sync/v0.9.76.json：介紹及圖庫已公開；前三張戰鬥圖保留，第4張30265118種植、第5張30265119庭院；24張歷史圖均保留。
- 論壇原首文17090045已從v64更新v76，離線倒數／操作說明修正，保留3張combat加1張新庭院圖；個人頁引用同時核對，未另發留言。
- 論壇編輯教訓：HTML貼上會變純字串；clipboard HTML亦未保留格式。最終reload原文，selectText精確選句→Backspace→輸入，逐段核對，保留圖片。不要整份fill或盲信貼上；某次typeText追加未取代，提交前已清除重複。
- cleanup先盤點再Apply，釋放13,477,703 bytes，2項刪除／0失敗，25個AccessDenied略過不改ACL；保留v76與v75 APK、存檔、簽章、證據。
- 本次排版實作／可運作發布項目已完成；下一步為使用者在手機確認新版操作體感，勿重做已完成發布。

## 範圍限制
- 真人易用性、聽感、市場需求、母語潤稿、真機長時效能尚未驗證。
- 不招募／發訊息／投廣告／改價／啟用多代理；不以自動化測試宣稱市場驗收。
