"""Verify the built APK/AAB payloads, not merely source files or Gradle output."""
from pathlib import Path
import hashlib
import json
import zipfile
import xml.etree.ElementTree as ET

native = Path(__file__).resolve().parent
root = native.parent
sha = lambda data: hashlib.sha256(data).hexdigest()
expected = sha((root / 'index.html').read_bytes())
app = json.loads((native / 'capacitor.config.json').read_text())['appId']
report = {'game_sha256':expected, 'artifacts':[]}
for filename, prefix in [('apk/debug/app-debug.apk',''), ('bundle/release/app-release.aab','base/')]:
    file = native / 'android/app/build/outputs' / filename
    with zipfile.ZipFile(file) as archive:
        assert archive.testzip() is None
        assert sha(archive.read(prefix + 'assets/public/index.html')) == expected
        config = json.loads(archive.read(prefix + 'assets/capacitor.config.json'))
        assert config['appId'] == app
        signatures = [n for n in archive.namelist() if n.startswith('META-INF/') and n.endswith(('.RSA','.DSA','.EC'))]
        if prefix:
            assert (app + '.MainActivity').encode() in archive.read('base/manifest/AndroidManifest.xml')
        report['artifacts'].append({'path':str(file), 'bytes':file.stat().st_size,
                                    'sha256':sha(file.read_bytes()), 'jar_signature_entries':signatures})
manifest_path = native / 'android/app/build/intermediates/packaged_manifests/release/processReleaseManifestForPackage/AndroidManifest.xml'
manifest = ET.parse(manifest_path).getroot()
ns = '{http://schemas.android.com/apk/res/android}'
application = manifest.find('application')
assert manifest.attrib['package'] == app
assert application.attrib.get(ns+'debuggable', 'false') == 'false'
assert application.find('activity').attrib[ns+'name'] == app+'.MainActivity'
report['release_merged_manifest'] = {'package':app, 'allowBackup':application.attrib.get(ns+'allowBackup'),
    'debuggable':application.attrib.get(ns+'debuggable', 'false'),
    'permissions':[p.attrib[ns+'name'] for p in manifest.findall('uses-permission')]}
report['limits'] = ['Release AAB is unsigned; no store submission.',
                    'Device validation used the debug APK, not an AAB-derived install.']
output = root / '_private/test-artifacts/android-artifacts.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
