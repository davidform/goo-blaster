# GOO BLASTER 精簡交接

## 目前任務（2026-09-20）
- 使用者要求：衝刺不可與Boss重疊；後期成長過強；衝刺冷卻過短；新增與闖關相連的種植／建設玩法。
- 單代理，序列修改／驗證／commit+push；最後同批交付，保留進度與購買紀錄。
- 分支codex/soft-world-ui；原基準a406fad，公開仍v0.9.60。
- 已安全pull --ff-only，未reset。新接手仍先核對工作區與BUILD。

## 已完成的獨立版本
- v61 commit dcf470f已push：玩家掃掠碰撞與Boss位移分離，不能衝刺穿過或重疊Boss。
- 完整69/69：_private/test-runs/20260920-212704-286175-boss-solid61-full/results.json。
- 60組碰撞／CPU4／離線／冷啟動皆過；舊v60新測試預期失敗，boss61-verification.json與截圖。
- v62 commit19317f0已push：商店dash等級改4/8/12%距離；局內cd卡才減冷卻3→2.6→2.2秒。
- 不讓speedScale加快冷卻，原.42秒遊戲時間無敵保留。
- 完整20260920-215416-831180-dash62-full為69PASS/效能FAIL；20260920-222510-276434-dash62-perf-standard-session補跑PASS，合併70項全過。
- dash62-verification.json：滿商店滿卡Lv25間隔.7667→2.2167秒，保護比32.83→11.67%；CPU4／離線皆過。
- v63 commit9d25416已push：每局2武器/4能力；第11關起主畫面選副武器，保留永久主武器+3。
- 搭配全滿後每張待選卡給2糖果幣，不再送經驗或回血。40搭配、50關×2副武器、11語言皆驗。
- 完整20260920-224239-905698-build63-full-final：70PASS/舊audit斷言FAIL；20260920-230249-160822-build63-audit-retry補跑PASS，合併71/71。
- SHA acc155252e017fd0b0e01614821fdb7a090bfbf91074e0fd8003b95fd787358a。
- build63-verification.json：CPU4/離線/冷啟動；固定靶場攻擊型DPS約-20.2%、防禦型-63.5%，不是通關率。
- 新手bot第1、2關過，第3關本次失敗；獨立效能45FPS。
- build63-power-ab.json：第9關bot舊1/3、新3/3；後期兩版bot都0/3，不代表真人難度曲線已完成。
- 第一輪v63因發現後期開局3武器繞過限制而主動中止，aborted.json及修前失敗保留，不用它驗收。

## 正在處理 v0.9.64 糖果庭院
- 根目錄v64已套用，尚未commit/push/公開。SHA b1d866d1b14d9698caf94fd448f6c10d70c4e4dcc4118a964a4b35128e66c0db。
- 三花圃、3植物（1/2/3次通關成熟，1/3/6花瓣）、小屋升級12/45/120花瓣。
- 初始3種子，種植花1、收成回1、每次通關+1；重玩可成長，失敗不倒退，無現實時間倒數，不加戰鬥屬性。
- 11語言19新key由i18n/build_v0964.py；docs-16-garden-design.md記範圍，後續章節收藏未實作。
- GARDEN存於既有存檔／備份碼／原生Preferences，按rev合併，舊存檔安全初始化。
- tests/py_garden.py已登記；種植/收成/重複結算/原生/備份碼/33語言尺寸專項通過，garden64.png已檢視。
- focused 20260920-231018-764692-garden64-focused：8/8通過。
- 完整72項20260920-231308-237941-garden64-full全部PASS、source_unchanged=true，獨立效能55.3FPS。
- garden64-verification.json：5項CPU4／離線／新存檔／冷啟動全部通過，截圖已檢視。
- 完整與專項已完成，接續commit `v0.9.64: add an offline Candy Garden linked to stage clears`，push。
- store/devlogs/v0.9.64-notes.json已備中英文案，未產生post/未发布，等itch公開驗證後prepare。

## 執行環境與限制
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- 全套jobs2，效能solo；全平行因Surface凍結紀錄未執行，CPU4不冒充全平行／Pixel測試。
- Windows一般命令曾1909鎖定，提升權限可用；23:08一般命令與CUA恢復。
- 鎖定期間elevated測試8–9FPS且舊版亦低，恢復普通環境45–50FPS；未證明確切原因，未改Windows安全設定。
- Git寫入與網路、ADB執行需要工具權限核准；先前拒絕是沙箱存取，不是自動審查拒絕。
- 23:15 ADB devices空，沒有安裝新版本至Pixel；保留固定APK入口。

## 待交付與驗證
- 遊戲提交／同SHA完整驗證後：native/build_test_apk.py --tests <v64完整>，先backup_android.py，再publish_test_apk.py --publish。
- Gradle不與效能測試並行。APK沿用appId／簽章，核對內部HTML／DEX／公開SHA，預期96400但以產物為準。
- Butler只傳_private/itch-builds/v0.9.64/index.html至davidform/goo-blaster:html5。
- CUA目前releaseBrowser選1/iab、releaseTab3，已登入davidform，公開頁仍v60、尚未按Run game。
- itch驗公開payload＋Run game/start/pause；native/publish_pages.py指定已驗commit與itch收據，驗Actions＋publicSHA＋啟動。
- _private/verify_pages64.py已準備；Devlog依native/DEVLOG-PUBLISHING.md，同批61–64一篇，查重／草稿／正文／Published。
- 手機未連線就提供 https://github.com/davidform/goo-blaster/releases/tag/android-test，不卸載／清資料。
- 發版後native/cleanup_local.ps1先盤點再-Apply，保留最新+前版APK、存檔、簽章、A/B、證據；不改ACL。
- 公開v60/96000基準與收據見_private/mobile-test/*v60.json，前次21個舊profile拒絕存取未清。
- 最終回報各渠道實際版本、測試證據、未執行真機/全平行/母語潤稿、UI截圖、4個commit Summary。
