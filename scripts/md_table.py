"""Markdown の表を『見出し行の列名』で読む。列の位置（セル番号）に依存しない。

旧 md（map-contract-checklist.md・map-specifications.md・map-topology.md）を読む scripts 用。
読み方（旧実装の『| で始まる行を全部読む』と同じ緩さを保つ）: 先頭列の名前が first で names を全て持つ見出し行が現れたら、
以降の『|』で始まる行をその見出しの列名で読む。途中に地の文・空行が挟まって物理的に表が分かれていても続きの行として読む。
区切り行は読み飛ばす。同じ先頭列の別の見出し行が現れたらそこから切り替える（names を持たない見出しなら、次の見出しまで読まない）。
"""
import re


def split(line):
    """'| a | b |' -> ['a', 'b']（前後の | を除く）"""
    s = line.strip()
    s = re.sub(r"\A\|", "", s)
    s = re.sub(r"\|\Z", "", s)
    return [c.strip() for c in s.split("|")]


def is_separator(cells):
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def rows(text, first, *names):
    """行は {列名: セル, 'cells': 生のセル配列}（足りない列は None）。"""
    header = None
    out = []
    for line in text.splitlines(keepends=True):
        if not line.startswith("|"):
            continue
        cells = split(line)
        if is_separator(cells):
            continue
        if cells[0] == first:
            header = cells if all(n in cells for n in names) else None
            continue
        if header is None:
            continue
        h = {name: (cells[i] if i < len(cells) else None) for i, name in enumerate(header)}
        h["cells"] = cells
        out.append(h)
    return out


def section_rows(text, first, *names):
    return rows(text, first, *names)


def pick(row, *names):
    for n in names:
        if n in row and row[n] is not None:
            return row[n]
    return None
