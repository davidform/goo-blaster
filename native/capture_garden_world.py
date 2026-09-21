"""Capture the real v66 scene from an isolated, reachable progression fixture."""
import hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'store/screenshots/v0.9.66'
OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(channel='msedge');c=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2);c.set_offline(True)
 p=c.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.goto((ROOT/'index.html').as_uri())
 p.evaluate('applyLanguage("zh-Hant")');p.locator('#navGarden').click();p.screenshot(path=str(OUT/'village-start-zh.png'))
 p.evaluate('''()=>{PROGRESS=21;GARDEN=cleanGarden({house:2,petals:60,plots:[{crop:0,growth:1},{crop:1,growth:1},{crop:2,growth:3}]});
 const solutions=[[[5,4],[4,2],[6,2]],[[5,3],[1,1],[6,1]],[[0,5],[1,5],[2,5],[3,5]]];
 for(let w=0;w<3;w++){GARDEN_TOOL=0;for(let i=0;i<16;i++)gardenPlace(i);for(const [i,t] of solutions[w]){GARDEN_TOOL=t;gardenPlace(i);}gardenWelcome(w);}
 GARDEN_TOOL=0;for(let i=0;i<16;i++)gardenPlace(i);
 const layout=[1,0,2,0,0,3,0,0,2,0,2,0,0,0,1,0];layout.forEach((t,i)=>{GARDEN_TOOL=t;gardenPlace(i)});GV.selected=null;GV.time=12;renderGarden();document.querySelector('#garden').scrollTop=0;}''')
 for lang,name in [('zh-Hant','village-grown-zh.png'),('en','village-grown-en.png')]:
  p.evaluate('lang=>{applyLanguage(lang);document.getElementById("garden").scrollTop=0}',lang);p.screenshot(path=str(OUT/name))
 manifest={'build':p.evaluate('BUILD'),'source_sha256':hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),'method':'Unretouched browser screenshots; isolated reachable progression fixture, not human gameplay','fixture':{'progress':21,'house':2,'petals':60,'guests':'first three wishes completed via gardenWelcome','plots':'mint ready, berry 1/2, moonflower ready'},'viewport':[390,844],'device_scale_factor':2,'errors':errors,'files':[p.name for p in OUT.glob('*.png')]}
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert not errors;print(json.dumps(manifest,ensure_ascii=False));b.close()
