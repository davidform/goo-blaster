# GOO BLASTER — 目前交接
更新：2026-09-09；詳細研究／歷史見docs-14、docs-15、docs-16。

## 接手與授權
- 完整讀AGENTS.md與本檔，核對Git差異／BUILD；安全同步，不reset覆蓋。
- 單一代理，繁體中文；三輪實跑、效能單獨；區分已驗證／失敗／未執行。
- Git可自動commit/push本次檔案。分支codex/soft-world-ui；Pages只在main push部署。
- 全平行門檻尚未完成，不發布Pages／itch／APK／AAB；商店送審、價格、憑證另行授權。
- 兒童可离線、US$2.99一次買斷；無廣告、訂閱、消耗型購買、付費隨機或FOMO。
- 一般階段完成更新交接並繼續，不因此要求換對話。

## 目前狀態與已完成版本
- v41 4839c6a：柔和配色、可愛果凍、Adventure／Upgrades／Settings導覽；已push開發分支。
- v42 02eb0e5：柔和音樂／武器音色、實際Boss曲切換、音訊亂數隔離、停止競態與音源回收；已push。
- v43：13個Boss×11語言重新命名、過期章節規則修正、日韓地面膠體術語、文字區可捲動、Boss總數含章節Boss。
- v43字典仍241keys×11、預設英文；未改關卡數值、卡池、商店或存檔。i18n/build_v0943.py可重建且冪等。
- v43 Commit Summary：v0.9.43: clarify monster names and localized game rules；實際提交狀態請核對git log。
- 使用者要求音訊、命名、11語言精準度、難度／局內道具／商店滿級困境，工作尚在持續。
- 母語潤稿／跨國玩家理解率未做，不宣稱全部翻譯精準自然。

## 測試證據
- v41 48/48：20260909-075803-379699-soft-final，2工；CPU4 UI132組及離線重啟通過。效能45.5→45.1FPS。
- v42 49/49：20260909-082740-083723-audio-full，2工；CPU4音訊／離線通過，效能39.5→39.3FPS。
- v43 50/50：20260909-091709-010332-localization-final，2工、source unchanged；CPU4語境／離線通過。
- v43 SHA fe9a39cec887aaaccdc84e3c79e17204edde9fa27787e366b8a2e5b45df57b05。
- v43第一輪報告原子替換遇Windows暫時鎖定，程序中斷；中途亦補Boss計數，不算完整驗收。
- run_tests.py加入短暫PermissionError重試；tests/check_runner_checkpoint.py用真實Windows讀取handle驗證通過。
- 新py_l10n_context：11語言13Boss、50關數量／章節規則、日韓术語、實際320×480文字區滑動0→91。
- l10n-cpu4.log、l10n-offline.log與l10n-*.png在_private/test-artifacts；完整紀錄在_private/test-runs。
- 原48工曾讓Surface失去回應，本機不重試；2/4工不替代全平行門檻，不宣稱三輪全綠。
- 環境：.venv Python Playwright、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- run_tests.py讀run_tests.sh清單，主效能最後單獨。勿讓診斷與其同時吃CPU。

## 下一步：先復活穩定，再射程收益，再評估难度
- 實際確認復活bug：1心＋1蠟燭＋3顆重疊敵彈，hurtPlayer清空EB後舊迴圈讀到undefined.life。
- 原始證據revive-collision-before.json；真實rAF回歸_private/py_revive_collision.py在舊版失敗，revive-collision-old.log。
- 候選修正：敵彈碰撞後若EB為空就break。_private/test-artifacts/revive-fixed/index.html；實際1/3/100顆、前中後位置全部通過。
- 下一版v44只修此bug。將_private/py_revive_collision.py移至tests、接test_paths／加入套件，補CPU4、完整回歸、歷史、commit/push。
- 遠視糖鏡確定只加鎖定數字：390×844的860個可視樣本各等級都860；噴槍300px靶都0傷害；yoyo前進149.77px不變。
- v45候選：永久射程每級投射物速度+10%，局內射程每級+15%，合計封頂+60%；壽命／數量不變，零強化不變。
- _private/prepare_range_candidate.py產生range-fixed候選；_private/build_v0945.py有3鍵×11語言文案，尚未套至正式檔。
- 候選實測噴槍第2級能打中300px靶，第3級yoyo前進206.55px；range-hit-before／candidate.json。
- v45還須正式回歸（實際命中、零強化相同、混合上限、同伴、敵彈不受影響）、文案排版與全套。

## 難度與道具診斷（尚不能宣稱完成）
- _private/balance_probe.py：真實loop／TouchEvent／選卡、虛擬60Hz計時器，停用畫圖；不是FPS或真人勝率。
- 固定同種子重播一致；三種狀態zero／逐局收入購買的earned／max。earned只沿可通關進程買最便宜戰鬥強化。
- balance-probe.json在30關max因復活bug中斷；balance-fixed-probe.json補30/50，各3種子max仍0/3，需追查，非雜訊。
- range-balance-ab.json：修射程前後同批max，第7關皆3/3；第30關0/3→1/3；第50關皆0/3，不足以解決全部後期體驗。
- 原dodge策略會避敵彈及選救命卡，但不主動找道具／使用核彈；新增prepared策略補這兩項，尚需完成對照，避免只為笨bot降難度。
- _private/range_balance_ab.py，GOO_BOT_POLICY=prepared、GOO_AB_LEVELS=30,50、GOO_AB_OUTPUT另取檔名；上次為獨立效能而停止，未完成。
- 固定50關純Boss火力：6→7峰值31→59、平均19.51→41.80；非舊幾何，不沿用舊+178%當現況。
- 一般ring冷卻×1.6候選讓7關峰值50／平均33.74，未寫進遊戲。另版才可調，不能與射程收益混改。
- 商店总成本8930、每局幣上限實際520；py_meta舊診斷額外乘幣加成印832是假高估，下一次應修測量工具。

## 原生／效能／發布限制
- 原生實際APK/AAB仍v0.9.40；appId com.demjastudio.gooblaster，debug APK4261164bytes、未簽AAB3112351bytes。
- SHA cc7e50fcb9d87979be694c413c0b6173af0435c4647a2166b599aef10e267d6b；JDK21/SDK36。
- Pixel先前離線／Preferences／冷啟動通過；目前未連線，卡頓版本與情境不明，不能宣稱新版本真機改善。
- native/BUILD-WINDOWS.md與prepare_android.py／audit_artifacts.py／test_device.cjs可重做；原生獨立repo未建。
- 簽章AAB派生安裝、升版／重裝／系統備份、完整網路稽核、Play Console／iOS皆未做。
- itch仍v0.9.31，butler授權但尚無頻道；隱私政策公開HTTP200已驗。新聲音手機揚聲器／耳機聽感待玩家試玩。
