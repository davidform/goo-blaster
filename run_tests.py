"""Cross-platform runner using the same suite lists as run_tests.sh.

python run_tests.py --jobs 4
python run_tests.py --jobs 48 --label stress
python run_tests.py --only py_i18n py_test9 --label focused
Performance runs alone after all other tests. Logs never overwrite earlier runs.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--jobs', type=int, default=4)
parser.add_argument('--only', nargs='+')
parser.add_argument('--label', default='full')
parser.add_argument('--timeout', type=int, default=900)
opts = parser.parse_args()
if opts.jobs < 1:
    parser.error('--jobs must be positive')
shell = (ROOT / 'run_tests.sh').read_text(encoding='utf-8').split('\nelse\n', 1)[1]
def names(key):
    return re.search(r'\b' + key + r'="([^"]+)"', shell).group(1).replace('\\\n', ' ').split()
regular = names('PY') + names('JS')
solo = names('SOLO')
if opts.only:
    unknown = set(opts.only) - set(regular + solo)
    if unknown:
        parser.error('Unknown test names: ' + ', '.join(sorted(unknown)))
    regular = [n for n in regular if n in opts.only]
    solo = [n for n in solo if n in opts.only]
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
logs = ROOT / '_private' / 'test-runs' / (stamp + '-' + opts.label)
logs.mkdir(parents=True)
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1', GOO_ROOT=str(ROOT))
sha = hashlib.sha256((ROOT / 'index.html').read_bytes()).hexdigest()
lock = threading.Lock()
results = []
active = {}
def checkpoint(complete=False):
    report = dict(sha256=sha, source_unchanged=sha == hashlib.sha256((ROOT / 'index.html').read_bytes()).hexdigest(),
                  jobs=opts.jobs, browser_channel=env.get('GOO_BROWSER_CHANNEL', 'chromium'),
                  complete=complete, planned=regular + solo, active=active, results=results)
    temporary = logs / 'results.tmp'
    temporary.write_text(json.dumps(report, indent=2), encoding='utf-8')
    # Windows readers/virus scanners can briefly deny replacement of an open
    # report. Keep the previous atomic checkpoint intact and retry the rename.
    for attempt in range(20):
        try:
            temporary.replace(logs / 'results.json')
            break
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(0.05)
checkpoint()
print('Logs:', logs, '\nSHA256:', sha, flush=True)
subprocess.run(['node', 'tests/syntax_check.js'], cwd=ROOT, env=env, check=True)
def run(name):
    suffix = '.py' if name.startswith('py_') else '.js'
    command = [sys.executable if suffix == '.py' else 'node', str(ROOT / 'tests' / (name + suffix))]
    begin = time.monotonic()
    with (logs / (name + '.log')).open('w', encoding='utf-8') as output:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=os.name != 'nt')
        with lock:
            active[name] = process.pid
            checkpoint()
        try:
            code = process.wait(timeout=opts.timeout)
        except subprocess.TimeoutExpired:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            else:
                import signal
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = 124
    content = (logs / (name + '.log')).read_text(encoding='utf-8')
    # Some legacy checks print FAIL but forget to set a non-zero exit code.
    printed_failure = bool(re.search(r'^\s*FAIL\b', content, re.M))
    if suffix == '.js' and code == 0:
        # These legacy Node tools emit JSON instead of asserting page errors.
        try:
            payload = json.loads(content)
            printed_failure = printed_failure or bool(payload.get('errs'))
        except (ValueError, AttributeError):
            printed_failure = True
    result = dict(test=name, exit_code=code, printed_failure=printed_failure,
                  seconds=round(time.monotonic()-begin, 1), passed=code == 0 and not printed_failure)
    with lock:
        active.pop(name, None)
        results.append(result)
        checkpoint()
    print(('PASS' if result['passed'] else 'FAIL'), name, result['seconds'], flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=opts.jobs) as pool:
    for future in concurrent.futures.as_completed([pool.submit(run, name) for name in regular]):
        future.result()
for name in solo:
    run(name)
unchanged = sha == hashlib.sha256((ROOT / 'index.html').read_bytes()).hexdigest()
checkpoint(complete=True)
failed = [r['test'] for r in results if not r['passed']]
print('FAILED:', failed, 'Source unchanged:', unchanged, flush=True)
sys.exit(1 if failed or not unchanged else 0)
