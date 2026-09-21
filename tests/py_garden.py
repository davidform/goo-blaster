"""Garden lifecycle, legacy/native/backup persistence, and phone UI."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},has_touch=True)
 c.add_init_script('window.requestAnimationFrame=()=>0');c.set_offline(True);p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))});p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 assert p.evaluate('GARDEN.seeds===3&&GARDEN.house===0&&GARDEN.plots.every(x=>x===null)')
 p.locator('#navGarden').click();p.locator('.gardenSpot[data-kind=plot]').first.click();p.locator('.gardenPlot button').first.click()
 assert p.evaluate('GARDEN.seeds===2&&GARDEN.plots[0].crop===0')
 result=p.evaluate('''()=>{
  const old={progress:3,coins:99,meta:{dmg:2},lang:'en',v:2};applySaveObject(old);
  const oldSafe=PROGRESS===3&&COINS===99&&META.dmg===2&&GARDEN.seeds===3;
  const combat=()=>{const g=newGame();applyMeta(g);return JSON.stringify([g.P.dmg,g.P.atkSpd,g.P.dashCDmax,g.P.maxHearts]);};
  const stats=combat();gardenPlant(0,0);const blocked= !gardenPlant(0,0)&&!gardenPlant(1,2)&&!gardenPlant(-1,0)&&!gardenHarvest(8)&&!gardenUpgrade();
  LV_IDX=0;start();endGame(false);const failKeeps=GARDEN.plots[0].growth===0;
  start();endGame(true);const once=JSON.stringify(GARDEN);endGame(true);const onceOnly=JSON.stringify(GARDEN)===once;
  const first= gardenHarvest(0),twice=!gardenHarvest(0),firstPetals=GARDEN.petals;
  GARDEN.petals=200;const upgrades=[gardenUpgrade(),gardenUpgrade(),gardenUpgrade(),!gardenUpgrade()];
  gardenPlant(0,0);gardenPlant(1,1);gardenPlant(2,2);
  for(let k=0;k<3;k++){start();endGame(true);}
  const allReady=GARDEN.plots.every(x=>x.growth===GARDEN_CROPS[x.crop].days);
  const petals=GARDEN.petals;for(let i=0;i<3;i++)gardenHarvest(i);const harvestYield=GARDEN.petals-petals;
  const stableStats=stats===combat();const garden=JSON.stringify(GARDEN),code=saveCodeEncode();
  GARDEN=cleanGarden();importSaveCode(code);const backup=JSON.stringify(GARDEN)===garden;
  const newer=cleanGarden(GARDEN);newer.rev+=10;newer.petals=47;
  const merged=pickBetterSave({progress:10,coins:200,v:2,garden:GARDEN},{progress:2,coins:5,v:2,garden:newer});
  const merge=merged.progress===10&&merged.garden.petals===47;
  const clean=cleanGarden({seeds:-3,petals:Infinity,house:90,plots:[{crop:-1,growth:8},{crop:1,growth:99},{crop:2,growth:-5}]});
  const sanitized=clean.seeds===0&&clean.petals===0&&clean.house===3&&clean.plots[0]===null&&clean.plots[1].growth===2&&clean.plots[2].growth===0;
  const retained=GARDEN;GARDEN=cleanGarden({seeds:0,petals:0,house:0});
  const zero=!gardenPlant(0,0)&&!gardenUpgrade()&&GARDEN.seeds===0;
  GARDEN=cleanGarden({seeds:999,petals:999999,house:3,plots:[{crop:2,growth:3}]});
  const cap=gardenClear()===0&&gardenHarvest(0)&&GARDEN.seeds===999&&GARDEN.petals===999999;
  GARDEN=retained;
  saveGame();return {oldSafe,blocked,failKeeps,onceOnly,first,twice,firstPetals,upgrades,allReady,harvestYield,stableStats,backup,merge,sanitized,zero,cap,garden};
 }''')
 for key in ['oldSafe','blocked','failKeeps','onceOnly','first','twice','allReady','stableStats','backup','merge','sanitized','zero','cap']:assert result[key],(key,result)
 assert result['firstPetals']==1 and result['harvestYield']==10 and all(result['upgrades']),result
 p.reload();assert p.evaluate('JSON.stringify(GARDEN)')==result['garden']
 payload=p.evaluate('localStorage.getItem(PROG_KEY)')
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('lang=>{applyLanguage(lang);showMenu();setHubPage("garden");}',lang)
   assert p.locator('#garden').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(w,lang)
   assert p.locator('#hubNav [aria-current="page"]').count()==1
   assert p.locator('#garden select').count()==3
   p.locator('.gardenSpot[data-kind=plot]').last.click();p.locator('.gardenPlot button').last.scroll_into_view_if_needed();assert p.locator('.gardenPlot button').last.is_visible()
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");gardenPlant(0,0);gardenPlant(1,1);setHubPage("garden");document.querySelector("#garden").scrollTop=0')
 p.screenshot(path=str(ARTIFACTS/'garden64.png'))
 p.locator('#navAdventure').click();p.locator('#btnPlay').click();assert p.locator('#garden').is_hidden()
 p.evaluate('endGame(true)');p.locator('#btnGarden').scroll_into_view_if_needed();p.locator('#btnGarden').click()
 assert p.locator('#garden').is_visible() and p.locator('#over').is_hidden()

 c.close()
 native=b.new_context();native.add_init_script('''window.requestAnimationFrame=()=>0;window.__native={};window.Capacitor={getPlatform:()=>"android",Plugins:{Preferences:{get:async({key})=>({value:window.__native[key]||null}),set:async({key,value})=>{window.__native[key]=value;}}}};''')
 native.add_init_script('window.__native["gooblaster_save_v3"]='+json.dumps(payload))
 q=native.new_page();q.goto((Path(GAME_ROOT)/'index.html').as_uri());q.wait_for_function('NATIVE_READY')
 assert q.evaluate('JSON.stringify(GARDEN)')==result['garden']
 assert not errors,errors;b.close();(ARTIFACTS/'garden64.json').write_text(json.dumps(result,indent=2))
print('PASS garden lifecycle, single settlement, old save/native/backup, unchanged combat and 33 locale/viewports offline')
