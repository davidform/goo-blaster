"""Hold a real Windows read handle while the atomic checkpoint is replaced."""
import ast,ctypes,hashlib,json,tempfile,threading,time,os,sys
from pathlib import Path
from types import SimpleNamespace
if os.name!='nt':
 print('SKIP: this sharing-lock regression is specific to Windows')
 sys.exit(0)
ROOT=Path(__file__).resolve().parents[1]
node=next(n for n in ast.parse((ROOT/'run_tests.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='checkpoint')
logs=Path(tempfile.mkdtemp(dir=ROOT/'_private/test-artifacts',prefix='checkpoint-lock-'))
target=logs/'results.json';target.write_text('{"old":true}')
kernel=ctypes.windll.kernel32
kernel.CreateFileW.restype=ctypes.c_void_p
handle=kernel.CreateFileW(str(target),0x80000000,1,None,3,0,None)
assert handle not in (None,ctypes.c_void_p(-1).value)
kernel.CloseHandle.argtypes=[ctypes.c_void_p]
threading.Timer(.25,lambda:kernel.CloseHandle(handle)).start()
ns=dict(ROOT=ROOT,logs=logs,sha=hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest(),
 opts=SimpleNamespace(jobs=2),env={},regular=[],solo=[],active={},results=[],json=json,hashlib=hashlib,time=time)
exec(compile(ast.Module(body=[node],type_ignores=[]),'checkpoint','exec'),ns)
t=time.monotonic();ns['checkpoint'](True);elapsed=time.monotonic()-t
assert json.loads(target.read_text())['complete']
print('PASS actual Windows sharing lock released, checkpoint saved; seconds=',round(elapsed,3))
