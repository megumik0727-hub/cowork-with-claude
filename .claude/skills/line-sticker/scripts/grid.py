"""records.tsv から、パターンごとの一覧画像と縮小プレビューを作る"""
import csv, glob, os, shutil, sys
from PIL import Image
TR = "/root/.claude/projects/-home-user-cowork-with-claude/21f3956b-4b4b-52ea-bbfa-fa226e8c2365/tool-results"
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, "records.tsv")), delimiter="\t"))
keys = {"基本": "01_kihon", "感謝": "02_kansha", "承諾": "03_shodaku", "謝罪": "04_shazai"}
for pat, slug in keys.items():
    rs = [r for r in rows if r["pattern"] == pat]
    if not rs:
        continue
    d = os.path.join(HERE, slug); os.makedirs(d, exist_ok=True)
    g = Image.new("RGB", (5 * 210 + 10, ((len(rs) + 4) // 5) * 210 + 10), (235, 238, 244))
    for i, r in enumerate(rs):
        src = glob.glob(os.path.join(TR, f"*{r['blob']}.jpg"))[0]
        dst = os.path.join(d, f"{int(r['no']):02d}_preview.jpg"); shutil.copy(src, dst)
        g.paste(Image.open(src).convert("RGB"), (10 + i % 5 * 210, 10 + i // 5 * 210))
    g.save(os.path.join(HERE, f"_grid_{slug}.png"))
    print(slug, len(rs))
