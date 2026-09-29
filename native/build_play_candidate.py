"""Build and audit an UNSIGNED Play candidate; never creates keys or uploads.

Run only after browser tests (including solo performance) finish. The existing
Android test version configuration is restored byte-for-byte even after failure.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from build_test_apk import ROOT, NATIVE, validate_reports, run


def build(args):
    source = (ROOT / 'index.html').read_bytes()
    sha = hashlib.sha256(source).hexdigest()
    validate_reports(args.tests, args.retry, sha)
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', 'index.html'], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    if b"const EDITION='full'" not in source:
        raise ValueError('Paid download must contain the full edition')
    version = re.search(rb"const BUILD='v([^']+)'", source)[1].decode()
    gradle = NATIVE / 'android/app/build.gradle'
    original = gradle.read_bytes()
    text = original.decode('utf-8')
    if re.search(r'signingConfig|storeFile|storePassword|keyPassword', text):
        raise ValueError('Signing configuration detected; this command is UNSIGNED only')
    existing_code = int(re.search(r'versionCode\s+(\d+)', text)[1])
    code = existing_code + 1
    replacement = re.sub(r'versionCode\s+\d+', f'versionCode {code}', text, count=1)
    replacement = re.sub(r'versionName\s+"[^"]+"', f'versionName "{version}-rc.1"', replacement, count=1)
    env = dict(os.environ, JAVA_HOME=str(args.java))
    if not re.search(r'version "21\.', run([args.java/'bin/java.exe','-version'],env=env)):
        raise ValueError('Use JDK 21')
    out = ROOT / '_private/play-preparation'
    out.mkdir(parents=True, exist_ok=True)
    bundle = out / f'goo-blaster-v{version}-{code}-unsigned.aab'
    if bundle.exists():
        raise ValueError('Candidate already exists; audit it or choose a new version, do not overwrite')
    try:
        gradle.write_text(replacement, encoding='utf-8')
        print(run([os.sys.executable,NATIVE/'prepare_android.py'],env=env),flush=True)
        print(run(['node',NATIVE/'node_modules/@capacitor/cli/bin/capacitor','sync','android'],cwd=NATIVE,env=env),flush=True)
        print(run([NATIVE/'android/gradlew.bat','--no-daemon','--max-workers=2','bundleRelease'],cwd=NATIVE/'android',env=env),flush=True)
        shutil.copyfile(NATIVE/'android/app/build/outputs/bundle/release/app-release.aab', bundle)
    finally:
        gradle.write_bytes(original)
    assert gradle.read_bytes() == original
    tool = [args.java/'bin/java.exe','-jar',args.bundletool]
    validation = run([*tool,'validate','--bundle='+str(bundle)],env=env)
    manifest_text = run([*tool,'dump','manifest','--bundle='+str(bundle),'--module=base'],env=env)
    (out / 'candidate-manifest.xml').write_text(manifest_text,encoding='utf-8')
    manifest = ET.fromstring(manifest_text)
    ns = '{http://schemas.android.com/apk/res/android}'
    app_id = 'com.demjastudio.gooblaster'
    assert manifest.attrib['package'] == app_id
    assert manifest.attrib[ns+'versionCode'] == str(code)
    assert manifest.attrib[ns+'versionName'] == version+'-rc.1'
    assert manifest.find('uses-sdk').attrib[ns+'targetSdkVersion'] == '36'
    assert manifest.find('application').attrib.get(ns+'debuggable','false') == 'false'
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read('base/assets/public/index.html')).hexdigest() == sha
        assert json.loads(z.read('base/assets/capacitor.config.json'))['appId'] == app_id
        signatures = [n for n in z.namelist() if re.match(r'META-INF/.*\.(RSA|DSA|EC|SF)$',n)]
        assert not signatures, 'Unexpected signature in unsigned candidate'
        native_libraries = [n for n in z.namelist() if n.endswith('.so')]
    assert (ROOT/'index.html').read_bytes() == source
    report = dict(build='v'+version,version_code=code,version_name=version+'-rc.1',application_id=app_id,
        game_sha256=sha,aab_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),aab_path=str(bundle),
        bytes=bundle.stat().st_size,bundletool_validated=True,bundletool_output=validation.strip(),
        target_sdk=36,debuggable=False,permissions=[e.attrib[ns+'name'] for e in manifest.findall('uses-permission')],
        native_libraries=native_libraries,jar_signatures=signatures,signed=False,uploaded=False,
        android_test_config_restored=True,tests=[str(p) for p in [args.tests,*args.retry]],
        remaining=['Upload-key authorization and secure backup','Sign and verify final bundle','Play delivery/device validation','Console review and real closed testing'])
    (out/'candidate.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tests',type=Path,required=True)
    p.add_argument('--retry',type=Path,action='append',default=[])
    p.add_argument('--bundletool',type=Path,required=True)
    p.add_argument('--java',type=Path,default=Path.home()/'.jdks/jbr-21.0.11')
    build(p.parse_args())
