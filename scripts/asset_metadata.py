#!/usr/bin/env python3
"""Build/check sanitized asset metadata JSON from normalized YAML masters.

数値は元JSONの表記（0.70 など）をそのまま保持する。検査は assert でなく明示的な失敗なので `python -O` でも効く。"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '.claude/skills/sit-field-background/tools'))
import ledger_io

ROOT = Path(os.environ.get('LEDGER_ROOT', ledger_io.REPO))
# ローカル絶対パス（Unix/macOS/WSL/Windows/ホーム略記）と生成実行IDを含む文字列は丸ごと置換する
PRIVATE = re.compile(r'(?:/Users/|/home/|/tmp/|/private/|/var/folders/|/mnt/|~/|\\\\[\w.-]+\\|\b[A-Za-z]:[\\/]|exec-[0-9a-f]{8}-[0-9a-f-]{20,})', re.I)
REDACTED = 'redacted local provenance'
NUMBER_TEXT = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?')


class MetadataError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise MetadataError(message)


class Lit(str):
    """元JSONの小数・指数表記をそのまま保つ数値リテラル。"""


def kind_of(node):
    if node is None:
        return 'null'
    if isinstance(node, bool):
        return 'boolean'
    if isinstance(node, (int, Lit)):
        return 'number'
    if isinstance(node, float):
        return 'number'
    if isinstance(node, str):
        return 'string'
    if isinstance(node, dict):
        return 'object'
    if isinstance(node, list):
        return 'array'
    raise MetadataError(f'Unsupported JSON value {type(node).__name__}')


def loads(text):
    return json.loads(text, parse_float=Lit)


def sanitize(node):
    if isinstance(node, dict):
        return {key: sanitize(value) for key, value in node.items()}
    if isinstance(node, list):
        return [sanitize(value) for value in node]
    if isinstance(node, str) and not isinstance(node, Lit) and PRIVATE.search(node):
        return REDACTED
    return node


def pointer(parent, part):
    return parent + '/' + str(part).replace('~', '~0').replace('/', '~1')


def literal(node):
    kind = kind_of(node)
    if kind == 'number':
        return str(node) if isinstance(node, (Lit, int)) else repr(node)
    return json.dumps(node, ensure_ascii=False)


def flatten(ident, node, path=''):
    kind = kind_of(node)
    yield {'メタデータID': ident, 'JSONポインタ': path, '型': kind,
           '値': literal(node) if kind not in ('object', 'array') else ''}
    if isinstance(node, dict):
        for key, value in node.items():
            yield from flatten(ident, value, pointer(path, key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from flatten(ident, value, pointer(path, index))


def reconstruct(rows):
    nodes = {}
    for row in rows:
        path, kind, value = row['JSONポインタ'], row['型'], row['値']
        if kind == 'object':
            node = {}
        elif kind == 'array':
            node = []
        elif kind == 'number':
            require(NUMBER_TEXT.fullmatch(value), f'Invalid number literal at {path}: {value}')
            node = int(value) if re.fullmatch(r'-?\d+', value) else Lit(value)
        elif kind in ('string', 'boolean', 'null'):
            node = json.loads(value)
            require(kind_of(node) == kind, f'Type mismatch at {path}: {kind}')
        else:
            raise MetadataError(f'Unknown JSON type {kind}')
        require(path not in nodes, f'Duplicate JSON pointer {path}')
        nodes[path] = node
        if path:
            parent, encoded = path.rsplit('/', 1)
            part = encoded.replace('~1', '/').replace('~0', '~')
            require(parent in nodes, f'Parent missing: {path}')
            if isinstance(nodes[parent], list):
                require(part == str(len(nodes[parent])), f'Array index gap: {path}')
                nodes[parent].append(node)
            else:
                require(isinstance(nodes[parent], dict), f'Parent is not a container: {path}')
                require(part not in nodes[parent], f'Duplicate property: {path}')
                nodes[parent][part] = node
    require('' in nodes, 'Root JSON pointer missing')
    return nodes['']


def dump(node, level=0):
    """json.dumps(indent=2, ensure_ascii=False) と同じ体裁。数値だけ元の表記で出す。"""
    if isinstance(node, dict):
        if not node:
            return '{}'
        pad = '  ' * (level + 1)
        body = ',\n'.join(f'{pad}{json.dumps(key, ensure_ascii=False)}: {dump(value, level + 1)}' for key, value in node.items())
        return '{\n' + body + '\n' + '  ' * level + '}'
    if isinstance(node, list):
        if not node:
            return '[]'
        pad = '  ' * (level + 1)
        return '[\n' + ',\n'.join(pad + dump(value, level + 1) for value in node) + '\n' + '  ' * level + ']'
    return literal(node)


def output_bytes(node):
    return (dump(node) + '\n').encode('utf-8')


def verify_or_build(build=False, root=None):
    root = Path(root or ROOT)
    metadata = ledger_io.read('素材メタデータ')
    leaves = ledger_io.read('素材メタデータ値')
    require(len({r['パス'] for r in metadata}) == len(metadata), 'Duplicate metadata path')
    require(len({r['メタデータID'] for r in metadata}) == len(metadata), 'Duplicate metadata id')
    by_id = {}
    for row in leaves:
        by_id.setdefault(row['メタデータID'], []).append(row)
    require(set(by_id) == {r['メタデータID'] for r in metadata}, 'Metadata ids differ between 素材メタデータ and 素材メタデータ値')
    images = root / 'assets/images'
    for row in metadata:
        path = (root / row['パス']).resolve()
        path.relative_to(images.resolve())
        require(path.suffix == '.json', f'Not a JSON path: {row["パス"]}')
        payload = output_bytes(reconstruct(by_id[row['メタデータID']]))
        require(not PRIVATE.search(payload.decode('utf-8')), f'Private provenance remains in {row["パス"]}')
        require(hashlib.sha256(payload).hexdigest() == row['安全化sha256'], f'Sanitized hash differs from YAML values: {row["パス"]}')
        if build:
            path.write_bytes(payload)
        else:
            require(path.is_file() and path.read_bytes() == payload, f'Stale metadata JSON: {row["パス"]}')
    # 台帳に載っていない画像用JSONが出てきたら失敗させる（件数の固定値ではなく集合で照合）
    on_disk = {p.relative_to(root).as_posix() for p in images.rglob('*.json')}
    require(on_disk == {r['パス'] for r in metadata}, f'Metadata JSON set differs: unregistered={sorted(on_disk - {r["パス"] for r in metadata})}, missing={sorted({r["パス"] for r in metadata} - on_disk)}')
    return len(metadata)


def ingest(source, path, owner, commit):
    """元の画像用JSON（source）を安全化し、素材メタデータ／素材メタデータ値へ取り込み直してJSONを再生成する。

    同じパスの行があればIDを保って置き換え、なければ AMETA-NNN を採番する。"""
    raw = Path(source).read_bytes()
    require(re.fullmatch(r'[0-9a-f]{7,40}', commit), f'出典commit は7〜40桁の小文字16進: {commit}')
    require(path.startswith('assets/images/') and path.endswith('.json') and '..' not in path.split('/'),
            f'--path は assets/images/ 配下の .json: {path}')
    import asset_chain
    git = asset_chain.git_runner(ROOT)
    require(git is not None, f'--commit を確認できない（{ROOT} が git リポジトリの最上位でない）')
    require(git('cat-file', '-e', f'{commit}^{{commit}}')[0] == 0, f'--commit {commit} が git に存在しない')
    known = {r[key] for table, key in (('MAP', 'MAP_ID'), ('人物', '人物ID'), ('敵', '敵ID'), ('召喚獣', '召喚獣ID'))
             for r in ledger_io.read(table)}
    require(owner and (re.sub(r'-(kids|fire|burnt|wc)\Z', '', owner) in known or re.fullmatch(r'BG\d{3}|BRAND', owner)),
            f'--owner {owner!r} が台帳にない（MAP・人物・敵・召喚獣のID）')
    node = sanitize(loads(raw.decode('utf-8')))
    payload = output_bytes(node)
    require(not PRIVATE.search(payload.decode('utf-8')), 'Private provenance remains after sanitize')
    metadata = ledger_io.read('素材メタデータ')
    leaves = ledger_io.read('素材メタデータ値')
    existing = next((r for r in metadata if r['パス'] == path), None)
    if existing:
        ident = existing['メタデータID']
    else:
        ident = 'AMETA-%03d' % (max([int(r['メタデータID'].split('-')[1]) for r in metadata] or [0]) + 1)
    row = {'メタデータID': ident, 'パス': path, '所有者ID': owner,
           '原文sha256': hashlib.sha256(raw).hexdigest(), '安全化sha256': hashlib.sha256(payload).hexdigest(),
           '出典commit': commit,
           '安全化方針': 'ローカル絶対パスと生成実行IDを含む文字列を redacted local provenance に置換。元値はYAMLに保持しない。'}
    metadata = [row if r['メタデータID'] == ident else r for r in metadata] + ([] if existing else [row])
    leaves = [r for r in leaves if r['メタデータID'] != ident] + list(flatten(ident, node))
    ledger_io.write('素材メタデータ', metadata)
    ledger_io.write('素材メタデータ値', leaves)
    return ident


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check', 'ingest'])
    parser.add_argument('--source', help='ingest: 元JSONのファイル')
    parser.add_argument('--path', help='ingest: 台帳上のパス（assets/images/ 配下の .json）')
    parser.add_argument('--owner', default='', help='ingest: 所有者ID')
    parser.add_argument('--commit', help='ingest: 出典commit')
    args = parser.parse_args(argv)
    try:
        if args.action == 'ingest':
            require(args.source and args.path and args.commit and args.owner,
                    'ingest には --source --path --owner --commit が必要')
            print(f'INGEST: {ingest(args.source, args.path, args.owner, args.commit)}（続けて build で JSON を再生成）')
            return
        count = verify_or_build(args.action == 'build')
    except (MetadataError, ValueError, OSError, KeyError) as error:
        raise SystemExit(f'FAIL: {error}')
    print(f'PASS: {count} sanitized asset metadata JSON files match YAML')


if __name__ == '__main__':
    main()
