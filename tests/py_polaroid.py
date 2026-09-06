#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
戰報拍立得（makePolaroid）的像素驗證 —— v0.9.32 新增。

為什麼要有這支測試：
  v0.9.31 之前，戰報圖上的「主角」只是一顆 42px 的純色光球——沒有輪廓線、
  沒有眼睛。這張圖底下印著 #GooBlaster、是設計來給玩家分享到社群的，
  主角認不出來等於白丟品牌辨識度。這個問題從 makePolaroid() 寫出來那天
  就存在，**整套 52 支測試沒有任何一支碰過這個函式**，所以沒人發現。
  （tests/py_cjk_scan.py 只是剛好在原始碼裡掃到 btnSave 這個字串而已。）

驗收標準（全部用真的讀畫素驗證，不是讀原始碼）：
  1. 過關圖與失敗圖必須「不一樣」——表情真的有隨勝負改變
  2. 兩張圖的角色區域都必須有深色（#0d2430 系）畫素 = 臉真的畫上去了
  3. 兩張圖都必須有角色本體色（#6ff0e0 系）與白色外框 = 角色本體還在
  4. 深色畫素必須落在角色圓形範圍內，而且左右兩側都要有 = 是「兩隻眼睛」
     而不是隨便一塊黑

⚠ 這支測試刻意不檢查「笑眼是弧形、失敗是叉」這種形狀細節——形狀細節換個
  畫法就會誤報，會訓練所有人忽略紅字（AGENTS.md 第 3 節第 6 條）。
  硬門檻只有「臉存在、左右都有、勝負不同」。

