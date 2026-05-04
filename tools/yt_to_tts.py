#!/usr/bin/env python3
"""YouTube台本Markdown → TTS用クリーンMarkdown 変換スクリプト

Usage:
    python yt_to_tts.py <input.md> [<input2.md> ...]
    python yt_to_tts.py --all    # scripts/ 配下を一括変換し scripts_tts/ に出力

仕様:
- 「# YouTube台本：◯◯」のH1タイトルは保持
- タイトル案 / サムネテキスト案 / 動画構成（表）/ 各種メタブロックは削除
- 「📝 台本本文」以降の本文のみを抽出
- [SECTION X：xxx｜0:00〜0:20] のセクション見出しを削除
- [テロップ:...] [画面:...] [BGM:...] [SE:...] 等の演出キューを削除
- Markdown装飾（**bold**, > 引用記号、--- 区切り）を除去
- ショート企画ブロックも削除（音声には不要）
- 連続空行を1つに圧縮
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "scripts"
DST_DIR = ROOT / "scripts_tts"

SECTION_HEADER_RE = re.compile(r"^#{2,4}\s*\[SECTION[^\]]*\]\s*$")
CUE_LINE_RE = re.compile(r"^\s*\[(?:テロップ|画面|BGM|SE|効果音|映像|カット|ナレーション)[：:][^\]]*\]\s*$")
INLINE_CUE_RE = re.compile(r"\[(?:テロップ|画面|BGM|SE|効果音|映像|カット|ナレーション)[：:][^\]]*\]")
HR_RE = re.compile(r"^-{3,}\s*$")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)")
QUOTE_PREFIX_RE = re.compile(r"^>\s?")
LIST_PREFIX_RE = re.compile(r"^[\-\*]\s+")
ORDERED_LIST_RE = re.compile(r"^\d+[\.、)]\s+")
H_RE = re.compile(r"^#{1,6}\s+")


def extract_body(text: str) -> tuple[str, str]:
    """H1タイトル行と、台本本文セクション以降を返す。"""
    lines = text.splitlines()
    title = ""
    for ln in lines:
        if ln.startswith("# "):
            title = ln[2:].strip()
            break

    # 「## 📝 台本本文」以降を抽出
    body_start = None
    for i, ln in enumerate(lines):
        if "台本本文" in ln and ln.lstrip().startswith("#"):
            body_start = i + 1
            break
    if body_start is None:
        # フォールバック: 最初の [SECTION ... ] から
        for i, ln in enumerate(lines):
            if "[SECTION" in ln:
                body_start = i
                break
    if body_start is None:
        return title, text

    # 「## 🎬 ショート」など、本文後のメタセクションが来たら打ち切り
    body_end = len(lines)
    for i in range(body_start, len(lines)):
        ln = lines[i].lstrip()
        if ln.startswith("## ") and ("ショート" in ln or "Shorts" in ln or "編集メモ" in ln or "関連" in ln):
            body_end = i
            break
    return title, "\n".join(lines[body_start:body_end])


def clean_body(body: str) -> str:
    out: list[str] = []
    for raw in body.splitlines():
        ln = raw.rstrip()

        # セクション見出し / 演出キュー行を除去
        if SECTION_HEADER_RE.match(ln.strip()):
            continue
        if CUE_LINE_RE.match(ln):
            continue
        if HR_RE.match(ln):
            continue
        # ブロック見出し ### / ## は削除
        if H_RE.match(ln):
            continue

        # インラインの演出キューを削除
        ln = INLINE_CUE_RE.sub("", ln)
        # 引用 / リスト記号を剥がす
        ln = QUOTE_PREFIX_RE.sub("", ln)
        ln = LIST_PREFIX_RE.sub("", ln)
        ln = ORDERED_LIST_RE.sub("", ln)
        # bold/italic装飾を除去
        ln = BOLD_RE.sub(r"\1", ln)
        ln = ITALIC_RE.sub(r"\1", ln)

        out.append(ln.rstrip())

    # 連続空行を1つに圧縮
    cleaned: list[str] = []
    blank = False
    for ln in out:
        if ln.strip() == "":
            if not blank:
                cleaned.append("")
            blank = True
        else:
            cleaned.append(ln)
            blank = False
    # 先頭末尾の空行を削る
    while cleaned and cleaned[0] == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned)


def convert_file(src: Path, dst_dir: Path) -> Path:
    text = src.read_text(encoding="utf-8")
    title, body = extract_body(text)
    cleaned = clean_body(body)
    header = f"# {title}\n\n" if title else ""
    out = header + cleaned + "\n"
    dst = dst_dir / src.name.replace("_yt.md", "_yt_tts.md")
    dst.write_text(out, encoding="utf-8")
    return dst


def main(argv: list[str]) -> int:
    DST_DIR.mkdir(exist_ok=True)
    if not argv or argv[0] == "--all":
        targets = sorted(SRC_DIR.glob("*_yt.md"))
    else:
        targets = [Path(p) for p in argv]
    for src in targets:
        dst = convert_file(src, DST_DIR)
        print(f"  {src.name}  ->  {dst.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
