# GOO BLASTER 精簡交接

## 目前任務（2026-09-29，v79驗證完成，交付進行中）
- 使用者要求移除兩個回主畫面按鈕，統一放到最下方導覽，改善手機觸控。
- 分支codex/soft-world-ui；接手HEAD3978977，安全pull已完成。v78遊戲commit2cc09a4已發布APK，勿重做。
- 本次v0.9.79尚未commit/push；預定Summary：v0.9.79: unify home navigation in the bottom bar。
- HTML SHA 6c8259ca544dd2087907061a51afa4be3ecdd7dd49cee604508a1883bf8fb538。
- .codex-remote-attachments使用者附件不可提交；私人收據僅_private。

## 改動
- 五格底列：冒險／強化／主畫面／庭院／設定，主畫面居中；移除homeHeader與btnShopBack。
- 88px底列加safe-area，至少48px觸控目標與4px間距；目前頁依aria-current變色。戰鬥仍隱藏整個導覽。
- 商店由內層清單改為整頁捲動並保存捲動位置；內容末端不被底列遮住。
- 庭院就地面板依內容上緣定位，不再依頂端返回鍵；11語言新增navHome短標籤，由i18n/build_v0979.py產生。
- 無玩法、倒數、價格或存檔格式改动。AGENTS第25／27節記錄使用者新決策。
- docs-22-bottom-navigation.md與docs-14-history.md有根因／新布局／量測；完成後更新結果。

## 驗證證據
- 新py_bottom_nav已註冊，完整套件86項。44版面、220次實際tap、中央位置、顏色、完整可見、三主題中途返回、存檔隔離。
- 未改v78實跑新測試FAIL，證據_private/baseline78-bottom/regression.log。
- 182213-bottom79-edges：py_soft_ui／py_town_home／py_garden_context／py_selection_feedback四項PASS且SHA未變。
- 完整：_private/test-runs/20260929-182818-349067-bottom79-full/results.json，首輪85/86，保留py_ui_fixes舊容器失敗。
- 原py_ui_fixes失敗因仍要求shopList內層捲動，已改測shop整頁真實觸控，185020-bottom79-cpu4-retry補跑PASS，真實滑動129px；保持原失敗報告。
- CPU4底列160.8秒／就地面板196.8秒PASS；同批三項全綠，合併完整86/86。效能獨立47.8→49.5FPS PASS。
- py_release_smoke CPU4離線／新存檔／真實重開PASS，恢復progress9 coins456 meta.dmg2 selection8，0錯誤／0外部請求。
- CUA本機實際強化→首頁→池塘→開始→移動鱼→首頁正常；中英390px截圖store/screenshots/v0.9.79已目視。
- 首次末項可見檢查scrollIntoView留下0.47px裁切，改實際捲到底後完整可見，不放寬門檻。
- .venv/Scripts/python.exe；GOO_BROWSER_CHANNEL=msedge、PYTHONUTF8=1、NODE_PATH=_private/test-node/node_modules。
- Surface依既定限制不跑全平行；本次ADB無裝置，Pixel未更新。

## 發版狀態與下一步
- v79尚未建置、上傳或發布；測試完成→遊戲commit/push→APK建置稽核／固定測試通道→itch→Pages→中英Devlog→商店／原論壇／profile→cleanup。
- v78 Butler build2029949現已Active，先前處理卡點已解除；不重傳v78。本批可合併v78選取色與v79導覽更新的Devlog。
- v78 APK97800／0.9.78-test.0已公開核對，APK SHA0edd3af57f8998728fca0d7eb6184f27014f871a49a18c640191eb2d0c15f3fb。
- 固定APK入口：https://github.com/davidform/goo-blaster/releases/tag/android-test。
- Pages／Devlog／商店介紹／原論壇首文與profile目前仍v77，不能宣稱已同步。
- 原論壇17090045仍保留5圖；先前選句局部替換會把新字插到开頭，沒有Save错误內容。後續須驗證完整正文／圖片／實際送出欄位才提交。
- 原論壇編輯https://itch.io/post/17090045/edit；公帖https://itch.io/t/6826201/50-stages-no-ads-no-gacha-works-offline-my-browser-roguelite-needs-breaking。
- 本版清理尚未執行，僅平台同步完後執行cleanup_local盤點再Apply。

## 限制
- 單代理；真人手持舒適度／聽感／市場／母語潤稿／Pixel覆蓋更新仍需實際回饋。
- 小鎮是原創小型場景，不以自動測試或畫面布局宣稱已達參考作品的內容量或市場驗證。
