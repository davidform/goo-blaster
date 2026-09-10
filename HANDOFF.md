# GOO BLASTER 精簡交接

## 目前狀態（2026-09-10）
- 本次任務：核彈標示置中並稍微放大；對更立體的方向提供建議。
- 開發分支codex/soft-world-ui；遊戲BUILD v0.9.60，待提交後封裝／公開同步。
- HTML SHA 4d7e83f6ffcf33818625fc92a13f42ea4715a54a83c3b774254a6de361c248ed。
- 接手先git status／log與BUILD，不reset；先核對未提交變更。
- 僅核彈內容改為內嵌SVG；位置／觸控區／演出／玩法數值不變，既有11語言aria-label保留。
- SVG為內容區54%；不受emoji字型留白影響。沒有新增相依，仍單檔離線。
- 使用者詢問更立體是否好：建議後續加強角色厚度與柔和高光，地面低對比；本版未再改微3D。

## 已驗證
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- 完整命令：.venv/Scripts/python.exe run_tests.py --jobs 2 --label nuke60-full。
- 報告_private/test-runs/20260910-085409-241472-nuke60-full/results.json，68/68、同SHA、source_unchanged=true。
- py_test9第1關滿血通關、前3關皆過；Node test9連續闖關553.6秒正常結束。
- 獨立py_v0927_perf三次56.7／55.1／53.5FPS，平均55.1；同批同伴51.1→50.9（-0.4%）。不是手機FPS。
- py_nuke_icon：5尺寸含橫向與平板、DPR1/2/3，實際PNG墨跡偏差每軸≤1 CSS px，真實觸控發射與衝刺鍵間距通過。
- 舊v59公開payload跑新測試，320×568向下偏3.5px、如預期失敗；v60同尺寸垂直0px。
- CPU4 py_nuke_icon與py_release_smoke離線／新存檔／冷啟動皆PASS。
- _private/test-artifacts/nuke60-verification.json保存SHA及log hashes；nuke60-game.png／nuke60-button.png已檢視。
- 測試開發先遇Pillow缺少，改用既有Canvas解碼；量測曾納入按鈕角落遊戲子彈，已修量測中央範圍；詳見docs-14-history。
- 全平行未執行（Surface過去凍結，不重試）；USB devices空，未做Pixel新版驗證。

## 交付下一步
- 先commit本次檔案，再依native/MOBILE-TESTING.md build_test_apk.py --tests上述report，backup_android.py與publish_test_apk.py --publish。
- 固定APK入口：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- 維持appId com.demjastudio.gooblaster與既有測試簽章；不卸載、不清資料。
- 已準備_private/mobile-test/notes.md與store/devlogs/v0.9.60-notes.json；待公開驗證後產生／發布Devlog。
- itch固定davidform/goo-blaster:html5，只傳已測index.html；公開Run game／開始／暫停及payload核對。
- Pages用native/publish_pages.py指定已測commit及itch收據；不能直接合併開發HEAD到main。
- CUA Chrome遊戲tab1912753174，releaseTab現位於Devlog管理頁；已確認僅v59/v55/v27三篇公開文章，無v60草稿。
- 發布後補各通道收據、歷史與本檔，再commit/push文件。

## 前版與授權
- 公開版目前v59，遊戲commit fd85af8；Pages main5854993、Actions34420337266 success。
- 前版交付完整證據見docs-14-history與_private/mobile-test/*v59.json。
- v56普通敵人射速／v57核彈演出／v58地面可讀性與故事目標／v59微3D均保留。
- v59 Devlog1658361已Published，勿重複發布；v60準備獨立小修正公告。
- 指定itch討論串留言已回覆17308395與17308411，store/community/topic-6826201.json防重；未設背景排程。
- Git／APK測試／itch／Devlog／Pages已授權，不逐次問；商店送審、定價、換簽章仍未授權。
- 單代理；不自行增加agents。未來遊戲沿用studio流程但不繼承身分／簽章／發布授權。

## 未執行與待回饋
- Pixel已知最後安裝v55；需下載新版驗證覆蓋更新存檔、長時間FPS／發熱、核彈白屏舒適度及第9關難度。
- 全平行壓測、11語言母語潤稿、正式AAB／商店送審未執行。
- 不把桌機FPS當Pixel效能，不把上傳當公開頁驗證。
