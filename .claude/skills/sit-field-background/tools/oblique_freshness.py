"""プロンプト段の入力 hash（oblique_build の prompt 段と起動判定 oblique_e2_schedule が共有する唯一の導出）。

画像ライブラリ（cv2 など）に依存しない。起動判定が『マニフェストのプロンプトが今の plan・台帳・ツールで作ったものか』を
oblique_build を import せずに確かめるために切り出した（#191）。
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ledger_query as LQ  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PROMPT_VERSION = "oblique-edit-prompt/5"
DECOR_FILE = os.path.join(REPO, "docs", "production", "oblique-mocks", "decor-pools.json")


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def src_sha(*names):
    return sha_bytes(b"".join(open(os.path.join(HERE, n), "rb").read() for n in names))


def plan_sha_of(plan_path, variant=None):
    return sha_file(plan_path) + (f"+{variant}" if variant else "")


def prompt_input_sha(plan_sha, ledger_text, ledger_mat):
    """prompt 段の input_sha。plan_sha は plan_sha_of の値、ledger_text/ledger_mat は LQ.sections(key, depends_on) の結果。"""
    decor = sha_file(DECOR_FILE) if os.path.exists(DECOR_FILE) else ""
    return sha_bytes((plan_sha + PROMPT_VERSION + src_sha("oblique_mock.py") + decor + ledger_text + json.dumps(ledger_mat, sort_keys=True)).encode())


def current_prompt_sha(map_id, depends_on, plan_path, variant=None):
    text, mat = LQ.sections(map_id, depends_on)
    return prompt_input_sha(plan_sha_of(plan_path, variant), text, mat)
