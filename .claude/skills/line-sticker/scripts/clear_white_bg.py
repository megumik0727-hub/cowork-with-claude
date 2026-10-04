"""白背景のまま書き出されたスタンプPNGの白を透過にする（上書き）
使い方: python3 clear_white_bg.py <png> [テキスト色 #4d3220] [テキストを探す範囲の下端y 150]
  Canvaでページを「レイヤー分解」すると背景が白い画像になり、背景透過で書き出しても白が残るときに使う。
  ・ほぼ白（暗さ12以下）の画素はすべて透過（文字の「日」「事」の内側も含む）
  ・白と接する輪郭は、白とのにじみを差し引いて半透明にする
  ・上部（y < 下端y）の、テキスト色と白の中間色は、テキスト色＋半透明に置き換える（細い隙間の白っぽさを消す）
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

path = sys.argv[1]
text = sys.argv[2] if len(sys.argv) > 2 else "#4d3220"
ymax = int(sys.argv[3]) if len(sys.argv) > 3 else 150

im = np.array(Image.open(path).convert("RGB")).astype(float)
h, w, _ = im.shape
bg = (255 - im.min(axis=2)) <= 12

br = np.array([int(text[i:i + 2], 16) for i in (1, 3, 5)], float)
v = 255 - br
k = (255 - im) @ v / (v @ v)
res = np.linalg.norm((255 - im) - k[..., None] * v, axis=2)
blend = (res < 10) & (k < 0.97) & ~bg
blend[ymax:, :] = False

a = np.ones((h, w))
a[bg] = 0
near = np.array(Image.fromarray((bg * 255).astype("uint8")).filter(ImageFilter.MaxFilter(5))) > 0
fr = near & ~bg & ~blend
a[fr] = np.clip((255 - im).max(axis=2)[fr] / 255.0, 0, 1)
rgb = im.copy()
sel = fr & (a > 0)
for c in range(3):
    rgb[..., c][sel] = np.clip((im[..., c][sel] - 255 * (1 - a[sel])) / a[sel], 0, 255)
a[blend] = np.clip(k[blend], 0, 1)
rgb[blend] = br
Image.fromarray(np.dstack([rgb, a * 255]).round().astype("uint8"), "RGBA").save(path, dpi=(96, 96))
print(f"{path}: 透過にしました")
