# GOO BLASTER 精簡交接

## 目前任務（2026-10-02）
- 使用者回報冒險過關後，回首頁及其他遊戲頁仍持續煙火音效；影片附件已擷取影格，根因由實際Web Audio實跑確認。
- 分支codex/soft-world-ui，接手5786549、v82完整交付已完成，git pull --ff-only確認同步，不重做v82。
- 本次v0.9.83修正結算慶祝生命週期，三輪驗證完成，待平台交付；沒有調整音樂曲目、數值／獎勵／存檔／字串。
- 預定Summary：v0.9.83: stop victory celebrations when leaving results。
- HTML SHA 6dfd46f3f9769f38b873e7698b7d7317bb4f846c5ec36fb8e169b57b198c00dd。
- 單代理；Surface最多2個測試工作，效能單獨跑，不與Android建置競爭。不要另開代理。

## 根因與修正
- showMenu只隱藏結算畫面但G.fw仍true，updateFW每幀繼續排煙火；勝利音符排程亦未清理。
- stopCelebration在setHubPage／start執行：取消初始煙火／結算延遲回呼、清空FW與旗標、停止並斷開慶祝專屬Web Audio來源。
- 回呼綁定原局，防止快速重玩跨局；背景音樂及其他音效維持各自狀態。
- 新tests/py_victory_audio.py列入完整91項，實際UI四出口、全部底列／三主題、快速過關／背景恢復／離線、ended與disconnect驗證。
- v82實跑FAIL：離頁後fw=true、164粒子、烟火呼叫15次；新版四出口離頁新增煙火0、粒子0、音源清理PASS。
- 證據_private/audio83/baseline-v82.log、fixed-first.log／fixed-diagnostic.log保留失敗，fixed-second.log修正PASS。
- 首次修正測試捕捉旧結算320ms延遲浮回，已加入同生命週期取消；不是僅關閉整體音效來掩蓋問題。

## 驗證與下一步
- 完整91/91 PASS、source_unchanged=true：_private/test-runs/20261002-002932-647933-victory83-final/results.json。
- 命令 .venv/Scripts/python.exe run_tests.py --jobs 2 --label victory83-final。
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- CPU4三項3/3 PASS：20261002-005637-940242-victory83-cpu4；py_release_smoke離線／新存檔／關閉重開PASS，release-smoke-v83.log。
- 任何HTML修改須重跑整套；不與效能／Android建置競爭。未執行全平行及Pixel真機。
- 已準備store/devlogs/v0.9.83-notes.json及store/google-play/release-notes-v0.9.83.txt；尚未發布v83。
- 已在_private/mobile-test/v0.9.82-receipts及_private/play-preparation/v0.9.82-receipts保留上一版收據。
- 測試完成審diff，commit／push本次檔案，建置稽核APK／AAB，固定測試入口、itch、Pages、內測、Devlog與商店／原公告同步。
- 音效修正不改版面，現有真實截圖可保留並註明來源v82，不把舊圖改名宣稱新擷取。
- 完成公開驗證後cleanup dry-run／Apply，保留最新與上一版APK、進度／金鑰／備份／證據。
- 附件.codex-remote-attachments及_private禁止提交；手機已是Play版，不能混裝debug APK。

## 上一版已驗證交付（v82，勿重做）
- 遊戲9e99161、文件5786549已push；完整90/90與CPU4四項／離線重開PASS，詳細見docs-14-history。
- APK98200／0.9.82-test.0，公開SHA cd1e625b437b0cc3d314476c6efdf337bda29991b2fd0675fe1c41c10bc82101。
- 固定入口 https://github.com/davidform/goo-blaster/releases/tag/android-test。
- itch2047274 Active；Pages8e009276／Actions36889382603成功，公開完整payload與實際開始／暫停PASS。
- Devlog1685583已Published；store/page-sync/v0.9.82.json記錄公開介紹／新三圖／論壇及profile各9圖已載入。
- cleanup移除2項13,446,234bytes、0失敗、25權限拒絕略過；保留v82與v81APK。

## Google Play 與 Pixel
- app4976029382108915574／com.demjastudio.gooblaster；US$1.99、目標9歲以上成人，不重建App或換簽章。
- IARC使用者10月1日10:04截圖確認完成；通知demjaholding@gmail.com。商家由本人處理，價格最終儲存／客服政策同步仍待核對。
- v82 AAB98201／0.9.82-rc.1已簽署、驗簽／bundletool／manifest／ZIP比對PASS；signed-candidate.json；原ZIP內容0變更，新增3項簽章。
- v82簽包SHA749c47e030bdc6cae4074030ecafd3fcaaff6ee932af69b567458a012fb4666d。
- 沿用既有上傳金鑰，憑證SHA ed7ec469e074b8489d6515520d1a20e99ec29b4ae25c53f71cc0d56a4fe2eee6；異地備份未完成。不得建立新key。
- Console 10月2日00:09顯示0.9.82-rc.1 Internal Test有效／提供給內部測試人員，track4701357753096403615／release3。
- 內測連結 https://play.google.com/apps/internaltest/4701357753096403615。
- 未正式上架；Alpha4700117103530327117的12人持續14天尚未開始，內部名單1位不等於封測。
- Pixel私人空間debug版曾阻擋Play，經一次性明確授權／備份還原驗證後已改由Play安裝98001，詳_private/pixel-play-migration；不得重做卸載。
- Play交付憑證57965f11182c1fa87082dc48573a7b9426ab029361da21ff0128416e1e7268f9，與debug／upload憑證不同。
- 本次adb清單無裝置；不得把debug APK覆蓋Pixel的Play版，不卸載／清資料。v82 Play真機版面與更新存檔尚未驗證。
- 手機未連線仍交付固定測試入口；已有Play安裝者須走Play內測更新，不能用GitHub debug APK混裝。
