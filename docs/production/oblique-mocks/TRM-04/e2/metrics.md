# E2 測定 TRM-04 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.906 | 0.394 | 3.12 | 0.182 | regions | True |
| 2 | FAIL | 0.815 | 0.227 | 4.53 | 0.091 | regions | True |
| 3 | FAIL | 0.811 | 0.275 | 3.86 | 0.0 | regions | True |
| 4 | PASS | 0.839 | 0.389 | 3.67 | 0.727 | - | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:desk,density:slab_front,density:floor | 1.22 | 33/NSW | 0.0056/0.0963/0.0182 | 0.0031 |
| 2 | FAIL | FAIL | density:slab_front,outside_trees,outside_evergreen | 1.14 | 37/NS | 0.0018/0.0728/0.0156 | 0.023 |
| 3 | FAIL | FAIL | density:slab_front,outside_evergreen | 1.17 | 26/ENS | 0.0001/0.1335/0.0494 | 0.0244 |
| 4 | FAIL | FAIL | density:slab_front,density:floor,outside_trees,outside_evergreen | 1.22 | 18/NS | 0.0009/0.1174/0.0227 | 0.0001 |
| ref | - | - | - | 1.0 | 38/ENSW | 0.0451/0.0899/0.0149 | 0.0001 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 0.25 / 0.67 / dE7.9 | 0.85 / 0.73 / dE4.2 | 0.98 / 0.81 / dE2.7 | 0.98 / 0.9 / dE5.1 | 0.0133, 5.554 |
| slab_front | 0.42 / 0.91 / dE5.2 | 0.42 / 0.72 / dE7.8 | 0.45 / 0.75 / dE11.6 | 0.47 / 0.68 / dE5.4 | 0.1212, 5.632 |
| outside | 0.96 / 0.91 / dE10.7 | 0.82 / 0.85 / dE13.8 | 0.89 / 0.91 / dE14.7 | 0.79 / 0.9 / dE11.9 | 0.0952, 5.73 |
| floor | 0.48 / 0.94 / dE19.8 | 0.64 / 0.99 / dE14.1 | 0.65 / 0.96 / dE16.4 | 0.55 / 0.99 / dE14.3 | 0.0393, 5.259 |
| wall | 1.01 / 1.01 | 0.85 / 0.98 | 0.76 / 0.96 | 0.73 / 0.97 | 0.0835, 6.626 |
| objects | 1.56 / 1.16 | 1.13 / 1.01 | 0.99 / 0.96 | 1.48 / 1.13 | 0.0498, 5.292 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 11.7・窓±8内 1/6・戸口±8内 1/3・全体ずれ中央値 [0.0, 0.0]; take2: 窓の平均|dy| 19.7・窓±8内 0/6・戸口±8内 1/3・全体ずれ中央値 [-6.0, 14.0]; take3: 窓の平均|dy| 16.7・窓±8内 0/6・戸口±8内 0/3・全体ずれ中央値 [-2.0, -12.0]; take4: 窓の平均|dy| 6.0・窓±8内 6/6・戸口±8内 1/3・全体ずれ中央値 [0.0, -6.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 12.1（基準 ≤8.0）→ FAIL（全テイクの合幾何+装飾を不合格扱い）

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-04.door-west | (6,-40) | (-2,10) | (-38,40) | (4,0) |
| door:TRM-04.door-east | (-2,-20) | (2,14) | (26,-4) | (24,-2) |
| door:TRM-04.door-south | (-2,0) | (-8,2) | (-30,-2) | (0,38) |
| window:TRM-04.win-cw1 | (0,12) | (-24,36) | (4,-12) | (-6,-6) |
| window:TRM-04.win-cw2 | (0,12) | (6,14) | (-4,-12) | (-6,-6) |
| window:TRM-04.win-cw3 | (0,12) | (4,14) | (0,-12) | (-4,-6) |
| window:TRM-04.win-ce1 | (0,-8) | (-6,16) | (-2,-12) | (2,-6) |
| window:TRM-04.win-ce2 | (0,14) | (-4,-22) | (2,-12) | (-6,-6) |
| window:TRM-04.win-ce3 | (-4,12) | (-8,16) | (0,40) | (2,-6) |
| box:step | (-8,-12) | (-10,-20) | (-8,-18) | (-30,-14) |
| box:dais | (-24,-26) | (-20,-8) | (-40,24) | (6,-6) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 54.35; 全体ピンク残り 0.0
- take2: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.011/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 54.32; 全体ピンク残り 0.0
- take3: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 56.6; 全体ピンク残り 0.0
- take4: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 57.97; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 5.42
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 5.12
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 6.82
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 5.63
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 6.61
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 7.44
  }
 ],
 "mean_pairwise_chamfer_px": 6.17,
 "blurred_lum_pixel_std_room_mean": 18.37,
 "region_shift_sd": {
  "door:TRM-04.door-west": {
   "dx_sd": 17.9,
   "dy_sd": 28.6
  },
  "door:TRM-04.door-east": {
   "dx_sd": 12.6,
   "dy_sd": 12.0
  },
  "door:TRM-04.door-south": {
   "dx_sd": 11.9,
   "dy_sd": 16.5
  },
  "window:TRM-04.win-cw1": {
   "dx_sd": 10.7,
   "dy_sd": 18.7
  },
  "window:TRM-04.win-cw2": {
   "dx_sd": 4.6,
   "dy_sd": 11.2
  },
  "window:TRM-04.win-cw3": {
   "dx_sd": 2.8,
   "dy_sd": 11.2
  },
  "window:TRM-04.win-ce1": {
   "dx_sd": 3.0,
   "dy_sd": 10.9
  },
  "window:TRM-04.win-ce2": {
   "dx_sd": 3.2,
   "dy_sd": 13.1
  },
  "window:TRM-04.win-ce3": {
   "dx_sd": 3.8,
   "dy_sd": 16.4
  },
  "box:step": {
   "dx_sd": 9.3,
   "dy_sd": 3.2
  },
  "box:dais": {
   "dx_sd": 16.5,
   "dy_sd": 17.9
  }
 },
 "region_shift_sd_mean_px": 11.64
}
```

合格テイク（幾何）: ['4'] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
