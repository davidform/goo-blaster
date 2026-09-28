# GOO BLASTER 精簡交接

## 目前任務（2026-09-28，修正與APK完成，網頁同步待平台）
- 使用者要求回主畫面更醒目，難度切換變綠，逐頁修正同類選取問題。
- 分支codex/soft-world-ui；安全pull完成，接手基準f4882a3／v77。勿重做v77發布。
- 遊戲v0.9.78 commit 2cc09a4d025b90825f78a1a8fa66f5ead6e5f6a9已push。
- Summary：v0.9.78: clarify selected options and home navigation。
- HTML SHA 6462ca6a1bf06e14f8fef80c292a9ac8b335f71ad947582fa3844ff3a5c1e4c9。
- .codex-remote-attachments為使用者附件，不可提交；私人收據僅_private。

## 改動與實際驗證
- 三主題難度依aria-pressed上色，選中深綠、未選米色；根因是相鄰按鈕CSS按位置上色。
- 冒險選中關卡深綠；設定音效開關依狀態上色。庭院作物／擺設／訪客／四分類、語言及導覽逐項檢查。
- 返回鍵48px高／16px白字／箭頭及外框，保留64px頁首背景與safe-area；不露出底層HUD。
- 沿用11語言toMenu，無玩法、倒數、存檔及新翻譯字串改動。
- docs-21-selection-audit.md有逐頁清單；新增py_selection_feedback，完整套件共85項。
- 未改v77實跑新測試FAIL，難度2选中仍米色、難度1未選卻綠；最終版本396次難度點擊通過。
- store/screenshots/v0.9.78中英手機截圖與manifest。池塘前兩階實際UI通關後選難度3，未注入成績。
- CUA本機實際玩池塘第一階，回首頁重入難度2變綠、1／3米色，返回頁首目視正常。

## 測試證據（完成，不重跑）
- 完整：_private/test-runs/20260928-201809-749466-selection78-full/results.json，85/85 PASS、來源SHA不變。
- CPU4：_private/test-runs/20260928-202245-030853-selection78-cpu4/results.json，兩項PASS且SHA不變；context388.6秒、selection423.3秒。
- 201737-selection78-edges四項PASS但過程補頁首背景，source_unchanged=false，不作發版證據。
- py_release_smoke已PASS：CPU4／離線／freshsave progress1 coins0 meta{}，瀏覽器真實重開還原progress9 coins456 meta.dmg2 selection8，0JS錯誤／0外部請求。
- py_test9第1／2關48／62秒通關，第3關54秒陣亡；硬門檻第1關PASS，不冒稱全部通關。
- 最後獨立效能44.2→44.1FPS（-0.2%）PASS，無JS錯誤；不與Android建置同跑。
- .venv/Scripts/python.exe；GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。
- Surface依既定限制不跑全平行，CPU4不取代全平行。

## 已完成交付
- Android v78／97800／0.9.78-test.0，applicationId及簽章與上一版相同，實際APK內HTML SHA核對。
- APK SHA 0edd3af57f8998728fca0d7eb6184f27014f871a49a18c640191eb2d0c15f3fb。
- 固定入口：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- _private/mobile-test/published.json public_download_verified=true；資產595389199，已重新下載驗SHA。
- 本次ADB無裝置，Pixel尚未更新；不卸載／不清資料。

## 網頁同步卡點與下一步
- Butler已成功上傳唯一index.html至固定html5通道，pending build2029949／upload19167726；不重複上傳。
- 20:51台北時間Butler及itch通道UI仍Processing v78，Active仍v77/build2018911。
- CUA公開Run game實際仍載入https://html-classic.itch.zone/html/19167726-2018911/index.html?v=1790409730。
- _private/mobile-test/itch-v78-pending.json明列尚未驗證；不可拿pending當已公開收據。
- 下一步先butler status；完成後從公開Run game實際iframe取得新URL，再native/verify_itch_payload.py核對完整payload並實際開始／暫停及選取色。
- 公開驗證通過後，依native/PAGES-PUBLISHING.md使用上述遊戲commit＋完整測試＋itch收據，完成Pages Actions／SHA／開始暫停。
- 接著中英Devlog、商店介紹與截圖、原論壇17090045及profile引用，最後cleanup_local先dry-run再Apply。
- Pages、Devlog、介紹／截圖／論壇／profile、清理本次均尚未完成，不宣稱全部平台更新。
- 商店與論壇均未Save v78，已reload核對公開原文仍v77；論壇5張原圖保留。
- 論壇selectText後按鍵／paste這次會刪除選句卻把新字插到編輯器開頭，p.fill也錯位；未提交。後續先量測焦點與游標，不能盲目重複或整份覆寫丟失圖片。
- Devlog管理頁目前最新v77，沒有v78草稿。原論壇編輯入口https://itch.io/post/17090045/edit。

## 限制
- 單代理；真人易用性、聽感、市場、母語潤稿、Pixel覆蓋更新與真機長時效能仍待實際回饋。