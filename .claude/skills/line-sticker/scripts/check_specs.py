"""LINEスタンプ申請前の書き出し画像チェック
使い方: python3 check_specs.py <書き出したPNGのフォルダ>
  01.png〜NN.png（スタンプ）、main.png（メイン）、tab.png（タブ）を想定
"""
import glob, os, sys
from PIL import Image

LIMITS = {"main": (240, 240, True), "tab": (96, 74, True)}   # (幅, 高さ, 完全一致)
STICKER = (370, 320)
COUNTS = {8, 16, 24, 32, 40}
MARGIN = 10

d = sys.argv[1]
ng = 0
stickers = sorted(p for p in glob.glob(os.path.join(d, "*.png")) if os.path.basename(p)[:2].isdigit())
if len(stickers) not in COUNTS:
    print(f"NG 個数 {len(stickers)}（8/16/24/32/40 のどれか）"); ng += 1
for p in glob.glob(os.path.join(d, "*.png")):
    name = os.path.splitext(os.path.basename(p))[0]
    im = Image.open(p)
    w, h = im.size
    msgs = []
    if os.path.getsize(p) > 1024 * 1024:
        msgs.append("1MB超")
    if im.mode != "RGBA":
        msgs.append(f"透過なし({im.mode})")
    if name in LIMITS:
        lw, lh, _ = LIMITS[name]
        if (w, h) != (lw, lh):
            msgs.append(f"サイズ {w}x{h}（{lw}x{lh}）")
    else:
        if w > STICKER[0] or h > STICKER[1]:
            msgs.append(f"サイズ超過 {w}x{h}")
        if w % 2 or h % 2:
            msgs.append(f"奇数サイズ {w}x{h}")
        if im.mode == "RGBA":
            bb = im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox()
            if bb and (bb[0] < MARGIN or bb[1] < MARGIN or w - bb[2] < MARGIN or h - bb[3] < MARGIN):
                msgs.append(f"余白不足 bbox={bb}")
            corners = [im.getpixel(c)[3] for c in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]]
            if any(corners):
                msgs.append("四隅が不透明（背景の消し残し）")
    if msgs:
        ng += 1
        print("NG", os.path.basename(p), " / ".join(msgs))
print("OK" if ng == 0 else f"{ng}件の要修正")
