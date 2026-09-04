# -*- coding: utf-8 -*-
"""把 i18n/keys_*.py 的翻譯注入 index.html，並把遊戲改成多語系架構。
   每一處取代都用 assert 確認真的有改到，避免靜默失敗。"""
import json, sys, re
sys.path.insert(0,'/home/claude/work/goo-blaster/i18n')
from keys_en import EN
from keys_zh import ZH_HANT, ZH_HANS
from keys_jako import JA, KO
from keys_eu1 import DE, FR
from keys_eu2 import ES, IT
from keys_eu3 import PT_BR, RU

LANGS=[("en","English",EN),("zh-Hant","繁體中文",ZH_HANT),("zh-Hans","简体中文",ZH_HANS),
       ("ja","日本語",JA),("ko","한국어",KO),("de","Deutsch",DE),("fr","Français",FR),
       ("es","Español",ES),("it","Italiano",IT),("pt-BR","Português (BR)",PT_BR),("ru","Русский",RU)]

# 一致性檢查：所有語言的 key 必須跟英文完全相同
for code,_,d in LANGS:
    miss=set(EN)-set(d); extra=set(d)-set(EN)
    assert not miss and not extra, f"{code} key 不一致 缺{miss} 多{extra}"

l10n={code:d for code,_,d in LANGS}
langlist=[{"c":c,"n":n} for c,n,_ in LANGS]

engine = """
//====================== 多語系（v0.9.19）======================
// 預設英文。原本 289 條中文字串全部抽成 key，翻譯放在 L10N 表裡。
// 設計重點：
//  ① 資料表（武器/升級卡/關卡/Boss/寶箱…）的顯示欄位在 applyLanguage() 時「就地改寫」，
//     所有既有的顯示程式碼（讀 .name / .n / .d）完全不用改，風險最低。
//  ② 難度層級 L.tier 從中文字串改成「數字索引」，因為它同時是 TIER_COLOR 的查表鍵——
//     如果翻譯了字串，查表就會壞掉。顏色用陣列、顯示名稱另外走 T('tier'+i)。
//  ③ 語言偵測順序：存檔裡玩家選過的 > 瀏覽器語言 > 英文。
const LANGS=__LANGLIST__;
const L10N=__L10N__;
let LANG='en';
function T(k){
  const s=(L10N[LANG]&&L10N[LANG][k])!==undefined?L10N[LANG][k]:(L10N.en[k]!==undefined?L10N.en[k]:k);
  if(arguments.length<2) return s;
  const a=arguments;
  return String(s).replace(/\\{(\\d+)\\}/g,(m,i)=>{ const v=a[+i+1]; return v===undefined?m:v; });
}
// 瀏覽器語言 → 我們支援的語言代碼。zh 要細分繁簡（TW/HK/MO/Hant 走繁體，其餘走簡體）。
function detectLang(){
  const list=(navigator.languages&&navigator.languages.length)?navigator.languages:[navigator.language||'en'];
  for(const raw of list){
    if(!raw) continue;
    const t=String(raw); const low=t.toLowerCase();
    if(low.startsWith('zh')){
      if(/hant|tw|hk|mo/.test(low)) return 'zh-Hant';
      return 'zh-Hans';
    }
    if(low.startsWith('pt')) return 'pt-BR';
    const base=low.split('-')[0];
    const hit=LANGS.find(l=>l.c.toLowerCase()===low)||LANGS.find(l=>l.c.toLowerCase().split('-')[0]===base);
    if(hit) return hit.c;
  }
  return 'en';
}
"""
engine = engine.replace("__LANGLIST__", json.dumps(langlist, ensure_ascii=False))
engine = engine.replace("__L10N__", json.dumps(l10n, ensure_ascii=False))

p='/home/claude/work/goo-blaster/index.html'
s=open(p,encoding='utf-8').read()
orig=s
def rep(old,new,cnt=1,tag=""):
    global s
    assert s.count(old)>=cnt, f"找不到要取代的內容({tag}): {old[:80]!r}"
    s=s.replace(old,new,cnt)

# 1) 插入引擎（放在 BUILD 之後）
rep("const BUILD='v0.9.18';", "const BUILD='v0.9.19';"+engine, 1, "engine")

open(p,'w',encoding='utf-8').write(s)
print("引擎注入完成，檔案行數:", s.count('\n')+1)
print("語言數:", len(LANGS), "每語言 key 數:", len(EN))
