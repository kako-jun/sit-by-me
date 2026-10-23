#!/usr/bin/env python3
"""体内 BDY-01..17 の配置モック（割付図）を幾何で作り、接続を機械検査する。

画像生成はしない。出力は 1920x1080 の単純図（床帯・辺ラベル・MAP ID）。後工程で imagegen の土台にする。

実行: uv run --with pillow python3 body_layout.py [--out DIR] [--main-width-ratio 0.14]
清書用: ... body_layout.py --clean --out verification/body-layout/clean
  --clean は imagegen の塗り直し土台用。文字・注記・遷移範囲の着色を描かず、床・地形・土台の縁・机(・広間の壁)を別の単色領域にする。
  構図: 机 -> 土台の縁の帯 -> 模型の天面。通路は模型の縁まで（画像端でない）。
  通路の幾何（本数・辺・位置・幅・経路）は通常版と同一コードで描くので不変（検査は pixel_check）。

正本（このコードは読むだけ。原文を要約・補完しない）:
  docs/map-topology.md の BDY door 行      -> 接続（MAP.port -> MAP.port）
  docs/topology/body.svg の node 座標       -> 出る辺の導出（頭=上, 手=斜め上, 足=斜め下）
  docs/map-specifications.md BDY-02 行      -> BDY-02 の方位指定（口=北東 ほか）と「首の通路は1本・頭は枝」

辺の決め方（原文に辺の指定は無いので、以下は『提案』であり原文ではない）:
  1. 親（BDY-02 を根とした木で根に近い側）から子へ向かう body.svg 上のベクトルの向きで、親側の出る辺を決める。
     角度は 北=上(SVG y が小さい方)。|dx| と |dy| を比べて大きい軸の側。|dx|==|dy|（真の斜め45度）は縦軸（N/S）を採る。
  2. 子側の入る辺は、親の出た辺の反対（map-topology.md 冒頭規則「→の両側は必ず反対の画像辺」）。
  3. 1つの辺に複数の通路があるときは、body.svg 上の相手の座標順に並べる（位置は提案。接続の一致条件ではない）。
"""
import argparse
import math
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

W, H = 1920, 1080
REPO = Path(__file__).resolve().parents[4]
# 正本 docs（map-topology.md・topology/body.svg）の置き場。既定はリポ。別の版で作りたい時だけ環境変数で差し替える
DOCS = Path(__import__("os").environ.get("BODY_DOCS_ROOT", REPO))
FONT = "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"

# 主路幅 = キャラクター3人が横に並べる幅。キャラ1人の画像幅比は原文に無い（TBD）ので、
# 「3人並び」を満たすための仮置きとして画像幅の 14%（= 1人あたり約4.7%）を既定にする。数値自体は TBD。
DEFAULT_MAIN_WIDTH_RATIO = 0.14

# BDY-02 の「首の通路は1本・頭はそこから分かれる北向きの枝」を満たす個別指定（正規化座標 0..1）。
# それ以外のMAPは portal -> 内側へ垂直 -> ハブ（画像中心付近）の汎用経路。
# slot: 辺上の位置（0..1、N/S辺なら x、E/W辺なら y）の提案値。
LW17_DIV = 3  # BDY-17・BDY-04 の通路幅 = 主路幅の 1/3（キャラ1人分。主路幅=3人並び）。入口の帯も1人幅（原文に無く『要確認』）


def mlw(m, lw):
    """MAPごとの通路幅。BDY-17・BDY-04（迷路）は 1人幅（主路幅/3）、他は主路幅。"""
    return int(round(lw / LW17_DIV)) if m in ONE_PERSON_MAPS else lw


ONE_PERSON_MAPS = ("BDY-17", "BDY-04")


BDY02_SLOTS = {
    "door-passage-head": 0.50,
    "door-passage-mouth": 0.74,
    "door-passage-left-arm": 0.28,    # 左右は身体の本人から見る（kako-jun 決定 #142 2026-10-22）。本人の左手 = 画面右 = 東辺
    "door-passage-lung": 0.26,        # 肺 = 画面左寄り x≈450–680（心臓は本人の左側 = 画面右。確定）
    "door-passage-heart": 0.74,       # 心臓 = 画面右寄り x≈1239–1469（確定）
    "door-passage-lower": 0.50,
    "door-passage-right-arm": 0.50,   # 本人の右手 = 画面左 = 西辺
}
HUB = {"BDY-02": (0.50, 0.50)}

# BDY-02 の新しい形（kako-jun 決定 #142『首は A案』）: 広間(丸い床+壁) -> 首(1本の太い帯) -> 分岐点 J -> 頭(ほぼ真北)・口(右上へ斜め→最後は辺に垂直)。
# 他の5本（左腕・右腕・肺・心臓・下半身）は広間に別々の角度で接する帯。辺の位置・本数・幅は不変。座標は画像 px。
# 広間は『首が見える長さ』を取るため、旧版（半径265・中心=模型中心）より小さく少し南へ寄せた。壁の厚み・台座なしは従来どおり。
BDY02_HALL = ((960, 700), 205)
BDY02_HALL_RX = 300           # 広間は横長の楕円（縦半径=BDY02_HALL[1]、横半径=この値）。6本の帯を別々に接するための周長
BDY02_J = (960, 350)          # 首の分岐点（広間と北辺の間）。首はここまで1本
BDY02_K_Y = 225               # 口の帯が辺へ垂直に曲がる高さ（辺に垂直な最後の区間 = 位置・幅が仕様どおり）
# 5本の帯: 辺の点から広間の中へ入る折れ線の途中の点（絶対 px）。最後の点は広間の床の内側。端は port=辺上の点。
BDY02_ARMS = {
    # 左右は身体の本人から見る（kako-jun 決定 #142 2026-10-22『本人は仰向け、それを正面から見ている。画面左側は右手』）。
    # 右腕（西辺）: 西辺 y425-655（辺から水平に 162px）-> 折れ点 (300,540) から広間へ向けて右下へ 16.7 度の斜め（kako-jun 2026-10-22『分岐にガクッと段差』の修正を踏襲）。
    # 旧版は水平のまま (800,540) で帯の端を平らに切っていたため、広間の楕円の縁より北側にはみ出した端の縦の切り口が段差になっていた。
    "door-passage-right-arm": [(300, 540), (800, 690)],
    # 左腕（東辺 slot0.28）: 辺から水平に入り、広間へ左下へ斜め（旧『右腕』の形をそのまま左腕に。口の分岐に北東で近い）
    "door-passage-left-arm": [(1662, 363), (1090, 650)],
    # 心臓（本人の左 = 画面右、南辺右寄り。確定）: 垂直に入り、左上へ斜めで広間へ（旧『肺』の形）
    "door-passage-heart": [(1355, 800), (1160, 745)],
    # 肺（画面左寄り。確定）: 垂直に入り、右上へ斜めで広間へ（旧『心臓』の形）
    "door-passage-lung": [(565, 800), (760, 745)],
    "door-passage-lower": [(960, 800)],
}

# ---- 体内の手足は『斜めに伸びる道』（kako-jun 確定 2026-10-22。原文: 胴体を真ん中として頭は上方向に、両手は右上、左上方向に、
#      足は右下、左下方向に、一本道の通路としてかけばいい / map-topology.md 686行付近・body.svg）----
# 模型の天面を原点とした px 座標 (0..MW, 0..MH)。BDY-02 以外はここで形を決める（BDY-02 は採用済みの形をそのまま使う）。
# ports: port -> (出る/入る辺, 辺上の位置の比)。辺は map-topology.md + body.svg から導いた側と一致すること（検査C2b）。
# paths: 折れ線。str は port（その辺上の点）、(x,y) は模型内の点。port で終わる端は模型の縁まで届く。
#        port でない端は丸い閉じた端（末端）か合流点。kind: limb=斜めであること(水平垂直から15度以上)を検査 / trunk=胴の縦通路 / stub=TBD枠への入口
MW0, MH0 = 1644, 804  # 模型の天面（W-2*MARGIN, H-2*MARGIN）。下で MARGIN から導く値と一致を assert
# BDY-09（左足1）の折れ点 = 膝の1つだけ（kako-jun 指示 2026-10-22『２回曲げちゃダメだ。関節は１つであるべき』→『極端すぎる。もっとちょっと曲がった程度でいいのだ。鈍角にしろ』）。
# 2区間とも同じ側（右下）へ進み続け、膝で進行方向が35度だけ変わる（内角145度の鈍角）。模型の天面基準 px。BDY-12 は x を左右反転。
# 入口（西辺）は 0.35→0.292、出口（南辺）は 0.392→0.407 へ動かした（鈍角の1折れを模型の天面に収めるため。接続は辺の反対だけで成立し位置の画素一致は条件外）。
THIGH_ENTRY_SLOT, THIGH_EXIT_SLOT = 0.292, 0.407
THIGH_KNEES = [(503, 491)]   # 付け根(0,235)→膝: 右下27度 / 膝→足首側(669,804): 右下62度。進行方向の変化 35度・中心線 約919px（旧の直線830pxの約1.11倍）
# BDY-15 胃の袋の中心線: ドーム(胃底)から真下へ少し、半径295の四分円で下から右へ曲がり(J字)、右へ進みながら細くなって丸い端(幽門)。制御点=(x,y,半径)。
# 曲がりの中心線の曲率半径(295)は袋の最大半径(232)より大きい＝内側の輪郭が尖らない（凹みは半径63の丸み）。
_SC = (740, 252); _SR = 295
SAC15 = [(445, 244, 222), (445, 252, 222)] + [(round(_SC[0] + _SR * math.cos(math.radians(a_))), round(_SC[1] + _SR * math.sin(math.radians(a_))), r_)
                                              for a_, r_ in ((150, 226), (120, 230), (90, 232))] + [(950, 555, 205), (1180, 530, 115), (1390, 455, 65)]

