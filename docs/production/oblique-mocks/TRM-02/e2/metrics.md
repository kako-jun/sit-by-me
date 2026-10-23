# E2 測定 TRM-02 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | FAIL | 0.776 | 0.281 | 3.74 | 0.615 | regions | True |
| 2 | FAIL | 0.937 | 0.364 | 2.11 | 0.692 | regions | True |
| 3 | PASS | 0.806 | 0.272 | 4.13 | 0.846 | - | True |
| 4 | PASS | 0.92 | 0.38 | 2.68 | 0.769 | - | True |

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-02.door-west | (-2,-6) | (-8,40) | (-18,10) | (-8,38) |
| door:TRM-02.door-outside | (8,-2) | (-2,2) | (-4,-6) | (-4,-2) |
| window:TRM-02.win-s1 | (0,-10) | (0,-2) | (-6,-8) | (-4,0) |
| window:TRM-02.win-s2 | (0,-10) | (0,2) | (-4,-6) | (0,0) |
| window:TRM-02.win-s3 | (0,-10) | (0,-2) | (-4,-6) | (0,0) |
| window:TRM-02.win-s4 | (0,-12) | (-2,-2) | (-4,-6) | (-2,0) |
| box:stage | (0,-12) | (0,-2) | (-2,-6) | (0,-4) |
| box:shelf-nw | (0,-8) | (0,-2) | (-12,-8) | (0,-8) |
| box:shelf-ne | (-2,-8) | (-20,38) | (0,-8) | (0,-6) |
| box:chair-w1 (測定不能) | (-6,30) | (-6,34) | (-6,28) | (-2,34) |
| box:chair-w2 (測定不能) | (-2,-6) | (-2,-2) | (-2,-8) | (2,-14) |
| box:chair-w3 | (-2,-4) | (-2,-2) | (-2,-6) | (2,-16) |
| box:table-small | (-4,2) | (-12,-20) | (2,-6) | (0,-24) |
| box:toy-rack | (0,-8) | (-2,-28) | (4,-6) | (0,-4) |
| box:round-table | (-4,-6) | (2,8) | (0,-2) | (-4,-2) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 28.2; 全体ピンク残り 0.0
- take2: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.007/g0.0; window:TRM-02.win-s2 w0.016/g0.0; window:TRM-02.win-s3 w0.016/g0.0; window:TRM-02.win-s4 w0.008/g0.0; 床lum_std 31.32; 全体ピンク残り 0.0
- take3: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 24.56; 全体ピンク残り 0.0
- take4: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.0/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 33.26; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 5.4
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 7.4
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 7.47
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 7.03
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 6.1
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 5.47
  }
 ],
 "mean_pairwise_chamfer_px": 6.48,
 "blurred_lum_pixel_std_room_mean": 12.21,
 "region_shift_sd": {
  "door:TRM-02.door-west": {
   "dx_sd": 5.7,
   "dy_sd": 19.4
  },
  "door:TRM-02.door-outside": {
   "dx_sd": 5.0,
   "dy_sd": 2.8
  },
  "window:TRM-02.win-s1": {
   "dx_sd": 2.6,
   "dy_sd": 4.1
  },
  "window:TRM-02.win-s2": {
   "dx_sd": 1.7,
   "dy_sd": 4.8
  },
  "window:TRM-02.win-s3": {
   "dx_sd": 1.7,
   "dy_sd": 3.8
  },
  "window:TRM-02.win-s4": {
   "dx_sd": 1.4,
   "dy_sd": 4.6
  },
  "box:stage": {
   "dx_sd": 0.9,
   "dy_sd": 3.7
  },
  "box:shelf-nw": {
   "dx_sd": 5.2,
   "dy_sd": 2.6
  },
  "box:shelf-ne": {
   "dx_sd": 8.4,
   "dy_sd": 19.6
  },
  "box:chair-w1": {
   "dx_sd": 1.7,
   "dy_sd": 2.6
  },
  "box:chair-w2": {
   "dx_sd": 1.7,
   "dy_sd": 4.3
  },
  "box:chair-w3": {
   "dx_sd": 1.7,
   "dy_sd": 5.4
  },
  "box:table-small": {
   "dx_sd": 5.4,
   "dy_sd": 10.5
  },
  "box:toy-rack": {
   "dx_sd": 2.2,
   "dy_sd": 9.6
  },
  "box:round-table": {
   "dx_sd": 2.6,
   "dy_sd": 5.2
  }
 },
 "region_shift_sd_mean_px": 5.03
}
```

合格テイク: ['3', '4'] / 追加ラウンド: 不要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
