import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS,GAME_ROOT,BROWSER_CHANNEL
GAME=Path(GAME_ROOT)
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL)
 page=b.new_page(viewport={'width':320,'height':568})
 page.context.new_cdp_session(page).send('Emulation.setCPUThrottlingRate',{'rate':int(os.environ.get('GOO_RANGE_CPU','1'))})
 page.add_init_script('window.requestAnimationFrame=()=>0;')
 page.goto((GAME/'index.html').as_uri());rows=[]
 for lang in page.evaluate('Object.keys(L10N)'):
  row=page.evaluate('''lang=>{
   showMenu();META={range:2};COINS=1000;applyLanguage(lang);showShop();
   const i=META_UPGRADES.findIndex(u=>u.id==='range'),m=META_UPGRADES[i];
   const row=document.querySelectorAll('#shopList .mrow')[i];row.scrollIntoView();
   const desc=row.querySelector('.md');
   return {lang,text:desc.textContent,expected:m.d(2),overflow:desc.scrollWidth>desc.clientWidth+1};
  }''',lang)
  assert row['text']==row['expected'] and '270' in row['text'] and '30%' in row['text'] and '{' not in row['text'] and not row['overflow'],row
  if lang in ['en','zh-Hant']:page.screenshot(path=str(ARTIFACTS/f'range-shop-{lang}.png'))
  maximum=page.evaluate('''()=>{
   META.range=3;renderShop();const i=META_UPGRADES.findIndex(u=>u.id==='range');
   const row=document.querySelectorAll('#shopList .mrow')[i];
   return {disabled:row.querySelector('.mbuy').disabled,text:row.querySelector('.md').textContent};
  }''')
  assert maximum['disabled'] and '270' in maximum['text'] and '30%' in maximum['text'] and '40%' not in maximum['text'],maximum
  for rank in [0,1]:
   card=page.evaluate('''rank=>{
    LV_IDX=0;start();G.P.rangeUp=rank;
    const u=UPGRADES.find(u=>u.id==='rangeUp'),original=rollCards;
    rollCards=()=>Array.from({length:3},()=>({...u,d:rank?u.d2:u.d,stack:rank}));
    showCards();rollCards=original;
    return [...document.querySelectorAll('#cards .ds')].map(e=>({text:e.textContent,overflow:e.scrollWidth>e.clientWidth+1}));
   }''',rank)
   assert len(card)==3 and all(not c['overflow'] and ('30%' if rank else '15%') in c['text'] for c in card),(lang,rank,card)
   if lang in ['en','zh-Hant'] and rank==1:page.screenshot(path=str(ARTIFACTS/f'range-card-{lang}.png'))
  rows.append(row)
 b.close()
(ARTIFACTS/'range-ui.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS 11 languages: actual shop values and both card tiers at 320px')
