"""Spatial garden wishes: real UI, boundaries, old saves, backup and locale fit."""
import json, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT, ARTIFACTS, BROWSER_CHANNEL
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},has_touch=True);c.set_offline(True);c.add_init_script('window.requestAnimationFrame=()=>0')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_UI_CPU','1'))});p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 p.locator('#navGarden').click();p.locator('#gardenArrange').click();p.locator('.gardenTool').nth(4).click();p.locator('.gardenTile').nth(9).click()
 assert p.locator('#gardenWelcome').is_enabled();p.locator('#gardenWelcome').click();assert p.locator('#gardenWelcome').is_disabled();assert p.locator('.resident.home').count()==1
 result=p.evaluate('''()=>{
 const a=(pairs)=>{const x=Array(16).fill(0);for(const [i,t] of pairs)x[i]=t;return x;};
 const cases=[[[5,4],[4,2],[6,2]],[[5,3],[1,1],[6,1]],[[0,5],[1,5],[2,5],[3,5]],[[5,4],[7,4],[1,2],[6,2],[11,2]],[[0,1],[3,1],[12,1],[15,1],[5,3]],[[0,1],[1,2],[2,3],[3,4],[7,5]]];
 const solved=cases.map((x,w)=>gardenWishMet(w,a(x)));
 const negatives=[!gardenWishMet(0,a([[5,4],[0,2],[10,2]])),!gardenWishMet(1,a([[5,3],[0,1],[10,1]])),!gardenWishMet(2,a([[0,5],[1,5],[6,5],[7,5]])),!gardenWishMet(2,a([[0,5],[1,5],[4,5],[5,5]])),!gardenWishMet(5,a([[0,1],[1,2],[2,3],[3,4],[15,5]]))];
 GARDEN=cleanGarden({layout:Array(16).fill(0),seeds:22,petals:31,house:2,plots:[{crop:1,growth:1}]});const original=[GARDEN.seeds,GARDEN.petals,GARDEN.house,JSON.stringify(GARDEN.plots)];
 GARDEN_TOOL=3;gardenPlace(0);gardenPlace(1);const limited=!gardenPlace(2);GARDEN_TOOL=0;gardenPlace(0);GARDEN_TOOL=3;const reuse=gardenPlace(2);const invalid=!gardenPlace(-1)&&!gardenPlace(16)&&!gardenPlace(1.1)&&!gardenWelcome(-1)&&!gardenWelcome(6);
 PROGRESS=1;GARDEN.layout=a(cases[1]);const locked=!gardenWelcome(1);PROGRESS=3;const unlocked=gardenWelcome(1),once=!gardenWelcome(1);GARDEN_TOOL=0;gardenPlace(5);const stays=GARDEN.guests.includes(1);
 PROGRESS=50;for(let w=5;w>=0;w--){GARDEN.layout=a(cases[w]);gardenWelcome(w);}
 const guests=GARDEN.guests.join(',')==='0,1,2,3,4,5';const preserved=JSON.stringify(original)===JSON.stringify([GARDEN.seeds,GARDEN.petals,GARDEN.house,JSON.stringify(GARDEN.plots)]);
 const snapshot=JSON.stringify(GARDEN),code=saveCodeEncode();GARDEN=cleanGarden();importSaveCode(code);const backup=JSON.stringify(GARDEN)===snapshot;saveGame();
 const sanitized=cleanGarden({layout:[-1,99,1.5,...Array(20).fill(3)],guests:[-1,0,0,2,99,1.5]});const clean=sanitized.layout.length===16&&sanitized.layout.filter(t=>t===3).length===2&&sanitized.guests.join(',')==='0,2';
 return {solved,negatives,limited,reuse,invalid,locked,unlocked,once,stays,guests,preserved,backup,clean,snapshot};
 }''')
 assert all(result['solved']) and all(result['negatives']),result
 for k in ['limited','reuse','invalid','locked','unlocked','once','stays','guests','preserved','backup','clean']:assert result[k],(k,result)
 p.reload();assert p.evaluate('JSON.stringify(GARDEN)')==result['snapshot']
 for w,h in [(320,568),(390,844),(844,390)]:
  p.set_viewport_size({'width':w,'height':h})
  for lang in p.evaluate('Object.keys(L10N)'):
   p.evaluate('lang=>{applyLanguage(lang);setHubPage("garden");}',lang)
   if not p.locator('.gardenTile').first.is_visible():p.locator('#gardenArrange').click()
   assert p.locator('#garden').evaluate('e=>e.scrollWidth<=e.clientWidth+1'),(w,lang)
   assert p.locator('.gardenTile').count()==16 and p.locator('.gardenTool').count()==6
   assert p.locator('.gardenTile').first.bounding_box()['width']>=44,(w,h,lang,p.locator('.gardenTile').first.bounding_box(),p.locator('#gardenWorkshop').get_attribute('open'))
   p.locator('.gardenTile').last.scroll_into_view_if_needed()
  toolbar=p.locator('.gardenTools').bounding_box()
  assert toolbar['y']>=0 and toolbar['y']+toolbar['height']<=h-60,(w,h,toolbar)
 p.set_viewport_size({'width':390,'height':844});p.evaluate('applyLanguage("zh-Hant");GARDEN_WISH=5;renderGarden();document.querySelector("#garden").scrollTop=0')
 p.screenshot(path=str(ARTIFACTS/'garden65.png'));p.locator('.gardenWishStatus').scroll_into_view_if_needed();p.screenshot(path=str(ARTIFACTS/'garden65-wish.png'))
 payload=p.evaluate('localStorage.getItem(PROG_KEY)')
 native=b.new_context();native.add_init_script('window.requestAnimationFrame=()=>0;window.__saved='+json.dumps(payload)+';window.Capacitor={getPlatform:()=>"android",Plugins:{Preferences:{get:async()=>({value:window.__saved}),set:async()=>{}}}};')
 q=native.new_page();q.goto((Path(GAME_ROOT)/'index.html').as_uri());q.wait_for_function('NATIVE_READY');assert q.evaluate('JSON.stringify(GARDEN)')==result['snapshot'];native.close()
 assert not errors,errors
 (ARTIFACTS/'garden65.json').write_text(json.dumps(result,indent=2),encoding='utf-8');b.close()
print('PASS garden design UI; 6 wishes; diagonal/disconnected/cycle rejection; limits; persistent guests; old resources; backup/reload; 33 layouts offline')
