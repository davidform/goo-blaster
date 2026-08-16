# GOO BLASTER

頂視角單指果凍射擊遊戲的可玩原型。單一 HTML 檔，無外部相依。

**線上試玩**：部署完成後網址是 `https://<你的帳號>.github.io/<repo名>/`

---

## 一次性設定（約 5 分鐘，手機也能做）

1. 到 GitHub 建立一個新的 repository，取名例如 `goo-blaster`，設為 **Public**
   （Public 才能免費用 GitHub Pages）
2. 把這個資料夾裡的所有檔案上傳到 repo 根目錄
   （網頁版：repo 頁面 → `Add file` → `Upload files` → 拖進去 → `Commit changes`）
3. repo 頁面 → **Settings** → 左側 **Pages** → **Source** 選 **GitHub Actions**
4. 等 1～2 分鐘，Actions 頁面顯示綠勾後，網址就會生效

## 之後每次更新

把新的 `index.html` 覆蓋上去 commit 就好，Actions 會自動重新部署，
**1～2 分鐘後手機重新整理就是新版**。

手機上也能做：GitHub 網頁版 → 進到 `index.html` → 右上鉛筆圖示 → 貼上新內容 → Commit。

## 加到手機主畫面（像 App 一樣開）

用手機瀏覽器開上面的網址後：

- **iPhone（Safari）**：分享鈕 → 加入主畫面
- **Android（Chrome）**：右上選單 → 安裝應用程式／加到主畫面

裝好之後是全螢幕、沒有網址列，操作手感跟正式上架的 App 幾乎一樣。

## 檔案說明

| 檔案 | 用途 |
|---|---|
| `index.html` | 遊戲本體（單檔，含所有程式、音效合成、美術） |
| `manifest.webmanifest` | PWA 設定，讓「加到主畫面」變成全螢幕 App |
| `icon-192.png` / `icon-512.png` | 主畫面圖示 |
| `.github/workflows/pages.yml` | 推 main 就自動部署 |
| `.nojekyll` | 告訴 GitHub Pages 不要跑 Jekyll 處理 |

## 版本確認

主畫面最下面那行會顯示版本號（例如 `v0.9.3`）與觸控診斷資訊。
如果懷疑手機讀到舊版，比對這個數字就知道。

## 為什麼要用網址而不是直接開 HTML 檔

用 `file://` 直接開本機 HTML 時，行動瀏覽器會限制不少能力，
而且從檔案管理員／聊天軟體開啟時，常常是被某個 App 的內建預覽器接手，
觸控事件可能被它自己的手勢攔截。改用 `https://` 就沒有這些問題。
