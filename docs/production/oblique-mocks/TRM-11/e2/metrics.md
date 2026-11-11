# E2 測定 TRM-11 e2

ゲート: {"edge_recall_room_min": 0.6, "edge_margin_min": 0.15, "chamfer_room_max_px": 6.0, "region_shift_max_px": 8, "region_ok_ratio_min": 0.7, "door_pink_residual_max": 0.02, "window_white_green_max": 0.05, "aspect_tol": 0.005}

| take | 参考(幾何) | recall6 | margin | chamfer | region_ok | 基準超の項目 | 本物 |
|---|---|---|---|---|---|---|---|
| 1 | 基準内 | 0.928 | 0.294 | 2.53 | 0.727 | - | True |

建物の輪郭の指標（参考）: take1: 窓の平均|dy| 8.3・窓±8内 15/18・戸口±8内 0/1・全体ずれ中央値 [0.0, 2.0]

## 戸口・窓の存在確認／開口の床色／畳らしい色（参考。人が見る）

- take1: 戸口・窓の欠落 door:TRM-11.door／測定不能 0／開口が壁色に見える なし／畳らしい色の面積 0.0002

## 領域ごとの最良ずれ (dx,dy) px

| region | take1 |
|---|---|
| door:TRM-11.door | (10,-14) |
| window:TRM-11.win-a-1 | (-2,8) |
| window:TRM-11.win-a-3 | (-2,6) |
| window:TRM-11.win-a-4 | (-4,8) |
| window:TRM-11.win-a-5 | (-8,32) |
| window:TRM-11.win-b-1 | (0,32) |
| window:TRM-11.win-b-2 | (-2,28) |
| window:TRM-11.win-b-3 | (0,8) |
| window:TRM-11.win-b-4 | (-2,8) |
| window:TRM-11.win-c-1 | (-8,2) |
| window:TRM-11.win-c-2 | (2,2) |
| window:TRM-11.win-c-3 | (-2,2) |
| window:TRM-11.win-c-4 | (2,2) |
| window:TRM-11.win-c-5 | (2,2) |
| window:TRM-11.win-c-6 | (4,2) |
| window:TRM-11.win-c-7 | (4,2) |
| window:TRM-11.win-c-8 | (2,2) |
| window:TRM-11.win-c-9 | (0,2) |
| window:TRM-11.win-c-10 | (2,2) |
| box:slide | (28,-34) |
| box:sandbox | (-16,14) |
| box:bike | (2,-8) |

## 窓ガラス内 white/green・戸口ピンク残り

- take1: door:TRM-11.door pink0.0; window:TRM-11.win-a-1 w0.001/g0.0; window:TRM-11.win-a-3 w0.001/g0.0; window:TRM-11.win-a-4 w0.001/g0.0; window:TRM-11.win-a-5 w0.0/g0.0; window:TRM-11.win-b-1 w0.002/g0.0; window:TRM-11.win-b-2 w0.0/g0.0; window:TRM-11.win-b-3 w0.002/g0.0; window:TRM-11.win-b-4 w0.002/g0.0; window:TRM-11.win-c-1 w0.003/g0.0; window:TRM-11.win-c-2 w0.013/g0.0; window:TRM-11.win-c-3 w0.017/g0.0; window:TRM-11.win-c-4 w0.01/g0.0; window:TRM-11.win-c-5 w0.007/g0.0; window:TRM-11.win-c-6 w0.012/g0.0; window:TRM-11.win-c-7 w0.006/g0.0; window:TRM-11.win-c-8 w0.011/g0.0; window:TRM-11.win-c-9 w0.007/g0.0; window:TRM-11.win-c-10 w0.015/g0.0; 床lum_std 49.61; 全体ピンク残り 0.0

## テイク間

```
{}
```

基準内のテイク（幾何・参考）: ['1'] / 基準内（装飾・参考）: [] / 基準内（幾何+装飾・参考）: [] / 追加ラウンドの目安（参考）: 要

## kako-jun の目視確認項目

- 窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）
- 床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）
- 壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）
- 家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）
- 質感が工作の素材（綿の雪・紙粘土・段ボール・紙やすり）か。実写のような質感・本物の雪になっていないか（屋根・塀・地面・枝の雪がすべて綿か。決定 SIT.miniature-materials-not-photoreal。採否の前に必ず挙げる）
- 消雪パイプの穴が道路の中央線の上だけにあるか（路肩・縁・私有地・石畳に無いか。水の噴射が無いか。決定 SIT.shosetsu-hole-only）
- 景色の扉（閉じた門・潜り戸・格子戸・土蔵の扉）が入れそうに見えないか（前に段・通路・足跡・石段・開いた隙間が無く、塀・段差・植栽・雪で塞がれているか。決定 SIT.scenery-door-not-enterable）
- 台座の前縁・飾りがわざとらしくないか（テープ・糊が等間隔・全マップ同位置・同じ形の繰り返しになっていないか。マップごとにばらついているか。決定 SIT.base-edge-decor-random）
- 鉄道模型のジオラマのような質感か（雪は繊維の見える綿、木は簡略化したスポンジの塊、塀・柵は爪楊枝・割り箸・マッチ棒、地面はターフ・おがくず。形は単純で縁が硬く、写真のように精密でないか）
- 段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）
