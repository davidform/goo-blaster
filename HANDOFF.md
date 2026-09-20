# GOO BLASTER 精簡交接

## 目前任務（2026-09-20）
- 使用者要求：衝刺不可與Boss重疊；後期成長過強；衝刺冷卻過短；新增與闖關相連的種植／建設玩法。
- 單代理、序列修改index.html；分版驗證後同批公開交付，不改存檔進度。
- 分支codex/soft-world-ui；原基準a406fad，公開版本仍v0.9.60。
- 已安全git pull --ff-only；沒有reset。新接手仍先核對未提交變更。
- Windows一般命令曾遇1909鎖定；22:25恢復後於22:47再鎖定，exec/view_image/CUA皆受影響；提升權限檔案操作可用。
- 效能以一般環境執行；提升權限環境曾8–9FPS、旧版亦低，恢復一般環境50.7FPS；未證明確切根因。

## v61 Boss碰撞修正
- v61已commit/push dcf470f；新增掃掠圓碰撞與初始重疊分離，Boss移動亦不能壓進玩家。
- 僅此單一機制；無敵、傷害、冷卻、卡池等不變。
- SHA dc5f516f6967cc1d17df961778c7c25654c965dc84dd637b9cf2ad8099da87ed。
- 完整.venv/Scripts/python.exe run_tests.py --jobs 2 --label boss-solid61-full：69/69、source_unchanged=true。
- 報告_private/test-runs/20260920-212704-286175-boss-solid61-full/results.json。
- 新py_boss_solid實跑60掃掠案例＋同中心恢復／普通接觸傷害／逃離。
- 舊v60對照預期exit1；v61 CPU4通過。boss61-verification.json確認離線／冷啟動通過，boss61-contact.png已檢視。
- 新手bot第1–3關通過，第1關滿心。效能獨立同批42.0→41.8FPS，單局有同伴47.5FPS；不是Pixel量測。
- 全平行未執行（Surface曾凍結），真機遊玩未執行。

## 接續順序
- v61/v62已完成驗證與commit/push。現在根目錄BUILD v0.9.63，尚未commit／公開。
- v62已commit/push 19317f0，SHA 293e4a1b662fc2654b2d5a2459c87b4f50c52197300875ac42e1ea016554e6fd。
- v62完整69功能PASS／效能FAIL；一般命令環境恢復後補跑效能PASS，合併70項皆過。
- 完整20260920-215416-831180-dash62-full，補跑20260920-222510-276434-dash62-perf-standard-session。
- dash62-verification.json含CPU4／離線／A-B：滿強化Lv25間隔0.77→2.22秒，無敵比32.8→11.7%；單局效能50.7FPS。
- v62：商店dash已買等級保留、改4/8/12%距離；只讓局內cd卡縮短冷卻3.0→2.6→2.2秒。
- 冷卻不再隨玩家等級speedScale加快；保留原.42秒遊戲時間無敵。
- v62程式／翻譯／測試已完成；私人patch腳本不可重複套用。
- tests/py_dash_cadence.py已登記／通過，24組shop/cards/level比較。
- v63：每局2武器／4能力槽，已選能力可升滿，永久攻擊強化保留。第11關起可於主畫面選副武器。
- 已抓到第21關起原始開局3武器會繞過上限，補startingWeapons與100組開局／真實select測試。
- 第一輪build63-full主動中止，aborted.json保留原因；不可用該報告驗收。
- v63正式完整20260920-224239-905698-build63-full-final：70PASS／舊audit斷言1FAIL；補跑20260920-230249-160822-build63-audit-retry PASS，合併71/71。
- SHA acc155252e017fd0b0e01614821fdb7a090bfbf91074e0fd8003b95fd787358a。
- build63-verification.json確認CPU4／離線／冷啟動；靶場攻擊配裝DPS約-20.2%，防禦配裝約-63.5%，不是通關率。
- 新手第1、2關bot通過，第3關本次失敗；獨立效能45.0FPS。全平行、真機未執行。
- 全卡滿後改少量糖果幣，不再送經驗／回血；避免回饋循環。
- v63專項與11語言／50關資料／主畫面回歸已通過；py_build_slots加入全50關兩種副武器及保留商店主武器等級。
- build63-power-ab.json為固定seed滿商店bot；第9關新3/3通過，後期bot兩版均失敗，不代表真人勝率／曲線完成。
- initial.json保留初稿量測（第21關起仍3武器），不是最終證據。
- v64庭院檔案不可混入v63 commit。
- 附加模式暫採糖果庭院：種子→種植→通關成長→收成→修復小屋，不以現實時間倒數，不加永久DPS。
- 庭院／城堡偏好已用async詢問，尚無答覆；已說明先按建議庭院規劃。
- 庭院已在_private/candidate64私人候選整合，尚未套用根目錄或發布。
- _private/implement64.py＋garden64.js及i18n/build_v0964.py可在v63通過後套用；docs-16-garden-design.md同步設計。
- 三花圃、3植物、通關推進、建材修復12/45/120花瓣；不增加戰鬥屬性。
- tests/py_garden.py候選實跑通過：種植／收成／防重複／舊存檔／原生／備份碼／33語言尺寸；最後空花圃與disabled樣式微調待根目錄實驗收。

## 測試與交付
- 環境PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- HTML每版完整套件，邊角、CPU4／离線；效能solo，不與Android建置並跑。
- 最終遊戲commit／完整同SHA報告後：build_test_apk.py、publish_test_apk.py、itch Butler、Pages、Devlog。
- CUA getState在22:55因1909失敗、kernel退出；恢復後重新初始化，不假設舊releaseTab變數存在。
- 現有授權涵蓋Git／測試APK／itch／Devlog／Pages；正式商店、定價、換簽章不包含。
- Pixel若連線，先備份進度及核對簽章，再install -r；禁止卸載／清資料。
- 固定APK入口：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- 公開基準v60／96000、SHA及各通道收據見_private/mobile-test/*v60.json及docs-14-history。
- v60 Pixel原生存檔與WebView已核對；當時進度保留，不代表目前新版本已同步。
- 每次最終交付後native/cleanup_local.ps1盤點再-Apply；保留最新／前版APK、進度備份、測試證據、A/B基準與簽章。
- 前次21個舊測試profile因Windows拒絕存取未刪，不改ACL。

