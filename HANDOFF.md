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

## 目前任務：升級／寶箱與後續工作
- 使用者要求重新構思升級寶箱、確認連升三級、進行下一步；已依game-studio單代理執行。
- v53已修連續獎勵顯示與歸屬：34×2XP仍升3級，標題由錯誤Lv.2／1/2改成Lv.4／1/3→2/3→3/3；XP與卡池不動。
- 舊卡事件只接受一次；Boss延遲獎勵不跨局；11語言說明已完成。
- BUILD v0.9.53；SHA 12e085900b78e800e44a765545ebe0e12ae1324a0855045eeb8d19440c33052e。
- v53完整61/61：_private/test-runs/20260909-192602-386494-upgrade-queue-final/results.json；CPU4與離線通過，單局45.0FPS；負對照v52確實失敗。
- v54火焰糖試作在_private/fire-preview，尚未套到正式index；6秒留火焰／每塊2秒／每秒24基礎傷害／重疊不加倍／只直接傷普通敵人／最多16塊。
- _private/prepare54.py從v53產生；build_v0954.py更新11語言；py_fire_trail.py已跑草稿驗證。正式套用後仍須完整／CPU／離線／APK。
- docs-15-upgrade-design.md：三種打法、十種寶箱定位與3種未實作構想。不要把後續构想宣稱已完成。
- 下一步完成v54、獨立提交，再建置最終APK到固定入口；不止於v53。

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
