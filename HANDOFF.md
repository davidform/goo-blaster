# GOO BLASTER 精簡交接

## 目前任務與實際狀態
- 使用者五項：第9關小怪包圍／子彈密集、核彈慢動作白屏、死亡殘影、故事一目了然、糖果屋衝刺。
- 分支codex/soft-world-ui；v56 887a6c9、v57 f8a9106已提交推送。root目前v0.9.58，本次提交以git log核對，勿reset覆蓋。
- v58 HTML SHA 3865448b235b1ee0d11f63ca4b2fc14770a72201e6c628c8b9ceb23d2a538da6。
- 公開APK、itch與Pixel仍v55，不能把本地v58當作已交付。
- 遵守AGENTS.md、game-studio；單HTML、零相依、離線、預設英文、11語言、每版單一平衡變數。
- 預設單代理；未獲多代理授權。Surface曾因48工無回應，不重試全平行。

## 本次實作
- v56只調7–19關普通敵人射擊間隔：第7關×3，逐關回復，20關×1；第9關×35/13。首次及後續CD一致。
- 出怪量、HP、速度、XP、Boss、商店、卡池不變。第1–6及20–50關普通射擊也不變。
- 無復活、Pixel實際強化、250ms決策，同種子第9關1/8→4/8；不是人類勝率。第8關0/2→1/2、第10關0/2→0/2，第一關2/2不變。
- v57核彈2.1秒：初期世界16%速度，0.48秒爆炸、白屏停留至約1.2秒、1.8秒退白，漸進恢復速度。
- 暫停凍結、單次爆炸音、新局重置、消除Boss／核彈大提示重疊；清敵／BossHP保留。
- 慢動作也會放慢淨空、冷卻與無敵的世界計時，關卡倒數用rawdt；不宣稱毫無玩法時間影響。
- v58地面單一20%淡色層，64塊重疊不再加深；實際果凍效果、生命期與資料不變。
- 故事目標＋章節小景直接顯示、地圖在下，長故事可展開；550目標與小螢幕滑動已驗。
- 商店原有三級dash改名衝刺訓練，顯示下一級冷卻／固定0.42秒無敵。不是新增第二套技能。
- 冷卻仍3→2.65→2.30→1.95；局內疊卡下限1.2秒。30秒連按25次、無敵34.72%，非連續無敵。
- i18n/build_v0958.py新增1key更新2keys×11；共266keys，尚未母語者潤稿。

## 測試證據與當前卡點
- 命令：PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules；.venv/Scripts/python.exe run_tests.py --jobs 2。
- v56完整63/64：_private/test-runs/20260909-223040-368026-ordinary-shot-full/results.json；only py_v0927_perf補跑20260909-225736-013931-shot56-perf-retry仍失敗。
- v57完整64/65：_private/test-runs/20260909-230337-065023-nuke-cinematic-full/results.json；亦只有py_v0927_perf失敗，單局24.5FPS。
- v58完整65/66，只有獨立效能未過：_private/test-runs/20260909-233021-174242-readability-full/results.json；SHA不變，所有程序已結束。
- 所有首輪失敗保留。v56同批ABBA舊v55 23.75FPS／新v56 23.65FPS；shot56-perf-diagnostic.json，未見測試殘留程序。
- Surface首測電池42%、CPU1073MHz；23:44仍電池26%、1035MHz（system-power58.json）。已詢問接電，尚無回答；環境影響尚非確定根因，不得當PASS。
- CPU4與離線新存檔／冷啟動：shot56-*、nuke57-*、readability58-* logs均過；visual-cpu-offline-receipt.json記錄v57／v58同SHA。
- v56新回歸普通射擊20秒：第9關40→12，第6關13→13、第20關49→49；v55負對照有抓到，200生成欄位比對過。
- 已檢視_private/test-artifacts/nuke57-0.85.png、story58-stage9.png／stage50.png、dash-shop58.png、goo58-dense.png。
- v58獨立DPR2／8秒／150敵＋64果凍ABBA：v57 21.3→v58 24.4FPS、比率1.143通過；goo58-perf.json，不是PixelFPS也不取代絕對門檻。
- 詳細根因／所有失敗與v58記錄已寫docs-14-history.md。完整壓力場景單局25.5FPS，低於30；未交付新APK／itch。

## 交付授權與下一步（等待效能驗證）
- Git commit/push開發分支、固定Prerelease APK與itch同步已授權；不用重複問。正式Pages／商店／AAB／定價／簽章更換未授權。
- 接穩定電源後，先核對同SHA，再跑run_tests.py --only py_v0927_perf --jobs 1 --label readability-perf-ac；不因上次失敗而重跑全部功能，也不調低門檻。若仍失敗繼續量測根因。
- 全部門檻過才能建置／同步：native/MOBILE-TESTING.md、native/ITCH-PUBLISHING.md；build_test_apk.py會強制核對同SHA完整報告，可保留原失敗加--retry。
- 本次Summary：v0.9.58: clarify terrain, stage goals and dash upgrades。
- APK入口：https://github.com/davidform/goo-blaster/releases/tag/android-test；目前v55／95500，APK SHA 9f2229ac26d43dfeee79d7622d48c729efac8a59d0d76d328f41e17e0122cab9。
- appId com.demjastudio.gooblaster；簽章native/test-channel.json固定。build→backup_android.py→notes→publish_test_apk.py --publish→公開下載SHA核對。
- _private/mobile-test/notes-v58-draft.md已備；只有全過與實際APK稽核後才轉正式notes.md。
- itch固定davidform/goo-blaster:html5，目前v55 upload19167726/build1962179；只上傳單一index，保留價格／公開狀態。實際Run game並核對iframe完整payload，CDN追加腳本差異需明示。
- USB若Pixel仍連線，_private/update_pixel58.py＋pixel58.cjs已備但未執行；先備份當前存檔，install -r保留原生bytes、核對版本與WebView，不卸載清資料。
- 全平行／母語潤稿／Pixel難度、白屏舒適度、殘影可讀性及FPS未驗；第10關診斷仍0/2。不得宣稱本次正式驗收完成。

## Devlog自動流程（2026-09-10）
- 使用者新增授權：itch公開遊戲驗證完成後自動發中英Devlog；同批一篇，按公開版本而非root BUILD，先查文章與草稿避免重複。
- native/DEVLOG-PUBLISHING.md＋native/devlog.py；準備／收據工具不直接登入，代理用CUA發文，非背景排程。
- v55已補發：https://davidform.itch.io/goo-blaster/devlog/1657882/v0955-clearer-upgrades-fire-trails-and-late-game-balance；Published、全部正文與v55附件已核對。
- store/devlogs/v0.9.55/post.json有公開網址／內容hash／版本證據；私人devlog-v55-receipt.json保存實際DOM正文。
- python tests/test_devlog_workflow.py：9/9；版本不符、未公開、草稿誤認、缺正文、不同網址重複及已發內容覆寫都擋住。遊戲HTML未變，未重跑遊戲三輪。
- 編輯器HTML fill後可能未同步送出textarea；須可視編輯器末尾真按鍵空格／Backspace觸發同步再查。第一次Save因空body失敗，修同步後成功；不得直接腳本提交。
- v58仍卡效能／未發版，因此沒有v58已上線Devlog。上述遊戲待辦不變。
