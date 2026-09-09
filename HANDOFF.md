# GOO BLASTER — 目前交接
更新：2026-09-09；詳細歷史／研究見 docs-14、docs-15、docs-16。

## 接手與授權
- 完整讀 AGENTS.md 與本檔，核對 Git 差異／BUILD；安全同步，不 reset 覆蓋。
- 單一代理、繁體中文；三輪實跑、效能單獨；區分已驗證／失敗／未執行。
- Git 可自動 commit/push 本次檔案；分支 codex/soft-world-ui，Pages 只在 main push 部署。
- 使用者要求固定手機測試方式，無需 USB；往後依 native/MOBILE-TESTING.md 自動提供已驗證的測試 APK。
- 不含正式 Pages／itch／商店／AAB 發布、价格或更換簽章。全平行與真機缺口必須明示。
- 兒童可離線、US$2.99 一次買斷；無廣告、訂閱、消耗型購買、付費隨機或 FOMO。
- 一般階段完成更新交接並繼續，不因此要求換對話。

## 實際遊戲與提交
- BUILD v0.9.48；SHA 027b00f8bccb94a50c16e8c0fa81db3b20af933b432c4ddcefd5c9f8368d66de。
- v41 4839c6a：柔和配色、可愛果凍、Adventure／Upgrades／Settings 導覽。
- v42 02eb0e5：柔和音樂／武器音色、Boss 曲切換、音訊亂數隔離、停止競態與音源回收。
- v43 a29d96c：13 個 Boss ×11 語言命名、章節規則、日韓術語、文字區捲動、Boss 數量。
- v44 01779c3：復活清彈後舊索引與重開局負 dt 的崩潰修正。
- v45 da99b82：翻滾保留較長既有無敵，不再覆蓋成 0.42 秒。
- v46 540e0d3：大型 Boss 可見身體時可鎖定；53px 露出時射擊 0→1 發。
- 測試工具 83fed99：test: measure absolute FPS without a competing game。
- v47 c1167c3：v0.9.47: make range upgrades extend projectile reach。
- 以上已 push；手機流程提交以 git log 核對，不把文件當成 Git 現況證據。
- 字典246 keys ×11、預設英文；v48新增5個儲存回饋鍵，原翻譯不變。

## 測試證據（_private/test-runs 與 _private/test-artifacts）
- v41 48/48：20260909-075803-379699-soft-final；v42 49/49：20260909-082740-083723-audio-full。
- v43 50/50：20260909-091709-010332-localization-final；v44 51/51：20260909-100123-816241-revive-final。
- v45 52/52：20260909-102121-309160-dash-full；上述版本CPU4／離線皆有通過證據，詳歷史。
- v46首輪52/53：20260909-103706-761985-target-full；僅效能28.8失敗，獨立重跑35.6→35.2通過。
- v47首輪54/55：20260909-105935-518167-range-full/results.json；功能54通過，原雙局效能27.1失敗。
- 未改測法的重跑仍23.8失敗：20260909-112203-606200-range-perf-retry；兩次失敗保留。
- 查明雙局資源競爭後，保留30FPS門檻，改以單局測絕對值；雙局仍驗同伴相對損失<20%。
- 修正後1/1：20260909-113211-349164-range-perf-isolated/results.json；同一遊戲SHA，單局均值51.3FPS。
- 不宣稱一次55/55全綠；完整功能與修正後獨立效能兩份報告合併驗證。
- v47 CPU4／離線：range-cpu4.log、range-ui-cpu4.log、range-offline.log；36組射程、12組最大dt命中、11語言320px商店／卡片皆過。
- 同場景來源A/B：v46中位52.15、v47中位50.42FPS；range-matched-20260909-112853/results.json。不是Pixel結果。
- 固定120敵場景中位56.79→56.77；range-perf.json，不能跨測法混比。
- 原48工曾讓Surface失去回應，本機不重試；2工完整套件不替代全平行門檻。
- 環境：.venv Python、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- run_tests.py --jobs 2；效能最後單獨。禁止診斷／Gradle與效能測試競爭CPU。

