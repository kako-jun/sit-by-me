# 窓の一覧（機械生成。`oblique_topology.py`。手で直さない）

平面スペックの `windows[]` から生成。個数・位置・種別をすべて明示する。位置は壁沿いの中心座標（平面単位）と、壁の何割か（比。西→東・奥→手前）。種別: 掃き出し窓=床まで届く引き違い（扉ではない）／腰高窓。status: fixed=#51 等で既決／default=既定（要確認）。窓は見た目のみで、歩行マスク・オクルージョンには影響しない。

## 壁ごとの個数

| MAP | 壁 | 個数 | 種別 | status |
|---|---|---|---|---|
| TRM-05 | wall-n（wall） | 1 | 腰高窓 | default |
| TRM-05 | wall-s（wall） | 2 | 腰高窓 | fixed |
| TRM-04 | corr-w-s（wall） | 3 | 腰高窓 | fixed |
| TRM-04 | corr-e-s（wall） | 3 | 腰高窓 | fixed |
| TRM-02 | wall-s（wall） | 4 | 掃き出し窓 | default |
| TRM-03 | residence（住居（庫裏）） | 2 | 腰高窓 | fixed |
| TRM-03 | conn-w（渡り廊下棟） | 3 | 腰高窓 | fixed |
| TRM-03 | conn-e（渡り廊下棟） | 3 | 腰高窓 | fixed |
| TRM-03 | kindergarten（幼稚園（遊戯室）） | 4 | 掃き出し窓 | fixed |
| TRM-04 | hall-n（窓なし） | 0 | - | fixed（本堂に窓は置かない（決定 TRM.hall-no-window）） |
| TRM-04 | hall-w（窓なし） | 0 | - | fixed（本堂に窓は置かない（決定 TRM.hall-no-window）） |
| TRM-04 | hall-e（窓なし） | 0 | - | fixed（本堂に窓は置かない（決定 TRM.hall-no-window）） |
| TRM-04 | hall-s（窓なし） | 0 | - | fixed（本堂に窓は置かない（決定 TRM.hall-no-window）） |
| TRM-03 | main-hall（窓なし） | 0 | - | fixed（本堂に窓は置かない（決定 TRM.hall-no-window）） |

## 窓ごとの位置

