# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者要求種植任務收成後才完成，並看得到倒數；v68已實作，完整76項含補跑、CPU4與離線已過，跨平台已發布。
- 分支codex/soft-world-ui，遊戲commit b369be10b2b1d94f1a346f136897e8c768604339，已push。BUILD v0.9.68。
- SHA d548aa28ba8e6c720158291b4fa31371698e327dae8f8fcd64d5341e9358b79b。
- 遊戲Summary：`v0.9.68: grow garden crops with harvest countdowns`。
- 單代理、單檔離線、11語言；.codex-remote-attachments不提交。

## 實作與決策
- 薄荷60秒／莓果180秒／月光360秒，readyAt持久化，離線成長、成熟不枯萎。
- 種植與收成同一步，領取前不進修屋；主要任務按鈕等已種作物收完；戰鬥可自由玩，通關仍給種子。
- 任務板、田地hotspot與詳情每秒倒數；每秒只更新文字/進度，不重建焦點；狀態跨界才render。
- 舊growth比例換為剩餘時間並保存，已熟不倒退；錯誤plots型別防護、無效日期與時鐘倒退有界。
- 同場景觸控拖曳後tap缺compatibility click，probe確認pointerup到達但沒有click；touch pointerup直接處理並忽略trusted touch click避免重複。
- 12/45/120修屋成本、1/3/6產量、每株種子1/收成返種、戰鬥數值不變。
- i18n/build_v0968.py同步7key×11語言。舊v67通關成長規則被使用者新要求取代。
- 真實新存檔種植，實際等待61.24秒才收成3花瓣；native/capture_garden_timer.py，可重現，不改時鐘。
- 截圖store/screenshots/v0.9.68；宣傳第4張用倒數，前三保留v64戰鬥（戰鬥未改）。

## 測試證據
- 完整最終批完成：_private/test-runs/20260921-200120-052686-garden68-final/results.json，76項主批75過+1載入逾時補跑過。
- 同SHA重試：20260921-200904-579195-garden68-boss-retry/results.json，py_boss_skin PASS；原批載入30秒逾時保留。
- 最終CPU4：20260921-200145-107706-garden68-final-cpu4/results.json，world/quest/timer 3/3 PASS。
- py_release_smoke exit0：新進度、CPU4、離線0外部請求、0JS錯誤、重開progress9/coins456/meta dmg2。
- 新增py_garden_timer：live countdown、migration90秒、offline/reload、壞save、clock bounds、收成前不跳任務、通關不跳倒數。
- py_garden_quest四輪UI收成到首修屋（長等待用測試時鐘）、132locale/size/state；舊生命週期和world已更新時間模型。
- 初敗garden68-first觸控逾時；probe和兩次重現後修產品事件路徑，garden68-edges 3/3。
- 舊SHA454d批garden68-full主動停止，因最終save型別防護；不可當通過。舊CPU4亦留存但最終報告才有效。
- _private/garden68/verification.json彙整。全平行依Surface限制不跑；Pixel無ADB裝置，未安裝。
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。

## 已完成交付
- Android96800 / 0.9.68-test.0，同簽章；公開APK SHA e20a72c29362e3ecb328ebf8050b3dbe03b6b696b50e94b13dd421906f62a7e4。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test；published.json verified，Pixel未連線未安裝。
- itch build2000616/upload19167726，公開payload同源；種植倒數、啟動/暫停已驗證；_private/mobile-test/itch-v68.json。
- Pages141e176b1b64ba46249ede275d940fd51d55c030，Actions35600120863成功；公開完整SHA與CUA啟動/暫停過；pages-v68.json。
- itch介紹v68及前四張圖30141028/30141027/30141026/30153616公開載入核對；store/page-sync/v0.9.68.json。
- Devlog1671947中英完整正文與PUBLISHED已核對；store/devlogs/v0.9.68/post.json。
- 先前CUA Windows1909/Debugger unattached已恢復；新Chrome tab完成公開驗證，不改ACL。
- 獨立效能56.7FPS，同伴50.5→50.3（-0.3%），非Pixel。
- 白名單清理保留v68/v67、存檔、簽章與證據；拒絕存取測試profiles保留。

## 其他未完成
- 原討論串首文仍待v65自動核准拒絕後明確授權，不重試／繞過。相簿歷史圖保留。
- 居民訂單、加工、更多建築未實作；離線時間可受裝置改時影響，不宣稱防作弊。
- Pixel長時間FPS、母語潤稿、付費市場體驗未驗收；技術通過不代表耐玩性完成。