SPECS = {
    "BDY-01": dict(ports={"door-passage-torso": ("S", 0.60)},
                   paths=[dict(kind="limb", pts=["door-passage-torso", (1300, 470)])]),
    "BDY-03": dict(ports={"door-passage-upper": ("N", 0.50), "door-passage-left-leg": ("E", 0.82),
                          "door-passage-right-leg": ("W", 0.82), "door-passage-stomach": ("E", 0.162)},
                   paths=[dict(kind="trunk", pts=["door-passage-upper", (822, 400)]),
                          dict(kind="limb", pts=[(822, 400), "door-passage-left-leg"]),
                          dict(kind="limb", pts=[(822, 400), "door-passage-right-leg"]),
                          dict(kind="limb", pts=[(822, 400), "door-passage-stomach"])]),
    # 左手（本人の左 = 画面右）: BDY-02 の東辺から出て西辺から入り、右上へ斜め（左右は本人から見る。kako-jun 決定 #142 2026-10-22）
    "BDY-05": dict(ports={"door-passage-torso": ("W", 0.50), "door-passage-tip": ("N", 0.392)},
                   paths=[dict(kind="limb", pts=["door-passage-torso", "door-passage-tip"])]),
    "BDY-06": dict(ports={"door-passage-base": ("S", 0.392)},
                   paths=[dict(kind="limb", pts=["door-passage-base", (1124, 424)])]),
    # 右手（本人の右 = 画面左）: BDY-02 の西辺から出て東辺から入り、左上へ斜め
    "BDY-07": dict(ports={"door-passage-torso": ("E", 0.50), "door-passage-tip": ("N", 0.608)},
                   paths=[dict(kind="limb", pts=["door-passage-torso", "door-passage-tip"])]),
    "BDY-08": dict(ports={"door-passage-base": ("S", 0.608)},
                   paths=[dict(kind="limb", pts=["door-passage-base", (520, 424)])]),
    # 左足（本人の左 = 画面右）: BDY-03 の東辺から出て西辺から入り、右下へ斜め
    # 太ももは1マップ内の道が短くもったいない（kako-jun 指示 2026-10-22『曲がってる感じしてはどうか』）ので、斜めの帯に膝の曲がりを1つだけ入れる
    # （『２回曲げちゃダメだ。関節は１つであるべき』『極端すぎる。もっとちょっと曲がった程度でいいのだ。鈍角にしろ』）: 付け根（西辺）から右下27度、膝（折れ点1つ）で
    # 右下62度へ35度だけ向きを変えて南辺へ。入口・出口の辺は不変（辺上の位置は上の THIGH_*_SLOT）。2区間とも水平垂直から15度以上、折れ点は丸い。中心線は旧（直線830px）の約1.11倍。
    "BDY-09": dict(ports={"door-passage-torso": ("W", THIGH_ENTRY_SLOT), "door-passage-middle": ("S", THIGH_EXIT_SLOT)},
                   paths=[dict(kind="limb", pts=["door-passage-torso", *THIGH_KNEES, "door-passage-middle"])]),
    "BDY-10": dict(ports={"door-passage-base": ("N", 0.392), "door-passage-tip": ("S", 0.70)},
                   paths=[dict(kind="limb", pts=["door-passage-base", "door-passage-tip"])]),
    "BDY-11": dict(ports={"door-passage-base": ("N", 0.70)},
                   paths=[dict(kind="limb", pts=["door-passage-base", (1494, 480)])]),
    # 右足（本人の右 = 画面左）: BDY-03 の西辺から出て東辺から入り、左下へ斜め
    # BDY-09 の左右ミラー（折れ点の x を MW0 - x に）
    "BDY-12": dict(ports={"door-passage-torso": ("E", THIGH_ENTRY_SLOT), "door-passage-middle": ("S", round(1 - THIGH_EXIT_SLOT, 3))},
                   paths=[dict(kind="limb", pts=["door-passage-torso", *[(MW0 - kx, ky) for kx, ky in THIGH_KNEES], "door-passage-middle"])]),
    "BDY-13": dict(ports={"door-passage-base": ("N", 0.608), "door-passage-tip": ("S", 0.30)},
                   paths=[dict(kind="limb", pts=["door-passage-base", "door-passage-tip"])]),
    "BDY-14": dict(ports={"door-passage-base": ("N", 0.30)},
                   paths=[dict(kind="limb", pts=["door-passage-base", (150, 480)])]),
    # 保留4枚（BDY-04/15/16/17）の『仮案』（kako-jun 指示 2026-10-22: 肺や心臓は医学的な4つ等の区分を抽象的な部屋で、脳は迷路状）。
    # 入口は1本だけ（辺と位置は接続表+body.svg 由来で不変）。rooms=(名前, x, y, 半径) 丸い部屋の床。名前は mock の注記にだけ描く（清書版には描かない）。
    # paths の kind: entry=入口から最初の合流点まで / maze=迷路の通路 / link=部屋どうしをつなぐ通路。座標は模型の天面基準 px。
    # expect = 機械検査の期待値（部屋数・曲がり数・T字分岐数・行き止まり数）。
    "BDY-04": None,  # 下の make_maze_spec() が作る（seed固定の迷路生成）
    # BDY-15 胃（kako-jun 指摘『なぜ胃が2つに分岐したようになってるのだ？人間はそうなのか？』で作り直し・分岐なしJ字の1袋）。
    # 入口(西辺)=噴門から、分岐のない1つの袋がJ字に曲がる: 入口のすぐ上に丸いドーム(胃底=袋の一部)、そこから幅広い袋の本体(胃体)が下へ膨らみ、
    # 右へ曲がって細くなり(幽門)、丸く閉じた端で終わる(出口は十二指腸へ続くが、このMAPの接続は入口1本だけなので行き止まり)。
    # 袋の形は SAC（中心線の制御点 (x,y,半径) を滑らかにつないだ掃引）。graph は曲がり・行き止まりを数えるための簡略中心線(描かない)。
    "BDY-15": dict(ports={"door-passage-torso": ("W", 0.162)},
                   paths=[dict(kind="entry", pts=["door-passage-torso", (445, 130)]),
                          dict(kind="graph", pts=[(445, 130), (445, 545), (1390, 455)])],
                   sac=SAC15,
                   rooms=[("噴門", 330, 130, 115), ("胃底", 445, 244, 222), ("胃体", 740, 400, 232), ("幽門", 1390, 455, 65)],
                   expect=dict(rooms=4, corners=2, tjunc=0, deadends=1),
                   proposal=["仮案(kako-jun指摘で作り直し・分岐なしJ字の1袋): 入口(西)=噴門 → すぐ上のドーム=胃底 → 袋の本体=胃体(入口の約2倍幅) → 右へ曲がって細く=幽門(丸い閉じた行き止まり)。部屋名は注記のみ",
                             "分岐なし・T字0・曲がり2・行き止まり1。道幅 入口230px・胃体は最大460px・幽門は130px(キャラ1人分77px以上)。出口なし(接続はこの1本のみ)"]),
    "BDY-16": dict(ports={"door-passage-torso": ("N", 0.26)},
                   paths=[dict(kind="entry", pts=["door-passage-torso", (427, 190)]),
                          dict(kind="link", pts=[(427, 190), (427, 614)]),
                          dict(kind="link", pts=[(1217, 190), (1217, 614)]),
                          dict(kind="link", pts=[(427, 190), (1217, 190)]),
                          dict(kind="link", pts=[(427, 614), (1217, 614)])],
                   rooms=[("右心房", 427, 190, 160), ("右心室", 427, 614, 160), ("左心房", 1217, 190, 160), ("左心室", 1217, 614, 160)],
                   expect=dict(rooms=4, corners=3, tjunc=1, deadends=0),
                   proposal=["仮案: 心臓=2x2の丸い4部屋(画面左上=右心房・画面左下=右心室・画面右上=左心房・画面右下=左心室、本人から見る名前)を四角い環の通路でつなぐ。入口(北)=右心房",
                             "部屋名は注記のみ(絵には描かない)。環の中央は地形の島。出口なし(接続はこの1本のみ)"]),
    # BDY-17 肺: kako-jun 指示『肺は左右の中心に上から入るように、通路をキャラ１人分の幅で左から上にぐるっとまわしては』。
    # 入口=北辺の左右中心(x=画像中心)の1本・通路幅=主路幅/3(キャラ1人分)・丸い5部屋(右肺3葉=画面左の列、左肺2葉=右の列)。
    # 『左から上にぐるっと』の解釈が2通りなので仮案A(外周の環)と仮案B(渦巻き)の2案。既定=A。B は SPEC17_B（下）。
    "BDY-17": dict(ports={"door-passage-torso": ("N", 0.50)}, label="A",
                   paths=[dict(kind="entry", pts=["door-passage-torso", (822, 160)]),
                          dict(kind="link", pts=[(822, 160), (230, 160)]),
                          dict(kind="link", pts=[(230, 160), (230, 402)]),
                          dict(kind="link", pts=[(230, 402), (230, 644)]),
                          dict(kind="link", pts=[(230, 644), (1414, 644)]),
                          dict(kind="link", pts=[(1414, 644), (1414, 160)]),
                          dict(kind="link", pts=[(1414, 160), (822, 160)])],
                   rooms=[("右肺上葉", 230, 160, 110), ("右肺中葉", 230, 402, 110), ("右肺下葉", 230, 644, 110),
                          ("左肺上葉", 1414, 160, 135), ("左肺下葉", 1414, 644, 135)],
                   expect=dict(rooms=5, corners=4, tjunc=1, deadends=0),
                   proposal=["仮案A(外周を回る環): 入口(北辺中央)から下り、環の上辺中央へ。左へ分かれ、右肺3葉(上・中・下)を経て下→右→左肺2葉(下・上)と上へ、ぐるっと一周して上辺中央に戻る",
                             "通路幅は全通路でキャラ1人分=主路幅の1/3。5部屋は丸く大きい。環の中央は地形の島。行き止まりなし。入口の帯も1人幅(入口幅は要確認: 原文にない)。部屋名は注記のみ"]),
}

# ---- BDY-04 脳の迷路（kako-jun 指示 #142 2026-10-22『脳もキャラ１人分の幅でもっと複雑にして』）----
# 通路幅=主路幅/3(77px)。格子 13列x6行・ピッチ120px（隣り合う通路の壁=120-77=43px >= 通路幅の半分38.5px）。
# 生成規則: 入口セル（南辺中央の真上=列6・行5）から seed 固定の乱数で深さ優先の全域木（ループなし=正解の道が1つ）。
#   各セルは 1回だけ訪れ、未訪問の隣セルをランダムに選んで進む(行き止まりになったら戻る)。得られた木のうち
#   曲がり>=20・T字>=8・行き止まり>=10 を満たす seed の中で『入口から最も遠い行き止まりまでの道』が最長のものを
#   seed 0..MAZE_SEED_TRIES-1 から選ぶ（探索は決定的）。座標は全て模型の天面基準 px。
MAZE_COLS, MAZE_ROWS, MAZE_PITCH = 13, 6, 120
MAZE_X0, MAZE_Y0 = 102, 102          # 左上セル中心（縁から 102px = 通路の縁まで 63px の余白）
MAZE_SEED_TRIES = 600
MAZE_MIN = dict(corners=20, tjunc=8, deadends=10)


def _maze_tree(seed):
    import random
    rnd = random.Random(seed)
    root = (MAZE_COLS // 2, MAZE_ROWS - 1)       # 入口の真上のセル
    adj = {}
    seen = {root}
    stack = [root]
    while stack:
        c = stack[-1]
        nb = [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
              if 0 <= c[0] + dx < MAZE_COLS and 0 <= c[1] + dy < MAZE_ROWS and (c[0] + dx, c[1] + dy) not in seen]
        if not nb:
            stack.pop(); continue
        n = rnd.choice(nb)
        seen.add(n); adj.setdefault(c, set()).add(n); adj.setdefault(n, set()).add(c)
        stack.append(n)
    return root, adj


def _maze_stats(root, adj):
    """曲がり・T字・行き止まり(入口セルは入口の帯が付くので次数+1)・入口から最も遠い行き止まりまでのセル数。"""
    corners = tj = de = 0
    for c, n in adj.items():
        deg = len(n) + (1 if c == root else 0)
        if deg == 1:
            de += 1
        elif deg == 2:
            nn = list(n) + ([(c[0], c[1] + 1)] if c == root else [])
            (a_, b_) = nn
            if (a_[0] - c[0], a_[1] - c[1]) != (c[0] - b_[0], c[1] - b_[1]):
                corners += 1
        elif deg >= 3:
            tj += 1
    dist, q = {root: 0}, [root]
    for c in q:
        for n in adj[c]:
            if n not in dist:
                dist[n] = dist[c] + 1; q.append(n)
    return corners, tj, de, max(dist.values())


def maze_seed():
    best = None
    for sd in range(MAZE_SEED_TRIES):
        root, adj = _maze_tree(sd)
        co, tj, de, far = _maze_stats(root, adj)
        if co >= MAZE_MIN["corners"] and tj >= MAZE_MIN["tjunc"] and de >= MAZE_MIN["deadends"]:
            if best is None or far > best[0]:
                best = (far, sd)
    return best[1]


def make_maze_spec():
    sd = maze_seed()
    root, adj = _maze_tree(sd)
    cx = lambda c: MAZE_X0 + c[0] * MAZE_PITCH
    cy = lambda c: MAZE_Y0 + c[1] * MAZE_PITCH
    pt = lambda c: (cx(c), cy(c))
    # 直線の連なりを 1 本の path にまとめる: 次数!=2 または曲がりのセルで区切る
    def is_node(c):
        deg = len(adj[c]) + (1 if c == root else 0)
        if deg != 2:
            return True
        nn = list(adj[c]) + ([(c[0], c[1] + 1)] if c == root else [])
        a_, b_ = nn
        return (a_[0] - c[0], a_[1] - c[1]) != (c[0] - b_[0], c[1] - b_[1])
    paths = [dict(kind="entry", pts=["door-passage-torso", pt(root)])]
    done = set()
    for c in sorted(adj):
        if not is_node(c):
            continue
        for n in sorted(adj[c]):
            if (c, n) in done:
                continue
            prev, cur = c, n
            while not is_node(cur):
                nxt = [k for k in adj[cur] if k != prev][0]
                prev, cur = cur, nxt
            done.add((c, n)); done.add((cur, prev))
            paths.append(dict(kind="maze", pts=[pt(c), pt(cur)]))
    co, tj, de, far = _maze_stats(root, adj)
    return dict(ports={"door-passage-torso": ("S", 0.50)}, paths=paths, rooms=[],
                expect=dict(rooms=0, corners=co, tjunc=tj, deadends=de), seed=sd, root=root, tree=adj, far=far,
                proposal=[f"仮案: 脳=迷路（seed={sd}の全域木・13x6格子・通路幅=キャラ1人分77px）。入口(南)から北へ入り、蛇行する通路と行き止まりの枝。出口なし(接続はこの1本のみ)",
                          f"曲がり{co}・T字分岐{tj}・行き止まり{de}(丸い閉じた端)・ループなし(正解の道は1つ)。壁は通路幅の半分以上。形は決め打ちでなく seed 生成の1案"])


SPECS["BDY-04"] = make_maze_spec()

# 仮案B（渦巻き）: 入口(北辺中央)から下りて左へ出て、左側を下り、右へ、右側を上り、内へ折れて渦を巻く（外から内へ）。行き止まり=渦の中心。
# 平面上、入口が北辺中央の1本なので『左から上へ』は入口の線を横切る（交差する）ため、渦は反時計回り（左→下→右→上→左…）。
SPEC17_B = dict(ports={"door-passage-torso": ("N", 0.50)}, label="B",
                paths=[dict(kind="entry", pts=["door-passage-torso", (822, 160)]),
                       dict(kind="link", pts=[(822, 160), (230, 160)]),
                       dict(kind="link", pts=[(230, 160), (230, 402)]),
                       dict(kind="link", pts=[(230, 402), (230, 644)]),
                       dict(kind="link", pts=[(230, 644), (1414, 644)]),
                       dict(kind="link", pts=[(1414, 644), (1414, 300)]),
                       dict(kind="link", pts=[(1414, 300), (500, 300)]),
                       dict(kind="link", pts=[(500, 300), (500, 500)]),
                       dict(kind="link", pts=[(500, 500), (1000, 500)])],
                rooms=[("右肺上葉", 230, 160, 110), ("右肺中葉", 230, 402, 110), ("右肺下葉", 230, 644, 110),
                       ("左肺下葉", 1414, 644, 135), ("左肺上葉", 1414, 300, 135)],
                expect=dict(rooms=5, corners=7, tjunc=0, deadends=1),
                proposal=["仮案B(渦巻き・外から内へ): 入口(北辺中央)から下りて左へ出て、左側を右肺3葉(上・中・下)、下辺を右へ、右側を上り左肺2葉(下・上)、さらに内へ折れて渦の中心(行き止まり)へ",
                          "通路幅は全通路でキャラ1人分=主路幅の1/3。5部屋は丸く大きい。入口の帯も1人幅(入口幅は要確認: 原文にない)。部屋名は注記のみ。『左から上へ』は入口線との交差になるため反時計回り"])
SPEC17_A = SPECS["BDY-17"]


def use17(variant):
    """SPECS['BDY-17'] を仮案A/Bに切り替える（検査・描画が SPECS を読むため）。"""
    SPECS["BDY-17"] = SPEC17_B if variant == "B" else SPEC17_A


def sac_samples(m):
    """袋(SAC)の中心線を制御点から Catmull-Rom で滑らかに補間し (x,y,r) を約1px間隔で返す。半径も滑らかに補間し、区間の両端の値の範囲に収める（膨らみ過ぎ・くびれ過ぎを防ぐ）。"""
    P = SPECS[m]["sac"]
    ext = [(2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1], P[0][2])] + list(P) + [(2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1], P[-1][2])]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1])))
        lo, hi = min(p1[2], p2[2]), max(p1[2], p2[2])
        for k in range(n + (1 if i == len(ext) - 3 else 0)):
            t = k / n
            f = lambda a_, b_, c_, d_: 0.5 * ((2 * b_) + (-a_ + c_) * t + (2 * a_ - 5 * b_ + 4 * c_ - d_) * t * t + (-a_ + 3 * b_ - 3 * c_ + d_) * t ** 3)
            out.append((f(p0[0], p1[0], p2[0], p3[0]), f(p0[1], p1[1], p2[1], p3[1]), min(hi, max(lo, f(p0[2], p1[2], p2[2], p3[2])))))
    return out




