# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者看不懂庭院，要求研究市場玩法並套用；v67已實作修復任務板，完整75/75與CPU4通過，正準備公開同步。
- 分支codex/soft-world-ui；上一個提交c208db9，本次改動未提交。BUILD v0.9.67，544276bytes。
- SHA d585a2b305fa4a981b4c941e43d0213c69c8c87af47b9c7944c436a8ba4b5467。
- 預定Summary：`v0.9.67: guide garden play through restoration goals`。
- 單代理，單檔離線；附件.codex-remote-attachments不提交。

## 研究與實作
- docs-17-garden-loop.md：FarmVille 3／Hay Day訂單板、Gardenscapes關卡資源修復的官方資料與取捨。
- 第一屏下一級小屋真實預覽、解鎖作物、花瓣進度；種植→冒險→收成→修復四步及依狀態切換的主要按鈕。
- 一次播種可用空田／收成熟田；選作物前列成本、通關數和收益；逐田操作保留。
- 成長時明說重玩也算、等待無效；只導回冒險，不自動開戰。收成／修復顯示結果。
- 保留12/45/120成本、作物1/2/3通關→1/3/6花瓣與存檔schema，無新增戰鬥屬性。
- 三田使用最佳作物，三階約4/10/21通關；後期重複感待另版處理，不把引導改善宣稱完整經營。
- 21新字串，i18n/build_v0967.py同步11語言；預設英文；非母語潤稿證據。
- 下一步由真人確認目標與動作是否清楚，再考慮有限居民委託／可選建築；加工與生活AI未實作。

## 驗證
- 完整指令：.venv/Scripts/python.exe run_tests.py --jobs 2 --label garden67-full。
- _private/test-runs/20260921-184815-132826-garden67-full/results.json；75/75過，source_unchanged，含獨立效能。
- py_garden_quest走4輪真實按鈕／模擬成功結算後完成第一修復；另驗種子不足、混合成熟、上限、重啟及132語言尺寸狀態。
- CPU4 garden/world/quest 3/3：_private/test-runs/20260921-184839-375860-garden67-cpu4/results.json。
- py_release_smoke.py exit0：離線、新存檔、CPU4、重開progress9/coins456、外部請求0、JS errors0。
- 首批garden67-first：garden舊選單總數失敗，改核對原gardenPlots三個；world立即檢查觸控狀態失敗。
- garden67-edges再次world失敗；probe確認點中正確但click未派送，改輪詢GV.selected後CPU4及完整批該項過。
- 初批報告20260921-184507-110846與20260921-184651-683269保留，是翻譯名修正前d987c5，不作最終驗收。
- _private/garden67/verification.json彙整。git確認LEVELS到COINS及META到檔尾沒變。
- py_test9第1/2關過53/79秒、2/3及3/3心；第3關90秒陣亡，非硬門檻但明列。第1關驗收過。
- 截圖store/screenshots/v0.9.67由native/capture_garden_quest.py可重現，通關是結算模擬，不是真人／真機。
- Surface全平行依凍結限制未跑，ADB無裝置；效能已独跑完成，現在可建Android。
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。

## 發版現況與下一步
- 公開仍v66：APK96600、itch1999525、Pages ca14d886、Devlog1671600。
- v67 notes與description已準備；_private/itch-builds/v0.9.67只含核對SHA的index，尚未上傳。
- Chrome tab1912753820遊戲編輯頁已填v67文案、7條清單核對但未Save；等全套過再發版／上傳quest-harvest-zh第四位，前三Boss圖保留。
- 完整測試完成後commit本版→build_test_apk→publish_test_apk→Butler→公開UI與SHA→Pages→Devlog→頁面說明／新圖。
- 原討論串首文仍待v65自動核准拒絕後的明確授權，不重試或繞過。
- 固定手機入口 https://github.com/davidform/goo-blaster/releases/tag/android-test 。不卸載、不清資料。
- 後續按cleanup_local.ps1白名單清理，保留最新版＋上版、所有存檔／簽章／證據。
- 舊相簿歷史圖片不擅刪，先前Chrome原生確認逾時；23舊profile拒絕存取不改ACL。
- Pixel長時間FPS、母語潤稿、付費市場品質尚未驗收。
