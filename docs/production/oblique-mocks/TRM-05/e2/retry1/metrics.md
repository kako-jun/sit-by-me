# E2 測定 TRM-05 e2/retry1

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.741 | 0.29 | 5.21 | 0.571 | regions | True |
| 2 | FAIL | 0.796 | 0.32 | 4.8 | 0.286 | regions | True |
| 3 | FAIL | 0.887 | 0.445 | 3.31 | 0.643 | regions | True |
| 4 | FAIL | 0.837 | 0.363 | 3.88 | 0.5 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 0.85 | 32/ENSW | 0.0003/0.1867/0.0376 | 0.0026 |
| 2 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 0.95 | 27/ENSW | 0.0004/0.1694/0.0231 | 0.0019 |
| 3 | FAIL | FAIL | density:floor,density:wall,outside_evergreen | 0.97 | 24/ENSW | 0.0006/0.1653/0.0648 | 0.0006 |
| 4 | FAIL | FAIL | density:slab_front,outside_evergreen | 1.06 | 33/ENSW | 0.0002/0.1057/0.0289 | 0.0293 |
| ref | - | - | - | 1.0 | 40/ENSW | 0.0315/0.0543/0.0088 | 0.0011 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 0.8 / 0.71 / dE3.7 | 0.86 / 0.73 / dE3.9 | 1.38 / 0.82 / dE3.8 | 0.88 / 0.84 / dE4.3 | 0.0096, 5.325 |
| slab_front | 0.26 / 0.56 / dE10.7 | 0.45 / 0.71 / dE7.9 | 0.75 / 0.79 / dE6.3 | 0.38 / 0.64 / dE7.1 | 0.1304, 5.851 |
| outside | 1.48 / 1.11 / dE6.1 | 1.23 / 1.09 / dE4.2 | 1.27 / 1.1 / dE5.8 | 0.82 / 0.86 / dE11.3 | 0.0749, 5.211 |
| floor | 0.5 / 1.01 / dE10.7 | 0.58 / 1.06 / dE5.9 | 0.55 / 1.03 / dE10.1 | 0.65 / 1.08 / dE11.7 | 0.0521, 5.885 |
| wall | 0.65 / 0.97 | 0.62 / 0.97 | 0.55 / 0.91 | 0.73 / 0.99 | 0.0986, 6.315 |
| objects | 0.71 / 0.99 | 0.89 / 1.01 | 0.8 / 0.98 | 1.27 / 1.05 | 0.0527, 6.009 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 8.0・窓±8内 2/3・戸口±8内 2/3・全体ずれ中央値 [1.0, -6.0]; take2: 窓の平均|dy| 14.0・窓±8内 1/3・戸口±8内 1/3・全体ずれ中央値 [-1.0, -21.0]; take3: 窓の平均|dy| 4.7・窓±8内 3/3・戸口±8内 1/3・全体ずれ中央値 [1.0, -6.0]; take4: 窓の平均|dy| 1.3・窓±8内 3/3・戸口±8内 1/3・全体ずれ中央値 [-2.0, -4.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 4.4（基準 ≤8.0）→ OK

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-05.door-hall | (40,-40) | (8,-6) | (-4,-34) | (4,-20) |
| door:TRM-05.door-outside | (-8,0) | (-12,-28) | (6,2) | (-18,2) |
| door:TRM-05.door-back | (-6,-2) | (-2,-38) | (6,-40) | (-6,-4) |
| window:TRM-05.win-s1 | (2,-6) | (4,-10) | (-2,-6) | (-4,0) |
| window:TRM-05.win-s2 | (4,-6) | (-18,-28) | (0,-6) | (4,2) |
| window:TRM-05.win-n1 | (4,-12) | (4,-4) | (2,2) | (2,2) |
| box:stove | (-6,-32) | (38,-38) | (2,-6) | (32,-22) |
| box:sink | (-6,-4) | (-6,-38) | (-6,-6) | (-10,-38) |
| box:cupboard | (-24,-40) | (-16,-34) | (12,-38) | (-6,-40) |
| box:fridge | (4,-4) | (0,8) | (0,0) | (-4,2) |
| box:shelf-w (測定不能) | (-4,-40) | (-2,-40) | (-4,-40) | (-10,-40) |
| box:table | (2,8) | (-2,38) | (2,-40) | (0,-38) |
| box:bench-l | (0,-6) | (4,-14) | (-2,-24) | (0,-28) |
| box:bench-r (測定不能) | (-36,2) | (-36,6) | (-2,-12) | (-36,-26) |
| box:dresser | (-20,20) | (-2,4) | (0,6) | (-6,-4) |
| box:rock (測定不能) | (-2,-6) | (40,-2) | (40,40) | (38,-6) |
| box:chest | (2,-40) | (4,-40) | (2,4) | (0,0) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 51.13; 全体ピンク残り 0.0
- take2: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 50.75; 全体ピンク残り 0.0
- take3: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 51.22; 全体ピンク残り 0.0
- take4: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 49.02; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 4.62
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 4.68
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 4.96
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 4.13
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 4.68
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 4.02
  }
 ],
 "mean_pairwise_chamfer_px": 4.51,
 "blurred_lum_pixel_std_room_mean": 15.86,
 "region_shift_sd": {
  "door:TRM-05.door-hall": {
   "dx_sd": 16.7,
   "dy_sd": 13.2
  },
  "door:TRM-05.door-outside": {
   "dx_sd": 8.8,
   "dy_sd": 12.7
  },
  "door:TRM-05.door-back": {
   "dx_sd": 4.9,
   "dy_sd": 18.0
  },
  "window:TRM-05.win-s1": {
   "dx_sd": 3.2,
   "dy_sd": 3.6
  },
  "window:TRM-05.win-s2": {
   "dx_sd": 9.1,
   "dy_sd": 11.2
  },
  "window:TRM-05.win-n1": {
   "dx_sd": 1.0,
   "dy_sd": 5.7
  },
  "box:stove": {
   "dx_sd": 18.8,
   "dy_sd": 12.1
  },
  "box:sink": {
   "dx_sd": 1.7,
   "dy_sd": 16.5
  },
  "box:cupboard": {
   "dx_sd": 13.4,
   "dy_sd": 2.4
  },
  "box:fridge": {
   "dx_sd": 2.8,
   "dy_sd": 4.3
  },
  "box:shelf-w": {
   "dx_sd": 3.0,
   "dy_sd": 0.0
  },
  "box:table": {
   "dx_sd": 1.7,
   "dy_sd": 32.8
  },
  "box:bench-l": {
   "dx_sd": 2.2,
   "dy_sd": 8.6
  },
  "box:bench-r": {
   "dx_sd": 14.7,
   "dy_sd": 12.6
  },
  "box:dresser": {
   "dx_sd": 7.8,
   "dy_sd": 8.6
  },
  "box:rock": {
   "dx_sd": 17.9,
   "dy_sd": 19.4
  },
  "box:chest": {
   "dx_sd": 1.4,
   "dy_sd": 21.0
  }
 },
 "region_shift_sd_mean_px": 9.76
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
