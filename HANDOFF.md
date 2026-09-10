# GOO BLASTER 精簡交接

## 目前狀態（2026-09-10）
- 本次兩項已完成：指定itch討論串新留言回覆、保留俯視玩法的圓潤微3D v0.9.59。
- 開發分支codex/soft-world-ui；遊戲commit fd85af8c439da213b77e085a9d249b1c7dc67954。接手先git status／log核對，不reset。
- root BUILD v0.9.59；HTML SHA d6a623ac167c987a60ec8922ad1db58f6f944ed8a90d3af034cd4569e0f23efc。
- APK測試下載、itch.io、GitHub Pages與Devlog皆已更新v59。USB未連線，Pixel已知仍v55，不能宣稱已安裝v59。
- 單代理；單檔零相依、預設英文、11語言、每版單一平衡變數。Surface曾因48工無回應，不重試全平行。

## 這批 v56–59 改動
- v56 887a6c9：只放慢7–19關普通敵人射擊間隔，第7關×3、第9關×35/13、第20關回原值；初始CD與後续CD一致。
- 出怪量、HP、速度、XP、Boss與卡池不變。同種子／無復活Pixel強化／250ms bot，第9關1/8→4/8；不是人類勝率。第10關診斷仍0/2。
- v57 f8a9106：核彈2.1秒演出，世界先16%速度；0.48秒爆炸、白屏停留到約1.2秒、1.8秒退白；暫停凍結、單次音效、新局重置。
- 世界慢動作也放慢無敵／冷卻／淨空，關卡倒數仍用rawdt；不宣稱完全沒有時間玩法影響。
- v58 9b05522：果凍地面单一20%淡色層，64塊重疊不加深；資料與效果保留。主畫面直接顯示故事目標與章節小景，長故事可展開。
- 原有三級dash改名衝刺訓練，顯示下級冷卻／固定0.42秒無敵；仍3→2.65→2.30→1.95秒，局內卡下限1.2秒。沒有新增第四級或改價格。
- v58字典266keys×11；未做母語者潤稿。
- v59：快取角色光影圖、柔和落地陰影、低對比地面浮雕、地圖節點厚度；Canvas 2.5D，非WebGL模型或斜視角。
- 光影圖144px、快取上限96；章節地面圖最多10份。受擊閃白／無敵彩虹保留；不改碰撞或其他玩法。

## 測試與失敗證據
- 命令環境：PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- 最終完整67/67：.venv/Scripts/python.exe run_tests.py --jobs 2 --label clay-depth-final。
- 報告_private/test-runs/20260910-074742-582529-clay-depth-final/results.json；同SHA、source_unchanged=true，程序全部結束。
- 單獨高負載py_v0927_perf：三次單局60.0／60.0／53.1，平均57.7FPS≥30；同伴同批52.7→52.6，-0.1%。不是PixelFPS。
- 邊角py_clay_depth：實際光照像素、cache重用／96上限、10Boss／狀態／resize／真實輸入；繪圖不改玩法狀態或消耗RNG。
- CPU4：GOO_UI_CPU=4 python tests/py_clay_depth.py；離線／新存檔／持久重啟：python tests/py_release_smoke.py。均PASS。
- _private/test-artifacts/clay59-verification.json記錄SHA與clay59-cpu4.log／clay59-offline.log hashes。
- 獨立ABBA：_private/clay59_perf.py，v58→v59、150敵＋64果凍、DPR2／390×844、每次8秒單分頁，53.83→56.72FPS（1.054）；clay59-perf.json。
- 首輪clay-depth-full（20260910-073659-892403）py_polaroid抓到戰報人物外框漏畫，45／16像素低於500；已停止首輪、保留失敗，補回外框3395／3367後重跑全套。
- 停runner時Windows對部分已結束子程序報錯；CIM再查確認無殘留，未帶進下一輪。
- 先前v56／57／58的63/64、64/65、65/66效能失敗仍保留在docs-14-history與私人reports，不能改寫為PASS。
- 此次Surface接電、78%；上一晚v58曾電池26%／CPU1035MHz。不得把跨供電批次差距全歸因微3D。
- 已檢視clay59-game.png／clay59-boss50.png；測試清除多Boss佈景堆疊toast並同步G.L，沒有改遊戲toast。

## 交付證據
- APK固定：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- v59／95900／0.9.59-test.0；appId com.demjastudio.gooblaster；既有簽章fa00189cc20d1c630da9c5ad9d3b1c54ddd230f61b84ecf1ba1531914fa14513未改。
- APK SHA 14bee140755dbc2880ee4c6c41fa2102f8b3fcdac4925ef3b896a0ac4a223e44，4290766 bytes；公開下載核對相同，含原生戰報外掛。
- _private/mobile-test/latest.json／published.json；來源備份android-source-20260910-080955.zip（80檔）。
- itch固定davidform/goo-blaster:html5，upload19167726/build1963772；itch-v59.json核對原完整payload，CDN只追加既知平台script。
- itch公開Run game→第5關→暫停已實按，畫面顯示v59／遊戲已暫停；iframe selector可用 `iframe#game_drop >> internal:control=enter-frame >> #btnPlay`。
- Pages https://davidform.github.io/goo-blaster/；部署commit5854993c58d35c759243d820042520e9f9ee7168；Actions34420337266 success。
- pages-v59.json：公開HTML SHA完全相同，獨立Edge開始3.0418秒／暫停，page_errors=[]。
- Devlog已Published：https://davidform.itch.io/goo-blaster/devlog/1658361/v0959-rounded-visuals-and-a-calmer-midgame。
- 中英全文／v59單一附件核對；store/devlogs/v0.9.59/post.json已記網址與hash，devlog-v59-receipt.json保存公開正文；不要重複發。

## 留言處理與授權
- 本次使用者授權已登入itch來源，核對整串所有新留言。其他回饋已有答覆；新增翻譯致謝17308395、Dualspace更新致謝17308411，兩篇公開正文已核對。
- store/community/topic-6826201.json保存父留言與回覆編號以防重複。沒有開背景排程。
- 未實玩Dualspace／Blade Baes Brawl、未提交他人遊戲評價表；沒有虛構體驗。
- Git同步、固定APK、itch、Devlog與Pages都已獲本作授權；按native對應流程執行，不必逐次問。
- 商店送審／AAB正式發布／定價／更換簽章仍未授權；新遊戲不繼承本作授權。
- main是網站交付分支：publish_pages.py只提交已測原始bytes與網站白名單，不直接合併未驗收開發HEAD。

## 下一步與未執行
- 等Pixel自行下載v59後的實測：第9關包圍／彈幕、長時間FPS與發熱、白屏舒適度、微3D可讀性及覆蓋更新存檔。
- USB未連線，不卸載／清資料；下次連線更新先備份原生存檔、核對簽章／版本，install -r後核對WebView。
- 全平行壓測、11語言母語潤稿、Pixel v59真機驗證未執行；不宣稱正式商店驗收。
- 詳細根因／版本與數字見docs-14-history.md；不要追加凍結的docs-04-append.md。
