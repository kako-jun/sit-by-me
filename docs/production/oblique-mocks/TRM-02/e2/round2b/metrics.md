# E2 測定 TRM-02 e2/round2b

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.706 | 0.061 | 5.36 | 0.0 | edge_margin,regions | True |
| 2 | FAIL | 0.677 | 0.026 | 5.49 | 0.0 | edge_margin,regions | True |
| 3 | FAIL | 0.675 | 0.026 | 5.57 | 0.0 | edge_margin,regions | True |
| 4 | FAIL | 0.749 | 0.15 | 4.86 | 0.077 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "outside_evergreen_ratio_min": 0.3, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | PASS | FAIL | - | 0.97 | 47/ENSW | 0.0243/0.1304/0.0409 | 0.0004 |
| 2 | PASS | FAIL | - | 1.07 | 39/ENSW | 0.0226/0.1065/0.0402 | 0.0012 |
| 3 | PASS | FAIL | - | 0.99 | 46/ENSW | 0.0218/0.1139/0.0392 | 0.0022 |
| 4 | PASS | FAIL | - | 1.01 | 37/ENSW | 0.0221/0.1025/0.042 | 0.0034 |
| ref | - | - | - | 1.0 | 29/ENSW | 0.0217/0.0711/0.0142 | 0.001 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 1.42 / 1.02 / dE3.4 | 0.86 / 0.98 / dE4.4 | 1.25 / 1.0 / dE2.0 | 1.25 / 1.02 / dE1.8 | 0.0096, 5.323 |
| slab_front | 0.97 / 1.0 / dE6.6 | 0.94 / 0.97 / dE4.4 | 0.97 / 0.95 / dE5.3 | 1.34 / 1.15 / dE13.7 | 0.1033, 5.206 |
| outside | 1.36 / 1.1 / dE3.6 | 1.03 / 1.02 / dE3.6 | 1.11 / 1.03 / dE2.8 | 1.03 / 1.02 / dE2.7 | 0.0863, 5.731 |
| floor | 1.02 / 1.13 / dE5.5 | 0.98 / 1.07 / dE3.9 | 0.93 / 1.07 / dE5.7 | 0.82 / 1.11 / dE4.4 | 0.0298, 4.631 |
| wall | 0.97 / 1.02 | 1.03 / 1.04 | 1.0 / 1.04 | 0.91 / 1.01 | 0.0842, 7.127 |
| objects | 1.02 / 1.07 | 1.04 / 1.04 | 1.09 / 1.04 | 1.01 / 1.03 | 0.0893, 6.45 |

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-02.door-west | (-26,-40) | (-20,-40) | (-24,-40) | (-38,-40) |
| door:TRM-02.door-outside | (-20,-28) | (-24,-28) | (-18,-24) | (18,2) |
| window:TRM-02.win-s1 | (24,-28) | (30,-26) | (28,-24) | (2,-20) |
| window:TRM-02.win-s2 | (28,-30) | (-12,-26) | (26,-28) | (-4,-20) |
| window:TRM-02.win-s3 | (-16,-30) | (28,-26) | (-16,-28) | (-12,-20) |
| window:TRM-02.win-s4 | (-14,-30) | (-14,-26) | (22,-24) | (-6,-20) |
| box:stage | (-10,-16) | (-10,-16) | (-8,-14) | (-6,-12) |
| box:shelf-nw | (-22,-12) | (-40,-10) | (40,-10) | (34,-8) |
| box:shelf-ne | (32,-12) | (32,-10) | (36,-10) | (6,-8) |
| box:chair-w1 (測定不能) | (-36,-12) | (-38,-20) | (-40,12) | (-6,20) |
| box:chair-w2 (測定不能) | (-40,-40) | (-34,-40) | (-38,-32) | (-40,-30) |
| box:chair-w3 | (-40,-24) | (-34,-34) | (-38,-34) | (-4,-32) |
| box:table-small | (-4,-28) | (-4,-26) | (-4,-18) | (6,-16) |
| box:toy-rack | (40,38) | (30,40) | (40,40) | (40,10) |
| box:round-table | (40,40) | (-2,40) | (40,40) | (14,40) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.009/g0.0; window:TRM-02.win-s2 w0.027/g0.0; window:TRM-02.win-s3 w0.019/g0.0; window:TRM-02.win-s4 w0.024/g0.0; 床lum_std 33.45; 全体ピンク残り 0.0
- take2: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.005/g0.0; window:TRM-02.win-s2 w0.016/g0.0; window:TRM-02.win-s3 w0.012/g0.0; window:TRM-02.win-s4 w0.008/g0.0; 床lum_std 32.18; 全体ピンク残り 0.0
- take3: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.003/g0.0; window:TRM-02.win-s2 w0.013/g0.0; window:TRM-02.win-s3 w0.012/g0.0; window:TRM-02.win-s4 w0.004/g0.0; 床lum_std 31.04; 全体ピンク残り 0.0
- take4: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.004/g0.0; window:TRM-02.win-s2 w0.002/g0.0; window:TRM-02.win-s3 w0.001/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 31.92; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 1.37
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 1.64
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 3.36
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 1.51
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 3.34
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 3.2
  }
 ],
 "mean_pairwise_chamfer_px": 2.4,
 "blurred_lum_pixel_std_room_mean": 10.29,
 "region_shift_sd": {
  "door:TRM-02.door-west": {
   "dx_sd": 6.7,
   "dy_sd": 0.0
  },
  "door:TRM-02.door-outside": {
   "dx_sd": 16.9,
   "dy_sd": 12.5
  },
  "window:TRM-02.win-s1": {
   "dx_sd": 11.2,
   "dy_sd": 3.0
  },
  "window:TRM-02.win-s2": {
   "dx_sd": 17.7,
   "dy_sd": 3.7
  },
  "window:TRM-02.win-s3": {
   "dx_sd": 18.5,
   "dy_sd": 3.7
  },
  "window:TRM-02.win-s4": {
   "dx_sd": 14.8,
   "dy_sd": 3.6
  },
  "box:stage": {
   "dx_sd": 1.7,
   "dy_sd": 1.7
  },
  "box:shelf-nw": {
   "dx_sd": 34.7,
   "dy_sd": 1.4
  },
  "box:shelf-ne": {
   "dx_sd": 11.9,
   "dy_sd": 1.4
  },
  "box:chair-w1": {
   "dx_sd": 13.9,
   "dy_sd": 16.5
  },
  "box:chair-w2": {
   "dx_sd": 2.4,
   "dy_sd": 4.6
  },
  "box:chair-w3": {
   "dx_sd": 14.6,
   "dy_sd": 4.1
  },
  "box:table-small": {
   "dx_sd": 4.3,
   "dy_sd": 5.1
  },
  "box:toy-rack": {
   "dx_sd": 4.3,
   "dy_sd": 12.7
  },
  "box:round-table": {
   "dx_sd": 17.9,
   "dy_sd": 0.0
  }
 },
 "region_shift_sd_mean_px": 8.85
}
```

合格テイク（幾何）: [] / 合格（装飾）: ['1', '2', '3', '4'] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
