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
Use `--only py_test9 py_ab_base` for focused reruns. On this 16 GB Surface, retain
`--jobs 4`: the previous 48-worker attempt made the host unresponsive and timed out.
Do not repeat that configuration on this machine. Four workers are a previously
completed operating point, not a measured maximum or a substitute for the required
full-concurrency stress round. That round remains incomplete and needs a more capable
test host before release acceptance can be claimed.
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

For performance measurement diagnostics, run the following alone, after other test
and build processes finish:

```powershell
$env:GOO_BROWSER_CHANNEL = 'msedge'
.venv/Scripts/python.exe tests/py_perf_capacity.py
```

This reuses the existing worst scene and records three rounds of single-page and
paired-page measurements, alternating their order. It saves timestamped JSON with
the game hash, actual frames/time, ally counts, page errors, and GPU feature status.
The fixed sampling window measures FPS; game readiness is checked by polling.
These figures diagnose test-host contention; they neither change the original
30 FPS / less-than-20% loss gates nor establish actual phone performance.

`tests/py_render_profile.py` is a separate, single-page diagnostic. Run it alone
with the same environment. It compares the unchanged game, shadowBlur disabled,
and DPR1 in disposable contexts, with three alternating rounds. Timestamped JSON
records frame gaps, draw/update call durations, actual canvas sizes, object counts,
and page errors. Call durations exclude asynchronous rendering/compositing work;
neither reduced-resolution measurements nor these experimental switches modify
the game or replace acceptance tests. See docs-15-performance-and-art-direction.md
for observed variability and the pending Pixel investigation.

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

## GitHub Pages deployment gate

`.github/workflows/pages.yml` checks pushes to `main`, PRs targeting `main`,
and manual runs. `validate` must succeed before `deploy`; only a non-PR run on
`main` may upload/deploy the Pages artifact. PRs and other manually selected
branches cannot deploy. Concurrency is scoped to the ref, so a PR does not cancel
an active main deployment. Only the deploy job receives Pages/OIDC write access.

The validation job runs these in order, without `continue-on-error` or retries:

1. `node tests/syntax_check.js` — parses the inline game JavaScript.
2. `node tests/check_release_docs.cjs` — checks the existing eight documentation
   invariants, including bilingual policy content and synchronized instructions.
3. Install Python 3.12, pinned Playwright from `tests/requirements-ci.txt`, and only
   Chromium headless shell (`python -m playwright install --with-deps --only-shell chromium`).
4. Stage the existing website allowlist into `_site`, then run
   `GOO_ROOT="$PWD/_site" python tests/py_release_smoke.py`.

The smoke test uses one isolated browser profile and one page at a time, runs
with network offline and CPU throttled 4x, opens Home → Adventure → Play, and
polls until the real game loop has advanced at least three game seconds. It then
seeds progress/coins/upgrades via `saveGame()`, closes the browser, and verifies
those values and stage selection after a real restart. Page errors and observed
HTTP(S) requests fail the test. This is a `file://` payload check, not an HTTP
hosting, service-worker, or production Pages availability check. It does not
prove that progress can be earned through a complete level.

A 3-minute smoke-step timeout and 10-minute job timeout bound resource use;
there is no parallel browser matrix, FPS gate, or full-suite run in this workflow.
Logs, game SHA256, and the existing smoke screenshots are retained for seven days.
The `tee` pipeline uses `pipefail`, so saving logs cannot turn a failed test green.
Only after success is the **same tested `_site`** uploaded as the Pages artifact;
the deploy job does not rebuild or check out different bytes.

These are basic deployment safeguards, **not AGENTS.md's three-round acceptance**.
Game modifications still require the complete existing suite, targeted edge cases,
and the prescribed stress round; performance tests must run separately. All-level
balance, 11-language layout, extended gameplay/save migration/garden behavior,
real touch/audio, phone performance, Android/iOS packaging, and real-device save
persistence remain outside this CI gate. Neither a green PR nor a successful
Pages deployment claims those checks passed. `AGENTS.md`, `CLAUDE.md`, `run_tests.sh`,
and the game BUILD are unchanged by the CI work.
