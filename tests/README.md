# Browser test execution

The game remains a single offline HTML file. Playwright is a development dependency only.

Windows PowerShell setup (Python and Node must already be installed):

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install playwright==1.62.0
npm install --prefix _private/test-node --no-audit --no-fund playwright@1.62.0
$env:NODE_PATH = (Join-Path (Get-Location) '_private/test-node/node_modules')
$env:GOO_BROWSER_CHANNEL = 'msedge'
.venv/Scripts/python.exe run_tests.py --jobs 4 --label baseline
```

This uses installed Microsoft Edge with isolated browser profiles. It does not use personal tabs or logins.
For Playwright Chromium, install it with `python -m playwright install chromium` using the same Python environment and omit `GOO_BROWSER_CHANNEL`.

`run_tests.py` reads the default suite names from `run_tests.sh`; it does not silently omit tests.
It runs the performance test only after the concurrent batch. Do not run another build or stress job during that performance test.
Use `--jobs 48 --label stress` for the full concurrent stress batch, or `--only py_test9 py_ab_base` for focused reruns.
Each invocation writes separate logs and `results.json` under `_private/test-runs/`, with the tested game's SHA256.
Exit 124 means a timeout; Windows timeout cleanup targets only that test's process tree.
Failures printed by legacy Python tests and nonempty Node `errs` also fail the runner.
Some legacy Node tests are diagnostic measurements, so a successful process is not a substitute for inspecting their results.

Tests in the default suite now resolve the game directory from `GOO_ROOT`, then `GOO_GAME_DIR`, then the repository location. Older optional diagnostics may still contain Linux-specific paths.
The v0.9.20 A/B baseline is extracted from historical commit `50b166b`; shallow clones must contain that commit.
The legacy shell runner is retained for existing Linux workflows; the Python runner is the portable entry point.

`py_test9.py` is the novice gameplay gate: stage 1 must be cleared. A perfect/no-damage clear is a reported observation, not a probabilistic pass/fail requirement. The test now returns a failing exit code for a missed clear or browser error.

Before itch.io publication, complete the required rounds and pass the SHA256 from the tested build:

```powershell
node tools/publish_itch.cjs --push --verified-sha256 <tested-sha256>
```

That parameter pins the bytes; it does not itself prove tests passed. Preserve and review the test logs first.
The default command without `--push` only prepares files locally.

## 其他

| 檔案 | 驗什麼 |
|---|---|
| `test5.js` | 多點觸控、加速鍵冷卻、愛心與死亡、慈悲無敵、實戰闖關、FPS |
| `test6.js` | 音效系統、果凍覆蓋率→傷害、升級卡池、遊戲速度、各卡機制 |
| `test8.js` | 關卡數值曲線、寶箱生成距離與七種效果 |
| `test10.js` | 模擬 TouchList 不可迭代、Web Audio 接線圖 |
| `test11.js` | 舊存檔殘留、循序解鎖、endGame 重入、觸控漏事件自我恢復 |
| `testaudio.js` | 攔截 AudioContext 統計音樂排程速率 |
| `testlead.js` | 相機前瞻平滑度 |
| `prof3.js` | 真實遊戲峰值 FPS 與 GPU 資訊 |

## ⚠ 模擬環境的極限

**合成的 `TouchEvent` 在 Chromium 裡的行為和真機不同。**
用 `new TouchEvent({changedTouches:[t]})` 建出來的物件，
無法真實重現 iOS Safari 的 TouchList 行為。

曾經因此誤以為證明了某個假設 —— 實際上沒有。
做行動裝置相容性驗證時要意識到這個極限，最終還是要真機測試。
