"""Maintain the authorized rolling Android test channel; never publish a store release."""
import argparse,hashlib,json,subprocess,urllib.request,urllib.error,urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO='davidform/goo-blaster'
TAG='android-test'
MARKER='<!-- goo-blaster-managed-android-test -->'
API='https://api.github.com'

class GitHub:
    def __init__(self):
        origin=subprocess.check_output(['git','remote','get-url','origin'],cwd=ROOT,text=True).strip()
        if origin!='https://github.com/'+REPO+'.git':raise ValueError('Unexpected repository')
        # Use Git's existing credential helper for this repository only. Never log credentials.
        result=subprocess.run(['git','credential','fill'],cwd=ROOT,input='protocol=https\nhost=github.com\npath='+REPO+'.git\n\n',text=True,capture_output=True,check=True)
        credentials=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
        self.token=credentials['password']

    def request(self,method,path,payload=None,binary=None):
        url=path if path.startswith('https://') else API+path
        if urllib.parse.urlparse(url).hostname not in ['api.github.com','uploads.github.com']:
            raise ValueError('Unexpected API host')
        data=binary if binary is not None else (json.dumps(payload).encode() if payload is not None else None)
        request=urllib.request.Request(url,data=data,method=method,headers={
            'Authorization':'Bearer '+self.token,'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'goo-blaster-test-channel',
            'Content-Type':'application/vnd.android.package-archive' if binary is not None else 'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=90) as response:return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code==404 and method=='GET':return None
            raise RuntimeError(f'GitHub {method} failed with HTTP {error.code}') from None

def channel_release(client):
    release=client.request('GET',f'/repos/{REPO}/releases/tags/{TAG}')
    if release:return release
    # Drafts have temporary untagged asset URLs and may not resolve by tag yet.
    page=1
    while True:
        releases=client.request('GET',f'/repos/{REPO}/releases?per_page=100&page={page}')
        matches=[r for r in releases if r['tag_name']==TAG]
        if len(matches)>1:raise ValueError('Multiple test channel drafts require review')
        if matches:return matches[0]
        if len(releases)<100:return None
        page+=1

def inspect(client):
    repo=client.request('GET','/repos/'+REPO)
    release=channel_release(client)
    if release and MARKER not in (release.get('body') or ''):
        raise ValueError('Existing test tag is not managed by this workflow; do not overwrite it')
    return {'repository':REPO,'can_push':repo.get('permissions',{}).get('push',False),
            'channel_exists':bool(release),'url':f'https://github.com/{REPO}/releases/tag/{TAG}',
            'release_id':release['id'] if release else None}

def publish(client,manifest,notes):
    info=inspect(client)
    if not info['can_push']:raise ValueError('Repository write permission unavailable')
    report=json.loads(manifest.read_text(encoding='utf-8'))
    pin=json.loads((ROOT/'native/test-channel.json').read_text(encoding='utf-8'))
    assert report['signer_sha256']==pin['signer_sha256'] and report['application_id']==pin['application_id']
    changes=notes.read_text(encoding='utf-8').strip()
    if not changes:raise ValueError('Human-readable test notes are required')
    apk=Path(report['apk_path']).resolve()
    if not apk.is_relative_to((ROOT/'_private/mobile-test').resolve()):raise ValueError('Unexpected artifact directory')
    data=apk.read_bytes();digest=hashlib.sha256(data).hexdigest()
    assert digest==report['apk_sha256'] and len(data)==report['bytes']
    assert report['application_id']=='com.demjastudio.gooblaster' and report['channel']==TAG and not report['official_release']
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    # A later tooling/docs commit is allowed, but the built game must remain identical.
    assert hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest()==report['game_sha256']
    subprocess.run(['git','merge-base','--is-ancestor',report['source_commit'],head],cwd=ROOT,check=True)
    release=channel_release(client)
    if release is None:
        release=client.request('POST',f'/repos/{REPO}/releases',{'tag_name':TAG,'target_commitish':report['source_commit'],
            'name':'Android 手機測試版','body':MARKER,'draft':True,'prerelease':True,'make_latest':'false'})
    assert MARKER in (release.get('body') or '') and release['prerelease']
    assets=client.request('GET',f'/repos/{REPO}/releases/{release["id"]}/assets')
    existing=next((a for a in assets if a['name']==apk.name),None)
    if existing:
        if existing.get('digest')!='sha256:'+digest:raise ValueError('Same-name asset has different content; do not overwrite')
        asset=existing
    else:
        asset=client.request('POST',f'https://uploads.github.com/repos/{REPO}/releases/{release["id"]}/assets?name='+urllib.parse.quote(apk.name),binary=data)
    assert asset['state']=='uploaded' and asset['size']==len(data)
    assert asset.get('digest')=='sha256:'+digest,'Uploaded asset digest must match the audited APK'
    download=f'https://github.com/{REPO}/releases/download/{TAG}/'+urllib.parse.quote(apk.name)
    body=f'''{MARKER}
## 最新測試版：{report['build']}

### [下載 Android 測試版 APK]({download})

請把這一頁加入手機書籤。往後都從同一頁下載最新版，不需要 USB，也不需要電腦保持開機。

1. 用 Pixel 的瀏覽器下載上方 APK，下載完成後開啟。
2. 第一次依 Android 提示允許瀏覽器安裝；已安裝時選「更新」。**請勿先解除安裝舊版**，以免刪除進度。
3. 開啟遊戲，確認版本為 **{report['build']}**。下載安裝後可離線遊玩。

{changes}

此為開發測試版，不是商店正式版。已核對 APK 內的遊戲內容、App 識別碼、版本與簽章；手機上的覆蓋更新、聲音、卡頓與後期難度仍待實測。回報時附上版本、關卡及遇到的情況即可。

<details><summary>測試版本與驗證資料</summary>

- Android versionCode：{report['version_code']}
- 遊戲來源 commit：{report['source_commit']}
- 遊戲 SHA256：`{report['game_sha256']}`
- APK SHA256：`{digest}`
- App：`{report['application_id']}`
- `android-test` 是持續更新的測試通道；每個 APK 使用獨立檔名，舊檔保留。

</details>
'''
    ref=client.request('GET',f'/repos/{REPO}/git/ref/tags/{TAG}')
    if ref and ref['object']['sha']!=report['source_commit']:
        # Advance only our marked test channel, never rewrite formal tags or non-descendant history.
        subprocess.run(['git','merge-base','--is-ancestor',ref['object']['sha'],report['source_commit']],cwd=ROOT,check=True)
        client.request('PATCH',f'/repos/{REPO}/git/refs/tags/{TAG}',{'sha':report['source_commit'],'force':False})
    release=client.request('PATCH',f'/repos/{REPO}/releases/{release["id"]}',{
        'name':f'Android 手機測試版 · {report["build"]}','body':body,'draft':False,'prerelease':True,'make_latest':'false'})
    published_asset=client.request('GET',f'/repos/{REPO}/releases/assets/{asset["id"]}')
    assert published_asset['browser_download_url']==download,'Published asset must use the permanent test tag'
    # Public download, deliberately without an Authorization header.
    with urllib.request.urlopen(download,timeout=90) as response:downloaded=response.read()
    assert hashlib.sha256(downloaded).hexdigest()==digest,'Public download differs from local audited APK'
    proof={'url':release['html_url'],'download_url':download,'build':report['build'],'apk_sha256':digest,
           'public_download_verified':True,'release_id':release['id'],'asset_id':asset['id'],'prerelease':release['prerelease']}
    (ROOT/'_private/mobile-test/published.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    print(json.dumps(proof,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true')
    parser.add_argument('--manifest',type=Path,default=ROOT/'_private/mobile-test/latest.json')
    parser.add_argument('--notes',type=Path,default=ROOT/'_private/mobile-test/notes.md')
    args=parser.parse_args();client=GitHub()
    if args.publish:publish(client,args.manifest,args.notes)
    else:print(json.dumps(inspect(client),indent=2))
