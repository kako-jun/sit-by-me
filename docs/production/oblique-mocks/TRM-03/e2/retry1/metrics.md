# E2 測定 TRM-03 e2/retry1

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.911 | 0.202 | 2.56 | 0.412 | regions | True |
| 2 | FAIL | 0.779 | 0.035 | 3.83 | 0.059 | edge_margin,regions,window_content | True |
| 3 | FAIL | 0.875 | 0.173 | 3.24 | 0.353 | regions | True |
| 4 | FAIL | 0.933 | 0.254 | 2.18 | 0.529 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,outside_trees,outside_evergreen | 1.15 | 57/SW | 0.0002/0.0536/0.0134 | 0.008 |
| 2 | FAIL | FAIL | density:objects,outside_trees,outside_evergreen | 0.67 | 39/SW | 0.0013/0.409/0.1753 | 0.0006 |
| 3 | FAIL | FAIL | outside_trees,outside_evergreen | 1.09 | 42/SW | 0.002/0.0569/0.0149 | 0.003 |
| 4 | FAIL | FAIL | outside_evergreen | 1.07 | 79/ESW | 0.0004/0.0736/0.0196 | 0.0017 |
| ref | - | - | - | 1.0 | 58/ESW | 0.0169/0.0491/0.0118 | 0.0002 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 2.47 / 0.92 / dE3.7 | 0.73 / 0.87 / dE4.6 | 2.72 / 0.95 / dE4.4 | 1.35 / 0.81 / dE1.6 | 0.0152, 5.62 |
| slab_front | 0.49 / 0.75 / dE6.2 | 0.69 / 0.86 / dE10.6 | 0.68 / 0.9 / dE7.0 | 0.86 / 0.95 / dE5.1 | 0.0969, 5.101 |
| outside | 0.73 / 0.89 / dE13.3 | 0.87 / 1.19 / dE15.5 | 0.97 / 0.96 / dE9.1 | 0.96 / 0.98 / dE5.9 | 0.0813, 5.581 |
| floor | 0.64 / 0.84 / dE15.5 | 0.91 / 1.2 / dE15.7 | 0.89 / 0.91 / dE11.6 | 0.88 / 0.93 / dE7.6 | 0.0825, 5.567 |
| wall | 2.05 / 1.14 | 1.41 / 1.19 | 1.68 / 1.12 | 1.57 / 1.09 | 0.0781, 5.833 |
| objects | 1.36 / 1.21 | 0.57 / 1.04 | 1.46 / 1.18 | 1.56 / 1.19 | 0.0668, 5.676 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 8.7・窓±8内 2/6・戸口±8内 3/3・全体ずれ中央値 [-2.0, -6.0]; take2: 窓の平均|dy| 32.7・窓±8内 1/6・戸口±8内 0/3・全体ずれ中央値 [4.0, -8.0]; take3: 窓の平均|dy| 8.0・窓±8内 1/6・戸口±8内 1/3・全体ずれ中央値 [2.0, -8.0]; take4: 窓の平均|dy| 3.3・窓±8内 6/6・戸口±8内 2/3・全体ずれ中央値 [0.0, -6.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 7.7（基準 ≤8.0）→ OK

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-03.door-main | (4,-4) | (16,24) | (-2,-14) | (0,-30) |
| door:TRM-03.door-residence | (2,-2) | (4,26) | (2,-8) | (0,8) |
| door:TRM-03.door-playroom | (6,-2) | (-16,4) | (-22,-4) | (0,2) |
| window:TRM-03.win-res1 | (-2,-2) | (6,-6) | (38,-6) | (0,-2) |
| window:TRM-03.win-res2 | (0,-2) | (8,-38) | (-12,-6) | (-4,-2) |
| window:TRM-03.win-kg1 | (-2,-12) | (36,-40) | (2,-8) | (2,-6) |
| window:TRM-03.win-kg2 | (-4,-12) | (14,-40) | (2,-10) | (0,-6) |
| window:TRM-03.win-kg3 | (-6,-12) | (32,-36) | (-2,-10) | (0,-4) |
| window:TRM-03.win-kg4 | (-2,-12) | (-28,-36) | (28,-8) | (-2,0) |
| box:bell | (-28,36) | (-4,-20) | (4,-2) | (-6,0) |
| box:statue | (2,-12) | (38,40) | (-2,12) | (-4,36) |
| box:slide | (-10,-22) | (-22,-40) | (18,-12) | (-6,-34) |
| box:swing | (-2,-34) | (20,34) | (40,-40) | (4,-36) |
| box:arch-1 | (-4,-6) | (-12,-8) | (-8,-4) | (-4,-14) |
| box:arch-2 | (-8,-6) | (-40,-8) | (-8,-2) | (2,-16) |
| box:arch-3 (測定不能) | (-34,-8) | (-28,4) | (0,-4) | (0,-14) |
| box:arch-4 | (-38,-6) | (-6,20) | (8,-2) | (6,-14) |
| box:animal | (10,-10) | (-2,34) | (36,-34) | (30,-40) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.002/g0.0; window:TRM-03.win-kg2 w0.0/g0.0; window:TRM-03.win-kg3 w0.002/g0.0; window:TRM-03.win-kg4 w0.001/g0.0; 床lum_std 58.88; 全体ピンク残り 0.0
- take2: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.016/g0.0; window:TRM-03.win-res2 w0.066/g0.0; window:TRM-03.win-kg1 w0.685/g0.0; window:TRM-03.win-kg2 w0.211/g0.0; window:TRM-03.win-kg3 w0.045/g0.0; window:TRM-03.win-kg4 w0.093/g0.0; 床lum_std 73.5; 全体ピンク残り 0.0
- take3: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.001/g0.0; window:TRM-03.win-kg1 w0.0/g0.0; window:TRM-03.win-kg2 w0.0/g0.0; window:TRM-03.win-kg3 w0.0/g0.0; window:TRM-03.win-kg4 w0.0/g0.0; 床lum_std 61.22; 全体ピンク残り 0.0
- take4: door:TRM-03.door-main pink0.0; door:TRM-03.door-residence pink0.0; door:TRM-03.door-playroom pink0.0; window:TRM-03.win-res1 w0.0/g0.0; window:TRM-03.win-res2 w0.0/g0.0; window:TRM-03.win-kg1 w0.0/g0.0; window:TRM-03.win-kg2 w0.0/g0.0; window:TRM-03.win-kg3 w0.0/g0.0; window:TRM-03.win-kg4 w0.0/g0.0; 床lum_std 57.99; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 4.36
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 2.34
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 2.57
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 4.5
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 5.05
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 2.9
  }
 ],
 "mean_pairwise_chamfer_px": 3.62,
 "blurred_lum_pixel_std_room_mean": 33.24,
 "region_shift_sd": {
  "door:TRM-03.door-main": {
   "dx_sd": 7.0,
   "dy_sd": 19.6
  },
  "door:TRM-03.door-residence": {
   "dx_sd": 1.4,
   "dy_sd": 12.9
  },
  "door:TRM-03.door-playroom": {
   "dx_sd": 11.4,
   "dy_sd": 3.2
  },
  "window:TRM-03.win-res1": {
   "dx_sd": 16.1,
   "dy_sd": 2.0
  },
  "window:TRM-03.win-res2": {
   "dx_sd": 7.2,
   "dy_sd": 15.1
  },
  "window:TRM-03.win-kg1": {
   "dx_sd": 15.4,
   "dy_sd": 13.7
  },
  "window:TRM-03.win-kg2": {
   "dx_sd": 6.7,
   "dy_sd": 13.5
  },
  "window:TRM-03.win-kg3": {
   "dx_sd": 15.2,
   "dy_sd": 12.2
  },
  "window:TRM-03.win-kg4": {
   "dx_sd": 19.8,
   "dy_sd": 13.4
  },
  "box:bell": {
   "dx_sd": 11.9,
   "dy_sd": 20.3
  },
  "box:statue": {
   "dx_sd": 17.2,
   "dy_sd": 20.9
  },
  "box:slide": {
   "dx_sd": 14.5,
   "dy_sd": 10.8
  },
  "box:swing": {
   "dx_sd": 16.3,
   "dy_sd": 30.7
  },
  "box:arch-1": {
   "dx_sd": 3.3,
   "dy_sd": 3.7
  },
  "box:arch-2": {
   "dx_sd": 15.8,
   "dy_sd": 5.1
  },
  "box:arch-3": {
   "dx_sd": 15.6,
   "dy_sd": 6.5
  },
  "box:arch-4": {
   "dx_sd": 18.4,
   "dy_sd": 12.6
  },
  "box:animal": {
   "dx_sd": 15.3,
   "dy_sd": 29.1
  }
 },
 "region_shift_sd_mean_px": 13.16
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
