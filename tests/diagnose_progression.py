"""Deterministic browser diagnostic, not a human win-rate or FPS benchmark.

Calls the game's actual loop at 60 Hz with drawing suppressed; virtual timers
preserve delayed goo chains. Input uses TouchEvents, cards use their real DOM
handlers. Fixed seeds and repeated replay validate the measuring instrument.
"""
import json,sys,time,os,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import BROWSER_CHANNEL
ROOT=Path(__file__).resolve().parents[1]
INIT=r'''(()=>{
 let now=0,id=0;const jobs=new Map();
 window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};
 window.setTimeout=(fn,ms=0,...args)=>{jobs.set(++id,{fn,args,at:now+ms,interval:0});return id;};
 window.setInterval=(fn,ms=0,...args)=>{jobs.set(++id,{fn,args,at:now+ms,interval:Math.max(1,ms)});return id;};
 window.clearTimeout=window.clearInterval=id=>jobs.delete(id);
 window.__clock={reset(){now=0;jobs.clear();},tick(){now+=1000/60;
   for(const [id,j] of [...jobs])if(j.at<=now){if(j.interval)j.at+=j.interval;else jobs.delete(id);j.fn(...j.args);}return now;}};
})();'''
RUN=r'''([lv,meta,seed,maxSeconds,policy])=>{
 __clock.reset();let rng=seed>>>0;Math.random=()=>{rng^=rng<<13;rng^=rng>>>17;rng^=rng<<5;return (rng>>>0)/4294967296;};
 META=meta;LV_IDX=lv-1;COINS=0;PROGRESS=50;start();if(!SFX.isMuted())SFX.toggle();lastT=0;draw=()=>{};
 const initial={hearts:G.P.hearts,dmg:G.P.dmg,aspd:G.P.atkSpd,wep:{...G.P.wep},revives:G.revives};
 let offered=[],cards=[],hits=[],peakE=0,peakEB=0,totalEB=0,nukes=0;
 const oldRoll=rollCards;rollCards=function(){const a=oldRoll();offered=a;return a;};
 const oldHurt=hurtPlayer;hurtPlayer=function(){const h=G.P.hearts,r=G.revives,s=G.P.shieldN;
   const source=String(new Error().stack).split('\n')[2];
   const nearestEnemy=Math.min(...G.E.map(e=>Math.hypot(e.x-G.P.x,e.y-G.P.y)-e.r-G.P.r));
   const out=oldHurt();if(h!==G.P.hearts||r!==G.revives||s!==G.P.shieldN)hits.push({t:+G.t.toFixed(2),hearts:G.P.hearts,shield:s!==G.P.shieldN,source,nearestEnemy});return out;};
 const oldPush=G.EB.push;G.EB.push=function(...items){totalEB+=items.length;return oldPush.apply(this,items);};
 const cv=document.querySelector('#cv');
 const mk=(id,x,y)=>new Touch({identifier:id,target:cv,clientX:x,clientY:y});
 const fire=(type,t,c)=>cv.dispatchEvent(new TouchEvent(type,{touches:t,changedTouches:c,bubbles:true,cancelable:true}));
 let cur=mk(1,195,500);fire('touchstart',[cur],[cur]);
 let frame=0;
 for(;frame<maxSeconds*60&&!G.over;frame++){
   if(G.paused&&!cardsEl.classList.contains('hide')){
     let pick=0,best=-Infinity;
     offered.forEach((u,i)=>{let score=u.w?(u.evo?100:50+(u.w==='bubble'?8:0)):10;
       if(['shield','regen','panic'].includes(u.id))score=G.P.hearts<=2?90:40;
       if(['chain','split','frenzy'].includes(u.id))score=35;
       if(score>best){best=score;pick=i;}});
     cards.push(offered[pick]?.id||offered[pick]?.w);cardsEl.querySelectorAll('.card')[pick].click();
   }
   if(frame%2===0&&!G.paused){
     const P=G.P;let fx=0,fy=0;
     for(const e of G.E){const dx=P.x-e.x,dy=P.y-e.y,d=Math.hypot(dx,dy)||1;if(d<170){fx+=dx/d/d*700;fy+=dy/d/d*700;}}
     if(policy!=='dumb')for(const e of G.EB){const dx=P.x-e.x-e.vx*.15,dy=P.y-e.y-e.vy*.15,d=Math.hypot(dx,dy)||1;if(d<85){fx+=dx/d/d*350;fy+=dy/d/d*350;}}
     if(['prepared','reactive','planner','engaged'].includes(policy)){
       const danger=Math.hypot(fx,fy);
       if(P.nukeHeld&&(P.hearts<=2||G.EB.filter(b=>Math.hypot(b.x-P.x,b.y-P.y)<180).length>12)){
         window.dispatchEvent(new KeyboardEvent('keydown',{key:'e',bubbles:true}));
         window.dispatchEvent(new KeyboardEvent('keyup',{key:'e',bubbles:true}));nukes++;
       }
       if(danger<2){
         const loot=[...G.CHEST,...(G.NUKE?[G.NUKE]:[]),...G.GEM];
         let target=null,near=350;
         for(const o of loot){const d=Math.hypot(o.x-P.x,o.y-P.y);if(d<near){near=d;target=o;}}
         if(target&&near>1){fx+=(target.x-P.x)/near;fy+=(target.y-P.y)/near;}
       }
     }
     if(policy==='engaged'&&G.boss&&G.E.includes(G.boss)){const e=G.boss,dx=e.x-P.x,dy=e.y-P.y,d=Math.hypot(dx,dy)||1;if(d>Math.max(220,e.r+P.r+90)){fx+=dx/d*2;fy+=dy/d*2;}}
     const cd=Math.hypot(P.x,P.y);if(cd>700){fx-=P.x/cd*5;fy-=P.y/cd*5;}
     let blocked=false;
     if(policy==='planner'&&P.dashT<=0){
       const scale=speedScale(),speed=P.spd*scale*(P.panicT>0?1.75:1)*(P.onGoo?1.45:1);
       const bullets=G.EB.filter(b=>(b.x-P.x)**2+(b.y-P.y)**2<400**2);
       const enemies=G.E.filter(e=>(e.x-P.x)**2+(e.y-P.y)**2<(300+e.r)**2);
       const want=Math.hypot(fx,fy)||1;let best=Infinity,bx=0,by=0;
       for(let a=0;a<24;a++){
         const dx=Math.cos(a*Math.PI/12),dy=Math.sin(a*Math.PI/12);
         let score=.2*(1-dx*IN.dx-dy*IN.dy)-.1*(dx*fx+dy*fy)/want;
         for(const t of [.08,.16,.24,.32]){
           const x=P.x+dx*speed*t,y=P.y+dy*speed*t;
           for(const b of bullets){const d2=(x-b.x-b.vx*scale*t)**2+(y-b.y-b.vy*scale*t)**2;
             score+=d2<(P.r+b.r+8)**2?10000:800/(d2+1);}
           for(const e of enemies){const d2=(x-e.x)**2+(y-e.y)**2;
             score+=d2<(P.r+e.r+20)**2?10000:1200/(d2+1);
             if(e.laserFireT>0||(e.laserWarnT>0&&t*scale>=e.laserWarnT))
               if(raySegDist(e.x,e.y,e.laserAng,1000,x,y)<P.r+36)score+=10000;
           }
           score+=Math.max(0,x*x+y*y-700*700)/1000000;
         }
         if(score<best){best=score;bx=dx;by=dy;}
       }
       fx=bx;fy=by;blocked=best>100;
     }
     if(Math.hypot(fx,fy)<.05){fx=Math.cos(frame*.015);fy=Math.sin(frame*.015);}
     const m=Math.hypot(fx,fy)||1;cur=mk(1,195+fx/m*58,500+fy/m*58);fire('touchmove',[cur],[cur]);
     if((frame%280===0||(['reactive','engaged'].includes(policy)&&Math.hypot(fx,fy)>4)||blocked)&&P.dashCD<=0){const t2=mk(2,BTN.x,BTN.y);fire('touchstart',[cur,t2],[t2]);fire('touchend',[cur],[t2]);}
   }
   loop(__clock.tick());peakE=Math.max(peakE,G.E.length);peakEB=Math.max(peakEB,G.EB.length);
 }
 rollCards=oldRoll;hurtPlayer=oldHurt;endJoy();
 return {lv,seed,policy,meta,initial,status:G.over?(G.win?'clear':'defeat'):'unfinished',win:G.win,over:G.over,t:+G.t.toFixed(2),dur:G.winT,frames:frame,
   remainingBosses:G.E.filter(e=>e.boss).map(e=>({name:e.name,hp:e.hp,maxhp:e.maxhp,x:e.x-G.P.x,y:e.y-G.P.y})),kills:G.kills,plv:G.P.lv,hearts:G.P.hearts,revives:G.revives,nukes,chests:G.chests,coins:runCoins(G.win,G.lvIdx,G.kills,G.t,G.winT),cards,hits,peakE,peakEB,totalEB};
}'''
out=ROOT/'_private/test-artifacts'/os.environ.get('GOO_BALANCE_OUTPUT','progression-'+time.strftime('%Y%m%d-%H%M%S')+'.json')
game_path=Path(os.environ.get('GOO_ROOT',str(ROOT)))/'index.html'
game_sha=hashlib.sha256(game_path.read_bytes()).hexdigest()
tool_sha=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
with sync_playwright() as p:
 b=p.chromium.launch(channel=BROWSER_CHANNEL);c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
 c.add_init_script(INIT);page=c.new_page();page.goto((Path(os.environ.get('GOO_ROOT',str(ROOT)))/'index.html').as_uri())
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 full=page.evaluate('Object.fromEntries(META_UPGRADES.map(u=>[u.id,u.max]))')
 costs=page.evaluate('META_UPGRADES.map(u=>({id:u.id,costs:Array.from({length:u.max},(_,i)=>u.cost(i))}))')
 structure=page.evaluate('LEVELS.map((L,i)=>({lv:i+1,dur:L.dur,hp:L.hp,rate:L.rate,start:L.startWep||{bubble:1},bosses:buildBosses(L).map(b=>({hp:b.hp,atk:b.atk,cooldown:b.atkT,t:b.t})),tier:Math.min(4,Math.floor(i/2))}))')
 # Exact repeated replay: seeds, timers, cards, input and simulation output.
 a=page.evaluate(RUN,[7,{},117,900,os.environ.get('GOO_BOT_POLICY','reactive')]);d=page.evaluate(RUN,[7,{},117,900,os.environ.get('GOO_BOT_POLICY','reactive')]);assert a==d,(a,d)
 results=[]
 levels=[int(n) for n in sys.argv[1:]] or [1,5,6,7,8,9,10,15,30,50]
 # Earned cohort: a single sequential campaign, at most 3 tries per stage.
 # Buy cheapest available combat upgrade after every result, using real runCoins.
 earned={};wallet=0;cohort={};campaign=[]
 for lv in range(1,11):
  cohort[lv]=dict(earned)
  for attempt in range(3):
   row=page.evaluate(RUN,[lv,earned,117+attempt,900,os.environ.get('GOO_BOT_POLICY','reactive')]);assert row['status']!='unfinished',row;wallet+=row['coins'];campaign.append(row)
   while True:
    options=[(u['costs'][earned.get(u['id'],0)],u['id']) for u in costs if u['id']!='coin' and earned.get(u['id'],0)<len(u['costs'])]
    if not options:break
    price,key=min(options)
    if wallet<price:break
    wallet-=price;earned[key]=earned.get(key,0)+1
   if row['win']:break
  if not row['win']:break
 for lv in levels:
  for seed in [117,271,503]:
   for name,meta in [('zero',{}),('earned',cohort.get(lv,earned)),('max',full)]:
    row=page.evaluate(RUN,[lv,meta,seed,900,os.environ.get('GOO_BOT_POLICY','reactive')]);assert row['status']!='unfinished',row;row['cohort']=name;results.append(row)
    out.write_text(json.dumps({'game_sha256':game_sha,'tool_sha256':tool_sha,'replay_identical':True,'structure':structure,'costs':costs,'campaign':campaign,'earned_frontier':max(cohort),'rows':results,'errors':errors},indent=2),encoding='utf-8')
   print(lv,seed,[(r['cohort'],r['win'],r['t'],r['plv']) for r in results[-3:]],flush=True)
 assert game_sha==hashlib.sha256(game_path.read_bytes()).hexdigest(),"Source changed during diagnostic"
 assert not errors,errors
 b.close()
