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


# ---- ひらがなセット（頭・しっぽ＋38文字＝40個） ----
HIRAGANA = "あいうえおかきくさしすたつてとなにねのはまみむめやよりれろんがごだでばっー♡"
INK = [(232, 106, 125, 255), (90, 140, 210, 255), (110, 170, 110, 255),
       (160, 120, 200, 255), (240, 150, 70, 255)]


def heart(d, cx, cy, r, fill):
    d.ellipse([cx - r, cy - r, cx, cy], fill=fill)
    d.ellipse([cx, cy - r, cx + r, cy], fill=fill)
    d.polygon([(cx - r + S, cy - r // 3), (cx + r - S, cy - r // 3), (cx, cy + r)], fill=fill)


def belly_hira(ch, color):
    im = canvas(); d = ImageDraw.Draw(im)
    band(d, 0, W)
    d.ellipse(s(48, 58, 132, 142), fill=PATCH)
    if ch == "♡":
        heart(d, W // 2, 96 * S, 26 * S, INK[0])
    else:
        f = ImageFont.truetype(JA, 62 * S)
        dy = {"っ": 10, "ー": 0}.get(ch, 0) * S
        d.text((W // 2, 100 * S + dy), ch, font=f, fill=color, anchor="mm",
               stroke_width=3 * S, stroke_fill=color)
    return im


def build_hiragana_set():
    out = os.path.join(os.path.dirname(__file__), "hiragana_set")
    os.makedirs(out, exist_ok=True)
    tiles = {"head": head(), "tail": tail()}
    for i, ch in enumerate(HIRAGANA):
        tiles[ch] = belly_hira(ch, INK[i % len(INK)])
    order = ["head", "tail"] + list(HIRAGANA)   # 001=頭, 002=しっぽ, 003以降=文字
    small = {}
    for n, key in enumerate(order, 1):
        small[key] = tiles[key].resize((180, 180), Image.LANCZOS)
        small[key].save(os.path.join(out, f"{n:03d}.png"))
    tab = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
    tab.alpha_composite(tiles["head"].resize((74, 74), Image.LANCZOS), (11, 0))
    tab.save(os.path.join(out, "tab.png"))
    # フレーズの見え方プレビュー
    phrases = ["ありがとう", "だいすき♡", "さみしい", "まってて", "あとで", "いえいえ", "おつかれ", "いってきます"]
    T = 90
    width = max(len(p) for p in phrases) + 2
    prev = Image.new("RGBA", (T * width + 30, T * len(phrases) + 30), (222, 228, 238, 255))
    for r, p in enumerate(phrases):
        for c, key in enumerate(["head"] + list(p) + ["tail"]):
            prev.alpha_composite(small[key].resize((T, T), Image.LANCZOS), (15 + c * T, 15 + r * T))
    prev.save(os.path.join(out, "_preview_phrases.png"))
    sheet = Image.new("RGBA", (T * 8 + 30, T * 5 + 30), (255, 255, 255, 255))
    for n, key in enumerate(order):
        sheet.alpha_composite(small[key].resize((T, T), Image.LANCZOS), (15 + n % 8 * T, 15 + n // 8 * T))
    sheet.save(os.path.join(out, "_preview_all40.png"))


if __name__ == "__main__":
    build_hiragana_set()
