"""Canvaから書き出したPNG一式を、LINE申請用のファイル名に並べ替えてZIPにする
使い方: python3 package.py <Canvaのダウンロードzipまたはフォルダ> <出力zip>
  画像サイズで振り分ける: 370x320→スタンプ（ファイル名の数字順に01〜NN）、240x240→main、96x74→tab。
  それ以外のサイズ（作業用の白紙ページなど）は無視する。
"""
import io, os, re, sys, zipfile
from PIL import Image

src, out = sys.argv[1], sys.argv[2]


def entries():
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.lower().endswith(".png") and not os.path.basename(n).startswith("."):
                    yield n, z.read(n)
    else:
        for n in os.listdir(src):
            if n.lower().endswith(".png"):
                with open(os.path.join(src, n), "rb") as f:
                    yield n, f.read()


def key(name):
    nums = re.findall(r"\d+", os.path.basename(name))
    return int(nums[-1]) if nums else 0


stickers, main, tab = [], None, None
for name, data in entries():
    size = Image.open(io.BytesIO(data)).size
    if size == (370, 320):
        stickers.append((key(name), name, data))
    elif size == (240, 240):
        main = data
    elif size == (96, 74):
        tab = data
    else:
        print(f"skip {name} {size}")

stickers.sort()
if main is None or tab is None:
    sys.exit("main（240x240）または tab（96x74）が見つかりません")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for i, (_, name, data) in enumerate(stickers, 1):
        z.writestr(f"{i:02d}.png", data)
        print(f"{i:02d}.png <- {name}")
    z.writestr("main.png", main)
    z.writestr("tab.png", tab)
print(f"{out}: スタンプ{len(stickers)}個 + main + tab")
