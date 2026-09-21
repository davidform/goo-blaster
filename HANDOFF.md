# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者看不懂庭院，要求研究市場玩法並套用；v67已實作修復任務板，完整75/75、CPU4與跨平台同步完成。
- 分支codex/soft-world-ui；遊戲commit e3a282d5e598d196ebe36dbc642e36cd9661a833已push。BUILD v0.9.67，549871bytes。
- SHA d585a2b305fa4a981b4c941e43d0213c69c8c87af47b9c7944c436a8ba4b5467。
- Summary：`v0.9.67: guide garden play through restoration goals`。
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
- Surface全平行依凍結限制未跑，ADB無裝置；效能已獨跑完成，平均56.8FPS；同伴50.7→50.5（-0.4%），非Pixel。
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。

## 已公開交付
- APK96700／0.9.67-test.0同簽章，內含HTML與DEX核對，公開SHA ba356090fd369696fc125b64ef26c1eec64ced48a64a10c9b1d0c012c3214ef6。
- 固定手機入口 https://github.com/davidform/goo-blaster/releases/tag/android-test 。手機未連線，沒有安裝本版；不卸載／不清資料。
- itch html5 build2000470／upload19167726公開完整payload一致；CUA舊存檔種子2→0、引導回冒險、開始／暫停過。itch-v67.json。
- Pages部署44635ccacd42507811d0380c6fb8030b03691e6f，Actions35593022389 success；完整HTML SHA及開始／Paused驗證。pages-v67.json。
- Devlog1671866 Published，中英完整正文／v67附件／新圖核對，workflow9/9；store/devlogs/v0.9.67/post.json。
- https://davidform.itch.io/goo-blaster/devlog/1671866/v0967-a-clear-path-from-planting-to-restoration 。
- 遊戲頁v67說明已保存，新圖30151941第四，前三Boss戰不變；store/page-sync/v0.9.67.json，公開四圖載入核對。
- 初次itch tail檢查漏defer屬性，完整讀差異後核對僅已知平台script；初次Pages收據欄位名不符被預檢擋住，映射既有證據後75項全過才push，未放寬驗證。
- HTML原始bytes549871；先前544276是read_text換行正規化後大小，已更正；原SHA從頭到尾是原始位元組，測試與三平台均一致。
- cleanup白名單刪v65 APK4311673bytes，保留v67/v66及存檔簽章證據；24舊profile拒絕存取未動，不改ACL。

## 未完成／後續
- 原討論串首文仍待v65自動核准拒絕後的明確授權，本次未重試／繞過。相簿後方10張歷史圖保留，原生刪除確認先前逾時。
- 下一步以玩家能否不看外部教學完成第一修復評估引導；再單獨設計居民委託／建築選擇，避免只增加材料和等待。
- Pixel長時間FPS、全平行壓測、母語潤稿、付費市場品質仍未驗收。
- 本版技術與交付完成，不宣稱完整農場經營或耐玩性已解決；不自行換新對話。
