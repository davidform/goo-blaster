# itch.io 固定同步流程

2026-09-09 使用者授權：往後遊戲改動完成驗證後，直接同步既有 itch.io 遊戲，不再逐次詢問。此流程與 Android 測試 APK 一起執行；不是背景自動排程。

- 公開頁：https://davidform.itch.io/goo-blaster
- 編輯頁：https://itch.io/game/edit/4906809
- 固定通道：`davidform/goo-blaster:html5`
- Butler：`_private/butler/butler.exe`；使用既有登入，不輸出／記錄 token。
- 只傳已驗證的單一 `index.html`。不能上傳整個 repo、`_private`、原生存檔、APK簽章或其他內部文件。

## 每次發布

1. 核對Git、BUILD及完整報告。沿用 `native/build_test_apk.py` 的 `validate_reports` 規則：完整當前套件、全部通過、同一HTML SHA，補跑必須保留原始失敗。不能拿舊版測試替新版。
2. 複製原始位元組至獨立 `_private/itch-builds/<BUILD>/index.html`，核對該資料夾只有這一個檔案且SHA相同；不得另改EDITION或翻譯。
3. 執行（替換實際BUILD）：

   ```powershell
   & _private/butler/butler.exe push _private/itch-builds/v0.9.55 davidform/goo-blaster:html5 --userversion v0.9.55
   & _private/butler/butler.exe status davidform/goo-blaster:html5
   ```

4. 等通道處理完成，開公開頁按Run game，核對版本並實際開始一關／暫停。從實際iframe取得資產網址，下載核對完整遊戲payload與測試SHA。
5. itch CDN可能在結尾追加 `https://static.itch.io/htmlgame.js`。保留原始差異與公開整檔SHA，只能在確定「原始完整payload未變，差異僅平台腳本」後通過，不能任意忽略差異。
6. 記錄upload/build ID、版本、payload SHA、公開資產網址、啟動結果至私人證據與歷史／HANDOFF，commit/push本次文件。
7. 依[DEVLOG-PUBLISHING.md](DEVLOG-PUBLISHING.md)自動產生、核對並發布該公開版本的中英更新日誌，記錄文章網址避免重複。這是2026-09-10新增授權，不必另問；尚未發版的改動不列為已上線。

8. 依[PAGES-PUBLISHING.md](PAGES-PUBLISHING.md)同步同一已驗證版本至GitHub Pages，核對Actions、公開SHA與啟動。

9. 同步頁面介紹與截圖，依下節執行。Butler只更新遊戲檔，不能將上傳成功當成介紹／圖片更新成功。

## 介紹與截圖同步（2026-09-21）

使用者要求 itch.io 遊戲頁自動更新，並指出個人頁仍顯示舊圖。每次已授權發版也須完成下列步驟；這是發版流程，不建立背景排程。

- 範圍：遊戲4906809的介紹／截圖，以及[既有討論串](https://itch.io/t/6826201/50-stages-no-ads-no-gacha-works-offline-my-browser-roguelite-needs-breaking)的開頭貼文17090045。個人頁會引用該貼文，須另外檢查。保留歷史回覆，不每版另發留言洗版。
- `native/prepare_itch_screenshots.py` 只提供介面紀錄，不作為商店主打圖驗收。宣傳圖以 `native/capture_combat_candidates.py` 擷取真實模擬的Boss戰候選，再依AGENTS第15節人工選圖；候選分數不代表圖片已合格。記錄可達成的商店升級設定、來源SHA、局內狀態；不是人類通關或真機FPS證據。遊戲本身不增加相依。
- 先確認公開版本與manifest來源一致，人工檢視每張圖片，再透過已登入瀏覽器上傳。不得以舊圖片改檔名冒充新版，不把測試作弊畫面當玩家成績。
- 介紹只列已公開功能；更新版本、玩法與固定Android測試入口，避免維護易過時的卡牌／寶箱總數。不更改價格、專案身分或公開狀態。
- 開頭貼文原地編輯並註明舊回覆對應舊版本；同步目前圖片。截圖上傳若被瀏覽器權限阻擋，明確記錄未完成，不能宣稱整個頁面同步完成。
- 儲存後重新開啟公開遊戲頁、討論串與個人頁，驗證正文、版本、圖片URL及圖片實際載入。收據放 `store/page-sync/<BUILD>.json`，分別記錄文字／圖片狀態及未完成原因。
- 無HTML改動的補同步不提高BUILD、不重發APK或重複Devlog；仍需核對來源SHA，並實際驗證頁面。

## 已完成的一次性設定

2026-09-09 v55首次建立html5通道；在編輯頁讓新版index.html勾選「This file will be played in the browser」。舊goo-blaster-v0.9.31.html取消網頁遊玩並勾「Hide this file and prevent it from being downloaded」，保留未刪除。之後只推同一通道，不能每版新增不同通道。

現有No payments、公開狀態、Portrait／mobile friendly均保留；使用者此次只授權同步遊戲，沒有要求改價格或其他商店。若需要重新登入或權限失效，完成本地準備並明示卡點，不聲稱發布成功。

官方工具說明：[Butler pushing](https://itch.io/docs/butler/pushing.html)。


## 論壇編輯器實測補充（2026-09-29）

論壇沒有HTML按鈕。若選句替換、HTML剪貼簿或contenteditable.fill造成錯位、空白或重複，先reload保留公開原文，不儲存失敗草稿。v79有效方法：先讀取完整原文／連結／圖片來源；Control+A、Backspace後**讀回確認空白**，再用CUA高階typeText輸入完整文字（換行即段落，勿大量重複空行）。用selectText與Link→Insert link恢復原超連結；Add image逐一恢復图片，最後核對textarea實際提交欄位、所有段落、連結與圖片再Save。

Choose image僅顯示近期十張；老圖片可由已有且已核對的原始截圖檔經Upload image→Pick image重傳，不把歷史圖改稱新版截圖。等Add image對話框真正就緒再等filechooser並點Pick image，避免載入期間逾時。公開profile圖片為lazy loading，實際捲到引用區後再檢查naturalWidth；不能僅因尚未捲到就判定圖片失效。此紀錄是實測處理方式，不保證工具每次相同，仍須逐步核對。
