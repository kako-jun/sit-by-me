"""Verify the MAP ID renumbering table (old ID -> area code + sequence) against the registries.

Checks docs/production/20261019-map-id-renumber.json is a complete one-to-one table for the 130 historical MAP rows (129 active; retired IDs such as TRM-01 stay as gaps),
matches docs/topology/areas.json (area membership, order, names) and map-ids.json, and that no
unregistered new-style ID or leftover old ID appears in the MAP documents.
"""
import argparse
import json
from pathlib import Path
import re

NEW_ID = re.compile(r'^([A-Z]{3})-(\d{2})$')
OLD_IDS = ({f'E{n}' for n in range(1, 34)} | {f'F{n}' for n in range(1, 87)}
           | {f'N{n}' for n in (1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12)})
# Files where every E/F/N+digits token is a MAP ID (other docs share the shape with BGM slots, decision labels, etc.).
# (旧)MAP専用文書の一覧。現在は全文書を文脈規則つきで検査するため参照用
MAP_ONLY_FILES = (
    'docs/map-topology.md', 'docs/map-specifications.md', 'docs/map-asset-registry.md',
    'docs/map-contract-checklist.md', 'docs/map-reference-research.md',
    'docs/topology/areas.json', 'docs/topology/overseas-progression.json',
)
# 直後が英字でも検出する(E18door型)。イベントID(E001, 3桁)は一致しない
OLD_TOKEN_ANY = re.compile(r'(?<![A-Za-z0-9])([EFN])(0\d|[1-9]\d?)(?![0-9])')
# E/F/N+数字が別体系(決定ラベルN1・BGMスロット等)で出る文書・行は旧ID検査から除く
EXEMPT_OLD_ID_FILES = ('docs/ability-candidates.md', 'scripts/verify_map_id_renumber.py')
EXEMPT_OLD_ID_LINE_WORDS = ('ぬすむ',)
# tests are not scanned: they use deliberately unregistered IDs (存在しない連番や旧ID名) as negative fixtures
SCAN_DIRS = ('docs', 'scripts', '.claude')
SKIP_PREFIXES = ('docs/reviews/', 'docs/production/20261018-asset-migration.json')


def old_key(old_id):
    return old_id[0] + str(int(old_id[1:]))


