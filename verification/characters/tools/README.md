# キャラ素材の加工

> 元グリッド（切り出し前の原本）は保管しない（#68決定、2026-10-19）。以下の `<生成グリッド>/` はスクラッチ等の一時置き場を指す。過去の原本は git 履歴 `1bb09d0` の `assets/images/characters/Cxxx/raw/` から復元できる。

## 透過の方式（2026-10-14 に統一）

**既定は「透過のまま生成した RGBA」**。各ツールの背景の指定に `alpha` を渡す。クロマキー（`green` / `magenta`）は、RGBA で返らなかったときの代替。同じグリッドで比べた結果、クロマキーは刃・リボンの青い光に緑が混ざって濁り、透過の直接生成は光が自分の色のまま半透明で残った。抜き方は `keying.py` に1つだけ置き、各ツールはそれを使う。

ポーズや構図をクロマキー背景で決めてから、その画像を編集元に背景だけを透過にしてもよい（小学生のセットはこの2段で作った）。下の幼稚園期の手順はクロマキーで作った当時のもので、結果を再現するにはそのまま `green` / `magenta` を渡す。手順の全体は `.claude/skills/sit-characters`。

出力は全ツール非可逆WebP（品質85・アルファ保持。imagegen出力のPNGが入力、正本パスの .webp が出力。PNGは残さない）。

`key_single.py`: 1体だけの画像を透過にしてタイトに切り抜く（グリッドで作れなかったコマの差し替え用）。`flip` を付けると左右反転する。

## 戦闘ポーズ

`key_grid.py`: imagegen で作った 3x3 のポーズグリッドを透過にして、コマごとに切り出す。各コマの体を先に決め、枠をはみ出した刃・手足は最寄りの体に付けるので、枠で切れない。右向きのコマは番号（0 始まり）を指定して左右反転し、左向きにそろえる。向きの判定は縮小一覧では誤るので、顔を拡大して見る。

```
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C001-grid.png assets/images/characters/C001/poses C001 green 8
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C002-grid.png assets/images/characters/C002/poses C002 green
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C003-grid.png assets/images/characters/C003/poses C003 magenta 0,1
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C004-grid.png assets/images/characters/C004/poses C004 green
```

シャーは服が緑なので背景をマゼンタにしている。シャーの ready（1）は、刀は左でも顔が右を向いていたため反転している（反転すると顔が敵を向き、刀を頭の後ろに振りかぶった構えになる）。ペー子の `down` だけはグリッドで倒れなかったため、単独生成した `peiko-down` 画像 を単独で生成して差し替えた。

## 園服版（お遊戯会の劇用）

`{name}-uniform-grid.png` は、上の 4 枚のグリッドを編集元に、服だけを `masters/{name}-kindergarten-uniform.png` の園服（鞄なし・上履き）に差し替えて生成したもの。ポーズ・コマ位置・向きは元のグリッドと同じなので、反転の指定も同じにする。

```
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C001-uniform-grid.png assets/images/characters/C001/poses C001-uniform green 8
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C002-uniform-grid.png assets/images/characters/C002/poses C002-uniform green
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C003-uniform-grid.png assets/images/characters/C003/poses C003-uniform magenta 0,1
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_grid.py \
  <生成グリッド>/C004-uniform-grid.png assets/images/characters/C004/poses C004-uniform green
```

ペー子の `down` は今回もグリッドで倒れなかったので、単独生成した `peiko-down` 画像 を同じく園服に編集した `peiko-uniform-down` 元画像 を `key_single.py ... green` で透過・タイトに切り抜いて `peiko-uniform-down.webp` を差し替えた。

## フィールドの歩き（幼稚園期・スノーボードウェア）

`key_walk.py`: 4行×3列の歩きグリッドを透過にし、12コマを同じ大きさの枠へ足元そろえで切り出す。背景指定は `alpha`（透過生成）またはクロマキー色。絵がセル境界をまたぐので、`key_grid.py` と同じく全体でかたまりを見つけて重心でコマへ振り分ける。生成では行順が変わることがあるので、顔と背中を拡大して向きを確認し、引数で各行を指定する。方向は `down`, `left`, `right`, `up`, `downleft`, `downright`, `upleft`, `upright`。出力は `walk/{name}-walk-{dir}-{1,2,3}.webp`。

```
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_walk.py \
  <生成グリッド>/C001-walk-grid.png assets/images/characters/C001/walk C001 green down,right,left,up
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_walk.py \
  <生成グリッド>/C002-walk-grid.png assets/images/characters/C002/walk C002 green down,right,left,up
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_walk.py \
  <生成グリッド>/C003-walk-grid.png assets/images/characters/C003/walk C003 magenta down,left,right,up
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_walk.py \
  <生成グリッド>/C004-walk-grid.png assets/images/characters/C004/walk C004 green down,right,left,up
uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools/key_walk.py \
  <生成グリッド>/C001-diagonal-walk-grid.png assets/images/characters/C001/walk C001 alpha downleft,downright,upleft,upright
```

