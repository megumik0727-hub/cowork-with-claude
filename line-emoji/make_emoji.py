"""腰長どうぶつ LINE絵文字の試作生成スクリプト（180x180 透過PNG）"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

S = 4                      # supersampling
W = 180 * S
FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else "fonts"
KO = os.path.join(FONT_DIR, "gaegu/files/gaegu-korean-700-normal.woff")
JA = os.path.join(FONT_DIR, "kosugi-maru/files/kosugi-maru-japanese-400-normal.woff")
OUT = os.path.join(os.path.dirname(__file__), "prototype")

LINE = (107, 74, 58, 255)
BODY = (255, 246, 228, 255)
EAR = (236, 196, 156, 255)
CHEEK = (248, 170, 185, 255)
PATCH = (255, 222, 228, 255)
LW = 6 * S                 # outline width
TOP, BOT = 56 * S, 144 * S # body band (shared by all tiles so they connect)


def s(*v):
    return [x * S for x in v]


def canvas():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def band(d, x0, x1):
    d.rectangle([x0, TOP, x1, BOT], fill=BODY)
    d.line([x0, TOP, x1, TOP], fill=LINE, width=LW)
    d.line([x0, BOT, x1, BOT], fill=LINE, width=LW)


def leg(d, x):
    d.rounded_rectangle([x, BOT - 8 * S, x + 22 * S, BOT + 22 * S], 10 * S, fill=BODY, outline=LINE, width=LW)
    d.rectangle([x + LW, BOT - 10 * S, x + 22 * S - LW, BOT - 2 * S], fill=BODY)


def head():
    im = canvas(); d = ImageDraw.Draw(im)
    band(d, 70 * S, W)
    leg(d, 100 * S)
    d.ellipse(s(14, 22, 112, 116), fill=BODY, outline=LINE, width=LW)      # head
    d.ellipse(s(4, 30, 40, 96), fill=EAR, outline=LINE, width=LW)          # ear
    d.ellipse(s(66, 52, 78, 66), fill=LINE)                                # eye
    d.ellipse(s(40, 50, 52, 64), fill=LINE)
    d.ellipse(s(52, 70, 64, 78), fill=LINE)                                # nose
    d.arc(s(46, 70, 58, 84), 20, 160, fill=LINE, width=3 * S)              # mouth
    d.arc(s(58, 70, 70, 84), 20, 160, fill=LINE, width=3 * S)
    d.ellipse(s(76, 70, 92, 80), fill=CHEEK)
    d.ellipse(s(26, 70, 42, 80), fill=CHEEK)
    return im


def tail():
    im = canvas(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([-40 * S, TOP - LW // 2, 150 * S, BOT + LW // 2], 44 * S, fill=BODY, outline=LINE, width=LW)
    leg(d, 110 * S)
    d.arc(s(140, 40, 172, 86), 170, 330, fill=LINE, width=LW)              # tail
    return im


def belly(text, kana=None):
    im = canvas(); d = ImageDraw.Draw(im)
    band(d, 0, W)
    d.rounded_rectangle(s(12, 68, 168, 132), 30 * S, fill=PATCH)
    n = len(text)
    size = {1: 62, 2: 50, 3: 40}[n] * S
    if kana:
        size = min(int(size * 0.85), 44 * S)
    f = ImageFont.truetype(KO, size)
    cy = (93 if kana else 100) * S
    d.text((W // 2, cy), text, font=f, fill=LINE, anchor="mm")
    if kana:
        fk = ImageFont.truetype(JA, 14 * S)
        d.text((W // 2, 121 * S), kana, font=fk, fill=(170, 110, 120, 255), anchor="mm")
    return im


def save(im, name):
    im.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, name))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    words = [("대박", "テバク"), ("헐", "ホル"), ("진짜", "チンチャ"), ("화이팅", "ファイティン"),
             ("사랑해", "サランヘ"), ("고마워", "コマウォ"), ("안녕", "アンニョン"), ("최고", "チェゴ")]
    save(head(), "head.png"); save(tail(), "tail.png")
    for i, (w, k) in enumerate(words, 1):
        save(belly(w), f"ko_{i:02d}.png")
        save(belly(w, k), f"kana_{i:02d}.png")
    # LINE上での見え方を確認するプレビュー
    rows = [["head", "ko_01", "tail"], ["head", "ko_04", "ko_05", "tail"],
            ["head", "kana_02", "kana_03", "tail"], ["head", "kana_06", "tail"]]
    prev = Image.new("RGBA", (180 * 4 + 40, 180 * len(rows) + 40), (222, 228, 238, 255))
    for r, row in enumerate(rows):
        for c, n in enumerate(row):
            t = Image.open(os.path.join(OUT, n + ".png"))
            prev.alpha_composite(t, (20 + c * 180, 20 + r * 180))
    prev.save(os.path.join(OUT, "_preview.png"))
