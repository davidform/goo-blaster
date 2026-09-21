# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者要求盡力完善糖果庭院；v69已實作生產／委託／建設循環，最終完整77項、CPU4與離線已過，發布準備中。
- 分支codex/soft-world-ui，接手7279223，pull已最新。未追蹤附件不可提交。
- BUILD v0.9.69，SHA b79b3cb1442f75d58975c3f2c733aa5a816d9a87d151e506d5b26e584c505838。
- 預定Summary：`v0.9.69: complete the garden production and village loop`。
- 單代理；單檔離線，47新增key×11語言；不使用付費工具或外部執行相依。

## 已實作
- 每株另給1食材，三食材＋三成品pantry各9999，旧進度保留。
- 薄荷茶1薄荷、果醬2莓果、月光派各1作物；立即製作，小屋0/1/2級解鎖。
- 三居民訂單每次1/2/3份輪替，每份1/6/10累積聲望。永不過期；同序號只可交付一次。
- 每3交付升友誼，最高3。幫助過的居民出現場景；既有六訪客布置保留。
- 六建設3/8/16/28/44/64：甜點店／涼亭／噴泉各兩階；後期需莓果/月光及三居民各3交付。
- 聲望不扣除，不給戰鬥屬性；戰鬥source段比對相同，既有作物倒數／花瓣／修屋成本皆不變。
- 缺料可前往種植；明列配方／庫存／解鎖與建設條件，收成告知食材用途。
- 新提示以key保存料理／人名，切語系時重新翻譯，避免混語。
- 設計與研究docs-17-garden-loop.md；原創Canvas新增三建築sprites。

## 測試與證據
- 新py_garden_village全新UI循環：12輪種植、兩次修屋、料理各6、三居民各3交付、102聲望、六建設。
- 等待用明示加速時鐘；原數值作物等待34分鐘，非真人時間實測。
- 初輪village69-first六項PASS，village69-loop一項PASS，scene兩項PASS（早期SHA）。
- CPU4舊SHA3454三項PASS；舊offline 0errors/0external，progress9/coins456/dmg2重開保留。
- village69-final因提示切語言修正主動停止，非完整驗收，原報告保留。
- 最終完整：_private/test-runs/20260921-212620-354209-village69-final2/results.json（77/77 PASS，無補跑）。
- 最終截圖、offline與CPU4三項已過（20260921-212730-432280-village69-final-cpu4）；_private/village69/verification.json彙整。
- store/screenshots/v0.9.69可達成fixture與來源manifest；不是玩家戰績／手機效能證據。
- 全平行不跑（Surface限制）；Pixel真機未驗證。效能必須独立，不與建置並跑。

## 待交付
- 最終同SHA完整77項／CPU4三項／offline已過；獨立效能單局34.1FPS、同伴相對0.0%，非Pixel。準備commit/push。
- Android同簽章固定測試通道、itch html5公開payload/啟動、Pages指定commit/Actions/公開SHA/啟動。
- store/page-sync/v0.9.69-description.html與store/devlogs/v0.9.69-notes.json已準備。
- Chrome CUA編輯頁tab1912753873已開，未修改；不要寫到舊使用者編輯tab。完整驗證後才發布頁面/Devlog。
- 同步新村莊截圖第4張，保留前三戰鬥。Devlog先查文章與草稿，防重複。
- 最後白名單清理保留最新/前版APK、存檔、簽章、證據；權限拒絕profiles不改ACL。

## 其他未完成
- 原論壇首文v65自動核准拒絕仍待明確授權，未重試；保留歷史相簿。
- 養動物／更多食譜／多區域／居民生活AI未做；單機可改裝置時鐘，不宣稱防作弊。
- 真機長時FPS、母語潤稿、玩家樂趣與市場付費驗收未完成。
