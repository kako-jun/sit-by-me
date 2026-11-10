# E2 測定 TRM-05 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | 参考(幾何) | recall6 | margin | chamfer | region_ok | 基準超の項目 | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | 基準超 | 0.435 | 0.019 | 11.23 | 0.071 | edge_recall,edge_margin,chamfer,regions | True |
| 2 | 基準超 | 0.679 | 0.28 | 6.34 | 0.214 | chamfer,regions,window_content | True |
| 3 | 基準超 | 0.413 | -0.002 | 12.11 | 0.0 | edge_recall,edge_margin,chamfer,regions | True |
| 4 | 基準超 | 0.562 | 0.133 | 8.19 | 0.143 | edge_recall,edge_margin,chamfer,regions | True |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 17.3・窓±8内 0/3・戸口±8内 0/3・全体ずれ中央値 [9.0, -15.0]; take2: 窓の平均|dy| 0.0・窓±8内 2/3・戸口±8内 0/3・全体ずれ中央値 [1.0, -8.0]; take3: 窓の平均|dy| 32.0・窓±8内 0/3・戸口±8内 0/3・全体ずれ中央値 [17.0, 13.0]; take4: 窓の平均|dy| 12.7・窓±8内 1/3・戸口±8内 1/3・全体ずれ中央値 [1.0, -13.0]

## 戸口・窓の存在確認／開口の床色／畳らしい色（参考。人が見る）

- take1: 戸口・窓の欠落 door:TRM-05.door-outside、door:TRM-05.door-back、window:TRM-05.win-s2、window:TRM-05.win-n1／測定不能 1／開口が壁色に見える open-dining-bed-n、open-dining-bed-s／畳らしい色の面積 0.0077（警告）
- take2: 戸口・窓の欠落 なし／測定不能 1／開口が壁色に見える なし／畳らしい色の面積 0.0
- take3: 戸口・窓の欠落 door:TRM-05.door-back、window:TRM-05.win-s1／測定不能 1／開口が壁色に見える open-dining-bed-n、open-dining-bed-s／畳らしい色の面積 0.0049
- take4: 戸口・窓の欠落 window:TRM-05.win-s2／測定不能 1／開口が壁色に見える open-dining-bed-n、open-dining-bed-s／畳らしい色の面積 0.0065（警告）

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 | take2 | take3 | take4 |
|---|---|---|---|---|
| door:TRM-05.door-hall | (-12,34) | (24,40) | (24,8) | (2,-40) |
| door:TRM-05.door-outside | (22,10) | (2,24) | (26,28) | (18,28) |
| door:TRM-05.door-back | (40,-36) | (38,-40) | (40,-30) | (-6,-6) |
| window:TRM-05.win-s1 | (-22,-10) | (-4,0) | (16,34) | (-6,18) |
| window:TRM-05.win-s2 | (28,18) | (0,0) | (18,40) | (2,18) |
| window:TRM-05.win-n1 | (8,-24) | (-10,0) | (-2,22) | (-6,-2) |
| box:stove | (40,-12) | (8,-30) | (34,-40) | (36,-34) |
| box:sink | (8,8) | (-4,-28) | (-20,-16) | (-28,-38) |
| box:cupboard | (6,-18) | (-2,-40) | (8,-26) | (40,10) |
| box:fridge | (6,-26) | (2,8) | (-40,32) | (-6,-40) |
| box:shelf-w (測定不能) | (4,-38) | (-2,-40) | (-36,0) | (-20,-10) |
| box:table | (10,-34) | (2,-40) | (-8,-12) | (0,-24) |
| box:bench-l | (16,-22) | (6,-16) | (36,-20) | (-18,-20) |
| box:bench-r (測定不能) | (-40,20) | (-2,4) | (-40,30) | (-32,12) |
| box:dresser | (-18,40) | (-22,14) | (38,34) | (40,2) |
| box:rock (測定不能) | (20,30) | (34,4) | (24,10) | (34,-24) |
| box:chest | (40,-18) | (-12,-40) | (-10,18) | (6,-34) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.008/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.01/g0.0; 床lum_std 53.73; 全体ピンク残り 0.0
- take2: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.144/g0.0; 床lum_std 44.86; 全体ピンク残り 0.0
- take3: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.002/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 51.75; 全体ピンク残り 0.0
- take4: door:TRM-05.door-hall pink0.0; door:TRM-05.door-outside pink0.0; door:TRM-05.door-back pink0.0; window:TRM-05.win-s1 w0.0/g0.0; window:TRM-05.win-s2 w0.0/g0.0; window:TRM-05.win-n1 w0.0/g0.0; 床lum_std 52.17; 全体ピンク残り 0.0

## テイク間

```
{
 "pairwise_chamfer": [
  {
   "pair": "1-2",
   "sym_chamfer_room_px": 10.3
  },
  {
   "pair": "1-3",
   "sym_chamfer_room_px": 9.39
  },
  {
   "pair": "1-4",
   "sym_chamfer_room_px": 10.33
  },
  {
   "pair": "2-3",
   "sym_chamfer_room_px": 8.81
  },
  {
   "pair": "2-4",
   "sym_chamfer_room_px": 5.16
  },
  {
   "pair": "3-4",
   "sym_chamfer_room_px": 7.01
  }
 ],
 "mean_pairwise_chamfer_px": 8.5,
 "blurred_lum_pixel_std_room_mean": 27.18,
 "region_shift_sd": {
  "door:TRM-05.door-hall": {
   "dx_sd": 15.3,
   "dy_sd": 31.5
  },
  "door:TRM-05.door-outside": {
   "dx_sd": 9.1,
   "dy_sd": 7.4
  },
  "door:TRM-05.door-back": {
   "dx_sd": 19.6,
   "dy_sd": 13.2
  },
  "window:TRM-05.win-s1": {
   "dx_sd": 13.5,
   "dy_sd": 16.9
  },
  "window:TRM-05.win-s2": {
   "dx_sd": 11.6,
   "dy_sd": 14.2
  },
  "window:TRM-05.win-n1": {
   "dx_sd": 6.7,
   "dy_sd": 16.3
  },
  "box:stove": {
   "dx_sd": 12.6,
   "dy_sd": 10.4
  },
  "box:sink": {
   "dx_sd": 14.0,
   "dy_sd": 17.2
  },
  "box:cupboard": {
   "dx_sd": 16.0,
   "dy_sd": 18.2
  },
  "box:fridge": {
   "dx_sd": 18.1,
   "dy_sd": 28.3
  },
  "box:shelf-w": {
   "dx_sd": 15.7,
   "dy_sd": 17.4
  },
  "box:table": {
   "dx_sd": 6.4,
   "dy_sd": 10.6
  },
  "box:bench-l": {
   "dx_sd": 19.4,
   "dy_sd": 2.2
  },
  "box:bench-r": {
   "dx_sd": 15.6,
   "dy_sd": 9.6
  },
  "box:dresser": {
   "dx_sd": 29.5,
   "dy_sd": 15.3
  },
  "box:rock": {
   "dx_sd": 6.2,
   "dy_sd": 19.3
  },
  "box:chest": {
   "dx_sd": 20.8,
   "dy_sd": 22.6
  }
 },
 "region_shift_sd_mean_px": 15.31
}
```

基準内のテイク（幾何・参考）: [] / 基準内（装飾・参考）: [] / 基準内（幾何+装飾・参考）: [] / 追加ラウンドの目安（参考）: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
