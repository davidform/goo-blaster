"""Rule text from actual chapters, monster identity, and real translated-menu swipes."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_paths import ARTIFACTS, GAME_ROOT, BROWSER_CHANNEL

with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=BROWSER_CHANNEL)
    context=browser.new_context(viewport={'width':320,'height':480},is_mobile=True,has_touch=True)
    page=context.new_page()
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    cdp=context.new_cdp_session(page)
    rate=int(os.environ.get('GOO_L10N_CPU','1'))
    cdp.send('Emulation.setCPUThrottlingRate',{'rate':rate})
    page.goto((Path(GAME_ROOT)/'index.html').as_uri())
    page.wait_for_function("document.querySelector('#stageInfo .ds').textContent.length>0")
    bounds=page.locator('#menu').evaluate('(e)=>({height:e.clientHeight,content:e.scrollHeight})')
    assert bounds['content']>bounds['height'],bounds
    # Start the gesture on the description, not an already-scrollable map or blank gutter.
    box=page.locator('#stageInfo .ds').bounding_box()
    x=round(box['x']+box['width']/2);y=round(min(box['y']+box['height']/2,385))
    assert page.evaluate('([x,y])=>document.elementFromPoint(x,y).closest("#stageInfo")!==null',[x,y])
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
    for step in range(1,13):
        cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x,'y':y-step*18}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    page.wait_for_function('''()=>document.querySelector('#menu').scrollTop>20 &&
      document.querySelector('#btnPlay').getBoundingClientRect().bottom<=document.querySelector('#hubNav').getBoundingClientRect().top+1''',timeout=15000)
    scroll=page.locator('#menu').evaluate('(e)=>e.scrollTop')
    page.screenshot(path=str(ARTIFACTS/'l10n-small-scroll.png'))
    page.set_viewport_size({'width':390,'height':844})
    stages=page.evaluate('LEVELS.flatMap((L,i)=>buildBosses(L).some(b=>b.superBoss)?[i+1]:[])')
    assert stages==list(range(5,51,5)),stages
    counts=page.evaluate('''()=>{PROGRESS=50;return LEVELS.map((L,i)=>{
      SEL_IDX=i;renderStage();const expected=T('bossCount',buildBosses(L).length);
      return {stage:i+1,expected,shown:document.querySelector('#stageInfo').textContent.includes(expected)};
    });}''')
    assert all(row['shown'] for row in counts),counts
    keys=['b1','b2','b3']+['sb'+str(i) for i in range(10)]
    gel_keys=['hudGoo','w_graffiti_d','e_bubble_n','e_bubble_d','e_graffiti_n','e_graffiti_d','u_chain_d','u_mine_n','u_mine_d','u_mine_d2','c_fire_go','shotGoo','lv7d']
    rows=[]
    for lang in page.evaluate('Object.keys(L10N)'):
        row=page.evaluate('''([lang,keys,gelKeys])=>{applyLanguage(lang);
          return {lang,names:keys.map(k=>T(k)),actual:[...BOSS_POOL,...BOSS_CHAPTER].map(b=>b.name),
            first:LEVELS[4].d,second:LEVELS[9].d,
            expectedFirst:T('lv5d',LEVELS[4].ch+1,5),expectedSecond:T('lv10d',LEVELS[9].ch+1,5),
            template:L10N[lang].lv10d,gel:gelKeys.map(k=>L10N[lang][k])};}''',[lang,keys,gel_keys])
        assert len(set(row['names']))==13 and row['names']==row['actual'],row
        assert '{0}' in row['template'] and '{1}' in row['template'],row
        assert row['first']==row['expectedFirst'] and row['second']==row['expectedSecond'],row
        assert not re.search(r'\{\d+\}',row['first']+row['second']),row
        if lang=='ja':assert all('ジェル' in text and 'グー' not in text for text in row['gel']),row
        if lang=='ko':assert all('젤' in text and not re.search(r'(?<![가-힣])구(?:\s|[가를에의도]|$)',text) for text in row['gel']),row
        rows.append({'lang':lang,'first':row['first'],'second':row['second'],'names':row['names']})
    for lang,stage in [('zh-Hant',4),('en',9)]:
        page.evaluate('([lang,stage])=>{PROGRESS=50;SEL_IDX=stage;applyLanguage(lang);renderStage();}',[lang,stage])
        page.screenshot(path=str(ARTIFACTS/f'l10n-{lang}-stage{stage+1}.png'))
    page.evaluate('''()=>{applyLanguage('en');LV_IDX=49;start();
      spawnBoss(buildBosses(CUR()).find(b=>b.superBoss));G.boss.x=G.P.x;G.boss.y=G.P.y-180;
      G.paused=true;G.hasMoved=true;DIAG.touch=3;}''')
    page.wait_for_function('G.boss.name===T("sb9")')
    page.screenshot(path=str(ARTIFACTS/'l10n-final-boss.png'))
    assert not errors,errors
    result={'build':page.evaluate('BUILD'),'cpu_rate':rate,'scroll_top':scroll,'boss_stages':stages,'rows':rows,'errors':errors}
    (ARTIFACTS/'l10n-context.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    browser.close()
print(json.dumps({'languages':len(rows),'scroll_top':scroll,'cpu_rate':rate,'errors':errors}))
print('PASS rule descriptions, 13 monster identities, terminology and real small-screen swipe')
