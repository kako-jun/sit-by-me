#!/usr/bin/env bash
# サンプル専用マップ SMP-01 の背景を imagegen で N テイク生成する（承認済みのときだけ。決定 DEMO.sample-bg-last-place-approved、Issue #281）。
# 使い方: sample_field_run.sh [N=2]（最大2。3以上は拒否）   前提: sample_field_build.py build で e2/send.txt を作ってある。参照はクリーンモック1枚だけ。
# 生成画像は目視しない（実寸と偽造PNG検査の数値だけ。見るのは kako-jun）。oblique_e2_run.sh と同じ codex exec の形。
set -u
RC=0
N=${1:-2}   # 同時生成は2件まで（pitfalls G）。既定2
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
D=docs/production/sample-field; OUT=$D/e2
[ -f "$OUT/send.txt" ] || { echo "$OUT/send.txt が無い。sample_field_build.py build を先に実行する" >&2; exit 1; }
GI=$HOME/.codex/generated_images
[ "$N" -le 2 ] || { echo "同時生成は2件まで" >&2; exit 1; }
mkdir -p "$OUT"; : > "$OUT/.sizes"; ls "$GI" > "$OUT/.gi-before.txt" 2>/dev/null
NEW=()
for i in $(seq 1 "$N"); do
  [ -e "$OUT/take$i.png" ] && { echo "skip take$i (exists)"; continue; }
  NEW+=("$i")
  BODY=$(cat "$OUT/send.txt")
  codex exec -s workspace-write --skip-git-repo-check -c model_reasoning_effort="high" \
"Invoke the \$imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), edit-mode with the 1 attached reference image (the clean mock = EDIT TARGET; its positions and sizes are the only truth), size 1672x941, then save the REAL generated PNG (decode the tool result, do not resize or modify it) into the current workspace at $OUT/take$i.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with ImageMagick, PIL, canvas or code.

$BODY" -i "$D/SMP-01-clean.png" < /dev/null > "$OUT/codex-take$i.log" 2>&1 &
done
wait
for i in "${NEW[@]:-}"; do
  [ -z "$i" ] && continue
  if [ -f "$OUT/take$i.png" ]; then
    # 偽造対策: 生成前後で ~/.codex/generated_images に新しい画像が増え、take と同一内容（sha256）のものがあること
    SHA=$(sha256sum "$OUT/take$i.png" | cut -d' ' -f1)
    if find "$GI" -newer "$OUT/.gi-before.txt" -type f -name '*.png' -print0 2>/dev/null | xargs -0 -r sha256sum | grep -q "$SHA"; then echo "take$i: generated_images と一致（本物）"; else echo "take$i: generated_images に同一画像が無い。偽造の疑い（ImageMagick 等）。採用しない" >&2; RC=1; fi
    uv run --with pillow python3 -I -c "
from PIL import Image; import sys
im=Image.open(sys.argv[1]); print(sys.argv[1], im.size, 'OK' if im.size==(1672,941) else 'size NG: 再生成が必要（リサイズで通さない）')" "$OUT/take$i.png" | tee -a "$OUT/.sizes"; grep -q 'size NG' "$OUT/.sizes" && RC=1
  else echo "take$i.png が出来なかった（$OUT/codex-take$i.log の末尾を見る）" >&2; fi
  [ -f "$OUT/codex-take$i.log" ] && { cut -c1-240 "$OUT/codex-take$i.log" | grep -v '^[A-Za-z0-9+/=]\{200,\}' | tail -40 > "$OUT/codex-take$i.log.txt"; rm "$OUT/codex-take$i.log"; }
done
exit $RC
