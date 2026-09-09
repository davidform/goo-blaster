"""Real shop prices/purchases, affordable first aid, and retained maxed saves."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL
BASE={'hearts':[60,220],'dmg':[40,90,180,320,520],'aspd':[40,90,180,320,520],'wep':[120,300,650],'range':[70,160,340],'xp':[50,120,260,480],'pickup':[45,110,240],'dash':[55,130,280],'revive':[400,1200],'coin':[80,180,380,700]}
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);p=b.new_page(viewport={'width':390,'height':844})
 p.context.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_SHOP_CPU','1'))})
 p.goto((Path(GAME_ROOT)/'index.html').as_uri())
 prices=p.evaluate('Object.fromEntries(META_UPGRADES.map(u=>[u.id,Array.from({length:u.max},(_,n)=>u.cost(n))]))')
 for name,values in prices.items():
  assert values[:2]==BASE[name][:2],(name,values)
  assert all(x<y for x,y in zip(values,values[1:])),(name,values)
 total=sum(map(sum,prices.values()));assert total>15000 and total<18000,total
 p.evaluate("META={dmg:2};COINS=META_UPGRADES.find(u=>u.id==='dmg').cost(2)-1;saveGame();showShop()")
 # Buy through the actual rendered row, with insufficient and then exact funds.
 index=p.evaluate('META_UPGRADES.findIndex(u=>u.id==="dmg")')
 row=p.locator('#shopList .mrow').nth(index)
 assert row.locator('.mbuy').is_disabled()
 p.evaluate('COINS++;showShop()')
 p.locator('#shopList .mrow').nth(index).locator('.mbuy').click()
 assert p.evaluate('META.dmg===3&&COINS===0')
 p.reload();assert p.evaluate('META.dmg===3&&COINS===0')
 p.evaluate('META=Object.fromEntries(META_UPGRADES.map(u=>[u.id,u.max]));COINS=777;saveGame()')
 p.reload();p.evaluate('showShop()')
 assert p.evaluate('COINS===777&&META_UPGRADES.every(u=>META[u.id]===u.max)')
 assert p.locator('#shopList .mbuy:not([disabled])').count()==0
 evidence=p.evaluate('''()=>{
   const full=JSON.stringify(META);const income=runCoins(true,49,10000,240,240);
   const old=META;META={};const first=runCoins(true,0,40,60,60),fail=runCoins(false,0,0,0,60);META=old;
   return {full,income,first,fail};
 }''')
 assert evidence['income']==520 and evidence['fail']==3
 p.evaluate("applyLanguage('zh-Hant');META={dmg:2};COINS=350;showShop()")
 p.screenshot(path=str(ARTIFACTS/'shop-pacing-v51.png'))
 (ARTIFACTS/'shop-pacing.json').write_text(json.dumps({'old_total':sum(map(sum,BASE.values())),'total':total,'prices':prices,'income':evidence,'minimum_capped_runs':(total+519)//520},ensure_ascii=False,indent=2),encoding='utf-8')
 b.close()
print('PASS early two ranks unchanged; total',total,'; actual underfunded/exact-price tap and reload, maxed save retained, unchanged reward floor/cap')