def sac_mask(m, lw):
    """袋＋入口の帯の床マスク（模型の天面の大きさの 'L'、255=床）。"""
    PAD = 100
    im = Image.new("L", (MW + 2 * PAD, MH + 2 * PAD), 0); dd = ImageDraw.Draw(im)
    for x, y, r in sac_samples(m):
        dd.ellipse([PAD + x - r, PAD + y - r, PAD + x + r, PAD + y + r], fill=255)
    ent = [p_ for p_ in SPECS[m]["paths"] if p_["kind"] == "entry"][0]
    (ex, ey) = [e for e in ent["pts"] if not isinstance(e, str)][0]
    py = SPEC_PORTS[m]["door-passage-torso"]["slot"] * MH
    dd.rectangle([0, PAD + py - lw / 2, PAD + ex, PAD + py + lw / 2], fill=255)
    dd.ellipse([PAD + ex - lw / 2, PAD + ey - lw / 2, PAD + ex + lw / 2, PAD + ey + lw / 2], fill=255)
    out = im
    return out.crop((PAD, PAD, PAD + MW, PAD + MH))


def paint_sac(d, m, ox, oy, fill, lw=230):
    """袋＋入口の帯の床を塗る（d は呼び出し側の ImageDraw。マスクの 255 を fill で塗る）。"""
    mk = sac_mask(m, lw)
    d._image.paste(fill, (int(ox), int(oy)), mk)

OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
SIDE_JA = {"N": "北辺(上)", "S": "南辺(下)", "E": "東辺(右)", "W": "西辺(左)"}

# 根(BDY-02)から見て親になる側を固定する。map-topology.md の BDY-01 行は BDY-01 が from だが、
# BDY-02 の方位指定は BDY-02 側から書かれているので、BDY-02 を親として扱う。
PARENT_OVERRIDE = {("BDY-01", "BDY-02")}
# 出る辺の個別指定（body.svg 由来の導出より優先）。心臓は画面右（南東）・肺は画面左（南西）で、どちらも真の斜め45度前後だが、
# BDY-02 の南辺は 肺(左寄り)・下半身(中央)・心臓(右寄り) の3本と確定（docs/map-specifications.md・map-topology.md）。
# よって BDY-02 側の出口を両方とも南辺に固定する（東辺=左腕のみ・西辺=右腕のみ）。入口は BDY-16(心臓)=北辺・BDY-17(肺)=北辺中央。
SIDE_OVERRIDE = {("BDY-02", "door-passage-lung"): "S", ("BDY-02", "door-passage-heart"): "S"}  # (from, to) をこの行だけ逆向きに解釈


def parse_topology():
    text = (DOCS / "docs/map-topology.md").read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*(BDY-\d\d)\.(door-passage-[a-z-]+)\s*\|\s*(BDY-\d\d)\.(door-passage-[a-z-]+)\s*\|\s*door\s*\|",
        text, re.M)
    ev = re.findall(r"^\|\s*(TRM-03)\.(event-kiss)\s*\|\s*(BDY-01)\.(event-mouth)\s*\|\s*event\s*\|", text, re.M)
    return rows, ev


def parse_svg():
    svg = (DOCS / "docs/topology/body.svg").read_text(encoding="utf-8")
    nodes = {m[0]: (float(m[1]), float(m[2])) for m in
             re.findall(r'<circle class="node" data-map="(BDY-\d\d)" cx="(\d+)" cy="(\d+)"', svg)}
    edges = re.findall(r'data-kind="door" data-edge-id="[^"]*" data-from="(BDY-\d\d)" data-to="(BDY-\d\d)" '
                       r'data-from-port="([a-z-]+)" data-to-port="([a-z-]+)"', svg)
    return nodes, edges


def side_of(vec):
    dx, dy = vec
    if abs(dy) >= abs(dx):  # 真の45度は縦軸を採る
        return "N" if dy < 0 else "S"
    return "E" if dx > 0 else "W"


def build_model():
    rows, ev = parse_topology()
    nodes, svg_edges = parse_svg()
    portals = {}  # map -> {port: dict(side, other, other_port, role)}
    SPEC_PORTS.clear(); SPEC_PORTS.update(portals)
    for a, ap, b, bp in rows:
        if (a, b) in PARENT_OVERRIDE:
            a, ap, b, bp = b, bp, a, ap
        ax, ay = nodes[a]
        bx, by = nodes[b]
        s = SIDE_OVERRIDE.get((a, ap)) or side_of((bx - ax, by - ay))
        portals.setdefault(a, {})[ap] = dict(side=s, other=b, other_port=bp, sortkey=(bx if s in "NS" else by))
        portals.setdefault(b, {})[bp] = dict(side=OPP[s], other=a, other_port=ap,
                                             sortkey=(ax if OPP[s] in "NS" else ay))
    # 辺ごとのスロット位置
    for m, ports in portals.items():
        for s in "NESW":
            on = sorted([p for p in ports if ports[p]["side"] == s], key=lambda p: ports[p]["sortkey"])
            for i, p in enumerate(on):
                ports[p]["slot"] = (i + 1) / (len(on) + 1)
        if m == "BDY-02":
            for p, v in BDY02_SLOTS.items():
                ports[p]["slot"] = v
    spec_side_issues = []
    for m, sp in SPECS.items():
        for p, (sd, sl) in sp["ports"].items():
            if portals[m][p]["side"] != sd:
                spec_side_issues.append(f"{m}.{p}: 図の辺{sd} != 接続表+body.svg由来の辺{portals[m][p]['side']}")
            portals[m][p]["slot"] = sl
        if set(sp["ports"]) != set(portals[m]):
            spec_side_issues.append(f"{m}: 図のport集合が接続表と不一致")
    SPEC_PORTS.clear(); SPEC_PORTS.update(portals)
    build_model.spec_side_issues = spec_side_issues
    return rows, ev, nodes, svg_edges, portals


# ---- 構図（kako-jun 決定 #142 2026-10-22: 通路は『模型の縁』まで。土台の板と机が見えたまま）----
# 1920x1080 の外周から: 机(DESK_M) -> 土台の縁の帯(BAND = foamboard 28 + corrugated 断面 20) -> 模型の天面(床と地形)。
# 根拠: 寺町の採用画像 teramachi-common-exterior-reference.webp では土台の縁の帯が画像高さの約6.4%(60/940)、
#   左右・奥に机と部屋が見える。体内は真上寄りカメラ(SKILL 目標の見た目)で帯は厚みだけが見えるため帯を高さの4.4%(48px)、
#   机は通路の先に机が判別できる幅として帯の約2倍の 90px を上下左右同じに取る。比率は TBD(生成して見て詰める)。
BAND_FOAM, BAND_CORR = 28, 20
BAND = BAND_FOAM + BAND_CORR
DESK_M = 90
MARGIN = DESK_M + BAND  # 138
MX0, MY0, MX1, MY1 = MARGIN, MARGIN, W - MARGIN, H - MARGIN  # 模型の天面 (138,138)-(1782,942) = 1644x804
MW, MH = MX1 - MX0, MY1 - MY0
assert (MW, MH) == (MW0, MH0)
import math
RANGE_DEPTH = 60  # 遷移範囲: 辺に沿う帯の奥行(px)。キャラがここに立つと遷移する。位置は辺上の範囲指定
WALL_T = 22       # 広間の壁の厚み
FLOOR = (232, 201, 168)
CLEAN_TERRAIN = (170, 130, 110)
CLEAN_DESK = (118, 120, 126)
CLEAN_BAND = (150, 110, 62)
CLEAN_WALL = (92, 104, 128)


def edge_point(side, slot):
    return {"N": (MX0 + slot * MW, MY0), "S": (MX0 + slot * MW, MY1),
            "W": (MX0, MY0 + slot * MH), "E": (MX1, MY0 + slot * MH)}[side]


def inward(side, depth_px):
    return {"N": (0, depth_px), "S": (0, -depth_px), "W": (depth_px, 0), "E": (-depth_px, 0)}[side]


def corridors(m, ports):
    """各 port の経路（px 座標の折れ線）。先頭は模型の縁上の点。"""
    hx, hy = HUB.get(m, (0.5, 0.5))
    hub = (MX0 + hx * MW, MY0 + hy * MH)
    out = {}
    for p, d in ports.items():
        e = edge_point(d["side"], d["slot"])
        iw = inward(d["side"], 0.16 * (MH if d["side"] in "NS" else MW))
        out[p] = [e, (e[0] + iw[0], e[1] + iw[1]), hub]
    if m == "BDY-02":
        out = {p: pl for p, _k, pl, _i in bdy02_paths(ports) if p}
    return out


def bdy02_paths(ports):
    """BDY-02 の帯の折れ線。戻り値: [(port 名 or None, kind, 折れ線の点, 端が port か)]。先頭の port 名は首など port でない帯は None。
    首: 広間 -> J。頭: J -> 北辺。口: J -> K -> 北辺（K から辺へ垂直）。他の5本: 辺から垂直に entry px 入り -> 広間の角度 ang の点。"""
    (cx, cy), r = BDY02_HALL
    J = BDY02_J
    rows = []
    rows.append((None, "neck", [(cx, cy - 0.6 * r), J], [False, False]))
    hx = MX0 + ports["door-passage-head"]["slot"] * MW
    mx = MX0 + ports["door-passage-mouth"]["slot"] * MW
    rows.append(("door-passage-head", "branch", [J, (hx, MY0)], [False, True]))
    rows.append(("door-passage-mouth", "branch", [J, (mx, BDY02_K_Y), (mx, MY0)], [False, False, True]))
    for p, via in BDY02_ARMS.items():
        pts = [edge_point(ports[p]["side"], ports[p]["slot"])] + [tuple(v) for v in via]
        rows.append((p, "arm", pts, [True] + [False] * (len(pts) - 1)))
    return rows


def bdy02_ports(ports):
    return [p for p, _k, _pl, _i in bdy02_paths(ports)]


