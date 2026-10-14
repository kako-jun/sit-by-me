# キャラ素材の加工

`key_grid.py`: imagegen で作った 3x3 のポーズグリッド（クロマキー背景）を透過にして、コマごとに切り出す。各コマの体を先に決め、枠をはみ出した刃・手足は最寄りの体に付けるので、枠で切れない。右向きのコマは番号（0 始まり）を指定して左右反転し、左向きにそろえる。向きの判定は縮小一覧では誤るので、顔を拡大して見る。

```
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/otton-grid.png assets/characters/poses otton green 8
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/nam-grid.png assets/characters/poses nam green
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/shah-grid.png assets/characters/poses shah magenta 0,1
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/peiko-grid.png assets/characters/poses peiko green
```

シャーは服が緑なので背景をマゼンタにしている。シャーの ready（1）は、刀は左でも顔が右を向いていたため反転している（反転すると顔が敵を向き、刀を頭の後ろに振りかぶった構えになる）。ペー子の `down` だけはグリッドで倒れなかったため、`raw/peiko-down.png` を単独で生成して差し替えた。

## 園服版（お遊戯会の劇用）

`poses/raw/{name}-uniform-grid.png` は、上の 4 枚のグリッドを編集元に、服だけを `masters/{name}-kindergarten-uniform.png` の園服（鞄なし・上履き）に差し替えて生成したもの。ポーズ・コマ位置・向きは元のグリッドと同じなので、反転の指定も同じにする。

```
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/otton-uniform-grid.png assets/characters/poses otton-uniform green 8
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/nam-uniform-grid.png assets/characters/poses nam-uniform green
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/shah-uniform-grid.png assets/characters/poses shah-uniform magenta 0,1
uv run --with pillow --with numpy --with scipy python3 -I assets/characters/tools/key_grid.py \
  assets/characters/poses/raw/peiko-uniform-grid.png assets/characters/poses peiko-uniform green
```

ペー子の `down` は今回もグリッドで倒れなかったので、`raw/peiko-down.png` を同じく園服に編集した `raw/peiko-uniform-down.png` を、緑キーで透過・タイトに切り抜いて `peiko-uniform-down.png` を差し替えた。
