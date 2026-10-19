# 素材ID配置（#68、2026-10-18）

本制作の画像正本は `assets/images/`。配置変更は採用判定ではない。

## 保存運用（#68決定、2026-10-19）

- **サンプル・候補の置き場を作らない**。`candidates/`、版suffix、`verification/` 配下の検証画像置き場は作らない。生成画像は、ゲームで使う正本パス（上表のID別パス）へ**直接上書き保存**する。
- 使うならコミットするだけ、使わないなら git でリバート（`git restore <path>`、未追跡の新規ファイルは削除）。**使う可能性のあるテイクは、次を生成する前にコミットする**（未コミットの新規ファイルは上書きで消える）。`git add` は名指し。
- **採用状態は置き場でなく台帳のstatusで管理する**（[map-asset-registry](../map-asset-registry.md)・各台帳）。正本パスにファイルがあることは、採用も審査通過も意味しない。
- **加工前原本（`raw/`）は保管しない**。人物・敵・召喚獣とも、切り出し・縮小・トリム前の元絵は残さず、来歴（prompt・測定値・判定）をIssueかレビュー文書に記録する。過去分の復元は git 履歴から（`git show 1bb09d0:<path>`、記録は `20261018-asset-migration.json` の `pruned_path`）。
- **不採用・失敗画像は残さない**。追跡済みなら `git restore <path>`、未追跡の新規ファイルなら即削除。`candidates/`・`legacy/`・版suffix・サンプル置き場は新運用では作らず、残さない前提とする。
- 参照用に残す画像（`fields/reference/`、外観参照専用。#105で許可済み）は、**長辺の上限を下げた縮小版**で保存し、役割が分かる名前（kebab-case、例 `teramachi-roof-exterior.png`）にリネームする。上限px・形式（例: 長辺1024px PNG／長辺768px WebP）は**未決（要確認）**。決まるまで参照画像を新規保存しない。原寸の元画像は参照として残さない。
- `raw/`・`verification/`（検証JSON・VFIELD・prototype/legacy-masks）・BG002〜004・BG006〜009（candidates/ ごと）・DIAG は #68 の追従PRで削除済み。復元は git 履歴から。

寺町16枚の全再作成と全件通過後の一括切替（#51）は継続する。

全712ファイルの旧→新／削除、SHA-256、理由は [移行manifest](20261018-asset-migration.json)。全行の復元元はmanifestの `base_commit` で、`git show <base_commit>:<old>` が元データを返す。元promptは既存の記録以外から復元・創作しない。過去レビューのパスは当時の記録として残す。

| 種別 | 正本配置 | 状態・対応 |
|---|---|---|
| 敵 | `assets/images/enemies/Mxxx.png` | monsters.mdの既存ID。M001も同じroot。既存の採用／採否待ちを継承し、新品質規約を満たすとは判定しない |
| 召喚獣 | `assets/images/summons/Sxxx.png` | S002〜S007の6種のみ現存。S001は未生成、S008は同じ存在の設計だが現存画像なし。架空のファイルを作らない |
| 人物 | `assets/images/characters/Cxxx/{masters,poses,walk}/Cxxx-<suffix>.png` | 下表のC管理ID。旧人名prefixをIDへ置換し、年齢・衣装・pose・方向・コマを全て保持 |
| MAP（旧素材・現存のみ） | `assets/images/fields/legacy/Exx[-variant].png` | 33MAP＋12旧差分。新規生成先ではない。寺町再作成候補の代わりに採用するものではない |
| legacy mask | `assets/images/fields/legacy/masks/Exx-*.png` | 旧接続を変更しない検証専用。JSON・生成補助（make_masks.py）は削除済み |
| 外観参照 | `assets/images/fields/reference/<kebab-case>.png` | 外観参照専用（平置き・小文字英数とハイフンのみ）。mapの「実行時参照」には使わない |
| 戦闘背景 | `assets/images/battle-backgrounds/BGxxx.png`（現存はBG001・BG005のみ。BG002〜004・006〜009は削除済みで、復元は git 履歴 `1bb09d0` から。戦闘背景の新規作成は別件） | 下表 |
| ブランド | `assets/images/brand/BRAND001.{png,svg}`、`BRAND002.{png,svg}` | 旧mouth-a／mouth-b。ゲームIDではない |

| C ID | 元人名prefix | 登場人物 |
|---|---|---|
| C001 | otton | オトン |
| C002 | nam | ナム |
| C003 | shah | シャー |
| C004 | peiko | ペー子 |

| BG ID | 元ファイル | 状態 |
|---|---|---|
| BG001 | bg-a.png | カメラ参照。旧状態を維持 |
| BG005 | stage-b.png | 既存採用舞台 |

M001の旧640px透過画像は移動で品質再承認しない。今後の再生成は敵スキルの45°・4グリッド契約を使い、既存画像をそのまま新規約passと扱わない。

削除した147ファイルは再作成必須の背景44、対応するrebuild専用mask/config82、pre-sync重複10、失敗または更新中の未審査戦闘候補11。未審査候補の削除理由を画素不合格と捏造しない。削除でワークツリーから約203.3MiBを除去するが、Git履歴には復元可能な原本が残る。

検証は `uv run python3 scripts/verify_asset_layout.py` と `ruby scripts/verify_map_ledger.rb`。画像byte hash、全移動先一意性、ID形式、旧path消失を確認する。実HTTPの画像読込は `uv run python3 -m unittest discover -s tests -v` で確認する。配信rootはリポジトリrootのまま。
