# E2 測定 TRM-05-fire e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.882 | 0.37 | 3.17 | 0.588 | regions | True |
| 2 | FAIL | 0.591 | 0.103 | 7.43 | 0.059 | edge_recall,edge_margin,chamfer,regions | True |
| 3 | FAIL | 0.778 | 0.356 | 4.39 | 0.235 | regions | True |
| 4 | FAIL | 0.815 | 0.345 | 4.73 | 0.294 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.98 | 29/ENSW | 0.0002/0.1092/0.036 | 0.0047 |
| 2 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.88 | 36/ESW | 0.0/0.1648/0.0453 | 0.0029 |
| 3 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 0.83 | 33/ENSW | 0.0001/0.1547/0.0519 | 0.0004 |
| 4 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 1.04 | 25/ESW | 0.0001/0.1245/0.0373 | 0.0001 |
| ref | - | - | - | 1.0 | 40/ENSW | 0.0315/0.0543/0.0088 | 0.0011 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 2.27 / 0.89 / dE9.9 | 2.29 / 0.86 / dE7.7 | 1.94 / 0.93 / dE4.1 | 0.96 / 0.81 / dE14.5 | 0.0096, 5.325 |
| slab_front | 0.56 / 0.77 / dE6.3 | 0.46 / 0.72 / dE6.7 | 0.34 / 0.61 / dE7.3 | 0.57 / 0.67 / dE4.3 | 0.1304, 5.851 |
| outside | 1.0 / 0.97 / dE8.3 | 1.0 / 1.05 / dE8.0 | 1.09 / 1.11 / dE8.4 | 1.04 / 1.03 / dE6.9 | 0.0749, 5.211 |
| floor | 0.72 / 1.05 / dE8.3 | 0.75 / 1.01 / dE9.5 | 0.59 / 1.01 / dE14.5 | 0.57 / 0.98 / dE4.1 | 0.0573, 5.643 |
| wall | 0.86 / 0.96 | 0.69 / 0.99 | 0.77 / 1.0 | 0.66 / 0.94 | 0.0989, 6.283 |
| objects | 1.25 / 1.11 | 0.61 / 0.99 | 0.92 / 1.09 | 1.22 / 0.97 | 0.0485, 5.996 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 1.3・窓±8内 3/3・戸口±8内 1/2・全体ずれ中央値 [2.0, 0.0]; take2: 窓の平均|dy| 15.3・窓±8内 0/3・戸口±8内 0/2・全体ずれ中央値 [-2.0, -12.0]; take3: 窓の平均|dy| 5.3・窓±8内 3/3・戸口±8内 0/2・全体ずれ中央値 [4.0, -12.0]; take4: 窓の平均|dy| 8.0・窓±8内 2/3・戸口±8内 1/2・全体ずれ中央値 [-2.0, -8.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 13.5（基準 ≤8.0）→ FAIL（全テイクの合幾何+装飾を不合格扱い）

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-05.door-hall | (0,-40) | (-32,20) | (8,-20) | (30,-16) |
| door:TRM-05.door-outside | (0,0) | (12,-4) | (0,-12) | (-6,-2) |
| window:TRM-05.win-s1 | (0,0) | (6,-12) | (-6,-8) | (-8,-8) |
| window:TRM-05.win-s2 | (6,0) | (38,-12) | (2,-8) | (-2,-10) |
| window:TRM-05.win-n1 | (4,-4) | (6,-22) | (-4,0) | (-8,-6) |
| box:stove | (2,2) | (-8,-12) | (14,-40) | (-16,30) |
| box:sink | (-2,4) | (-12,-14) | (-18,-38) | (-2,-8) |
| box:cupboard | (-32,-40) | (40,-8) | (-2,-40) | (-28,8) |
| box:fridge | (2,0) | (4,-12) | (2,4) | (40,38) |
| box:shelf-w (測定不能) | (-6,-40) | (-6,-40) | (-2,-40) | (-6,-40) |
| box:table | (4,-40) | (-2,-2) | (2,-30) | (4,-40) |
| box:bench-l | (8,-18) | (6,-20) | (10,-4) | (8,-40) |
| box:bench-r (測定不能) | (-32,-22) | (0,4) | (0,12) | (-4,4) |
| box:dresser | (-2,0) | (-22,-16) | (40,-2) | (-6,14) |
| box:rock | (40,12) | (20,28) | (40,-12) | (-2,-28) |
| box:chest | (2,2) | (-30,-36) | (24,-34) | (-2,-38) |
| box:fire-zone | (2,-4) | (-36,8) | (40,8) | (2,-6) |
| box:burnt-back-door-embers | (4,-30) | (-16,-38) | (10,-40) | (-10,12) |
| box:burnt-back-door-flame | (12,-28) | (-8,-40) | (4,-38) | (-4,-30) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.006/g0.0; 床lum_std 55.91; 全体ピンク残り 0.0
- take2: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.013/g0.0; 床lum_std 50.76; 全体ピンク残り 0.0
- take3: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.002/g0.0; 床lum_std 48.86; 全体ピンク残り 0.0
- take4: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 48.22; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 7.53
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 6.38
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 4.11
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 6.97
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 9.4
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 7.84
  }
 ],
 "mean_pairwise_chamfer_px": 7.04,
 "blurred_lum_pixel_std_room_mean": 22.76,
 "region_shift_sd": {
  "door:TRM-05.door-hall": {
   "dx_sd": 22.2,
   "dy_sd": 21.6
  },
  "door:TRM-05.door-outside": {
   "dx_sd": 6.5,
   "dy_sd": 4.6
  },
  "window:TRM-05.win-s1": {
   "dx_sd": 5.5,
   "dy_sd": 4.4
  },
  "window:TRM-05.win-s2": {
   "dx_sd": 15.8,
   "dy_sd": 4.6
  },
  "window:TRM-05.win-n1": {
   "dx_sd": 5.7,
   "dy_sd": 8.4
  },
  "box:stove": {
   "dx_sd": 11.2,
   "dy_sd": 25.2
  },
  "box:sink": {
   "dx_sd": 6.8,
   "dy_sd": 15.3
  },
  "box:cupboard": {
   "dx_sd": 28.7,
   "dy_sd": 20.8
  },
  "box:fridge": {
   "dx_sd": 16.2,
   "dy_sd": 18.6
  },
  "box:shelf-w": {
   "dx_sd": 1.7,
   "dy_sd": 0.0
  },
  "box:table": {
   "dx_sd": 2.4,
   "dy_sd": 15.6
  },
  "box:bench-l": {
   "dx_sd": 1.4,
   "dy_sd": 12.8
  },
  "box:bench-r": {
   "dx_sd": 13.4,
   "dy_sd": 12.8
  },
  "box:dresser": {
   "dx_sd": 22.9,
   "dy_sd": 10.6
  },
  "box:rock": {
   "dx_sd": 17.3,
   "dy_sd": 21.5
  },
  "box:chest": {
   "dx_sd": 19.2,
   "dy_sd": 16.5
  },
  "box:fire-zone": {
   "dx_sd": 26.9,
   "dy_sd": 6.5
  },
  "box:burnt-back-door-embers": {
   "dx_sd": 10.4,
   "dy_sd": 21.1
  },
  "box:burnt-back-door-flame": {
   "dx_sd": 7.7,
   "dy_sd": 5.1
  }
 },
 "region_shift_sd_mean_px": 12.84
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
