#!/usr/bin/env python3
"""docs/ledger/BGM録音.yaml から BGM 入力素材(新世界より)を再取得する。

音源は git 管理外の ~/data/sit-bgm/raw/{録音ID}/{楽章}.{ext} に保存する(リポ内には置かない)。
実行: uv run python3 scripts/fetch_bgm_sources.py [--ids a,b] [--max-rank B] [--force] [--probe-only]
  - ファイルパス列が空/備考が「手動取得要」の行は取得しない(IMSLP 等)。
  - 取得後 ffprobe で長さ(秒)と形式を測り、YAML に書き戻す。
  - 外部 HTTPS は curl 経由(施設内プロキシ環境でも通る)。
"""
import argparse, json, os, subprocess, sys, tempfile, time
from pathlib import Path
import yaml

YAML_PATH = Path(__file__).resolve().parent.parent / "docs" / "ledger" / "BGM録音.yaml"
RAW_ROOT = (Path.home() / "data" / "sit-bgm" / "raw").resolve()
UA = "sit-bgm-fetch/1.0 (personal research; contact via repo owner)"
RANK_ORDER = {"A": 0, "B": 1, "C": 2, "X": 3}
COL_PATH, COL_URL, COL_DUR, COL_FMT, COL_NOTE, COL_RANK, COL_ID = "ファイルパス", "出典URL", "ffprobeで実測した長さ(秒)", "形式", "備考", "ランク", "録音ID"


MIN_BYTES = 10_000  # これ未満は HTML エラーページ等とみなす
AUDIO_EXT = {".ogg", ".oga", ".mp3", ".flac", ".wav", ".opus"}


def valid_audio(path: Path) -> bool:
    """最小サイズ・拡張子・ffprobe で音声と判定できるか。"""
    if path.suffix.lower() not in AUDIO_EXT or path.stat().st_size < MIN_BYTES:
        return False
    dur, _ = probe(path)
    return dur is not None and dur > 0


def download(url: str, dest: Path) -> bool:
    if not url.startswith("https://"):
        print(f"https 以外の URL は取得しない(手動扱い): {url}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    tmp.unlink(missing_ok=True)  # 古い .part は再開せず、やり直す
    for attempt in range(4):
        tmp.unlink(missing_ok=True)
        r = subprocess.run(["curl", "-sSL", "--fail", "--proto", "=https", "--proto-redir", "=https",
                            "-A", UA, "-m", "900", "-o", str(tmp), url])
        if r.returncode == 0 and tmp.exists():  # 空応答もリトライせず検証に回す
            # 拡張子を保ったまま検証できるよう、検証用の名前に一時リネーム
            chk = dest.with_name(dest.name + ".chk" + dest.suffix)
            tmp.rename(chk)
            if valid_audio(chk):
                chk.rename(dest)
                return True
            print(f"不正なファイル(音声と判定できない/小さすぎる)を削除: {url}")
            chk.unlink(missing_ok=True)
            return False  # 決定的な不正はリトライしない(リトライは curl 失敗・429 のみ)
        if attempt == 3:  # 最終試行の失敗後は待たない
            break
        time.sleep(30 * (attempt + 1) if "wikimedia.org" in url else 3 * (attempt + 1))  # Wikimedia は 429 になりやすい
    tmp.unlink(missing_ok=True)
    return False


def probe(path: Path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,format_name:stream=codec_name",
                        "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        return None, None
    j = json.loads(r.stdout or "{}")
    dur = float(j.get("format", {}).get("duration", 0) or 0)
    codec = (j.get("streams") or [{}])[0].get("codec_name", "")
    return round(dur, 2), f"{j.get('format', {}).get('format_name', '')}/{codec}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="カンマ区切りの録音ID(省略で全部)")
    ap.add_argument("--max-rank", default="X", choices=list(RANK_ORDER), help="このランク以上のみ(A<B<C<X)")
    ap.add_argument("--force", action="store_true", help="既存ファイルも再取得")
    ap.add_argument("--probe-only", action="store_true", help="取得せず既存ファイルの ffprobe だけ更新")
    a = ap.parse_args()
    ids = set(a.ids.split(",")) if a.ids else None

    rows = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    for i, row in enumerate(rows, start=1):
        if row.get(COL_RANK) not in RANK_ORDER:
            sys.exit(f"{YAML_PATH.name} {i}件目 (録音ID={row.get(COL_ID)}): ランク列が A/B/C/X のいずれでもない: {row.get(COL_RANK)!r}")
    original = [dict(r) for r in rows]
    ok = ng = skip = 0
    for row in rows:
        if ids and row[COL_ID] not in ids:
            continue
        if RANK_ORDER[row[COL_RANK]] > RANK_ORDER[a.max_rank]:
            continue
        if not row[COL_PATH] or row[COL_NOTE].startswith("手動取得要") or not row[COL_URL].startswith("http"):
            print(f"SKIP(手動) {row[COL_ID]} {row['楽章']}")
            skip += 1
            continue
        dest = Path(os.path.expanduser(row[COL_PATH])).resolve()
        if RAW_ROOT not in dest.parents:  # リポ内などへの誤配置防止
            sys.exit(f"保存先が {RAW_ROOT} 配下ではない: {dest}")
        if not a.probe_only and (a.force or not dest.exists() or dest.stat().st_size == 0):
            print(f"GET  {row[COL_ID]} {row['楽章']} <- {row[COL_URL]}", flush=True)
            if not download(row[COL_URL], dest):
                print(f"FAIL {row[COL_ID]} {row['楽章']}")
                ng += 1
                continue
        if dest.exists():
            dur, fmt = probe(dest)
            if dur is None:  # probe 失敗は ok に数えず、既存の長さ・形式列も上書きしない
                print(f"FAIL(probe) {row[COL_ID]} {row['楽章']}")
                ng += 1
                continue
            row[COL_DUR], row[COL_FMT] = str(dur), fmt or ""
            ok += 1
        else:
            ng += 1
    if rows == original:  # 内容が変わらなければ書き込まない
        print(f"done: ok={ok} fail={ng} skipped(manual)={skip}")
        return
    # 一時ファイルに書いてから rename(原子的更新)
    fd, tmp_name = tempfile.mkstemp(dir=YAML_PATH.parent, prefix=".bgm-recordings.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("# 表: BGM録音。移行後はこの YAML が正本。全値は文字列。\n")
            yaml.safe_dump(rows, f, allow_unicode=True, sort_keys=False, default_style='"', width=100000)
        os.replace(tmp_name, YAML_PATH)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    print(f"done: ok={ok} fail={ng} skipped(manual)={skip}")


if __name__ == "__main__":
    main()
