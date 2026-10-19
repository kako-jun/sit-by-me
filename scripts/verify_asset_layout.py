"""Verify #68 asset paths (manifest, bytes, ID names) without scanning historical prose."""
import argparse
import hashlib
import json
from pathlib import Path
import re

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
        if new.suffix in {'.png', '.svg'}:
            actual = hashlib.sha256(new.read_bytes()).hexdigest()
            assert actual == row['sha256'], f'Image bytes changed: {row["new"]}'

    image_root = root / 'assets/images'
    for image in (path for path in image_root.rglob('*') if path.suffix in {'.png', '.webp'}):
        relative = image.relative_to(image_root).as_posix()
        patterns = (
            r'enemies/M\d{3}\.png',
            r'summons/S\d{3}\.png',
            r'characters/(C00[1-4])/(?:masters|poses|walk)/\1-[^/]+\.png',
            r'fields/legacy/E\d{2}(?:-[\w-]+)?\.png',
            r'fields/legacy/masks/E\d{2}[-\w]+\.png',
            # 外観参照のみ非可逆WebP(品質85)も許可。他種別のWebP全面移行は別PR
            r'fields/reference/[a-z0-9]+(?:-[a-z0-9]+)*\.(?:png|webp)',
            r'battle-backgrounds/BG\d{3}\.png',
            r'brand/BRAND\d{3}\.png',
        )
        assert any(re.fullmatch(p, relative) for p in patterns), f'Non-ID image: {relative}'
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