| MAP | 壁 | 窓ID | 中心（平面単位） | 比 | 種別 | 寸法 | status | 備考 |
|---|---|---|---|---|---|---|---|---|
| TRM-05 | wall-n | `TRM-05.win-n1` | 1070 | 0.87 | 腰高窓 | 窓台50・高さ55・幅80 | default | 北壁の腰高窓1つ（石のすぐ左の壁）。種別・寸法は既定（要確認。掃き出しにしない）。石は北東の隅（決定 TRM-05.stone-pos） |
| TRM-05 | wall-s | `TRM-05.win-s1` | 850 | 0.57 | 腰高窓 | 窓台45・高さ55・幅120 | fixed | 南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）（決定 TRM.windows-spec） |
| TRM-05 | wall-s | `TRM-05.win-s2` | 1030 | 0.81 | 腰高窓 | 窓台45・高さ55・幅120 | fixed | 南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）（決定 TRM.windows-spec） |
| TRM-04 | corr-w-s | `TRM-04.win-cw1` | 160 | 0.17 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 西廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-04 | corr-w-s | `TRM-04.win-cw2` | 270 | 0.47 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 西廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-04 | corr-w-s | `TRM-04.win-cw3` | 380 | 0.77 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 西廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-04 | corr-e-s | `TRM-04.win-ce1` | 1230 | 0.24 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 東廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-04 | corr-e-s | `TRM-04.win-ce2` | 1340 | 0.54 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 東廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-04 | corr-e-s | `TRM-04.win-ce3` | 1450 | 0.84 | 腰高窓 | 窓台20・高さ50・幅70 | fixed | 東廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-02 | wall-s | `TRM-02.win-s1` | 390 | 0.09 | 掃き出し窓 | 窓台0・高さ130・幅140 | default | 南面の掃き出し窓（床まで届く引き違い・扉ではない）。枚数4は仮。位置は採用v3の窓の帯に合わせた既定（要確認）。窓から見えるのは室内の床で外の景色ではない（決定 TRM-03.kindergarten-bigger, TRM.windows-spec, TRM.window-glass） |
| TRM-02 | wall-s | `TRM-02.win-s2` | 573 | 0.27 | 掃き出し窓 | 窓台0・高さ130・幅140 | default | 南面の掃き出し窓（床まで届く引き違い・扉ではない）。枚数4は仮。位置は採用v3の窓の帯に合わせた既定（要確認）。窓から見えるのは室内の床で外の景色ではない（決定 TRM-03.kindergarten-bigger, TRM.windows-spec, TRM.window-glass） |
| TRM-02 | wall-s | `TRM-02.win-s3` | 757 | 0.46 | 掃き出し窓 | 窓台0・高さ130・幅140 | default | 南面の掃き出し窓（床まで届く引き違い・扉ではない）。枚数4は仮。位置は採用v3の窓の帯に合わせた既定（要確認）。窓から見えるのは室内の床で外の景色ではない（決定 TRM-03.kindergarten-bigger, TRM.windows-spec, TRM.window-glass） |
| TRM-02 | wall-s | `TRM-02.win-s4` | 940 | 0.64 | 掃き出し窓 | 窓台0・高さ130・幅140 | default | 南面の掃き出し窓（床まで届く引き違い・扉ではない）。枚数4は仮。位置は採用v3の窓の帯に合わせた既定（要確認）。窓から見えるのは室内の床で外の景色ではない（決定 TRM-03.kindergarten-bigger, TRM.windows-spec, TRM.window-glass） |
| TRM-03 | residence | `TRM-03.win-res1` | 285 | 0.67 | 腰高窓 | 窓台40・高さ50・幅50 | fixed | 住居棟の南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）（決定 TRM.windows-spec） |
| TRM-03 | residence | `TRM-03.win-res2` | 345 | 0.88 | 腰高窓 | 窓台40・高さ50・幅50 | fixed | 住居棟の南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）（決定 TRM.windows-spec） |
| TRM-03 | conn-w | `TRM-03.win-cw1` | 415 | 0.17 | 腰高窓 | 窓台13・高さ32・幅42 | fixed | 西の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | conn-w | `TRM-03.win-cw2` | 481 | 0.47 | 腰高窓 | 窓台13・高さ32・幅42 | fixed | 西の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | conn-w | `TRM-03.win-cw3` | 546 | 0.77 | 腰高窓 | 窓台13・高さ32・幅42 | fixed | 西の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | conn-e | `TRM-03.win-ce1` | 1002 | 0.23 | 腰高窓 | 窓台13・高さ32・幅35 | fixed | 東の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | conn-e | `TRM-03.win-ce2` | 1058 | 0.54 | 腰高窓 | 窓台13・高さ32・幅35 | fixed | 東の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | conn-e | `TRM-03.win-ce3` | 1113 | 0.84 | 腰高窓 | 窓台13・高さ32・幅35 | fixed | 東の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）（決定 TRM.building-shared） |
| TRM-03 | kindergarten | `TRM-03.win-kg1` | 1188 | 0.11 | 掃き出し窓 | 窓台0・高さ130・幅52 | fixed | 幼稚園棟の南面の掃き出し窓（床まで届く引き違い・扉ではない。玄関扉 door-playroom とは別）。枚数4は仮。位置は既定（要確認）（決定 TRM-03.kindergarten-bigger） |
| TRM-03 | kindergarten | `TRM-03.win-kg2` | 1254 | 0.26 | 掃き出し窓 | 窓台0・高さ130・幅52 | fixed | 幼稚園棟の南面の掃き出し窓（床まで届く引き違い・扉ではない。玄関扉 door-playroom とは別）。枚数4は仮。位置は既定（要確認）（決定 TRM-03.kindergarten-bigger） |
| TRM-03 | kindergarten | `TRM-03.win-kg3` | 1320 | 0.42 | 掃き出し窓 | 窓台0・高さ130・幅52 | fixed | 幼稚園棟の南面の掃き出し窓（床まで届く引き違い・扉ではない。玄関扉 door-playroom とは別）。枚数4は仮。位置は既定（要確認）（決定 TRM-03.kindergarten-bigger） |
| TRM-03 | kindergarten | `TRM-03.win-kg4` | 1386 | 0.58 | 掃き出し窓 | 窓台0・高さ130・幅52 | fixed | 幼稚園棟の南面の掃き出し窓（床まで届く引き違い・扉ではない。玄関扉 door-playroom とは別）。枚数4は仮。位置は既定（要確認）（決定 TRM-03.kindergarten-bigger） |

窓なしと確定した壁（no_window_walls）: 本堂（TRM-03 の本堂棟・TRM-04 の広間の壁）。kako-jun 決定 2026-10-23「本堂に窓はいらない」。
