# 申請用書き出しの進捗

| セット | Canvaデザイン | 状態 |
|---|---|---|
| 基本 | [ゆるクマおじさん構文 基本 書き出し用](https://www.canva.com/d/6zvFVs_B6FzBOxa)（DAHXB9y1vOw） | 2〜25ページ目＝スタンプ01〜24、26ページ目＝メイン、27ページ目＝タブ。申請用ZIP作成済み（`submit/yurukuma_kihon.zip`）。01はCanvaで白背景になっていたため `clear_white_bg.py` で透過処理 |
| 感謝 | [ゆるクマおじさん構文 感謝 書き出し用](https://canva.link/9sswb16cfbvucc5)（DAHXDVV5Akc） | 同じページ構成。配置済み。kansha02のウインクを「>」から「<」に修正（肌色の角丸四角で元の目を隠し、線を重ねた） |
| 承諾 | [ゆるクマおじさん構文 承諾 書き出し用](https://canva.link/2507o2c9996091n)（DAHXDTjYvqo） | 同じページ構成。配置済み |
| 謝罪 | [ゆるクマおじさん構文 謝罪 書き出し用](https://canva.link/si5410yzrnxbehn)（DAHXDf7GKGo） | 同じページ構成。配置済み。shazai15は顔の縦線と余計な線をなくした画像に作り直して差し替え（旧 MAHXDWTl3gQ）。shazai18は崩れていた左耳を図形で描き直し |

- 申請用ZIP：Canvaから2〜27ページ目をPNG（背景透過）でダウンロードし、`.claude/skills/line-sticker/scripts/package.py` で 01〜24.png・main.png・tab.png に名前を付け直す。

- 1ページ目（1264×1264の白紙）は作業用なので書き出し対象外。
- 配置ルール: スタンプは370×320のページに300×300で(35,10)に配置（上下10px・左右35pxの余白）。メインは240×240に220×220、タブは96×74に70×70。
- 背景透過済み画像のmedia idは `nobg.tsv`。
- Canvaからの書き出しURL（export-download.canva.com）はこの環境からは取得できないため、ダウンロードは本人がCanvaで行う。
