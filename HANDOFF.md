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
- v43 a29d96c：13個Boss×11語言重新命名、過期章節規則修正、日韓膠體術語、文字區捲動、Boss總數；已push。
- v43字典仍241keys×11、預設英文；未改關卡數值、卡池、商店或存檔。i18n/build_v0943.py可重建且冪等。
- v43 Commit Summary：v0.9.43: clarify monster names and localized game rules；實際提交狀態請核對git log。
- v44完成畫格安全修正：清彈後跳出舊索引迴圈；重開局的舊rAF時間戳不得令dt為負。提交以git log核對。
- 使用者要求音訊、命名、11語言精準度、難度／局內道具／商店滿級困境，工作尚在持續。
- 母語潤稿／跨國玩家理解率未做，不宣稱全部翻譯精準自然。

## 測試證據
- v41 48/48：20260909-075803-379699-soft-final，2工；CPU4 UI132組及離線重啟通過。效能45.5→45.1FPS。
- v42 49/49：20260909-082740-083723-audio-full，2工；CPU4音訊／離線通過，效能39.5→39.3FPS。
- v43 50/50：20260909-091709-010332-localization-final，2工、source unchanged；CPU4語境／離線通過。
- v43 SHA fe9a39cec887aaaccdc84e3c79e17204edde9fa27787e366b8a2e5b45df57b05。
- v44最終51/51：20260909-100123-816241-revive-final；SHA a14d97a6f383d95026d1ffda0108fe6bf0333f3e4505ab180dfa8b905a87fc63。
- v44 CPU4／離線最終通過：revive-cpu4-final.log、revive-offline-final.log；獨立效能39.6→39.4FPS。
- v44首輪50/51（py_v0927固定300ms未等到dmgEff），修為狀態輪詢；另CPU4找到負dt／负半徑，修好後已整套重跑。
- v43第一輪報告原子替換遇Windows暫時鎖定，程序中斷；中途亦補Boss計數，不算完整驗收。
- run_tests.py加入短暫PermissionError重試；tests/check_runner_checkpoint.py用真實Windows讀取handle驗證通過。
- 新py_l10n_context：11語言13Boss、50關數量／章節規則、日韓术語、實際320×480文字區滑動0→91。
- l10n-cpu4.log、l10n-offline.log與l10n-*.png在_private/test-artifacts；完整紀錄在_private/test-runs。
- 原48工曾讓Surface失去回應，本機不重試；2/4工不替代全平行門檻，不宣稱三輪全綠。
- 環境：.venv Python Playwright、GOO_BROWSER_CHANNEL=msedge、NODE_PATH=_private/test-node/node_modules。
- run_tests.py讀run_tests.sh清單，主效能最後單獨。勿讓診斷與其同時吃CPU。

## 下一步：大型Boss可視鎖定，再處理射程收益
- v44原始證據revive-collision-before.json、negative-frame-before.json；tests/py_revive_collision.py已加入套件。
- v44 Commit Summary：v0.9.44: prevent revival crashes from stale bullets and frames。
- 已直接重現tryDash把各來源保護覆蓋成0.42：一般受傷1.45、panic2.1、護盾0.9、復活3.2都縮短（dash-iframe-before.json）。
- v45只改P.iframe=Math.max(P.iframe,.42)；不增加原保護秒數。_private/py_dash_protection.py在dash-only候選已過（含真實雙指／後續子彈）。
- v45正式52/52通過：20260909-102121-309160-dash-full；CPU4／離線皆過，僅BUILD與iframe最大值改動，提交核對git log。
- 遠視糖鏡確定只加鎖定數字：390×844的860個可視樣本各等級都860；噴槍300px靶都0傷害；yoyo前進149.77px不變。
- 後續射程候選：永久射程每級投射物速度+10%，局內射程每級+15%，合計封頂+60%；壽命／數量不變，零強化不變。
- _private/prepare_range_candidate.py產生range-fixed候選；_private/build_v0945.py有3鍵×11語言文案，尚未套至正式檔。
- 候選實測噴槍第2級能打中300px靶，第3級yoyo前進206.55px；range-hit-before／candidate.json。
- _private/py_range_reach.py已驗36組實際命中／混合上限／同伴／敵彈；正式版仍須全語言文案排版與整套。
- 已重現大型Boss露出53px身體卻不鎖定／不開火；boss-visibility-before.json/png。候選以max(44,e.r)做可視邊界，兩方向尺寸與四邊測試通過，正式版尚未套用。

## 難度與道具診斷（尚不能宣稱完成）
- _private/balance_probe.py：真實loop／TouchEvent／選卡、虛擬60Hz計時器，停用畫圖；不是FPS或真人勝率。
- 固定同種子重播一致；三種狀態zero／逐局收入購買的earned／max。earned只沿可通關進程買最便宜戰鬥強化。
- 舊360秒虛擬牆鐘樣本含win:false/over:false，**未完成不等於陣亡**；不可沿用舊0/3當勝率。新工具clear/defeat/unfinished分開、上限900，未完成明確報錯。
- finished-balance-ab.json：reactive策略滿商店，第30關射程前2/3→後3/3；第50關真實0/3；bot不是玩家勝率。
- prepared/ reactive會拾取、使用核彈，reactive在危險時可立即翻滾；planner另看短期彈道，僅屬操作參考。
- 完成勝負的降彈速／減攻擊頻率實驗仍0/3，未採用；加倍受傷保護結果完全相同，追查才找到翻滾覆蓋iframe。
- dash-preservation-ab.json：50關修保護後存活約276~282秒、加射程約307~315秒，但此bot仍陣亡；勿宣稱已解決所有難度問題。
- _private/range_balance_ab.py以GOO_BOT_POLICY／GOO_AB_LEVELS／GOO_AB_ARMS／GOO_AB_OUTPUT控制；只讀候選檔，勿與獨立效能競爭CPU。
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