def paint_corridors(d, cor, lw, fill):
    for p, pts in cor.items():
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if abs(y1 - y0) < 1e-6:
                d.rectangle([min(x0, x1), y0 - lw / 2, max(x0, x1), y0 + lw / 2], fill=fill)
            elif abs(x1 - x0) < 1e-6:
                d.rectangle([x0 - lw / 2, min(y0, y1), x0 + lw / 2, max(y0, y1)], fill=fill)
            else:
                d.line([(x0, y0), (x1, y1)], fill=fill, width=lw)
        for x, y in pts[1:]:
            d.ellipse([x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2], fill=fill)


def resolve_paths(m, ports):
    """SPECS の折れ線を px 絶対座標に解決。戻り値: [(kind, [(x,y)...], [端が port か])]"""
    out = []
    for pa in SPECS[m]["paths"]:
        pts, isp = [], []
        for e in pa["pts"]:
            if isinstance(e, str):
                pts.append(edge_point(ports[m][e]["side"], ports[m][e]["slot"])); isp.append(True)
            else:
                pts.append((MX0 + e[0], MY0 + e[1])); isp.append(False)
        out.append((pa["kind"], pts, isp))
    return out


def graph_of(m):
    """仮案MAPの通路グラフ。戻り値: (頂点->隣接頂点集合, 線分リスト, port頂点集合)。座標は模型の天面基準 px（port は縁上の点）。"""
    adj, segs, portv = {}, [], set()
    for pid, pa in enumerate(SPECS[m]["paths"]):
        pts = []
        for e in pa["pts"]:
            if isinstance(e, str):
                pt = edge_point(SPEC_PORTS[m][e]["side"], SPEC_PORTS[m][e]["slot"])
                pt = (round(pt[0] - MX0, 3), round(pt[1] - MY0, 3)); portv.add(pt)
            else:
                pt = (float(e[0]), float(e[1]))
            pts.append(pt)
        for a_, b_ in zip(pts, pts[1:]):
            adj.setdefault(a_, set()).add(b_); adj.setdefault(b_, set()).add(a_); segs.append((a_, b_, pid))
    return adj, segs, portv


SPEC_PORTS = {}  # build_model 後に portals を入れる（graph_of が辺上の点を解くため）


def dead_ends(m):
    adj, segs, portv = graph_of(m)
    return [v for v, n in adj.items() if len(n) == 1 and v not in portv]


def bend_counts(m):
    """曲がり(次数2で向きが変わる頂点)・T字分岐(次数3以上)・行き止まり(次数1で port でない)の数。"""
    adj, _segs, portv = graph_of(m)
    corners = tjunc = 0
    for v, n in adj.items():
        if len(n) == 2:
            a_, b_ = sorted(n)
            u1 = (a_[0] - v[0], a_[1] - v[1]); u2 = (b_[0] - v[0], b_[1] - v[1])
            if abs(u1[0] * u2[1] - u1[1] * u2[0]) > 1e-6 * math.hypot(*u1) * math.hypot(*u2):
                corners += 1
        elif len(n) >= 3:
            tjunc += 1
    return corners, tjunc, len(dead_ends(m))


def seg_seg_dist(p1, p2, q1, q2):
    def pd(p, a_, b_):
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]; L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - a_[0]) * dx + (p[1] - a_[1]) * dy) / L))
        return math.hypot(p[0] - a_[0] - t * dx, p[1] - a_[1] - t * dy)
    return min(pd(p1, q1, q2), pd(p2, q1, q2), pd(q1, p1, p2), pd(q2, p1, p2))


SAC_MIN_PERSON = 77      # キャラ1人分の幅(主路幅の1/3)。袋の最小幅はこれ以上
SAC_MARGIN = 15          # 入口の帯が天面の縁から持つ余白(y=15)と同じ。袋は入口以外の縁からこれ以上離す


def sac_checks(m, tag, lw, portv, portals):
    """袋(SAC)MAPの検査: P3 道幅（入口lw・本体最大・先端・最小>=1人分）/ P4 天面に収まり入口以外の縁に床が出ない / P5 床が一連結（袋は分岐なしの1つ）。"""
    import numpy as np
    rep_ = []
    sm = sac_samples(m)
    rs = [r for _x, _y, r in sm]
    wmin, wmax, wend = 2 * min(rs), 2 * max(rs), 2 * sm[-1][2]
    ok3 = lw == 230 and wmax >= 1.8 * lw and wmax <= 2.1 * lw and 115 <= wend <= 150 and wmin >= SAC_MIN_PERSON and abs(wend - wmin) < 1e-6
    rep_.append((f"P3 {tag} 道幅: 入口{lw}px・袋の最大幅{wmax:.0f}px(入口の1.8〜2.1倍)・先端(幽門){wend:.0f}px(115〜150)・最小幅{wmin:.0f}px>=キャラ1人分{SAC_MIN_PERSON}px", ok3,
                 f"最小{wmin:.0f}・最大{wmax:.0f}・先端{wend:.0f}"))
    im = sac_mask(m, lw)
    py = SPEC_PORTS[m]["door-passage-torso"]["slot"] * MH
    a = np.array(im) > 0
    ys, xs = np.nonzero(a)
    inside_entry = (xs < SAC_MARGIN) & (ys >= py - lw / 2 - 1) & (ys <= py + lw / 2 + 1)
    bad = int(((xs < SAC_MARGIN) | (xs > MW - 1 - SAC_MARGIN) | (ys < SAC_MARGIN - 0) | (ys > MH - 1 - SAC_MARGIN)).__and__(~inside_entry).sum())
    # 上辺は入口の帯の上端(y=py-lw/2=15)と同じ余白なので < 15 を禁止
    rep_.append((f"P4 {tag} 袋が模型の天面に収まり、入口以外の縁に{SAC_MARGIN}px以上の余白（床の最小 x={xs.min()}, y={ys.min()}, 右端 {xs.max()}, 下端 {ys.max()}）", bad == 0, f"縁に出る床 {bad}画素"))
    # 一連結 + 分岐なし: 床の成分が1つ（袋は1つ・枝の通路なし）。細い枝が無いことは graph の T字0・行き止まり1(P1)で担保
    seen = np.zeros_like(a[::3, ::3]); aa = a[::3, ::3]
    st = [tuple(np.argwhere(aa)[0])]; seen[st[0]] = True
    while st:
        y_, x_ = st.pop()
        for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y_ + dy_, x_ + dx_
            if 0 <= yy < aa.shape[0] and 0 <= xx < aa.shape[1] and aa[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True; st.append((yy, xx))
    rep_.append((f"P5 {tag} 床が一連結（1つの袋・離れた島なし）", int(aa.sum()) == int(seen.sum()), f"床 {int(aa.sum())} / 連結 {int(seen.sum())}（3px間引き）"))
    return rep_


def proposal_checks(portals, lw0):
    """仮案4枚の幾何検査: 部屋数・曲がり数・行き止まり数・道幅・壁の間隔・縁からの余白・一連結。"""
    rep_ = []
    MIN_WALL = 20
    for m, var in (("BDY-04", None), ("BDY-15", None), ("BDY-16", None), ("BDY-17", "A"), ("BDY-17", "B")):
        if var:
            use17(var)
        tag = f"{m}{'案' + var if var else ''}"
        lw = mlw(m, lw0)
        sp = SPECS[m]; ex = sp["expect"]
        rooms = sp.get("rooms", [])
        adj, segs, portv = graph_of(m)
        corners, tj, de = bend_counts(m)
        rep_.append((f"P1 {tag} 部屋数{ex['rooms']}・曲がり{ex['corners']}・T字分岐{ex['tjunc']}・行き止まり{ex['deadends']}",
                     (len(rooms), corners, tj, de) == (ex["rooms"], ex["corners"], ex["tjunc"], ex["deadends"]),
                     f"実測 部屋{len(rooms)}・曲がり{corners}・T字{tj}・行き止まり{de}"))
        ent = [v for v in portv]
        rep_.append((f"P2 {tag} 入口は1本だけ（接続表のport数）", len(ent) == 1 == len(portals[m]), f"port頂点{len(ent)}"))
        if "sac" in sp:
            rep_ += sac_checks(m, tag, lw, portv, portals)
            continue
        small = [n for n, _, _, r in rooms if r * 2 <= lw]
        want_lw = round(lw0 / LW17_DIV) if m in ONE_PERSON_MAPS else lw0
        rep_.append((f"P3 {tag} 道幅{want_lw}px（{'キャラ1人分=主路幅1/3' if m in ONE_PERSON_MAPS else '3人並び=主路幅'}）で全通路に適用、部屋の直径は道幅より大きい", lw == want_lw and not small,
                     "部屋小:" + ",".join(small) if small else f"道幅{lw}px 全通路一定"))
        # 余白: 非 port の頂点まわりの床が模型の天面の内側に MIN_WALL 以上の余白で収まる
        bad = []
        for v in adj:
            if v in portv:
                continue
            r = max([rr for _, rx, ry, rr in rooms if (rx, ry) == v] + [lw / 2])
            if not (r + MIN_WALL <= v[0] <= MW - r - MIN_WALL and r + MIN_WALL <= v[1] <= MH - r - MIN_WALL):
                bad.append(f"{v}(r={r})")
        rep_.append((f"P4 {tag} 床が模型の天面に収まり、入口以外の縁に{MIN_WALL}px以上の余白を残す", not bad, "; ".join(bad) or "問題なし"))
        # 壁の間隔: 関連しない要素どうしの床の隙間 >= MIN_WALL
        gaps = []
        rel = lambda sg, v: v in sg
        for i, (a1, b1, _p1) in enumerate(segs):
            for (a2, b2, _p2) in segs[i + 1:]:
                if {a1, b1} & {a2, b2} or _p1 == _p2:
                    continue
                gaps.append(seg_seg_dist(a1, b1, a2, b2) - lw)
        for _, rx, ry, rr in rooms:
            for (a_, b_, pid_) in segs:
                # 同じ一本の通路(折れ線)の上にある部屋は、その通路の別の区間と重なってよい(部屋は通路の途中にある)
                # 同じ通路に乗る部屋と、その通路にT字でつながる通路の端(a_,b_のどちらか)は、部屋と一体の床
                own = {tuple(map(float, e)) for pa_ in SPECS[m]["paths"] if (rx, ry) in pa_["pts"] for e in pa_["pts"] if not isinstance(e, str)}
                if (rx, ry) in SPECS[m]["paths"][pid_]["pts"] or a_ in own or b_ in own:
                    continue
                gaps.append(seg_seg_dist((rx, ry), (rx, ry), a_, b_) - rr - lw / 2)
        for i, (_, x1, y1, r1) in enumerate(rooms):
            for (_, x2, y2, r2) in rooms[i + 1:]:
                linked = any({(x1, y1), (x2, y2)} == {a_, b_} for a_, b_, _ in segs)
                if not linked:
                    gaps.append(math.hypot(x1 - x2, y1 - y2) - r1 - r2)
        mg = min(gaps) if gaps else float("inf")
        rep_.append((f"P5 {tag} 関連しない通路・部屋どうしの壁(隙間)が{MIN_WALL}px以上", mg >= MIN_WALL, f"最小の隙間 {mg:.0f}px" if gaps else "対象なし"))
    use17("A")
    sp4 = SPECS["BDY-04"]
    co, tj, de = bend_counts("BDY-04")
    rep_.append((f"P7 BDY-04 迷路の複雑さ: 曲がり>={MAZE_MIN['corners']}・T字>={MAZE_MIN['tjunc']}・行き止まり>={MAZE_MIN['deadends']}（seed={sp4['seed']}、入口から最奥まで {sp4['far']}区間）",
                 co >= MAZE_MIN["corners"] and tj >= MAZE_MIN["tjunc"] and de >= MAZE_MIN["deadends"],
                 f"曲がり{co}・T字{tj}・行き止まり{de}・道は木構造(ループなし): 辺数{sum(len(v) for v in sp4['tree'].values()) // 2}=セル数{len(sp4['tree'])}-1"))
    # BDY-17 の個別検査: 入口が北辺の左右中心の1本（x=画像中心）
    for var in ("A", "B"):
        use17(var)
        pt = SPEC_PORTS["BDY-17"]["door-passage-torso"]
        cx = MX0 + pt["slot"] * MW
        rep_.append((f"P6 BDY-17案{var} 入口は北辺の左右中心(x=画像中心{W // 2})の1本", pt["side"] == "N" and abs(cx - W / 2) < 0.5 and len(SPEC_PORTS["BDY-17"]) == 1,
                     f"辺{pt['side']} x={cx:.1f}"))
    use17("A")
    return rep_


def paint_bands(d, paths, lw, fill, round_free_ends=True):
    """幅一定の斜めの帯。port 端は模型の外まで延長して縁で切る（呼び出し側が模型の外を戻す）。他端と折れ点は丸い。"""
    for kind, pts, isp in paths:
        pts = list(pts)
        if isp[0]:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]; n = math.hypot(dx, dy)
            pts[0] = (pts[0][0] - dx / n * 3 * lw, pts[0][1] - dy / n * 3 * lw)
        if isp[-1]:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]; n = math.hypot(dx, dy)
            pts[-1] = (pts[-1][0] + dx / n * 3 * lw, pts[-1][1] + dy / n * 3 * lw)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0; n = math.hypot(dx, dy)
            nx, ny = -dy / n * lw / 2, dx / n * lw / 2
            d.polygon([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], fill=fill)
        for i, (x, y) in enumerate(pts):
            if (i == 0 and isp[0]) or (i == len(pts) - 1 and isp[-1]):
                continue
            if not round_free_ends and i in (0, len(pts) - 1):
                continue
            d.ellipse([x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2], fill=fill)


