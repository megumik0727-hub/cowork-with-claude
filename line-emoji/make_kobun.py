"""おじさん構文スタンプ（370x320 透過PNG）
案A: LINEの緑の吹き出しに、絵文字と顔文字を詰め込んだ文面そのものをスタンプにする
案B: 顔文字を主役にして、短いセリフを添える
使い方: python3 make_kobun.py <フォントのディレクトリ>
"""
from PIL import Image, ImageDraw, ImageFont
import os, sys, unicodedata

FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else "fonts"
JA = os.path.join(FONT_DIR, "kosugi-maru/files/kosugi-maru-japanese-400-normal.woff")
FALLBACK = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kobun_stickers")
S = 3
W, H = 370, 320
TEXT = (30, 30, 30, 255)
BUBBLE = (140, 224, 90, 255)

_emoji_font = ImageFont.truetype(EMOJI, 109)
_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def is_emoji(ch):
    cp = ord(ch)
    return cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or cp in (0x2049, 0x203C, 0x2B50)


def tokens(line):
    """絵文字（異体字セレクタ付き）と通常の文字に分ける"""
    out, i = [], 0
    while i < len(line):
        ch = line[i]
        if i + 1 < len(line) and line[i + 1] == "️":
            out.append(("e", ch + "️")); i += 2; continue
        out.append(("e" if is_emoji(ch) else "t", ch)); i += 1
    return out


def glyph_font(ch, size):
    f = font(JA, size)
    if ch in "◎＿" or (f.getmask(ch).getbbox() is None and not ch.isspace()):
        return font(FALLBACK, size)
    return f


def draw_line(im, x, y, line, size, color=TEXT, measure=False):
    d = ImageDraw.Draw(im)
    for kind, ch in tokens(line):
        if kind == "e":
            g = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((0, 0), ch, font=_emoji_font, embedded_color=True)
            g = g.crop(g.getbbox() or (0, 0, 1, 1))
            e = size * 1.05
            k = e / max(g.width, g.height)
            g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)
            if not measure:
                im.alpha_composite(g, (int(x), int(y + size * 0.5 - g.height / 2)))
            x += g.width + size * 0.08
        else:
            f = glyph_font(ch, size)
            if not measure:
                d.text((x, y + size * 0.5), ch, font=f, fill=color, anchor="lm")
            x += f.getlength(ch)
    return x


def bubble_sticker(text, size=31):
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    lines = text.split("\n")
    sz = size * S
    lh = sz * 1.32
    widths = [draw_line(im, 0, 0, l, sz, measure=True) for l in lines]
    if max(widths) > (W - 60) * S:                      # はみ出す場合は縮小
        return bubble_sticker(text, size - 1)
    bw, bh = max(widths) + 2 * 18 * S, lh * len(lines) + 2 * 14 * S
    x0 = (W * S - bw) / 2 + 6 * S
    y0 = (H * S - bh) / 2
    d = ImageDraw.Draw(im)
    # 吹き出し（右向きのしっぽ）＋白フチ
    for pad, col in ((5 * S, (255, 255, 255, 255)), (0, BUBBLE)):
        d.rounded_rectangle([x0 - pad, y0 - pad, x0 + bw + pad, y0 + bh + pad], 22 * S, fill=col)
        tx = x0 + bw
        d.polygon([(tx - 14 * S, y0 + 12 * S - pad), (tx + 14 * S + pad, y0 + 4 * S - pad),
                   (tx - 4 * S, y0 + 34 * S + pad)], fill=col)
    for i, l in enumerate(lines):
        draw_line(im, x0 + 18 * S, y0 + 14 * S + i * lh, l, sz)
    return im.resize((W, H), Image.LANCZOS)


def kaomoji_sticker(face, caption, face_size=78, color=(30, 30, 30, 255)):
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    big = face_size * S
    fw = draw_line(im, 0, 0, face, big, measure=True)
    if fw > (W - 30) * S:
        big = int(big * (W - 30) * S / fw); fw = draw_line(im, 0, 0, face, big, measure=True)
    cs = 34 * S
    cw = draw_line(im, 0, 0, caption, cs, measure=True)
    # 白フチ: 同じ文字列を少しずつずらして白で描く
    edge = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for dx in range(-6 * S, 6 * S + 1, 2 * S):
        for dy in range(-6 * S, 6 * S + 1, 2 * S):
            if dx * dx + dy * dy <= (6 * S) ** 2:
                draw_line(edge, (W * S - fw) / 2 + dx, 70 * S + dy, face, big, color=(255, 255, 255, 255))
                draw_line(edge, (W * S - cw) / 2 + dx, 210 * S + dy, caption, cs, color=(255, 255, 255, 255))
    # 白フチの絵文字部分も白くする
    a = edge.split()[3]
    edge = Image.new("RGBA", im.size, (255, 255, 255, 255)); edge.putalpha(a)
    im.alpha_composite(edge)
    draw_line(im, (W * S - fw) / 2, 70 * S, face, big, color)
    draw_line(im, (W * S - cw) / 2, 210 * S, caption, cs, (215, 40, 40, 255))
    return im.resize((W, H), Image.LANCZOS)


