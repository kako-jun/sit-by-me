"""入れ子の JSON ⇔ (項目パス, 値, 型) の行。装飾プール・エリア固定・接続図設定の表に使う。

項目パス: `layers.desk.fixed` / `forbid[3]` / `mean_rgb[0]`。型: 文 / 数 / 真偽 / 空 / 空配列 / 空辞書。
"""
import json
import re

TOK = re.compile(r'\["([^"]+)"\]|\.?([^.\[\]]+)|\[(\d+)\]')


def flatten(o, prefix=""):
    out = []
    if isinstance(o, dict):
        if not o:
            return [(prefix, "", "空辞書")]
        for k, v in o.items():
            if "." in k or "[" in k:
                out += flatten(v, f'{prefix}["{k}"]')
            else:
                out += flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(o, list):
        if not o:
            return [(prefix, "", "空配列")]
        for i, v in enumerate(o):
            out += flatten(v, f"{prefix}[{i}]")
    elif isinstance(o, bool):
        out.append((prefix, "true" if o else "false", "真偽"))
    elif o is None:
        out.append((prefix, "", "空"))
    elif isinstance(o, (int, float)):
        out.append((prefix, json.dumps(o), "数"))
    else:
        out.append((prefix, o, "文"))
    return out


def tokens(path):
    out = []
    for m in TOK.finditer(path):
        if m.group(1) is not None:
            out.append((m.group(1), None))
        elif m.group(2) is not None:
            out.append((m.group(2), None))
        else:
            out.append((None, int(m.group(3))))
    return out


def _val(v, t):
    if t == "数":
        return json.loads(v)
    if t == "真偽":
        return v == "true"
    if t == "空":
        return None
    if t == "空配列":
        return []
    if t == "空辞書":
        return {}
    return v


def unflatten(rows):
    """rows: [(path, value, type)] → 入れ子。リストの添字は出現順（0 始まり連番）を要求する。"""
    root = {}
    for p, v, t in rows:
        toks = tokens(p)
        cur = root
        for i, (k, idx) in enumerate(toks):
            last = i == len(toks) - 1
            nxt = toks[i + 1] if not last else None
            container_new = [] if (nxt and nxt[1] is not None) else {}
            if k is not None:
                if last:
                    cur[k] = _val(v, t)
                else:
                    cur = cur.setdefault(k, container_new)
            else:
                while len(cur) <= idx:
                    cur.append(None)
                if last:
                    cur[idx] = _val(v, t)
                else:
                    if cur[idx] is None:
                        cur[idx] = container_new
                    cur = cur[idx]
    return root
