#!/usr/bin/env bash
# E2: クリーンモック編集元の imagegen を N テイク並列生成 → 本物確認 → 測定 → ログ縮約まで1コマンド。
# テイク数は4で固定（既定 N=4）。自動の順位づけ・上位絞り込みはしない。全テイクを kako-jun が目視で判定する。測定値は参考情報と不具合検出（崩れ・混入・偽造PNG）にのみ使う。
# 使い方: [REF_IMAGE=git:REV:PATH] [DRY_RUN=1] oblique_e2_run.sh MAP [N=4] [ROUND(既定 e2)] [PROMPT_FILE]  （DRY_RUN=1 は生成せずプロンプトと参考画像だけ確認）
#  例 A案（文章のみ。参照=クリーンモック＋素材見本）:
#       oblique_e2_run.sh TRM-02 4 e2/round2a
# プロンプト既定: <MAP>-edit-prompt.txt（『# ---- 台帳の出所 ----』行より前=DRAFT/BLOCKED の末尾は imagegen に渡さない。見た目と許す/禁じる装飾を含む。oblique_build.py が生成）＋参照・出力の節。
# 前提: プロンプト先頭で $imagegen を明示起動（しないと ImageMagick 偽造PNGを掴む）。生成画像は目視しない（数値のみ）。
# 測定の基準画像: REF_IMAGE。装飾量・層の測定は基準画像があるときだけ出る。
set -u
MAP=${1:?MAP}; N=${2:-4}; ROUND=${3:-e2}
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
M=docs/production/oblique-mocks/$MAP
OUT=$M/$ROUND
PROMPT=${4:-$OUT/prompt.txt}
GI=$HOME/.codex/generated_images
SCHED="uv run python3 -I .claude/skills/sit-field-background/tools/oblique_e2_schedule.py"
# 依存グラフ: 親が全て確定済みでなければ起動しない（直列）。確定済みの親の正本画像を参考画像（扉・材質・家具・装飾のデザインの参考のみ）として自動で付ける
# 拒否された実行が副作用（空ディレクトリ・swatch のコピー）を残さないよう、check を mkdir／cp より先に実行する
$SCHED check "$MAP" || exit 1
mkdir -p "$OUT" "$M/e2"
# プロンプトの『台帳の出所』行（台帳 プロンプト文面.yaml が出す DRAFT/BLOCKED 末尾の始まり）。スクリプトと生成側の文字列が乖離しないよう tests/test_ledger.py が全 edit-prompt との一致を縛る
LEDGER_MARKER_RE='^# ---- 台帳の出所'
# 素材見本シート（material-swatch-sheet。採用画像と以前の良い絵から切った素材だけのクロップ。tools/oblique_material_sheet.py で作る）を常に2枚目として付ける。旧の段ボール断面の見本（テープ入り）は付けない（台座の前縁は素の断面が既定で、テープ・糊は継ぎ目にだけ。決定 SIT.base-edge-decor-random）
SHEET_SRC=docs/production/oblique-mocks/material-swatch/material-swatch-sheet.webp
SHEET_PNG="$OUT/material-swatch-sheet.png"
[ -f "$SHEET_SRC" ] || { echo "素材見本シート $SHEET_SRC が無い。oblique_material_sheet.py build を実行する" >&2; exit 1; }
uv run --with pillow python3 -I -c "
from PIL import Image
import sys
Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2])" "$SHEET_SRC" "$SHEET_PNG"
REFS=(-i "$M/$MAP-clean.png" -i "$SHEET_PNG")
NREF=2
PARENT_IDS=()
while IFS='=' read -r PID PPATH; do
  [ -z "$PID" ] && continue
  case "$PPATH" in *.webp) uv run --with pillow python3 -I -c "
from PIL import Image
import sys
Image.open(sys.argv[1]).convert('RGB').save(sys.argv[2])" "$PPATH" "$OUT/ref-$PID.png"; PPATH="$OUT/ref-$PID.png";; esac
  REFS+=(-i "$PPATH"); NREF=$((NREF+1)); PARENT_IDS+=("$PID")
done < <($SCHED refs "$MAP")
# EXTRA_REFS="ID=path ID=path"（任意）: 採用前の隣接MAPの絵を、つなぎ目の参考として追加で付ける（親ではないので生成のゲートには影響しない。道の縁の境界の種類・位置・用水の流れ・地面の材質だけを合わせる）
EXTRA_IDS=()
for KV in $(printf '%s\n' "${EXTRA_REFS:-}"); do
  [ -z "$KV" ] && continue
  REFS+=(-i "${KV#*=}"); NREF=$((NREF+1)); EXTRA_IDS+=("${KV%%=*}")
