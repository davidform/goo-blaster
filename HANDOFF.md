# GOO BLASTER — 目前交接
更新：2026-09-09；詳細歷史 docs-14-history.md，玩法設計 docs-15-upgrade-design.md。

## 目前進行中（手機回饋新一輪，尚未交付）
- 使用者：第9關小怪包圍／子彈密；核彈需慢動作與白屏停留；地面殘影太深；故事需一目了然；詢問商店衝刺等級與上限。
- v56普通敵人射擊節奏功能已驗，效能尚未過（7–19關，20關回原速），其餘數值不變。SHA c5ceb7ee28fc7b685ce8dc2a7ad4d70cd46a61e09f69cbf611927febc201b263。
- 完整63/64，效能待驗：_private/test-runs/20260909-223040-368026-ordinary-shot-full/results.json；有同伴未達標（首輪25.7、補跑24.7；同批舊v55 23.75／新v56 23.65）FPS。CPU4／離線shot56-cpu4.log與shot56-offline.log已過。
- stage9-shot2-ab.json：16完成對照，Pixel強化無復活／250ms操作，第9關1/8→4/8；相鄰第8關0/2→1/2、第10關0/2→0/2、第一關2/2不變。出怪減量與較小射擊調整候選未採用。
- v57候選_private/nuke57-preview；_private/prepare57.py與py_nuke_cinematic.py實作2.1秒慢動作白屏、暫停凍結、提示互斥；nuke57-preview-reviewed.log已過。
- v58候選_private/readability58-preview；prepare58.py＋build_v0958.py。單層20%果凍、可見目標卡＋章節小景、翻滾大師改名衝刺訓練並顯示冷卻／0.42無敵，不改數值。
- py_readability.py：550目標、11語言、三級冷卻3→2.65→2.30→1.95，局內疊加下限1.2秒；readability58-preview-reviewed.log已過，圖片已檢視；小螢幕滑動context也過。
- 先完成v56並提交，再依序v57完整65項／CPU／離線／提交，v58完整66項／CPU／離線／獨立效能／提交；最後APK與itch同步、若Pixel仍連線可覆蓋更新保留存檔。
- 公開／手機仍v55；以下v55證據保留作基準，不能當v56–58已交付。

## 接手與授權
- 完整讀 AGENTS.md／本檔，先核對 Git 差異與 BUILD；安全同步，不 reset 覆蓋。
- 繁體中文、game-studio共用流程；預設單代理，多代理需另確認。
- 分支 codex/soft-world-ui；本次commit/push已授權，正式Pages只由main觸發。
- 單HTML、零執行期依賴、離線、預設英文、11語言；每版一項平衡變數。
- 三輪實跑；效能獨立，勿與其他瀏覽器或Gradle同跑。
- Surface曾在48工失去回應，勿重試全平行；本次2工＋CPU4不是全平行通過。
- 固定Prerelease APK分發已授權；保留appId／簽章、增加versionCode，勿卸載／清資料。
- itch.io已新增同步授權；正式Pages／商店／AAB／價格／私鑰操作仍不包含。
- US$2.99買斷、家庭受眾，無付費隨機／廣告／FOMO；私人簽章不入Git。

## 本次完成範圍
- 使用者要求重想升級寶箱、查連升3級、處理下一步；依序v53→v54→v55。
- 實際BUILD v0.9.55；SHA 2cb6787d111a950c14ae1bae78d24fa6294dcda278c0fd31d14d04e49a4da9ef。
- v53修選卡佇列：34×2XP=68，Lv1→Lv4／剩17XP，應選3張；現正確顯示Lv4與1/3→2/3→3/3。
- XP／卡池不動；補同幀多晶核、追加Boss獎勵、舊卡單次事件、跨局延遲保護、11語言剩餘提示。
- v54火焰糖：6秒走位留火／每塊2秒／半徑34／每秒24基礎傷害；重疊不加倍、刷新不疊層、上限16。
- 只直接傷普通敵人；玩家不受傷，普通自爆怪死亡仍可間接傷Boss。寶箱權重與收益不變。
- v55只改第15／20／25／30／35／40／45／50關章節Boss HP；前十關與所有其他Boss欄位不變。
- 十章HP：23296、80240、82246、84252、86258、88264、90270、92276、94282、96288。
- 末章523002→96288（-81.6%）是大幅重校，不可說微調；登場223秒、240秒後狂暴等原規則保留。
- docs-15分現有三種打法、十種寶箱定位、三件未做構想；沒有新增三套武器或三件新道具。

