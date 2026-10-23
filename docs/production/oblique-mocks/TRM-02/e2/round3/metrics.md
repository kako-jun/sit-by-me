# E2 測定 TRM-02 e2/round3

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.808 | 0.241 | 6.61 | 0.615 | chamfer,regions | True |
| 2 | FAIL | 0.817 | 0.238 | 4.22 | 0.077 | regions | True |
| 3 | FAIL | 0.875 | 0.303 | 3.12 | 0.462 | regions | True |
| 4 | FAIL | 0.809 | 0.213 | 4.29 | 0.154 | regions | True |

## 装飾量・層構造（元の採用画像=ref との比）

DECOR_GATES: {"density_ratio_min": 0.6, "layer_color_dE_max": 30.0, "layer_sep_ratio_min": 0.6, "outside_flat_white_max": 0.15, "outside_tree_blobs_min": 6, "outside_tree_sides_min": 3, "desk_dE_area_max": 15.0, "desk_inter_take_dE_max": 8.0, "desk_grain_ratio_min": 0.8, "outside_evergreen_ratio_min": 0.3, "outside_branch_ratio_min": 0.3, "outside_grass_ratio_min": 0.2}

| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | FAIL | density:slab_front,density:floor,outside_evergreen | 0.9 | 30/ENSW | 0.0012/0.1625/0.0326 | 0.0085 |
| 2 | FAIL | FAIL | density:slab_front,outside_evergreen | 0.95 | 22/ENSW | 0.0024/0.1261/0.0346 | 0.0053 |
| 3 | FAIL | FAIL | density:floor,outside_evergreen | 0.95 | 21/ENSW | 0.0085/0.1306/0.0473 | 0.0009 |
| 4 | FAIL | FAIL | outside_evergreen | 1.05 | 35/ENSW | 0.0079/0.0755/0.0236 | 0.0086 |
| ref | - | - | - | 1.0 | 38/ENSW | 0.0468/0.0711/0.0141 | 0.001 |

領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）

| region | take1 | take2 | take3 | take4 | ref(エッジ密度,エントロピー) |
|---|---|---|---|---|---|
| desk | 1.0 / 0.75 / dE5.1 | 2.42 / 0.88 / dE9.5 | 1.52 / 0.89 / dE4.4 | 1.46 / 0.95 / dE5.8 | 0.0096, 5.323 |
| slab_front | 0.34 / 0.72 / dE8.8 | 0.49 / 0.71 / dE7.6 | 0.77 / 0.88 / dE5.2 | 0.68 / 0.91 / dE0.9 | 0.1033, 5.206 |
| outside | 1.04 / 0.99 / dE5.4 | 1.13 / 0.98 / dE7.0 | 1.05 / 1.08 / dE5.8 | 0.84 / 0.94 / dE9.4 | 0.0863, 5.731 |
| floor | 0.59 / 0.92 / dE7.3 | 0.62 / 1.03 / dE14.5 | 0.59 / 1.01 / dE10.9 | 0.64 / 1.07 / dE13.9 | 0.0298, 4.631 |
| wall | 0.95 / 0.94 | 0.92 / 1.01 | 0.94 / 0.98 | 0.93 / 1.0 | 0.0842, 7.127 |
| objects | 0.96 / 1.07 | 1.0 / 1.07 | 1.02 / 1.1 | 1.13 / 1.12 | 0.0893, 6.45 |

机の天面（エリア固定）: テイク間の最大ペア差 ΔE 6.3（基準 ≤8.0）→ OK

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-02.door-west | (0,-8) | (6,40) | (-6,12) | (-4,10) |
| door:TRM-02.door-outside | (-6,-2) | (-8,-26) | (-2,0) | (2,-6) |
| window:TRM-02.win-s1 | (0,-2) | (4,-14) | (6,0) | (-10,-10) |
| window:TRM-02.win-s2 | (4,0) | (2,-12) | (6,-4) | (-6,-10) |
| window:TRM-02.win-s3 | (4,0) | (-10,-12) | (-4,-6) | (4,-10) |
| window:TRM-02.win-s4 | (0,-2) | (0,-12) | (-6,-4) | (6,-10) |
| box:stage | (-32,-4) | (-20,-20) | (2,-2) | (-12,-14) |
| box:shelf-nw | (-6,4) | (26,-36) | (-16,-10) | (10,-16) |
| box:shelf-ne | (38,-14) | (40,-36) | (34,-10) | (38,-24) |
| box:chair-w1 (測定不能) | (-10,34) | (-6,36) | (-2,0) | (-4,10) |
| box:chair-w2 (測定不能) | (-6,-14) | (-6,36) | (-2,-14) | (-6,10) |
| box:chair-w3 | (-6,-14) | (-2,-14) | (-2,-16) | (-4,-10) |
| box:table-small | (0,-36) | (-2,-36) | (0,-26) | (-2,-34) |
| box:toy-rack | (2,0) | (0,-6) | (-16,-38) | (2,8) |
| box:round-table | (-18,28) | (36,24) | (36,32) | (38,28) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 38.55; 全体ピンク残り 0.0
- take2: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.001/g0.0; window:TRM-02.win-s2 w0.006/g0.0; window:TRM-02.win-s3 w0.004/g0.0; window:TRM-02.win-s4 w0.002/g0.0; 床lum_std 39.36; 全体ピンク残り 0.0
- take3: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 35.56; 全体ピンク残り 0.0
- take4: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.001/g0.0; window:TRM-02.win-s2 w0.002/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 37.88; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 4.04
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 4.34
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 3.82
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 4.25
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 3.69
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 3.85
  }
 ],
 "mean_pairwise_chamfer_px": 4.0,
 "blurred_lum_pixel_std_room_mean": 14.43,
 "region_shift_sd": {
  "door:TRM-02.door-west": {
   "dx_sd": 4.6,
   "dy_sd": 17.2
  },
  "door:TRM-02.door-outside": {
   "dx_sd": 3.8,
   "dy_sd": 10.3
  },
  "window:TRM-02.win-s1": {
   "dx_sd": 6.2,
   "dy_sd": 5.7
  },
  "window:TRM-02.win-s2": {
   "dx_sd": 4.6,
   "dy_sd": 4.8
  },
  "window:TRM-02.win-s3": {
   "dx_sd": 5.9,
   "dy_sd": 4.6
  },
  "window:TRM-02.win-s4": {
   "dx_sd": 4.2,
   "dy_sd": 4.1
  },
  "box:stage": {
   "dx_sd": 12.4,
   "dy_sd": 7.3
  },
  "box:shelf-nw": {
   "dx_sd": 16.0,
   "dy_sd": 14.4
  },
  "box:shelf-ne": {
   "dx_sd": 2.2,
   "dy_sd": 10.0
  },
  "box:chair-w1": {
   "dx_sd": 3.0,
   "dy_sd": 15.4
  },
  "box:chair-w2": {
   "dx_sd": 1.7,
   "dy_sd": 20.7
  },
  "box:chair-w3": {
   "dx_sd": 1.7,
   "dy_sd": 2.2
  },
  "box:table-small": {
   "dx_sd": 1.0,
   "dy_sd": 4.1
  },
  "box:toy-rack": {
   "dx_sd": 7.5,
   "dy_sd": 17.5
  },
  "box:round-table": {
   "dx_sd": 23.7,
   "dy_sd": 2.8
  }
 },
 "region_shift_sd_mean_px": 7.99
}
```

合格テイク（幾何）: [] / 合格（装飾）: [] / 合格（幾何+装飾）: [] / 追加ラウンド: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
