# -*- coding: utf-8 -*-
"""v0.9.21 補漏：7 個原本硬寫中文、沒有走 T() 的顯示字串。

這批是 v0.9.19 多語系改造漏掉的——當時的稽核只掃了 DOM 元素與 L10N 表本身，
沒有掃「直接畫在 canvas 上的字」，所以三個 toast、兩個 HUD 指示、
兩行結算/分享圖統計全部留在中文。真人玩家在英文版看到中文就是這個原因。

用詞刻意沿用既有 key 的譯法以保持一致：
  - 果凍/Goo 的各語言用字 → 對齊 hudGoo
  - 擊殺/Kills → 對齊 hudKills
  - LV → 對齊 hudLv（fr/es 用 NIV、it 用 LIV、pt-BR 用 NÍV、ru 用 УР）
  - 護盾/Shield → 對齊 tShieldGain
  - 暴走/Frenzy → 對齊 tFrenzy
"""

NEW = {
"en": {
  "tChest":    "A chest appeared in the distance — go grab it!",
  "tNukeDrop": "☢️ Nuke supply dropped — go pick it up!",
  "tNukeGet":  "Nuke ready! Tap the icon at bottom-left to fire",
  "hudShield": "Shield ×{0}",
  "hudFrenzy": "FRENZY!",
  "shotStats": "Survived {0}   ·   LV.{1}   ·   {2} kills",
  "shotGoo":   "Goo coverage {0}%",
},
"zh-Hant": {
  "tChest":    "遠處出現寶箱！快去拿",
  "tNukeDrop": "☢️ 出現核彈補給！快去撿",
  "tNukeGet":  "取得核彈！左下角圖示可以引爆",
  "hudShield": "護盾 ×{0}",
  "hudFrenzy": "暴走中！",
  "shotStats": "存活 {0}   ·   LV.{1}   ·   擊殺 {2}",
  "shotGoo":   "果凍覆蓋率 {0}%",
},
"zh-Hans": {
  "tChest":    "远处出现宝箱！快去拿",
  "tNukeDrop": "☢️ 出现核弹补给！快去捡",
  "tNukeGet":  "取得核弹！左下角图标可以引爆",
  "hudShield": "护盾 ×{0}",
  "hudFrenzy": "暴走中！",
  "shotStats": "存活 {0}   ·   LV.{1}   ·   击杀 {2}",
  "shotGoo":   "果冻覆盖率 {0}%",
},
"ja": {
  "tChest":    "遠くに宝箱が出現！急いで取りに行こう",
  "tNukeDrop": "☢️ 核爆弾の補給が出現！拾いに行こう",
  "tNukeGet":  "核爆弾を入手！左下のアイコンで起爆できる",
  "hudShield": "シールド ×{0}",
  "hudFrenzy": "暴走中！",
  "shotStats": "生存 {0}   ·   LV.{1}   ·   撃破 {2}",
  "shotGoo":   "グー占有率 {0}%",
},
"ko": {
  "tChest":    "멀리 보물상자가 나타났다! 어서 가지러 가자",
  "tNukeDrop": "☢️ 핵폭탄 보급이 나타났다! 어서 주우러 가자",
  "tNukeGet":  "핵폭탄 획득! 왼쪽 아래 아이콘으로 폭발시킬 수 있다",
  "hudShield": "실드 ×{0}",
  "hudFrenzy": "폭주 중!",
  "shotStats": "생존 {0}   ·   LV.{1}   ·   처치 {2}",
  "shotGoo":   "구 점유율 {0}%",
},
"de": {
  "tChest":    "In der Ferne ist eine Truhe aufgetaucht – hol sie dir!",
  "tNukeDrop": "☢️ Nuke-Nachschub aufgetaucht – schnapp ihn dir!",
  "tNukeGet":  "Nuke erhalten! Tippe unten links auf das Symbol zum Zünden",
  "hudShield": "Schild ×{0}",
  "hudFrenzy": "RASEREI!",
  "shotStats": "Überlebt {0}   ·   LV.{1}   ·   {2} besiegt",
  "shotGoo":   "Glibber-Abdeckung {0}%",
},
"fr": {
  "tChest":    "Un coffre est apparu au loin — va le chercher !",
  "tNukeDrop": "☢️ Ravitaillement nucléaire apparu — va le ramasser !",
  "tNukeGet":  "Nuke obtenue ! Touche l'icône en bas à gauche pour la déclencher",
  "hudShield": "Bouclier ×{0}",
  "hudFrenzy": "FRÉNÉSIE !",
  "shotStats": "Survie {0}   ·   NIV.{1}   ·   {2} éliminés",
  "shotGoo":   "Couverture de gelée {0}%",
},
"es": {
  "tChest":    "¡Ha aparecido un cofre a lo lejos! Ve a por él",
  "tNukeDrop": "☢️ ¡Ha aparecido un suministro nuclear! Ve a recogerlo",
  "tNukeGet":  "¡Bomba obtenida! Toca el icono de abajo a la izquierda para detonarla",
  "hudShield": "Escudo ×{0}",
  "hudFrenzy": "¡FRENESÍ!",
  "shotStats": "Sobrevivido {0}   ·   NIV.{1}   ·   {2} bajas",
  "shotGoo":   "Cobertura de gelatina {0}%",
},
"it": {
  "tChest":    "È apparso uno scrigno in lontananza — vai a prenderlo!",
  "tNukeDrop": "☢️ È apparsa una scorta nucleare — vai a raccoglierla!",
  "tNukeGet":  "Bomba ottenuta! Tocca l'icona in basso a sinistra per farla esplodere",
  "hudShield": "Scudo ×{0}",
  "hudFrenzy": "FRENESIA!",
  "shotStats": "Sopravvissuto {0}   ·   LIV.{1}   ·   {2} uccisioni",
  "shotGoo":   "Copertura di gelatina {0}%",
},
"pt-BR": {
  "tChest":    "Apareceu um baú ao longe — vá pegá-lo!",
  "tNukeDrop": "☢️ Apareceu um suprimento nuclear — vá pegá-lo!",
  "tNukeGet":  "Bomba obtida! Toque no ícone no canto inferior esquerdo para detonar",
  "hudShield": "Escudo ×{0}",
  "hudFrenzy": "FRENESI!",
  "shotStats": "Sobreviveu {0}   ·   NÍV.{1}   ·   {2} abates",
  "shotGoo":   "Cobertura de gosma {0}%",
},
"ru": {
  "tChest":    "Вдалеке появился сундук — скорее за ним!",
  "tNukeDrop": "☢️ Появился ядерный заряд — подбери его!",
  "tNukeGet":  "Заряд получен! Нажмите значок внизу слева, чтобы взорвать",
  "hudShield": "Щит ×{0}",
  "hudFrenzy": "ЯРОСТЬ!",
  "shotStats": "Выжил {0}   ·   УР.{1}   ·   убито: {2}",
  "shotGoo":   "Покрытие слизью {0}%",
},
}
