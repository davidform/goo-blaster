#!/bin/bash
# GOO BLASTER 一鍵測試。改完 index.html 就跑這支，全綠才算完成。
#
# 用法：
#   bash run_tests.sh            # 全部平行跑（最嚴苛條件）
#   bash run_tests.sh quick      # 只跑最關鍵的 5 支
#
# 需要：python3 + playwright + chromium、node + playwright

set -u
REPO="$(cd "$(dirname "$0")" && pwd)"
GAME_DIR="${GOO_GAME_DIR:-/home/claude/goo/game}"   # 測試用的 HTTP server 根目錄
LOG="${TMPDIR:-/tmp}/goo-tests"

mkdir -p "$GAME_DIR" "$LOG"
rm -rf "${LOG:?}"/*
cp "$REPO/index.html" "$GAME_DIR/index.html" || { echo "找不到 index.html"; exit 1; }

echo "版本：$(grep -o "BUILD='[^']*'" "$REPO/index.html" | head -1)"
echo "測試根目錄：$GAME_DIR"

# 語法先過，不然後面 33 支都會用同一個原因失敗
if ! node "$REPO/tests/syntax_check.js"; then echo "❌ 語法檢查沒過"; exit 1; fi

if [ "${1:-}" = "quick" ]; then
  PY="py_test9 py_ab_base py_bullet_density py_i18n py_cjk_scan py_v0927 py_native_store"
  JS=""
else
  PY="py_50levels py_ab_base py_audit_fixes py_balance py_boss_skin py_boss_time \
      py_btn_conflict py_bullet_density py_card_pool py_cards_fix py_cjk_scan \
      py_i18n py_i18n_new py_lang_attr py_laser_boss py_layout_fit py_level_audit \
      py_meta py_range_music py_spawn py_touch_real py_ui_edge py_ui_fixes \
      py_v0926_edge py_v0927 py_native_store py_lv5_stress py_test9"
  JS="test5 test6 test8 test9 test10 test11 testaudio testlead"
  # ⚠ 效能測試不能跟其他 36 支搶 CPU：平行時整台機器只剩個位數 FPS，
  #   連「有同伴 vs 沒同伴」的相對比較都失去解析度（2.6 fps vs 1.6 fps
  #   在 8 秒裡只差兩幀）。所以它排在平行批次「之後」單獨跑。
  SOLO="py_v0927_perf"
  # 診斷型測試（跑很久、要嚴格的同批次對照）不進預設套件，需要時單獨跑：
  #   py_v0927_ab_lv1（第1關 A/B）／py_lv5_diag／py_lv5_growth／py_card_pool
fi

cd "$REPO"
for t in $PY; do
  ( timeout 900 python3 "tests/$t.py" > "$LOG/$t.log" 2>&1; echo "$? $t" >> "$LOG/RESULT" ) &
done
for t in $JS; do
  ( timeout 900 node "tests/$t.js" > "$LOG/$t.log" 2>&1; echo "$? $t" >> "$LOG/RESULT" ) &
done
wait

for t in ${SOLO:-}; do
  echo "（單獨跑效能測試 $t，避免被其他測試搶 CPU）"
  timeout 900 python3 "tests/$t.py" > "$LOG/$t.log" 2>&1; echo "$? $t" >> "$LOG/RESULT"
done

echo
echo "========== 結果 =========="
sort -k2 "$LOG/RESULT"
echo "=========================="
FAILED=$(grep -cv '^0 ' "$LOG/RESULT" || true)
if [ "$FAILED" -gt 0 ]; then
  echo "❌ 失敗 $FAILED 支："
  grep -v '^0 ' "$LOG/RESULT"
  echo "詳細記錄在 $LOG/"
  echo
  echo "⚠ 先確認不是「平行負載造成的偶發逾時」——"
  echo "  單獨重跑一次那一支；若單獨跑會過，代表測試本身寫了固定 sleep，"
  echo "  請照 AGENTS.md 第 3 節把它改成輪詢，而不是放寬逾時了事。"
  exit 1
fi
echo "✅ 全部通過（$(wc -l < "$LOG/RESULT") 支）"
