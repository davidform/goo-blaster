# GOO BLASTER 精簡交接

## 目前狀態（2026-09-21）
- 當前任務：使用者認為庭院無趣；v0.9.65已在工作區加入16格自由佈置＋六位訪客願望，已完成APK／itch／Pages／Devlog公開交付。戰鬥／種植數值未改。
- 完整測試73/73通過：_private/test-runs/20260921-100707-600303-garden65-final/results.json，SHA 659113668783665bd22dd598d99a08605146cc334ea78d6330101bf22dc763eb；source_unchanged。
- 專項py_garden／py_garden_design＋CPU4／離線冷啟動／最終UI均通過；完整回歸73/73，跨平台已完成；收據見下方。首輪因工具列可達性改版而中止，音效測試絕對時鐘問題已重現並修正；_private/garden65/verification.json。
- 前批四項需求已實作並交付v0.9.64：Boss阻擋、衝刺節奏、搭配上限、糖果庭院。
- 分支codex/soft-world-ui，遊戲commit3528764d61f1747473f0b14b88e8523d1eead2f6；新接手仍先核對工作區／遠端／BUILD。
- 最終HTML SHA 659113668783665bd22dd598d99a08605146cc334ea78d6330101bf22dc763eb。
- 單代理，保留進度與購買等級。未建立背景排程，未更改價格或正式商店。

## 下一步／未完成
- 宣傳改為3張真實Boss交戰：大型Boss／裝甲Boss／怪群包圍；遊戲相簿前三張、原貼文17090045與profile均已公開核對載入，原正文保留。
- 素材store/screenshots/v0.9.64/combat/manifest.json；實際完整loop加速擷取、隔離可達成存檔，0errors、HTML SHA未變；不是真人／FPS測試。
- 相簿後方仍有3張已被取代的v64 UI圖＋5張legacy圖；Chrome Delete confirm/accept逾時未刪。勿重傳戰鬥圖；收據store/page-sync/v0.9.64.json。
- game-studio已新增市場品質標準並同步已安裝skill：技術／玩家體驗／商業呈現分別驗收，動作遊戲主圖必須實戰，檢查原圖與縮圖。
- 下一個視覺候選：Boss連續受擊變純白遮掉造型、特效遮角色、背景層次少；尚未修改，不宣称圖片更新代表已達付費品質。
- 收集Pixel上第9關以後攻擊／防禦搭配、Boss邊緣衝刺、庭院成長循環的實玩回饋，再單一變數調整。
- Pixel長時間FPS未測；Surface全平行因凍結紀錄未跑，CPU4不是替代證據；11語言母語潤稿未做。
- Windows一般工具帳戶反覆1909鎖定；提升權限檔案／Git工具可用，已啟動一般環境測試照常完成。
- 鎖定期間elevated效能8–9FPS、舊版亦低；普通環境恢復45–55FPS，未證明原因、未改Windows安全設定。
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules；jobs2，效能solo，不與Gradle同時跑。
- Git／測試APK／itch／Pages／Devlog／白名單清理授權沿用；正式商店／定價／簽章更換仍須另行授權。

## v65交付證據與限制
- Summary：`v0.9.65: add garden layout puzzles and resident wishes`（3528764）。音效測試修正7bd0b42，未改遊戲音效。
- 六個有限空間願望：立即／通過2、5、10、15、20關開放；16格五物件免費佈置，已入住居民不因重排消失。
- layout／guests走garden.rev、備份碼、原生合併；原農作／戰力數值保持。是否有趣仍需真人試玩。
- 最終bot第1/2/3關過，3/3、2/3、1/3心，僅本批樣本。獨立平均54.2FPS，有無同伴36.2→36.0，非Pixel。
- CPU4專項20260921-101118-406875-garden65-cpu4-offline；離線／新存檔／冷啟動release-smoke.log，0errors／0外部請求。
- 新增測試涵蓋六題、斜角／斷路／環形、庫存、重複入住、重排、舊資源、原生／備份、11語言×3尺寸。
- APK v65/96500/0.9.65-test.0，4311673bytes，簽章與appId一致，HTML／DEX／公開下載SHA核對。
- APK SHA db6b77467e46bd7e928eaaab84ce5c1a9b2fa9f00a2ad84c9aec6345f771c7c3；固定android-test入口。
- 本次ADB沒有裝置，未安裝v65到Pixel；上次v64才有真機安裝與存檔一致證據。
- itch upload19167726/build1999423，公開payload同SHA；實際布置／入住0→1／開始暫停，itch-v65.json。
- Pages ca1fde0fb13895a530e35c2989acc173a4aca5bd，Actions35554519239 success；公開SHA一致，CUA開始／Paused通過。
- Devlog Published https://davidform.itch.io/goo-blaster/devlog/1671547/v0965-a-garden-to-arrange-and-neighbours-to-welcome。
- 雙語全文、v65附件、庭院圖核對；devlog workflow 9/9；store/devlogs/v0.9.65/post.json。
- 遊戲頁v65介紹已公開核對；相簿前三張戰鬥、第四張新庭院30143572，四圖均載入。
- 原討論串首文v65已編妥未保存：自動核准審查拒絕公開改寫，已詢問明確授權。不要走API繞過；Chrome編輯頁保留。
- 討論串／profile目前仍v64三張戰鬥圖；新庭院圖僅遊戲頁與Devlog。
- 白名單清理刪舊v60 APK4290992bytes，保留v65/v64及全部存檔／簽章／測試證據。22舊profile拒絕存取留存。
- 圖片store/screenshots/v0.9.65為實際UI、可達成測試存檔，非真人遊玩；manifest保留來源。
- 玩家若擺完六題便不回來，下一步考慮有個性的居民互動／取捨，不堆重複收成門檻。
