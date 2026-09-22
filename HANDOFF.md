# GOO BLASTER 精簡交接

## 目前任務（2026-09-22）
- 使用者要求先實玩v70、再選單一庭院改善，不重做v70發布／整套驗證；本輪已完成v0.9.71實作、驗證與交付。
- 分支codex/soft-world-ui；遊戲commit9011350de5a5de9589b4377f9acc2ba630abd485已push。
- Summary：`v0.9.71: clarify themed garden challenge feedback`。
- 原始碼SHA 51dae94f04efa369f6e85a8dee6b0a66c1f5fd625aea5898b98091c94dc47921。
- .codex-remote-attachments為使用者附件，不提交。v70既有發布不重做。

## 實玩與固定決策
- 先實玩v70三田種植／收成、野餐一階、池塘拾珠與星光一階；發現操作結果只剩數字／勾號、可走格不可辨、連動範圍未保留。
- 取捨見docs-18-garden-feedback.md；只改善操作因果／主題回饋，三階後內容選擇不足留待另一版。
- 野餐保留已送料理、落盤／錯誤動態，答案不提前透露；池塘可走箭頭、魚漣漪、貝殼珍珠收集槽。
- 星光亮燈數與上次連動虛線；終局保留棋盤並禁止輸入。900ms動態不鎖操作，減少動態仍有靜態資訊。
- 4key×11語言由i18n/build_v0971.py產生；feedback不存檔，不改難度／資源／種植時間／戰鬥。
- gardenScene到檔尾與v70逐字相同（正規化換行），原字典內容不變。不宣稱新增挑戰或已證明長期耐玩。

## 已驗證
- 完整79/79無補跑：_private/test-runs/20260922-131921-531042-feedback71-full/results.json。
- 初輪3/3：20260922-131658-124382-feedback71-initial；CPU4三項全過：20260922-134912-526237-feedback71-cpu4。
- CPU4 timer10.8s/feedback39.2s/festival145.6s。新test py_garden_feedback：送餐、隱藏答案、錯誤菜、方向／拾珠、連動、终局、重開、99語言尺寸與減少動態。
- 新測試對v70於已送料理斷言預期失敗，證明能抓舊缺口；_private/feedback71/baseline-test.log。
- offline.log：0JS錯誤/0外部請求，CPU4，重開progress9/coins456/dmg2/selection8保留。
- py_test9第1/2/3關59/59/90秒通關，3/3、3/3、2/3心；獨立perf46.4FPS，同批同伴+1.3%，非Pixel。
- 截圖store/screenshots/v0.9.71，已檢視三面板及上傳縮圖；全新存檔UI操作，無資源／徽章注入。
- 彙整_private/feedback71/verification.json。遊戲測試無失敗；工具沙箱曾1909，後續命令經require_escalated核准執行。

## 已交付
- Android97100／0.9.71-test.0同原簽章，公開下載SHA48245f783d6b09305ac8efe3e8cbf2b41b8678b08ab173dc0dff8908541c5348，asset580691054。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test；ADB無裝置，不宣稱Pixel覆蓋安裝完成。
- itch build2003135/upload19167726，公開完整payload一致（僅平台script後綴），CUA實際開始／暫停；_private/mobile-test/itch-v71.json。
- Pages部署1a5341e337b76e4770eea707f93c8448230d182f，Actions35693149233成功，公開完整SHA與CUA開始／暫停通過；pages-v71.json。
- itch介紹v71、新池塘圖30171953第四，前三戰鬥圖保留、14歷史圖未刪；18圖公開載入。store/page-sync/v0.9.71.json。
- Devlog1672834 Published，完整中英正文／v71附件／新圖經草稿核對；流程unit9/9。
- https://davidform.itch.io/goo-blaster/devlog/1672834/v0971-see-every-move-in-your-village-adventures
- 清理13711759bytes：舊v69APK與release-profile-xnb_ryit，保留v71/v70。25個拒絕存取profile未動，0失敗，不改ACL。

## 未完成／下一步
- 待使用者手機回饋：三主題操作是否更直覺；Pixel安裝／長時FPS、全平行未執行。Surface限制不能以CPU4冒充全平行。
- 長期耐玩性、三階後經營選擇、動物／多區域／居民生活AI、母語潤稿仍未完成。
- 論壇首文17090045及社群個人頁引用仍v0.9.64；舊核准阻擋未解除，本輪只讀核對，未重試修改。
- Windows沙箱帳戶CreateProcessWithLogonW1909；必要命令走工具核准，不繞过權限。
