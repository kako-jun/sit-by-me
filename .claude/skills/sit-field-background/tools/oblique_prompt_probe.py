"""台帳から導出される imagegen 編集プロンプトを、ファイルに書かずに全MAP分 JSON で標準出力する（画像生成 API は呼ばない）。

verify_prompt_reflects_ledger.rb が呼ぶ。oblique_build.build_one のプロンプト段と同じ導出
（必須キー欠落ならゲート停止 → gated に欠落一覧、そうでなければ LQ.sections + build_prompt）。
  uv run --with numpy --with opencv-python-headless --with pillow python3 oblique_prompt_probe.py [PLANS_DIR]
PLANS_DIR 既定: <LEDGER_ROOT or repo>/docs/production/oblique-mocks（*-plan.json とその variants を全部対象にする）
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_io as LIO  # noqa: E402
import ledger_query as LQ  # noqa: E402
import oblique_build as B  # noqa: E402
import oblique_mock as M  # noqa: E402


def main():
    plans_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(LIO.REPO, "docs", "production", "oblique-mocks")
    out = []
    for pp in sorted(glob.glob(os.path.join(plans_dir, "*-plan.json"))):
        with open(pp, encoding="utf-8") as f:
            variants = list(json.load(f).get("variants", {}))
        for v in [None] + variants:
            p = M.load_plan(pp, v)
            key = p["map_id"]
            rec = {"map_id": key, "plan": os.path.relpath(pp, LIO.REPO), "gated": [], "prompt": ""}
            miss = LQ.missing_keys(key)
            if miss:
                rec["gated"] = miss
            else:
                ledger_text, _ = LQ.sections(key, p.get("depends_on", []))
                rec["prompt"] = B.build_prompt(p, key, ledger_text)
            out.append(rec)
    json.dump(out, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
