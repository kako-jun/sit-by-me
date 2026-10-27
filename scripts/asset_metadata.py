#!/usr/bin/env python3
"""Build/check sanitized asset metadata JSON from normalized YAML masters."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.claude/skills/sit-field-background/tools'))
import ledger_io

PRIVATE = re.compile(r'(?:/Users/|/home/|/tmp/|exec-[0-9a-f]{8}-[0-9a-f-]{20,})', re.I)
TYPES = {dict: 'object', list: 'array', str: 'string', int: 'number', float: 'number', bool: 'boolean', type(None): 'null'}


def sanitize(node):
    if isinstance(node, dict):
        return {key: sanitize(value) for key, value in node.items()}
    if isinstance(node, list):
        return [sanitize(value) for value in node]
    if isinstance(node, str) and PRIVATE.search(node):
        return 'redacted local provenance'
    return node


def pointer(parent, part):
    return parent + '/' + str(part).replace('~', '~0').replace('/', '~1')


def flatten(ident, node, path=''):
    kind = TYPES[type(node)]
    yield {'メタデータID': ident, 'JSONポインタ': path, '型': kind,
           '値': json.dumps(node, ensure_ascii=False) if kind not in ('object', 'array') else ''}
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
        elif kind in ('string', 'number', 'boolean', 'null'):
            node = json.loads(value)
            assert TYPES[type(node)] == kind, (path, kind)
        else:
            raise ValueError(f'Unknown JSON type {kind}')
        assert path not in nodes, f'Duplicate JSON pointer {path}'
        nodes[path] = node
        if path:
            parent, encoded = path.rsplit('/', 1)
            part = encoded.replace('~1', '/').replace('~0', '~')
            assert parent in nodes, f'Parent missing: {path}'
            if isinstance(nodes[parent], list):
                assert part == str(len(nodes[parent])), f'Array index gap: {path}'
                nodes[parent].append(node)
            else:
                assert part not in nodes[parent], f'Duplicate property: {path}'
                nodes[parent][part] = node
    assert '' in nodes, 'Root JSON pointer missing'
    return nodes['']


def output_bytes(node):
    return (json.dumps(node, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def verify_or_build(build=False):
    metadata = ledger_io.read('素材メタデータ')
    leaves = ledger_io.read('素材メタデータ値')
    assert len(metadata) == 7, f'Expected seven metadata records, got {len(metadata)}'
    assert len({r['パス'] for r in metadata}) == len(metadata)
    assert len({r['メタデータID'] for r in metadata}) == len(metadata)
    by_id = {}
    for row in leaves:
        by_id.setdefault(row['メタデータID'], []).append(row)
    assert set(by_id) == {r['メタデータID'] for r in metadata}
    for row in metadata:
        path = ROOT / row['パス']
        path.resolve().relative_to(ROOT)
        assert path.suffix == '.json' and path.as_posix().startswith((ROOT / 'assets/images').as_posix())
        payload = output_bytes(reconstruct(by_id[row['メタデータID']]))
        assert not PRIVATE.search(payload.decode('utf-8')), f'Private provenance remains in {row["パス"]}'
        assert hashlib.sha256(payload).hexdigest() == row['安全化sha256'], row['パス']
        if build:
            path.write_bytes(payload)
        else:
            assert path.read_bytes() == payload, f'Stale metadata JSON: {row["パス"]}'
    print(f'PASS: {len(metadata)} sanitized asset metadata JSON files match YAML')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    verify_or_build(args.action == 'build')
