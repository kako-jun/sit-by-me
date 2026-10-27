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
    """移行SHA start から素材更新の連鎖を辿った終点が現物SHA actual か（連鎖なしは start == actual）。
    途中のSHAは受理しない。"""
    return walk(chains.get(path, {}), start)[-1] == actual


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
    # 移行時SHAと現物SHAが違うのに素材更新の連鎖がない素材（更新の書き忘れ）
    for path, row in moved.items():
        if path in current and path not in chains and row['sha256'] != current[path]:
            errors.append(f'素材移行 {path}: 移行時SHAと素材.sha256 が違うのに素材更新の連鎖がない')
    return errors


def git_runner(root):
    """root が git リポジトリの最上位ならその git を呼ぶ関数、そうでなければ None（fixture では照合を省く）。"""
    import subprocess
    from pathlib import Path

    def git(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
        return result.returncode, result.stdout

    code, out = git('rev-parse', '--show-toplevel')
    if code != 0 or Path(out.decode().strip()).resolve() != Path(root).resolve():
        return None
    return git


def validate_sources(updates, migration, git):
    """素材更新の出典を git 履歴と照合する。エラー文のリストを返す。

    git(*args) -> (終了コード, 標準出力bytes)。出典commit の実在・新sha256＝出典commit の blob、
    移行行のない path の連鎖起点＝その path の履歴上のどれかの blob を確認する。
    限界: 移行行のない path は、起点が履歴上の blob と一致することしか確かめられず、途中の更新行の欠落は検出できない
    （移行行のある path は validate が移行SHA→現物SHAの連鎖で欠落を検出する）。"""
    import hashlib

    def blob_sha(ref, path):
        code, out = git('cat-file', 'blob', f'{ref}:{path}')
        return hashlib.sha256(out).hexdigest() if code == 0 else None

    errors = []
    moved = {r['新パス'] for r in migration if r['操作'] == 'move' and r['新パス']}
    shallow = git('rev-parse', '--is-shallow-repository')[1].strip() == b'true'
    for row in updates:
        ident, commit, source = row['更新ID'], row['出典commit'], row['出典パス']
        if git('cat-file', '-e', f'{commit}^{{commit}}')[0] != 0:
            hint = '（shallow clone のため履歴が足りない可能性。git fetch --unshallow で全履歴を取得して再実行）' if shallow \
                else ''
            errors.append(f'素材更新 {ident}: 出典commit {commit} が git に存在しない{hint}')
            continue
        if blob_sha(commit, source) != row['新sha256']:
            errors.append(f'素材更新 {ident}: 新sha256 が {commit}:{source} の blob と違う')
    try:
        chains = index(updates)
    except ChainError:
        return errors
    by_path = {}
    for row in updates:
        by_path.setdefault(row['パス'], row)
    for path, steps in chains.items():
        if path in moved:
            continue
        heads = [old for old in steps if old not in steps.values()]
        if len(heads) != 1:
            continue
        source = by_path[path]['出典パス']
        code, out = git('log', '--follow', '--name-only', '--format=%x00%H', '--', source)
        history = set()
        if code == 0:
            for block in out.decode().split('\x00')[1:]:  # 各コミット時点のパス（改名を辿った名前）で blob を引く
                lines = [line for line in block.splitlines() if line]
                if len(lines) >= 2:
                    history.add(blob_sha(lines[0], lines[1]))
        if heads[0] not in history:
            errors.append(f'素材更新 {path}: 連鎖の起点が移行行にも git 履歴上の blob にもない')
    return errors
