# E2 測定 TRM-03 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.809 | 0.029 | 3.58 | 0.176 | edge_margin,regions | True |
| 2 | FAIL | 0.899 | 0.245 | 2.95 | 0.412 | regions | True |
| 3 | FAIL | 0.903 | 0.248 | 2.86 | 0.529 | regions | True |
| 4 | FAIL | 0.906 | 0.144 | 2.64 | 0.471 | edge_margin,regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,outside_evergreen | 1.13 | 49/ESW | 0.001/0.077/0.0309 | 0.0003 |
| 2 | FAIL | FAIL | density:slab_front,outside_trees,outside_evergreen | 1.22 | 60/SW | 0.0001/0.0508/0.0155 | 0.0175 |
| 3 | FAIL | FAIL | outside_trees,outside_evergreen | 1.15 | 72/SW | 0.0001/0.0952/0.0177 | 0.0012 |
| 4 | FAIL | FAIL | outside_trees,outside_evergreen | 0.86 | 66/SW | 0.0008/0.1088/0.0395 | 0.0003 |
| ref | - | - | - | 1.0 | 58/ESW | 0.0169/0.0491/0.0118 | 0.0002 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 2.17 / 0.88 / dE4.9 | 2.05 / 0.88 / dE2.9 | 1.88 / 0.8 / dE5.6 | 3.81 / 1.06 / dE8.4 | 0.0152, 5.62 |
| slab_front | 0.29 / 0.77 / dE6.7 | 0.47 / 0.81 / dE5.1 | 0.81 / 0.85 / dE3.9 | 0.8 / 0.88 / dE5.9 | 0.0969, 5.101 |
| outside | 0.82 / 0.98 / dE10.9 | 0.74 / 0.93 / dE14.7 | 0.93 / 0.98 / dE6.6 | 1.14 / 1.03 / dE8.1 | 0.0813, 5.581 |
| floor | 0.75 / 0.93 / dE13.7 | 0.71 / 0.87 / dE17.1 | 0.89 / 0.93 / dE8.2 | 1.11 / 0.99 / dE9.4 | 0.0825, 5.567 |
| wall | 1.86 / 1.13 | 1.7 / 1.13 | 1.88 / 1.12 | 1.78 / 1.12 | 0.0781, 5.833 |
| objects | 1.3 / 1.22 | 1.1 / 1.18 | 1.61 / 1.24 | 1.68 / 1.27 | 0.0668, 5.676 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 14.7・窓±8内 2/6・戸口±8内 1/3・全体ずれ中央値 [-8.0, -12.0]; take2: 窓の平均|dy| 5.7・窓±8内 4/6・戸口±8内 2/3・全体ずれ中央値 [2.0, -8.0]; take3: 窓の平均|dy| 2.0・窓±8内 6/6・戸口±8内 2/3・全体ずれ中央値 [0.0, -4.0]; take4: 窓の平均|dy| 6.3・窓±8内 2/6・戸口±8内 2/3・全体ずれ中央値 [-2.0, -4.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 11.7（基準 ≤8.0）→ FAIL（全テイクの合幾何+装飾を不合格扱い）

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-03.door-main | (-8,-14) | (-4,32) | (-6,-10) | (2,-10) |
| door:TRM-03.door-residence | (2,-8) | (6,-6) | (0,0) | (4,6) |
| door:TRM-03.door-playroom | (-26,-10) | (0,-4) | (0,0) | (-4,0) |
| window:TRM-03.win-res1 | (0,-8) | (2,-8) | (-2,-4) | (-2,2) |
| window:TRM-03.win-res2 | (-8,-8) | (-10,-8) | (0,-6) | (-30,2) |
| window:TRM-03.win-kg1 | (6,-12) | (-4,0) | (6,-2) | (-16,-8) |
| window:TRM-03.win-kg2 | (2,-20) | (6,-6) | (4,0) | (10,-8) |
| window:TRM-03.win-kg3 | (2,-20) | (6,2) | (2,0) | (-4,-8) |
| window:TRM-03.win-kg4 | (4,-20) | (6,-10) | (2,0) | (0,-10) |
| box:bell | (12,-40) | (0,-12) | (0,-6) | (16,8) |
| box:statue | (-8,-10) | (18,-4) | (-40,20) | (2,-16) |
| box:slide | (-10,-32) | (20,-8) | (-6,-30) | (-2,4) |
| box:swing | (-10,-40) | (30,-26) | (40,-22) | (-4,-10) |
| box:arch-1 | (-10,-10) | (-8,-14) | (-6,-12) | (-6,-4) |
| box:arch-2 | (-8,-10) | (-6,-10) | (-6,-12) | (-6,0) |
| box:arch-3 (測定不能) | (-8,-8) | (-4,-10) | (-2,-10) | (-6,-10) |
| box:arch-4 | (-10,-10) | (2,-8) | (-2,-12) | (-4,-4) |
| box:animal | (2,-20) | (28,-36) | (40,8) | (12,-34) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.004/g0.0; window:TRM-03.win-kg2 w0.008/g0.0; window:TRM-03.win-kg3 w0.0/g0.0; window:TRM-03.win-kg4 w0.002/g0.0; 床lum_std 56.54; 全体ピンク残り 0.0
- take2: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.0/g0.0; window:TRM-03.win-kg2 w0.001/g0.0; window:TRM-03.win-kg3 w0.0/g0.0; window:TRM-03.win-kg4 w0.0/g0.0; 床lum_std 55.58; 全体ピンク残り 0.0
- take3: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.004/g0.0; window:TRM-03.win-kg2 w0.0/g0.0; window:TRM-03.win-kg3 w0.0/g0.0; window:TRM-03.win-kg4 w0.001/g0.0; 床lum_std 61.66; 全体ピンク残り 0.0
- take4: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.01/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.003/g0.0; window:TRM-03.win-kg2 w0.002/g0.0; window:TRM-03.win-kg3 w0.003/g0.0; window:TRM-03.win-kg4 w0.001/g0.0; 床lum_std 62.84; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 2.93
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 2.6
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 2.5
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 2.7
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 2.76
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 2.4
  }
 ],
 "mean_pairwise_chamfer_px": 2.65,
 "blurred_lum_pixel_std_room_mean": 27.83,
 "region_shift_sd": {
  "door:TRM-03.door-main": {
   "dx_sd": 3.7,
   "dy_sd": 18.8
  },
  "door:TRM-03.door-residence": {
   "dx_sd": 2.2,
   "dy_sd": 5.5
  },
  "door:TRM-03.door-playroom": {
   "dx_sd": 10.8,
   "dy_sd": 4.1
  },
  "window:TRM-03.win-res1": {
   "dx_sd": 1.7,
   "dy_sd": 4.1
  },
  "window:TRM-03.win-res2": {
   "dx_sd": 11.0,
   "dy_sd": 4.1
  },
  "window:TRM-03.win-kg1": {
   "dx_sd": 9.1,
   "dy_sd": 4.8
  },
  "window:TRM-03.win-kg2": {
   "dx_sd": 3.0,
   "dy_sd": 7.3
  },
  "window:TRM-03.win-kg3": {
   "dx_sd": 3.6,
   "dy_sd": 8.6
  },
  "window:TRM-03.win-kg4": {
   "dx_sd": 2.2,
   "dy_sd": 7.1
  },
  "box:bell": {
   "dx_sd": 7.1,
   "dy_sd": 17.5
  },
  "box:statue": {
   "dx_sd": 21.2,
   "dy_sd": 13.7
  },
  "box:slide": {
   "dx_sd": 11.6,
   "dy_sd": 15.1
  },
  "box:swing": {
   "dx_sd": 21.4,
   "dy_sd": 10.7
  },
  "box:arch-1": {
   "dx_sd": 1.7,
   "dy_sd": 3.7
  },
  "box:arch-2": {
   "dx_sd": 0.9,
   "dy_sd": 4.7
  },
  "box:arch-3": {
   "dx_sd": 2.2,
   "dy_sd": 0.9
  },
  "box:arch-4": {
   "dx_sd": 4.3,
   "dy_sd": 3.0
  },
  "box:animal": {
   "dx_sd": 14.6,
   "dy_sd": 17.6
  }
 },
 "region_shift_sd_mean_px": 7.88
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