def verify(root):
    root = Path(root).resolve()
    table = json.loads((root / 'docs/production/20261019-map-id-renumber.json').read_text(encoding='utf-8'))
    maps = table['maps']
    assert len(maps) == 130, f'expected 130 MAPs, got {len(maps)}'
    olds = [old_key(m['old_id']) for m in maps]
    news = [m['new_id'] for m in maps]
    assert len(set(olds)) == 130, 'duplicate old ID'
    assert len(set(news)) == 130, 'duplicate new ID'
    retired = {m['new_id'] for m in maps if m.get('retired')}
    assert set(olds) == OLD_IDS, f'old ID set differs: {sorted(set(olds) ^ OLD_IDS)}'
    assert not (set(olds) & set(news)), 'old and new ID spaces overlap'

    by_area = {}
    for m in maps:
        found = NEW_ID.match(m['new_id'])
        assert found, f'bad new ID format: {m["new_id"]}'
        assert found[1] == m['area_code'], f'area code mismatch: {m["new_id"]}'
        by_area.setdefault(m['area_code'], []).append((int(found[2]), m))
    code_to_area = {}
    for code, rows in by_area.items():
        assert sorted(n for n, _ in rows) == list(range(1, len(rows) + 1)), f'{code}: sequence has a gap or duplicate'
        assert len({m['area_id'] for _, m in rows}) == 1, f'{code}: mixes areas'
        assert len({m['area_name'] for _, m in rows}) == 1, f'{code}: mixes area names'
        code_to_area[code] = rows[0][1]['area_id']
    assert len(set(code_to_area.values())) == len(code_to_area), 'two area codes share an area'
    for m in maps:
        if 'new_slug' in m:
            assert m.get('old_slug') and m['new_slug'] != m['old_slug'], f'{m["new_id"]}: bad slug rename'
    assert sorted(table['area_order']) == sorted(by_area), 'area_order mismatch'

    areas = json.loads((root / 'docs/topology/areas.json').read_text(encoding='utf-8'))['areas']
    assert [a['id'] for a in areas] == [code_to_area[c] for c in table['area_order']], \
        'areas.json order differs from area_order'
    for area in areas:
        expected = sorted(m['new_id'] for m in maps if m['area_id'] == area['id'] and m['new_id'] not in retired)
        assert sorted(area['maps']) == expected, f'areas.json maps differ for {area["id"]}'
        assert sorted(area['layout']) == expected, f'areas.json layout differs for {area["id"]}'
        names = {m['area_name'] for m in maps if m['area_id'] == area['id']}
        assert names == {area['name']}, f'area name differs for {area["id"]}'
    register = json.loads((root / 'docs/topology/map-ids.json').read_text(encoding='utf-8'))
    assert register['expected_count'] == 130 - len(retired)
    assert set(register.get('retired', {})) == retired, 'map-ids.json retired differs'
    assert register['areas'] == {c: len(by_area[c]) for c in table['area_order']}, 'map-ids.json differs'

    valid = set(news)
    codes = '|'.join(table['area_order'])
    new_token = re.compile(rf'(?<![A-Za-z0-9])(?:{codes})-\d{{2}}(?![A-Za-z0-9])')
    # イベント・遷移・BGMなど別体系の語の直後に新MAP IDが来たら、E005等を誤置換した疑い
    wrong_context = re.compile(rf'(?:イベント(?:ID)?|遷移|BGM|スロット|ERA)\s*(?:{codes})-\d{{2}}(?![A-Za-z0-9])')
    old_slugs = {m['old_slug'] for m in maps if m.get('new_slug')}
    for directory in SCAN_DIRS:
        for path in sorted((root / directory).rglob('*')):
            relative = path.relative_to(root).as_posix()
            if not path.is_file() or relative.startswith(SKIP_PREFIXES) or path.suffix not in {
                    '.md', '.json', '.rb', '.py', '.csv', '.yaml'}:
                continue
            text = path.read_text(encoding='utf-8')
            is_bgm = relative.startswith('docs/bgm')
            for token in new_token.findall(text):
                assert token in valid, f'{relative}: unregistered new-style ID {token}'
            if is_bgm:
                assert not new_token.search(text), f'{relative}: MAP ID in BGM table (slot/MAP混同)'
            assert not wrong_context.search(text), f'{relative}: MAP ID right after an event/BGM word (誤置換の疑い)'
            if relative == 'docs/scenario-registry.md':
                for line in text.splitlines():
                    first = line.split('|')[1].strip() if line.startswith('| ') and line.count('|') > 2 else ''
                    assert not new_token.fullmatch(first), f'{relative}: MAP ID in event ID column: {first}'
                    if re.fullmatch(r'E\d+', first):
                        assert re.fullmatch(r'E\d{3}', first), f'{relative}: bad event ID {first}'
            if relative.startswith('docs/production/20261019'):
                continue
            for slug in old_slugs:
                assert slug not in text, f'{relative}: old slug {slug} remains'
            if is_bgm or relative in EXEMPT_OLD_ID_FILES:
                continue
            for line in text.splitlines():
                if any(word in line for word in EXEMPT_OLD_ID_LINE_WORDS):
                    continue
                for found in OLD_TOKEN_ANY.finditer(line):
                    if found[0] == 'N1' and line[found.end():found.end() + 1] == 'b':
                        continue  # 決定ラベルN1b
                    assert old_key(found[0]) not in OLD_IDS, f'{relative}: old ID {found[0]} remains'
    print(f'PASS: 130 MAP rows one-to-one ({130 - len(retired)} active, retired {sorted(retired)}), {len(by_area)} areas, areas.json/map-ids.json match, no unregistered or leftover IDs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        verify(args.root)
    except (AssertionError, KeyError, OSError, ValueError) as error:
        parser.exit(1, f'FAIL: {error}\n')