BUBBLES = [
    "了解ダヨ👍😃✋\n(^o^)❗❗",
    "オツカレサマ😃✋💦\n今日もガンバッタ\nネ❗(^_^;)",
    "寝ちゃったの\nカナ❓😅❓❓",
    "返信まだカナ😅💦\nオジサン待ってる\nヨ✋(^_^)",
    "オジサンは\n〇〇チャンの味方\nダカラネ❗😃✋",
    "ナンチャッテ😁\n(^3<)(笑)",
    "オハヨー☀️😃✋\nオイラは今日も\n元気ダヨ❗(^o^)",
    "ゴメンネ😱💦\n(◎＿◎;)オジサン\n反省…😓",
]
KAOMOJI = [
    ("(^3<)", "ナンチャッテ"),
    ("(◎＿◎;)", "既読ついてるヨ❓"),
    ("(^_^;💦", "オジサンだよ〜"),
    ("(^o^)✋", "お疲れサマ❗"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for i, t in enumerate(BUBBLES, 1):
        p = os.path.join(OUT, f"A{i:02d}.png"); bubble_sticker(t).save(p); made.append(p)
    for i, (f, c) in enumerate(KAOMOJI, 1):
        p = os.path.join(OUT, f"B{i:02d}.png"); kaomoji_sticker(f, c).save(p); made.append(p)
    # LINEのトーク画面風プレビュー
    cols = 4
    rows = (len(made) + cols - 1) // cols
    T = (W // 2 + 10, H // 2 + 10)
    prev = Image.new("RGBA", (cols * T[0] + 20, rows * T[1] + 20), (140, 171, 216, 255))
    for n, p in enumerate(made):
        t = Image.open(p).resize((W // 2, H // 2), Image.LANCZOS)
        prev.alpha_composite(t, (15 + n % cols * T[0], 15 + n // cols * T[1]))
    prev.save(os.path.join(OUT, "_preview.png"))


if __name__ == "__main__":
    main()


def notification_sticker(msgs, badge="未読 99+"):
    """案C: ロック画面の通知が連続で積み上がる"""
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = len(msgs)
    cw, ch, gap = (W - 24) * S, 62 * S, 8 * S
    top = (H * S - (n * ch + (n - 1) * gap)) / 2 + 6 * S
    for i, m in enumerate(msgs):
        y = top + i * (ch + gap)
        x = 12 * S + (n - 1 - i) * 0
        d.rounded_rectangle([x - 3 * S, y - 3 * S, x + cw + 3 * S, y + ch + 3 * S], 16 * S, fill=(255, 255, 255, 255))
        d.rounded_rectangle([x, y, x + cw, y + ch], 14 * S, fill=(242, 242, 247, 255), outline=(200, 200, 210, 255), width=S)
        d.ellipse([x + 10 * S, y + 12 * S, x + 48 * S, y + 50 * S], fill=(255, 214, 186, 255))   # アイコン（おじさん）
        draw_line(im, x + 14 * S, y + 20 * S, "😃", 22 * S)
        draw_line(im, x + 58 * S, y + 6 * S, "オジサン", 17 * S, (60, 60, 60, 255))
        d.text((x + cw - 10 * S, y + 15 * S), "たった今", font=font(JA, 13 * S), fill=(130, 130, 130, 255), anchor="rm")
        draw_line(im, x + 58 * S, y + 30 * S, m, 20 * S)
    d.rounded_rectangle([W * S - 118 * S, 2 * S, W * S - 6 * S, 34 * S], 16 * S, fill=(230, 40, 40, 255), outline="white", width=3 * S)
    d.text((W * S - 62 * S, 18 * S), badge, font=font(JA, 18 * S), fill="white", anchor="mm")
    return im.resize((W, H), Image.LANCZOS)


def readmore_sticker(lines):
    """案D: 長すぎて途中で切れている吹き出し"""
    im = bubble_sticker("\n".join(lines))
    big = im.resize((W * S, H * S), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    bb = big.getbbox()
    d.rounded_rectangle([bb[0] + 12 * S, bb[3] - 44 * S, bb[2] - 30 * S, bb[3] - 12 * S], 10 * S, fill=(120, 205, 75, 255))
    d.text(((bb[0] + bb[2]) / 2 - 9 * S, bb[3] - 28 * S), "…続きを読む（全2,480文字）", font=font(JA, 17 * S),
           fill=(30, 30, 30, 255), anchor="mm")
    return big.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    notification_sticker(["寝ちゃったのカナ❓😅", "オーイ😃✋", "既読ついてるヨ❓❓(^_^;)",
                          "ナンチャッテ😁(笑)"]).save(os.path.join(OUT, "C01.png"))
    readmore_sticker(["〇〇チャン、お疲れサマ😃✋💦", "今日はオジサン、会社で", "ちょっとした事件があって",
                      "ネ(^_^;)聞いてくれるカナ❓", "", ""]).save(os.path.join(OUT, "D01.png"))
    made = [os.path.join(OUT, f) for f in ["A03.png", "A05.png", "B02.png", "C01.png", "D01.png", "A06.png"]]
    prev = Image.new("RGBA", (3 * (W + 10) + 10, 2 * (H + 10) + 10), (140, 171, 216, 255))
    for n, p in enumerate(made):
        prev.alpha_composite(Image.open(p), (10 + n % 3 * (W + 10), 10 + n // 3 * (H + 10)))
    prev.save(os.path.join(OUT, "_preview_pick.png"))
