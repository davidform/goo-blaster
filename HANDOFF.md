# GOO BLASTER 精簡交接

## 目前狀態（2026-09-22）
- 使用者要求處理失敗並執行可操作的未執行項目；v0.9.73交付已完成，停止新增功能。
- 分支codex/soft-world-ui；index.html未在交付續作修改，BUILD仍v0.9.73。
- SHA bcf79c3942ee5f7dae29d64dff63b7460940ca5b3a34547bbae204b26225c10d。
- 單一代理；.codex-remote-attachments為使用者附件，不提交。存檔／簽章／後台數據僅_private。

## 本次變更與測試
- v73情境音樂：battle132／boss148／garden84／picnic112／pond76／starlight68 BPM，menu104。
- 原創WebAudio合成，單檔離線；旋律／配器分開，保留靜音、背景暫停與舊聲音清理。
- v72小屋Lv.0／1／2／3新種倍率1／1.5／2／2.5一併交付；已有作物完成時間不延長。
- 關App仍依readyAt計時；工具／料理／建設／修屋仍立即完成。
- 原完整81項80PASS，perf因同時兩個最壞場景競爭而失敗；原始報告保留，不抹除。
- 診斷同批雙局18.6FPS，單局44.3／41.5FPS；不能直接歸因其他程式。
- perf改為單局AB/BA/BA/AB、固定種子、無競爭context斷言及幀數／牆鐘紀錄。
- 原門檻保留：控制≥20、同伴損失<20%、單局≥30FPS；不改遊戲或降低門檻。
- 補驗無同伴43.325、有同伴41.675FPS（-3.81%）PASS，同SHA合併81/81。
- 全套：_private/test-runs/20260922-191446-066345-music73-full/results.json。
- 補驗：_private/test-runs/20260922-194512-979185-music73-perf-isolated/results.json。
- 命令：GOO_BROWSER_CHANNEL=msedge .venv/Scripts/python.exe run_tests.py --jobs 1 --label music73-perf-isolated --only py_v0927_perf（PowerShell以$env設定）。
- GOO_PERF_CPU=4反向測試23.2FPS，預期exit1拒絕，證明仍抓得出慢速；_private/perf73/negative-cpu4.log。
- 先前music73-initial三項、music73-cpu4-offline兩項與release_smoke通過；音訊七場景0削波／0非有限值／0JS錯誤。
- py_test9第1／2關通關，第3關陣亡；符合第1關硬門檻，不宣稱全關通過。
- Surface不跑全平行（曾無回應）；CPU4不等於全平行，效能單獨執行。

## 已公開交付
- APK v0.9.73／97300／com.demjastudio.gooblaster，簽章沿用；公開下載SHA與本地相同。
- https://github.com/davidform/goo-blaster/releases/tag/android-test
- APK SHA 447671ad9363d571ef82e72f48187d666e747244eff6e9559d902a83bf5d0a1d。
- _private/mobile-test/latest.json與published.json保存建置／公開收據。
- itch build2003942／upload19167726；公開payload與原碼相同（只多平台script），實際開始／暫停通過。
- Pages部署e614100a9f1cb5a3f8596652e980b827dbfd7917，Actions35723987696成功；公開完整SHA與開始／暫停通過。
- _private/mobile-test/itch-v73.json與pages-v73.json。
- 中英合併Devlog已Published：https://davidform.itch.io/goo-blaster/devlog/1673107/v0973-music-for-every-adventure-growing-with-your-cottage
- store/devlogs/v0.9.73/post.json已record；test_devlog_workflow.py九項PASS。
- 遊戲頁介紹與截圖已更新v73；首三張戰鬥保留，新小屋倍率圖第四張，原圖與公開縮圖已目視核對。
- Pixel adb devices無裝置，未更新；最後已驗證v71／97100。不卸載／清除資料。

## 研究與剩餘項目
- docs-19-market-review.md：市場需求未驗證，先測短場戰鬥→庭院可見成長；不以測試PASS代表好玩或會賣。
- store/research/player-study-kit.md及兩份空白CSV已完成，提供非誘導成人觀察與決策門檻。
- 未招募／發訊息／投廣告／改价／啟用多代理；研究提案不等於新增功能授權。
- 真人聽感、真機長時效能、回訪／付費意願、母語潤稿尚未完成。
- 論壇首文17090045仍v64：本次可開編輯，但富文字工具貼入／局部fill造成錯誤位置；已重新載入還原，沒有儲存錯文。個人頁引用仍待同步。
- 先前論壇自動核准拒絕保留為歷史；本次未遇同一拒絕，不把編輯器失敗誤稱核准問題。
- cleanup_local.ps1先盤點再Apply，刪除v70 APK與一份暫存，共13,748,740 bytes；保留v73及v71回退APK。
- 25個舊profile AccessDenied仍保留，未改ACL；清理收據_private/mobile-test/cleanup-local-20260922-200656.json。
- 已push 387eddc：test: isolate performance samples and verify slowdown rejection。
- 後續僅補真機／真人與論壇同步；不要重做v70發布或擴增遊戲功能。