## 測試證據
- .venv/Scripts/python.exe；GOO_BROWSER_CHANNEL=msedge；NODE_PATH=_private/test-node/node_modules；PYTHONUTF8=1。
- 最終命令：python run_tests.py --jobs 2 --label chapter-health-full。
- v55完整63/63：_private/test-runs/20260909-201434-055020-chapter-health-full/results.json，同SHA、來源未變，效能最後單獨執行。
- CPU4：health55-cpu4.log／health55-queue-cpu4.log／health55-fire-cpu4.log；離線新存檔冷啟動health55-offline.log，全PASS。
- v53完整61/61：20260909-192602-386494-upgrade-queue-final；CPU4／離線過；v52負對照抓到錯標題。
- v54首跑61/62：20260909-194555-526485-fire-trail-full；舊測試誤要求新火焰說明含凝膠，修測試後同SHA補跑20260909-201300-555777-fire-context-retry，合併62/62。
- v54獨立150敵人／0與16火焰ABBA：52.9→57.0FPS，比率1.076；不是Pixel實測。fire-active-perf.json。
- v53首輪cp950註冊讀取失敗已中止／重跑；v55草稿把第5關HP誤填28288，實測原本23296，修測試而非遊戲；原失敗log保留。
- 已檢視upgrade-queue-v53.png／fire-trail-v54.png；11語言265key與參數、版面檢查過，尚未母語者潤稿。
- tests/py_chapter_health.py固定v54 e14d846基準，逐項比對50關＋真實生成／碎甲／通關；v54負對照失敗如預期。

## 難度量測與限制
- boss-windows53.json：取消小怪推Boss候選仍0/4，已拒用；沒有混入移動改動。
- boss-health55-ab.json＋boss-health55-holdout.json：32個完成對照，固定種子真實迴圈，重播一致。
- MAX末關0/8→4/8；其中保留種子619／1043／2027與兩種操作0/6→2/6，不是真人50%勝率或MAX保證過。
- MAX第15／30／45關共4/4→4/4；零強化第一關2/2→2/2；零強化末關0/2→0/2。
- fire54-ab.json：強制給一顆火焰糖的16完成對照；不代表自然掉落勝率，該版末關仍0/2。
- 商店全買16250、每場含幣增益3–520，理論最快32場非實際買滿關卡；本次不再改價格。

## 手機交付與下一步
- 固定入口：https://github.com/davidform/goo-blaster/releases/tag/android-test
- 已公開v0.9.55／95500／0.9.55-test.0；4288528bytes，遊戲來源與android-test標籤為3244ce3。
- APK SHA 9f2229ac26d43dfeee79d7622d48c729efac8a59d0d76d328f41e17e0122cab9；同舊簽章、APK內HTML同完整測試SHA、DEX戰報外掛過。
- latest.json／published.json／page-v55.json：公開下載SHA一致、頁面HTTP200及新版連結過；來源備份android-source-20260909-203116.zip，80檔。
- 流程native/MOBILE-TESTING.md：遊戲提交→build_test_apk.py --tests <v55報告>→backup_android.py→notes.md→publish_test_apk.py --publish。
- latest.json／published.json需確認版本、APK內HTML同SHA、同簽章、公開下載hash；來源正確不等於APK／真機正確。
- appId com.demjastudio.gooblaster，簽章固定native/test-channel.json；不更換。
- Pixel已由v52覆蓋安裝v55／95500，原生存檔逐位元不變，WebView進度／糖果幣／永久強化一致；pixel-update-v55.json與pixel-runtime-v55.json。
- Pixel仍待手感驗證：連續選卡、火焰走位、後段難度、音效／卡頓、戰報PNG與取消重試。
- 全平行／母語者與兒童理解度未執行；AAB仍v40未簽，正式Pages／商店未更新；itch已更新v55。
- 本次範圍已交付；下一步收Pixel回饋，再選下一個單一槓桿；不直接把誘餌／糖環／回力標一起塞進池子。

## itch.io 新授權與交付
- 往後完成驗證後直接同步itch.io，不重複問；固定davidform/goo-blaster:html5，見native/ITCH-PUBLISHING.md。
- v55 upload19167726／build1962179，公開頁Run game與暫停實測通過；舊v31手動檔隱藏保留，未刪除，價格未改。
- itch-v55.json：完整遊戲payload同測試SHA；CDN另追加static.itch.io/htmlgame.js，所以公開整檔SHA不同，不能宣稱位元組全部相同。
- 本次無遊戲源碼改動，不提高BUILD或重跑63項；沿用同SHA完整報告，加做安裝／線上發布驗證。
