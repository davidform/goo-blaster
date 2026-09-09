# 遊戲工作室系統 v1

往後可以直接說：**「我要做一款……，沿用遊戲工作室流程。」** 不必重貼整份 GOO BLASTER 指令。共用 skill 支援自动選用；若新對話沒有顯示，可明確說「使用 $game-studio」。每個新專案仍有自己的 AGENTS.md、設定與交接，不依賴對話記憶。

現在已提供：

- [共用開發流程](game-studio/SKILL.md)：接手、實作、驗證、手機測試與交接。
- [架構與分工原則](game-studio/references/architecture.md)：玩法與平台服務分界、何時用多 agents。
- 專案初始化工具：建立身分、語言、驗證欄位、交接與原始想法，不複製前作存檔或簽章。
- [現有遊戲設定](../studio.project.json)：保留 GOO BLASTER 的實際技術與授權。
- [發版後更新日誌](../native/DEVLOG-PUBLISHING.md)：已授權的GOO專案自動整理中英文案、核對公開版本、發布及防重複；其他新遊戲仍需自己的授權。
- [可選的 ChatGPT 簡報](game-studio/references/idea-brief.md)：可以先討論構想再帶回來，但不必多跑一趟。

這是開發流程與專案架構的第一版，不是已完成所有玩法的通用引擎，也不是無人確認就會自動上架的服務。

## 初始化與檢查

代理收到新想法後，先確認合適的目錄與新的 App 身分，再執行：

```powershell
python studio/game-studio/scripts/studio.py init --target <新目錄> --id <遊戲代號> --title <遊戲名稱> --app-id <新的App身分> --idea <原始想法>
python studio/game-studio/scripts/studio.py check --root <專案目錄>
```

初始化拒絕覆寫已有目錄，也拒絕新遊戲沿用 GOO BLASTER 的 App 身分。`check` 只驗證設定，輸出明列 `tests_executed: false`；缺少遊戲產物與測試命令不會被說成測試通過。App 身分在封裝／上架前仍要確認未與其他作品重複。

設定中的測試命令是參數陣列，代理依專案規則執行；此工具不偷偷啟動外部服務或發布。GOO 的 `edges` 是目前改動的入口，任務改變時需更新；`stress`／`device` 尚未完成的限制明列，不能拿初始化檢查取代。

本目錄是可版本管理的 skill 原始來源；本機已安裝至 `C:/Users/Surface/.agents/skills/game-studio`，其他專案也能探索使用。後續修改先在本專案驗證，再同步安裝副本；不改使用者其他技能或全域 AGENTS。官方文件說明技能會自動被偵測；若介面未出現，重啟 Codex 後再確認。安裝檔案驗證不等於每次自動選用都已被實測。

官方參考：[Skills](https://learn.chatgpt.com/docs/build-skills)、[Capacitor 原生功能](https://capacitorjs.com/docs/v7/android/custom-code)、[Android 檔案選擇與儲存](https://developer.android.com/training/data-storage/shared/documents-files)。

本作Pages同步已於2026-09-10獲授權：依[native/PAGES-PUBLISHING.md](../native/PAGES-PUBLISHING.md)，同批完成APK、itch、Devlog與Pages；主站只接收已驗證產物。新遊戲不繼承此授權。
