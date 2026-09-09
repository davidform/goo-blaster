"""Reviewed monster names and rule descriptions; all 11 languages together."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NAMES=['b1','b2','b3']+['sb'+str(i) for i in range(10)]
ROWS={
'en':['Jelly Giant','Caramel Guard','Candy King','Spiky Jelly','Candy Knight','Horned Jelly','Blue Guardian','Crowned Jelly','Glowing Giant','Winged King','Golden Beast','Star King','Jelly Dragon'],
'zh-Hant':['果凍巨人','焦糖守衛','糖果國王','尖刺果凍','糖果騎士','長角果凍','藍色守護者','王冠果凍','發光巨人','飛翼國王','金色巨獸','星光國王','果凍巨龍'],
'zh-Hans':['果冻巨人','焦糖守卫','糖果国王','尖刺果冻','糖果骑士','长角果冻','蓝色守护者','王冠果冻','发光巨人','飞翼国王','金色巨兽','星光国王','果冻巨龙'],
'ja':['ゼリーの巨人','キャラメルの番人','キャンディの王','トゲトゲゼリー','キャンディの騎士','ツノつきゼリー','青い守護者','王冠ゼリー','光る巨人','翼の王','金色の魔獣','星の王','ゼリードラゴン'],
'ko':['젤리 거인','캐러멜 수호자','사탕 왕','가시 젤리','사탕 기사','뿔 달린 젤리','푸른 수호자','왕관 젤리','빛나는 거인','날개 달린 왕','황금 괴수','별의 왕','젤리 드래곤'],
'de':['Gelee-Riese','Karamellwächter','Bonbonkönig','Gelee mit Stacheln','Bonbonritter','Gelee mit Hörnern','Blauer Wächter','Gekröntes Gelee','Leuchtender Riese','Geflügelter König','Goldene Bestie','Sternenkönig','Gelee-Drache'],
'fr':['Géant de gelée','Gardien de caramel','Roi des bonbons','Gelée à piquants','Chevalier des bonbons','Gelée à cornes','Gardien bleu','Gelée couronnée','Géant lumineux','Roi ailé','Bête dorée','Roi des étoiles','Dragon de gelée'],
'es':['Gigante de gelatina','Guardián de caramelo','Rey de los dulces','Gelatina con púas','Caballero de caramelo','Gelatina con cuernos','Guardián azul','Gelatina coronada','Gigante brillante','Rey alado','Bestia dorada','Rey de las estrellas','Dragón de gelatina'],
'it':['Gigante di gelatina','Guardiano di caramello','Re delle caramelle','Gelatina spinosa','Cavaliere delle caramelle','Gelatina con le corna','Guardiano blu','Gelatina incoronata','Gigante luminoso','Re alato','Bestia dorata','Re delle stelle','Drago di gelatina'],
'pt-BR':['Gigante de geleia','Guardião de caramelo','Rei dos doces','Geleia com espinhos','Cavaleiro dos doces','Geleia com chifres','Guardião azul','Geleia coroada','Gigante brilhante','Rei alado','Fera dourada','Rei das estrelas','Dragão de geleia'],
'ru':['Желейный великан','Карамельный страж','Конфетный король','Колючее желе','Конфетный рыцарь','Рогатое желе','Синий страж','Желе с короной','Светящийся великан','Крылатый король','Золотой зверь','Звёздный король','Желейный дракон'],
}
HELP_KEYS=['lv3d','lv5d','lv7d','lv10d','hintDash']
HELP={
'en':[
 'Jelly Bunnies are faster than small jellies. Fewer enemies give you room to learn.',
 'Jelly Shooters fire from a distance. Chapter {0} finale: face your first Mega Boss.',
 'Burst Jellies explode when close and ignite goo on the ground. Three bosses.',
 'Chapter {0} finale. Another Mega Boss awaits; one appears every {1} stages.',
 'Bottom-left »: dash in your direction; briefly invincible'],
'zh-Hant':[
 '兔兔果凍比小果凍更快。這關敵人較少，讓你練習閃躲。',
 '射擊果凍會從遠處開火。第 {0} 章壓軸：迎戰第一隻超級大 Boss。',
 '爆爆果凍靠近就會爆炸，也會點燃地上的果凍。這關有三隻 Boss。',
 '第 {0} 章壓軸。又一隻超級大 Boss 等著你；每 {1} 關會遇到一隻。',
 '左下 »：朝移動方向衝刺，短暫不會受傷'],
'zh-Hans':[
 '兔兔果冻比小果冻更快。这关敌人较少，让你练习闪躲。',
 '射击果冻会从远处开火。第 {0} 章压轴：迎战第一只超级大 Boss。',
 '爆爆果冻靠近就会爆炸，也会点燃地上的果冻。这关有三只 Boss。',
 '第 {0} 章压轴。又一只超级大 Boss 等着你；每 {1} 关会遇到一只。',
 '左下 »：朝移动方向冲刺，短暂不会受伤'],
'ja':[
 'ウサギゼリーは小さなゼリーより速く動きます。敵が少ないこのステージで回避を練習しましょう。',
 '射撃ゼリーは遠くから撃ってきます。第{0}章の最後には、初めての超大型ボスが待っています。',
 '爆発ゼリーは近づくと爆発し、地面のジェルにも引火します。ボスは3体。',
 '第{0}章の最終ステージ。新たな超大型ボスが待っています。{1}ステージごとに登場します。',
 '左下の»で移動方向にダッシュ。短時間ダメージを受けません'],
'ko':[
 '토끼 젤리는 작은 젤리보다 빠릅니다. 적이 적은 이번 스테이지에서 피하는 연습을 해 보세요.',
 '젤리 사수는 멀리서 공격합니다. 챕터 {0}의 마지막 스테이지에서 첫 초대형 보스를 만나세요.',
 '폭발 젤리는 가까이 오면 터지고 바닥의 젤에도 불을 붙입니다. 보스는 3마리입니다.',
 '챕터 {0}의 마지막 스테이지입니다. 또 다른 초대형 보스가 기다립니다. {1}스테이지마다 등장합니다.',
 '왼쪽 아래 »: 이동 방향으로 구르면 잠깐 무적이 됩니다'],
'de':[
 'Gelee-Hasen sind schneller als kleine Gelees. Weniger Gegner geben dir Zeit zum Üben.',
 'Gelee-Schützen feuern aus der Ferne. Finale von Kapitel {0}: Dein erster Megaboss wartet.',
 'Explosive Gelees platzen aus der Nähe und entzünden Glibber am Boden. Drei Bosse.',
 'Finale von Kapitel {0}. Ein weiterer Megaboss wartet; alle {1} Stufen erscheint einer.',
 'Unten links »: in Bewegungsrichtung rollen, kurz unverwundbar'],
'fr':[
 'Les lapins de gelée sont plus rapides que les petites gelées. Moins d’ennemis vous laissent le temps d’apprendre.',
 'Les tireurs de gelée attaquent à distance. Finale du chapitre {0} : affrontez votre premier méga-boss.',
 'Les gelées explosives éclatent de près et enflamment la gelée au sol. Trois boss.',
 'Finale du chapitre {0}. Un autre méga-boss vous attend ; il en apparaît un tous les {1} niveaux.',
 'En bas à gauche » : esquive dans votre direction, brève invincibilité'],
'es':[
 'Los conejos de gelatina son más rápidos que las gelatinas pequeñas. Hay menos enemigos para que puedas practicar.',
 'Las gelatinas tiradoras disparan a distancia. Final del capítulo {0}: enfréntate a tu primer megajefe.',
 'Las gelatinas explosivas estallan de cerca y encienden la gelatina del suelo. Tres jefes.',
 'Final del capítulo {0}. Te espera otro megajefe; aparece uno cada {1} fases.',
 '» abajo a la izquierda: esquiva en tu dirección; invencibilidad breve'],
'it':[
 'I conigli di gelatina sono più veloci delle piccole gelatine. Ci sono meno nemici, così puoi esercitarti.',
 'Le gelatine tiratrici sparano da lontano. Finale del capitolo {0}: affronta il tuo primo megaboss.',
 'Le gelatine esplosive scoppiano da vicino e incendiano la gelatina a terra. Tre boss.',
 'Finale del capitolo {0}. Ti aspetta un altro megaboss: ne appare uno ogni {1} livelli.',
 '» in basso a sinistra: scatta nella tua direzione; breve invincibilità'],
'pt-BR':[
 'Os coelhos de geleia são mais rápidos que as geleias pequenas. Há menos inimigos para você praticar.',
 'Os atiradores de geleia atacam de longe. Final do capítulo {0}: enfrente seu primeiro megachefe.',
 'As geleias explosivas estouram de perto e incendeiam a gosma no chão. Três chefes.',
 'Final do capítulo {0}. Outro megachefe espera por você; um aparece a cada {1} fases.',
 '» embaixo à esquerda: role na direção do movimento; breve invencibilidade'],
'ru':[
 'Желейные кролики быстрее маленьких желе. Врагов меньше, чтобы было легче освоиться.',
 'Желейные стрелки атакуют издалека. Финал главы {0}: вас ждёт первый мегабосс.',
 'Взрывные желе взрываются вблизи и поджигают слизь на земле. Три босса.',
 'Финал главы {0}. Вас ждёт новый мегабосс: они появляются каждые {1} этапов.',
 '» внизу слева: рывок по ходу движения и короткая неуязвимость'],
}
GEL_KEYS=['hudGoo','w_graffiti_d','e_bubble_n','e_bubble_d','e_graffiti_n','e_graffiti_d','u_chain_d','u_mine_n','u_mine_d','u_mine_d2','c_fire_go','shotGoo']
KOREAN_GEL=[
 '젤 {0}%  피해 +{1}%','부채꼴 산탄 · {0}발 · 명중 시 젤 생성','네온 젤 폭우',
 '화면 전체에 젤 비를 내려 적을 느리게 만듭니다','무지개 젤 카펫','뿌린 젤이 자동으로 연쇄 점화됩니다',
 '적 처치 시 30% 확률로 발밑의 젤에 불이 붙습니다','부식 젤','젤 위의 적은 지속 피해를 받습니다',
 '피해 2배, 젤 지속 시간도 증가','젤이 일제히 점화됩니다!','젤 점유율 {0}%']

def main():
    path=ROOT/'index.html';text=path.read_text(encoding='utf-8')
    line=next(x for x in text.splitlines() if x.startswith('const L10N='))
    data=json.loads(line[len('const L10N='):-1])
    assert set(ROWS)==set(HELP)==set(data)
    for lang,values in ROWS.items():
        assert len(values)==len(NAMES) and len(set(values))==len(values)
        data[lang].update(zip(NAMES,values))
        assert len(HELP[lang])==len(HELP_KEYS)
        data[lang].update(zip(HELP_KEYS,HELP[lang]))
    # Other languages already use a material word for the ground goo; retain it.
    for key in GEL_KEYS:data['ja'][key]=data['ja'][key].replace('グー','ジェル')
    assert len(KOREAN_GEL)==len(GEL_KEYS)
    data['ko'].update(zip(GEL_KEYS,KOREAN_GEL))
    path.write_text(text.replace(line,'const L10N='+json.dumps(data,ensure_ascii=False)+';'),encoding='utf-8')
    print('Updated 13 boss names and 5 rule descriptions in all 11 languages; aligned Japanese/Korean gel terms')

if __name__=='__main__':main()
