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
    if path.startswith("."):
        raise ValueError(f"不正な経路: {path}")
    out = []
    pos = 0
    for m in TOK.finditer(path):
        if m.start() != pos:
            raise ValueError(f"不正な経路: {path}")
        pos = m.end()
        if m.group(1) is not None:
            out.append((m.group(1), None))
        elif m.group(2) is not None:
            out.append((m.group(2), None))
        else:
            out.append((None, int(m.group(3))))
    if pos != len(path) or not out:
        raise ValueError(f"不正な経路: {path}")
    return out


def _val(v, t):
    if t == "数":
        value = json.loads(v)
        if type(value) not in (int, float) or not __import__('math').isfinite(value):
            raise ValueError(f"数でない値: {v}")
        return value
    if t == "真偽":
        if v not in ("true", "false"):
            raise ValueError(f"真偽でない値: {v}")
        return v == "true"
    if t in ("空", "空配列", "空辞書") and v != "":
        raise ValueError(f"{t} の値は空欄にする: {v}")
    if t == "空":
        return None
    if t == "空配列":
        return []
    if t == "空辞書":
        return {}
    if t == "文":
        return v
    raise ValueError(f"未知の型: {t}")


def unflatten(rows):
    """rows: [(path, value, type)] → 入れ子。リストの添字は出現順（0 始まり連番）を要求する。"""
    root = {}
    seen = set()
    for p, v, t in rows:
        toks = tokens(p)
        path_key = tuple(toks)
        if path_key in seen:
            raise ValueError(f"経路が重複: {p}")
        if any(path_key[:len(old)] == old or old[:len(path_key)] == path_key for old in seen):
            raise ValueError(f"親と子の経路が衝突: {p}")
        seen.add(path_key)
        cur = root
        for i, (k, idx) in enumerate(toks):
            last = i == len(toks) - 1
            nxt = toks[i + 1] if not last else None
            container_new = [] if (nxt and nxt[1] is not None) else {}
            if k is not None:
                if not isinstance(cur, dict):
                    raise ValueError(f"辞書と配列の経路が衝突: {p}")
                if last:
                    cur[k] = _val(v, t)
                else:
                    cur = cur.setdefault(k, container_new)
            else:
                if not isinstance(cur, list):
                    raise ValueError(f"辞書と配列の経路が衝突: {p}")
                if idx > len(cur):
                    raise ValueError(f"配列の添字は0始まり連番にする: {p}")
                while len(cur) <= idx:
                    cur.append(None)
                if last:
                    cur[idx] = _val(v, t)
                else:
                    if cur[idx] is None:
                        cur[idx] = container_new
                    cur = cur[idx]
    return root
