"""Capture the real home and garden layout with fresh saves; no player data."""
import hashlib,json,os,re
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
source=(root/'index.html').read_bytes()
build=re.search(rb"const BUILD='([^']+)'",source)[1].decode()
out=root/'store/screenshots'/build;out.mkdir(parents=True,exist_ok=True)
rows=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(channel=os.getenv('GOO_BROWSER_CHANNEL','msedge'))
    c=b.new_context(viewport={'width':393,'height':759},has_touch=True,device_scale_factor=2)
    c.set_offline(True);p=c.new_page();p.goto((root/'index.html').as_uri())
    for lang in ['en','zh-Hant']:
        p.evaluate('v=>{applyLanguage(v);renderTown()}',lang)
        for name,nav in [('home-fit','btnHome'),('garden-scroll','navGarden')]:
            p.locator('#'+nav).tap()
            if nav=='navGarden':p.locator('#garden').evaluate('e=>e.scrollTop=e.scrollHeight')
            file=f'{name}-{lang}.png';p.screenshot(path=str(out/file))
            rows.append(dict(file=file,language=lang,viewport=[393,759],build=build,sha256=hashlib.sha256(source).hexdigest(),setup='Fresh offline save; real navigation; garden scrolled to bottom; browser capture, not Android.'))
    b.close()
(out/'viewport-manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
