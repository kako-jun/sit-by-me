"""Verify #68 asset paths (manifest, bytes, ID names) without scanning historical prose.

ID 名の規則は台帳 docs/ledger/ファイル配置.yaml が正本（ここに正規表現を重複して持たない）。"""
import argparse
import hashlib
import json
from pathlib import Path
import re

MAP_ID = r'(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\d{2}'
LAYOUT = 'docs/ledger/ファイル配置.yaml'


def image_name_patterns(root):
    """画像の ID 名規則の正本は台帳 docs/ledger/ファイル配置.yaml（検査=画像ID規則 の行のパターン。{MAP_ID} を展開）。"""
    import sys
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / '.claude/skills/sit-field-background/tools'))
    import ledger_io
    # 検証対象 root に配置表が無い（最小 fixture）なら、このスクリプトのリポの表を使う
    table = root / LAYOUT if (root / LAYOUT).is_file() else repo / LAYOUT
    rows = ledger_io.parse('ファイル配置', table.read_text(encoding='utf-8'))
    patterns = [r['パターン'].replace('{MAP_ID}', MAP_ID) for r in rows if r['検査'] == '画像ID規則']
    assert patterns, f'{LAYOUT} に 検査=画像ID規則 の行が無い'
    return patterns


def check_image_names(root):
    patterns = image_name_patterns(root)
    for image in (path for path in (root / 'assets/images').rglob('*') if path.suffix in {'.png', '.webp'}):
        relative = image.relative_to(root).as_posix()
        assert any(re.fullmatch(p, relative) for p in patterns), f'Non-ID image: {relative}'


def verify(root):
    root = root.resolve()
    manifest = json.loads((root / 'docs/production/20261018-asset-migration.json').read_text())
    rows = manifest['entries']
    old_paths = [r['old'] for r in rows]
    destinations = [r['new'] for r in rows if r['new']]
    assert len(old_paths) == len(set(old_paths)), 'Duplicate manifest source'
    assert len(destinations) == len(set(destinations)), 'Duplicate manifest destination'
    for row in rows:
        assert row['action'] in {'move', 'delete'}, row
        assert row['reason'] and re.fullmatch(r'[0-9a-f]{64}', row['sha256']), row
        old = (root / row['old']).resolve()
        old.relative_to(root)
        assert not old.exists(), f'Old asset remains: {row["old"]}'
        if row['action'] == 'delete':
            assert row['new'] is None, row
            continue
        assert row['new'], row
        new = (root / row['new']).resolve()
        new.relative_to(root)
        assert new.is_file(), f'Missing migrated asset: {row["new"]}'
        if new.suffix in {'.png', '.webp', '.svg'}:
            actual = hashlib.sha256(new.read_bytes()).hexdigest()
            assert actual == row['sha256'], f'Image bytes changed: {row["new"]}'

    image_root = root / 'assets/images'
    check_image_names(root)
    remaining_sample_files = [
        path for path in (root / 'sample').rglob('*')
        if path.is_file() and path.name != '.DS_Store'
    ]
    assert not remaining_sample_files, 'sample still contains files'
    for image in (root / 'assets').rglob('*.png'):
        assert image.is_relative_to(image_root), f'Image outside canonical root: {image}'

    print(f'PASS: {len(rows)} manifest entries, {len(destinations)} kept files, all image hashes and ID paths verified.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        verify(args.root)
    except (AssertionError, ValueError, OSError, KeyError) as error:
        parser.exit(1, f'FAIL: {error}\n')