def inward_dirs(m, ports):
    """port -> 内向き単位ベクトル。折れ線の port 端の区間の向き。"""
    res = {}
    for pa, (kind, pts, isp) in zip(SPECS[m]["paths"], resolve_paths(m, ports)):
        for i in (0, len(pts) - 1):
            if isp[i]:
                j = 1 if i == 0 else len(pts) - 2
                dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]; n = math.hypot(dx, dy)
                res[pa["pts"][i]] = (dx / n, dy / n)
    return res


def edge_half(side, dvec, lw):
    """帯が辺と交わる区間の半幅（辺に沿う方向）。辺に垂直なら lw/2、斜めなら lw/2/|sin|。"""
    comp = abs(dvec[1]) if side in "NS" else abs(dvec[0])  # 辺の法線方向成分
    return lw / 2 / comp


def hall_radius(m, cor, lw):
    """BDY-02 の広間（新版は横長の楕円。BDY02_HALL=(中心, 縦半径)、横半径=BDY02_HALL_RX）。以下は旧版（円）の説明: 中心=ハブ。広間の床円＋壁の縁取りが模型の天面に収まり、かつ最寄りの辺へ出る通路が
    『主路幅の半分』以上の長さで壁の外に残る最大の整数半径。ハブから模型の4辺までの距離で決まる（measure_hall_radius.py が同じ値を出す）。
    床円が通路で埋まって壁が見えなくなる半径（旧: 通路だけの図の内接円 198px）にならないよう、広間は通路より先に決める。"""
    return BDY02_HALL


NAMES = {"BDY-01": "口・体内入口", "BDY-02": "上半身", "BDY-03": "下半身", "BDY-04": "頭・脳の迷路通路",
         "BDY-05": "左手1", "BDY-06": "左手2・末端", "BDY-07": "右手1", "BDY-08": "右手2・末端",
         "BDY-09": "左足1", "BDY-10": "左足2", "BDY-11": "左足3・末端", "BDY-12": "右足1",
         "BDY-13": "右足2", "BDY-14": "右足3・末端", "BDY-15": "胃・J字の1袋", "BDY-16": "心臓・分岐室",
         "BDY-17": "肺・分岐室"}
DIAG_MIN_DEG = 15  # 斜め = 直線の傾きが水平・垂直から 15 度以上離れている


def render(m, rows, ev, nodes, ports, outdir, ratio, maze_tbd, clean=False, fname=None):
    lw = int(round(ratio * MW))  # 主路幅は『模型の天面の幅』に対する比
    lwb = lw  # 返す値は主路幅（MAPごとの通路幅は lw に上書き）
    lw = mlw(m, lw)
    img = Image.new("RGB", (W, H), CLEAN_DESK if clean else (70, 72, 78))
    d = ImageDraw.Draw(img, "RGBA")
    F = lambda s: ImageFont.truetype(FONT, s, index=0)
    is02 = m == "BDY-02"
    cor = corridors(m, ports[m]) if is02 else None
    paths = None if is02 else [p_ for p_ in resolve_paths(m, ports) if p_[0] != "graph"]  # graph=数え上げ専用の簡略中心線(描かない)
    dirs = None if is02 else inward_dirs(m, ports)
    if clean:
        d.rectangle([DESK_M, DESK_M, W - DESK_M - 1, H - DESK_M - 1], fill=CLEAN_BAND)
    else:
        d.rectangle([DESK_M, DESK_M, W - DESK_M - 1, H - DESK_M - 1], fill=(235, 232, 222))
        d.rectangle([DESK_M + BAND_FOAM, DESK_M + BAND_FOAM, W - DESK_M - BAND_FOAM - 1, H - DESK_M - BAND_FOAM - 1],
                    fill=(160, 120, 70))
    d.rectangle([MX0, MY0, MX1 - 1, MY1 - 1], fill=CLEAN_TERRAIN if clean else (38, 38, 46))
    snap = img.copy()  # 机・土台の縁・地形だけの状態（床の塗りが模型の外へはみ出すのを戻すため）
    hall = None
    if is02:
        c, r = hall_radius(m, cor, lw)
        hall = (c, r)
        rx = BDY02_HALL_RX
        d.ellipse([c[0] - rx - WALL_T, c[1] - r - WALL_T, c[0] + rx + WALL_T, c[1] + r + WALL_T],
                  fill=CLEAN_WALL if clean else (92, 104, 128))
        paint_bands(d, [(k, pl, ip) for _p, k, pl, ip in bdy02_paths(ports[m])], lw, FLOOR, round_free_ends=False)
        (cx, cy), r = hall
        d.ellipse([cx - BDY02_HALL_RX, cy - r, cx + BDY02_HALL_RX, cy + r], fill=FLOOR)
    else:
        paint_bands(d, paths, lw, FLOOR)
        if "sac" in SPECS[m]:
            paint_sac(d, m, MX0, MY0, FLOOR, lw)
        for _n, rx, ry, rr in ([] if "sac" in SPECS[m] else SPECS[m].get("rooms", [])):
            d.ellipse([MX0 + rx - rr, MY0 + ry - rr, MX0 + rx + rr, MY0 + ry + rr], fill=FLOOR)
    keep = Image.new("L", (W, H), 255)
    ImageDraw.Draw(keep).rectangle([MX0, MY0, MX1 - 1, MY1 - 1], fill=0)
    img.paste(snap, (0, 0), keep)  # 模型の外は塗り直し前に戻す
    d = ImageDraw.Draw(img, "RGBA")
    if clean:
        path = outdir / f"{fname or m}.png"
        img.save(path)
        return path, img, lwb, cor, hall
    prop = None if is02 else SPECS[m].get("proposal")
    # 遷移範囲: 模型の縁に沿う帯（辺上の範囲。斜めの帯は縁との交わり区間）
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    palette = [(220, 90, 90), (90, 160, 220), (110, 190, 110), (230, 170, 60), (170, 110, 210), (60, 190, 190), (210, 110, 160)]
    srt = sorted(ports[m].items(), key=lambda kv: kv[1]["slot"])
    for i, (p, dd) in enumerate(srt):
        col = palette[i % len(palette)]
        s, sl = dd["side"], dd["slot"]
        x, y = edge_point(s, sl)
        hw = lw / 2 if is02 else edge_half(s, dirs[p], lw)
        if s in "NS":
            box = [x - hw, MY0 if s == "N" else MY1 - RANGE_DEPTH, x + hw, MY0 + RANGE_DEPTH if s == "N" else MY1]
        else:
            box = [MX0 if s == "W" else MX1 - RANGE_DEPTH, y - hw, MX0 + RANGE_DEPTH if s == "W" else MX1, y + hw]
        od.rectangle(box, fill=col + (150,), outline=col + (255,), width=3)
    img.paste(over, (0, 0), over)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (p, dd) in enumerate(srt):
        col = palette[i % len(palette)]
        s, sl = dd["side"], dd["slot"]
        x, y = edge_point(s, sl)
        if is02:
            d.line(cor[p], fill=col + (255,), width=8, joint="curve")
        lab = f"{s}: {p}{'【仮案】' if is02 and p in ('door-passage-heart', 'door-passage-lung') else ''}\n→ {dd['other']} ({dd['other_port'].replace('door-passage-', '')}) の{OPP[s]}辺へ"
        hw = lw / 2 if is02 else edge_half(s, dirs[p], lw)
        if s == "N":
            tx, ty = x - hw + 6, MY0 + RANGE_DEPTH + 6
        elif s == "S":
            tx, ty = (x + hw + 14, MY1 - 58) if m == "BDY-04" else (x - hw + 6, MY1 - RANGE_DEPTH - 56)  # BDY-04 は迷路の下余白（右隣）に置いて通路に重ねない
        elif s == "W":
            tx, ty = MX0 + RANGE_DEPTH + 6, y - 30
        else:
            tx, ty = MX1 - RANGE_DEPTH - 400, y - 30
        lines = lab.split("\n")
        wbox = max(d.textlength(t, font=F(22)) for t in lines)
        d.rectangle([tx - 4, ty - 2, tx + wbox + 4, ty + 56], fill=(255, 255, 255, 170))
        d.multiline_text((tx, ty), lab, font=F(22), fill=(30, 30, 30), spacing=4)
    if not is02:
        # 中心線（斜めの傾きの確認用）と傾きの値
        for pi, (kind, pts, isp) in enumerate(paths):
            d.line(pts, fill=(255, 255, 255, 230), width=3, joint="curve")
            if kind in ("maze", "link", "entry"):
                continue
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                ang = math.degrees(math.atan2(abs(y1 - y0), abs(x1 - x0)))
                kd = {"limb": "斜め", "trunk": "胴の縦通路"}[kind]
                d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 14), f"{kd} 水平から{ang:.0f}度", font=F(24), fill=(20, 20, 20), anchor="mm",
                       stroke_width=3, stroke_fill=(255, 255, 255))
    if "sac" in SPECS.get(m, {}):  # 袋の中心線（白）
        d.line([(MX0 + x, MY0 + y) for x, y, _r in sac_samples(m)], fill=(255, 255, 255, 230), width=3, joint="curve")
    if prop:  # 仮案の注記: 部屋名と行き止まり（mock の注記。清書版には出さない）
        for rn, rx, ry, rr in SPECS[m].get("rooms", []):
            d.text((MX0 + rx, MY0 + ry + min(rr * 0.5, 75)), rn, font=F(40), fill=(30, 30, 30), anchor="mm", stroke_width=4, stroke_fill=(255, 255, 255))
        for (x, y) in dead_ends(m):
            if any((rx, ry) == (x, y) for _n, rx, ry, _r in SPECS[m].get("rooms", [])):
                continue  # 部屋の行き止まりは部屋名で足りる
            d.text((MX0 + x, MY0 + y), "行き止まり", font=F(20 if m == "BDY-04" else 26), fill=(30, 30, 30), anchor="mm", stroke_width=3, stroke_fill=(255, 255, 255))
    d.text((W / 2, DESK_M / 2), f"{m}  {NAMES[m]}" + (f"  【仮案{SPECS[m]['label']}】" if prop and SPECS[m].get("label") else "  【仮案】" if prop else ""), font=F(52), fill=(245, 245, 245), anchor="mm")
    d.text((W / 2, DESK_M + BAND_FOAM / 2), "土台の縁: foamboard", font=F(18), fill=(60, 60, 60), anchor="mm")
    d.text((W / 2, DESK_M + BAND_FOAM + BAND_CORR / 2), "corrugated 断面", font=F(15), fill=(40, 25, 10), anchor="mm")
    notes = [f"割付図(配置モック) 1920x1080。模型の天面{MW}x{MH}、主路幅={lwb}px(模型幅比{ratio}、3人並びの仮置き・数値TBD)" + (f"。この図の通路幅={lw}px(キャラ1人分=主路幅の1/3)" if lw != lwb else "") + "。着色帯=遷移範囲(辺上の範囲)",
             "手足は斜めに伸びる道（kako-jun確定）。辺は body.svg の方位から導いた提案。体の外形は描かない。通路は模型の縁まで。通路の無い辺には何も出さない"]
    if prop:
        notes = notes[:1] + prop
    if hall:
        notes[1] = ("南辺の心臓=右寄り(x≈1239–1469)・肺=左寄り(x≈450–680): 心臓は本人の左側=画面右。心臓=右寄り・肺=左寄りは確定（kako-jun 2026-10-22）。左右は身体の本人から見る(西辺=右腕・東辺=左腕)")
        notes.append(f"BDY-02: 広間(壁で縁取った横長の楕円の床。横半径{BDY02_HALL_RX}px・縦半径{hall[1]}px・壁厚{WALL_T}px、台座なし)から首が1本北へ伸び、上で頭(真北)と口(右上へ斜め)に分かれる")
    if m == "BDY-01":
        notes.append("event-mouth: TRM-03.event-kiss からの一方向イベント到着。到着位置・向きは原文に無い(TBD)。辺ではない")
        ex, ey = paths[0][1][-1]
        d.ellipse([ex - 30, ey - 30, ex + 30, ey + 30], outline=(150, 40, 80), width=5)
        d.text((ex, ey + 60), "event-mouth 到着点 TBD", font=F(22), fill=(235, 235, 235), anchor="mm",
               stroke_width=3, stroke_fill=(150, 40, 80))
    yb = H - DESK_M + 8
    d.rectangle([W / 2 - 800, yb - 4, W / 2 + 800, yb + len(notes) * 22 + 2], fill=(38, 38, 46, 235))
    for i, t in enumerate(notes):
        d.text((W / 2, yb + 8 + i * 22), t, font=F(16), fill=(235, 235, 235), anchor="mm")
    path = outdir / f"{fname or m}.png"
    img.save(path)
    return path, img, lwb, cor, hall


