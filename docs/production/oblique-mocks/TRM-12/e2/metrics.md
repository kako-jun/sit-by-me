# E2 測定 TRM-12 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | 参考(幾何) | recall6 | margin | chamfer | region_ok | 基準超の項目 | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | 基準超 | 0.67 | 0.235 | 6.28 | 0.091 | chamfer,regions | True |
| 2 | 基準超 | 0.837 | 0.41 | 4.15 | 0.455 | regions | True |
| 3 | 基準超 | 0.856 | 0.458 | 3.87 | 0.545 | regions | True |
| 4 | 基準超 | 0.78 | 0.359 | 7.46 | 0.364 | chamfer,regions | True |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 14.0・窓±8内 0/2・戸口±8内 0/1・全体ずれ中央値 [0.0, 14.0]; take2: 窓の平均|dy| 0.0・窓±8内 2/2・戸口±8内 1/1・全体ずれ中央値 [2.0, 0.0]; take3: 窓の平均|dy| 3.0・窓±8内 2/2・戸口±8内 1/1・全体ずれ中央値 [-2.0, -2.0]; take4: 窓の平均|dy| 2.0・窓±8内 2/2・戸口±8内 0/1・全体ずれ中央値 [2.0, -2.0]

## 戸口・窓の存在確認／開口の床色／畳らしい色（参考。人が見る）

- take1: 戸口・窓の欠落 door:TRM-12.door／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0
- take2: 戸口・窓の欠落 なし／測定不能 0／開口が壁色に見える open-dk-a／畳らしい色の面積 0.0002
- take3: 戸口・窓の欠落 window:TRM-12.win-n-a／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0006
- take4: 戸口・窓の欠落 window:TRM-12.win-n-b／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0001

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-12.door | (-4,32) | (-6,0) | (2,2) | (14,-10) |
| window:TRM-12.win-n-a | (8,14) | (0,0) | (-2,-2) | (2,-2) |
| window:TRM-12.win-n-b | (0,14) | (8,0) | (-2,-4) | (2,2) |
| box:sink | (4,12) | (18,14) | (10,22) | (14,-40) |
| box:stove (測定不能) | (4,-6) | (40,-2) | (6,-34) | (20,2) |
| box:fridge | (8,30) | (4,-34) | (14,-32) | (16,0) |
| box:table | (-4,34) | (2,6) | (-4,4) | (-6,4) |
| box:chair-1 (測定不能) | (-2,22) | (-12,-40) | (20,-26) | (16,0) |
| box:chair-2 | (8,32) | (-2,-32) | (-30,-26) | (-34,0) |
| box:tv | (-4,12) | (2,24) | (-6,-14) | (-8,-28) |
| box:dresser | (6,-36) | (22,-32) | (-2,-6) | (38,-10) |
| box:low-table | (-8,2) | (0,-12) | (-2,6) | (2,-20) |
| box:closet | (-20,20) | (6,4) | (-40,26) | (8,0) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-12.door pink0.0; window:TRM-12.win-n-a w0.0/g0.0; window:TRM-12.win-n-b w0.0/g0.0; 床lum_std 43.04; 全体ピンク残り 0.0
- take2: door:TRM-12.door pink0.0; window:TRM-12.win-n-a w0.003/g0.0; window:TRM-12.win-n-b w0.003/g0.0; 床lum_std 35.76; 全体ピンク残り 0.0
- take3: door:TRM-12.door pink0.0; window:TRM-12.win-n-a w0.0/g0.0; window:TRM-12.win-n-b w0.0/g0.0; 床lum_std 36.97; 全体ピンク残り 0.0
- take4: door:TRM-12.door pink0.0; window:TRM-12.win-n-a w0.016/g0.0; window:TRM-12.win-n-b w0.019/g0.0; 床lum_std 31.88; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 8.32
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 9.82
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 9.44
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 6.21
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 6.68
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 6.25
  }
 ],
 "mean_pairwise_chamfer_px": 7.79,
 "blurred_lum_pixel_std_room_mean": 17.63,
 "region_shift_sd": {
  "door:TRM-12.door": {
   "dx_sd": 7.8,
   "dy_sd": 15.7
  },
  "window:TRM-12.win-n-a": {
   "dx_sd": 3.7,
   "dy_sd": 6.7
  },
  "window:TRM-12.win-n-b": {
   "dx_sd": 3.7,
   "dy_sd": 6.7
  },
  "box:sink": {
   "dx_sd": 5.2,
   "dy_sd": 24.5
  },
  "box:stove": {
   "dx_sd": 14.4,
   "dy_sd": 14.1
  },
  "box:fridge": {
   "dx_sd": 4.8,
   "dy_sd": 26.2
  },
  "box:table": {
   "dx_sd": 3.0,
   "dy_sd": 12.7
  },
  "box:chair-1": {
   "dx_sd": 13.1,
   "dy_sd": 23.9
  },
  "box:chair-2": {
   "dx_sd": 17.9,
   "dy_sd": 25.3
  },
  "box:tv": {
   "dx_sd": 3.7,
   "dy_sd": 20.6
  },
  "box:dresser": {
   "dx_sd": 15.4,
   "dy_sd": 13.2
  },
  "box:low-table": {
   "dx_sd": 3.7,
   "dy_sd": 10.5
  },
  "box:closet": {
   "dx_sd": 19.8,
   "dy_sd": 10.8
  }
 },
 "region_shift_sd_mean_px": 12.58
}
```

基準内のテイク（幾何・参考）: [] / 基準内（装飾・参考）: [] / 基準内（幾何+装飾・参考）: [] / 追加ラウンドの目安（参考）: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
