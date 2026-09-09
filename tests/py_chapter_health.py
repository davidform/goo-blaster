"""Actual Boss spawns plus a pinned v54 A/B of all 50 schedules."""
import sys,json,subprocess,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from test_paths import GAME_ROOT,ARTIFACTS,BROWSER_CHANNEL,REPO
from playwright.sync_api import sync_playwright
# Filled with the exact v54 commit when this test is promoted after its full suite.
BASE_COMMIT='e14d846e1bc53f2cdaa7fc88430abe2f72415366'
if BASE_COMMIT=='V54_COMMIT':baseline=REPO/'index.html'
else:
 baseline=ARTIFACTS/'chapter-health-v54.html'
 baseline.write_bytes(subprocess.check_output(['git','show',BASE_COMMIT+':index.html'],cwd=REPO))
with sync_playwright() as pw:
 b=pw.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844});c.add_init_script('window.requestAnimationFrame=()=>0')
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
 c.new_cdp_session(p).send('Emulation.setCPUThrottlingRate',{'rate':int(os.getenv('GOO_HEALTH_CPU','1'))})
 p.goto(baseline.resolve().as_uri());old=p.evaluate('LEVELS.map(L=>buildBosses(L))')
 p.goto((Path(GAME_ROOT)/'index.html').as_uri());new=p.evaluate('LEVELS.map(L=>buildBosses(L))')
 assert old[:10]==new[:10],'First ten stages changed'
 expected=[23296,80240,82246,84252,86258,88264,90270,92276,94282,96288]
 actual=[];changed=[]
 for lv,(a,z) in enumerate(zip(old,new),1):
  assert len(a)==len(z)
  for before,after in zip(a,z):
   if after.get('superBoss'):
    actual.append(after['hp'])
    if lv>10:
     changed.append(lv);before=dict(before);before['hp']=after['hp']
   assert before==after,(lv,before,after)
 assert actual==expected,(actual,expected)
 assert changed==[15,20,25,30,35,40,45,50],changed
 assert all(x<y for x,y in zip(actual,actual[1:])),actual
 spawn=[]
 for lv,hp in zip(range(5,51,5),expected):
  r=p.evaluate('''lv=>{LV_IDX=lv-1;META={};start();spawnBoss(buildBosses(CUR()).find(b=>b.superBoss));const e=G.boss;return {hp:e.hp,maxhp:e.maxhp,ch:e.chIdx,kind:e.kind};}''',lv)
  assert r=={'hp':hp,'maxhp':hp,'ch':lv//5-1,'kind':'final'},r
  spawn.append(r)
 # Actual damage/armor/end path uses the new HP, not a stale displayed number.
 end=p.evaluate('''()=>{LV_IDX=49;start();G.P.crit=0;G.P.wep={bubble:0,graffiti:0,yoyo:0};spawnBoss(buildBosses(CUR()).find(b=>b.superBoss));const e=G.boss;hurtEnemy(e,e.maxhp*.51,false);const broken=e.armorBroken;hurtEnemy(e,e.hp+1,false);return {broken,win:G.win,over:G.over,running:G.running};}''')
 assert end=={'broken':True,'win':True,'over':True,'running':False},end
 assert not errors,errors
 (ARTIFACTS/'chapter-health.json').write_text(json.dumps({'hp':actual,'changed_stages':changed,'spawns':spawn,'end':end,'errors':errors},indent=2),encoding='utf-8')
 b.close()
print('PASS exact late-chapter HP curve and real spawn/armor/win, first ten and every other Boss field unchanged')
