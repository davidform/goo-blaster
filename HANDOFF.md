# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者要求種植任務收成後才完成，並看得到倒數；v68已實作，完整76項含補跑、CPU4與離線已過，尚未發布。
- 分支codex/soft-world-ui，基底5ca8627；本次遊戲改動準備commit。BUILD v0.9.68。
- SHA d548aa28ba8e6c720158291b4fa31371698e327dae8f8fcd64d5341e9358b79b。
- 預定Summary：`v0.9.68: grow garden crops with harvest countdowns`。
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

## 待完成交付
- 完整回歸/獨立效能已完畢。平均56.7FPS，同伴50.5→50.3（-0.3%），非Pixel。commit/push本次檔案。
- Android固定同簽章測試通道、itch html5實際payload/啟動、Pages指定commit工具與公開SHA/啟動、中英Devlog。
- 頁面文案store/page-sync/v0.9.68-description.html；Devlog notes已備妥。未驗證公開前不可宣稱v68已上線。
- Devlog管理頁確認目前8篇、無v68或草稿；CUA在遊戲編輯頁；重連後kernel無法啟動Windows1909，兩次失敗，不改安全設定。匿名公開遊戲可用獨立瀏覽器實際驗證，介紹/Devlog需CUA恢復。
- 既有公開v67：APK96700、itch build2000470、Pages44635cca、Devlog1671866。
- 同步後白名單cleanup，保留新版與上一版APK／存檔／簽章／測試證據；拒絕存取不改ACL。

## 其他未完成
- 原討論串首文仍待v65自動核准拒絕後明確授權，不重試／繞過。相簿歷史圖保留。
- 居民訂單、加工、更多建築未實作；離線時間可受裝置改時影響，不宣稱防作弊。
- Pixel長時間FPS、母語潤稿、付費市場體驗未驗收；技術通過不代表耐玩性完成。
