# E2 測定 TRM-02 e2/round2a

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.571 | -0.043 | 8.39 | 0.0 | edge_recall,edge_margin,chamfer,regions,window_content | True |
| 2 | FAIL | 0.82 | 0.181 | 4.37 | 0.385 | regions | True |
| 3 | FAIL | 0.64 | -0.014 | 7.33 | 0.077 | edge_margin,chamfer,regions | True |
| 4 | FAIL | 0.482 | -0.062 | 8.96 | 0.0 | edge_recall,edge_margin,chamfer,regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "outside_evergreen_ratio_min": 0.3, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,density:objects | 1.04 | 40/ENSW | 0.0091/0.1062/0.1031 | 0.0179 |
| 2 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.91 | 26/ENSW | 0.0005/0.1282/0.1114 | 0.0041 |
| 3 | FAIL | FAIL | outside_evergreen | 0.89 | 27/ENSW | 0.0039/0.1089/0.0798 | 0.0015 |
| 4 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.91 | 43/ENSW | 0.0042/0.1203/0.1369 | 0.0041 |
| ref | - | - | - | 1.0 | 29/ENSW | 0.0217/0.0711/0.0142 | 0.001 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 1.92 / 0.94 / dE6.2 | 2.08 / 1.01 / dE5.2 | 1.46 / 0.94 / dE6.4 | 1.03 / 0.79 / dE1.5 | 0.0096, 5.323 |
| slab_front | 0.42 / 0.74 / dE6.0 | 0.47 / 0.74 / dE4.9 | 0.7 / 0.86 / dE2.9 | 0.15 / 0.54 / dE7.3 | 0.1033, 5.206 |
| outside | 1.05 / 1.01 / dE12.9 | 1.04 / 1.04 / dE12.1 | 0.94 / 1.03 / dE10.5 | 1.07 / 1.1 / dE7.8 | 0.0863, 5.731 |
| floor | 0.78 / 1.05 / dE16.8 | 0.67 / 0.99 / dE11.0 | 0.64 / 1.07 / dE6.8 | 0.62 / 1.05 / dE14.3 | 0.0298, 4.631 |
| wall | 1.14 / 1.05 | 1.18 / 1.01 | 1.36 / 1.05 | 1.19 / 1.06 | 0.0842, 7.127 |
| objects | 0.58 / 0.95 | 0.87 / 1.0 | 0.79 / 0.99 | 0.82 / 0.99 | 0.0893, 6.45 |

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-02.door-west | (-20,-8) | (-22,-32) | (-16,-40) | (-36,-38) |
| door:TRM-02.door-outside | (4,-26) | (-2,2) | (6,-6) | (30,-26) |
| window:TRM-02.win-s1 | (-2,-26) | (-4,-8) | (-2,-20) | (-30,-32) |
| window:TRM-02.win-s2 | (0,-26) | (2,-6) | (0,-18) | (-8,-32) |
| window:TRM-02.win-s3 | (2,-28) | (-4,-6) | (2,-20) | (-6,-40) |
| window:TRM-02.win-s4 | (4,-40) | (6,-6) | (6,-20) | (20,-40) |
| box:stage | (2,-40) | (4,-20) | (6,-40) | (6,-28) |
| box:shelf-nw | (-24,-34) | (-36,-18) | (-16,-28) | (-30,-10) |
| box:shelf-ne | (40,-40) | (32,-12) | (-40,-40) | (24,-10) |
| box:chair-w1 (測定不能) | (-10,2) | (0,14) | (-14,22) | (-34,-2) |
| box:chair-w2 (測定不能) | (-12,-2) | (0,-2) | (-8,-26) | (-40,28) |
| box:chair-w3 | (-10,-40) | (-38,4) | (-10,-24) | (-36,-20) |
| box:table-small | (14,-34) | (10,-30) | (4,-40) | (20,-16) |
| box:toy-rack | (38,-40) | (24,6) | (10,-6) | (40,-22) |
| box:round-table | (40,4) | (6,40) | (40,14) | (24,8) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.068/g0.0; window:TRM-02.win-s2 w0.076/g0.0; window:TRM-02.win-s3 w0.101/g0.0; window:TRM-02.win-s4 w0.06/g0.0; 床lum_std 40.37; 全体ピンク残り 0.0
- take2: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 39.1; 全体ピンク残り 0.0
- take3: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.001/g0.0; window:TRM-02.win-s2 w0.002/g0.0; window:TRM-02.win-s3 w0.001/g0.0; window:TRM-02.win-s4 w0.005/g0.0; 床lum_std 37.3; 全体ピンク残り 0.0
- take4: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.01/g0.0; window:TRM-02.win-s2 w0.043/g0.0; window:TRM-02.win-s3 w0.042/g0.0; window:TRM-02.win-s4 w0.05/g0.0; 床lum_std 38.27; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 6.53
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 4.75
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 6.06
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 4.46
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 5.74
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 5.32
  }
 ],
 "mean_pairwise_chamfer_px": 5.48,
 "blurred_lum_pixel_std_room_mean": 22.21,
 "region_shift_sd": {
  "door:TRM-02.door-west": {
   "dx_sd": 7.5,
   "dy_sd": 12.8
  },
  "door:TRM-02.door-outside": {
   "dx_sd": 12.2,
   "dy_sd": 12.3
  },
  "window:TRM-02.win-s1": {
   "dx_sd": 11.9,
   "dy_sd": 8.9
  },
  "window:TRM-02.win-s2": {
   "dx_sd": 3.8,
   "dy_sd": 9.7
  },
  "window:TRM-02.win-s3": {
   "dx_sd": 3.6,
   "dy_sd": 12.4
  },
  "window:TRM-02.win-s4": {
   "dx_sd": 6.4,
   "dy_sd": 14.4
  },
  "box:stage": {
   "dx_sd": 1.7,
   "dy_sd": 8.5
  },
  "box:shelf-nw": {
   "dx_sd": 7.4,
   "dy_sd": 9.2
  },
  "box:shelf-ne": {
   "dx_sd": 31.7,
   "dy_sd": 14.5
  },
  "box:chair-w1": {
   "dx_sd": 12.4,
   "dy_sd": 9.5
  },
  "box:chair-w2": {
   "dx_sd": 15.1,
   "dy_sd": 19.2
  },
  "box:chair-w3": {
   "dx_sd": 13.5,
   "dy_sd": 15.7
  },
  "box:table-small": {
   "dx_sd": 5.8,
   "dy_sd": 8.8
  },
  "box:toy-rack": {
   "dx_sd": 12.1,
   "dy_sd": 17.3
  },
  "box:round-table": {
   "dx_sd": 14.0,
   "dy_sd": 14.0
  }
 },
 "region_shift_sd_mean_px": 11.54
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
