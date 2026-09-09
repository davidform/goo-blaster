# GOO BLASTER — 目前交接
更新：2026-09-09；本檔只留現況，詳細歷史見docs-14-history.md。

## 接手與授權
- 完整讀AGENTS.md及本檔，再核對Git差異、版本與任務；安全同步，不reset覆蓋。
- 單一代理，繁體中文；遊戲三輪實跑，效能單獨跑；回報區分已驗證／失敗／未執行。
- Git可自動commit/push，只提交本次檔案。Pages僅main push部署；開發分支不自動部署。
- itch.io已授權在規定測試通過後更新網頁遊戲；商店送審、正式發布、價格及敏感簽章另行授權。
- 兒童可離線、US$2.99一次買斷、無廣告/訂閱/消耗型購買；正式年齡與資料申報未定。
- 只有確實需要換對話才提醒；一般階段完成更新本檔並繼續，不為階段完成要求換對話。

## 目前任務：v0.9.42 聲音修改
- v0.9.41已commit/push至開發分支4839c6a，公開版與原生產物未更新。
- 正在修改v0.9.42：柔和旋律/武器音色、Boss主題切換、重啟音樂競態、音訊亂數獨立及資源回收。
- py_audio_quality已通過；舊v41對照在音訊污染遊戲亂數斷言確實失敗。新舊離線音訊各7段已輸出。
- v42全套49/49：20260909-082740-083723-audio-full/results.json（2工、source unchanged）。CPU4音訊／離線重啟皆過。
- v42 SHA8db9e1206ed2a376c9eb36258f5fd4a181f0c235f122bf1e435fc445697e833f；效能單獨39.5→39.3FPS（損失0.5%）。
- v42 Commit Summary：v0.9.42: soften audio and restore boss music transitions；提交以git log核對。
- 下一步v43文案：_private/build_v0943.py已準備但未執行；需動態填入章節說明的參數並更新最後Boss名稱測試。

## 已完成：v0.9.41
- 使用者已核可柔和配色與可愛果凍，要求實作及改善Adventure/Candy Shop/Settings。
- 工作分支codex/soft-world-ui；接手基準8c5bebd（v0.9.40）；本版已完成可在本機進行的驗證，提交以git log核對。
- index.html已為v0.9.41：奶油鼠尾草世界、共用新角色、50關路徑、三頁導覽、設定集中。
- 入口為Adventure/Upgrades/Settings，Candy Shop留作強化頁標題；切頁與Back保留選關、商品捲動。
- 8新key×11語言；各語言241keys，預設英文；未改玩法、數值、卡池、商店價格或存檔格式。
- 設定音效是既有本次執行開關，尚未增加持久化欄位。
- 市場與導覽研究、規格見docs-15-performance-and-art-direction.md；概念稿不等於出貨遊戲。
- 最終遊戲SHA256：421212514bc35e36f9ea0b1d38d0b0deb2112524d2b5d40a4e2896b4d249ac51。
- Commit Summary：v0.9.41: introduce soft visuals and clear hub navigation

## 驗證與發布限制
- 第一輪完整4工45/48：20260909-073913-224767-soft-full/results.json，source unchanged。
- 失敗：py_card_hp_weight導頁30秒逾時；py_nuke_calm期待舊主角色碼；效能對照11.4FPS測不到。
- 已修：畫素測試同步核可色碼、保留原門檻；Back保留選關；升級標題對比8.03:1。
- py_soft_ui新增至預設套件：11語言×4尺寸×3頁＝132組，設定／切頁／零強化遊戲通過。
- 最終完整2工48/48通過：_private/test-runs/20260909-075803-379699-soft-final/results.json，source unchanged。
- CPU4新UI132組／離線重啟存檔通過，pageerror0、外部請求0；soft-cpu4.log與soft-offline.log。
- 原套件py_lv5_stress（CPU4、零強化）通過；第1關bot45秒3/3心通關、第2通關、第3陣亡參考。
- 原效能門檻單独45.5→45.1FPS、同伴損失1.0%，未改門檻。
- 截圖_private/test-artifacts/soft-menu.png、soft-game.png、soft-upgrades.png、soft-settings.png、soft-cards.png。
- 上輪48工讓Surface失去回應並導頁逾時；本機不再重試。2/4工不替代全平行驗收。
- 全平行壓力需更充足測試主機，仍未完成；不得宣稱三輪全綠或據此發布。
- 本版未推Pages/itch.io、未重建APK/AAB、未在Pixel實測美術或效能。

