# 測試腳本

用 Playwright 驅動真實遊戲迴圈的整合測試，不是單元測試。

## 怎麼跑

```bash
npm init -y
npm i playwright
# 容器內已有 Chromium 就不用再 install；本機第一次要跑：
npx playwright install chromium

node test9.js
```

腳本裡的路徑是 `file:///home/claude/goo-blaster/index.html`，
在自己的環境要改成你的 `index.html` 實際路徑。

## 最重要的一支：test9.js

裡面有一個刻意寫得很笨的 bot（只感知 170px 內的敵人、完全不看子彈、
升級卡隨機亂點、幾乎不按加速鍵），代表「第一次玩的小朋友」的操作水準。

**第 1 關的驗收標準：這個笨 bot 必須零失誤通關。**

每次調整難度數值後都要重跑，確認這條標準還成立。
目前實測：第 1 關 48 秒通關、愛心一顆沒掉；連續闖關可過 1–5 關、死在第 6 關。

## 其他

| 檔案 | 驗什麼 |
|---|---|
| `test5.js` | 多點觸控、加速鍵冷卻、愛心與死亡、慈悲無敵、實戰闖關、FPS |
| `test6.js` | 音效系統、果凍覆蓋率→傷害、升級卡池、遊戲速度、各卡機制 |
| `test8.js` | 關卡數值曲線、寶箱生成距離與七種效果 |
| `test10.js` | 模擬 TouchList 不可迭代、Web Audio 接線圖 |
| `test11.js` | 舊存檔殘留、循序解鎖、endGame 重入、觸控漏事件自我恢復 |
| `testaudio.js` | 攔截 AudioContext 統計音樂排程速率 |
| `testlead.js` | 相機前瞻平滑度 |
| `prof3.js` | 真實遊戲峰值 FPS 與 GPU 資訊 |

## ⚠ 模擬環境的極限

**合成的 `TouchEvent` 在 Chromium 裡的行為和真機不同。**
用 `new TouchEvent({changedTouches:[t]})` 建出來的物件，
無法真實重現 iOS Safari 的 TouchList 行為。

曾經因此誤以為證明了某個假設 —— 實際上沒有。
做行動裝置相容性驗證時要意識到這個極限，最終還是要真機測試。
