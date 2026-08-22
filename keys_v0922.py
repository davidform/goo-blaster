# -*- coding: utf-8 -*-
"""v0.9.22：全新的 Boss 名稱（13 個）＋ 盔甲碎裂提示，11 種語言。

命名設計原則（使用者回饋「BOSS 的名稱太遜了」）：
  1. 舊名是上班族笑話（加班文件怪／已讀不回怪）。對兒童客群不好笑，
     對任何客群都不威風，而且翻成英文之後更弱（"Overtime Paperwork"）。
  2. 新名維持糖果／果凍的世界觀，但用「材質 + 頭銜」的結構，
     頭銜本身構成一條清楚的力量階梯：
       Brute 蠻兵 < Warden 獄卒 < Tyrant 暴君                （一般 Boss）
       Crusher 粉碎者 < Warlord 督戰王 < Reaper 收割者 <
       Overlord 霸主 < Devourer 吞噬者 < Colossus 巨像 <
       Sovereign 君主 < Archfiend 魔君 < Titan 泰坦 < Ender 滅世者
     玩家不需要看數值，光看名字就知道「下一隻更兇」。
  3. 每個語言都用該語言自己的頭銜階梯，不是直譯——
     所以 fr/es/it/pt 的 Overlord 與 Sovereign 刻意用不同的字，避免撞名。
  4. 長度控制：HUD 有寬度限制（v0.9.21 已加自動縮放＋截斷），
     但仍盡量壓在 2~3 個詞以內。
"""

