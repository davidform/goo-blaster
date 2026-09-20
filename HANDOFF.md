# GOO BLASTER 精簡交接

## 目前狀態（2026-09-20）
- 使用者本次四項需求已實作並交付v0.9.64：Boss阻擋、衝刺節奏、搭配上限、糖果庭院。
- 分支codex/soft-world-ui，遊戲commit0f1f17a624937e81c19bad2fbe6c66abc37041c8；新接手仍先核對工作區／遠端／BUILD。
- 最終HTML SHA b1d866d1b14d9698caf94fd448f6c10d70c4e4dcc4118a964a4b35128e66c0db。
- 單代理，保留進度與購買等級。未建立背景排程，未更改價格或正式商店。

## 已交付機制與commit Summary
- dcf470f `v0.9.61: prevent movement through Boss bodies`：掃掠碰撞及Boss位移分離，避免重疊／穿越。
- 19317f0 `v0.9.62: bound dash recovery to in-run upgrade choices`：冷卻3→2.6→2.2秒，不再隨角色等級加快。
- 商店dash保留已買等級／價格，改4/8/12%距離；原.42秒遊戲時間無敵不加長。
- 9d25416 `v0.9.63: limit each run to two weapons and four skills`：2武器／4能力，已選可升級進化。
- 第11關起可選本局副武器；所有50關開局也受2武器限制，永久主武器+3保留。
- 搭配滿後每張待選卡給2糖果幣，不再回送經驗或回血。
- 0f1f17a `v0.9.64: add an offline Candy Garden linked to stage clears`。
- 三花圃／三植物：通關1/2/3次成熟、產1/3/6花瓣；小屋修復12/45/120花瓣。
- 初始3種子，種植花1／收成回1／通關+1；重玩可成長，失敗不倒退，不以真實時間倒數、不加戰力。
- 庭院存於既有存檔／備份碼／原生Preferences，rev獨立合併；舊存檔安全初始化。
- 首版有3次小屋升級，章節收藏／後續家園區域未實作，設計見docs-16-garden-design.md。

## 驗證證據
- v61完整69/69：20260920-212704-286175-boss-solid61-full；boss61-verification.json含CPU4／離線／舊版預期失敗。
- v62完整20260920-215416-831180-dash62-full：69PASS/效能FAIL；20260920-222510-276434-dash62-perf-standard-session補跑PASS，合併70/70。
- dash62-verification.json：滿強化Lv25間隔.7667→2.2167秒，保護比32.83→11.67%。
- v63完整20260920-224239-905698-build63-full-final：70PASS/舊audit斷言FAIL；20260920-230249-160822-build63-audit-retry PASS，合併71/71。
- build63-verification.json：固定靶場攻擊型DPS約-20.2%、防禦型-63.5%，不是通關率。
- build63-power-ab.json：第9關bot舊1/3、新3/3，後期兩版0/3；集中升級可能更有效，不宣稱整條難度曲線已完成。
- v63第一次完整批因發現後期開局3武器而中止，aborted.json保留，不用該批驗收。
- v64命令 `.venv/Scripts/python.exe run_tests.py --jobs 2 --label garden64-full`。
- _private/test-runs/20260920-231308-237941-garden64-full/results.json：72/72、source_unchanged=true，無失敗。
- garden64-verification.json：py_garden／boss_solid／dash_cadence／build_slots／release_smoke CPU4全過，含離線／新存檔／冷啟動。
- 庭院驗11語言×3尺寸、0／上限／重複領取／原生／備份碼；garden64.png已檢視。
- v64新手bot第1、2關滿心過，第3關陣亡；第1關硬門檻過。Node test9實跑455.8秒完成。
- 獨立效能三次53.8/56.1/56.1平均55.3FPS，同批41.2→41.7；不是Pixel量測。

## 公開渠道
- APK固定 https://github.com/davidform/goo-blaster/releases/tag/android-test ，v64/96400/0.9.64-test.0。
- APK4300800bytes，SHA c557d7f97251af3890a4ec682e8d83431ce0ecf0436ab1a7a1d1437859497226，原appId／簽章一致，HTML／DEX／公開SHA均核對。
- USB無裝置，未安裝Pixel；不要卸載／清資料，下載新版選更新。
- itch upload19167726/build1997627；公開payload同SHA、實際Run game/start/pause通過，收據itch-v64.json。
- Pages部署9b59ad7ee52485bb680369f173b13688bb119fbc，Actions35520352539 success；完整SHA／開始3.0359秒／暫停／0errors通過。
- Pages首次下載逾時，第二次成功，未重推或改內容；pages-v64.json記最終證據。
- Devlog Published https://davidform.itch.io/goo-blaster/devlog/1670920/v0964-a-candy-garden-and-more-meaningful-builds。
- 中英全文及單一v64附件確認，store/devlogs/v0.9.64/post.json；9項devlog工作流程測試通過。
- 原生來源備份android-source-20260920-232738.zip，80檔。
- cleanup-v64-output.json：刪舊v59 APK＋3profile共32,321,374bytes；留v64/v60與所有存檔／簽章／測試證據。
- 22個舊profile拒絕存取未清，不改ACL。

## 下一步／未完成
- 收集Pixel上第9關以後攻擊／防禦搭配、Boss邊緣衝刺、庭院成長循環的實玩回饋，再單一變數調整。
- Pixel新版覆蓋更新與長時間FPS未測；Surface全平行因凍結紀錄未跑，CPU4不是替代證據；11語言母語潤稿未做。
- Windows一般工具帳戶反覆1909鎖定；提升權限檔案／Git工具可用，已啟動一般環境測試照常完成。
- 鎖定期間elevated效能8–9FPS、舊版亦低；普通環境恢復45–55FPS，未證明原因、未改Windows安全設定。
- PYTHONUTF8=1、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules；jobs2，效能solo，不與Gradle同時跑。
- Git／測試APK／itch／Pages／Devlog／白名單清理授權沿用；正式商店／定價／簽章更換仍須另行授權。
