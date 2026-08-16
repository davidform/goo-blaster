#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOO BLASTER 本機測試伺服器
把這個檔案放在專案資料夾（index.html 旁邊），執行它，
手機連同一個 Wi-Fi 就能用網址開啟遊戲。

重點：這個伺服器會強制關閉快取，所以你改完 index.html 之後，
手機重新整理就一定拿到最新版，不會測到舊的。
"""
import http.server, socketserver, socket, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = os.path.dirname(os.path.abspath(__file__))


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # 沒有這幾行，手機會一直讀到快取裡的舊版本
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        # 只印出真正的請求，不要洗版
        sys.stdout.write("  %s\n" % (fmt % args))


def lan_ips():
    """列出這台電腦在區域網路上的 IP（可能有多張網卡）"""
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))          # 不會真的送封包，只是問系統走哪張網卡
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass
    return ips


def main():
    if not os.path.exists(os.path.join(ROOT, "index.html")):
        print("\n  ⚠ 這個資料夾裡找不到 index.html")
        print("     請把 start-server.py 放到 index.html 旁邊再執行\n")
        input("  按 Enter 關閉...")
        return

    ips = lan_ips()
    bar = "═" * 52
    print("\n╔" + bar + "╗")
    print("║  GOO BLASTER 本機伺服器已啟動" + " " * 22 + "║")
    print("╠" + bar + "╣")
    print("║  桌機自己測：                                      ║")
    print("║    http://localhost:%-31d║" % PORT)
    print("║" + " " * 52 + "║")
    if ips:
        print("║  手機測（要連同一個 Wi-Fi）：                      ║")
        for ip in ips:
            url = "http://%s:%d" % (ip, PORT)
            print("║    %-48s║" % url)
    else:
        print("║  找不到區域網路 IP，請確認有連上 Wi-Fi              ║")
    print("║" + " " * 52 + "║")
    print("║  快取已停用 → 改完檔案，手機重新整理就是新版        ║")
    print("║  要停止：在這個視窗按 Ctrl + C                      ║")
    print("╚" + bar + "╝\n")
    print("  連線紀錄：")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), NoCacheHandler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        print("\n  ⚠ 連接埠 %d 被佔用了（%s）" % (PORT, e))
        print("     換一個：在命令列執行  python start-server.py 8001\n")
        input("  按 Enter 關閉...")
    except KeyboardInterrupt:
        print("\n  已停止。\n")


if __name__ == "__main__":
    main()