done
if [ ! -f "$PROMPT" ]; then
  sed "/$LEDGER_MARKER_RE/,\$d" "$M/$MAP-edit-prompt.txt" > "$PROMPT"
  # プロンプトの REFERENCE IMAGES 節に載るが添付しない MAP（親でないもの。例: 時期差分MAPの本堂 TRM-04）=テキスト参照のみ
  TEXT_ONLY=()
  while read -r TID; do
    [ -z "$TID" ] && continue
    case " ${PARENT_IDS[*]:-} " in *" $TID "*) continue;; esac
    TEXT_ONLY+=("$TID")
  done < <(awk '/^REFERENCE IMAGES/{f=1;next} f&&/^$/{exit} f&&/^- [A-Z][A-Z][A-Z]-[0-9][0-9](-[a-z]+)?: /{sub(/^- /,"");sub(/:.*/,"");print}' "$PROMPT")
  {
  echo; echo "ATTACHED IMAGES（添付画像の役割。全部で $NREF 枚）:"
  echo "1. 1枚目 = 編集元（EDIT TARGET）: 色付きの箱で作った間取りのクリーンモック。位置・大きさ（COORDINATES の座標・層の境界・壁・戸口・窓・家具の箱・開口）は**この画像だけが正本**。表面を工作の細かな装飾で塗り直す。"
  echo "2. 2枚目 = 素材見本シート（CRAFT MATERIAL SHEET）: 採用済みの手作りミニチュアと以前の良い絵から切った素材だけのクロップ15枚（綿の雪・紙粘土の瓦と壁・スポンジの木・石粉粘土の石・段ボール断面・黒紙の道・爪楊枝と割り箸の竹垣・鉄道模型の木・青い樹脂の用水）。**素材の質感・作り方の参考のみ**: 全てこの見本のような工作の素材の手触り・粗さ・つくりもの感で仕上げる。構図・配置・物の形・色の配置は参考にしない。"
  N3=3
  for PID in "${PARENT_IDS[@]:-}"; do
    [ -z "$PID" ] && continue
    echo "$N3. $N3 枚目 = 確定済みの $PID の採用画像（参考のみ）: **扉・材質・家具・装飾のデザイン**の参考にする。構図・配置・位置・大きさはコピーしない（位置は1枚目のクリーンモックが正本）。台座の前縁は COORDINATES の指定だけに従う（指定が無い MAP は素の段ボール断面。この画像の前縁の飾りは真似しない）。この MAP と接続する扉・渡り廊下・共有する家具は $PID と同じデザインにする。外観の渡り廊下・扉は確定済みの内部と一致させる。"
    N3=$((N3+1))
  done
  for PID in "${EXTRA_IDS[@]:-}"; do
    [ -z "$PID" ] && continue
    echo "$N3. $N3 枚目 = 隣接する $PID の絵（つなぎ目の参考のみ）: この MAP と接する端で、道の両脇の境界の種類・位置・用水の流れる向きと位置・地面と雪の材質だけを合わせる。構図・建物・木・位置・大きさはコピーしない（位置は1枚目のクリーンモックが正本）。"
    N3=$((N3+1))
  done
  if [ "${#TEXT_ONLY[@]}" -gt 0 ]; then
    echo "※ 添付画像は上の $NREF 枚だけ。プロンプト中の REFERENCE IMAGES 節に ${TEXT_ONLY[*]} のパス・sha256 が書かれていても、添付が無いものはテキスト上の参照にすぎない（画像として見えていない）。"
  fi
  echo; echo "OUTPUT: one image, 1672x941 landscape (if exactly that size is impossible, the nearest allowed size with the same aspect ratio). Do not crop, rotate, zoom or re-frame the mock."
  } >> "$PROMPT"
fi
if [ "${DRY_RUN:-0}" = 1 ]; then echo "DRY_RUN: 生成しない。参考画像 $NREF 枚: ${REFS[*]}"; echo "prompt: $PROMPT"; exit 0; fi
ls "$GI" > "$OUT/.gi-before.txt"
date -Iseconds > "$OUT/.started"
for i in $(seq 1 "$N"); do
  [ -e "$OUT/take$i.png" ] && { echo "skip take$i (exists)"; continue; }
  BODY=$(cat "$PROMPT")
  codex exec -s workspace-write --skip-git-repo-check -c model_reasoning_effort="high" \
"Invoke the \$imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), edit-mode with the $NREF attached reference images in the order described below, size 1672x941, then save the REAL generated PNG (decode the tool result, do not resize or modify it) into the current workspace at $OUT/take$i.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate — output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not use files already present in ~/.codex/generated_images made by other runs; copy only the image generated by this call. Report the saved file path.

$BODY" "${REFS[@]}" < /dev/null > "$OUT/codex-take$i.log" 2>&1 &
done
wait
ls "$GI" > "$OUT/.gi-after.txt"
date -Iseconds > "$OUT/.finished"
REFARG=()
[ -n "${REF_IMAGE:-}" ] && REFARG=(--ref "$REF_IMAGE")
uv run --with numpy --with opencv-python-headless --with pillow python3 -I \
  .claude/skills/sit-field-background/tools/oblique_e2_measure.py "$MAP" --round "$ROUND" --takes "$N" "${REFARG[@]}"
# 生ログは base64 画像で数MBになる。先頭だけ残して置き換える（測定後。偽造ツール使用の有無は metrics.json に記録済み）
for i in $(seq 1 "$N"); do
  [ -f "$OUT/codex-take$i.log" ] && { cut -c1-240 "$OUT/codex-take$i.log" | grep -v '^[A-Za-z0-9+/=]\{200,\}' | head -60 > "$OUT/codex-take$i.log.txt"; rm "$OUT/codex-take$i.log"; }
done
echo "== 全テイク（kako-jun が目視で判定する。測定は参考）=="
for i in $(seq 1 "$N"); do echo "$ROOT/$OUT/take$i.png  (重ね: $ROOT/$OUT/overlay-take$i.png)"; done
