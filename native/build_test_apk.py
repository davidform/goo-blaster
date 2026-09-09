"""Build an update-compatible Android test APK after browser regression passes."""
import argparse,hashlib,json,os,re,shutil,subprocess,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'native'
sha=lambda data:hashlib.sha256(data).hexdigest()

def required_suite():
    shell=(ROOT/'run_tests.sh').read_text(encoding='utf-8').split('\nelse\n',1)[1]
    return {name for key in ['PY','JS','SOLO'] for name in re.search(r'\b'+key+r'="([^"]+)"',shell)[1].replace('\\\n',' ').split()}

def validate_reports(tests,retries,game_sha):
    report=json.loads(tests.read_text(encoding='utf-8'));required=required_suite()
    if set(report['planned'])!=required:raise ValueError('The primary report must cover the entire current suite')
    merged={}
    for path in [tests,*retries]:
        data=json.loads(path.read_text(encoding='utf-8'))
        if not(data['complete'] and data['source_unchanged'] and data['sha256']==game_sha):
            raise ValueError('Complete reports for the unchanged game payload are required')
        if {r['test'] for r in data['results']}!=set(data['planned']):raise ValueError('Incomplete test result list')
        if not set(data['planned']).issubset(required):raise ValueError('Unknown test in retry report')
        merged.update({r['test']:r['passed'] and r['exit_code']==0 and not r['printed_failure'] for r in data['results']})
    if set(merged)!=required or not all(merged.values()):raise ValueError('Every required test must pass before packaging')

def run(args,cwd=None,env=None):
    try:
        return subprocess.check_output([str(a) for a in args],cwd=cwd,env=env,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    except subprocess.CalledProcessError as error:
        print(error.output,flush=True)
        raise

def build_test(tests,java,sdk,retries=()):
    game=(ROOT/'index.html').read_bytes();game_sha=sha(game)
    build=re.search(rb"const BUILD='(v(\d+)\.(\d+)\.(\d+))'",game)
    if not build:raise ValueError('Missing game version')
    version=build[1].decode();major,minor,patch=map(int,build.groups()[1:])
    if minor>=100 or patch>=100:raise ValueError('Version components exceed the Android versionCode mapping')
    subprocess.run(['git','diff','--exit-code','HEAD','--','index.html'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    validate_reports(tests,retries,game_sha)
    env=dict(os.environ,JAVA_HOME=str(java),ANDROID_HOME=str(sdk))
    if not re.search(r'version "21\.',run([java/'bin/java.exe','-version'],env=env)):
        raise ValueError('Use the validated JDK 21')
    builds=sorted((p for p in (sdk/'build-tools').iterdir() if re.fullmatch(r'\d+(?:\.\d+)+',p.name)),key=lambda p:tuple(map(int,p.name.split('.'))))
    tools=builds[-1];signer=tools/'apksigner.bat';aapt=tools/'aapt.exe'
    def certificate(path):
        output=run([signer,'verify','--print-certs',path],env=env)
        return re.search(r'Signer #1 certificate SHA-256 digest: (\w+)',output)[1].lower()
    apk=NATIVE/'android/app/build/outputs/apk/debug/app-debug.apk'
    previous=certificate(apk) if apk.exists() else None
    previous_code=0
    if apk.exists():
        old_package=re.search(r"package: name='([^']+)' versionCode='([^']+)'",run([aapt,'dump','badging',apk],env=env))
        assert old_package and old_package[1]=='com.demjastudio.gooblaster'
        previous_code=int(old_package[2])
    gradle=NATIVE/'android/app/build.gradle';s=gradle.read_text(encoding='utf-8')
    old_code=int(re.search(r'versionCode\s+(\d+)',s)[1]);base=major*1_000_000+minor*10_000+patch*100
    code=max(base,old_code+1,previous_code+1)
    if code>=base+100:raise ValueError('Test revision exhausted; advance game version')
    name=version[1:]+f'-test.{code-base}'
    s=re.sub(r'versionCode\s+\d+',f'versionCode {code}',s,count=1)
    s=re.sub(r'versionName\s+"[^"]+"',f'versionName "{name}"',s,count=1)
    gradle.write_text(s,encoding='utf-8')
    print(run([os.sys.executable,NATIVE/'prepare_android.py'],env=env),flush=True)
    print(run(['node',NATIVE/'node_modules/@capacitor/cli/bin/capacitor','sync','android'],cwd=NATIVE,env=env),flush=True)
    print(run([NATIVE/'android/gradlew.bat','--no-daemon','--max-workers=2','assembleDebug'],cwd=NATIVE/'android',env=env),flush=True)
    with zipfile.ZipFile(apk) as z:
        assert z.testzip() is None
        assert sha(z.read('assets/public/index.html'))==game_sha
        config=json.loads(z.read('assets/capacitor.config.json'))
        assert config['appId']=='com.demjastudio.gooblaster'
    badging=run([aapt,'dump','badging',apk],env=env)
    package=re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'",badging)
    assert package and package.groups()==(config['appId'],str(code),name)
    cert=certificate(apk)
    if previous and cert!=previous:raise ValueError('Signing certificate changed; cannot preserve installed app data through an update')
    pin=NATIVE/'test-channel.json'
    if pin.exists():
        assert json.loads(pin.read_text(encoding='utf-8'))['signer_sha256']==cert,'Recover the original test signing key; do not change it'
    else:
        assert previous==cert,'First channel setup requires the existing validated test APK as signing baseline'
        pin.write_text(json.dumps({'channel':'android-test','application_id':config['appId'],'signer_sha256':cert},indent=2)+'\n',encoding='utf-8')
    assert sha((ROOT/'index.html').read_bytes())==game_sha,'Game changed during build'
    target=ROOT/'_private/mobile-test';target.mkdir(parents=True,exist_ok=True)
    filename=f'goo-blaster-{version}-{code}.apk';out=target/filename
    shutil.copyfile(apk,out)
    report={'build':version,'version_code':code,'version_name':name,'application_id':config['appId'],
      'game_sha256':game_sha,'apk_sha256':sha(out.read_bytes()),'apk_path':str(out),'bytes':out.stat().st_size,
      'signer_sha256':cert,'previous_signer_sha256':previous,'same_signer_as_previous_apk':previous==cert,
      'test_results':[str(p.resolve()) for p in [tests,*retries]],'source_commit':run(['git','rev-parse','HEAD'],cwd=ROOT).strip(),
      'device_update_verified':False,'channel':'android-test','official_release':False}
    (target/'latest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests',required=True,type=Path)
    parser.add_argument('--retry',action='append',type=Path,default=[],help='Same-payload focused retry report; the original full report remains required')
    parser.add_argument('--java',type=Path,default=Path.home()/'.jdks/jbr-21.0.11')
    parser.add_argument('--sdk',type=Path,default=Path(os.environ.get('LOCALAPPDATA',''))/'Android/Sdk')
    args=parser.parse_args();build_test(args.tests,args.java,args.sdk,args.retry)