def expected_runs(m, ports, lw):
    """辺ごとの期待床区間 [(中心, 幅)] と検査の深さ。BDY-02 は従来どおり（縁から40px内側・帯中心=辺上の位置・幅lw）。
    他は縁から2px内側で、斜めの帯の縁との交わり（中心は傾きぶんずれ、幅=lw/|法線成分|）を解析的に求める。"""
    out = {s: [] for s in "NESW"}
    lw = mlw(m, lw)
    if m == "BDY-02":
        for d_ in ports[m].values():
            o = MX0 if d_["side"] in "NS" else MY0
            out[d_["side"]].append((o + d_["slot"] * (MW if d_["side"] in "NS" else MH), lw))
        return out, {"N": 2, "S": 40, "E": 40, "W": 40}  # 北辺は口の斜めの区間が辺の近くまで来るため縁から2px（他の辺は従来どおり40px）
    dirs = inward_dirs(m, ports)
    depth = 2
    for p, d_ in ports[m].items():
        s = d_["side"]
        x, y = edge_point(s, d_["slot"])
        ux, uy = dirs[p]
        if s in "NS":
            t = depth / abs(uy); out[s].append((x + ux * t, lw / abs(uy)))
        else:
            t = depth / abs(ux); out[s].append((y + uy * t, lw / abs(ux)))
    return out, depth


