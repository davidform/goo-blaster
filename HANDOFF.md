# GOO BLASTER 精簡交接

## 目前任務（2026-09-22）
- 使用者要求情境配樂：戰鬥刺激、庭院放鬆、挑戰各有主題。完成音樂後停止加功能，研究市場需求與AI團隊工作方式。
- v0.9.73音樂已實作，市場研究已完成；完整81項中80項通過，效能環境判準兩次失敗，尚未發布。
- 分支codex/soft-world-ui；先前v72提交7929733已push，未發布；v71公開及Pixel已交付，不重做。
- 預設單一代理；.codex-remote-attachments是使用者附件，不提交。存檔、簽章、後台數據只留_private。

## v73實作
- battle132／boss148／garden84／picnic112／pond76／starlight68 BPM，menu104。旋律、和聲、節奏、配器與密度按情境分開。
- 原創WebAudio合成，仍單檔／離線／零執行期相依／11語言；未新增可見字串。
- syncHubMusic與庭院入口／挑戰進退連動；Boss結束回battle；淡出舊music bus並斷線，保留靜音與背景暫停。
- 無戰鬥／存檔／計時／價格改動。SHA bcf79c3942ee5f7dae29d64dff63b7460940ca5b3a34547bbae204b26225c10d。
- 新py_music_scenes列入全套，真實UI＋音訊排程驗七情境、快速30次切換、清理、靜音、暫停／恢復、離線；消耗遊戲RNG=0。

## v73證據
- _private/test-runs/20260922-191326-238846-music73-initial/results.json：三項PASS（audio_quality、range_music、music_scenes）。
- _private/test-runs/20260922-192109-001379-music73-cpu4-offline/results.json：兩項PASS，CPU4，20.5／45.0秒。
- tests/py_release_smoke.py：新存檔progress1／coins0／meta{}；離線、CPU4、重啟還原PASS；0外部請求、0JS錯誤。
- _private/test-artifacts/music73-preview/results.json與七場景wav：實際OfflineAudioContext輸出，全部0削波／0非有限值／0JS錯誤。真人聽感尚未驗收。
- 完整81項：_private/test-runs/20260922-191446-066345-music73-full/results.json，complete=true、source_unchanged=true、80PASS，唯一FAIL為py_v0927_perf。
- 效能初輪對照18.1FPS、單局31.3–39.6FPS；確認無殘留測試後獨立補跑仍對照18.2FPS、單局42.2–44.6FPS。失敗為環境門檻，原因未確定，不降門檻／不宣稱效能合格。
- 補跑：_private/test-runs/20260922-193527-534085-music73-perf-retry/results.json。未建APK／更新Pixel／同步itch或Pages／發Devlog／清理。
- 本輪py_test9第1／2關通關（59／68秒）、第3關87秒陣亡；符合既定第1關門檻，不冒稱全關通關。py_ab_base PASS。
- Surface不跑全平行（曾無回應）；CPU4不等於全平行。效能獨立、不可與建置並跑。

## 市場研究與暫停範圍
- docs-19-market-review.md：有日期的官方競品資料、自身實際itch頁與後台、兩週觀察計畫、AI角色審查責任／否決條件與可重用prompt。
- 判定：市場需求尚未驗證；建議先測「短場戰鬥→庭院可見成長」。不以版本數、下載級距或自動測試宣稱好玩／會賣。
- _private/market73/analytics-note.md保存精確後台數字；樣本少、未排除開發流量，無留存／付費轉換證據，不公開提交。
- 下一步提案為8–12名成人的非誘導觀察，尚未招募／發訊息／投廣告／改價／啟用多代理。
- 不自動實作研究中的建議；新的功能開發等使用者決定。正常驗證與既有交付流程不代表批准市場實驗。

## v72一併保留
- 小屋Lv.0／1／2／3倍率1／1.5／2／2.5，只影響新種；已有作物duration＋readyAt凍結，關閉App繼續計時。
- 薄荷60／90／120／150秒；莓果180／270／360／450秒；月光360／540／720／900秒。工具／料理／修屋仍即時。
- v72因perf環境門檻失敗未交付；未改v71同環境亦失敗，只能作診斷，不能當通過。
- 當時SETUP64安裝程序高CPU，不確定因果、未擅自中止；19:22查已無該程序。本輪效能以實測為準。

## 已交付v71（不重做）
- 版本v0.9.71，APK97100；固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test 。
- itch build2003135/upload19167726；Pages1a5341e337b76e4770eea707f93c8448230d182f；Devlog1672834。
- Pixel已覆蓋更新97100，簽章與存檔保留；倒數實機60秒force-stop14.010秒重開剩46秒，再关到成熟可收成，未重現關App停止。
- v73尚未更新Pixel；需同SHA全套通過、APK稽核後才install -r，不卸載／清資料。

## 未完成與後續限制
- 發布卡在perf環境判準；使用者要求音樂後停工，暫不延伸效能重構。後續需先釐清量測環境與測試假設，不能只重跑至綠或降低門檻。
- 通過後依native三平台與Devlog流程交付同版；v72＋v73應合併一篇Devlog，不發未公開版本。
- 真機長時效能／聽感、全平行、母語潤稿、回訪與付費意願未完成。
- 論壇首文17090045／個人頁引用仍v64，先前自動核准阻擋未解除，不繞過；舊清理25個AccessDenied profile保留，不改ACL。
