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
`--jobs 2` or `--jobs 4`: the previous 48-worker attempt made the host unresponsive and timed out.
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
## Soft-world UI (v0.9.41)

`py_soft_ui.py` is included in the default suite. It checks actual navigation,
selected-stage and shop-scroll preservation, settings entry points, all 11
languages at four viewport sizes, title contrast and zero-meta gameplay.
Screenshots are written to `_private/test-artifacts/soft-*.png`.

```powershell
$env:GOO_BROWSER_CHANNEL='msedge'
$env:GOO_UI_CPU='4'
.venv/Scripts/python.exe tests/py_soft_ui.py
Remove-Item Env:GOO_UI_CPU
```

`py_art_perf.py` is a standalone diagnostic comparing the committed v0.9.40
source (`8c5bebd`) to the working game with fixed seeds, three alternating
single-page rounds and three paired rounds. Run it alone. Timestamped evidence
goes to `_private/test-artifacts/art-perf-*/results.json`; it does not replace
`py_v0927_perf`, the full-parallel stress gate or physical-device testing.

## Audio (v0.9.42)

`py_audio_quality.py` is in the default suite. It uses real Web Audio nodes to
check weapon coexistence, Boss music transitions, stop/start races, mute,
source cleanup and isolation from the gameplay random stream. Set
`GOO_AUDIO_CPU=4` for the focused CPU-throttled run.

`python tests/render_audio_samples.py --label audio-review` writes seven stereo
WAVs and signal/source-count JSON under `_private/test-artifacts/audio-review`.
It injects a scheduling hook into a disposable copy and renders the actual
instruments through OfflineAudioContext; it never edits the game. It fails on
non-finite/clipped/silent output, but does not grade taste or replace phone listening.
Omit `--label` to use a timestamp and preserve earlier samples.
# v0.9.43 語境與長翻譯

`py_revive_collision.py`（v0.9.44）已加入預設套件。用真正敵彈碰撞觸發蠟燭復活，驗證清空敵彈後的剩餘索引不會讓遊戲拋例外；也涵蓋普通受傷、護盾與死亡。`GOO_REVIVE_CPU=4` 可執行 CPU 節流版本。

`py_l10n_context.py` 已加入預設套件：11 語言的實際 Boss 名稱、每五關章節規則、日韓地面膠體術語，以及 320×480 從說明文字開始的真實觸控捲動。可設 `GOO_L10N_CPU=4` 做 CPU 節流。截圖／JSON 在 `_private/test-artifacts/l10n-*`。鍵完整與排版通過不代表母語潤稿完成。

`python tests/check_runner_checkpoint.py` 單獨驗證 Windows 報告檔被讀取鎖定時的原子替換重試：使用真實 Windows handle，並非只模擬例外。其他平台明確 SKIP；這是測試工具的診斷，不計入遊戲瀏覽器套件數。

## 翻滾保護（v0.9.45）

`py_dash_protection.py`驗各來源保護及真實雙指逃生後的敵彈；`GOO_DASH_CPU=4`做節流驗證。

## 大型目標（v0.9.46）

`py_visible_target.py`驗橫豎畫面四邊的實際鎖定／開火，以及完全離屏、小怪與距離排除；`GOO_TARGET_CPU=4`可節流。

## 絕對效能量測（2026-09-09）

`py_v0927_perf.py`的兩局同批A/B保留<20%同伴損失門檻；30FPS門檻改由同場景的三輪單局平均檢查，並確認沒有其他browser context殘留。原雙局絕對門檻失敗紀錄不改写。`py_art_perf.py --baseline <commit>`可比較任意已提交來源，暖機與音訊啟動條件與主效能測試一致，另記錄場景物件數與遊戲時間。

## 射程收益（v0.9.47）

`py_range_reach.py`驗36種混合強化、真實命中／飛行距離、同伴及12種最大步長射擊；`py_range_ui.py`驗11語言商店下一級／滿級及兩階卡片。可設`GOO_RANGE_CPU=4`。兩支都在預設完整套件。

`GOO_BROWSER_CHANNEL=msedge`環境下執行`python tests/diagnose_progression.py 1 6 7 9 10 30 50`，以真實遊戲迴圈／觸控／卡片比較零強化、逐局賺幣購買與滿級。預設reactive；`GOO_BOT_POLICY=engaged`加上接近Boss的操作參考。固定種子與重播、遊戲／工具SHA、clear/defeat/unfinished分離，未完成直接報錯。預設時間戳檔案避免覆蓋；`GOO_BALANCE_OUTPUT`可指定輸出名。這是診斷，不是人類勝率、FPS測試或預設硬性驗收門檻；不要與效能測試同時跑。
