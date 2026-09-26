# GOO BLASTER 精簡交接

## 目前任務（2026-09-26）
- 使用者要求首頁只作小鎮入口，各主題獨立頁面並有回首頁按鈕；v0.9.75已實作、驗證與三平台交付。
- 分支codex/soft-world-ui；單一代理。只改頁面分層／導覽，不改戰鬥、倒數、存檔或價格。
- HTML SHA b8297cb48e149c91c35a18dddc14b0fb5c536ac97980ba2d477e01fe5930278c。
- .codex-remote-attachments是使用者附件，禁止提交；私密收據／憑證／存檔僅_private。

## 實作與證據
- 首頁只顯示小鎮與資源；冒險地標進入關卡／開始頁，野餐／池塘／星光進入相應挑戰頁。
- 挑戰隱藏庭院任務／村莊／其他主題選單，進入即切換主題音樂；既有動態與回饋保留。
- 各目的地固定返回列，內容區從64px＋safe-area下方開始，避免scrollIntoView後遮擋。
- 返回首頁清除單次挑戰暫態，保留已存資源、獎章及進度。底部導覽仍可切冒險／強化／庭院／設定。
- 既有11語言toMenu文字；預設英文；不新增翻譯鍵。AGENTS第25節記錄需求。
- 截圖store/screenshots/v0.9.75：新存檔真實UI，含首頁及五目的地；已檢視手機／桌面／主題。
- native/capture_town_home.py能重現；manifest逐張保存來源與設定。

## 測試
- 完整82項：_private/test-runs/20260926-112822-457114-pages75-verified-full/results.json，jobs2，同一SHA。
- 初輪81PASS／1FAIL：py_ui_fixes舊首頁地圖假設讀0/0；修正測試先點城門再驗證原定位。
- 補驗115208-785775-pages75-edges-retry，py_ui_fixes與py_town_home皆PASS；validate_reports合併82/82。
- CPU4：115228-016840-pages75-cpu4，town_home／music_scenes／l10n_context三項PASS。
- py_release_smoke PASS：新progress1/coins0/meta{}，離線／CPU4／瀏覽器重啟還原progress9/coins456/meta.dmg2/selection8，無JS錯誤／外部請求。
- py_test9第1／2／3關58／57／95秒通關；效能最後單独PASS：39.8→38.1FPS，-4.1%。
- 早期111446、112244完整批次因視覺修正中止；111758診斷來源中途變更；保留，不拿來驗收。
- Surface不跑全平行；CPU4不取代全平行。Android建置不能與效能並行。
- 測試環境GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。

## 交付完成與未完成
- 遊戲commit 3b76d1b06020103e9a21dcabad7e902530d55c45已push：v0.9.75: separate the town home from themed game pages。
- 固定APK：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- APK97500／0.9.75-test.0／同簽章；公開下載SHA 82e5ff9758b2e57aa644a8ac0a97d897a7aac32916ee53e924f2f77ae5d17b7c。
- itch build2018298／upload19167726，完整原始payload一致（僅平台腳本後綴），實際池塘→回主頁→冒險→開始／暫停通過。
- Pages f11efd29273d53d0ec674323c25ed0ce3408010d，Actions36216389644成功；公開完整SHA／實際開始／暫停皆核對。
- 中英Devlog1677545已Published並record；tests/test_devlog_workflow.py九項PASS。
- Devlog：https://davidform.itch.io/goo-blaster/devlog/1677545/v0975-a-little-room-for-every-adventure。
- 公開介紹v75／分頁文案核對；新首頁30263551排第四，池塘30263552第五；前三戰鬥及歷史圖保留，實際縮圖已檢視。store/page-sync/v0.9.75.json。
- 圖片排序長批次逾時後舊tab控制失效；新編輯頁核對已上傳圖片，未重複上傳，重新填文案及短批次排序後公開驗證完成。
- 收據_private/mobile-test/itch-v75.json、pages-v75.json、published.json、devlog-v75-receipt.json。
- cleanup盤點＋Apply完成，釋放13,456,431 bytes；保留v75／v74回退、存檔／簽章。25個AccessDenied仍保留，不改ACL。
- Pixel本次adb devices沒有裝置；最後實測v71／97100，不卸載／不清資料，不宣稱手機已更新。
- 論壇原首文17090045／個人頁引用最後核對仍v64；前次編輯工具插入位置錯誤，未儲存。v75未重試該編輯，不發新回覆取代；仍未完成。

## 範圍限制
- 市場需求未驗證；docs-19-market-review.md與store/research/player-study-kit.md已備妥，不生成假訪談。
- 未招募／發訊息／投廣告／改價／啟用多代理；真人聽感、真機長時效能、回訪／付費意願與母語潤稿未驗收。
