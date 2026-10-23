# E2 測定 TRM-05 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.908 | 0.451 | 2.72 | 0.643 | regions | True |
| 2 | FAIL | 0.762 | 0.382 | 5.35 | 0.357 | regions | True |
| 3 | FAIL | 0.886 | 0.482 | 3.1 | 0.643 | regions | True |
| 4 | FAIL | 0.759 | 0.351 | 6.05 | 0.429 | chamfer,regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:desk,density:slab_front,outside_evergreen | 1.04 | 30/ENSW | 0.0007/0.1224/0.0539 | 0.0063 |
| 2 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 0.88 | 30/ENSW | 0.0016/0.076/0.0116 | 0.0004 |
| 3 | FAIL | FAIL | density:slab_front,density:floor,density:wall,outside_evergreen | 0.94 | 40/ENSW | 0.0015/0.089/0.0291 | 0.0005 |
| 4 | FAIL | FAIL | density:floor,outside_evergreen | 0.94 | 52/ENSW | 0.0004/0.0973/0.0158 | 0.0012 |
| ref | - | - | - | 1.0 | 40/ENSW | 0.0315/0.0543/0.0088 | 0.0011 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 0.56 / 0.74 / dE1.1 | 1.69 / 0.83 / dE8.6 | 2.35 / 0.9 / dE7.1 | 1.33 / 0.88 / dE7.3 | 0.0096, 5.325 |
| slab_front | 0.48 / 0.73 / dE6.0 | 0.39 / 0.71 / dE6.5 | 0.5 / 0.7 / dE6.5 | 0.67 / 0.74 / dE4.3 | 0.1304, 5.851 |
| outside | 1.07 / 1.02 / dE8.1 | 0.99 / 1.06 / dE4.2 | 1.19 / 1.02 / dE6.1 | 1.09 / 0.98 / dE5.0 | 0.0749, 5.211 |
| floor | 0.65 / 1.07 / dE10.2 | 0.47 / 0.93 / dE0.3 | 0.58 / 1.06 / dE10.1 | 0.46 / 1.04 / dE2.9 | 0.0521, 5.885 |
| wall | 0.75 / 1.0 | 0.66 / 0.99 | 0.58 / 0.93 | 0.74 / 1.0 | 0.0986, 6.315 |
| objects | 0.87 / 1.03 | 0.81 / 0.99 | 1.15 / 1.05 | 0.68 / 0.94 | 0.0527, 6.009 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 6.0・窓±8内 3/3・戸口±8内 2/3・全体ずれ中央値 [-2.0, -6.0]; take2: 窓の平均|dy| 4.7・窓±8内 3/3・戸口±8内 1/3・全体ずれ中央値 [0.0, -7.0]; take3: 窓の平均|dy| 4.7・窓±8内 3/3・戸口±8内 0/3・全体ずれ中央値 [-2.0, -6.0]; take4: 窓の平均|dy| 4.0・窓±8内 3/3・戸口±8内 1/3・全体ずれ中央値 [1.0, -6.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 7.8（基準 ≤8.0）→ OK

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-05.door-hall | (-4,-34) | (36,-6) | (6,20) | (4,-34) |
| door:TRM-05.door-outside | (0,-2) | (-6,-2) | (-8,-14) | (-8,-2) |
| door:TRM-05.door-back | (-2,-2) | (-2,-24) | (-2,-14) | (0,30) |
| window:TRM-05.win-s1 | (0,-8) | (-2,-8) | (-6,-6) | (2,-6) |
| window:TRM-05.win-s2 | (-8,-8) | (-2,-2) | (4,-8) | (4,-6) |
| window:TRM-05.win-n1 | (-2,2) | (-2,-4) | (0,0) | (-4,0) |
| box:stove | (-2,-32) | (-16,-38) | (0,-6) | (-18,-40) |
| box:sink | (-2,-6) | (-24,-6) | (-4,-6) | (-10,-4) |
| box:cupboard | (0,-6) | (2,-38) | (-2,-10) | (0,-26) |
| box:fridge | (-2,0) | (2,0) | (-2,-6) | (2,-6) |
| box:shelf-w (測定不能) | (0,-40) | (0,-38) | (-4,-40) | (-4,-40) |
| box:table | (2,-40) | (6,-40) | (-2,4) | (2,-18) |
| box:bench-l | (-32,-18) | (6,-34) | (0,-32) | (4,-4) |
| box:bench-r (測定不能) | (-32,-4) | (0,-16) | (-32,-22) | (-2,6) |
| box:dresser | (-4,2) | (40,0) | (-4,2) | (-22,8) |
| box:rock (測定不能) | (40,-8) | (40,-18) | (40,20) | (40,2) |
| box:chest | (-28,40) | (40,-40) | (-2,4) | (4,-40) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.004/g0.0; 床lum_std 50.16; 全体ピンク残り 0.0
- take2: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 51.34; 全体ピンク残り 0.0
- take3: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 53.61; 全体ピンク残り 0.0
- take4: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 50.83; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 5.5
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 4.24
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 5.47
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 5.21
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 4.89
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 5.27
  }
 ],
 "mean_pairwise_chamfer_px": 5.1,
 "blurred_lum_pixel_std_room_mean": 18.12,
 "region_shift_sd": {
  "door:TRM-05.door-hall": {
   "dx_sd": 15.2,
   "dy_sd": 22.5
  },
  "door:TRM-05.door-outside": {
   "dx_sd": 3.3,
   "dy_sd": 5.2
  },
  "door:TRM-05.door-back": {
   "dx_sd": 0.9,
   "dy_sd": 20.3
  },
  "window:TRM-05.win-s1": {
   "dx_sd": 3.0,
   "dy_sd": 1.0
  },
  "window:TRM-05.win-s2": {
   "dx_sd": 5.0,
   "dy_sd": 2.4
  },
  "window:TRM-05.win-n1": {
   "dx_sd": 1.4,
   "dy_sd": 2.2
  },
  "box:stove": {
   "dx_sd": 8.1,
   "dy_sd": 13.6
  },
  "box:sink": {
   "dx_sd": 8.6,
   "dy_sd": 0.9
  },
  "box:cupboard": {
   "dx_sd": 1.4,
   "dy_sd": 12.8
  },
  "box:fridge": {
   "dx_sd": 2.0,
   "dy_sd": 3.0
  },
  "box:shelf-w": {
   "dx_sd": 2.0,
   "dy_sd": 0.9
  },
  "box:table": {
   "dx_sd": 2.8,
   "dy_sd": 18.2
  },
  "box:bench-l": {
   "dx_sd": 15.5,
   "dy_sd": 12.1
  },
  "box:bench-r": {
   "dx_sd": 15.5,
   "dy_sd": 10.8
  },
  "box:dresser": {
   "dx_sd": 22.9,
   "dy_sd": 3.0
  },
  "box:rock": {
   "dx_sd": 0.0,
   "dy_sd": 14.0
  },
  "box:chest": {
   "dx_sd": 24.3,
   "dy_sd": 33.5
  }
 },
 "region_shift_sd_mean_px": 9.07
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
