"""腰長おじさん LINE絵文字（180x180 透過PNG）
頭（001）＋腹巻き（文字）＋足（002）をつなげて、おじさん構文を組み立てる。
使い方: python3 make_ojisan.py <フォントのディレクトリ>
"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

S = 4
W = 180 * S
FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else "fonts"
JA = os.path.join(FONT_DIR, "kosugi-maru/files/kosugi-maru-japanese-400-normal.woff")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ojisan_set")

LINE = (92, 64, 51, 255)
SKIN = (255, 214, 186, 255)
CHEEK = (250, 150, 150, 255)
SHIRT = (255, 255, 255, 255)
HARA = (246, 205, 92, 255)       # 腹巻き
HARA_RIB = (226, 180, 70, 255)
PANTS = (170, 205, 240, 255)
SANDAL = (150, 105, 80, 255)
INK = (120, 60, 40, 255)
RED = (230, 60, 60, 255)
BLUE = (90, 160, 230, 255)
PINK = (240, 110, 140, 255)
LW = 6 * S
TOP, BOT = 56 * S, 144 * S       # 胴体の帯（全パーツ共通）

LETTERS = "アイウオカクサシスタチツテトナネハマミメヤヨリレロンガゴジダバャッー！？💦♡"


def s(*v):
    return [x * S for x in v]


def canvas():
    return Image.new("RGBA", (W, W), (0, 0, 0, 0))


def band(d, x0, x1, fill):
    d.rectangle([x0, TOP, x1, BOT], fill=fill)
    d.line([x0, TOP, x1, TOP], fill=LINE, width=LW)
    d.line([x0, BOT, x1, BOT], fill=LINE, width=LW)


def haramaki(d, x0, x1):
    band(d, x0, x1, HARA)
    for y in (TOP + 9 * S, BOT - 9 * S):        # ゴム編みの縁
        d.line([x0, y, x1, y], fill=HARA_RIB, width=3 * S)
    for x in range(x0 + 10 * S, x1, 20 * S):    # 縦のリブ
        d.line([x, TOP + 16 * S, x, BOT - 16 * S], fill=HARA_RIB + (0,)[:0], width=2 * S)


def head():
    im = canvas(); d = ImageDraw.Draw(im)
    band(d, 96 * S, 150 * S, SHIRT)                  # ランニングシャツ
    d.line(s(118, 56, 108, 100), fill=LINE, width=3 * S)  # 肩ひも
    haramaki(d, 150 * S, W)
    d.line(s(150, 56, 150, 144), fill=LINE, width=LW)
    # 頭
    d.ellipse(s(4, 66, 26, 96), fill=SKIN, outline=LINE, width=LW)       # 耳
    d.ellipse(s(14, 20, 112, 140), fill=SKIN, outline=LINE, width=LW)
    d.pieslice(s(14, 60, 40, 100), 120, 240, fill=(80, 70, 70, 255))     # 横の髪
    for x in (54, 62, 70):                                               # 頭頂の3本毛
        d.arc(s(x - 6, 6, x + 6, 30), 200, 340, fill=LINE, width=3 * S)
    d.arc(s(40, 34, 86, 50), 200, 340, fill=(220, 160, 140, 255), width=2 * S)  # おでこのしわ
    d.arc(s(34, 64, 52, 78), 200, 340, fill=LINE, width=4 * S)           # にっこり目
    d.arc(s(70, 64, 88, 78), 200, 340, fill=LINE, width=4 * S)
    d.ellipse(s(26, 80, 44, 92), fill=CHEEK)
    d.ellipse(s(80, 80, 98, 92), fill=CHEEK)
    d.ellipse(s(54, 78, 68, 90), fill=(245, 180, 160, 255), outline=LINE, width=2 * S)  # 鼻
    d.chord(s(44, 88, 78, 104), 180, 360, fill=(80, 70, 70, 255))        # ひげ
    d.arc(s(52, 98, 70, 112), 20, 160, fill=LINE, width=3 * S)           # 口
    return im


def feet():
    im = canvas(); d = ImageDraw.Draw(im)
    haramaki(d, 0, 22 * S)
    d.rounded_rectangle([22 * S, TOP - LW // 2, 104 * S, BOT + LW // 2], 20 * S, fill=PANTS, outline=LINE, width=LW)
    d.rectangle([22 * S, TOP + LW // 2, 40 * S, BOT - LW // 2], fill=PANTS)
    d.line(s(22, 56, 22, 144), fill=LINE, width=LW)
    d.line(s(64, 100, 104, 100), fill=LINE, width=3 * S)                  # 股の線
    for y in (62, 104):                                                    # 足
        d.rounded_rectangle(s(100, y, 150, y + 30), 14 * S, fill=SKIN, outline=LINE, width=LW)
        d.rounded_rectangle(s(146, y - 6, 160, y + 36), 6 * S, fill=SANDAL, outline=LINE, width=4 * S)
    return im


def drop(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r // 2, cx + r, cy + r * 3 // 2], fill=fill)
    d.polygon([(cx - r + S, cy), (cx + r - S, cy), (cx, cy - r * 3 // 2)], fill=fill)


def heart(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx, cy], fill=fill)
    d.ellipse([cx, cy - r, cx + r, cy], fill=fill)
    d.polygon([(cx - r + S, cy - r // 3), (cx + r - S, cy - r // 3), (cx, cy + r)], fill=fill)


def belly(ch):
    im = canvas(); d = ImageDraw.Draw(im)
    haramaki(d, 0, W)
    c = W // 2
    if ch == "♡":
        heart(d, c, 96 * S, 30 * S, PINK)
    elif ch == "💦":
        drop(d, c - 16 * S, 84 * S, 14 * S, BLUE)
        drop(d, c + 18 * S, 106 * S, 12 * S, BLUE)
    else:
        color = RED if ch == "！" else INK
        f = ImageFont.truetype(JA, 66 * S)
        dy = {"ッ": 8, "ャ": 8}.get(ch, 0) * S
        d.text((c, 100 * S + dy), ch, font=f, fill=color, anchor="mm",
               stroke_width=3 * S, stroke_fill=color)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = {"head": head(), "feet": feet()}
    for ch in LETTERS:
        tiles[ch] = belly(ch)
    order = ["head", "feet"] + list(LETTERS)
    small = {}
    for n, key in enumerate(order, 1):
        small[key] = tiles[key].resize((180, 180), Image.LANCZOS)
        small[key].save(os.path.join(OUT, f"{n:03d}.png"))
    tab = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
    tab.alpha_composite(tiles["head"].crop((0, 0, 130 * S, 150 * S)).resize((64, 74), Image.LANCZOS), (16, 0))
    tab.save(os.path.join(OUT, "tab.png"))

    T = 72
    phrases = ["オツカレサマ💦", "ナンチャッテ♡", "ゲンキカナ？", "アリガトウ！", "ゴメンネ💦",
               "オハヨー！", "アイタイナ♡", "ヨロシクネ！", "オヤスミ♡"]
    phrases = [p for p in phrases if all(c in LETTERS for c in p)]
    width = max(len(p) for p in phrases) + 2
    prev = Image.new("RGBA", (T * width + 24, T * len(phrases) + 24), (222, 228, 238, 255))
    for r, p in enumerate(phrases):
        for c, key in enumerate(["head"] + list(p) + ["feet"]):
            prev.alpha_composite(small[key].resize((T, T), Image.LANCZOS), (12 + c * T, 12 + r * T))
    prev.save(os.path.join(OUT, "_preview_phrases.png"))
    T = 90
    sheet = Image.new("RGBA", (T * 8 + 30, T * 5 + 30), (255, 255, 255, 255))
    for n, key in enumerate(order):
        sheet.alpha_composite(small[key].resize((T, T), Image.LANCZOS), (15 + n % 8 * T, 15 + n // 8 * T))
    sheet.save(os.path.join(OUT, "_preview_all40.png"))
    print(len(order), "tiles;", "phrases:", phrases)


if __name__ == "__main__":
    main()
