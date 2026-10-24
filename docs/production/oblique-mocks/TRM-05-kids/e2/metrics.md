# E2 測定 TRM-05-kids e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.847 | 0.456 | 3.64 | 0.385 | regions | True |
| 2 | FAIL | 0.843 | 0.363 | 3.63 | 0.538 | regions | True |
| 3 | FAIL | 0.683 | 0.229 | 5.5 | 0.385 | regions | True |
| 4 | FAIL | 0.809 | 0.344 | 4.14 | 0.538 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,density:floor | 1.0 | 38/ESW | 0.0041/0.1073/0.026 | 0.0058 |
| 2 | FAIL | FAIL | density:slab_front,density:wall,outside_evergreen | 1.01 | 33/ENSW | 0.0002/0.1115/0.0437 | 0.0165 |
| 3 | FAIL | FAIL | density:slab_front,density:wall | 0.88 | 27/ENSW | 0.005/0.13/0.0357 | 0.0162 |
| 4 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.96 | 30/ESW | 0.0004/0.1214/0.0249 | 0.0023 |
| ref | - | - | - | 1.0 | 40/ENSW | 0.0315/0.0543/0.0088 | 0.0011 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 0.81 / 0.8 / dE4.1 | 1.28 / 0.75 / dE4.6 | 1.57 / 0.85 / dE3.2 | 1.39 / 0.69 / dE5.6 | 0.0096, 5.325 |
| slab_front | 0.38 / 0.68 / dE6.1 | 0.56 / 0.77 / dE4.8 | 0.54 / 0.7 / dE8.8 | 0.22 / 0.57 / dE5.6 | 0.1304, 5.851 |
| outside | 0.99 / 1.09 / dE6.9 | 1.05 / 0.94 / dE8.3 | 1.1 / 1.06 / dE5.0 | 1.16 / 1.0 / dE5.2 | 0.0749, 5.211 |
| floor | 0.55 / 0.99 / dE5.1 | 0.7 / 0.99 / dE7.9 | 0.67 / 1.04 / dE6.5 | 0.65 / 1.02 / dE7.4 | 0.0508, 5.908 |
| wall | 0.74 / 0.96 | 0.54 / 0.91 | 0.59 / 0.91 | 0.65 / 0.95 | 0.1014, 6.341 |
| objects | 0.98 / 1.04 | 0.95 / 1.02 | 0.93 / 1.01 | 1.19 / 1.03 | 0.052, 6.002 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 6.7・窓±8内 3/3・戸口±8内 0/3・全体ずれ中央値 [-2.0, -8.0]; take2: 窓の平均|dy| 5.3・窓±8内 3/3・戸口±8内 3/3・全体ずれ中央値 [-4.0, -6.0]; take3: 窓の平均|dy| 8.0・窓±8内 3/3・戸口±8内 0/3・全体ずれ中央値 [0.0, -2.0]; take4: 窓の平均|dy| 7.3・窓±8内 3/3・戸口±8内 2/3・全体ずれ中央値 [-2.0, -6.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 2.7（基準 ≤8.0）→ OK

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-05.door-hall | (-2,-16) | (0,-2) | (40,-40) | (0,-2) |
| door:TRM-05.door-outside | (-16,-2) | (-6,-4) | (-28,-22) | (-18,2) |
| door:TRM-05.door-back | (0,-12) | (-4,-2) | (-26,32) | (-4,-4) |
| window:TRM-05.win-s1 | (0,-8) | (-4,-8) | (-4,8) | (-6,-8) |
| window:TRM-05.win-s2 | (-4,-8) | (6,-6) | (8,8) | (6,-8) |
| window:TRM-05.win-n1 | (-2,-4) | (-8,-2) | (0,-8) | (-4,-6) |
| box:stove | (12,-38) | (12,-40) | (-10,-2) | (-2,-26) |
| box:sink | (-6,2) | (-24,-40) | (-8,0) | (-8,-32) |
| box:cupboard | (-24,-40) | (-22,-40) | (8,-34) | (-4,-12) |
| box:fridge | (4,2) | (-4,0) | (10,2) | (-2,4) |
| box:shelf-w (測定不能) | (-20,-40) | (-6,-40) | (0,-36) | (-6,-40) |
| box:table | (4,-40) | (2,-40) | (4,-38) | (-2,24) |
| box:bench-l | (8,-22) | (0,-28) | (-2,-14) | (-2,-4) |
| box:bench-r (測定不能) | (0,2) | (-34,-26) | (-2,8) | (-36,6) |
| box:dresser | (-22,-6) | (0,14) | (4,0) | (0,-38) |
| box:rock (測定不能) | (-2,-4) | (32,-32) | (8,-26) | (-6,-40) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.001/g0.0; window:TRM-05.win-s2 w0.006/g0.0; window:TRM-05.win-n1 w0.011/g0.0; 床lum_std 52.29; 全体ピンク残り 0.0
- take2: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.012/g0.0; window:TRM-05.win-s2 w0.021/g0.0; window:TRM-05.win-n1 w0.01/g0.0; 床lum_std 43.76; 全体ピンク残り 0.0
- take3: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 45.46; 全体ピンク残り 0.0
- take4: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.001/g0.0; window:TRM-05.win-n1 w0.002/g0.0; 床lum_std 42.36; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 4.38
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 5.01
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 4.51
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 5.06
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 4.52
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 4.95
  }
 ],
 "mean_pairwise_chamfer_px": 4.74,
 "blurred_lum_pixel_std_room_mean": 15.31,
 "region_shift_sd": {
  "door:TRM-05.door-hall": {
   "dx_sd": 17.6,
   "dy_sd": 15.5
  },
  "door:TRM-05.door-outside": {
   "dx_sd": 7.8,
   "dy_sd": 9.2
  },
  "door:TRM-05.door-back": {
   "dx_sd": 10.2,
   "dy_sd": 16.9
  },
  "window:TRM-05.win-s1": {
   "dx_sd": 2.2,
   "dy_sd": 6.9
  },
  "window:TRM-05.win-s2": {
   "dx_sd": 4.7,
   "dy_sd": 6.7
  },
  "window:TRM-05.win-n1": {
   "dx_sd": 3.0,
   "dy_sd": 2.2
  },
  "box:stove": {
   "dx_sd": 9.4,
   "dy_sd": 15.1
  },
  "box:sink": {
   "dx_sd": 7.3,
   "dy_sd": 18.7
  },
  "box:cupboard": {
   "dx_sd": 13.2,
   "dy_sd": 11.5
  },
  "box:fridge": {
   "dx_sd": 5.5,
   "dy_sd": 1.4
  },
  "box:shelf-w": {
   "dx_sd": 7.3,
   "dy_sd": 1.7
  },
  "box:table": {
   "dx_sd": 2.4,
   "dy_sd": 27.4
  },
  "box:bench-l": {
   "dx_sd": 4.1,
   "dy_sd": 9.0
  },
  "box:bench-r": {
   "dx_sd": 17.0,
   "dy_sd": 13.7
  },
  "box:dresser": {
   "dx_sd": 10.2,
   "dy_sd": 19.0
  },
  "box:rock": {
   "dx_sd": 14.8,
   "dy_sd": 13.4
  }
 },
 "region_shift_sd_mean_px": 10.16
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