def pixel_check(m, geom_img, img, lw, ports, hall):
    """geom_img = 同じ幾何の清書版。縁の近くの走査で床の連続区間が仕様の帯（位置・幅）と一致すること、
    床が模型の外に一画素も無いこと、広間の円が床に収まることを検査する。"""
    import numpy as np
    px = geom_img.load()
    issues = []
    want_by, depth = expected_runs(m, ports, lw)
    lw = mlw(m, lw)
    dp = depth if isinstance(depth, dict) else {k: depth for k in "NESW"}
    probes = {"N": [(x, MY0 + dp["N"]) for x in range(W)], "S": [(x, MY1 - 1 - dp["S"]) for x in range(W)],
              "W": [(MX0 + dp["W"], y) for y in range(H)], "E": [(MX1 - 1 - dp["E"], y) for y in range(H)]}
    for s, pts in probes.items():
        runs, run = [], None
        for i, (x, y) in enumerate(pts):
            f = px[x, y] == FLOOR
            if f and run is None:
                run = i
            if not f and run is not None:
                runs.append((run, i - 1)); run = None
        if run is not None:
            runs.append((run, len(pts) - 1))
        want = sorted(want_by[s])
        if len(runs) != len(want):
            issues.append(f"{s}辺: 床区間{len(runs)}本 != 仕様{len(want)}本")
            continue
        for (a, b), (c, wd) in zip(runs, want):
            if abs((a + b) / 2 - c) > 4 or abs((b - a + 1) - wd) > 4:
                issues.append(f"{s}辺: 区間{a}-{b} が帯 中心{c:.0f} 幅{wd:.0f} と不一致")
    for name, im in (("清書", geom_img), ("出力", img)):
        q = np.array(im)
        mask = np.ones((H, W), bool); mask[MY0:MY1, MX0:MX1] = False
        bad = int((q[mask] == np.array(FLOOR)).all(axis=1).sum())
        if bad:
            issues.append(f"{name}: 模型の外（土台の縁・机・画像端）に床色が{bad}画素")
    for p, dd in ports[m].items():
        x, y = edge_point(dd["side"], dd["slot"])
        x, y = int(min(max(x, MX0), MX1 - 1)), int(min(max(y, MY0), MY1 - 1))
        if px[x, y] != FLOOR:
            issues.append(f"{dd['side']}辺: {p} が模型の縁に届いていない")
    if hall:
        (cx, cy), r = hall
        for ang in range(0, 360, 5):
            x = round(cx + BDY02_HALL_RX * math.cos(math.radians(ang))); y = round(cy + r * math.sin(math.radians(ang)))
            if px[x, y] != FLOOR:
                issues.append("広間の円周が床から外れている"); break
        if not (np.array(geom_img) == CLEAN_WALL).any():
            issues.append("広間の壁が見えない")
    if (m in SPECS) and SPECS[m].get("expect"):
        adj, _segs, portv = graph_of(m)
        for v in dead_ends(m):
            (nb,) = adj[v]
            ux, uy = v[0] - nb[0], v[1] - nb[1]; n_ = math.hypot(ux, uy); ux, uy = ux / n_, uy / n_
            rr = max([r for _n, rx, ry, r in SPECS[m]["rooms"] if (rx, ry) == v] or [lw / 2])  # 部屋が無ければ帯の半幅(袋の先端は幽門の半径)
            inner = (round(MX0 + v[0] + ux * (rr - 3)), round(MY0 + v[1] + uy * (rr - 3)))
            outer = (round(MX0 + v[0] + ux * (rr + 4)), round(MY0 + v[1] + uy * (rr + 4)))
            if px[inner] != FLOOR or px[outer] == FLOOR:
                issues.append(f"行き止まり{v}が丸い閉じた端になっていない")
        # 床は一連結（BFS、4px間引き）
        a_ = (np.array(geom_img) == np.array(FLOOR)).all(axis=2)[::4, ::4]
        ys, xs = np.nonzero(a_)
        seen = np.zeros_like(a_); stack = [(ys[0], xs[0])]; seen[ys[0], xs[0]] = True
        while stack:
            y_, x_ = stack.pop()
            for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y_ + dy_, x_ + dx_
                if 0 <= yy < a_.shape[0] and 0 <= xx < a_.shape[1] and a_[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True; stack.append((yy, xx))
        if int(a_.sum()) != int(seen.sum()):
            issues.append("床が一連結でない（離れた島がある）")
    if m == "BDY-04":
        issues += maze_metrics(geom_img, lw)[1]
    cols = {c for _, c in geom_img.getcolors(maxcolors=1 << 20)}
    okc = {FLOOR, CLEAN_TERRAIN, CLEAN_DESK, CLEAN_BAND} | ({CLEAN_WALL} if hall else set())
    if cols != okc:
        issues.append(f"清書の色が想定外: {sorted(cols)[:6]}")
    return issues


def maze_metrics(geom, lw):
    """BDY-04 の迷路の画素検査（清書版の画素から）。戻り値: dict と問題リスト。
    width: 全ての通路区間（隣り合うセル中心の中間）で、通路に垂直な床の連続区間の長さ（期待 lw）。
    wall: 模型の天面の中で、床と床に挟まれた地形の連続区間（行・列方向）の最小長 = 壁の最小厚（>= lw/2 を期待）。
    terrain/floor 成分数: 地形が1つ（床どうしが接触してループを作っていない・孤立した壁の島なし）、床が1つ（一連結）。
    longest: 入口の帯の端から最奥の行き止まりまでの中心線の長さ（px）。"""
    import numpy as np
    sp = SPECS["BDY-04"]
    a = np.array(geom)
    fl = (a == np.array(FLOOR)).all(axis=2)
    iss = []
    widths = []
    for c, ns in sp["tree"].items():
        for n in ns:
            if n < c:
                continue
            x = MX0 + (MAZE_X0 + (c[0] + n[0]) / 2 * MAZE_PITCH); y = MY0 + (MAZE_Y0 + (c[1] + n[1]) / 2 * MAZE_PITCH)
            x, y = int(round(x)), int(round(y))
            if c[0] == n[0]:  # 縦の通路 -> 水平方向の床の長さ
                l = r = x
                while fl[y, l - 1]: l -= 1
                while fl[y, r + 1]: r += 1
            else:
                l = r = y
                while fl[l - 1, x]: l -= 1
                while fl[r + 1, x]: r += 1
            widths.append(r - l + 1)
    if any(abs(w - lw) > 1 for w in widths):
        iss.append(f"通路幅が{lw}pxでない区間あり: {sorted(set(widths))}")
    m = fl[MY0:MY1, MX0:MX1]
    def min_gap(arr):
        best = 10 ** 9
        for row in arr:
            d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
            st = np.nonzero(d == 1)[0]; en = np.nonzero(d == -1)[0]  # 床の連続区間 [st, en)
            for e_, s_ in zip(en[:-1], st[1:]):
                best = min(best, int(s_ - e_))
        return best
    wall = min(min_gap(m), min_gap(m.T))
    if wall < lw / 2:
        iss.append(f"壁の最小厚{wall}px < 通路幅の半分{lw / 2:.1f}px")
    def comps(mask):
        mask = mask[::2, ::2]; seen = np.zeros_like(mask); n_ = 0
        for y, x in zip(*np.nonzero(mask)):
            if seen[y, x]: continue
            n_ += 1; st = [(y, x)]; seen[y, x] = True
            while st:
                yy, xx = st.pop()
                for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    y2, x2 = yy + dy_, xx + dx_
                    if 0 <= y2 < mask.shape[0] and 0 <= x2 < mask.shape[1] and mask[y2, x2] and not seen[y2, x2]:
                        seen[y2, x2] = True; st.append((y2, x2))
        return n_
    nt, nf = comps(~m), comps(m)
    if nt != 1: iss.append(f"地形（壁）の連結成分が{nt}個（通路どうしが接触してループ/島ができている）")
    if nf != 1: iss.append(f"床の連結成分が{nf}個")
    dist, q = {sp["root"]: 0}, [sp["root"]]
    for c in q:
        for n in sp["tree"][c]:
            if n not in dist:
                dist[n] = dist[c] + 1; q.append(n)
    longest = (MH - (MAZE_Y0 + (MAZE_ROWS - 1) * MAZE_PITCH)) + max(dist.values()) * MAZE_PITCH  # 入口の帯（縁→入口セル）+ セル間の道
    return dict(widths=len(widths), width_min=min(widths), width_max=max(widths), wall=wall, terrain=nt, floor=nf, longest=longest,
                far=max(dist.values())), iss


def bdy02_neck_checks(geom, lw):
    """BDY-02 の首の検査（清書版の画素から）。C11 首が1本: 分岐点 J より下〜広間の壁の上で、首の床の連続区間が x=960 を含む1本(幅=主路幅)だけ。
    C12 分岐: J は広間と北辺の間、北辺 MY0+2 の床区間は頭・口の2本、頭は真北・口は右上へ斜め(水平から15度以上)。C13 広間の壁が見える弧の数。"""
    import numpy as np
    a = np.array(geom)
    fl = (a == np.array(FLOOR)).all(axis=2)
    (cx, cy), ry = BDY02_HALL
    J = BDY02_J
    wall_top = cy - ry - WALL_T
    def runs(y, x0=0, x1=W):
        out, st = [], None
        for x in range(x0, x1):
            if fl[y, x] and st is None: st = x
            if (not fl[y, x]) and st is not None: out.append((st, x - 1)); st = None
        if st is not None: out.append((st, x1 - 1))
        return out
    rep_ = []
    y0, y1 = int(J[1] + 100), int(wall_top)
    bad, n_rows = [], 0
    for y in range(y0, y1):
        n_rows += 1
        rr = [r_ for r_ in runs(y) if r_[0] <= cx <= r_[1]]
        ok = len(rr) == 1 and abs((rr[0][1] - rr[0][0] + 1) - lw) <= 4
        if ok:
            others = [r_ for r_ in runs(y, MX0, MX1) if not (r_[0] <= cx <= r_[1]) and r_[1] > cx - lw / 2 - 30 and r_[0] < cx + lw / 2 + 30]
            ok = not others
        if not ok: bad.append(y)
    rep_.append((f"C11 BDY-02 首は1本: 分岐点より下(y={y0}..{y1 - 1}, {n_rows}行)で x={cx} を通る北向きの道が1本・幅{lw}px", n_rows >= 20 and not bad,
                 f"{n_rows}行すべて一致" if n_rows >= 20 and not bad else f"行数{n_rows}、不一致{len(bad)}行")) 
    rn = runs(MY0 + 2)
    mouth_x = MX0 + SPEC_PORTS["BDY-02"]["door-passage-mouth"]["slot"] * MW
    ang = math.degrees(math.atan2(J[1] - BDY02_K_Y, mouth_x - J[0]))
    ok12 = MY0 < J[1] - lw / 2 and J[1] < wall_top and len(rn) == 2 and DIAG_MIN_DEG <= ang <= 90 - DIAG_MIN_DEG
    rep_.append(("C12 BDY-02 分岐: 分岐点が広間の壁と北辺の間・北辺の床は頭と口の2本・頭=真北・口=右上へ斜め(水平から15度以上)", ok12,
                 f"J=y{J[1]}(壁の上端y{wall_top}、北辺y{MY0})、北辺の床{len(rn)}本{rn}、口の斜めは水平から{ang:.1f}度"))
    wm = (a == np.array(CLEAN_WALL)).all(axis=2)
    seen = np.zeros_like(wm); comps = 0
    for y, x in zip(*np.nonzero(wm)):
        if seen[y, x]: continue
        comps += 1; st = [(y, x)]; seen[y, x] = True
        while st:
            yy, xx = st.pop()
            for dy_, dx_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                y2, x2 = yy + dy_, xx + dx_
                if 0 <= y2 < H and 0 <= x2 < W and wm[y2, x2] and not seen[y2, x2]:
                    seen[y2, x2] = True; st.append((y2, x2))
    rep_.append(("C13 BDY-02 広間の壁（壁色）が見える弧の数（参考。帯が接する所以外に壁が残る）", comps >= 3, f"{comps}か所"))
    return rep_


def geometry_checks(portals, lw):
    """幾何の検査（画素ではなく仕様）: 斜め・丸い末端が模型内・隣接MAPの入口の向きと BDY-02 の7辺の整合。"""
    rep_ = []
    # 斜め
    angs, bad = [], []
    for m, sp in SPECS.items():
        for (kind, pts, isp) in resolve_paths(m, portals):
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                a = math.degrees(math.atan2(abs(y1 - y0), abs(x1 - x0)))
                if kind == "limb":
                    angs.append((m, round(a, 1)))
                    if not (DIAG_MIN_DEG <= a <= 90 - DIAG_MIN_DEG):
                        bad.append(f"{m}: {a:.1f}度")
    rep_.append((f"C8 手足・口・下半身の枝の道は斜め（水平・垂直から{DIAG_MIN_DEG}度以上）。区間{len(angs)}本",
                 not bad, ("最小/最大(水平からの度) %.1f/%.1f" % (min(a for _, a in angs), max(a for _, a in angs))) if not bad else "; ".join(bad)))
    # 太ももの折れ点は1つ（関節は膝の1つ）・区間は2本・膝で進行方向が30〜45度だけ変わる（内角135度以上の鈍角。kako-jun 指示 2026-10-22『もっとちょっと曲がった程度。鈍角にしろ』）・道は旧の直線以上
    kinfo, kbad = [], []
    for m in ("BDY-09", "BDY-12"):
        pts = resolve_paths(m, portals)[0][1]
        nb = bend_counts(m)[0]
        L = sum(math.hypot(b_[0] - a_[0], b_[1] - a_[1]) for a_, b_ in zip(pts, pts[1:]))
        st = math.hypot(0.392 * MW0, MH0 - 0.35 * MH0)  # 旧の直線（入口 西辺0.35 → 出口 南辺0.392）の長さ。位置を動かしても比較の基準は旧のまま
        turn = 0.0
        if len(pts) == 3:
            h1 = math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]); h2 = math.atan2(pts[2][1] - pts[1][1], pts[2][0] - pts[1][0])
            turn = abs(math.degrees((h2 - h1 + math.pi) % (2 * math.pi) - math.pi))
        same_side = len(pts) == 3 and (pts[1][0] - pts[0][0]) * (pts[2][0] - pts[1][0]) > 0 and (pts[1][1] - pts[0][1]) * (pts[2][1] - pts[1][1]) > 0
        kinfo.append(f"{m}: 折れ点{nb}・区間{len(pts) - 1}・折れ角（進行方向の変化）{turn:.1f}度・内角{180 - turn:.1f}度・中心線{L:.0f}px・旧直線{st:.0f}px（入口0.35→出口0.392）の{L / st:.2f}倍")
        if nb != 1 or len(pts) != 3 or not (30 <= turn <= 45) or 180 - turn < 135 or not same_side or L < st:
            kbad.append(kinfo[-1])
    rep_.append(("C14 太ももの折れ点=1（関節は膝の1つ・区間2本）・折れ角（進行方向の変化）30〜45度以内（内角135度以上の鈍角・2区間とも同じ側へ進む）・道の長さ >= 旧直線", not kbad, "; ".join(kbad or kinfo)))
    # 末端の丸い端と折れ点が模型内
    out = []
    for m in SPECS:
        for (kind, pts, isp) in resolve_paths(m, portals):
            for (x, y), ip in zip(pts, isp):
                if not ip and not (MX0 + mlw(m, lw) / 2 <= x <= MX1 - mlw(m, lw) / 2 and MY0 + mlw(m, lw) / 2 <= y <= MY1 - mlw(m, lw) / 2):
                    out.append(f"{m}:({x - MX0:.0f},{y - MY0:.0f})")
    rep_.append(("C9 丸い末端・合流点の円が模型の天面に収まる", not out, "; ".join(out) or "問題なし"))
    rep_ += proposal_checks(portals, lw)
    # 仕様の辺 == 接続表+body.svg の辺
    iss = build_model.spec_side_issues
    rep_.append(("C2b 各MAPの図の辺・port集合 == 接続表+body.svg 由来の辺", not iss, "; ".join(iss) or "BDY-02 以外の全port一致"))
    # BDY-02 の7辺と隣接MAPの入口: 隣の入る辺が BDY-02 の出る辺の反対、かつ向き（斜め方向）が矛盾しない
    sides02 = {p: d_["side"] for p, d_ in portals["BDY-02"].items()}
    conflicts = []
    for p, d_ in portals["BDY-02"].items():
        nb, nbp = d_["other"], d_["other_port"]
        if portals[nb][nbp]["side"] != OPP[d_["side"]]:
            conflicts.append(f"{p}->{nb}: BDY-02 {d_['side']} なのに隣が {portals[nb][nbp]['side']}")
    rep_.append(("C10 BDY-02 の7本の辺と隣接MAPの入口が矛盾しない（全て反対辺）", not conflicts,
                 "; ".join(conflicts) or "7/7 (" + ", ".join(f"{p.replace('door-passage-', '')}:{s}" for p, s in sides02.items()) + ")"))
    return rep_


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "verification/body-layout"))
    ap.add_argument("--clean", action="store_true", help="清書用: 文字・表題・注記・中心線・着色帯を除き、床=単色・地形=単色")
    ap.add_argument("--main-width-ratio", type=float, default=DEFAULT_MAIN_WIDTH_RATIO)
    ap.add_argument("--with-bdy02", action="store_true", help="BDY-02 も出力する（既定は採用済みのため書き換えない。検査は常に行う）")
    a = ap.parse_args()
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    rows, ev, nodes, svg_edges, portals = build_model()
    maze = {
        "BDY-04": "脳内迷路の形は原文に無い(TBD)。入口辺(南)だけ描いた。出口辺は原文に無く、接続はこの1本だけ",
        "BDY-15": "胃の内部形は原文に無い(TBD)。入口辺(西)だけが確定。内部は仮案(分岐なしJ字の1袋)",
        "BDY-16": "心臓・分岐室の内部形は原文に無い(TBD)。入口辺(北)だけ描いた",
        "BDY-17": "肺・分岐室の内部形は原文に無い(TBD)。入口辺(西)だけ描いた",
    }
    results = []
    report = []
    import tempfile

    t = {(r[0], r[1], r[2], r[3]) for r in rows}
    s = {(e[0], e[2], e[1], e[3]) for e in svg_edges}
    c1 = t == s and len(t) == 16
    report.append(("C1 map-topology.md の door 16行 == body.svg の door 16本", c1, f"{len(t)} vs {len(s)}"))
    lines = []
    c2 = True
    for ra, rap, rb, rbp in rows:
        da = portals[ra][rap]
        db = portals[rb][rbp]
        good = OPP[da["side"]] == db["side"]
        c2 &= good
        lines.append((f"{ra}.{rap}", da["side"], f"{rb}.{rbp}", db["side"], good, ra, rap, rb, rbp))
    report.append(("C2 全接続で両端の辺が反対", c2, f"{sum(1 for l in lines if l[4])}/{len(lines)}"))
    exp = {}
    for ra, rap, rb, rbp in rows:
        exp.setdefault(ra, set()).add(rap)
        exp.setdefault(rb, set()).add(rbp)
    c3 = all(set(portals[m]) == exp[m] for m in exp)
    report.append(("C3 各MAPの描画通路 == 接続表のport集合", c3, f"MAP数={len(exp)}"))
    c4 = sorted(portals) == [f"BDY-{i:02d}" for i in range(1, 18)]
    report.append(("C4 BDY-01..17 を全て生成", c4, f"{len(portals)}"))
    c5 = len(portals["BDY-02"]) == 7
    report.append(("C5 BDY-02 の通路は7本のみ", c5, str(len(portals["BDY-02"]))))
    c6 = True
    lw = int(round(a.main_width_ratio * MW))
    for m, ps in portals.items():
        want_by, _ = expected_runs(m, portals, lw)
        for sd in "NESW":
            sl = sorted(want_by[sd])
            for (c0, w0), (c1_, w1) in zip(sl, sl[1:]):
                if (c1_ - w1 / 2) - (c0 + w0 / 2) < 0:
                    c6 = False
                    report.append((f"  {m} {sd}辺で帯が重なる", False, f"{c0:.0f}+{w0 / 2:.0f} vs {c1_:.0f}-{w1 / 2:.0f}"))
    report.append(("C6 同一辺の通路帯（斜めは縁との交わり区間）が重ならない", c6, f"主路幅{lw}px"))
    report += geometry_checks(portals, lw)

    jobs = [(f"BDY-{i:02d}", None) for i in range(1, 18)] + [("BDY-17", "B")]  # BDY-17 は仮案A(既定)とB(BDY-17-B.png)
    for m, var in jobs:
        use17(var or "A")
        fname = "BDY-17-B" if var == "B" else None
        od = outdir
        path, img, lw, cor, hall = render(m, rows, ev, nodes, portals, od, a.main_width_ratio, maze, clean=a.clean, fname=fname)
        assert img.size == (W, H)
        if a.clean:
            geom = img
        else:
            with tempfile.TemporaryDirectory() as td:
                geom = render(m, rows, ev, nodes, portals, Path(td), a.main_width_ratio, maze, clean=True)[1]
        issues = pixel_check(m, geom, img, lw, portals, hall)
        results.append((fname or m, path, issues))
    use17("A")
    report += bdy02_neck_checks(render("BDY-02", rows, ev, nodes, portals, Path(tempfile.mkdtemp()), a.main_width_ratio, maze, clean=True)[1], lw)
    sp4 = SPECS["BDY-04"]
    with __import__("tempfile").TemporaryDirectory() as td4:
        g4 = render("BDY-04", rows, ev, nodes, portals, Path(td4), a.main_width_ratio, maze, clean=True)[1]
    mm, mi = maze_metrics(g4, mlw("BDY-04", lw))
    co4, tj4, de4 = bend_counts("BDY-04")
    report.append((f"P8 BDY-04 迷路の画素検査: 全{mm['widths']}区間の通路幅が{mlw('BDY-04', lw)}px一定・壁の最小厚>={mlw('BDY-04', lw) / 2:.1f}px・床も地形も一連結（通路どうしが接触せずループなし）", not mi,
                   f"通路幅 {mm['width_min']}〜{mm['width_max']}px、壁の最小厚 {mm['wall']}px、地形の成分{mm['terrain']}・床の成分{mm['floor']}、入口から最奥まで {mm['far']}区間・中心線の長さ {mm['longest']}px、曲がり{co4}・T字{tj4}・行き止まり{de4}、seed={sp4['seed']}" if not mi else "; ".join(mi)))
    c7 = all(not r[2] for r in results)
    report.append(("C7 描画画素: 模型の縁の床帯位置・幅が仕様と一致、他の辺に漏れ無し、模型の外(土台の縁・机・画像端)に床なし、縁に届く、広間は床に収まる", c7,
                   "; ".join(f"{r[0]}:{r[2]}" for r in results if r[2]) or "問題なし"))
    ok_all = all(r[1] for r in report if not r[0].startswith("  "))
    if a.clean:
        for n, ok, det in report:
            print(("OK " if ok else "NG ") + n, det)
        print("written (clean, consistency.md は更新しない):", outdir)
        return 0 if ok_all else 1

    md = ["# 体内 BDY-01..17 配置モック 整合表（自動生成）", "",
          f"画像 {W}x{H} / 模型の天面 {MW}x{MH}（余白: 机{DESK_M}px + 土台の縁の帯{BAND}px=foamboard{BAND_FOAM}+corrugated断面{BAND_CORR}）/ 主路幅 {lw}px（模型幅比 {a.main_width_ratio}、『キャラクター3人が横に並べる幅』の仮置き。数値はTBD）", "",
          f"**手足は斜めに伸びる道**（kako-jun 確定。原文: 胴体を真ん中として頭は上方向に、両手は右上、左上方向に、足は右下、左下方向に、一本道の通路としてかけばいい）。通路は模型の縁まで届く（画像端ではない）。遷移位置は辺上の範囲（図の着色帯、奥行{RANGE_DEPTH}px。斜めの帯は縁との交わり区間）。BDY-02 は広間（壁で縁取った横長の楕円の床）から首が1本北へ伸び、上で頭（真北）と口（右上へ斜め→北辺に垂直）に分かれる形（kako-jun 決定 #142『首は A案』。旧版は首が見えない床の塊だったため作り直し）。", "",
          "辺は body.svg の方位から導いた**提案**（原文に辺の指定は無い）。形は body_layout.py の SPECS。保留4枚（BDY-04/15/16/17）は入口の辺と位置が確定、内部は『仮案』（脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の4部屋の環・肺=5部屋。部屋名は注記のみ・絵には描かない）。", "",
          "**BDY-17（肺）は2案を併記**（kako-jun 指示 2026-10-22『肺は左右の中心に上から入るように、通路をキャラ１人分の幅で左から上にぐるっとまわしては』。解釈が2通り）: 仮案A=外周を回る環（既定。BDY-17.png）／仮案B=渦巻き（BDY-17-B.png）。入口は北辺の左右中心（x=画像中心）の1本、通路幅はキャラ1人分=主路幅の1/3（約77px）、右3葉・左2葉の丸い5部屋。入口の帯の幅（1人幅か3人幅か）は原文に無く**要確認**。BDY-02 側の肺の出口は東辺から南辺へ移した（東辺は左腕のみ・西辺は右腕のみ。南辺は肺・下半身・心臓の3本）。**左右は身体の本人から見る**（kako-jun 決定 #142 2026-10-22『本人は仰向け、それを正面から見ている。画面左側は右手』）: 西辺=右腕・東辺=左腕・左足=画面右下・右足=画面左下。**心臓・肺の左右は確定**: 心臓は本人の左側=画面右（南辺 x≈1239–1469）、肺=画面左（x≈450–680）。", "",
          "**BDY-15（胃）は kako-jun 指摘『なぜ胃が2つに分岐したようになってるのだ？人間はそうなのか？』で作り直し**: 旧図は胃底を横へ伸びる行き止まりの枝にして『噴門→胃底(枝)と胃体→幽門』と分岐させていた(区分の名前から枝を作った誤り)。新図は分岐なしJ字の1つの袋: 入口(西・噴門)のすぐ上の丸いドーム=胃底(袋の一部)→袋の本体=胃体(最大幅460px=入口230pxの2倍)→右へ曲がって細く(幽門130px)→丸く閉じた行き止まり。曲がり2・T字0・行き止まり1・入口1本。部屋名は注記のみ。形は SAC15(中心線の制御点＋半径の掃引)。", "",
          "## 機械検査", ""]
    for n, ok, det in report:
        md.append(f"- {'OK' if ok else 'NG'} {n} ({det})")
    md += ["", "## BDY-04 迷路の生成規則（kako-jun 指示 #142 2026-10-22『脳もキャラ１人分の幅でもっと複雑にして』）", "",
           f"- 通路幅 {mlw('BDY-04', lw)}px（=主路幅{lw}pxの1/3、BDY-17 の mlw と同じ扱い）。入口は南辺中央の1本のまま（BDY-02 の頭の出口から）、出口なし。",
           f"- 格子 {MAZE_COLS}列x{MAZE_ROWS}行・ピッチ{MAZE_PITCH}px（隣り合う通路の壁 = {MAZE_PITCH}-{mlw('BDY-04', lw)} = {MAZE_PITCH - mlw('BDY-04', lw)}px >= 通路幅の半分）、左上セル中心=模型の天面の({MAZE_X0},{MAZE_Y0})、縁から通路の縁まで {MAZE_X0 - mlw('BDY-04', lw) // 2}px の余白。",
           f"- 生成: 入口の真上のセル（列{MAZE_COLS // 2}・行{MAZE_ROWS - 1}）から Python `random.Random(seed)` で深さ優先の全域木（未訪問の隣セルを `rnd.choice`、袋小路で戻る）。全{MAZE_COLS * MAZE_ROWS}セルを1回ずつ通る木＝ループなし（正解の道は1つ）。",
           f"- seed 選択: seed 0..{MAZE_SEED_TRIES - 1} のうち 曲がり>={MAZE_MIN['corners']}・T字>={MAZE_MIN['tjunc']}・行き止まり>={MAZE_MIN['deadends']} を満たし、入口から最も遠い行き止まりまでの道が最長のもの = **seed {sp4['seed']}**（決定的）。",
           f"- 結果: 曲がり{co4}・T字{tj4}・行き止まり{de4}・入口から最奥まで{mm['far']}区間（中心線 {mm['longest']}px）・壁の最小厚 {mm['wall']}px・通路幅 {mm['width_min']}〜{mm['width_max']}px。行き止まりは丸い閉じた端、折れ点も丸い。",
           "", "## 段差検査（全17枚+17-B の clean 画素。body_step_scan.py）", "",
           step_report(outdir), "",
           "## 全接続の両端の辺（出る辺 / 入る辺）", "",
           "| 出る側 | 出る辺 | 入る側 | 入る辺 | 反対か |", "|---|---|---|---|---|"]
    for l in lines:
        md.append(f"| {l[0]} | {l[1]} | {l[2]} | {l[3]} | {'OK' if l[4] else 'NG'} |")
    md += ["", "## event（辺ではない）", "", "| TRM-03.event-kiss | BDY-01.event-mouth | 一方向。到着位置・向きは原文に無い(TBD)。BDY-01 の図には印だけ |", "",
           "## MAPごとの通路", "", "| MAP | 辺 | port | 相手 | 辺上の位置(提案、模型の辺に対する比) |", "|---|---|---|---|---|"]
    for mm in sorted(portals):
        for p, dd in sorted(portals[mm].items(), key=lambda kv: ("NESW".index(kv[1]["side"]), kv[1]["slot"])):
            md.append(f"| {mm} | {dd['side']} | {p} | {dd['other']}.{dd['other_port']} | {dd['slot']:.3f} |")
    (outdir / "consistency.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    write_connections(outdir, lines, portals, lw)
    for n, ok, det in report:
        print(("OK " if ok else "NG ") + n, det)
    print("written:", outdir)
    return 0 if ok_all else 1


def step_report(outdir):
    """clean 画像の段差検査の結果を文にする（opencv が無ければ未実行と書く）。"""
    try:
        import body_step_scan as bs
    except ImportError:
        return "未実行（`uv run --with opencv-python-headless --with numpy --with pillow python3 -I body_layout.py` で実行）"
    cd = Path(outdir) / "clean"
    if not cd.exists():
        return "未実行（clean 画像が無い）"
    res = {f.stem: bs.scan(f) for f in sorted(cd.glob("BDY-*.png"))}
    bad = {k: v for k, v in res.items() if v}
    if not bad:
        return f"{len(res)}枚すべて 段差 0 件（床の輪郭の短い水平/垂直の辺で前後が逆向きに約90度曲がる Z 形の食い違いなし。縁に触れる辺は除く）。"
    return "段差あり: " + "; ".join(f"{k}: " + ", ".join(f"({a},{b})-({c},{e}) {l}px" for a, b, c, e, l in v) for k, v in bad.items())


def write_connections(outdir, lines, portals, lw):
    """connections.md: 各接続の出る辺・入る辺・斜めの向き（図の帯の向き）。"""
    def band_dir(m, p):
        if m == "BDY-02":
            return {"door-passage-head": "広間から首が1本北へ→分岐点→真北（北辺に垂直）", "door-passage-mouth": "広間から首が1本北へ→分岐点→右上へ斜め→最後は北辺に垂直",
                    "door-passage-right-arm": "縁（西辺 y425–655）から水平に162px→折れ点から広間へ右下へ16.7度の斜め（段差なし）", "door-passage-left-arm": "縁（東辺 y≈363）から水平→左下へ斜めで広間へ（北東で口の分岐に近い）",
                    "door-passage-heart": "縁（南辺・右寄り）から垂直→左上へ斜めで広間へ", "door-passage-lung": "縁（南辺・左寄り）から垂直→右上へ斜めで広間へ",
                    "door-passage-lower": "縁から垂直（広間の下へ）"}[p]
        if m in ("BDY-09", "BDY-12"):  # 太ももは膝で鈍角に1回だけ曲がる（THIGH_KNEES）。左右ミラー
            side = "右" if m == "BDY-09" else "左"
            return {"door-passage-torso": f"縁（{'西' if m == 'BDY-09' else '東'}辺）から{side}下へ27度の斜め → 膝（折れ点は1つ・丸い・段差なし）で進行方向が35度だけ変わり（内角145度の鈍角）{side}下へ62度で南辺へ（中心線は旧の直線の約1.11倍）",
                    "door-passage-middle": f"縁（南辺）から{'左' if m == 'BDY-09' else '右'}上へ62度 → 膝 → 付け根側へ27度（上の逆順）"}[p]
        dirs = inward_dirs(m, portals)
        ux, uy = dirs[p]
        ang = math.degrees(math.atan2(abs(uy), abs(ux)))
        v = ("上" if uy < 0 else "下") if abs(uy) > 0.02 else ""
        h = ("右" if ux > 0 else "左") if abs(ux) > 0.02 else ""
        return f"縁から内側へ{h}{v}向き（水平から{ang:.0f}度）"
    md = ["# 体内 全接続の一覧（自動生成: body_layout.py）", "",
          "出る辺 = 親側の模型の縁、入る辺 = 子側の模型の縁（必ず反対）。向きは各MAP図の帯が縁から内側へ伸びる向き。", "",
          "| 接続 | 出る側の辺 | 入る側の辺 | 出る側の帯の向き | 入る側の帯の向き |", "|---|---|---|---|---|"]
    for l in lines:
        ra, rap, rb, rbp = l[5], l[6], l[7], l[8]
        md.append(f"| {ra}.{rap.replace('door-passage-', '')} → {rb}.{rbp.replace('door-passage-', '')} | {ra} の{SIDE_JA[l[1]]} | {rb} の{SIDE_JA[l[3]]} | {band_dir(ra, rap)} | {band_dir(rb, rbp)} |")
    md += ["", f"太もも（BDY-09・BDY-12）の入口・出口の辺上の位置は、鈍角の1折れ（進行方向の変化35度）を模型の天面に収めるため動かした（辺は不変・接続は辺の反対だけで成立）。BDY-09 入口（西辺）{THIGH_ENTRY_SLOT:.3f}（旧0.350）= 辺上 y={THIGH_ENTRY_SLOT * MH0:.0f}px: 相手 BDY-03 の出口（東辺 0.820, y={0.82 * MH0:.0f}px）との差 {abs(0.82 - THIGH_ENTRY_SLOT) * MH0:.0f}px（旧 {abs(0.82 - 0.35) * MH0:.0f}px）。BDY-09 出口（南辺）{THIGH_EXIT_SLOT:.3f}（旧0.392）= x={THIGH_EXIT_SLOT * MW0:.0f}px: 相手 BDY-10 の入口（北辺 0.392, x={0.392 * MW0:.0f}px）との差 {abs(THIGH_EXIT_SLOT - 0.392) * MW0:.0f}px。BDY-12 は左右ミラー（入口 東辺 {THIGH_ENTRY_SLOT:.3f}・出口 南辺 {1 - THIGH_EXIT_SLOT:.3f}、BDY-13 の入口 北辺 0.608 との差 {abs(1 - THIGH_EXIT_SLOT - 0.608) * MW0:.0f}px）。位置の画素一致は条件外（BDY-10・BDY-13 は変更しない）。"]
    md += ["", "手の通路（左右は身体の本人から見る。本人は仰向け、画面左=本人の右）: 左手=画面右上、右手=画面左上、左足=画面右下、右足=画面左下、口=右上（body.svg の方位）。BDY-02 は首が1本で、そこから頭（北）と口（北東）が分かれる。BDY-03 の胃=右（やや上）。保留4枚（BDY-04/15/16/17）は入口の辺と位置が確定、内部は『仮案』（脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の4部屋の環・肺=5部屋で2案: 仮案A=外周の環、仮案B=渦巻き。入口の帯は辺に垂直。BDY-17 の通路はキャラ1人分=主路幅の1/3）。BDY-02 の南辺は左寄りが肺・右寄りが心臓（心臓は本人の左 = 画面右。確定）。肺は BDY-17 の北辺中央へ、心臓は BDY-16 の北辺へ入る。"]
    (outdir / "connections.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
