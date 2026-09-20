"""Build limits keep decisions meaningful and full builds cannot manufacture XP."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':320,'height':568})
 c.add_init_script('window.requestAnimationFrame=()=>0');p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))});p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 starts=p.evaluate('''()=>{const rows=[];for(const secondary of ['graffiti','yoyo'])for(let i=0;i<50;i++){SECONDARY_WEAPON=secondary;META={wep:3};LV_IDX=i;start();const rank=Math.max((CUR().startWep||{}).graffiti||0,(CUR().startWep||{}).yoyo||0);rows.push({stage:i+1,weapons:Object.values(G.P.wep).filter(v=>v>0).length,rank,secondary:G.P.wep[secondary],main:G.P.wep.bubble,expectedMain:Math.min(5,((CUR().startWep||{}).bubble||1)+3)});}SECONDARY_WEAPON='graffiti';return rows;}''')
 assert all(x['weapons']<=2 and x['rank']==x['secondary'] and x['main']==x['expectedMain'] for x in starts),starts
 result=p.evaluate('''()=>{
  const rows=[];
  for(let run=0;run<40;run++){
   META={};LV_IDX=8;start();const P=G.P;let choices=0;
   while(choices<60){const list=rollCards();if(!list.length)break;applyCard(list[(run+choices)%list.length]);choices++;}
   const counts=buildCounts(P);rows.push({...counts,choices,empty:rollCards().length===0});
  }
  const P=G.P,before={coins:COINS,hearts:P.hearts,xp:P.xp,gems:G.GEM.length};
  P.hearts=1;queueCards(3);const after={coins:COINS,hearts:P.hearts,xp:P.xp,gems:G.GEM.length,paused:G.paused,pending:G.pendingCards};
  const missing=UPGRADES.find(u=>!u.w&&!P[u.id]);applyCard(missing);const staleBlocked=!P[missing.id];
  const missingWeapon=UPGRADES.find(u=>u.w&&!P.wep[u.w]);applyCard(missingWeapon);const thirdWeaponBlocked=!P.wep[missingWeapon.w];
  const countBefore=JSON.stringify(buildCounts(P));for(const chest of CHEST_TYPES)chest.go(P);const chestsKeepSlots=countBefore===JSON.stringify(buildCounts(P));
  return {rows,before,after,staleBlocked,thirdWeaponBlocked,chestsKeepSlots};
 }''')
 assert all(r['weapons']==2 and r['skills']==4 and r['empty'] and r['choices']<60 for r in result['rows']),result
 before,after=result['before'],result['after']
 assert after['coins']==before['coins']+6 and after['hearts']==1 and after['xp']==before['xp'] and after['gems']==before['gems'] and not after['paused'] and after['pending']==0,result
 assert result['staleBlocked'] and result['thirdWeaponBlocked'] and result['chestsKeepSlots'],result
 for width,height in [(320,568),(568,320)]:
  p.set_viewport_size({'width':width,'height':height})
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('lang=>{applyLanguage(lang);start();queueCards(2);}',lang)
   assert p.locator('.buildSlots').evaluate('e=>e.textContent.length>5&&e.scrollWidth<=e.clientWidth+1'),(width,lang)
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");showMenu();PROGRESS=50;SEL_IDX=49;renderStage()');p.locator('#startingWeapon').select_option('yoyo');p.screenshot(path=str(ARTIFACTS/'build63-loadout.png'));p.locator('#btnPlay').click()
 assert p.evaluate('G.P.wep.yoyo===5&&G.P.wep.graffiti===0')
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");start();queueCards(1)')
 p.screenshot(path=str(ARTIFACTS/'build63-cards.png'));assert not errors,errors
 (ARTIFACTS/'build63.json').write_text(json.dumps(result,indent=2));b.close()
print('PASS 40 complete builds, 2 weapons/4 skills, stale selections, 11 locales and no full-pool XP/healing loop')