用法：python3 tests/py_polaroid.py
"""
import http.server, socketserver, threading, functools, sys
from playwright.sync_api import sync_playwright

# ⚠ 逾時刻意放到 60 秒：這些 wait_for_function 都是「輪詢到條件成立為止」，
#   機器閒置時毫秒級就回來，長逾時不會讓測試變慢。但 run_tests.sh 是 43 支
#   平行跑，開 43 個 Chromium 時光是把頁面載完就可能超過 15 秒——
#   短逾時在那個情境下必定假紅字（AGENTS.md 第 3 節第 1 條）。


ROOT = "/home/claude/goo/game"
PORT = 8799

# 戰報圖尺寸與照片區座標（跟 makePolaroid() 裡的常數一致）
W, H = 560, 740
PX, PY, PW, PH = 34, 34, W - 68, 430
# 角色肖像的圓心與半徑（跟 drawHeroPortrait() 的呼叫參數一致）
CX, CY, CR = PX + PW // 2, PY + PH // 2 - 12, 78


class _Server(socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def serve():
    """回傳 (httpd, port)。埠被佔用時往上找一個能用的，不要讓測試因為
    上一輪留下的 TIME_WAIT socket 就整支失敗（那會是假紅字）。"""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    last = None
    for port in range(PORT, PORT + 20):
        try:
            httpd = _Server(("127.0.0.1", port), handler)
        except OSError as e:
            last = e
            continue
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return httpd, port
    raise last


JS_GRAB = """
async (win) => {
  // 直接叫 makePolaroid()，再把 dataURL 畫回一張 canvas 讀畫素
  const url = makePolaroid(win);
  const img = new Image();
  await new Promise((ok, no) => { img.onload = ok; img.onerror = no; img.src = url; });
  const c = document.createElement('canvas');
  c.width = img.width; c.height = img.height;
  const g = c.getContext('2d');
  g.drawImage(img, 0, 0);
  const d = g.getImageData(0, 0, c.width, c.height).data;
  return { w: c.width, h: c.height, data: Array.from(d) };
}
"""


def classify(px):
    """把一個畫素分類成 dark(臉) / body(角色本體) / outline(白框) / other"""
    r, g, b = px
    if r < 70 and 20 <= g < 90 and 30 <= b < 100:
        return "dark"          # #0d2430 系
    if r < 160 and g > 190 and b > 180:
        return "body"          # #6ff0e0 系
    if r > 215 and g > 235 and b > 230:
        return "outline"       # #e8fffb 系
    return "other"


def scan(shot):
    """回傳 (各色畫素數, 左眼畫素數, 右眼畫素數, 圓外深色數, 圓內深色座標集合)。

    ⚠ 圓「外」的深色畫素一律不採計：照片區背景是 130 顆隨機顏色的泡泡
    （makePolaroid 每次呼叫都重抽），裡面本來就會有深色的。只有角色圓形
    範圍內的畫素是確定性的（drawHeroPortrait 沒有任何隨機成分），
    所以所有硬性判斷都只看圓內。
    """
    w, d = shot["w"], shot["data"]
    counts = {"dark": 0, "body": 0, "outline": 0}
    dark_left = dark_right = 0
    dark_outside = 0
    face = set()
    for y in range(CY - CR - 6, CY + CR + 7):
        for x in range(CX - CR - 6, CX + CR + 7):
            i = (y * w + x) * 4
            kind = classify(d[i:i + 3])
            if kind in counts:
                counts[kind] += 1
            if kind == "dark":
                inside = (x - CX) ** 2 + (y - CY) ** 2 <= (CR + 4) ** 2
                if not inside:
                    dark_outside += 1
                else:
                    face.add((x, y))
                    if x < CX:
                        dark_left += 1
                    else:
                        dark_right += 1
    return counts, dark_left, dark_right, dark_outside, face


def main():
    httpd, port = serve()
    fails = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 420, "height": 820})
            pg.goto(f"http://127.0.0.1:{port}/index.html")
            pg.wait_for_function("typeof makePolaroid === 'function'", timeout=60000)
            # 需要一份活的 G（makePolaroid 會讀 G.lvIdx / G.L.n / G.t / G.P.lv / G.kills）
            pg.evaluate("()=>{ META={}; LV_IDX=0; start(); }")
            pg.wait_for_function("!!(G && G.running && G.P)", timeout=60000)

            shots = {}
            for label, win in (("win", True), ("lose", False)):
                shots[label] = pg.evaluate(JS_GRAB, win)
                sz = (shots[label]["w"], shots[label]["h"])
                if sz != (W, H):
                    fails.append(f"{label}：圖片尺寸 {sz} != 預期 {(W, H)}")

            faces = {}
            for label in ("win", "lose"):
                counts, dl, dr, out, face = scan(shots[label])
                faces[label] = face
                print(f"[{label}] 臉部深色（圓內）{len(face)}　左 {dl} / 右 {dr}"
                      f"　｜背景雜訊(圓外) {out}　本體 {counts['body']}　外框 {counts['outline']}")
                if len(face) < 150:
                    fails.append(f"{label}：角色圓內幾乎沒有深色畫素（{len(face)}）——臉沒畫上去")
                if dl < 40 or dr < 40:
                    fails.append(f"{label}：深色畫素沒有左右各一群（左 {dl}／右 {dr}）——不像兩隻眼睛")
                if counts["body"] < 3000:
                    fails.append(f"{label}：角色本體色太少（{counts['body']}）——本體不見了")
                if counts["outline"] < 500:
                    fails.append(f"{label}：白色外框太少（{counts['outline']}）——輪廓線不見了")

            # 表情必須真的有隨勝負改變。
            # ⚠ 這裡刻意「不」比整張圖：照片區的 130 顆泡泡是每次呼叫都重抽的隨機顏色
            #    與位置，整張圖比對永遠會不同 → 那個斷言等於沒有斷言（AGENTS.md
            #    第 3 節第 9 條：測試的輸入不能是機率的）。改成只比對角色圓內的
            #    深色畫素座標集合，那一塊是完全確定性的。
            if faces["win"] == faces["lose"]:
                fails.append("過關與失敗的臉部畫素完全相同——表情沒有隨勝負改變")
            else:
                only_win = len(faces["win"] - faces["lose"])
                only_lose = len(faces["lose"] - faces["win"])
                print(f"[diff] 臉部畫素差異：只在過關圖 {only_win} 個／只在失敗圖 {only_lose} 個")
                if only_win < 50 or only_lose < 50:
                    fails.append(f"兩種表情差異太小（{only_win}/{only_lose}）——看起來會像同一張臉")

            b.close()
    finally:
        httpd.shutdown()

    if fails:
        print("\n❌ 失敗：")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("\n✅ py_polaroid 全過")


if __name__ == "__main__":
    main()
