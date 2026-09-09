"""Real gem pickups, late rewards, stale taps and cross-run Boss callbacks."""
import os,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL)
 c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_QUEUE_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 p.evaluate("applyLanguage('zh-Hant');META={};LV_IDX=0;start();G.nukeCalm=1e9;G.hasMoved=true;DIAG.touch=3;G.P.iframe=1e9;G.GEM=Array.from({length:34},()=>({x:G.P.x,y:G.P.y,xp:2,vx:0,vy:0,hue:45,r:5,wob:0}));")
 p.wait_for_function('G.GEM.length===0 && G.pendingCards===3')
 result=p.evaluate("({lv:G.P.lv,xp:G.P.xp,total:G.cardTotal,title:cardsEl.querySelector('.lvtitle').textContent})")
 assert result['lv']==4 and result['xp']==17 and result['total']==3,result
 assert '1/3' in result['title'],result
 p.screenshot(path=str(ARTIFACTS/'upgrade-queue-v53.png'))
 seq=[]
 for i in range(3):
  seq.append(p.locator('#cards .lvtitle').inner_text())
  assert f'{i+1}/3' in seq[-1],seq
  p.locator('#cards .card').first.tap()
 assert p.evaluate('G.pendingCards===0 && G.cardTotal===0 && !G.paused')
 # Reward arrives while the second of three choices is already displayed.
 late=p.evaluate('''()=>{start();gainXP(68);document.querySelector('#cards .card').click();const selected=cardsEl.firstChild;queueCards(1);return {pending:G.pendingCards,total:G.cardTotal,title:selected.textContent,same:selected===cardsEl.firstChild};}''')
 assert late['pending']==3 and late['total']==4 and '2/4' in late['title'] and late['same'],late
 # Reusing a detached card event cannot apply a choice twice.
 stale=p.evaluate('''()=>{const e=cardsEl.querySelector('.card'),click=e.onclick;click();const n=G.pendingCards;click();return {before:n,after:G.pendingCards};}''')
 assert stale['before']==stale['after'],stale
 # Many distinct gem calls, not only a synthetic one-shot gainXP(120).
 micro=p.evaluate('''()=>{start();for(let i=0;i<34;i++)gainXP(2);return {lv:G.P.lv,pending:G.pendingCards,total:G.cardTotal};}''')
 assert micro=={'lv':4,'pending':3,'total':3}
 invalid=p.evaluate('''()=>{start();const before=JSON.stringify([G.P.xp,G.P.lv,G.pendingCards]);for(const n of [0,-1,NaN,Infinity,undefined])gainXP(n);return before===JSON.stringify([G.P.xp,G.P.lv,G.pendingCards]);}''')
 assert invalid
 # A delayed reward from a previous run must not become a free choice in a new run.
 p.evaluate('''()=>{LV_IDX=9;start();G.nukeCalm=1e9;spawnBoss(buildBosses(CUR()).find(x=>x.kind!=='final'));killEnemy(G.boss);start();G.nukeCalm=1e9;G.hasMoved=true;G.P.iframe=1e9;window.__settled=false;setTimeout(()=>window.__settled=true,650);}''')
 p.wait_for_function('__settled')
 assert p.evaluate('G.pendingCards===0 && !G.paused && G.P.lv===1')
 # New explanation fits all locales and narrow screens; every card remains reachable.
 for lang in p.evaluate('Object.keys(L10N)'):
  p.set_viewport_size({'width':320,'height':568})
  p.evaluate("lang=>{start();G.nukeCalm=1e9;applyLanguage(lang);gainXP(68);}",lang)
  assert p.locator('.cardQueueHint').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),lang
  for card in p.locator('#cards .card').all():
   card.scroll_into_view_if_needed();assert card.is_visible(),lang
 # Exhausted pool still releases pause and consumes all owed choices.
 empty=p.evaluate('''()=>{start();for(const u of UPGRADES){if(u.w){G.P.wep[u.w]=5;G.P.evo[u.w]=true;}else G.P[u.id]=u.max||1;}gainXP(68);return {pending:G.pendingCards,paused:G.paused};}''')
 assert empty=={'pending':0,'paused':False},empty
 assert not errors,errors
 (ARTIFACTS/'upgrade-queue.json').write_text(json.dumps({'pickup':result,'sequence':seq,'late':late,'stale':stale,'micro':micro,'empty':empty,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
print('PASS actual 34-gem pickup / three choices, late Boss reward totals, no stale taps or cross-run reward, invalid XP, full pool, 11 locales')
