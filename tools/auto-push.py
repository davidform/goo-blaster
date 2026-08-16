#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動上傳到 GitHub
放在專案資料夾（跟 .git 同一層）執行，會持續監看檔案變動，
一有改動就自動 commit + push。筆電長開著就能一直跑。

零相依套件，只用 Python 標準函式庫。
"""
import os, sys, time, subprocess, hashlib
from datetime import datetime

ROOT      = os.path.dirname(os.path.abspath(__file__))
POLL      = 2.0      # 每幾秒看一次
DEBOUNCE  = 4.0      # 檔案停止變動幾秒後才上傳（避免存檔存到一半就送出）
RETRY     = 30.0     # push 失敗後隔多久重試
IGNORE_DIRS  = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.idea', '.vscode'}
IGNORE_FILES = {'.DS_Store', 'Thumbs.db'}
IGNORE_EXT   = {'.pyc', '.tmp', '.swp', '.log'}


def log(msg, tag='·'):
    print('  %s %s  %s' % (datetime.now().strftime('%H:%M:%S'), tag, msg), flush=True)


def git(*args, check=False):
    """跑 git，回傳 (returncode, stdout+stderr)"""
    try:
        r = subprocess.run(['git'] + list(args), cwd=ROOT,
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except FileNotFoundError:
        return 127, 'git not found'


def snapshot():
    """掃描資料夾，回傳一個代表「目前內容」的指紋"""
    h = hashlib.md5()
    n = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for fn in sorted(filenames):
            if fn in IGNORE_FILES:              continue
            if os.path.splitext(fn)[1] in IGNORE_EXT: continue
            p = os.path.join(dirpath, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            h.update(os.path.relpath(p, ROOT).encode('utf-8', 'replace'))
            h.update(str(int(st.st_mtime)).encode())
            h.update(str(st.st_size).encode())
            n += 1
    return h.hexdigest(), n


def changed_files():
    code, out = git('status', '--porcelain')
    if code != 0:
        return []
    names = []
    for line in out.splitlines():
        if len(line) > 3:
            names.append(line[3:].strip().strip('"'))
    return names


def do_push():
    files = changed_files()
    if not files:
        return None                              # 內容其實沒變（可能只是 mtime 動了）

    git('add', '-A')
    code, _ = git('diff', '--cached', '--quiet')
    if code == 0:
        return None                              # 加進暫存後發現沒有實際差異

    preview = ', '.join(files[:3]) + ('' if len(files) <= 3 else ' 等 %d 個檔案' % len(files))
    msg = '自動更新 %s — %s' % (datetime.now().strftime('%Y-%m-%d %H:%M'), preview)

    code, out = git('commit', '-m', msg)
    if code != 0 and 'nothing to commit' not in out:
        return ('commit 失敗', out.strip()[:300])

    log('已提交：%s' % preview, '✓')
    code, out = git('push')
    if code != 0:
        # 最常見的原因：你在手機上用 GitHub 網頁改過檔案，遠端比本地新。
        # 先把遠端的改動 rebase 進來再推一次。
        low = out.lower()
        if 'rejected' in low or 'non-fast-forward' in low or 'fetch first' in low:
            log('遠端有新的更動，先同步再推…', '↓')
            code2, out2 = git('pull', '--rebase')
            if code2 != 0:
                git('rebase', '--abort')
                return ('遠端與本地衝突，需要你手動處理', out2.strip()[:400])
            code, out = git('push')
            if code != 0:
                return ('push 失敗（已嘗試同步）', out.strip()[:400])
        else:
            return ('push 失敗', out.strip()[:400])
    log('已上傳到 GitHub', '↑')
    return True


def preflight():
    if not os.path.isdir(os.path.join(ROOT, '.git')):
        print('\n  ⚠ 這個資料夾不是 git repo（找不到 .git）\n')
        print('  請先在這個資料夾執行一次：\n')
        print('    git init')
        print('    git branch -M main')
        print('    git remote add origin https://github.com/你的帳號/你的repo.git')
        print('    git add -A && git commit -m "first" && git push -u origin main\n')
        input('  按 Enter 關閉...')
        return False
    gi = os.path.join(ROOT, '.gitignore')
    if not os.path.exists(gi):
        try:
            with open(gi, 'w', encoding='utf-8') as f:
                f.write('\n'.join([
                    '# 由 auto-push.py 自動建立', '*.log', '*.tmp', '*.swp',
                    'node_modules/', '__pycache__/', '.venv/', 'venv/',
                    'dist/', 'build/', '.DS_Store', 'Thumbs.db', '']))
            log('已建立 .gitignore（避免暫存檔被上傳）', '+')
        except OSError:
            pass
    code, out = git('remote', 'get-url', 'origin')
    if code != 0:
        print('\n  ⚠ 這個 repo 還沒設定 origin 遠端\n')
        print('    git remote add origin https://github.com/你的帳號/你的repo.git\n')
        input('  按 Enter 關閉...')
        return False
    return out.strip()


def main():
    remote = preflight()
    if not remote:
        return
    _, branch = git('rev-parse', '--abbrev-ref', 'HEAD')
    bar = '═' * 54
    print('\n╔' + bar + '╗')
    print('║  自動上傳 GitHub — 監看中' + ' ' * 28 + '║')
    print('╠' + bar + '╣')
    print('║  資料夾：%-44s║' % ROOT[-44:])
    print('║  遠端　：%-44s║' % remote[-44:])
    print('║  分支　：%-44s║' % branch.strip()[-44:])
    print('║' + ' ' * 54 + '║')
    print('║  改完檔案 → %d 秒後自動 commit + push' % int(DEBOUNCE) + ' ' * 15 + '║')
    print('║  要停止：按 Ctrl + C' + ' ' * 33 + '║')
    print('╚' + bar + '╝\n')

    last, cnt = snapshot()
    log('開始監看，目前 %d 個檔案' % cnt)
    dirty_since = None
    retry_at = 0

    try:
        while True:
            time.sleep(POLL)
            now = time.time()
            cur, cnt = snapshot()

            if cur != last:
                last = cur
                dirty_since = now                 # 還在動，把倒數往後推
                continue

            due = dirty_since is not None and (now - dirty_since) >= DEBOUNCE
            retry_due = retry_at and now >= retry_at
            if not (due or retry_due):
                continue

            dirty_since = None
            retry_at = 0
            result = do_push()
            if result is None:
                pass                              # 沒有實質變更，安靜跳過
            elif result is True:
                pass
            else:
                what, detail = result
                log('%s，%d 秒後重試' % (what, int(RETRY)), '⚠')
                for ln in detail.splitlines()[:4]:
                    print('        ' + ln)
                retry_at = now + RETRY
    except KeyboardInterrupt:
        print('\n  已停止監看。\n')


if __name__ == '__main__':
    main()
