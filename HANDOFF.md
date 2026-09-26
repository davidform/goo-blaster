# GOO BLASTER 精簡交接

## 目前任務（2026-09-26，已交付）
- 使用者回報：切到佈置與訪客，綠色仍停在照顧田地；附67707.jpg。
- 本次v0.9.77只修四分類選取狀態與顏色，不改玩法／存檔／倒數／字串。
- 分支codex/soft-world-ui；接手安全pull完成，基準5d5af44；原本僅未追蹤使用者附件。
- .codex-remote-attachments不可提交；憑證、存檔、私密收據僅_private。
- HTML SHA 9d3d464837474274aa1df2fabed6ba0b49d4a09ad0e2c829b8f3ffc024e74627。

## 根因與修復
- CSS first-child硬編碼綠色；gardenArrange未更新aria-pressed。
- 四分類依GARDEN_TAB更新aria-pressed，選中綠色、未選米色，阴影一致。
- 新py_garden_tabs納入完整套件；264次真實切換含11語言／4尺寸，測實際背景色與唯一選中。
- 覆蓋重畫、回首頁重入、建築捷徑、離線；不只檢查DOM屬性。
- CUA Chrome本機逐一點四分類，背景色與頁面狀態一致。
- store/screenshots/v0.9.77/garden-selected-decorate-zh-Hant-390.png已目視核對，manifest有SHA及真實新存檔來源。

## 測試
- 系統python缺Playwright，使用.venv/Scripts/python.exe，未安裝新依賴。
- 未修v76上新測試實跑失敗，farm=false仍綠，kitchen=true米色，arrange=null，重現使用者問題。
- 153026-tabs77-edges初次修復FAIL，未選色仍受舊兄弟CSS影響；已統一未選色。
- _private/test-runs/20260926-153051-211800-tabs77-edges-fixed/results.json PASS。
- 完整84/84全PASS：_private/test-runs/20260926-153126-590879-tabs77-full/results.json。
- CPU4 155806-tabs77-cpu4 PASS；release_smoke離線／新手／重開還原PASS，0JS錯誤／外部請求。效能最後獨立35.2→36.8FPS PASS。
- 環境GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。
- Surface不跑全平行，CPU4不取代全平行；建置不與效能測試同跑。

## 已完成交付
- 完整測試及CPU4／離線完成；commit b7c9a83826aa924a0d9a09adb2b8046cf47fc62a已push：v0.9.77: sync garden category selection colours。
- APK、itch、Pages、中英Devlog、介紹／截圖／原論壇首文及清理均已完成核對。
- Devlog1677699已Published，正文／v77附件核對並record；工作流程9项PASS。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test；目前v77/97700，公開APK SHA64e0debc8444fda5815f225d5a615bb37b220e1fcb109c0eae56c961bdd6b861，同簽章。
- 本次ADB無裝置；不宣稱Pixel已更新，不卸載／清資料。
- v76三平台、Devlog1677628、介紹／論壇17090045及profile引用都已完成，不重做歷史發布。
- 論壇編輯需selectText精確選句→Backspace→輸入→查重；HTML貼上未保留格式，不能整份fill。
- itch build2018911/upload19167726，完整payload與四分類實際顏色／開始暫停核對。
- Pages部署62a0fc020e1affd70e12800e6c3853b67a17b93b，Actions36228689338成功，完整SHA及實際分類／開始暫停通過。
- 新截圖30267050位於三張原combat後；公開原圖目視通過，商店縮圖載入；論壇原首文與profile正文及新圖已核對，未新增留言。
- 清理先dry-run再Apply，實際釋放13,460,377 bytes，2項刪除／0失敗／25項AccessDenied略過不改ACL，保留v77＋v76 APK與存檔簽章證據。
- 本次修正與可運作交付皆完成，下一步待使用者手機體驗回饋，不重跑歷史發布。

## 限制
- 真人易用性、聽感、市場需求、母語潤稿、真機長時效能仍未驗證。
- 單一代理，不招募／發新訊息／投廣告／改價；自動測試不等於市場驗收。
