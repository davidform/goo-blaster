"""Synchronize the web payload and Android identifiers without signing credentials.

Run before `npx cap sync android`, then build from native/android.
The generated Android tree remains local; this script makes the identifier fix reproducible.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil

NATIVE = Path(__file__).resolve().parent
REPO = NATIVE.parent
config = json.loads((NATIVE / 'capacitor.config.json').read_text(encoding='utf-8'))
app_id = config['appId']
if not re.fullmatch(r'[a-z]\w*(?:\.[a-z]\w*)+', app_id):
    raise ValueError('Invalid appId')
android = NATIVE / 'android'
gradle = (android / 'app/build.gradle').read_text(encoding='utf-8')
for key in ['namespace', 'applicationId']:
    if not re.search(key + r'\s+["\x27]' + re.escape(app_id) + r'["\x27]', gradle):
        raise ValueError(key + ' must match capacitor.config.json')
activities = list((android / 'app/src/main/java').rglob('MainActivity.java'))
if len(activities) != 1:
    raise ValueError('Expected exactly one MainActivity.java')
activity = activities[0]
strings = android / 'app/src/main/res/values/strings.xml'
for file in [activity, strings]:
    source = file.read_text(encoding='utf-8')
    # Only accept the known migration; unknown values require investigation.
    if file == activity:
        match = re.search(r'^package ([\w.]+);', source, re.M)
        if not match or match[1] not in [app_id, 'io.itch.davidform.gooblaster']:
            raise ValueError('Unexpected activity package')
        updated = source.replace(match[0], 'package ' + app_id + ';', 1)
    else:
        updated = source
        for key in ['package_name', 'custom_url_scheme']:
            pattern = r'(<string name="' + key + r'">)([^<]+)(</string>)'
            match = re.search(pattern, updated)
            if not match or match[2] not in [app_id, 'io.itch.davidform.gooblaster']:
                raise ValueError('Unexpected ' + key)
            updated = re.sub(pattern, lambda m: m[1] + app_id + m[3], updated)
    if updated != source:
        backup = REPO / '_private' / 'android-preparation-backup' / file.relative_to(android)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(file, backup)
        file.write_text(updated, encoding='utf-8', newline='\n')
# Tracked native feature sources must be copied on every build, not only on this PC.
for name in ['MainActivity.java', 'BattleReportPlugin.java']:
    source = NATIVE / 'android-src' / name
    shutil.copyfile(source, activity.parent / name)
web = (NATIVE / config['webDir']).resolve()
if not web.is_relative_to(NATIVE):
    raise ValueError('webDir must remain inside native')
web.mkdir(parents=True, exist_ok=True)
shutil.copyfile(REPO / 'index.html', web / 'index.html')
print('Prepared', app_id)
print('Game SHA256:', hashlib.sha256((web / 'index.html').read_bytes()).hexdigest())
