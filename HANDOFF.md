# GOO BLASTER 精簡交接

## 目前任務（2026-09-21）
- 使用者以FarmVille 3澄清庭院應是立體農場世界，確認開始；v0.9.66已實作可操作的2.5D村莊，測試與跨平台同步已完成。
- 分支codex/soft-world-ui；遊戲commit3947d1d83f78812744e0245d60ee9328001c3c43已push；BUILD v0.9.66，527762bytes。
- SHA0055b2c47875fc07ebe8b4d8090734a23ebbe0422eb273efe1314f9d0a468c11。
- Summary：`v0.9.66: turn the garden into an interactive isometric village`。
- 單代理，原創Canvas／单檔離線，沒有新增runtime相依。使用者附件未追蹤，不提交。

## 本版內容
- 斜俯視小屋、樹、池塘、圍籬、三塊田、已布置物件與步行居民；sprite快取、深度排序、20Hz庭院可見時更新。
- 拖曳平移、0.8–1.8倍縮放、回中；點田地種植或收成、點屋修復。標記在作物旁，44px以上點擊區。
- 原布置／六位願望收進details工具面板。未改農作成本、成長、戰力、商店或存檔schema。
- 第一位園丁是環境角色，並不代表已領願望。居民點擊有愛心／開啟願望；沒有生活AI、獨立生產或對話樹。
- 手機像素場景是初版，不宣稱達到FarmVille內容量／美術精細度。後續以真機體驗確認方向。
- 11語言新增六個導航鍵，i18n/build_v0966.py。預設仍英文。

## 驗證
- `.venv/Scripts/python.exe run_tests.py --jobs 2 --label garden66-full`：74/74、source_unchanged。
- _private/test-runs/20260921-111641-240067-garden66-full/results.json。
- 新增py_garden_world：真實mouse／touch拖移不誤種、放手不漂、縮放界限、通關成長收成、修屋、重啟、33語言尺寸、離線、reduce-motion、離開庭院停動畫。
- 既有py_garden／py_garden_design仍驗資源、六題、上限、備份與原生合併；只改走新UI入口，沒有放寬斷言。
- 首批開發途中source_changed不作驗收；設計測試重啟後未打開工具面板，補真實操作後過。
- CPU4原批20260921-112025-184789-garden66-cpu4：garden/design過、world結算導航失敗。
- 根因新測試直接setHubPage跳過玩家btnGarden，延遲CLEAR層攔截；改點真實btnGarden，不改產品。
- 重跑20260921-112510-799996-garden66-cpu4-real-navigation過；補真正touch事件20260921-113002-454297-garden66-touch-cpu4也過。
- py_release_smoke.py離線／新存檔／CPU4／冷啟動過；_private/garden66/release-smoke.log。
- 新手bot1/2/3关過（50/59/101秒，3/2/1心）；Node test9 475.5秒完成。非真人勝率。
- 獨立效能50.1/48.0/50.8平均49.6FPS；同伴35.2→35.2（+0.2%），非Pixel。
- 單獨村莊繪製80次中位0.5ms、p95 0.8ms、最大1ms、17sprite；_private/garden66/scene-cost.json。
- Surface全平行因既有凍結限制未跑；CPU4不能替代真機／全平行。手機ADB沒有裝置。
- PYTHONUTF8=1，GOO_BROWSER_CHANNEL=msedge，NODE_PATH=_private/test-node/node_modules。效能不與Gradle同跑。

## 素材與发布
- native/capture_garden_world.py擷取實際遊戲；store/screenshots/v0.9.66含初始繁中、成長繁中／英文、manifest。
- 成長圖使用可達成隔離存檔（進度21、屋2、花瓣60），前三願望透過gardenWelcome完成；不是真人或真機證據。
- APK96600同簽章，公開SHA2535ac88f4775e61e5157475ce273d34cf30fd321650b21e46d4cabf1f8ffff7核對。
- itch build1999525公開payload一致，真實UI種植種子3→2、開始／暫停通過；_private/mobile-test/itch-v66.json。
- Pages部署ca14d8869534b64158e57cd21483420541b9be15，Actions35558741597 success；完整SHA及實際開始／Paused核對，pages-v66.json。
- Devlog1671600 Published，中英全文＋v66附件／新圖核對，workflow9/9；store/devlogs/v0.9.66/post.json。
- 遊戲頁v66說明已公開，新圖30144894第四，前三戰鬥圖保留；store/page-sync/v0.9.66.json。
- 原討論串首篇改寫仍待前次明確授權：v65時自動核准拒絕Save，不能繞過；本次不另送首篇修改。
- https://davidform.itch.io/goo-blaster/devlog/1671600/v0966-step-into-your-candy-village 。手機未連線，未安裝v66。
- 固定手機入口 https://github.com/davidform/goo-blaster/releases/tag/android-test 。不卸載、不清資料。

## 待辦與限制
- 本版交付完成；下一步以手機實際拖曳／種植／收成體感評估，再單獨設計居民生活與村莊成長玩法，不同時調戰鬥平衡。
- cleanup_local.ps1白名單清除v64 APK＋一個測試profile，共13668045bytes；保留v66/v65、存檔、簽章與證據。
- 先前相簿3張v64 UI＋5張legacy未刪，Chrome確認逾時；v65圖將列舊圖但保留Devlog用途，不擅自刪歷史素材。
- 23個舊profile拒絕存取留存，不改ACL。一般工具1909間歇鎖定，提升權限可用；不改Windows安全設定。
- Pixel長時間FPS、11語言母語潤稿、付費市場品質仍未驗收。
- 使用者要求主圖真實Boss戰；不能以測試通過替代好玩與商業呈現。後續另處理Boss受擊純白／特效遮角色等。
- Git／測試APK／itch／Pages／Devlog／白名單清理授权沿用；正式商店／定價／簽章另授權。
