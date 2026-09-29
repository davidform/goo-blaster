# GOO BLASTER 精簡交接

## 目前狀態（2026-09-29，v79完成）
- 使用者要求移除重複回主畫面按鈕，統一放底列並改善手機觸控，已完成本次範圍。
- 分支codex/soft-world-ui；遊戲commit bcb3d0f8ffc214cbd6589e132c04bac963e9e309已push。
- Summary：v0.9.79: unify home navigation in the bottom bar。
- HTML SHA 6c8259ca544dd2087907061a51afa4be3ecdd7dd49cee604508a1883bf8fb538。
- .codex-remote-attachments為使用者附件，不可提交；私人收據僅_private。勿重做v78／v79已完成驗證與發布。

## 改動與決策
- 五格固定底列：冒險／強化／主畫面／庭院／設定，主畫面居中；移除homeHeader與btnShopBack。
- 底列88px加safe-area、至少48px觸控範圍與4px間距；目前頁依aria-current變色，戰鬥隱藏整個導覽。
- 商店整頁捲動並保存位置，取消內層清單；內容末端與庭院就地面板不被底列遮住。
- 11語言新增navHome短標籤，由i18n/build_v0979.py生成；無玩法、倒數、價格或存檔格式改動。
- AGENTS第25／27節記錄新決策，取代舊頂端返回要求。設計／根因見docs-22-bottom-navigation.md及docs-14-history.md。

## 已驗證
- 完整：_private/test-runs/20260929-182818-349067-bottom79-full/results.json，首輪85/86；唯一舊捲動測試失敗保留。
- 補跑：_private/test-runs/20260929-185020-589524-bottom79-cpu4-retry/results.json，三項全PASS且SHA未變，合併86/86。
- py_ui_fixes改測shop整頁真實滑動，scrollTop129；CPU4底列160.8秒／庭院就地面板196.8秒。
- 新py_bottom_nav：44版面（11語言×4尺寸）、220次真實tap、唯一中央首頁、顏色、末項可達、三主題中途返回、存檔隔離。
- 未改v78實跑新測試FAIL，證據_private/baseline78-bottom/regression.log；邊角182213-bottom79-edges四項PASS。
- py_test9第1／2關54／64秒通關，第3關90秒陣亡；硬門檻第1關PASS，沒有冒稱全通。test9長模擬346.7秒PASS。
- 效能獨立47.8→49.5FPS（+3.6%量測波動）PASS；不與Android建置同跑，0JS錯誤。
- py_release_smoke CPU4／離線／新存檔／真實重開PASS，還原progress9 coins456 meta.dmg2 selection8，0錯誤／0外部請求。
- CUA本機強化→首頁→池塘→開始→移動魚→首頁成功；中英實際新存檔截圖store/screenshots/v0.9.79已目視且附manifest。
- 環境：.venv/Scripts/python.exe；GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。

## 已交付
- APK97900／0.9.79-test.0，applicationId及簽章延續；實際APK內HTML／簽章核對。
- APK SHA755559421f431e33d266d5bc57eb3552ad9a15c66f7090ed160bc1080ef6a10a；公開資產597990169重新下載核對。
- 固定入口：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- itch build2035414/upload19167726 Active，_private/mobile-test/itch-v79.json；完整payload一致，實際開始／暫停與底列返回PASS。
- Pages部署0246bf171e506d5b8c45a4498efe0f6ad2a5ba52，Actions36558941043成功；公開SHA及實際開始／暫停PASS，pages-v79.json。
- 中英Devlog已Published並record，9項工作流程測試PASS：https://davidform.itch.io/goo-blaster/devlog/1682140/v0979-one-home-button-within-thumb-reach。
- 商店介紹／新截圖30370495、原公告17090045／profile均已公開核對；所有段落／兩個連結／六圖完整，store/page-sync/v0.9.79.json。
- 商店前三張保留原combat，v79介面圖第四。論壇圖片庫限近期10張，原3張combat由v64原檔重傳，仍明確為歷史圖，未刪舊資產與回覆。
- 論壇HTML貼上／fill失效曾產生空白或重複草稿，均未Save；明確清空→確認→高階CUA typeText→工具列重建連結／圖片後完成。見native/ITCH-PUBLISHING.md實測補充。
- cleanup先dry-run後Apply，移除4項釋放26,930,141 bytes，0失敗／25項AccessDenied略過；保留v79／v78 APK與進度、簽章、測試證據。

## 未執行與限制
- 本次ADB無裝置，Pixel尚未覆蓋更新；使用固定APK入口更新，不卸載或清資料。
- Surface依既定限制未跑全平行；CPU4不冒充全平行。真人手持舒適度／市場／母語潤稿仍需實際回饋。
- 預設單代理；本次沒有新增研究提案中的玩法／行銷活動，沒有調價或正式商店送審。
- 小鎮是原創小型場景，不以自動測試或布局宣稱已達參考作品的內容量或市場驗證。
