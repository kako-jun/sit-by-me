#!/usr/bin/env python3
"""隣り合う屋外MAPのつなぎ目で、道の縁の境界の種類が両側で一致するかを検査する（決定 SIT.road-edge-solid-boundary、Issue #191）。

台帳 接続 の edge 接続（期待=opposite）ごとに、両MAPの plan から辺に接する道の両脇（北/南 または 西/東）の境界の種類を取り、
共通の種類が1つも無ければ食い違い。種類は look に出てくる既存の語（oblique_build.EDGE_KIND_GROUPS）。
片側に境界が無い・種類が読めない箇所は『比較できない』として表示だけする。
既知の未決（直し方を台帳から決められず、kako-jun の判断待ち）は KNOWN_UNDECIDED に理由つきで持つ。それ以外の食い違いは FAIL。
  uv run --with numpy --with scipy --with opencv-python-headless --with pillow python3 scripts/verify_seam_boundaries.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".claude", "skills", "sit-field-background", "tools"))
import oblique_build as B  # noqa: E402

# (MAP_A, 辺A, 側, MAP_B, 辺B): 理由
KNOWN_UNDECIDED = {}  # 現在は未決なし（用水の連続は決定 TRM.canal-continuity で解消）


def main():
    mism, unknown = B.seam_mismatches()
    bad = []
    for ma, sa, side, ka, mb, sb, kb in mism:
        why = KNOWN_UNDECIDED.get((ma, sa, side, mb, sb))
        line = f"{ma}.{sa}（{side}）{'・'.join(ka)} と {mb}.{sb} {'・'.join(kb)} が食い違う"
        if why:
            print(f"UNDECIDED: {line}。{why}")
        else:
            bad.append(line)
            print(f"FAIL: {line}")
    for ma, sa, side, ka, mb, sb, kb in unknown:
        print(f"INFO: 比較できない: {ma}.{sa}（{side}）{'・'.join(ka) or '境界なし'} / {mb}.{sb} {'・'.join(kb) or '境界なし'}")
    if bad:
        sys.exit(1)
    print(f"PASS: つなぎ目の境界の種類に未決以外の食い違いなし（未決 {sum(1 for m in mism if (m[0], m[1], m[2], m[4], m[5]) in KNOWN_UNDECIDED)} 件・比較できない {len(unknown)} 件）")


if __name__ == "__main__":
    main()
