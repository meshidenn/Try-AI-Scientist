"""VLMへ渡すdomain/application向けの指示文。"""

from __future__ import annotations

import re


def prompt(method: str, page_number: int, content_hint: str) -> str:
    """Markdown変換用のページ単位promptを生成する。"""
    source = (
        "以下はPDFから抽出した文字block、座標、ページ番号です。"
        if method == "parse_first"
        else "添付画像はPDFの1ページです。画像に見える内容だけを読み取ってください。"
    )
    return f"""あなたは企業PDFを忠実にMarkdown化する抽出器です。
{source}
ページ番号: {page_number}
出力規則:
- 出力はMarkdown本文だけにする。コードフェンスは使わない。
- 見出し、段落、箇条書き、表、脚注の順序を可能な限り保つ。
- 表はMarkdown tableにし、列数を各行で揃える。単位と注記も残す。
- 数字、符号、%などを変更・丸め・推測しない。
- 判読できない箇所は空欄にせず`[判読不能]`と書く。
- ページをまたぐ補完はせず、このページの内容だけを出力する。

入力補助:
{content_hint}
"""


def html_prompt(method: str, page_number: int, content_hint: str) -> str:
    """HTML変換用のページ単位promptを生成する。"""
    source = (
        "以下はPDFから抽出した文字block、座標、ページ番号です。"
        if method == "parse_first"
        else "添付画像はPDFの1ページです。画像に見える内容だけを読み取ってください。"
    )
    return f"""あなたは企業PDFを忠実にHTML化する抽出器です。
{source}
ページ番号: {page_number}
出力規則:
- 出力はHTML fragmentだけにする。コードフェンス、Markdown、html要素、body要素は使わない。
- 見出しはh1〜h6、段落はp、箇条書きはul/ol/li、表はtable/thead/tbody/tr/th/tdを使う。
- CSS、script、imgを出力しない。表では可能な限り各trのセル数を揃える。
- 数字、符号、%などを変更・丸め・推測しない。
- 判読できない箇所は空欄にせず[判読不能]と書く。
- ページをまたぐ補完はせず、このページの内容だけを出力する。

入力補助:
{content_hint}
"""


def normalize_markdown(text: str) -> str:
    """VLM出力からコードフェンスと特殊box tokenだけを除去する。"""
    text = text.strip()
    text = re.sub(r"^```(?:markdown|html)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"<\|(?:begin|end)_of_box\|>", "", text)
    return text.strip() + "\n"
