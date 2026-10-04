"""おじさん構文スタンプ v2（370x320 透過PNG、吹き出しなし）

圧の再現ルール
1. 主文: ポップな極太書体＋白フチで大きく、少し傾ける
2. 署名: 全スタンプ右下に「😃✋」を大きく置く（おじさんの気配）
3. 物量: 絵文字 6〜9 個を大小・角度ばらばらに主文の周りへ
4. 侵食: 一部の絵文字は主文に食い込ませ、距離の近さを出す
5. 顔文字: 主文の下にスマホ標準風のゴシック体で小さく添える
6. 呼称: 名前は入れず「キミ」で汎用化
使い方: python3 make_kobun2.py <フォントのディレクトリ>
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont
import glob, json, math, os, random, sys

FONT_DIR = sys.argv[1] if len(sys.argv) > 1 else "fonts"
GOTHIC = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kobun_stickers_v2")
S = 3
W, H = 370 * S, 320 * S
MARGIN = 10 * S


def charmap(name):
    path = os.path.join(FONT_DIR, name + ".map.json")
    if os.path.exists(path):
        return {int(k): v if os.path.isabs(v) else os.path.join(FONT_DIR, v)
                for k, v in json.load(open(path)).items()}
    m = {}
    for f in glob.glob(os.path.join(FONT_DIR, name, "files", "*-normal.woff")):
        for cp in TTFont(f)["cmap"].getBestCmap():
            m.setdefault(cp, f)
    return m


POP = charmap("mochiy-pop-one")
_fonts = {}
_emoji = ImageFont.truetype(EMOJI, 109)


def font_for(ch, size, plain=False):
    path = GOTHIC if plain or ord(ch) not in POP else POP[ord(ch)]
    if (path, size) not in _fonts:
        _fonts[(path, size)] = ImageFont.truetype(path, size)
    return _fonts[(path, size)]


def is_emoji(ch):
    cp = ord(ch)
    return cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or cp in (0x2049, 0x203C, 0x2B50)


def tokens(s):
    out, i = [], 0
    while i < len(s):
        if i + 1 < len(s) and s[i + 1] == "️":
            out.append(("e", s[i:i + 2])); i += 2
        else:
            out.append(("e" if is_emoji(s[i]) else "t", s[i])); i += 1
    return out


def emoji_img(ch, size, angle=0):
    g = Image.new("RGBA", (140, 130), (0, 0, 0, 0))
    ImageDraw.Draw(g).text((0, 0), ch, font=_emoji, embedded_color=True)
    g = g.crop(g.getbbox())
    k = size / max(g.size)
    g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)
    return g.rotate(angle, expand=True, resample=Image.BICUBIC) if angle else g


def render_line(text, size, color, plain=False):
    """1行を透過画像に描く（文字＋絵文字の混在）"""
    parts, x = [], 0
    for kind, ch in tokens(text):
        if kind == "e":
            g = emoji_img(ch, int(size * 1.0)); parts.append((g, x, "e")); x += g.width + size * 0.04
        else:
            f = font_for(ch, size, plain); parts.append((ch, x, f)); x += f.getlength(ch)
    im = Image.new("RGBA", (int(x) + 2, int(size * 1.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for p, px, f in parts:
        if f == "e":
            im.alpha_composite(p, (int(px), int(size * 0.65 - p.height / 2)))
        else:
            d.text((px, size * 0.65), p, font=f, fill=color, anchor="lm")
    return im


def outline(im, r, color=(255, 255, 255, 255)):
    """白フチ（アルファを膨張させて下に敷く）"""
    pad = r + 2
    base = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    base.alpha_composite(im, (pad, pad))
    a = base.split()[3].filter(ImageFilter.MaxFilter(2 * r + 1))
    edge = Image.new("RGBA", base.size, color); edge.putalpha(a)
    edge.alpha_composite(base)
    return edge


def sticker(lines, kao, swarm, color=(40, 30, 30, 255), seed=0, size=66, tilt=-4):
    rnd = random.Random(seed)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 主文ブロック
    rows = [render_line(l, size * S, color) for l in lines]
    while max(r.width for r in rows) > W - 40 * S:
        size -= 3; rows = [render_line(l, size * S, color) for l in lines]
    bw = max(r.width for r in rows); bh = sum(int(r.height * 0.92) for r in rows)
    block = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); y = 0
    for r in rows:
        block.alpha_composite(r, ((bw - r.width) // 2, y)); y += int(r.height * 0.92)
    block = outline(block, 6 * S).rotate(tilt, expand=True, resample=Image.BICUBIC)
    kao_img = None
    if kao:                                              # 顔文字は白いラベルに載せる
        t = render_line(kao, 38 * S, (50, 50, 50, 255), plain=True)
        kao_img = Image.new("RGBA", (t.width + 28 * S, t.height + 8 * S), (0, 0, 0, 0))
        ImageDraw.Draw(kao_img).rounded_rectangle([0, 0, kao_img.width - 1, kao_img.height - 1], 22 * S,
                                                  fill=(255, 255, 255, 255), outline=(190, 190, 190, 255), width=2 * S)
        kao_img.alpha_composite(t, (14 * S, 4 * S))
        kao_img = kao_img.rotate(3, expand=True, resample=Image.BICUBIC)

    total_h = block.height + (kao_img.height - 10 * S if kao_img else 0)
    bx = (W - block.width) // 2 - 8 * S
    by = (H - total_h) // 2 - 4 * S
    # 背面の絵文字の群れ（主文の周囲、少し食い込む）
    cx, cy = bx + block.width / 2, by + block.height / 2
    swarm = list(tokens(swarm))
    swarm = [c for _, c in swarm] * 2                    # 物量は2倍に
    n = len(swarm)
    for i, ch in enumerate(swarm):
        ang = 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25)
        k = 0.75 if i % 2 else 1.05                       # 内側（食い込み）と外側の2重リング
        rx = (block.width / 2) * k + rnd.uniform(-10, 20) * S
        ry = (block.height / 2) * k + rnd.uniform(10, 40) * S
        sz = int(rnd.uniform(40, 78) * S)
        g = outline(emoji_img(ch, sz, rnd.uniform(-30, 30)), 2 * S)
        x = int(min(max(cx + rx * math.cos(ang) - g.width / 2, MARGIN), W - MARGIN - g.width))
        y = int(min(max(cy + ry * math.sin(ang) - g.height / 2, MARGIN), H - MARGIN - g.height))
        canvas.alpha_composite(g, (x, y))
    canvas.alpha_composite(block, (bx, by))
    if kao_img:
        canvas.alpha_composite(kao_img, ((W - kao_img.width) // 2 - 40 * S, by + block.height - 10 * S))
    # 署名 😃✋（右下・前面）
    face, hand = emoji_img("😃", 74 * S, 8), emoji_img("✋", 56 * S, -15)
    canvas.alpha_composite(outline(face, 3 * S), (W - MARGIN - face.width - 44 * S, H - MARGIN - face.height - 6 * S))
    canvas.alpha_composite(outline(hand, 3 * S), (W - MARGIN - hand.width - 4 * S, H - MARGIN - hand.height - 30 * S))
    return canvas.resize((370, 320), Image.LANCZOS)


STICKERS = [
    (["オツカレサマ❗"], "(^_^)v", "💦☀️❗😅🎵💕👍", (40, 30, 30, 255)),
    (["了解ダヨ👍"], "(^o^)ゞ", "❗❗🎵😁💕✨👌", (40, 30, 30, 255)),
    (["キミ、元気", "カナ❓"], "(^3<)", "❓❓💕🤔😘❗🎵", (40, 30, 30, 255)),
    (["寝ちゃったの", "カナ❓"], "(^_^;", "😴💤❓❓😅🛌❗", (40, 30, 30, 255)),
    (["ナンチャッテ"], "(笑)(^3<)", "😁💕😘❗🎵✨😅", (220, 50, 90, 255)),
    (["オジサンは、キミの", "味方ダカラネ❗"], "(^_^)", "💪❗😤✨💕🔥", (40, 30, 30, 255)),
    (["そろそろ、", "ご飯行こうヨ"], "(^o^)", "🍜🍕🍣😋❗🎵💕", (40, 30, 30, 255)),
    (["返信、", "待ってるヨ❗"], "(◎＿◎;)", "📱❓❗⏰😅💦❓", (40, 30, 30, 255)),
    (["くれぐれも、", "体調に気をつけテ"], "(^^;;", "😪💊🌡️💦❗💕💕", (40, 30, 30, 255)),
    (["ゴメンネ💦"], "(◎＿◎;)", "😱💦🙏😓💦❗😭", (40, 30, 30, 255)),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for i, (lines, kao, swarm, col) in enumerate(STICKERS, 1):
        p = os.path.join(OUT, f"{i:02d}.png")
        sticker(lines, kao, swarm, col, seed=i).save(p); paths.append(p)
    sticker(["オツカレサマ❗"], "", "", seed=0).resize((240, 208), Image.LANCZOS)  # 動作確認
    # トーク画面風プレビュー（LINEの表示に近い 1/2 サイズ）
    cols = 5; tw, th = 185, 160
    prev = Image.new("RGBA", (cols * (tw + 10) + 10, 2 * (th + 10) + 10), (140, 171, 216, 255))
    for n, p in enumerate(paths):
        prev.alpha_composite(Image.open(p).resize((tw, th), Image.LANCZOS), (10 + n % cols * (tw + 10), 10 + n // cols * (th + 10)))
    prev.save(os.path.join(OUT, "_preview.png"))
    big = Image.new("RGBA", (3 * 380 + 10, 380 + 10), (140, 171, 216, 255))
    for n, p in enumerate(paths[:3]):
        big.alpha_composite(Image.open(p), (10 + n * 380, 40))
    big.save(os.path.join(OUT, "_preview_large.png"))


if __name__ == "__main__":
    main()
