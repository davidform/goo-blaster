# GOO BLASTER 精簡交接

## 目前任務（2026-09-22）
- 使用者要求倒數隨升級延長；已選定小屋Lv.0／1／2／3倍率1／1.5／2／2.5。
- v0.9.72已實作；79/80通過，效能環境門檻阻擋發布。只改新種時間，已種時間凍結；工具／料理／修屋仍即時。
- 分支codex/soft-world-ui；v71遊戲9011350及交付588d50d已push，Pixel倒數核對文件3c5d081已push。
- .codex-remote-attachments為使用者附件，不提交；手機存檔與簽章只在_private。

## v72實作與決策
- 薄荷60／90／120／150秒；莓果180／270／360／450秒；月光360／540／720／900秒，仍依原種類解鎖。
- 每田duration＋readyAt；gardenPlantSeconds算新種時間，gardenDuration處理該批作物。升級不回溯延長，舊存檔沿原時間。
- 倒數上限、存檔清理與成長比例改讀duration，避免高階時間被舊上限截短。
- 任務板與单田詳情顯示新時間；gardenPace說明等級倍率。i18n/build_v0972.py產生11語言新key，原字串不變。
- 原碼SHA b7fcbfb1e4eed2d71ca581b6c2254723a39a72ca3f1d25801c2e246de55a573f。
- _private/level72/source-audit.json：pickBetterSave至EOF逐字未變；無戰鬥、價格、產量變更。
- store/screenshots/v0.9.72為真實UI四輪種收→首次修屋→莓果預覽／倒數，只加速等待，無資源注入；中英圖片已檢視。

## v72驗證進度
- level72-edges：新test py_garden_level_timer 19.8秒PASS；涵蓋四級、預覽、半程、升級中舊田、遷移、極值、備份／原生合併、冷啟動離線、33語系尺寸。
- 初輪level72-initial新test因JSON欄位順序誤報；改解碼物件比對後通過，保留原始失敗，不改遊戲處理。
- CPU4離線兩項PASS：_private/test-runs/20260922-162652-776411-level72-cpu4-offline/results.json（timer63.7s／level_timer266.9s）。
- 完整80項完成，原始78/80；layout補跑後79/80。_private/test-runs/20260922-162318-467202-level72-full/results.json。
- py_layout_fit因擷取後數值變動找不到原行；改正規化數字後保留實測字框。20260922-163658-844548-level72-layout-retry 77.6s PASS。
- py_v0927_perf兩次環境門檻失敗：對照組12.1／11.6FPS，單局約21FPS；未改v71亦對照11.6FPS失敗。僅證明舊版也過不了，不作跨批次效能差異推論。
- 無殘留測試程序；另有SETUP64自16:08執行並持續用CPU，是否為原因尚未確定。已問使用者是否正在安裝，未中止或改設定。
- retry：20260922-165411-961523-level72-perf-retry；v71對照_private/level72/baseline-v71-perf.log；總收據_private/level72/verification.json。
- 不在Surface重跑全平行（曾無回應）；CPU4不能冒充全平行。效能需單独跑完才建APK。

## 本輪後續
- 待安裝／背景負載狀態確認，重跑單獨py_v0927_perf；不改門檻、不把舊版也失敗當通過。
- 通過後以完整報告＋layout/perf補跑報告build_test_apk，再publish_test_apk；來源SHA不得改動，改動須重跑整套。
- APK／itch／Pages／Devlog／頁面同步皆依現有授權執行，v72尚未發布。
- 尚未填寫／儲存公開文案，未上傳截圖。新版Devlog不存在，已有檢查防重複；不要把本地準備當發布。
- store/devlogs/v0.9.72-notes.json已準備，待公開itch收據通過後才devlog prepare。
- Pixel目前已裝v71，若ADB連線可直接備份後install -r更新v72，不卸載／清資料。

## 已完成v71（不重做）
- 完整79/79＋CPU4三項通過；APK97100，SHA48245f783d6b09305ac8efe3e8cbf2b41b8678b08ab173dc0dff8908541c5348。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test 。
- itch build2003135/upload19167726、Pages 1a5341e337b76e4770eea707f93c8448230d182f、Devlog1672834均已公開核對。
- v71在Pixel由96400覆蓋更新97100，簽章、版本、原有存檔保留；新字段遷移正常。
- 關App倒數回報：實機60秒，force-stop後14.010秒重開剩46秒；再關到成熟重開可收成，未重現停止。只UI收成重種第一田，其餘兩田未動。
- _private/mobile-test/pixel-timer71-growing.json與pixel-timer71-mature.png；原始save備份未公開。

## 其他未完成
- 長時手機FPS、全平行、母語潤稿、長期耐玩性仍未驗證；不宣稱正式商店／商業品質驗收完成。
- 論壇首文17090045及個人頁引用仍v64，前次核准阻擋未解除，不繞過。
- 上次清理釋放13711759bytes；25個AccessDenied profile保留，不改ACL。
