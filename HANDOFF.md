# GOO BLASTER 精簡交接

## 目前狀態（2026-09-10）
- 本次任務：核彈標示置中並稍微放大；對更立體的方向提供建議。
- 開發分支codex/soft-world-ui；遊戲BUILD v0.9.60，遊戲commit293437122c2df48f6632b3e1aa360d1bf216f4bf；所有通道交付完成。
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
- 全平行未執行（Surface過去凍結，不重試）；本次已透過USB完成Pixel v55→v60覆蓋更新與WebView冷啟動驗證；未做長時間遊玩。

## 交付證據
- 遊戲Summary：v0.9.60: center and enlarge the nuke button symbol。
- APK固定：https://github.com/davidform/goo-blaster/releases/tag/android-test，v60／96000／0.9.60-test.0。
- APK SHA 8b4c2837340bc2fe4440cac142132112e71f19ef6d27f6f56497147751e09096，4290992 bytes，公開下載SHA一致。
- appId com.demjastudio.gooblaster，既有簽章fa00189cc20d1c630da9c5ad9d3b1c54ddd230f61b84ecf1ba1531914fa14513；DEX含戰報外掛。
- _private/mobile-test/latest.json／published.json；原生備份android-source-20260910-091848.zip（80檔）。
- itch固定html5，upload19167726/build1963926；itch-v60.json核對完整payload，僅附加平台htmlgame.js。
- CUA實按Run game，確認v60，再第5關開始／暫停成功；首次導航後click太早無匹配，重讀DOM後成功。
- Pages部署8f26191380c45d3ebc89a2b3f144217e9e0d0a8e，Actions34425141870 success。
- pages-v60.json：公開HTML SHA與測試相同，Edge實際開始3.038秒、暫停成功，零pageerror。
- Devlog：https://davidform.itch.io/goo-blaster/devlog/1658406/v0960-a-clearer-nuke-button。
- Published核對1個，中英全文／單一v60附件皆核對；store/devlogs/v0.9.60/post.json已記網址，不重複發。
- CUA releaseTab為Chrome tab1912753174，現位於v60日誌；可視編輯器先click取得焦點再End/Space/Backspace才會同步隱藏正文。

## 前版與授權
- 前版v59遊戲commit fd85af8；本次只加核彈圖示修正，先前內容完整保留。
- 前版交付完整證據見docs-14-history與_private/mobile-test/*v59.json。
- v56普通敵人射速／v57核彈演出／v58地面可讀性與故事目標／v59微3D均保留。
- v59 Devlog1658361已Published，勿重複發布；v60小修正公告亦已發布。
- 指定itch討論串留言已回覆17308395與17308411，store/community/topic-6826201.json防重；未設背景排程。
- Git／APK測試／itch／Devlog／Pages已授權，不逐次問；商店送審、定價、換簽章仍未授權。
- 單代理；不自行增加agents。未來遊戲沿用studio流程但不繼承身分／簽章／發布授權。

## 未執行與待回饋
- Pixel已安裝v60／96000；既有簽章核對、原生存檔備份、install -r前後存檔bytes一致；WebView v60且進度／金幣／強化／語言與備份相同。
- 證據_private/mobile-test/pixel-update-v60.json與pixel-runtime-v60.json；仍需長時間FPS／發熱、核彈白屏舒適度及第9關難度實玩。
- 全平行壓測、11語言母語潤稿、正式AAB／商店送審未執行。
- 不把桌機FPS當Pixel效能，不把上傳當公開頁驗證。
