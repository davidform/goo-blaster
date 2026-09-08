# GOO BLASTER — 原生外殼（Capacitor）

把 `index.html` 包成 Android / iOS App。**這個資料夾要另外開一個 repo**
（見 `AGENTS.md` 第 4 節：E 區塊「原生封裝」跟遊戲本體分開）。

> 2026-09-08 更新：已在 Windows 建出 debug APK 與未簽署 release AAB，並在 Android 真機驗證離線冷啟動與 Preferences 存檔保留。
> 目前可重複執行的指令、產物限制與備份方法見 [BUILD-WINDOWS.md](BUILD-WINDOWS.md)。
> 以下保留原生外殼的一般說明；簽署、AAB 安裝、升版與系統備份恢復仍需另行驗證。

---

## 你電腦上要先有什麼

| 需要 | 給誰用 | 備註 |
|---|---|---|
| Node.js（18 以上） | 兩者都要 | https://nodejs.org |
| Android Studio | 打包 Android | 內含 Android SDK 與模擬器 |
| JDK 21 | 打包 Android | Android Studio 通常會一起裝 |
| Xcode | 打包 iOS | **只能在 Mac 上**。沒有 Mac 就先做 Android |

**建議先只做 Android。** 理由見 `docs-12-上架路線圖.md`：
Google Play 有 12 位測試員 × 14 天的強制等待期，那個鐘要越早開始越好。

---

## 步驟

### 1. 放進遊戲檔案

把最新的 `index.html` 複製到這個資料夾的 `www/` 底下：

```
native/
  www/
    index.html     ← 放這裡
```

⚠ **每次遊戲更新都要重新複製一次**，然後重跑 `npx cap sync`。
忘記做這一步的話，打包出來的還是舊版——這是最常見的錯誤。

### 2. 安裝

在 `native/` 資料夾裡開終端機：

```bash
npm install
npx cap add android
```

### 3. 同步

```bash
npx cap sync
```

`sync` 做兩件事：把 `www/` 的內容複製進原生專案、把外掛（Preferences）接上去。

### 4. 開 Android Studio 打包

```bash
npx cap open android
```

Android Studio 開起來之後：

- **測試機跑跑看**：上方選你的手機/模擬器 → 按綠色三角形
- **產生上架用的檔案**：選單 `Build` → `Generate Signed Bundle / APK`
  → 選 **Android App Bundle (.aab)**（Google Play 要的是 aab，不是 apk）

⚠ **簽章金鑰（keystore）產生之後一定要備份。**
弄丟的話，你**永遠沒辦法更新**這個 App，只能用新的套件名重新上架、
所有既有玩家與評價都拿不回來。備份到雲端硬碟，密碼另外記。

---

## 這個外殼幫遊戲解決了什麼

### 原生儲存（唯一必要的外掛）

`@capacitor/preferences` 會把資料寫進 App 的私有空間，
**不會像 WebView 的 localStorage 那樣被系統當成快取清掉。**

遊戲本體（`index.html`）裡的 `NATIVE_STORE` 會自己偵測：

- 偵測到 Capacitor → 存檔同時寫 localStorage 與原生儲存
- 沒偵測到（純網頁版）→ 完全維持原本的行為，一行都不會變

**你不需要在這裡寫任何程式**，遊戲那邊已經做完了。

### 開機時會發生什麼

1. 先同步讀 localStorage，主選單立刻畫出來（不會有等待畫面）
2. 再非同步讀原生儲存
3. 兩份合併——**進度取高的、糖果幣取高的、買斷狀態只要有一邊是 true 就保留**
4. 需要的話重畫一次選單

第一次在 App 裡跑的時候，如果原生儲存是空的、localStorage 有東西，
會自動把它搬進原生儲存（一次性遷移）。

---

## 買斷解鎖要怎麼接（之後才需要）

如果走「免費下載 + 內購解鎖」，在原生端接好內購 SDK，
**付款成功之後呼叫這一行就好**：

```js
window.GOO_UNLOCK();
```

遊戲會自己把 `prem` 寫進存檔（localStorage 與原生儲存都會寫），
之後所有關卡就解鎖了。

如果走「付費下載」（App 本身就要錢），
`index.html` 裡的 `const EDITION='full'` 維持不動就好，**什麼都不用接**。

---

## 送審前的檢查清單

- [ ] `www/index.html` 是最新版（`Ctrl+F` 搜 `const BUILD=` 確認版本號）
- [ ] 跑過 `npx cap sync`
- [ ] 實機測過：**進度存得住**（玩一關 → 關掉 App → 重開 → 進度還在）
- [ ] 實機測過：**觸控可以移動**（這是 v0.9.4 出過事的地方）
- [ ] 實機測過：**離線可以玩**（開飛航模式再進遊戲）
- [ ] keystore 已備份，密碼已另外記下來
- [ ] 隱私政策網址已經準備好（`PRIVACY.md`，要放到一個公開網址）
- [ ] Play Console 裡宣告了目標年齡層
- [ ] 完成 IARC 內容分級問卷
