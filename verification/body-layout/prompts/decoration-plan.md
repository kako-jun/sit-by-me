# 体内BDY 装飾計画（MAPごとに変える）

生成元: `.claude/skills/sit-field-background/tools/build_body_prompt.py --plan <このファイル>`（表は `DECO_PICK` から機械出力。手で直さない）。
BDY-02・BDY-09 も新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』。採用済みの旧版は新版が採用されるまで残す。ビルダーは `--force-redo` が要る）。新プールは人体に関係する抽象的な工作物だけ（骨・細胞・筋肉の糸・鼓動線・皮膚・ばんそうこう・毛・ばい菌）。

| MAP | 役割 | 主役モチーフ族 | 配置パターン | 地形の色味 | 縁取り毛糸 | 土台縁のテープ・PVA | 机の木目 | 机の切れ端 |
|---|---|---|---|---|---|---|---|---|
| BDY-01 | 口(閉端) | BONE/SKIN/HAIR | corners | pink | cream | cream masking tape and clear-white PVA | medium honey-coloured oak grain | two short scraps of masking tape and a few thread ends in the lower-left corner of the desk |
| BDY-02 | 上半身(広間・首・分岐。作り直し) | PULSE/THREAD/SKIN | scatter | brown | deep skin-tone | cream masking tape and white PVA | warm medium-brown grain with fine straight lines | a few thread ends and a small clay crumb along the lower desk margin |
| BDY-03 | 下半身(合流) | CELL/PLASTER/PULSE | mass | skin | pale pink | ivory masking tape and white PVA | light pale birch grain with fine lines | a loose curl of tape and a toothpick lying along the top desk margin |
| BDY-05 | 左手1 | BONE/THREAD/GERM | wallband | skin | light skin-tone | kraft-brown paper tape and white PVA | dark walnut-coloured grain, fairly strong | a few thread ends and a small clay crumb in the upper-right corner of the desk |
| BDY-06 | 左手2(閉端) | SKIN/PULSE/HAIR | diagonal | pink | pale pink | white masking tape and a thin PVA line | medium grain with a visible knot near one side | a torn paper-tape strip and two tape scraps along the right desk margin |
| BDY-07 | 右手1 | CELL/PLASTER/HAIR | spiral | cream | cream | cream masking tape and white PVA | light honey grain, wide and soft | a small ball of leftover yarn and a toothpick in the lower-right corner of the desk |
| BDY-08 | 右手2(閉端) | GERM/BONE/THREAD | scatter | skin | light skin-tone | skin-coloured masking tape and white PVA | medium grain with tight lines | a few thread ends and tape scraps scattered along the left desk margin |
| BDY-09 | 左足1(作り直し) | HAIR/GERM/CELL | diagonal | cream | light skin-tone | ivory masking tape and a thin PVA line | pale honey grain with a few soft knots | two short thread tufts and a spare toothpick along the left desk margin |
| BDY-10 | 左足2 | BONE/PULSE/SKIN | wallband | pink | pale pink | cream masking tape and white PVA | dark reddish-brown grain | a small lump of clay with fingerprints and a thread end in the upper-left corner of the desk |
| BDY-11 | 左足3(閉端) | GERM/PLASTER/THREAD | mass | skin | cream | white masking tape and white PVA | light grain, nearly plain | two spare cream beads and a toothpick near the bottom desk margin |
| BDY-12 | 右足1 | THREAD/SKIN/GERM | spiral | cream | light skin-tone | cream masking tape and a thin PVA line | medium grain with long waves | a coil of yarn and one tape scrap in the upper-right corner of the desk |
| BDY-13 | 右足2 | CELL/BONE/HAIR | corners | pink | pale pink | kraft-brown paper tape and white PVA | dark grain with a few cracks | a few small clay balls and a thread end at the lower-left of the desk |
| BDY-14 | 右足3(閉端) | PLASTER/PULSE/GERM | diagonal | cream | cream | white masking tape and a thin PVA line | light pale grain with a soft stripe | paper-tape scraps and a crumb of clay along the right desk margin |

## 隣接MAPの被り検査（機械検査・違反があれば --all / --plan は停止）

| 隣接 | 主役族の重なり | 配置パターン | 地形の色味 |
|---|---|---|---|
| BDY-01 - BDY-02 | 1種 ['SKIN'] (<=1) | corners / scatter (異) | pink / brown (異) |
| BDY-02 - BDY-03 | 1種 ['PULSE'] (<=1) | scatter / mass (異) | brown / skin (異) |
| BDY-02 - BDY-05 | 1種 ['THREAD'] (<=1) | scatter / wallband (異) | brown / skin (異) |
| BDY-02 - BDY-07 | 0種  (<=1) | scatter / spiral (異) | brown / cream (異) |
| BDY-05 - BDY-06 | 0種  (<=1) | wallband / diagonal (異) | skin / pink (異) |
| BDY-07 - BDY-08 | 0種  (<=1) | spiral / scatter (異) | cream / skin (異) |
| BDY-03 - BDY-09 | 1種 ['CELL'] (<=1) | mass / diagonal (異) | skin / cream (異) |
| BDY-09 - BDY-10 | 0種  (<=1) | diagonal / wallband (異) | cream / pink (異) |
| BDY-10 - BDY-11 | 0種  (<=1) | wallband / mass (異) | pink / skin (異) |
| BDY-03 - BDY-12 | 0種  (<=1) | mass / spiral (異) | skin / cream (異) |
| BDY-12 - BDY-13 | 0種  (<=1) | spiral / corners (異) | cream / pink (異) |
| BDY-13 - BDY-14 | 0種  (<=1) | corners / diagonal (異) | pink / cream (異) |

## 左右の対（同じ族を使ってよいが配置は変える）

| 対 | 主役族 | 配置 |
|---|---|---|
| BDY-05 / BDY-07 | BONE/THREAD/GERM ; CELL/PLASTER/HAIR | wallband / spiral |
| BDY-06 / BDY-08 | SKIN/PULSE/HAIR ; GERM/BONE/THREAD | diagonal / scatter |
| BDY-09 / BDY-12 | HAIR/GERM/CELL ; THREAD/SKIN/GERM | diagonal / spiral |
| BDY-10 / BDY-13 | BONE/PULSE/SKIN ; CELL/BONE/HAIR | wallband / corners |
| BDY-11 / BDY-14 | GERM/PLASTER/THREAD ; PLASTER/PULSE/GERM | mass / diagonal |

## 規則

- 手の連続 05→06 / 07→08、足 09→10→11 / 12→13→14 は主役族の重なり1種以下・配置・色味を必ず変える。
- 地形の色味は隣接MAPと必ず変える（茶 brown は隣が肌・薄桃・クリームだけの BDY-02 に割り当て）。
- 赤い折り紙は模型の中の地形の上にちょうど6枚（模型の外・机・床・土台縁には置かない）。置き場所の言及は MAP ID を seed にした順で変える。
- 床は平らに空ける。装飾は地形・壁際・土台縁・机だけ。装飾は文章のみ（様式参照画像なし）。
