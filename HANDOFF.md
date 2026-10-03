# GOO BLASTER 精簡交接

## 目前狀態（2026-10-03）
- 目前目標：網站舊圖示已更新並公開驗證；手機Chrome常用網站格的快取刷新仍待使用者確認。Pixel音效／存檔真機驗證仍待完成。
- 本輪接手HEAD b7af2f9（交付紀錄）與遊戲commit均已推送；git pull --ff-only回報Already up to date。
- 本輪文件變更AGENTS.md／CLAUDE.md／HANDOFF.md；提交以docs: clarify proactive conversation handoff rules查找。未追蹤.codex-remote-attachments/保留且不提交。
- 本次煙火音效跨頁持續播放問題已完成v0.9.83修正、驗證與授權平台交付。
- 分支codex/soft-world-ui；遊戲commit 2e6a74b33450f9ef06c0b3ad671e70778571ad87已push。
- Summary：v0.9.83: stop victory celebrations when leaving results。
- HTML SHA 6dfd46f3f9769f38b873e7698b7d7317bb4f846c5ec36fb8e169b57b198c00dd。
- 前版v82免捲動／標題固定已完成；本次沒有改排版、音樂曲目、數值、獎勵、倒數、存檔或字串。不要重做已驗證工作。
- 單代理；Surface最多2測試工作，效能單獨跑，不與Android建置競爭。

## 修正與三輪證據
- 根因：showMenu只隱藏結算畫面，G.fw仍true，updateFW持續產生煙火；已排程勝利音符亦未取消。
- stopCelebration在setHubPage／start執行：取消煙火／結算回呼、清空FW旗標粒子、停止並斷開慶祝專屬Web Audio來源。
- 回呼綁定原局，避免快速重玩跨局；主題音樂和其他音效保留。
- 新tests/py_victory_audio.py已納入整套91項；四個實際UI出口、所有底列／三主題、快速連勝、背景恢复、離線與音源ended/disconnect驗證。
- v82實跑FAIL：離頁fw=true、164粒子、煙火呼叫15次；新版四出口新增煙火0／粒子0，音源清理PASS。
- 首次修正抓到320ms舊結算延遲浮回，已修正；_private/audio83保留baseline-v82／fixed-first／fixed-diagnostic失敗及fixed-second成功日誌。
- 完整91/91 PASS、source_unchanged=true：_private/test-runs/20261002-002932-647933-victory83-final/results.json。
- 命令 .venv/Scripts/python.exe run_tests.py --jobs 2 --label victory83-final。
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- CPU4三項3/3 PASS：_private/test-runs/20261002-005637-940242-victory83-cpu4/results.json。
- py_release_smoke離線／零強化新存檔／關閉重開PASS、0外部請求與JS錯誤；_private/test-artifacts/release-smoke-v83.log。
- py_test9前三關57/64/87秒通過；獨立效能54.3→54.3FPS（不是Pixel數據）。免捲動1532頁／66尺寸語言組合PASS。
- 未執行全平行（Surface限制）、Pixel真機聽感與更新後存檔；目前無最終測試失敗。

## 已驗證交付
- APK98300／0.9.83-test.0，固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test。
- 公開下載SHA 2d8caf14fae7176ad93289812dc6b64aaaaa44287f41c024b21379a4a8e40623；原debug簽章／實際HTML／bridge稽核PASS。
- itch build2047572 Active，完整payload及平台suffix核對PASS；https://davidform.itch.io/goo-blaster。
- Pages commit ca5265ff88599c264e188eaa3c7fa999ad2eb289，Actions36896268358成功，公開完整HTML SHA一致。
- https://davidform.github.io/goo-blaster/；兩網站實際開始／暫停PASS，_private/mobile-test/itch-v83.json、pages-v83.json及截圖。
- 中英Devlog1685658已Published，工作流程9/9 PASS；store/devlogs/v0.9.83/post.json。
- https://davidform.itch.io/goo-blaster/devlog/1685658/v0983-leave-the-fireworks-at-the-finish-line。
- 商店介紹／原論壇17090045／profile均核對v83；論壇兩處9圖均載入，保留既有v82真實UI圖而未重複上傳。store/page-sync/v0.9.83.json。
- cleanup已dry-run／Apply：移除2項13,446,775bytes，0失敗、25權限拒絕略過；保留v83／v82 APK、進度／金鑰／備份／證據。
- 附件.codex-remote-attachments與_private不得提交；可重新產生的暫存以現有清理白名單處理。

## Google Play 與 Pixel
- app4976029382108915574／com.demjastudio.gooblaster；US$1.99、目標9歲以上成人，不重建App或更換簽章。
- AAB98301／0.9.83-rc.1已沿用上傳金鑰；驗簽／bundletool／manifest／ZIP PASS，原ZIP內容0更改、新增3簽章項目。
- 簽包SHA 744f3ce905b2206e64a6b76f284ce3a1a6eb3cdd697d2d7feb055bca59538714；_private/play-preparation/signed-candidate.json。
- Console 10月2日01:06：0.9.83-rc.1 Internal Test提供給內測者，track4701357753096403615／release4。
- 內測入口 https://play.google.com/apps/internaltest/4701357753096403615；更新包不等於已安裝到Pixel。
- 唯一Console警告為缺去混淆檔（minify=false）；裝置支援數不變。_private/play-preparation/internal-v83-receipt.json。
- 2026-10-02後續adb已核對Pixel安裝98301／0.9.83-rc.1，installer=com.android.vending；真機聽感與存檔仍未驗。必須走Play更新，不混裝debug APK、不卸載／清資料。
- Play簽章57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9；upload憑證ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6。
- 上傳金鑰異地備份未完成，不得建立新key。IARC已完成；商家由本人處理，價格最終儲存／客服政策同步仍待核對。
- 未正式上架；Alpha4700117103530327117的12人持續14天尚未開始，內測1位與自動測試均不等於封測。

## 下一次接手
- 本輪僅文件整合與唯讀核對，未啟動測試／建置／發布工作；沒有本輪尚在執行的外部操作。Play待驗事項如上，不代表新對話必須立即再換。
- 文件驗證：studio.py check設定有效（未跑遊戲測試）；HTML SHA仍與上述v83一致。既有91項／CPU／離線／發布驗證不得重做；文件差異以git diff --check核對。
- 先讀AGENTS.md／本檔，核對Git與實際BUILD；歷史只按需要搜尋，不重跑已完成的v83發布與三輪驗證。
- Pixel已核對98301；下一步以真實過關→主畫面→庭院／三主題確認無殘留煙火聲，保留存檔。
- 無手機連線則明示真機未驗；可續處理Play上架待辦，但不得替代12人14天或擅自正式發布。

## 網站圖示補同步（2026-10-03）
- commit 766a456：build: refresh website icons and publish asset-only updates，已push。沿用Google Play綠色角色，icon-192／512更新；遊戲HTML原位元組未改、BUILD仍v83，不重發APK／Devlog。
- Pages工具原本HTML相同就跳過，已改為比對完整網站白名單；tests/test_pages_workflow.py 9/9 PASS，含僅圖示更新回歸。
- Pages部署3afcb4e／Actions37080685003成功；公開HTML與兩個icon SHA一致；真實開始／暫停PASS。_private/site-icons/pages-check.json、pages-pause.png。
- itch封面由29349624換為30483200；公開favicon及og:image均指向新圖；重開編輯頁確認已保存，_private/site-icons/itch-cover.png。
- 收據store/page-sync/icons-2026-10-03.json；手機新分頁快取未驗，不要求清除網站資料（避免影響網頁存檔）。本轮無待完成發布程序。
