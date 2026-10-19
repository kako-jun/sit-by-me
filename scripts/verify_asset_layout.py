"""Verify #68 asset paths and active fixture references without scanning historical prose."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

PATH_KEYS = {'background', 'sprite', 'image', 'mask', 'standingMask', 'wheelchairMask',
             'foreground', 'foregroundMask', 'traversal', 'traversalMap', 'foregroundImage'}

def references(value, key=''):
    if isinstance(value, dict):
        for child_key, child in value.items():
            yield from references(child, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from references(child, key)
    elif isinstance(value, str):
        # Named path fields or sprite frame arrays; never notes or template expressions.
        if '{' not in value and (key in PATH_KEYS or value.endswith('.png')):
            if value.endswith(('.png', '.json')):
                yield value

def resolve_reference(root, config, value):
    parts = urlsplit(value)
    if parts.scheme in {'http', 'https'}:
        if parts.hostname not in {'localhost', '127.0.0.1'}:
            raise ValueError(f'Unsupported external verification asset: {value}')
        target = root / unquote(parts.path).lstrip('/')
    elif value.startswith('/'):
        target = root / unquote(value).lstrip('/')
    else:
        target = config.parent / value
    target = target.resolve()
    target.relative_to(root.resolve())
    return target

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
    for image in image_root.rglob('*.png'):
        relative = image.relative_to(image_root).as_posix()
        patterns = (
            r'enemies/(?:raw/)?M\d{3}(?:-alpha)?\.png',
            r'summons/(?:raw/)?S\d{3}\.png',
            r'characters/(C00[1-4])/(?:masters|poses|walk|raw)/\1-[^/]+\.png',
            r'fields/legacy/E\d{2}(?:-[\w-]+)?\.png',
            r'fields/legacy/masks/E\d{2}[-\w]+\.png',
            r'fields/verification/(?:masks/)?VFIELD\d{3}(?:-[-\w]+)?\.png',
            r'fields/reference/[a-z0-9]+(?:-[a-z0-9]+)*\.png',
            r'battle-backgrounds/(?:candidates/)?BG\d{3}\.png',
            r'brand/BRAND\d{3}\.png', r'diagrams/DIAG\d{3}\.png',
        )
        assert any(re.fullmatch(p, relative) for p in patterns), f'Non-ID image: {relative}'
    remaining_sample_files = [
        path for path in (root / 'sample').rglob('*')
        if path.is_file() and path.name != '.DS_Store'
    ]
    assert not remaining_sample_files, 'sample still contains files'
    for image in (root / 'assets').rglob('*.png'):
        assert image.is_relative_to(image_root), f'Image outside canonical root: {image}'

    count = 0
    for config in sorted((root / 'verification').rglob('*.json')):
        spec = json.loads(config.read_text())
        for value in references(spec):
            assert 'sample/' not in value, f'Old runtime path: {config}: {value}'
            target = resolve_reference(root, config, value)
            assert target.is_file(), f'Dangling reference: {config.relative_to(root)}: {value}'
            assert target.is_relative_to(image_root) or target.is_relative_to(root / 'verification'), target
            count += 1
        if isinstance(spec, dict) and 'output_prefix' in spec:
            output = resolve_reference(root, config, spec['output_prefix'] + '-mask.png')
            assert output.is_file(), f'Missing mask output: {output}'
    print(f'PASS: {len(rows)} manifest entries, {len(destinations)} kept files, {count} active references; all image hashes and ID paths verified.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        verify(args.root)
    except (AssertionError, ValueError, OSError, KeyError) as error:
        parser.exit(1, f'FAIL: {error}\n')
