"""Fifty short scenes from ten settings and five journey beats, in eleven locales."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROWS={
'en':[
'The story so far',
'The village jam fountain has lost its glow. A trail of scattered candy leads away from home.',
'Blue light flickers behind the candy town’s empty windows. Someone is stealing the warmth from every oven.',
'The whispering forest has swallowed the road. Thorn-covered sweets mark a path between the trees.',
'The abandoned station’s clock has stopped. A train full of stolen candy waits in the mist.',
'Footsteps echo through an empty castle. Suits of armor are guarding a stolen light.',
'The frozen bell tower rings without a hand to move it. Shadows stir beneath the ice.',
'A storm tears across the broken sky bridges. A winged ruler has hidden the next light above the clouds.',
'The golden mine is melting from within. A sleeping beast blocks the last safe tunnel.',
'Stars vanish above a cracked world. Beyond the ruins, a crowned shadow feeds the growing rift.',
'The last candy lantern hangs above a sea of fire. The jelly dragon guards the rift at the end of the world.',
'You arrive at the edge of this strange place. Follow the candy trail to find where the light went.',
'The way home is fading behind you. Push ahead while the last lanterns still show the path.',
'A faint glow calls from deeper inside. Reach it before the shadows close around the trail.',
'The guardian’s gate is close. Gather your courage for the darkness waiting beyond it.',
'The guardian stands between you and the stolen light. Defeat it to let this place shine again.'
],
'zh-Hant':[
'這一關的故事',
'村裡的果醬泉失去了光芒。散落的糖果一路延伸，指向家園之外。',
'糖果鎮空蕩的窗後閃著藍光。有人正在偷走每一座烤爐的溫暖。',
'低語森林吞沒了道路。纏著荊棘的糖果，在樹叢間標出一條小徑。',
'廢棄車站的時鐘停止轉動。滿載失竊糖果的列車，靜靜停在迷霧裡。',
'空無一人的城堡傳出腳步聲。一副副盔甲，守著被偷走的光。',
'冰封鐘塔無人敲打卻響起鐘聲。冰層底下，有影子正在甦醒。',
'暴風撕扯著斷裂的空中橋梁。長翼的王，把下一道光藏在雲端之上。',
'黃金礦坑正從內部熔化。沉睡的巨獸，擋住了最後一條安全隧道。',
'破碎世界上方的星星逐一熄滅。廢墟深處，戴冠的暗影正在餵養裂隙。',
'最後一盞糖果燈懸在火海上。果凍巨龍守著世界盡頭的裂隙。',
'你抵達這片陌生地方的邊緣。循著糖果的蹤跡，找出光芒去了哪裡。',
'回家的路在身後漸漸消失。趁最後幾盞燈還亮著，繼續向前。',
'深處傳來微弱的光。在暗影吞沒小徑之前，努力靠近它。',
'守護者的大門就在前方。鼓起勇氣，準備面對門後的黑暗。',
'守護者擋住了被偷走的光。打敗它，讓這片地方重新亮起來。'
],
'zh-Hans':[
'这一关的故事',
'村里的果酱泉失去了光芒。散落的糖果一路延伸，指向家园之外。',
'糖果镇空荡的窗后闪着蓝光。有人正在偷走每一座烤炉的温暖。',
'低语森林吞没了道路。缠着荆棘的糖果，在树丛间标出一条小径。',
'废弃车站的时钟停止转动。满载失窃糖果的列车，静静停在迷雾里。',
'空无一人的城堡传出脚步声。一副副盔甲，守着被偷走的光。',
'冰封钟塔无人敲打却响起钟声。冰层底下，有影子正在苏醒。',
'暴风撕扯着断裂的空中桥梁。长翼的王，把下一道光藏在云端之上。',
'黄金矿坑正从内部熔化。沉睡的巨兽，挡住了最后一条安全隧道。',
'破碎世界上方的星星逐一熄灭。废墟深处，戴冠的暗影正在喂养裂隙。',
'最后一盏糖果灯悬在火海上。果冻巨龙守着世界尽头的裂隙。',
'你抵达这片陌生地方的边缘。循着糖果的踪迹，找出光芒去了哪里。',
'回家的路在身后渐渐消失。趁最后几盏灯还亮着，继续向前。',
'深处传来微弱的光。在暗影吞没小径之前，努力靠近它。',
'守护者的大门就在前方。鼓起勇气，准备面对门后的黑暗。',
'守护者挡住了被偷走的光。打败它，让这片地方重新亮起来。'
],
'ja':[
'このステージの物語',
'村のジャムの泉が光を失った。落ちたキャンディが、村の外へと続いている。',
'誰もいないお菓子の町で、窓の奥に青い光が揺れる。何者かがかまどの温もりを奪っている。',
'ささやく森が道を飲み込んだ。とげに絡まったお菓子が、木々の間に道を示している。',
'廃駅の時計は止まったまま。盗まれたお菓子を積んだ列車が、霧の中で待っている。',
'誰もいない城に足音が響く。鎧たちが、盗まれた光を守っている。',
'凍った鐘楼の鐘が、ひとりでに鳴る。氷の下で影が目覚めようとしている。',
'嵐が壊れた空の橋を引き裂く。翼の王は、次の光を雲の上に隠した。',
'黄金の鉱山が内側から溶け始めた。眠る巨獣が、最後の安全なトンネルをふさいでいる。',
'ひび割れた世界の空から星が消えていく。廃墟の奥で、冠をかぶった影が裂け目を広げている。',
'最後のお菓子の灯りが火の海の上にともる。ゼリードラゴンが、世界の果ての裂け目を守っている。',
'見知らぬ場所の入口にたどり着いた。キャンディの跡をたどり、光の行方を探そう。',
'帰り道が後ろで薄れていく。残った灯りが道を照らすうちに、先へ進もう。',
'奥でかすかな光が呼んでいる。影が道を包み込む前に、そこへ近づこう。',
'守り手の門はもうすぐだ。勇気を集めて、門の向こうの闇に備えよう。',
'守り手が盗まれた光の前に立ちはだかる。倒して、この場所に明かりを取り戻そう。'
],
'ko':[
'이번 스테이지 이야기',
'마을의 잼 분수가 빛을 잃었어요. 흩어진 사탕이 마을 밖으로 길게 이어져 있어요.',
'텅 빈 사탕 마을의 창문 뒤로 푸른빛이 깜박여요. 누군가 모든 화덕의 온기를 훔치고 있어요.',
'속삭이는 숲이 길을 삼켜 버렸어요. 가시에 감긴 사탕들이 나무 사이로 길을 알려 줘요.',
'버려진 역의 시계가 멈췄어요. 도둑맞은 사탕을 실은 기차가 안개 속에서 기다려요.',
'아무도 없는 성에서 발소리가 울려요. 갑옷들이 도둑맞은 빛을 지키고 있어요.',
'얼어붙은 종탑의 종이 저절로 울려요. 얼음 아래에서 그림자들이 깨어나요.',
'폭풍이 부서진 하늘 다리를 찢어 놓아요. 날개 달린 왕이 다음 빛을 구름 위에 숨겼어요.',
'황금 광산이 안쪽부터 녹고 있어요. 잠든 거대한 짐승이 마지막 안전한 터널을 막고 있어요.',
'갈라진 세계 위로 별들이 사라져요. 폐허 너머에서 왕관 쓴 그림자가 균열을 키우고 있어요.',
'마지막 사탕 등불이 불바다 위에 걸려 있어요. 젤리 드래곤이 세상 끝의 균열을 지켜요.',
'낯선 곳의 입구에 도착했어요. 사탕 자국을 따라 빛이 어디로 갔는지 찾아봐요.',
'돌아갈 길이 뒤에서 희미해져요. 마지막 등불이 길을 비출 때 앞으로 나아가요.',
'깊은 곳에서 희미한 빛이 불러요. 그림자가 길을 덮기 전에 그곳으로 다가가요.',
'수호자의 문이 가까워졌어요. 용기를 내어 문 너머의 어둠에 대비해요.',
'수호자가 도둑맞은 빛을 가로막고 있어요. 수호자를 물리치고 이곳을 다시 밝혀요.'
],
'de':[
'Die Geschichte dieses Levels',
'Der Marmeladenbrunnen im Dorf leuchtet nicht mehr. Verstreute Bonbons führen von zu Hause fort.',
'Hinter den leeren Fenstern der Süßigkeitenstadt flackert blaues Licht. Jemand stiehlt die Wärme aus allen Öfen.',
'Der flüsternde Wald hat die Straße verschluckt. Süßigkeiten voller Dornen markieren einen Weg zwischen den Bäumen.',
'Die Uhr im verlassenen Bahnhof steht still. Ein Zug voller gestohlener Süßigkeiten wartet im Nebel.',
'Schritte hallen durch eine leere Burg. Rüstungen bewachen ein gestohlenes Licht.',
'Die Glocke im gefrorenen Turm läutet von selbst. Unter dem Eis erwachen Schatten.',
'Ein Sturm zerreißt die kaputten Himmelsbrücken. Ein geflügelter König hat das nächste Licht über den Wolken versteckt.',
'Die Goldmine schmilzt von innen. Ein schlafendes Ungeheuer versperrt den letzten sicheren Tunnel.',
'Über der zerbrochenen Welt verschwinden die Sterne. Hinter den Ruinen nährt ein gekrönter Schatten den wachsenden Riss.',
'Die letzte Bonbonlaterne hängt über einem Feuermeer. Der Geleedrache bewacht den Riss am Ende der Welt.',
'Du erreichst den Rand dieses fremden Ortes. Folge der Bonbonspur und suche das verschwundene Licht.',
'Hinter dir verblasst der Heimweg. Geh weiter, solange die letzten Laternen noch den Weg zeigen.',
'Aus der Tiefe lockt ein schwaches Leuchten. Erreiche es, bevor die Schatten den Pfad verschlingen.',
'Das Tor des Wächters ist nah. Sammle Mut für die Dunkelheit dahinter.',
'Der Wächter steht vor dem gestohlenen Licht. Besiege ihn, damit dieser Ort wieder leuchten kann.'
],
'fr':[
'L’histoire de ce niveau',
'La fontaine de confiture du village ne brille plus. Des bonbons éparpillés forment une piste qui s’éloigne des maisons.',
'Une lueur bleue vacille derrière les fenêtres vides de la ville sucrée. Quelqu’un vole la chaleur de tous les fours.',
'La forêt murmurante a englouti la route. Des friandises couvertes d’épines indiquent un passage entre les arbres.',
'L’horloge de la gare abandonnée s’est arrêtée. Un train de bonbons volés attend dans la brume.',
'Des pas résonnent dans un château vide. Des armures gardent une lumière volée.',
'La cloche du beffroi gelé sonne toute seule. Des ombres s’éveillent sous la glace.',
'Une tempête déchire les ponts brisés du ciel. Un roi ailé a caché la prochaine lumière au-dessus des nuages.',
'La mine d’or fond de l’intérieur. Une bête endormie bloque le dernier tunnel sûr.',
'Les étoiles disparaissent au-dessus du monde fissuré. Au-delà des ruines, une ombre couronnée nourrit la faille.',
'La dernière lanterne de bonbons surplombe une mer de feu. Le dragon de gelée garde la faille au bout du monde.',
'Tu arrives aux portes de cet endroit étrange. Suis les bonbons pour retrouver la lumière disparue.',
'Le chemin du retour s’efface derrière toi. Avance tant que les dernières lanternes éclairent encore la route.',
'Une faible lueur t’appelle plus loin. Rejoins-la avant que les ombres n’engloutissent le sentier.',
'La porte du gardien est proche. Rassemble ton courage pour affronter l’obscurité qui t’attend.',
'Le gardien se tient devant la lumière volée. Bats-le pour que cet endroit brille à nouveau.'
],
'es':[
'La historia de este nivel',
'La fuente de mermelada del pueblo ha perdido su brillo. Un rastro de caramelos se aleja de casa.',
'Una luz azul parpadea tras las ventanas vacías de la ciudad de dulces. Alguien roba el calor de todos los hornos.',
'El bosque susurrante se ha tragado el camino. Dulces cubiertos de espinas señalan un sendero entre los árboles.',
'El reloj de la estación abandonada se ha parado. Un tren lleno de dulces robados espera en la niebla.',
'Resuenan pasos en un castillo vacío. Unas armaduras vigilan una luz robada.',
'La campana de la torre helada suena sola. Bajo el hielo despiertan sombras.',
'Una tormenta azota los puentes rotos del cielo. Un rey alado ha escondido la siguiente luz sobre las nubes.',
'La mina de oro se derrite desde dentro. Una bestia dormida bloquea el último túnel seguro.',
'Las estrellas desaparecen sobre el mundo agrietado. Más allá de las ruinas, una sombra coronada alimenta la grieta.',
'El último farol de caramelo cuelga sobre un mar de fuego. El dragón de gelatina protege la grieta del fin del mundo.',
'Llegas al borde de este lugar extraño. Sigue el rastro de caramelos para encontrar la luz perdida.',
'El camino a casa se desvanece a tu espalda. Avanza mientras los últimos faroles aún iluminen la ruta.',
'Un débil resplandor te llama desde el interior. Acércate antes de que las sombras cubran el sendero.',
'La puerta del guardián está cerca. Reúne valor para afrontar la oscuridad que te espera.',
'El guardián se interpone entre tú y la luz robada. Derrótalo para que este lugar vuelva a brillar.'
],
'it':[
'La storia di questo livello',
'La fontana di marmellata del villaggio ha perso la sua luce. Una scia di caramelle si allontana da casa.',
'Una luce blu tremola dietro le finestre vuote della città dei dolci. Qualcuno ruba il calore da ogni forno.',
'La foresta sussurrante ha inghiottito la strada. Dolci coperti di spine indicano un sentiero tra gli alberi.',
'L’orologio della stazione abbandonata si è fermato. Un treno carico di dolci rubati attende nella nebbia.',
'Dei passi risuonano in un castello vuoto. Alcune armature sorvegliano una luce rubata.',
'La campana della torre gelata suona da sola. Sotto il ghiaccio si risvegliano le ombre.',
'Una tempesta squarcia i ponti spezzati del cielo. Un re alato ha nascosto la prossima luce sopra le nuvole.',
'La miniera d’oro si scioglie dall’interno. Una bestia addormentata blocca l’ultima galleria sicura.',
'Le stelle scompaiono sopra il mondo incrinato. Oltre le rovine, un’ombra incoronata alimenta la frattura.',
'L’ultima lanterna di caramelle è sospesa su un mare di fuoco. Il drago di gelatina custodisce la frattura alla fine del mondo.',
'Arrivi ai margini di questo strano luogo. Segui la scia di caramelle per ritrovare la luce perduta.',
'La strada di casa svanisce alle tue spalle. Avanza finché le ultime lanterne illuminano il sentiero.',
'Un debole bagliore ti chiama dall’interno. Raggiungilo prima che le ombre avvolgano il cammino.',
'Il portone del guardiano è vicino. Fatti coraggio per affrontare l’oscurità che ti aspetta.',
'Il guardiano ti separa dalla luce rubata. Sconfiggilo per far risplendere questo luogo.'
],
'pt-BR':[
'A história desta fase',
'A fonte de geleia da vila perdeu o brilho. Uma trilha de doces espalhados leva para longe de casa.',
'Uma luz azul pisca atrás das janelas vazias da cidade de doces. Alguém está roubando o calor de todos os fornos.',
'A floresta sussurrante engoliu a estrada. Doces cobertos de espinhos marcam um caminho entre as árvores.',
'O relógio da estação abandonada parou. Um trem cheio de doces roubados espera na neblina.',
'Passos ecoam por um castelo vazio. Armaduras guardam uma luz roubada.',
'O sino da torre congelada toca sozinho. Sombras despertam debaixo do gelo.',
'Uma tempestade rasga as pontes quebradas do céu. Um rei alado escondeu a próxima luz acima das nuvens.',
'A mina de ouro está derretendo por dentro. Uma fera adormecida bloqueia o último túnel seguro.',
'As estrelas desaparecem sobre o mundo rachado. Além das ruínas, uma sombra coroada alimenta a fenda.',
'A última lanterna de doces paira sobre um mar de fogo. O dragão de gelatina guarda a fenda no fim do mundo.',
'Você chega à entrada deste lugar estranho. Siga a trilha de doces para encontrar a luz perdida.',
'O caminho de casa desaparece atrás de você. Siga em frente enquanto as últimas lanternas ainda iluminam a trilha.',
'Um brilho fraco chama lá de dentro. Chegue até ele antes que as sombras cubram o caminho.',
'O portão do guardião está perto. Junte coragem para enfrentar a escuridão do outro lado.',
'O guardião está entre você e a luz roubada. Derrote-o para fazer este lugar brilhar de novo.'
],
'ru':[
'История этого уровня',
'Фонтан варенья в деревне погас. Дорожка из рассыпанных конфет уводит прочь от дома.',
'За пустыми окнами конфетного города мерцает синий свет. Кто-то крадёт тепло из каждой печи.',
'Шепчущий лес поглотил дорогу. Сладости, оплетённые колючками, указывают путь между деревьями.',
'Часы на заброшенной станции остановились. Поезд с украденными сладостями ждёт в тумане.',
'В пустом замке слышны шаги. Доспехи охраняют украденный свет.',
'Колокол в замёрзшей башне звонит сам по себе. Подо льдом просыпаются тени.',
'Буря рвёт разрушенные небесные мосты. Крылатый король спрятал следующий огонёк над облаками.',
'Золотая шахта плавится изнутри. Спящий зверь преграждает последний безопасный тоннель.',
'Над расколотым миром гаснут звёзды. За руинами тень в короне питает растущую трещину.',
'Последний конфетный фонарь висит над морем огня. Желейный дракон охраняет разлом на краю мира.',
'Ты у входа в это странное место. Иди по конфетному следу и найди пропавший свет.',
'Дорога домой исчезает за спиной. Продвигайся вперёд, пока последние фонари ещё освещают путь.',
'Из глубины манит слабое сияние. Доберись до него, пока тени не поглотили тропу.',
'Ворота стража уже близко. Соберись с духом перед тьмой, которая ждёт за ними.',
'Страж стоит между тобой и украденным светом. Одолей его, чтобы это место снова засияло.'
]}
KEYS=['storyTitle']+[f'storyCh{i}' for i in range(10)]+[f'storyStep{i}' for i in range(5)]
TOWN_NAMES={
'en':['Caramel Backstreets','Candy Town Gate'],
'zh-Hant':['焦糖暗巷','糖果鎮城門'],'zh-Hans':['焦糖暗巷','糖果镇城门'],
'ja':['キャラメルの裏通り','お菓子の町の門'],'ko':['캐러멜 뒷골목','사탕 마을의 문'],
'de':['Karamellgassen','Tor der Süßigkeitenstadt'],'fr':['Ruelles de caramel','Porte de la ville sucrée'],
'es':['Callejones de caramelo','Puerta de la ciudad dulce'],'it':['Vicolo di caramello','Porta della città dei dolci'],
'pt-BR':['Becos de caramelo','Portão da cidade dos doces'],'ru':['Карамельные переулки','Ворота конфетного города']}
CONTROL_NAMES={
'en':['Pause game','Launch nuke'],'zh-Hant':['暫停遊戲','發射核彈'],'zh-Hans':['暂停游戏','发射核弹'],
'ja':['ゲームを一時停止','核弾を発射'],'ko':['게임 일시 정지','핵폭탄 발사'],
'de':['Spiel pausieren','Atombombe starten'],'fr':['Mettre en pause','Lancer la bombe nucléaire'],
'es':['Pausar el juego','Lanzar bomba nuclear'],'it':['Metti in pausa','Lancia la bomba nucleare'],
'pt-BR':['Pausar o jogo','Lançar bomba nuclear'],'ru':['Пауза','Запустить ядерную бомбу']}
if __name__=='__main__':
 p=ROOT/'index.html'
 with p.open(encoding='utf-8',newline='') as f:s=f.read()
 old=next(x for x in s.splitlines() if x.startswith('const L10N='))
 data=json.loads(old[11:-1]);assert set(data)==set(ROWS)
 for lang,row in ROWS.items():
  assert len(row)==len(KEYS),(lang,len(row))
  data[lang].update(zip(KEYS,row))
  data[lang].update(zip(['lv9n','lv10n'],TOWN_NAMES[lang]))
  data[lang].update(zip(['pauseAction','launchAction'],CONTROL_NAMES[lang]))
 with p.open('w',encoding='utf-8',newline='') as f:f.write(s.replace(old,'const L10N='+json.dumps(data,ensure_ascii=False)+';'))
 print('Updated 18 narrative/control keys and 2 town-stage names x 11 locales; 50 unique chapter/scene pairs per locale')
