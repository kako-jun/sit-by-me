"""素材更新表の SHA 連鎖（素材移行 SHA → … → 現物 SHA）の共通ロジック。

素材移行.sha256 は移行時点の履歴として固定したまま、後日の差し替えは素材更新の行
（パス・旧sha256 → 新sha256）で辿る。verify_asset_layout.py・verify_domain_ledger.py・テストが共有する。"""
import re

SHA = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'[0-9a-f]{7,40}')


class ChainError(ValueError):
    pass


def index(updates):
    """{パス: {旧sha256: 新sha256}}。同じ旧SHAから2方向に分岐する連鎖は拒否する。"""
    result = {}
    for row in updates:
        steps = result.setdefault(row['パス'], {})
        if row['旧sha256'] in steps:
            raise ChainError(f'{row["パス"]}: 旧sha256 {row["旧sha256"][:12]} から連鎖が分岐している')
        steps[row['旧sha256']] = row['新sha256']
    return result


def walk(steps, start):
    """start から連鎖を辿った全SHA（start を含む順序つき）。循環は拒否する。"""
    seen = [start]
    while seen[-1] in steps:
        following = steps[seen[-1]]
        if following in seen:
            raise ChainError(f'連鎖が循環している: {following[:12]}')
        seen.append(following)
    return seen


def reaches(chains, path, start, actual):
    """移行SHA start から、素材更新の連鎖で現物SHA actual に到達できるか（actual == start も可）。"""
    return actual in walk(chains.get(path, {}), start)


def validate(updates, assets, migration):
    """素材更新の検査。エラー文のリストを返す。

    assets: 素材行のリスト、migration: 素材移行行のリスト。"""
    errors = []
    by_id = {r['素材ID']: r for r in assets}
    moved = {r['新パス']: r for r in migration if r['操作'] == 'move' and r['新パス']}
    seen = set()
    for row in updates:
        ident = row['更新ID']
        if not ident or ident in seen:
            errors.append(f'素材更新: 主キー{"が空" if not ident else "重複"} {ident}')
        seen.add(ident)
        asset = by_id.get(row['素材ID'])
        if asset is None:
            errors.append(f'素材更新 {ident}: 素材ID {row["素材ID"]} が素材にない')
        elif asset['パス'] != row['パス']:
            errors.append(f'素材更新 {ident}: パス {row["パス"]} が素材 {row["素材ID"]} のパス {asset["パス"]} と違う')
        for column in ('旧sha256', '新sha256'):
            if not SHA.fullmatch(row[column]):
                errors.append(f'素材更新 {ident}: {column} が64桁の小文字16進でない')
        if row['旧sha256'] == row['新sha256']:
            errors.append(f'素材更新 {ident}: 旧sha256と新sha256が同じ')
        if not COMMIT.fullmatch(row['出典commit']):
            errors.append(f'素材更新 {ident}: 出典commit が必須（7〜40桁の小文字16進）')
        if not row['出典パス']:
            errors.append(f'素材更新 {ident}: 出典パス が必須')
    try:
        chains = index(updates)
    except ChainError as error:
        return errors + [f'素材更新: {error}']
    current = {r['パス']: r['sha256'] for r in assets if r['パス']}
    for path, steps in chains.items():
        heads = [old for old in steps if old not in steps.values()]
        if len(heads) != 1:
            errors.append(f'素材更新 {path}: 連鎖の起点が1つに定まらない（{len(heads)}件）')
            continue
        try:
            end = walk(steps, heads[0])[-1]
        except ChainError as error:
            errors.append(f'素材更新 {path}: {error}')
            continue
        if path in moved and heads[0] != moved[path]['sha256']:
            errors.append(f'素材更新 {path}: 連鎖の起点が素材移行.sha256 と違う')
        if path in current and end != current[path]:
            errors.append(f'素材更新 {path}: 連鎖の終点が素材.sha256 と違う')
        if path not in current:
            errors.append(f'素材更新 {path}: 素材に現存行がない')
    return errors