## Pixel效能與測試工具
- adb最後無装置；卡頓對應新/舊App或網頁、版本/關卡/情境尚不明。不可用桌機否定真機回報。
- 單獨診斷py_art_perf：固定v40/v41同批三輪，沒有殘留headless程序（唯讀程序檢查）。
- paired FPS 24.92/25.29、16.83/16.35、37.57/37.71；兩版同步波動，不宣稱真機改善。
- 證據_private/test-artifacts/art-perf-20260909-075543/results.json；不取代原30FPS門檻。
- .venv Python Playwright1.62、GOO_BROWSER_CHANNEL=msedge；NODE_PATH指_private/test-node/node_modules。
- run_tests.py讀run_tests.sh清單，效能放最後單獨跑；完整指令見tests/README.md。
- 既有py_render_profile/py_perf_capacity/py_perf_baseline皆為診斷；原先47套件46/47不是新版驗收。

## 使用者新增的後續工作（逐項、分版）
1. 研究並修改背景音樂與射擊等音效；下一版先做聲音，保持原創、離線、零執行期相依。
2. 研究怪物名字的跨語言理解，必要時重新命名；固定ID、11語言同步。
3. 逐項核對11語言語意／數值／術語。完整key及排版通過不代表母語自然或全部精準。
4. 研究難度曲線、局內卡與寶箱、糖果屋增益；測零強化／合理累積／全滿強化，固定輸入同批比較。
5. 特別查滿級糖果屋仍卡關：先分清增益未生效或強度/操作需求問題，不盲加無限強化。
- 已實跑發現Boss出現仍theme=cute；musicIntensity只加BPM，Boss分支未觸發。audio-theme-baseline.json有證據。
- 音訊新舊取樣audio-v0941／audio-v0942-final；工具tests/render_audio_samples.py；研究見docs-16-audio-localization-and-balance.md。
- 已發現lv10d仍說第一章／每10關Boss，與v23後每5關一章不符；命名多為生僻詞。尚未修改。
- 初步來源及診斷筆記在_private/next-work-notes.md；正式實作後寫歷史，不把研究宣稱已完成修改。

## 原生與商店現況
- 現有實際APK/AAB仍v0.9.40，SHA cc7e50fcb9d87979be694c413c0b6173af0435c4647a2166b599aef10e267d6b。
- appId com.demjastudio.gooblaster；debug APK4,261,164bytes，未簽AAB3,112,351bytes；JDK21/SDK36。
- Pixel曾飛航離線、Preferences存檔、強制停止冷啟動通過；與舊io.itch.davidform.gooblaster並存，未覆蓋。
- native/BUILD-WINDOWS.md、prepare_android.py、audit_artifacts.py、test_device.cjs及backup_android.py可重做。
- 原生android/仍Git忽略；本機73檔來源ZIP不是異機備份，獨立原生遠端repo未建。
- 尚未執行簽章AAB派生安裝、升版/重裝/系統備份恢復、完整網路稽核、Play Console與iOS。
- butler15.31已授權但從未首次推送；itch目前goo-blaster-v0.9.31.html、尚無butler頻道。
- tools/publish_itch.cjs --push的SHA參數只核bytes，不會代替測試驗收。
- 公開隱私政策已驗HTTP200且與本機一致：https://davidform.github.io/goo-blaster/privacy.html。
