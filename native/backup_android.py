"""Create a local Android source backup excluding caches, artifacts and credentials."""
from pathlib import Path
import datetime
import json
import re
import zipfile

native = Path(__file__).resolve().parent
out = native.parent / '_private' / 'android-backups'
out.mkdir(parents=True, exist_ok=True)
destination = out / ('android-source-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip')
excluded_dirs = {'.git', '.gradle', '.idea', 'build', 'node_modules', '.cxx'}
excluded_names = {'local.properties', 'key.properties', 'keystore.properties', 'google-services.json'}
files = []
for file in (native / 'android').rglob('*'):
    if not file.is_file():
        continue
    relative = file.relative_to(native)
    if any(part in excluded_dirs for part in relative.parts) or file.name in excluded_names:
        continue
    if file.suffix.lower() in {'.jks', '.keystore', '.p12', '.pem', '.key'}:
        continue
    if file.suffix in {'.gradle', '.properties'}:
        text = file.read_text(encoding='utf-8', errors='replace')
        if re.search(r'(?i)storePassword|keyPassword|storeFile|api[_-]?key\s*[=:]', text):
            raise ValueError('Credential-related configuration needs manual exclusion: ' + str(relative))
    files.append(file)
files += [native / name for name in ['package.json', 'package-lock.json', 'capacitor.config.json',
                                   'prepare_android.py', 'test_device.cjs', 'audit_artifacts.py', 'backup_android.py', 'README.md', 'BUILD-WINDOWS.md']]
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        archive.write(file, file.relative_to(native).as_posix())
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert not any(name.endswith(tuple(excluded_names)) for name in archive.namelist())
print(json.dumps({'backup':str(destination), 'files':len(files), 'bytes':destination.stat().st_size}, indent=2))
