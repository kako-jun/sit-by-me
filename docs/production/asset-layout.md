# 素材ID配置（#68、2026-10-18）

本制作の画像正本は `assets/images/`。配置変更は採用判定ではない。

## 保存運用（#68決定、2026-10-19）

- **サンプル・候補の置き場を作らない**。`candidates/`、版suffix、`verification/` 配下の検証画像置き場は作らない。生成画像は、ゲームで使う正本パス（上表のID別パス）へ**直接上書き保存**する。
- 使うならコミットするだけ、使わないなら git でリバート（`git restore <path>`、未追跡の新規ファイルは削除）。**使う可能性のあるテイクは、次を生成する前にコミットする**（未コミットの新規ファイルは上書きで消える）。`git add` は名指し。
- **採用状態は置き場でなく台帳のstatusで管理する**（[map-asset-registry](../map-asset-registry.md)・各台帳）。正本パスにファイルがあることは、採用も審査通過も意味しない。
- **加工前原本（`raw/`）は保管しない**。人物・敵・召喚獣とも、切り出し・縮小・トリム前の元絵は残さず、来歴（prompt・測定値・判定）をIssueかレビュー文書に記録する。過去分の復元は git 履歴から（`git show 1bb09d0:<path>`、記録は `20261018-asset-migration.json` の `pruned_path`）。
- **不採用・失敗画像は残さない**。追跡済みなら `git restore <path>`、未追跡の新規ファイルなら即削除。`candidates/`・`legacy/`・版suffix・サンプル置き場は新運用では作らず、残さない前提とする。
- 参照用に残す画像（`fields/reference/`、外観参照専用。#105で許可済み）は、役割が分かる名前（kebab-case）で保存する。形式は **非可逆WebP（品質85）** を許可する（`magick <元PNG> -quality 85 <名>.webp`。実寸は縮小しない）。人物・敵・召喚獣・戦闘背景も同じ非可逆WebP（品質85、アルファ保持、実寸不変）が正本（#68 PR-W）。MAP（fields/legacy・masks）はMAP改名PR（PR-M）でWebP化するまでPNG、brandはPNGのまま。原寸の元画像は参照として残さない。
- 保存済み: `assets/images/fields/reference/teramachi-common-exterior-reference.webp`（非可逆WebP品質85、1672×940、430,536 bytes、sha256 `c596781d351fce35d71b1b31c8db8964e39b2623fde558b44f92cd4723da3175`。元PNG sha256 `7082a759e364a4731d18ba20908034a1f89317c4e6599cd96bee1d6703e77663`）。用途は**順序・包含関係の確認のみ**。池・墓地・鐘楼・井戸・像・遊具・築地塀・通用門などの位置・寸法・扉位置・廊下の形は確定させない。独立画像レビュー合格済み（[#51コメント](https://github.com/kako-jun/sit-by-me/issues/51)参照）。
- 保存済み（派生参照・#51 2026-10-21）: `assets/images/fields/reference/teramachi-exterior-building-band-crop.webp`（上の共通外観参照の左上原点から 1672×280 を非リサイズでクロップした可逆WebP、483,246 bytes、sha256 `c92c51cebcdc8e2299bd05a61732eaf4b2385c059a5ce8089ec240ecebbabc2d`。元は無変更）。建物帯（屋根と南面）だけで池・園庭・遊具・灯籠・墓地・鐘楼を含まず、TRM-03 生成時に全体図の代わりに渡す。用途は3棟の順序・包含関係のみ。
- 保存済み（採用外観・#51 2026-10-21）: `assets/images/fields/reference/teramachi-temple-grounds-exterior-standing.webp`（TRM-03の立位期。非可逆WebP品質85、実寸1672×941・リサイズなし、392,390 bytes、sha256 `1f4a3bb602d7981ece1fc50ac7fd5cba9ba724187cd40af2745b40e8b08526cc`（v7。v5 から差し替え。v5 の WebP は 391,674 bytes）。PNG原本は残さない）。室内3MAPの唯一の参照。mask・links・red-team未通過のためruntime未切替。来歴は [採用記録](20261021-trm03-standing-exterior-adoption.md)。
- 保存済み（採用・#51 2026-10-21）: `assets/images/fields/reference/teramachi-main-hall-interior-adopted.webp`（TRM-04 本堂の室内、v11。非可逆WebP品質85、実寸1672×940・リサイズなし、363,540 bytes、sha256 `837d3a108990ee5e1bdd931417eca350c4406b28fbe780c46e39066d5ed96042`。PNG原本は残さない）。TRM-05/TRM-02の参照。mask・links・red-team未通過のためruntime未切替。来歴は [採用記録](20261021-trm04-main-hall-adoption.md)。
- 保存済み（採用・#51 2026-10-21）: `assets/images/fields/reference/teramachi-residence-interior-adopted.webp`（TRM-05 住居の室内、中3・火事前の基準。v12。非可逆WebP品質85、実寸1672×941・リサイズなし、316,742 bytes、sha256 `353859f04c2bac75f5b872d68843633b16bc26dc2054e0b5d0b1cb3a828948af`。PNG原本は残さない）。mask・links・red-team未通過のためruntime未切替。来歴は [採用記録](20261021-trm05-residence-adoption.md)。
- `raw/`・`verification/`（検証JSON・VFIELD・prototype/legacy-masks）・BG002〜004・BG006〜009（candidates/ ごと）・DIAG は #68 の追従PRで削除済み。復元は git 履歴から。

寺町16枚の全再作成と全件通過後の一括切替（#51）は継続する。

全712ファイルの旧→新／削除、SHA-256、理由は [移行manifest](20261018-asset-migration.json)。全行の復元元はmanifestの `base_commit` で、`git show <base_commit>:<old>` が元データを返す。元promptは既存の記録以外から復元・創作しない。過去レビューのパスは当時の記録として残す。

| 種別 | 正本配置 | 状態・対応 |
|---|---|---|
| 敵 | `assets/images/enemies/Mxxx.webp` | monsters.mdの既存ID。M001も同じroot。既存の採用／採否待ちを継承し、新品質規約を満たすとは判定しない |
| 召喚獣 | `assets/images/summons/Sxxx.webp` | S002〜S007の6種のみ現存。S001は未生成、S008は同じ存在の設計だが現存画像なし。架空のファイルを作らない |
| 人物 | `assets/images/characters/Cxxx/{masters,poses,walk}/Cxxx-<suffix>.webp` | 下表のC管理ID。旧人名prefixをIDへ置換し、年齢・衣装・pose・方向・コマを全て保持 |
| MAP（旧素材・現存のみ） | `assets/images/fields/legacy/<MAP ID>[-variant].webp`（MAP IDは区域コード3字＋2桁連番。例 `TRM-01`。[対応表](20261019-map-id-renumber.json)） | 33MAP＋12旧差分。非可逆WebP（品質85）。新規生成先ではない。寺町再作成候補の代わりに採用するものではない。PNGは置かない |
| legacy mask | `assets/images/fields/legacy/masks/<MAP ID>-*.webp` | 旧接続を変更しない検証専用。**可逆WebP**（元PNGと画素が完全一致）。JSON・生成補助（make_masks.py）は削除済み |
| 外観参照 | `assets/images/fields/reference/<kebab-case>.webp` | 外観参照専用（平置き・小文字英数とハイフンのみ）。mapの「実行時参照」には使わない |
| 戦闘背景 | `assets/images/battle-backgrounds/BGxxx.webp`（現存はBG001・BG005のみ。BG002〜004・006〜009は削除済みで、復元は git 履歴 `1bb09d0` から。戦闘背景の新規作成は別件） | 下表 |
| ブランド | `assets/images/brand/logo.svg`（正本）、`logo.png`（SVG派生、WebP化しない） | 暫定の文字ロゴ（SIT BY ME）。ゲームIDではない。のち差し替え予定 |

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
