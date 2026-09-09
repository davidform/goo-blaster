# GOO BLASTER — 目前交接
更新：2026-09-09；詳細紀錄 docs-14-history.md，工作室流程 studio/README.md。

## 接手與授權
- 完整讀 AGENTS.md／本檔，核對 Git 差異／實际BUILD；安全同步，不 reset 覆蓋。
- 繁體中文、預設單一agent；多agent需先確認，沒有新增授權。
- 分支 codex/soft-world-ui；可commit/push本次檔案，正式Pages僅main觸發。
- 遊戲單HTML、零執行期依賴、離線、預設英文、11語言；一次只改一項平衡變數。
- 三輪實跑；效能單獨、不與其他瀏覽器／Gradle競爭CPU。
- Surface曾因48工失去回應，本機不重試全平行；2工＋CPU4不可冒稱全平行通過。
- 手機透過固定Prerelease下載；不以USB為前提。既有授權涵蓋最終測試APK分發。
- 保留appId／簽章、增加versionCode；勿卸載／清資料。正式Pages／itch／商店／AAB／價格／私鑰操作未授權。
- US$2.99一次買斷、家庭受眾，無付費隨機／廣告／FOMO；私人簽章不入Git。

## 目前任務：使用者新增八項要求
- ① 暫停／聲音重疊；② 遠方寶箱提示不清楚；③ 越強敵人稍慢並有敵種差異。
- ④ 糖果屋太快MAX；⑤ 主畫面關卡從親切可愛→陰森→地獄末日。
- ⑥ 每關故事與11語言；⑦ 核彈發射演出；⑧ 每5關Boss外貌不同、越後越恐怖。
- 已採用：v49先修HUD；v50單獨改普通敵人移速；v51單獨調商店高階價格；v52整合世界／故事／發射／Boss純演出。
- 不得因v49完成就停止整個八項任務；仍須序列完成後續版本與最終APK。

## 當前來源與驗證
- BUILD v0.9.50；SHA 4e84f759de441ac33d0e538a1e2b166177f86b8e108eba37cb8193bef810476b。
- v49：右上兩個44px DOM按鈕共用flex橫列、12px間距；遠方箱八方向分組＋箱型＋數量。
- `_private/test-runs/20260909-135759-427624-field-ui-final/results.json` 57/57 PASS；單局有同伴46.1FPS，同批相對-0.6%。
- 邊角 tests/py_field_ui.py 四視窗×兩安全區真實點擊；24箱→8標×3。
- CPU4 field-ui-cpu4.log；離線／新存檔／冷啟動 field-ui-offline.log；證據在_private/test-artifacts。
- 已檢視field-ui-v49.png。初次完整批次因截圖發現統計遮擋中止，完整重跑通過；不能算初次全綠。
- 橫向多箱標可能擁擠，v52整合時補檢；Pixel真實安全區仍待手機驗證。
- 環境：.venv/Scripts/python.exe、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules、PYTHONUTF8=1。
- run_tests.py --jobs 2；node test9連續闖關會跑數分鐘，v49花447.2秒並通過，勿把無stdout當掛死。

## v50本次完成與後續草稿
- v50已完成：新強度／移速規則，第一關保留43.83；末關各敵型30.68／61.37／38.60／47.51。
- v50完整初輪57/58；舊基準表引用失敗，另發現py_balance吞100關例外。修工具後2/2補驗證，合併58項通過；CPU4／離線通過。
- v50完整20260909-142237-869825-enemy-weight-full，補測20260909-144428-666138-enemy-weight-recheck；單局48.0FPS。
- 16個固定完成bot A/B：第9關zero：0/2→0/2；第9關max：2/2→2/2；第50關zero：0/2→0/2；第50關max：0/2→0/2；有限樣本不等於真人勝率，詳late-speed-ab.json。
- edit51.py／py_shop_pacing.py：前兩級原價、高階倍率[1,1,2,2.5,3]，保留舊MAX存檔與收入。
- world-presentation.js／edit52.py／story_builder.py／py_world_story.py：十章插畫、50組章節／推進短篇×11語言、Boss護盾尖牙與核彈演出。
- v51價格草稿未套用；v52曾在_private/world-preview執行視覺草稿檢查（550故事／十Boss／發射），但最新草稿仍須正式套用後完整驗證。
- 後續i18n builder要移至i18n，測試移至tests並註冊run_tests.sh；各版各跑完整套件。

## 前版與未解問題
- v48 fdeff02已修戰報：原生ACTION_CREATE_DOCUMENT、PNG寫入、成功／取消／失敗提示；56/56＋CPU4／離線＋Java編譯／APK稽核過。
- v47 c1167c3已修永久射程實效；原生持久層與新版覆蓋更新仍需Pixel確認。
- v47固定63個完成bot樣本：1／6／7皆3/3；9／10／30零強化0/3、沿前10關收入／滿級3/3；50所有組0/3。
- 這是固定bot結果，不是人類勝率；會漏寶箱／核彈、Boss離畫面；末章難度未宣稱解決。
- v49前商店總成本8930、單局含幣增益上限520；再生2/4次、救命卡加權、綠殼第9關不變。
- 11語言結構／參數／語境／版面已測，但尚無母語者／兒童理解度研究。

## 固定手機測試入口（仍為v48，等本次整合）
- https://github.com/davidform/goo-blaster/releases/tag/android-test
- 公開v0.9.48／94800／0.9.48-test.0；appId com.demjastudio.gooblaster。
- APK4270375bytes，SHA 5df277d0cbced790d4f07e98b3661730288fcd2caf71dece1f16d8454ea50f2b。
- 同舊簽章；native/test-channel.json固定公開指紋，_private/mobile-test/latest.json與published.json含稽核。
- 依native/MOBILE-TESTING.md：最終測試完成並提交→build_test_apk.py --tests <報告>→notes.md→publish_test_apk.py --publish。
- Pixel待驗：實際PNG可開、取消重試、更新保存進度、聲音／卡頓／新HUD；舊v40曾驗持久層不代表新版。
- 目前AAB仍v40未簽；正式Pages／itch／商店未更新。工作室skill已安裝，8項工具測試＋官方驗證過。
