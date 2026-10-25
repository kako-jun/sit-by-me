# E2 測定 TRM-04 e2/retry1

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.882 | 0.234 | 3.17 | 0.545 | regions | True |
| 2 | FAIL | 0.75 | 0.185 | 4.87 | 0.364 | regions | True |
| 3 | PASS | 0.818 | 0.178 | 3.14 | 0.727 | - | True |
| 4 | FAIL | 0.836 | 0.215 | 3.45 | 0.364 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_pine_green_abs_min": 0.003, "outside_evergreen_ratio_min": null, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | outside_evergreen | 1.21 | 32/ENSW | 0.0008/0.0975/0.0275 | 0.0015 |
| 2 | FAIL | FAIL | density:slab_front | 1.01 | 36/ENSW | 0.0091/0.1355/0.0346 | 0.0005 |
| 3 | FAIL | FAIL | density:slab_front | 1.04 | 49/ENSW | 0.0063/0.1431/0.067 | 0.0003 |
| 4 | FAIL | FAIL | density:desk,density:slab_front | 1.26 | 30/ENSW | 0.0088/0.1149/0.0408 | 0.0005 |
| ref | - | - | - | 1.0 | 38/ENSW | 0.0451/0.0899/0.0149 | 0.0001 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 0.95 / 0.78 / dE1.4 | 1.13 / 0.71 / dE2.2 | 0.86 / 0.88 / dE2.0 | 0.22 / 0.61 / dE6.9 | 0.0133, 5.554 |
| slab_front | 0.82 / 0.93 / dE3.6 | 0.34 / 0.75 / dE12.2 | 0.41 / 0.74 / dE7.0 | 0.22 / 0.75 / dE13.3 | 0.1212, 5.632 |
| outside | 0.94 / 0.9 / dE13.1 | 1.06 / 0.97 / dE7.8 | 1.26 / 1.06 / dE8.6 | 0.98 / 0.91 / dE12.9 | 0.0952, 5.73 |
| floor | 0.67 / 0.99 / dE15.0 | 0.62 / 0.98 / dE11.8 | 0.76 / 1.01 / dE11.5 | 0.93 / 0.94 / dE17.4 | 0.0393, 5.259 |
| wall | 1.05 / 1.02 | 0.87 / 0.99 | 0.85 / 1.03 | 1.01 / 0.97 | 0.0835, 6.626 |
| objects | 1.57 / 1.14 | 0.89 / 0.98 | 1.76 / 1.21 | 0.98 / 1.05 | 0.0498, 5.292 |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 6.3・窓±8内 5/6・戸口±8内 0/3・全体ずれ中央値 [-4.0, 4.0]; take2: 窓の平均|dy| 18.7・窓±8内 3/6・戸口±8内 1/3・全体ずれ中央値 [-4.0, -8.0]; take3: 窓の平均|dy| 5.3・窓±8内 6/6・戸口±8内 1/3・全体ずれ中央値 [2.0, -2.0]; take4: 窓の平均|dy| 15.3・窓±8内 3/6・戸口±8内 1/3・全体ずれ中央値 [0.0, -8.0]

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 8.9（基準 ≤8.0）→ FAIL（全テイクの合幾何+装飾を不合格扱い）

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-04.door-west | (-22,-4) | (-20,-32) | (4,18) | (2,-22) |
| door:TRM-04.door-east | (-4,-34) | (6,0) | (0,-2) | (0,-8) |
| door:TRM-04.door-south | (-28,22) | (26,-30) | (-4,36) | (-16,-18) |
| window:TRM-04.win-cw1 | (6,4) | (-40,38) | (4,-8) | (-36,40) |
| window:TRM-04.win-cw2 | (-4,4) | (6,-8) | (6,0) | (-4,-10) |
| window:TRM-04.win-cw3 | (4,4) | (4,-10) | (6,0) | (0,0) |
| window:TRM-04.win-ce1 | (2,4) | (-4,-8) | (-6,-8) | (2,-8) |
| window:TRM-04.win-ce2 | (2,4) | (0,-8) | (2,-8) | (2,-8) |
| window:TRM-04.win-ce3 | (0,18) | (-8,40) | (2,-8) | (18,26) |
| box:step | (-8,-8) | (-12,-12) | (-8,-8) | (-20,-16) |
| box:dais | (-10,-38) | (-40,-28) | (18,10) | (18,-30) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 55.69; 全体ピンク残り 0.0
- take2: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.0/g0.0; 床lum_std 51.39; 全体ピンク残り 0.0
- take3: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.011/g0.0; window:TRM-04.win-cw2 w0.025/g0.0; window:TRM-04.win-cw3 w0.022/g0.0; window:TRM-04.win-ce1 w0.012/g0.0; window:TRM-04.win-ce2 w0.016/g0.0; window:TRM-04.win-ce3 w0.015/g0.0; 床lum_std 59.21; 全体ピンク残り 0.0
- take4: door:TRM-04.door-west pink0.0; door:TRM-04.door-east pink0.0; door:TRM-04.door-south pink0.0; window:TRM-04.win-cw1 w0.0/g0.0; window:TRM-04.win-cw2 w0.0/g0.0; window:TRM-04.win-cw3 w0.0/g0.0; window:TRM-04.win-ce1 w0.0/g0.0; window:TRM-04.win-ce2 w0.0/g0.0; window:TRM-04.win-ce3 w0.033/g0.0; 床lum_std 51.7; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 5.02
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 5.05
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 4.9
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 5.32
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 5.15
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 5.42
  }
 ],
 "mean_pairwise_chamfer_px": 5.14,
 "blurred_lum_pixel_std_room_mean": 21.17,
 "region_shift_sd": {
  "door:TRM-04.door-west": {
   "dx_sd": 12.0,
   "dy_sd": 19.0
  },
  "door:TRM-04.door-east": {
   "dx_sd": 3.6,
   "dy_sd": 13.6
  },
  "door:TRM-04.door-south": {
   "dx_sd": 20.1,
   "dy_sd": 27.3
  },
  "window:TRM-04.win-cw1": {
   "dx_sd": 21.6,
   "dy_sd": 20.9
  },
  "window:TRM-04.win-cw2": {
   "dx_sd": 5.0,
   "dy_sd": 5.7
  },
  "window:TRM-04.win-cw3": {
   "dx_sd": 2.2,
   "dy_sd": 5.2
  },
  "window:TRM-04.win-ce1": {
   "dx_sd": 3.6,
   "dy_sd": 5.2
  },
  "window:TRM-04.win-ce2": {
   "dx_sd": 0.9,
   "dy_sd": 5.2
  },
  "window:TRM-04.win-ce3": {
   "dx_sd": 9.4,
   "dy_sd": 17.5
  },
  "box:step": {
   "dx_sd": 4.9,
   "dy_sd": 3.3
  },
  "box:dais": {
   "dx_sd": 24.0,
   "dy_sd": 18.6
  }
 },
 "region_shift_sd_mean_px": 11.31
}
```

合格テイク（幾何）: ['3'] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
