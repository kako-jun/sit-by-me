#!/usr/bin/env bash
# サンプル専用マップ SMP-01 の背景を imagegen で N テイク生成する（承認済みのときだけ。決定 DEMO.sample-bg-last-place-approved、Issue #281）。
# 使い方: sample_field_run.sh [N=4]   前提: sample_field_build.py build で e2/send.txt を作ってある。参照はクリーンモック1枚だけ。
# 生成画像は目視しない（実寸と偽造PNG検査の数値だけ。見るのは kako-jun）。oblique_e2_run.sh と同じ codex exec の形。
set -u
N=${1:-4}
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
D=docs/production/sample-field; OUT=$D/e2
[ -f "$OUT/send.txt" ] || { echo "$OUT/send.txt が無い。sample_field_build.py build を先に実行する" >&2; exit 1; }
GI=$HOME/.codex/generated_images
mkdir -p "$OUT"; ls "$GI" > "$OUT/.gi-before.txt" 2>/dev/null
for i in $(seq 1 "$N"); do
  [ -e "$OUT/take$i.png" ] && { echo "skip take$i (exists)"; continue; }
  BODY=$(cat "$OUT/send.txt")
  codex exec -s workspace-write --skip-git-repo-check -c model_reasoning_effort="high" \
"Invoke the \$imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), edit-mode with the 1 attached reference image (the clean mock = EDIT TARGET; its positions and sizes are the only truth), size 1672x941, then save the REAL generated PNG (decode the tool result, do not resize or modify it) into the current workspace at $OUT/take$i.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with ImageMagick, PIL, canvas or code.

$BODY" -i "$D/SMP-01-clean.png" < /dev/null > "$OUT/codex-take$i.log" 2>&1 &
done
wait
for i in $(seq 1 "$N"); do
  if [ -f "$OUT/take$i.png" ]; then
    uv run --with pillow python3 -I -c "
from PIL import Image; import sys
im=Image.open(sys.argv[1]); print(sys.argv[1], im.size, 'OK' if im.size==(1672,941) else 'size NG: 再生成が必要（リサイズで通さない）')" "$OUT/take$i.png"
  else echo "take$i.png が出来なかった（$OUT/codex-take$i.log の末尾を見る）" >&2; fi
  [ -f "$OUT/codex-take$i.log" ] && { cut -c1-240 "$OUT/codex-take$i.log" | grep -v '^[A-Za-z0-9+/=]\{200,\}' | tail -40 > "$OUT/codex-take$i.log.txt"; rm "$OUT/codex-take$i.log"; }
done
