# GOO BLASTER 精簡交接

## 目前任務（2026-09-22）
- 使用者要求先實玩v70再選單一改善，不重做v70發布／完整驗證。接手HEAD20d19b8、分支codex/soft-world-ui，pull已最新；附件.codex-remote-attachments不提交。
- 已實玩種植收成／野餐／池塘拾珠／星光，取捨見docs-18-garden-feedback.md；v0.9.71只改善操作因果與主題回饋。
- 野餐保留已送料理與落盤／錯誤動態；池塘可走箭頭、漣漪、貝殼珍珠收集槽；星光連動虛線與亮燈數；終局保留棋盤並停止輸入。
- 900ms動態不鎖輸入、支援減少動態；4key×11語言；feedback不存檔，不改資源／難度／戰鬥。三階後內容深度仍待後續改善。
- SHA `51dae94f04efa369f6e85a8dee6b0a66c1f5fd625aea5898b98091c94dc47921`；待提交Summary：`v0.9.71: clarify themed garden challenge feedback`。
- 完整79/79 PASS無補跑：_private/test-runs/20260922-131921-531042-feedback71-full/results.json；初輪3/3在20260922-131658-124382-feedback71-initial。
- CPU4三項全過：_private/test-runs/20260922-134912-526237-feedback71-cpu4/results.json；timer10.8s/feedback39.2s/festival145.6s。
- offline smoke 0錯誤/0外部請求，重開progress9/coins456/dmg2/selection8保留；_private/feedback71/offline.log。新測試對v70在已送料理斷言預期失敗，baseline-test.log。
- 新手三關59/59/90秒通關、3/3、3/3、2/3心；獨立perf單局46.4FPS、同伴+1.3%，非Pixel。
- 三主題真實UI截圖store/screenshots/v0.9.71已檢視，fresh save無資源／徽章注入。新增tests/py_garden_feedback.py，99語言尺寸、免費／終局／重開／減少動態。
- 下一步：本版commit/push、APK／itch／Pages／Devlog／介紹截圖同步及清理；沿用native各發布流程，不重做v70。文案store/devlogs/v0.9.71-notes.json已備，尚未發布。
- Windows沙箱啟動1909失敗；既有測試程序正常完成，後續命令走require_escalated核准。全平行、Pixel與長期耐玩性未驗證。

## v70既有玩法／固定決策
- 村莊小冒險：野餐記憶3/4/5道料理；池塘5×5三珍珠到旗幟，步數最短路＋4/2/0；星光3×3相鄰翻轉、無步數限制。
- 三種玩法各三階，成功後重玩改序列／旋轉／打散；免費、失敗不扣材料、不加戰力、不限每日次數。
- medals/outings/theme存檔，舊存檔零／原庭院；徽章解鎖主題，更多徽章增加裝飾，完成防重複領取。
- 野餐旗幟與餐盤／游魚池／星燈夜色；種植搖葉、廚房蒸氣、建設小槌、居民跳動、游魚與星光SVG。
- 遵守減少動態設定，單檔離線；29key×11語言，預設英文。
- 新挑戰無被動等待；作物倒數、建設即時完成、料理／修屋成本保留。戰鬥段逐字比對相同。
- 既有v69生產／訂單／六建設不改，全部等待顯示时间規範見AGENTS第20節。
- 不是農場動物／地圖擴張，不能宣稱已證明長期留存或付費吸引力。

## v70歷史測試（不當作v71證據）
- 初輪timer/i18n 2/2，festival-loop九挑戰21.1s；舊SHA，僅歷史。
- 最終SHA edges5/5：cjk12.6/world12.2/layout27.1/village25.8/festival24.2秒。
- 完整回歸_private/test-runs/20260921-224139-214971-festival70-final/results.json，78/78 PASS無補跑。
- CPU4 _private/test-runs/20260921-224444-799807-festival70-cpu4/results.json：3/3過，world124.2/timer26.0/festival431.0秒。
- offline smoke已過：0JS錯誤/0外部請求，CPU4、重開progress9/coins456/dmg2/selection8保留；_private/festival70/offline.log。
- 新test py_garden_festival：九次UI解題、免費重試/錯誤輸入/重複完成、保存/重開/備份/合併、99語系尺寸版面、減少動態。
- 新手py_test9第1關58秒2/3心通關、第2關58秒滿心；第3關102秒陣亡，非硬門檻；0JS錯誤。
- 截圖native/capture_garden_festival.py與store/screenshots/v0.9.70。明示可達成fixture，真實操作後畫面，非真人紀錄／Pixel測試。
- 全平行未跑（Surface限制），ADB空，Pixel未安裝／效能未驗證。彙整_private/festival70/verification.json。

## v70已交付收據（不重做）
- 遊戲commit e1e2de920a1ca35a81a3ac912fa404d11320f5ba已push；Pages部署commit a1f652cd8b5643be79479347858815d1695f80e7。
- Android 97000 / 0.9.70-test.0，同原簽章；公開下載SHA 417035e56504081e81cf03e10a159e6cee3d4ab7c7971d8ea147dc2b57ba7db8，asset579270925。
- 固定手機入口 https://github.com/davidform/goo-blaster/releases/tag/android-test；ADB未連線，未安裝Pixel，保留進度。
- itch build2001061/upload19167726；完整636006byte payload一致、實際開始與暫停通過；_private/mobile-test/itch-v70.json。
- Chrome首次載入曾截斷於字典，重新取得後完整；公開下載逐byte相同，非程式碼錯誤，不能掩蓋初次失敗。
- Pages Actions35618312729成功；完整SHA與公開開始／暫停通過，_private/mobile-test/pages-v70.json。
- itch頁v70介紹與首四圖已驗證；前三戰鬥保留、新池塘實玩30157101第四、13歷史圖保留；store/page-sync/v0.9.70.json。
- Devlog1672102 Published，中英正文／v70附件／新截圖已核對；store/devlogs/v0.9.70/post.json，流程unit9/9。
- https://davidform.itch.io/goo-blaster/devlog/1672102/v0970-three-new-ways-to-play-in-the-village
- 清理先遭審查因未列完整路徑拒絕；補核對後獲准移除v68APK與本輪release-profile-wpn5b_g7，共13716306bytes；保留v70/v69，25舊profile未動，0失敗。
- 獨立perf66.6s通過：單局58.5FPS、同伴-1.0%；非Pixel。最終只補文件收據，不再改遊戲。

## 其他未完成
- 原論壇首文v65自動核准拒絕仍待明確授權，未重試。
- 動物／更多料理／多區域／居民生活AI、母語潤稿、真機長時FPS及玩家耐玩性驗收未完成。
- 舊25個拒絕存取測試profile保持原狀，不改ACL；玩家進度、簽章與備份不可刪。
