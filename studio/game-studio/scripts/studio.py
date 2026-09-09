"""Create isolated game-project instructions and inspect configuration. No publishing."""
import argparse,json,re,sys
from pathlib import Path

LANGUAGES=['en','zh-Hant','zh-Hans','ja','ko','de','fr','es','it','pt-BR','ru']
GATES=['full','edges','stress','offline','device']

def local(root,value):
    p=(root/value).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('Project paths must stay inside the project')
    return p

def validate(profile,root):
    if profile.get('schema_version')!=1:raise ValueError('Unsupported studio schema')
    if not re.fullmatch(r'[a-z][a-z0-9-]{1,63}',profile['id']):raise ValueError('Invalid project id')
    if not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*){2,}',profile['app_id']):raise ValueError('Invalid app id')
    for key in ['artifact','handoff','history']:local(root,profile[key])
    if profile['default_language'] not in profile['languages']:raise ValueError('Missing default language')
    if set(profile['verification'])!=set(GATES):raise ValueError('Verification gates must be explicit')
    for gate,value in profile['verification'].items():
        if value is not None and (not isinstance(value,list) or not value or not all(isinstance(v,str) and v for v in value)):
            raise ValueError('Commands must be argument arrays or null for unconfigured gates')
    auth=profile['authorization']
    if auth['official_release'] or auth['pricing_changes']:
        raise ValueError('Record task-specific official publication authorization separately')
    return profile

def initialize(target,slug,title,app_id,idea):
    target=target.resolve()
    if target.exists():raise ValueError('Destination exists; initialization never overwrites a project')
    if app_id=='com.demjastudio.gooblaster':raise ValueError('New games must not reuse the existing GOO BLASTER app id')
    profile={'schema_version':1,'workflow_version':'1.0','id':slug,'title':title,'app_id':app_id,
      'phase':'concept','engine':'evaluate-web-canvas-first','artifact':'index.html',
      'handoff':'HANDOFF.md','history':'HISTORY.md','default_language':'en','languages':LANGUAGES,
      'business':{'model':'paid-once','price':None,'audience':'to-confirm'},
      'verification':{g:None for g in GATES},'test_channel':None,
      'authorization':{'git_sync':False,'test_distribution':False,'official_release':False,'pricing_changes':False}}
    validate(profile,target)
    # Do not copy the previous game's runtime, saves, app identity, signing key or permissions.
    target.mkdir(parents=True)
    (target/'studio.project.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (target/'AGENTS.md').write_text('''# 遊戲專案規則
先讀 studio.project.json、HANDOFF.md 與使用者 game-studio skill。
繁體中文，單一代理預設；額外agents依使用者授權，禁止共同修改同一產物。
核對實際Git與產物，勿覆蓋未提交差異。實際跑測試，不以文件或假資料當完成證據。
所有玩家文字走本地化、預設英文；離線原型不引入CDN。
一次只改一項平衡槓桿；保留失敗與未執行紀錄，效能獨立量測。
商業預設一次買斷；售價與受眾另確認。不沿用其他遊戲的appId、簽章或發布授權。
完成後更新精簡HANDOFF與HISTORY，提供測試證據、未完成與確切commit Summary。
測試通道尚未啟用，正式上架尚未授權；設定檢查通過不等於遊戲驗收通過。
''',encoding='utf-8')
    (target/'HANDOFF.md').write_text('# 目前交接\n- 階段：構想；沒有可玩產物，也沒有已執行的遊戲測試。\n- 已建立工作室專案設定；原始想法見IDEA.md。\n- 下一步：確認核心迴圈、受眾與最小原型，再選擇引擎並填入實際測試命令。\n- Git同步／測試分發／正式發布尚未授權。\n',encoding='utf-8')
    (target/'HISTORY.md').write_text('# 決策與驗證\n\n工作室流程v1.0初始化；未建立遊戲或聲稱測試通過。\n',encoding='utf-8')
    (target/'IDEA.md').write_text('# 原始遊戲想法\n\n'+idea+'\n',encoding='utf-8')
    (target/'.gitignore').write_text('_private/\n.venv/\nnode_modules/\n__pycache__/\n*.keystore\n*.jks\n.env\nlocal.properties\n',encoding='utf-8')
    return profile

def inspect(root):
    root=root.resolve();profile=validate(json.loads((root/'studio.project.json').read_text(encoding='utf-8-sig')),root)
    missing=[g for g,v in profile['verification'].items() if v is None]
    return {'project':profile['id'],'configuration_valid':True,'artifact_exists':local(root,profile['artifact']).is_file(),
      'unconfigured_gates':missing,'tests_executed':False,'release_approved':False,
      'test_channel':profile['test_channel']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    init=sub.add_parser('init');init.add_argument('--target',required=True,type=Path)
    for key in ['id','title','app-id','idea']:init.add_argument('--'+key,required=True)
    check=sub.add_parser('check');check.add_argument('--root',type=Path,default=Path.cwd())
    args=parser.parse_args()
    try:
        if args.command=='init':
            initialize(args.target,args.id,args.title,args.app_id,args.idea)
            print(json.dumps(inspect(args.target),ensure_ascii=False,indent=2))
        else:print(json.dumps(inspect(args.root),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as error:
        print(str(error),file=sys.stderr);sys.exit(2)
