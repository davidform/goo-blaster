# 聲音、語言與難度整體檢查

使用者於2026-09-09提出五項需求：重做背景音樂與音效、改善怪物命名、查11語言準確度、檢查難度與局內道具、檢查糖果屋滿級後的成長困境。各項分版修改，不能用一版混改後的勝率推論哪項有效。

## 聲音：v0.9.42

研究方向是讓常態音樂、武器、受傷及Boss事件各有清楚角色。Audiokinetic的[互動音樂文件](https://www.audiokinetic.com/en/public-library/2024.1.8_8893/?id=creating_interactive_music&source=Help)與[混音控制說明](https://www.audiokinetic.com/ja/library/edge/?id=defining_properties_of_bus&source=Help)提供狀態切換和訊號層次的參考。本作仍使用內建Web Audio，不導入Wwise或外部音檔。

已確認的根因與改動：

- 舊musicIntensity只改112/158 BPM，沒有改M.theme。實際spawnBoss後musicDebug仍為cute，因此原有Boss曲式從未啟用。新版本真正切到Boss主題，普通/Boss使用104/124 BPM。
- 原一般主題每個十六分音符都播放琶音，另疊高頻噪音鼓。這是「聽感可能疲勞」的設計判斷，不是所有玩家的問卷結果。新版本採四小節旋律與休止、柔和鍵音、較低的鼓聲頻段；Boss另有小調句型。
- 重複射擊、命中與拾取音減少噪音及尖銳高頻層。水泡為短促下滑音、噴槍為低頻噴霧、溜溜球為上下滑音；每種武器各有節流，避免同時開火時全部被第一種武器占用。
- 音效原本消耗遊戲共用Math.random，調音會干擾固定亂數的卡池/難度比較。改成音訊私有亂數，不改遊戲機率。實測同一組音效舊版消耗22次、新版0次遊戲亂數。
- 舊停止音樂的延遲回呼可能停掉剛重新開始的音樂。新增世代檢查；音源結束後斷開連線，靜音時不再建立背景音樂音源。

音訊驗證：`tests/render_audio_samples.py`在暫存HTML插入排程掛鉤，以實際遊戲的合成器做OfflineAudioContext輸出；不是錄自手機揚聲器。舊版audio-v0941、新版audio-v0942-final，各含一般/Boss音樂、三武器、受傷與混音共7段WAV及JSON。

| 固定排程 | 舊音源數 | 新音源數 | 新版削波樣本 |
|---|---:|---:|---:|
| 一般主題四小節 | 132 | 78 | 0 |
| Boss主題四小節 | 132（仍用cute） | 88 | 0 |
| 代表性戰鬥混音 | 815 | 681 | 0 |

上述是合成器建立的音源數，不能換算成Pixel FPS改善百分比。主觀音色已提供試聽，手機揚聲器／耳機的聽感與真機效能仍待玩家實測。

`py_audio_quality.py`走真實AudioContext：三種武器同時有音源、Boss出現/死亡主題切換、快速停止重啟、靜音不分配音源、音源結束後回收、音訊不消耗遊戲亂數。舊v41對照確實在亂數斷言失敗；新版通過，78個音源全部結束並斷開。完整套件與最終壓測狀態見HANDOFF及歷史。

## 命名與11語言：v0.9.43，未宣稱母語潤稿完成

- [Microsoft writing style](https://learn.microsoft.com/en-us/windows/apps/design/style/writing-style)建議採常用而清楚的詞；[IGDA在地化建議](https://igda.org/news-archive/high-quality-localization-help-loc-help-you/)強調可玩的版本、語境與術語。這比孤立地逐字翻譯更適合本作。
- 舊Boss名稱含Molar、Archfiend、Omega等詞；Jawbreaker亦有特定糖果語境，見[Cambridge詞條](https://dictionary.cambridge.org/us/dictionary/english/jawbreaker?topic=sweets)。改為輪廓／常見角色稱呼，固定b1-b3/sb0-sb9識別碼，11語言同步：Jelly Giant、Caramel Guard、Candy King，以及Spiky Jelly、Candy Knight、Horned Jelly、Blue Guardian、Crowned Jelly、Glowing Giant、Winged King、Golden Beast、Star King、Jelly Dragon。此為易讀性的設計判斷，尚無跨國玩家理解率調查。
- 修正lv10d沿用「第一章、首次Mega Boss、每10關」的過期原文。第5/10關說明現在從實際章節欄位與首個章節Boss間距填參數；實測Boss在5、10…50關。兔子速度改為相對說明，避免速度上限造成「兩倍」不實；自爆怪改用Burst Jellies等描述名稱，翻滾提示不再用i-frames縮寫。
- 日文地面Goo統一為ジェル，韓文為젤，明示膠體材質。角色名稱仍用各語言的Jelly／果凍詞，不將地面危險與怪物識別碼混在一起。
- 241鍵×11語言已做數值字面比對及語境修正；字面差異仍包含one/double與日韓數字寫法，這不是語意準確度分數。母語者潤稿尚未完成，不能宣稱每句都精準自然。
- 長文案實際手勢測試發現v41主畫面的子元素仍是touch-action:none：320×480從說明文字滑動，scrollTop為0。修正子元素後同樣手勢為91，開始按鈕完整可見。新增py_l10n_context覆蓋實際手勢、章節規則、13個Boss身份及日韓術語；不再只檢查overflow數值。
- 截圖另抓到章節Boss未計入主畫面Boss數：第5關1→2、第10關3→4。改讀buildBosses(L).length，新增50關實際出場表與畫面計數核對。

## 難度、局內道具與糖果屋：待實測後選單一槓桿

- 不要求每關嚴格單調增加；現有章節開頭回落是喘息安排。要找的是不合理的跳升、上限後仍有無法靠操作解決的壓力，及道具的實際收益。
- 分開量零永久強化、合理累積、全滿三種狀態；固定輸入、同批比較。既有笨bot隨機選卡不能代表真人會優先點救命卡，也不能把少量試跑當成玩家勝率。
- 優先檢查第7關多種變化同時出現，以及晚期滿強化是否仍有有效的閃避／輸出窗口。先確認增益確實套用，再判斷是否足以應對。
- 現有商店總成本8930；既有測試確認滿級會增加生命、傷害、攻速、拾取、起始武器、復活與經驗收益。但這只能證明功能生效，不能證明50關的体验都合理。不得以增加無限強化或新貨幣取代難度檢查。

研究取捨：Mike Lopez的[Gameplay Progression](https://www.gamedeveloper.com/design/gameplay-design-fundamentals-gameplay-progression)將機制、時長、回饋與難度一起評估；[Hades官方FAQ](https://www.supergiantgames.com/blog/hades-faq/)則說明永久成長之外另有可選生存輔助。對本作的推論是：不應把刷滿商店當成所有操作程度玩家都能通關的保證，也不必用無限成長掩蓋關卡跳升。

2026-09-09診斷新發現（先修實際錯誤，再繼續整體比較）：

- 固定位置／30秒／停用玩家武器、Boss不受傷的50關火力診斷，第6→7關同時敵彈峰值31→59、平均19.51→41.80。這與舊工具幾何、暴走時機不同，不拿舊+178%直接當現況。一般ring冷卻×1.6的實驗使第7關峰值50、平均33.74；尚未寫入遊戲。
- 遠視糖鏡在390×844畫面860個可視位置，0→3級可鎖目標皆860；噴槍初速470、壽命0.52秒也不變。實際300px外的固定敵人，噴槍四種商店等級皆0傷害；溜溜球最大前進距離皆149.77px。這證明「數字有加」不代表有效射程有增加。證據range-probe.json、range-hit-before.json；此時尚未修改強化。
- 固定60Hz、虛擬計時器、真實loop/TouchEvent/選卡處理的診斷，在第30關長局遇到敵彈讀取undefined。簡化重現：1心、1次蠟燭、3顆重疊敵彈，update觸發復活清彈後仍讀取舊索引，得到TypeError。真實rAF碰撞回歸測試亦失敗，不是模擬計時器獨有。證據revive-collision-before.json與revive-collision-old.log。
- 此次生存矩陣因錯誤中斷，不能宣稱50關難度完成驗收。已完成的樣本顯示強化有幫助，但bot策略與三個固定種子不是玩家勝率；完成修正後須重跑。虛擬時間診斷停用畫圖，不用來判定FPS或Pixel體驗。

### 測量工具修正：未完成不等於失敗

初版balance／range對照限制360秒虛擬牆鐘，晚期大量hitstop會讓遊戲時間只走到約200～240秒；部分`win:false`其實同時`over:false`、仍有愛心與蠟燭。**舊檔的0/3未通關不能解讀成三次陣亡**，亦不能据此調低難度。已增加明确clear／defeat／unfinished狀態、延長安全上限，未完成樣本令工具明確報錯；受傷追蹤保留來源及護盾事件。

同時補上原bot未使用的道具操作：安全時拾取、危險時使用已取得的核彈、危險時且冷卻完成便翻滾。固定每4.67秒翻滾的舊策略不能量到糖果屋將冷卻降到1.95秒的完整收益。

finished-balance-ab.json是首次全部有真正勝負的後期對照（各3固定種子、同批滿商店、reactive策略）：第30關修射程前2/3、後3/3通關；第50關皆0/3陣亡，最後受傷以敵彈為主。這仍是工具樣本，不是玩家勝率。舊prepared／late-speed檔含截短樣本，保留反省用途，不當驗收數字。

### 已找到的保護時間覆蓋問題

放慢後期彈速（上限1.9／1.75）或增加攻擊間隔（atkSlow下限0.75／0.8），在完成勝負的對照中未帶來穩定通關改善，因此不採用。另測受傷保護加倍，結果竟與原版逐項相同，遂檢查所有寫入iframe的路徑。

真正重現的問題：tryDash直接將P.iframe設為0.42，覆蓋了較長的既有保護。實際hurtPlayer→tryDash：一般受傷1.45→0.42、急救棒棒糖2.1→0.42、護盾0.9→0.42、蠟燭復活3.2→0.42（dash-iframe-before.json）。這會讓危險時主動翻滾的玩家提早失去保護，亦掩蓋商店／救命卡應有的收益。

下一個獨立修正應保留max(現有無敵,0.42)，不是新增保護秒數或無限強化。已准备dash-only及range-dash-fixed候選與真實雙指操作回歸，正式遊戲尚未套用；不新增Gentle模式，先恢復既有機制的正確行為。
