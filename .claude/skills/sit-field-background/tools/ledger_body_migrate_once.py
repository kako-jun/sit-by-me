"""body_layout.py の既存入力値だけを体内幾何.yamlへ一度だけ移す。

描画を実行せず、PILを読み込まない。BDY-04 の迷路の木は seed から
決定論で導く派生物なので、seed・格子条件だけを入力として記録する。
"""
import importlib.util
import sys
import types

import ledger_flat as F
import ledger_io as L


def normal(value):
    if isinstance(value, tuple):
        return [normal(x) for x in value]
    if isinstance(value, list):
        return [normal(x) for x in value]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise ValueError("幾何入力に文字列以外の辞書キーがある。派生迷路を混ぜていないか")
        return {k: normal(v) for k, v in value.items()}
    return value


def main():
    if L.read("体内幾何"):
        raise SystemExit("体内幾何.yamlは既にある。再実行禁止")
    dummy = types.ModuleType("PIL")
    dummy.Image = dummy.ImageDraw = dummy.ImageFont = types.SimpleNamespace()
    sys.modules["PIL"] = dummy
    source = L.HERE + "/body_layout.py"
    spec = importlib.util.spec_from_file_location("body_layout_migration", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    constants = ("DEFAULT_MAIN_WIDTH_RATIO", "LW17_DIV", "BDY02_SLOTS", "HUB",
                 "BDY02_HALL", "BDY02_HALL_RX", "BDY02_J", "BDY02_K_Y", "BDY02_ARMS",
                 "THIGH_ENTRY_SLOT", "THIGH_EXIT_SLOT", "THIGH_KNEES", "SAC15",
                 "MAZE_COLS", "MAZE_ROWS", "MAZE_PITCH", "MAZE_X0", "MAZE_Y0",
                 "MAZE_SEED_TRIES", "MAZE_MIN", "MW0", "MH0")
    rows = []

    def add(mid, variant, obj, certainty):
        for path, value, typ in F.flatten(normal(obj)):
            rows.append({"幾何ID": f"BODY-{len(rows)+1:04d}", "MAP_ID": mid, "変種": variant,
                         "経路": path, "型": typ, "値": value, "確度": certainty,
                         "根拠": ".claude/skills/sit-field-background/tools/body_layout.py（移行前の入力）",
                         L.FREE: ""})

    add("GLOBAL", "基準", {k: getattr(module, k) for k in constants}, "既存モック入力")
    for mid, data in module.SPECS.items():
        if mid == "BDY-04":
            # 迷路の tree と paths は seed/格子から生まれる派生物。コードの
            # make_maze_spec が同じ値を再構成し、比較ゲートで確認する。
            add(mid, "基準", {"seed": data["seed"]}, "仮案")
        else:
            add(mid, "A" if mid == "BDY-17" else "基準", data,
                "仮案" if mid in ("BDY-15", "BDY-16", "BDY-17") else "既存モック入力")
    add("BDY-17", "B", module.SPEC17_B, "仮案")
    L.write("体内幾何", rows)
    print(f"体内幾何 {len(rows)}行、対象MAP {len(module.SPECS)}、BDY-17 A/Bを保持")


if __name__ == "__main__":
    main()