NEW = {
"en": {
  "b1":"Gumdrop Brute", "b2":"Syrup Warden", "b3":"Jawbreaker Tyrant",
  "sb0":"Molar Crusher",      "sb1":"Sourfang Warlord",   "sb2":"Licorice Reaper",
  "sb3":"Frostbite Overlord", "sb4":"Cinder Devourer",    "sb5":"Obsidian Colossus",
  "sb6":"Nightmare Sovereign","sb7":"Abyss Archfiend",    "sb8":"Starfall Titan",
  "sb9":"Omega, the Ender",
  "tArmorBreak":"ARMOR SHATTERED!",
},
"zh-Hant": {
  "b1":"軟糖蠻兵", "b2":"糖漿獄卒", "b3":"硬糖暴君",
  "sb0":"臼齒粉碎者", "sb1":"酸牙督戰王", "sb2":"甘草收割者",
  "sb3":"霜噬霸主",   "sb4":"燼焰吞噬者", "sb5":"黑曜巨像",
  "sb6":"夢魘君主",   "sb7":"深淵魔君",   "sb8":"隕星泰坦",
  "sb9":"終焉·滅世者",
  "tArmorBreak":"盔甲碎裂！",
},
"zh-Hans": {
  "b1":"软糖蛮兵", "b2":"糖浆狱卒", "b3":"硬糖暴君",
  "sb0":"臼齿粉碎者", "sb1":"酸牙督战王", "sb2":"甘草收割者",
  "sb3":"霜噬霸主",   "sb4":"烬焰吞噬者", "sb5":"黑曜巨像",
  "sb6":"梦魇君主",   "sb7":"深渊魔君",   "sb8":"陨星泰坦",
  "sb9":"终焉·灭世者",
  "tArmorBreak":"盔甲碎裂！",
},
"ja": {
  "b1":"グミの荒くれ", "b2":"シロップの獄卒", "b3":"硬飴の暴君",
  "sb0":"臼歯クラッシャー", "sb1":"酸牙の軍王",   "sb2":"リコリスの刈り手",
  "sb3":"氷噛みの覇王",     "sb4":"燼焔の喰らい手","sb5":"黒曜の巨像",
  "sb6":"悪夢の君主",       "sb7":"深淵の魔王",   "sb8":"流星のタイタン",
  "sb9":"オメガ・終焉者",
  "tArmorBreak":"装甲破壊！",
},
"ko": {
  "b1":"젤리 난폭자", "b2":"시럽 간수", "b3":"사탕 폭군",
  "sb0":"어금니 분쇄자", "sb1":"산성송곳니 군왕", "sb2":"감초 수확자",
  "sb3":"서릿니 군주",   "sb4":"잿불 포식자",     "sb5":"흑요석 거상",
  "sb6":"악몽의 지배자", "sb7":"심연의 마왕",     "sb8":"유성 타이탄",
  "sb9":"오메가, 종말자",
  "tArmorBreak":"장갑 파괴!",
},
"de": {
  "b1":"Gummidrops-Rohling", "b2":"Sirup-Wärter", "b3":"Bonbon-Tyrann",
  "sb0":"Backenzahn-Zermalmer", "sb1":"Säurezahn-Kriegsherr", "sb2":"Lakritz-Schnitter",
  "sb3":"Frostbiss-Oberherr",   "sb4":"Aschenglut-Verschlinger","sb5":"Obsidian-Koloss",
  "sb6":"Albtraum-Souverän",    "sb7":"Abgrund-Erzdämon",       "sb8":"Sternenfall-Titan",
  "sb9":"Omega, der Ender",
  "tArmorBreak":"PANZER ZERBROCHEN!",
},
"fr": {
  "b1":"Brute en Gomme", "b2":"Gardien de Sirop", "b3":"Tyran de Bonbon",
  "sb0":"Broyeur de Molaires", "sb1":"Chef de Guerre Croc-Acide", "sb2":"Faucheur de Réglisse",
  "sb3":"Suzerain du Gel",     "sb4":"Dévoreur de Braises",       "sb5":"Colosse d'Obsidienne",
  "sb6":"Souverain des Cauchemars","sb7":"Archidémon de l'Abîme", "sb8":"Titan des Étoiles",
  "sb9":"Oméga, la Fin",
  "tArmorBreak":"ARMURE BRISÉE !",
},
"es": {
  "b1":"Bruto de Gominola", "b2":"Guardián de Jarabe", "b3":"Tirano de Caramelo",
  "sb0":"Triturador de Muelas", "sb1":"Señor Colmillo Ácido", "sb2":"Segador de Regaliz",
  "sb3":"Amo Supremo del Hielo","sb4":"Devorador de Brasas",  "sb5":"Coloso de Obsidiana",
  "sb6":"Soberano de Pesadillas","sb7":"Archidemonio del Abismo","sb8":"Titán de Estrellas",
  "sb9":"Omega, el Fin",
  "tArmorBreak":"¡ARMADURA DESTROZADA!",
},
"it": {
  "b1":"Bruto Gommoso", "b2":"Guardiano di Sciroppo", "b3":"Tiranno di Caramella",
  "sb0":"Frantumatore di Molari","sb1":"Signore Zanna Acida", "sb2":"Mietitore di Liquirizia",
  "sb3":"Dominatore del Gelo",   "sb4":"Divoratore di Braci", "sb5":"Colosso d'Ossidiana",
  "sb6":"Sovrano degli Incubi",  "sb7":"Arcidemone dell'Abisso","sb8":"Titano delle Stelle",
  "sb9":"Omega, la Fine",
  "tArmorBreak":"ARMATURA IN FRANTUMI!",
},
"pt-BR": {
  "b1":"Brutamontes de Goma", "b2":"Guardião de Xarope", "b3":"Tirano de Bala",
  "sb0":"Triturador de Molares","sb1":"Senhor Presa Ácida",  "sb2":"Ceifador de Alcaçuz",
  "sb3":"Dominador do Gelo",    "sb4":"Devorador de Brasas", "sb5":"Colosso de Obsidiana",
  "sb6":"Soberano dos Pesadelos","sb7":"Arquidemônio do Abismo","sb8":"Titã das Estrelas",
  "sb9":"Ômega, o Fim",
  "tArmorBreak":"ARMADURA DESTRUÍDA!",
},
"ru": {
  "b1":"Мармеладный Громила", "b2":"Сиропный Надзиратель", "b3":"Леденцовый Тиран",
  "sb0":"Дробитель Коренных", "sb1":"Кислотный Военачальник","sb2":"Лакричный Жнец",
  "sb3":"Морозный Владыка",   "sb4":"Пожиратель Углей",      "sb5":"Обсидиановый Колосс",
  "sb6":"Повелитель Кошмаров","sb7":"Архидемон Бездны",      "sb8":"Титан Звездопада",
  "sb9":"Омега, Погибель Миров",
  "tArmorBreak":"БРОНЯ РАЗБИТА!",
},
}
