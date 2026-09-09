# 發版後 Devlog 流程

使用者於2026-09-10要求自動處理itch.io的New devlog。本作發版工作包含產文、核對、公開發布與保存網址；不需每次另問。這是代理執行發版時的流程，沒有常駐服務或定時排程。

## 觸發與內容

- 先依ITCH-PUBLISHING.md完成遊戲公開payload與Run game驗證，再發布對應版本文章。v58尚未發版時不能以「v58已上線」發文。
- 同一批交付可合併數個內部版本成一篇，以最終公開BUILD為準；不每個commit通知玩家。
- 預設English＋繁體中文，簡短說明玩家感受到的改動與回饋重點。11語言規則針對遊戲字串，不要求Devlog一次發布11篇。
- 一般更新選General Update or Announcement。不要加入私密測試資料、手機存檔、憑證，或把bot結果寫成真人勝率。
- 權限只適用本作。未來其他遊戲可沿用流程，但需該專案自己的發布／Devlog授權。

## 準備

1. 將玩家文案寫為store/devlogs/<version>-notes.json，格式參考v0.9.55-notes.json。版本必須來自已驗證itch收據，不是直接抄root的BUILD。
2. 執行：

   ```powershell
   python native/devlog.py prepare --release _private/mobile-test/itch-v55.json --notes store/devlogs/v0.9.55-notes.json
   ```

   工具輸出post.json與body.html；阻擋版本不符、未驗證的公開遊戲與同版不同payload。文章一旦已發布，不靜默改寫內容或建立第二個網址。
3. 先讀post.json，再透過已登入瀏覽器開Devlog管理頁，檢查公開文章及草稿。已有同版文章就核對／補登收據；已有草稿就續編。不要因工具逾時就重建文章。

## 瀏覽器發布（使用CUA，非隱藏API）

- 從遊戲頁New devlog或管理頁Write a new post進入，填標題、選一般更新。
- HTML模式填body.html，回可視編輯器。檢查實際送出欄位textarea[name="post[body]"]非空，且所有段落完整。
- 實測HTML模式fill後，畫面已有內容但送出欄位可能仍空。改在可視contenteditable末尾用真實按鍵輸入空格再Backspace，觸發同步，再讀取欄位核對。不得以隱藏腳本直接送表單。
- 附件只保留對應公開版本；移除本篇重複附件，不刪除遊戲檔。語言選English、Chinese (Traditional)；第一個選取後輸入框可能不再有Optional名稱，需看新DOM。
- 先Save為草稿，確認正文、版本附件及中英內容；再Edit post勾Published、Save。這是內部核對步驟，不是另一次使用者核准。
- 等到公開頁Published標示，核對標題與每個內容段落。Save按鈕暫時disabled或舊Errors殘留不代表新請求已失敗，先讀新狀態，勿重複送出。
- 不另發社群貼文、電子郵件或留言；本授權是遊戲Devlog，包含平台本身可能的追蹤者通知。

## 留下收據

將瀏覽器實際讀到的url、title、body_text與published:true保存到私人receipt.json，不從預期文案生成假證據。

```powershell
python native/devlog.py record --post store/devlogs/v0.9.55/post.json --receipt _private/mobile-test/devlog-v55-receipt.json
python tests/test_devlog_workflow.py
```

工具核對正確專案網址、已公開狀態及每一段正文後才標記published；相同收據重跑不新增文章。最後commit/push本次文案與收據摘要，更新HANDOFF並回報公開網址。

工具負責本地產文與防重複，瀏覽器操作及公開狀態查核由當次代理執行；不能宣稱Python本身已登入或自動呼叫itch發文API。登入失效時保留草稿／既有網址並回報，不重複發文。