## 難度、道具與語言：結論及下一步
- v47永久射程每級投射速度+10%、局內每級+15%、合計封頂60%；原先只增加已被可視範圍封頂的鎖定數字。
- 壽命／彈數／傷害／敵彈／價格／掉落權重未改；同伴繼承，只有加速彈使用整段移動碰撞防穿透。
- 噴槍永久第2級能打中300px靶（21傷害）；第3級溜溜球前進149.77→206.55px。
- 正式v47的v0947-progression.json：63個完成樣本、固定重播一致；tests/diagnose_progression.py，不是FPS或真人勝率。
- 三組零強化／沿前10關收入購買／全滿，每格3種子；1／6／7關皆3/3，9／10／30关零強化0/3、其餘3/3；50關皆0/3真正陣亡。
- bot有時沒拾寶箱／核彈，避敵也可能讓Boss離開畫面；不可宣稱已解決末章難度。
- 下一步透過手機回饋記錄關卡、受傷／補給／Boss情境，再選一項後期數值調整；未採用任意降彈速、延冷卻或無限商店等級。
- 舊360秒樣本含unfinished，不等於敗北；新工具900上限，未完成報錯，勿沿用舊假0/3。
- 商店成本8930、含幣加成單局上限520；py_meta原832是假高估，已修工具，收入價格沒改。
- 救命卡加權、再生2／4次上限、綠殼第9關入池不變；局內卡滿補心與永久商店滿級不同。
- 11語言完成鍵／參數／數值／語境／版面核對；母語潤稿與跨國兒童理解度未做，不宣稱全部精準自然。

## 固定手機測試入口（已上線）
- https://github.com/davidform/goo-blaster/releases/tag/android-test ，加入Pixel本機瀏覽器書籤；不依賴USB／PC開機。
- v0.9.48，Android versionCode 94800／versionName 0.9.48-test.0；APK 4270375 bytes。
- APK SHA 5df277d0cbced790d4f07e98b3661730288fcd2caf71dece1f16d8454ea50f2b；內嵌遊戲SHA等於根目錄，DEX確認含原生儲存外掛。
- appId com.demjastudio.gooblaster，與舊APK同簽章；公開指紋固定於native/test-channel.json，私鑰不入Git。
- _private/mobile-test/latest.json／published.json保存稽核；公開下載SHA一致、未登入頁面HTTP200、版本／連結／限制說明存在。
- 首次發布遇草稿untagged網址檢查失敗，修正後沿同草稿完成；release385210316、asset551909536，無重複發布。
- 每版獨立APK檔名、保留舊檔、固定測試tag只沿歷史前進；拒絕改寫未管理的Release。
- native/build_test_apk.py --tests <完整報告> --retry <同SHA補驗證報告>；見MOBILE-TESTING.md。
- 手機按「更新」，勿解除安裝／清資料；此APK覆蓋更新與存檔保留尚待Pixel實測，不能以簽章核對代替。
- 原AAB仍v40且未簽；正式Pages／itch／商店未更新，itch仍v31。Play／iOS／原生獨立repo未完成。
- Pixel先前v40離線／Preferences／冷啟動曾通過；新版揚聲器／耳機／效能／存檔仍待試玩。

## 本次接手：戰報與工作室系統
- v48 fdeff02已push，修復存戰報：原生ACTION_CREATE_DOCUMENT、自選位置寫PNG、成功／取消／失敗提示與結算捲動；玩法數值不變。
- 最終56/56：20260909-124035-339602-report-final；CPU4／離線通過，原生Java編譯成功；APK已公開，asset 552038154、公開下載SHA與HTTP200核對通過。

- 工作室流程2f8d936已push：studio/README.md、studio.project.json與game-studio skill；8項工具測試與官方skill驗證通過。
- skill已安裝C:/Users/Surface/.agents/skills/game-studio；未來新遊戲沿用流程，不繼承本作App身分／簽章／售價／授權。
- 預設單一agent；按需經同意後才分工。無需先轉ChatGPT，若想先構思可用studio/game-studio/references/idea-brief.md。
- 待Pixel確認：更新後存戰報能開系統儲存視窗、實際PNG可開、取消後可重試；未冒稱已真機通過。
