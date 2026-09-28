# GOO BLASTER 精簡交接

## 目前任務（2026-09-28，v0.9.78驗證中）
- 使用者要求回主畫面按鈕更明顯，難度切換變綠，逐頁修正同類問題。
- 分支codex/soft-world-ui；接手pull already up to date，基準f4882a3／遊戲v77。
- 原未追蹤只有.codex-remote-attachments；不可提交使用者附件。
- 已實作v78，尚未提交／發布。勿重做已完成v77發布。
- HTML SHA 6462ca6a1bf06e14f8fef80c292a9ac8b335f71ad947582fa3844ff3a5c1e4c9，整套執行期間不再修改。

## 改動與稽核
- 三主題難度選取依aria-pressed上色，選中深綠、未選米色；先前按排列位置上色。
- 冒險所選關卡深綠；設定音效開關也依狀態上色。保留即時動作與棋盤的獨立語意。
- 返回鍵48px高／16px白字／箭頭與外框，獨立64px頁首背景避免露出底層HUD。
- 沿用11語言toMenu，無玩法／倒數／存檔／新字串變更。
- docs-21-selection-audit.md逐頁記錄；py_selection_feedback加入完整套件（共85項）。
- 396次难度真實切換，11語言×4尺寸×3主題×3選項；包含其他選取控制及返回。
- 未改v77新測試實跑FAIL，難度2選中仍米色、難度1未選卻綠，已重現問題。
- store/screenshots/v0.9.78中英手機截圖與manifest；新存檔實際UI解鎖池塘前兩階，無注入獎章／資源。
- CUA本機實際玩池塘第一階，回首頁重入難度2綠色、1／3米色，頁首背景目視正常。

## 測試狀態
- 完整：_private/test-runs/20260928-201809-749466-selection78-full/results.json，85/85 PASS、來源SHA不變；效能獨立44.2→44.1FPS PASS。
- CPU4：_private/test-runs/20260928-202245-030853-selection78-cpu4/results.json，context PASS388.6秒、selection PASS423.3秒，來源SHA不變。
- 201737-selection78-edges四項PASS，但過程補頁首背景導致source_unchanged=false，不作最終發版證據。
- py_release_smoke已PASS：CPU4／離線／freshsave progress1 coins0 meta{}，真實重開還原progress9 coins456 meta.dmg2 selection8，0JS錯誤／0外部請求。
- 本批py_test9第1關48秒／第2關62秒通關，第3關54秒陣亡；硬門檻第1關通關PASS，不冒稱全部通關。
- 效能在全套最後單獨執行；Android建置不能與其重疊。
- 使用.venv/Scripts/python.exe，GOO_BROWSER_CHANNEL=msedge，PYTHONUTF8=1，NODE_PATH=_private/test-node/node_modules。
- Surface依既定限制不跑全平行；CPU4不取代全平行。

## 下一步
- 等完整85項、CPU4結束；若失敗保留並診斷，確認來源SHA一致。
- 更新history測試證據，git diff後只commit本次檔案，Summary：v0.9.78: clarify selected options and home navigation。
- 依已授權流程建置APK／公開SHA、itch完整payload與開始暫停、Pages指定commit及Actions／SHA／開始暫停。
- 公開後產生中英Devlog、同步商店介紹與截圖、原論壇17090045及profile引用；不新增留言。
- Chrome商店與Devlog管理頁已讀，最新仍v77，沒有v78草稿。已準備介紹字串但未填入或儲存。
- CUA論壇首文Edit入口https://itch.io/post/17090045/edit，保留原圖與格式，精確替換版本與說明。
- 全部交付後cleanup_local先dry-run再Apply，更新收據／HANDOFF／docscommit。

## 限制與既有入口
- 本次ADB無装置；Pixel尚未覆蓋更新，不卸載／清資料。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test，目前仍v77／97700。
- itch與Pages目前仍v77；未聲稱v78已上線。
- 單代理；真人易用性、聽感、市場與母語潤稿仍需實際玩家回饋。