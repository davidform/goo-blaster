"""Prepare verified-release Devlogs and record UI-verified publication; no credentials or posting API."""
import argparse, hashlib, html, json, re
from datetime import datetime, timezone
from pathlib import Path

PAGE='https://davidform.itch.io/goo-blaster'
def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(release,notes,directory):
    if not (release.get('page')==PAGE and release.get('game_payload_identical') is True and release.get('browser_start_verified') is True):
        raise ValueError('Verified public itch game payload and browser start are required')
    version=notes['build']
    if not re.fullmatch(r'v\d+\.\d+\.\d+',version) or version!=release['build']:
        raise ValueError('Notes must describe the verified public version')
    if version not in notes['title'] or not notes['blocks']:
        raise ValueError('A versioned title and player-facing content are required')
    if not re.fullmatch(r'[0-9a-f]{64}',release['game_sha256']):
        raise ValueError('Invalid verified game SHA256')
    if notes['languages']!=['en','zh-Hant']:
        raise ValueError('This project uses English and Traditional Chinese Devlogs')
    parts=[];in_list=False
    for block in notes['blocks']:
        kind=block['kind'];text=block['text']
        if kind not in ('h2','p','li') or not isinstance(text,str) or not text.strip():
            raise ValueError('Invalid content block')
        if kind=='li' and not in_list:parts.append('<ul>');in_list=True
        if kind!='li' and in_list:parts.append('</ul>');in_list=False
        parts.append(f'<{kind}>{html.escape(text)}</{kind}>')
    if in_list:parts.append('</ul>')
    folder=Path(directory)/version;folder.mkdir(parents=True,exist_ok=True);path=folder/'post.json'
    content_hash=digest(notes)
    if path.exists():
        old=read(path)
        if old['public_game_sha256']!=release['game_sha256']:
            raise ValueError('This version already refers to a different game payload')
        if old['content_sha256']==content_hash:return path
        if old['status']=='published':raise ValueError('Published content cannot be silently replaced')
    post=dict(notes,status='prepared',content_sha256=content_hash,public_game_sha256=release['game_sha256'],
              public_build_id=release['build_id'],page=PAGE,post_type='General Update or Announcement',body_html='\n'.join(parts))
    write(path,post);(folder/'body.html').write_text(post['body_html'],encoding='utf-8');return path
def record(path,receipt):
    post=read(path);url=receipt['url']
    if receipt.get('published') is not True:
        raise ValueError('The public Published state must be verified, not only a draft preview')
    if not re.fullmatch(re.escape(PAGE)+r'/devlog/\d+/[a-z0-9-]+',url):
        raise ValueError('Expected this project\'s public Devlog URL')
    norm=lambda s:' '.join(s.split())
    if receipt['title']!=post['title'] or not all(norm(b['text']) in norm(receipt['body_text']) for b in post['blocks']):
        raise ValueError('Public title and every content block must be verified in the browser')
    if post['status']=='published':
        if post['url']!=url:raise ValueError('Duplicate publication URL for this version')
        return post
    post.update(status='published',url=url,verified_at=datetime.now(timezone.utc).isoformat())
    write(path,post);return post
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--release',required=True);p.add_argument('--notes',required=True);p.add_argument('--output',default='store/devlogs')
    p=sub.add_parser('record');p.add_argument('--post',required=True);p.add_argument('--receipt',required=True)
    args=parser.parse_args()
    if args.command=='prepare':print(prepare(read(args.release),read(args.notes),args.output))
    else:print(record(args.post,read(args.receipt))['url'])
