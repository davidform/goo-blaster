# GOO BLASTER — 目前交接
更新：2026-09-09；詳細紀錄 docs-14-history.md，工作室流程 studio/README.md。

## 接手與授權
- 完整讀 AGENTS.md／本檔，核對 Git 差異／實際BUILD；安全同步，不 reset 覆蓋。
- 繁體中文、預設單一agent；多agent需先確認，沒有新增授權。
- 分支 codex/soft-world-ui；可commit/push本次檔案，正式Pages僅main觸發。
- 單HTML、零執行期依賴、離線、預設英文、11語言；一次只改一項平衡變數。
- 三輪實跑；效能單獨、不與其他瀏覽器／Gradle競爭CPU。
- Surface曾因48工失去回應，本機不重試全平行；2工＋CPU4不可冒稱全平行通過。
- 固定Prerelease下載，不以USB為前提；既有授權涵蓋最終測試APK分發。
- 保留appId／簽章、增加versionCode；勿卸載／清資料。正式Pages／itch／商店／AAB／價格／私鑰操作未授權。
- US$2.99一次買斷、家庭受眾，無付費隨機／廣告／FOMO；私人簽章不入Git。

## 本次八項要求：實作完成
- v49 aea0d88：暫停／靜音兩個44px DOM按鈕，橫列間距12px；寶箱方向分組。
- v50 edeab83：普通敵人越強越慢，保留類型差異；只改速度，不改Boss／HP／射擊。
- v51 8144464：糖果屋高階成本8930→16250，前兩級／愛心／復活不動，MAX存檔保留。
- v52 7522f97：十章地圖可愛→陰森→火海；50關章節背景＋推進短篇×11語言，可收合閱讀。
- v52：核彈升空0.48秒後爆光／爆音，1.35秒結束；清怪、Boss免疫、2.5秒淨空仍立即生效。
- v52：十隻章節Boss各異，後期加盔甲外盾／尖牙／怒眉；不增加減傷或改血量。
- v52：補給箭頭包含核彈，八方向合併數量、稀有優先；短螢幕／橫向避開核彈鍵。
- BUILD v0.9.52；SHA 0a79ad312c1a53648a64e5a09c32a22580c1b6830625f9ea6aefc495af91e82f。

## 驗證證據
- 環境：.venv/Scripts/python.exe、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules、PYTHONUTF8=1。
- v52完整60/60 PASS：_private/test-runs/20260909-151918-794758-world-story-full/results.json；同SHA／來源未變，單局有同伴44.2FPS，相對+1.2%。
- CPU4：world52-field-cpu4.log、world52-story-cpu4.log；離線／零永久強化／冷啟動：world52-offline.log。
- 六視窗×兩安全區真實觸控；24箱／25補給幾何、550故事組合、十Boss、發射時序皆驗。
- world52-i18n-scope.json：264key×11，18新增＋2既有關名改動，builder重跑位元組相同。
- 已檢視world-scene-1..10、boss-world-5..50、world-stage-1/15/25/50、核彈時間序列、field-ui-v0.9.52.png。
- v51完整59/59：20260909-145033-416041-shop-pacing-full；CPU4／離線過，單局46.4FPS。
- v50初輪57/58；舊基準引用失敗，另發現py_balance吞100關例外。修工具後2/2補驗證，同SHA合併58項通過；CPU4／離線過。
- v50報告20260909-142237-869825-enemy-weight-full＋20260909-144428-666138-enemy-weight-recheck，單局48.0FPS。
- v49完整57/57：20260909-135759-427624-field-ui-final；CPU4／離線過，單局46.1FPS。

## 數值與未解事項
- 實際末波速度：第一關slime43.83不變；末關slime／bunny／drone／bomber為30.68／61.37／38.60／47.51。
- 舊末關速度143.65／156／156／156；本版移除舊關卡與tier加速，所以比舊版減幅大，不宜只說微調。
- late-speed-ab.json：固定16個完成A/B，第9關zero0/2→0/2、max2/2→2/2；第50關zero與max皆0/2→0/2。
- 這是有限bot結果，不是人類勝率；會漏寶箱／核彈與離畫面Boss，末關難度未宣稱解決。
- shop-campaign-ab.json：以實賺收入買戰鬥能力，前後各10場通過前10關，購買級數22→20；不等於完整50關經濟驗證。
- 商店全買成本16250；每場含幣增益3–520；理論最快32場不是實際買滿關卡。
- 既有MAX不削弱，價格無法幫助已滿級仍卡末關玩家；下一個平衡任務應另版測量末章Boss可攻擊時間／可見性等單一槓桿。
- 11語言結構／參數／版面已測，但尚無母語者／兒童理解度驗證；50故事是10章×5段組合。
- v48 fdeff02原生戰報ACTION_CREATE_DOCUMENT已編譯／DEX檢查；實際PNG儲存、取消重試仍需Pixel。

## 手機測試交付
- 固定入口：https://github.com/davidform/goo-blaster/releases/tag/android-test
- 已公開v0.9.52／95200／0.9.52-test.0，4286598bytes；來源7522f97、測試標籤同commit。
- APK SHA 5db689e8189cf7ba1135700fcd09e1703851141f8347511624fb422c0daed9ca；同舊簽章，APK內HTML同完整測試SHA，DEX戰報外掛核對通過。
- latest.json／published.json／page-v52.json：公開下載hash一致、頁面HTTP200／新版連結過；android-source-20260909-154414.zip備份80檔。
- appId com.demjastudio.gooblaster；簽章固定於native/test-channel.json，私鑰不可入Git。
- 依native/MOBILE-TESTING.md：完整通過並提交→build_test_apk.py --tests <報告>→notes.md→publish_test_apk.py --publish。
- Pixel待驗：更新保留進度、新HUD／補給方向、核彈、音效／卡頓、戰報PNG與取消重試；舊v40真機證據不能替代新版。
- AAB仍v40未簽；正式Pages／itch／商店未更新。工作室skill已安裝，8項工具測試＋驗證過。
