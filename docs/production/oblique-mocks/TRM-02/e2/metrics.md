# E2 測定 TRM-02 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | 参考(幾何) | recall6 | margin | chamfer | region_ok | 基準超の項目 | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | 基準超 | 0.615 | 0.079 | 5.64 | 0.167 | edge_margin,regions | True |
| 2 | 基準超 | 0.685 | 0.162 | 5.59 | 0.333 | regions | True |
| 3 | 基準超 | 0.724 | 0.099 | 5.12 | 0.083 | edge_margin,regions | True |
| 4 | 基準超 | 0.651 | -0.004 | 5.96 | 0.0 | edge_margin,regions,window_content | True |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 9.0・窓±8内 2/4・戸口±8内 0/2・全体ずれ中央値 [-5.0, -9.0]; take2: 窓の平均|dy| 6.0・窓±8内 4/4・戸口±8内 0/2・全体ずれ中央値 [2.0, 6.0]; take3: 窓の平均|dy| 26.0・窓±8内 0/4・戸口±8内 0/2・全体ずれ中央値 [4.0, -16.0]; take4: 窓の平均|dy| 28.0・窓±8内 0/4・戸口±8内 0/2・全体ずれ中央値 [-7.0, -28.0]

## 戸口・窓の存在確認／開口の床色／畳らしい色（参考。人が見る）

- take1: 戸口・窓の欠落 なし／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0049
- take2: 戸口・窓の欠落 なし／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0009
- take3: 戸口・窓の欠落 なし／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0017
- take4: 戸口・窓の欠落 door:TRM-02.door-west、door:TRM-02.door-outside、window:TRM-02.win-s1／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.003

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-02.door-west | (-8,-40) | (-16,-40) | (12,-40) | (-22,-40) |
| door:TRM-02.door-outside | (10,-2) | (12,18) | (-8,-12) | (-18,-2) |
| window:TRM-02.win-s1 | (-12,-10) | (-6,6) | (6,-26) | (-20,-28) |
| window:TRM-02.win-s2 | (-6,-10) | (0,6) | (-2,-26) | (-4,-28) |
| window:TRM-02.win-s3 | (-4,-8) | (6,6) | (2,-26) | (0,-28) |
| window:TRM-02.win-s4 | (2,-8) | (8,6) | (10,-26) | (8,-28) |
| box:stage | (8,-34) | (4,10) | (10,-8) | (8,-12) |
| box:shelf-nw | (-28,20) | (-16,4) | (-8,-6) | (-6,-26) |
| box:shelf-ne | (22,14) | (18,2) | (30,16) | (8,-22) |
| box:chair-w1 (測定不能) | (-10,-40) | (-20,16) | (10,-4) | (-12,0) |
| box:chair-w2 (測定不能) | (-10,-30) | (-16,-34) | (-40,28) | (-8,-38) |
| box:chair-w3 | (-8,-38) | (-16,-2) | (8,-20) | (-8,-38) |
| box:table-small | (-20,-8) | (-12,-10) | (-10,-12) | (-30,-30) |
| box:toy-rack (測定不能) | (34,-20) | (-2,-22) | (6,-36) | (0,-26) |
| box:round-table | (40,-40) | (18,38) | (-4,14) | (-26,20) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.001/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 47.87; 全体ピンク残り 0.0
- take2: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.001/g0.0; window:TRM-02.win-s2 w0.0/g0.0; window:TRM-02.win-s3 w0.0/g0.0; window:TRM-02.win-s4 w0.0/g0.0; 床lum_std 48.18; 全体ピンク残り 0.0
- take3: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.006/g0.0; window:TRM-02.win-s2 w0.001/g0.0; window:TRM-02.win-s3 w0.001/g0.0; window:TRM-02.win-s4 w0.001/g0.0; 床lum_std 46.17; 全体ピンク残り 0.0
- take4: door:TRM-02.door-west pink0.0; door:TRM-02.door-outside pink0.0; window:TRM-02.win-s1 w0.031/g0.0; window:TRM-02.win-s2 w0.027/g0.0; window:TRM-02.win-s3 w0.048/g0.0; window:TRM-02.win-s4 w0.053/g0.0; 床lum_std 47.16; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 4.53
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 4.47
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 5.45
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 5.91
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 6.0
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 4.79
  }
 ],
 "mean_pairwise_chamfer_px": 5.19,
 "blurred_lum_pixel_std_room_mean": 23.12,
 "region_shift_sd": {
  "door:TRM-02.door-west": {
   "dx_sd": 12.8,
   "dy_sd": 0.0
  },
  "door:TRM-02.door-outside": {
   "dx_sd": 12.5,
   "dy_sd": 10.9
  },
  "window:TRM-02.win-s1": {
   "dx_sd": 9.5,
   "dy_sd": 13.7
  },
  "window:TRM-02.win-s2": {
   "dx_sd": 2.2,
   "dy_sd": 13.7
  },
  "window:TRM-02.win-s3": {
   "dx_sd": 3.6,
   "dy_sd": 13.9
  },
  "window:TRM-02.win-s4": {
   "dx_sd": 3.0,
   "dy_sd": 13.9
  },
  "box:stage": {
   "dx_sd": 2.2,
   "dy_sd": 15.7
  },
  "box:shelf-nw": {
   "dx_sd": 8.6,
   "dy_sd": 16.7
  },
  "box:shelf-ne": {
   "dx_sd": 7.9,
   "dy_sd": 15.1
  },
  "box:chair-w1": {
   "dx_sd": 11.0,
   "dy_sd": 20.5
  },
  "box:chair-w2": {
   "dx_sd": 12.8,
   "dy_sd": 27.0
  },
  "box:chair-w3": {
   "dx_sd": 8.7,
   "dy_sd": 14.9
  },
  "box:table-small": {
   "dx_sd": 7.9,
   "dy_sd": 8.8
  },
  "box:toy-rack": {
   "dx_sd": 14.4,
   "dy_sd": 6.2
  },
  "box:round-table": {
   "dx_sd": 24.6,
   "dy_sd": 29.1
  }
 },
 "region_shift_sd_mean_px": 12.06
}
```

基準内のテイク（幾何・参考）: [] / 基準内（装飾・参考）: [] / 基準内（幾何+装飾・参考）: [] / 追加ラウンドの目安（参考）: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
