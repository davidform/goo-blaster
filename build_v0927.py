# -*- coding: utf-8 -*-
"""v0.9.27 的多語系：糖果援軍（同伴寶箱）＋ 免費/付費切點的鎖關與解鎖面板。

一次補齊 11 種語言，遵守長期指令 D（任何修改都要同時做完各語言）。
文字風格跟著各語言既有的寶箱提示走（CJK 用全形驚嘆號、法文驚嘆號前留空格、
俄文數字與單位之間有空格），不要自己另立一套。
"""
import json, io, sys

P = '/home/claude/work/goo-blaster/index.html'
s = io.open(P, encoding='utf-8').read()
lines = s.split('\n')
li = [i for i, l in enumerate(lines) if l.startswith('const L10N=')]
assert len(li) == 1, f"找不到唯一的 L10N（{len(li)} 個）"
L = json.loads(lines[li[0]][len('const L10N='):].rstrip(';'))

NEW = {
 'en': {
   'c_ally_n':'Candy Comrades',
   'c_ally_go':'{0} comrades joined for {1}s!',
   'lockTitle':'Full Game',
   'lockSub':'Stage {0} and beyond are part of the full game.',
   'lockBody':'You have {0} free stages. Unlock all {1} stages — one purchase, no ads, no loot boxes, yours forever.',
   'lockCta':'Get the Full Game',
   'lockLater':'Keep Playing Free',
   'lockTag':'LOCKED',
   'lockDemoEnd':'That is the end of the free stages!',
   'unlocked':'Full game unlocked — all {0} stages!',
 },
 'zh-Hant': {
   'c_ally_n':'糖果援軍',
   'c_ally_go':'{0} 個援軍加入 {1} 秒！',
   'lockTitle':'完整版',
   'lockSub':'第 {0} 關之後屬於完整版內容。',
   'lockBody':'免費版有 {0} 關。解鎖全部 {1} 關——一次買斷、沒有廣告、沒有轉蛋，永久擁有。',
   'lockCta':'取得完整版',
   'lockLater':'繼續玩免費關卡',
   'lockTag':'未解鎖',
   'lockDemoEnd':'免費關卡到這裡結束！',
   'unlocked':'完整版已解鎖——全部 {0} 關！',
 },
 'zh-Hans': {
   'c_ally_n':'糖果援军',
   'c_ally_go':'{0} 个援军加入 {1} 秒！',
   'lockTitle':'完整版',
   'lockSub':'第 {0} 关之后属于完整版内容。',
   'lockBody':'免费版有 {0} 关。解锁全部 {1} 关——一次买断、没有广告、没有扭蛋，永久拥有。',
   'lockCta':'获取完整版',
   'lockLater':'继续玩免费关卡',
   'lockTag':'未解锁',
   'lockDemoEnd':'免费关卡到这里结束！',
   'unlocked':'完整版已解锁——全部 {0} 关！',
 },
 'ja': {
   'c_ally_n':'キャンディ仲間',
   'c_ally_go':'仲間{0}体が{1}秒間参戦！',
   'lockTitle':'製品版',
   'lockSub':'ステージ{0}以降は製品版の内容です。',
   'lockBody':'無料版は{0}ステージまで。全{1}ステージを解放——買い切り、広告なし、ガチャなし、ずっとあなたのものです。',
   'lockCta':'製品版を入手',
   'lockLater':'無料ステージを続ける',
   'lockTag':'ロック中',
   'lockDemoEnd':'無料ステージはここまでです！',
   'unlocked':'製品版を解放——全{0}ステージ！',
 },
 'ko': {
   'c_ally_n':'캔디 동료',
   'c_ally_go':'동료 {0}명이 {1}초간 합류!',
   'lockTitle':'정식판',
   'lockSub':'{0}단계부터는 정식판 콘텐츠입니다.',
   'lockBody':'무료판은 {0}단계까지입니다. 전체 {1}단계 잠금 해제 — 한 번 구매, 광고 없음, 뽑기 없음, 영구 소장.',
   'lockCta':'정식판 구매',
   'lockLater':'무료 단계 계속하기',
   'lockTag':'잠김',
   'lockDemoEnd':'무료 단계는 여기까지입니다!',
   'unlocked':'정식판 잠금 해제 — 전체 {0}단계!',
 },
 'de': {
   'c_ally_n':'Bonbon-Kameraden',
   'c_ally_go':'{0} Kameraden für {1}s dabei!',
   'lockTitle':'Vollversion',
   'lockSub':'Level {0} und weiter gehören zur Vollversion.',
   'lockBody':'Du hast {0} Gratis-Level. Schalte alle {1} Level frei — einmal kaufen, keine Werbung, keine Lootboxen, für immer deins.',
   'lockCta':'Vollversion holen',
   'lockLater':'Gratis weiterspielen',
   'lockTag':'GESPERRT',
   'lockDemoEnd':'Das war das letzte Gratis-Level!',
   'unlocked':'Vollversion freigeschaltet — alle {0} Level!',
 },
 'fr': {
   'c_ally_n':'Camarades bonbons',
   'c_ally_go':'{0} camarades pour {1}s !',
   'lockTitle':'Version complète',
   'lockSub':'Le niveau {0} et les suivants font partie de la version complète.',
   'lockBody':'Tu as {0} niveaux gratuits. Débloque les {1} niveaux — un seul achat, sans pub, sans coffres aléatoires, à toi pour toujours.',
   'lockCta':'Obtenir la version complète',
   'lockLater':'Continuer en gratuit',
   'lockTag':'VERROUILLÉ',
   'lockDemoEnd':'C’est la fin des niveaux gratuits !',
   'unlocked':'Version complète débloquée — les {0} niveaux !',
 },
 'es': {
   'c_ally_n':'Camaradas de caramelo',
   'c_ally_go':'¡{0} camaradas durante {1}s!',
   'lockTitle':'Juego completo',
   'lockSub':'La fase {0} en adelante es parte del juego completo.',
   'lockBody':'Tienes {0} fases gratis. Desbloquea las {1} fases: una sola compra, sin anuncios, sin cajas de botín, tuyo para siempre.',
   'lockCta':'Conseguir el juego completo',
   'lockLater':'Seguir jugando gratis',
   'lockTag':'BLOQUEADO',
   'lockDemoEnd':'¡Aquí acaban las fases gratuitas!',
   'unlocked':'Juego completo desbloqueado: ¡las {0} fases!',
 },
 'it': {
   'c_ally_n':'Compagni caramella',
   'c_ally_go':'{0} compagni per {1}s!',
   'lockTitle':'Gioco completo',
   'lockSub':'Il livello {0} e successivi fanno parte del gioco completo.',
   'lockBody':'Hai {0} livelli gratuiti. Sblocca tutti i {1} livelli: un solo acquisto, niente pubblicità, niente casse premio, tuo per sempre.',
   'lockCta':'Ottieni il gioco completo',
   'lockLater':'Continua gratis',
   'lockTag':'BLOCCATO',
   'lockDemoEnd':'Qui finiscono i livelli gratuiti!',
   'unlocked':'Gioco completo sbloccato: tutti i {0} livelli!',
 },
 'pt-BR': {
   'c_ally_n':'Camaradas de doce',
   'c_ally_go':'{0} camaradas por {1}s!',
   'lockTitle':'Jogo completo',
   'lockSub':'A fase {0} em diante faz parte do jogo completo.',
   'lockBody':'Você tem {0} fases grátis. Desbloqueie as {1} fases — uma compra só, sem anúncios, sem caixas aleatórias, seu para sempre.',
   'lockCta':'Obter o jogo completo',
   'lockLater':'Continuar de graça',
   'lockTag':'BLOQUEADO',
   'lockDemoEnd':'Aqui terminam as fases grátis!',
   'unlocked':'Jogo completo desbloqueado — todas as {0} fases!',
 },
 'ru': {
   'c_ally_n':'Конфетные союзники',
   'c_ally_go':'{0} союзника на {1} с!',
   'lockTitle':'Полная версия',
   'lockSub':'Уровень {0} и далее входят в полную версию.',
   'lockBody':'У вас {0} бесплатных уровней. Откройте все {1} — одна покупка, без рекламы, без лутбоксов, навсегда ваше.',
   'lockCta':'Купить полную версию',
   'lockLater':'Играть бесплатно дальше',
   'lockTag':'ЗАКРЫТО',
   'lockDemoEnd':'Бесплатные уровни закончились!',
   'unlocked':'Полная версия открыта — все {0} уровней!',
 },
}

assert set(NEW) == set(L), f"語言不齊：多 {set(NEW)-set(L)} 少 {set(L)-set(NEW)}"
KEYS = sorted(NEW['en'])
for c in L:
    assert sorted(NEW[c]) == KEYS, f"[{c}] key 不齊"
    for k, v in NEW[c].items():
        assert k not in L[c], f"[{c}] {k} 已存在，不要重複加"
        L[c][k] = v

lines[li[0]] = 'const L10N=' + json.dumps(L, ensure_ascii=False) + ';'
io.open(P, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"已加入 {len(KEYS)} 個 key × {len(L)} 種語言：{', '.join(KEYS)}")
print(f"每種語言現在有 {len(L['en'])} 個 key")