コマ数（各方向3コマ）と枠の大きさは仮。name-name にフィールド移動のモードができたら、その仕様に合わせる。

## 小学生（少年編前半）

透過のまま生成したグリッドから切り出す（`alpha`）。ポーズの配置は幼稚園のグリッド、人物と服は `masters/{name}-elementary.png` を参照して、まずクロマキー背景で生成し、その画像の背景だけを透過にする編集をかけた（`{name}-elementary-grid.png` / `{name}-elementary-walk-grid.png` は透過後のもの）。反転の指定は幼稚園と同じ。歩きは4人とも上から 下・左・右・上 の順で出た。ペー子の `down` は今回もグリッドで倒れなかったので、単独で生成して透過にした `raw/peiko-elementary-down.png` を使う。

```
T="uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools"
$T/key_grid.py <生成グリッド>/C001-elementary-grid.png assets/images/characters/C001/poses C001-elementary alpha 8
$T/key_grid.py <生成グリッド>/C002-elementary-grid.png assets/images/characters/C002/poses C002-elementary alpha
$T/key_grid.py <生成グリッド>/C003-elementary-grid.png assets/images/characters/C003/poses C003-elementary alpha 0,1
$T/key_grid.py <生成グリッド>/C004-elementary-grid.png assets/images/characters/C004/poses C004-elementary alpha
$T/key_single.py <生成グリッド>/C004-elementary-down.png assets/images/characters/C004/poses/C004-elementary-down.webp alpha
$T/key_walk.py <生成グリッド>/{C-ID}-elementary-walk-grid.png assets/images/characters/{C-ID}/walk {C-ID}-elementary alpha down,left,right,up
```

## 振り分けの方式（keying.split）

透過生成の光は薄く広がって隣のコマとつながるので、かたまり単位でなく画素単位で振り分ける。体は濃い部分（alpha>0.5）のかたまりのうち重心のあるコマで最大のもの。残りの見える画素は、いちばん近い体へ付ける。足元より下に丸ごと離れて浮いた小さな塊（光の粒）は捨てる（付くと切り抜きの下端が足でなくなり、台座から浮く）。2026-10-14 にこの方式へ変えたとき、幼稚園期の切り出しも出し直した（差は縁の薄い画素と、足元の下の光の粒が取れたことだけ）。

## 車椅子の主人公（小学生）

`{otton,nam}-elementary-wheelchair-grid.png`（戦闘 3x3）と `-walk.png`（移動 4x3、ハンドリムをこぐ）は、`masters/{name}-elementary-wheelchair.png` と立ちポーズのグリッドを参照して、透過のまま生成した。車椅子は斜めから見た形で出るので、向きは**椅子の向き（前輪のキャスターが敵側＝左）**で判定する。戦闘グリッドはオトンの 3・7・9 番、ナムの 5 番が右向きだったので反転した。移動はオトンの 2 行目・3 行目がどちらも右向きだったため、3 行目を反転して左向きにしている。

```
T="uv run --with pillow --with numpy --with scipy python3 -I verification/characters/tools"
$T/key_grid.py <生成グリッド>/C001-elementary-wheelchair-grid.png assets/images/characters/C001/poses C001-elementary-wheelchair alpha 2,6,8
$T/key_grid.py <生成グリッド>/C002-elementary-wheelchair-grid.png assets/images/characters/C002/poses C002-elementary-wheelchair alpha 4
$T/key_walk.py <生成グリッド>/C001-elementary-wheelchair-walk.png assets/images/characters/C001/walk C001-elementary-wheelchair alpha down,right,left,up 2
$T/key_walk.py <生成グリッド>/C002-elementary-wheelchair-walk.png assets/images/characters/C002/walk C002-elementary-wheelchair alpha down,right,left,up
```

## C001の年齢段階別フィールド歩き

小学生・中学生・青年・壮年の車椅子歩きは各8方向×3コマ（24枚）。同じ頭身と車椅子寸法を保つため、年齢段階を進めるときは前段階の採用済み12コマを同時生成の配置・位相参照として使い、対象年齢のマスターを顔・年齢・衣装の参照にする。4方向の4×3グリッドは対応が保てる場合に一括切り出しできる。斜め4方向のグリッドは行連結、位相重複、色縁が続いたため、2回失敗した段階で同方向・同コマの採用済み画像と対象年齢マスターを使う個別編集に切り替える。グリッドを切り出すときは `key_walk.py` が12体を正しく分離できることを確認し、失敗時に行境界で強制分割しない。

個別編集後はフレーム1〜3を並べ、手の接触状態、ハンドリム位置、肘、スポーク位相を年齢段階間で照合する。移動距離は生成画像の縮小前サイズではなく、最終共通キャンバス上の可視座標で測る。全身が出力端に触れる斜め上方向などは、縦横比を変えずに等方縮小して共通キャンバスへ収め、左右4%以上・上下6%以上の透明余白を確認する。余白追加は端接触がある候補に限り、通常フレームのスケールを一律に変えない。
