# -*- coding: utf-8 -*-
"""v0.9.33：🍬 軟糖再生（regen）加上「整關回血次數上限」，卡片描述 11 語言同步。

背景：使用者 2026-09-05 第一次在真機（Android App）試玩後回報「吃到這個道具
就延續一整局都有回覆效果，那就有點無敵狀態了」。他當下講的是 🩹 急救棒棒糖，
查證後發現那張卡（panic）根本不回血、只是受傷後 3 秒移速 +75%——**真正無限
回血的是 🍬 軟糖再生**。直覺抓對了問題，只是抓錯卡片。

實際數字（v0.9.32 之前）：
  愛心上限固定 3 顆；中後期關卡長 140~240 秒
  Lv.1 每 40 秒回一顆 → 一關白拿 3~6 顆
  Lv.2 每 25 秒回一顆 → 一關白拿 5~9 顆（= 3 顆心的實際血量翻 2~3 倍）

v0.9.33 加上上限：Lv.1 最多 2 顆、Lv.2 最多 4 顆（每一關重新計算）。
即使砍到 2 顆，對一個「上限只有 3 顆心」的角色來說仍然接近多一條命，
這張卡不會變成廢卡，只是不再是無限。

這支只改**既有 key** `u_regen_d` / `u_regen_d2` 的文字，不新增 key、
不動任何其他語系內容。一次改完 11 種語言，遵守長期指令 D。
"""
import json, io

P = '/home/claude/work/goo-blaster/index.html'
s = io.open(P, encoding='utf-8').read()
lines = s.split('\n')
li = [i for i, l in enumerate(lines) if l.startswith('const L10N=')]
assert len(li) == 1, f"找不到唯一的 L10N（{len(li)} 個）"
L = json.loads(lines[li[0]][len('const L10N='):].rstrip(';'))

BEFORE_KEYS = len(L['en'])

# Lv.1：每 40 秒回一顆，整關最多 2 顆
NEW_D = {
 'en':      'Restore one heart every 40s, up to 2 per stage',
 'zh-Hant': '每 40 秒回復一顆愛心，每關最多 2 顆',
 'zh-Hans': '每 40 秒回复一颗爱心，每关最多 2 颗',
 'ja':      '40秒ごとにハートを1つ回復（1ステージ最大2つ）',
 'ko':      '40초마다 하트 1개 회복 (스테이지당 최대 2개)',
 'de':      'Alle 40s ein Herz zurück, max. 2 pro Level',
 'fr':      'Un cœur toutes les 40s, 2 max par niveau',
 'es':      'Un corazón cada 40s, máx. 2 por fase',
 'it':      'Un cuore ogni 40s, max 2 per livello',
 'pt-BR':   'Um coração a cada 40s, até 2 por fase',
 'ru':      'Сердце каждые 40 с, до 2 за уровень',
}

# Lv.2：改成每 25 秒，上限提高到 4 顆
NEW_D2 = {
 'en':      'Every 25s instead, up to 4 per stage',
 'zh-Hant': '改為每 25 秒一顆，上限提高到 4 顆',
 'zh-Hans': '改为每 25 秒一颗，上限提高到 4 颗',
 'ja':      '25秒ごとに変更（最大4つ）',
 'ko':      '25초마다로 변경 (최대 4개)',
 'de':      'Stattdessen alle 25s, max. 4',
 'fr':      'Toutes les 25s, 4 max',
 'es':      'Cada 25s, máx. 4',
 'it':      'Ogni 25s, max 4',
 'pt-BR':   'A cada 25s, até 4',
 'ru':      'Каждые 25 с, до 4',
}

for name, NEW in (('u_regen_d', NEW_D), ('u_regen_d2', NEW_D2)):
    assert set(NEW) == set(L), f"{name} 語言不齊：多 {set(NEW)-set(L)} 少 {set(L)-set(NEW)}"
    print(f'── {name} ' + '─' * 40)
    for c in L:
        assert name in L[c], f"[{c}] {name} 不存在，這支腳本是改既有 key 不是加新的"
        old = L[c][name]
        L[c][name] = NEW[c]
        print(f'  [{c:8s}] {old!r}\n             -> {NEW[c]!r}')

for c in L:
    assert len(L[c]) == BEFORE_KEYS, f"[{c}] key 數變了（{len(L[c])} != {BEFORE_KEYS}）"

lines[li[0]] = 'const L10N=' + json.dumps(L, ensure_ascii=False) + ';'
io.open(P, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"\n✅ 已修改 u_regen_d / u_regen_d2 × {len(L)} 種語言；key 數維持 {BEFORE_KEYS}")
