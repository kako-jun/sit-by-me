# 素材ID配置（#68、2026-10-18）

本制作の画像正本は `assets/images/`。配置変更は採用判定ではない。

## 保存運用（#68決定、2026-10-19）

- **サンプル・候補の置き場を作らない**。`candidates/`、版suffix、`verification/` 配下の検証画像置き場は新規に使わない。生成画像は、ゲームで使う正本パス（上表のID別パス）へ**直接上書き保存**する。
- 使うならコミットするだけ、使わないなら git でリバート（`git restore <path>`、未追跡の新規ファイルは削除）。**使う可能性のあるテイクは、次を生成する前にコミットする**（未コミットの新規ファイルは上書きで消える）。`git add` は名指し。
- **採用状態は置き場でなく台帳のstatusで管理する**（[map-asset-registry](../map-asset-registry.md)・各台帳）。正本パスにファイルがあることは、採用も審査通過も意味しない。
- 加工前原本の保管は、実際に必要な工程だけ: 人物の `Cxxx/raw/`（切り出しツールの入力。ツール変更時の出し直し比較に要る）。敵・召喚獣の `raw/` は、縮小・トリム等の加工を行う場合に限る（加工しないなら置かない）。それ以外の原本・失敗版は保管せず、来歴（prompt・測定値・判定）をIssueかレビュー文書に記録する。
- **不採用・失敗画像は残さない**。追跡済みなら `git restore <path>`、未追跡の新規ファイルなら即削除。`candidates/`・`legacy/`・版suffix・サンプル置き場は新運用では作らず、残さない前提とする。
- 参照用に残す画像（`fields/reference/`、外観参照専用。#105で許可済み）は、役割が分かる名前（kebab-case）で保存する。形式は **非可逆WebP（品質85）** を許可する（`magick <元PNG> -quality 85 <名>.webp`。実寸は縮小しない）。他の画像種別のWebP全面移行は別PR。原寸の元画像は参照として残さない。
- 保存済み: `assets/images/fields/reference/teramachi-common-exterior-reference.webp`（非可逆WebP品質85、1672×940、430,536 bytes、sha256 `c596781d351fce35d71b1b31c8db8964e39b2623fde558b44f92cd4723da3175`。元PNG sha256 `7082a759e364a4731d18ba20908034a1f89317c4e6599cd96bee1d6703e77663`）。用途は**順序・包含関係の確認のみ**。池・墓地・鐘楼・井戸・像・遊具・築地塀・通用門などの位置・寸法・扉位置・廊下の形は確定させない。独立画像レビュー合格済み（[#51コメント](https://github.com/kako-jun/sit-by-me/issues/51)参照）。
- 現存する `candidates/`・`legacy/`・`verification/`・`raw/` の画像は、この運用では不要とする方向だが、**このPRでは移動・削除・縮小しない**。棚卸し結果（PR本文）に基づき、kako-junの承認後に別PRで削除／縮小する。検査スクリプトの許可パターンは現存分のみで、削除PRで該当行を外す。

寺町16枚の全再作成と全件通過後の一括切替（#51）は継続する。

全712ファイルの旧→新／削除、SHA-256、理由は [移行manifest](20261018-asset-migration.json)。全行の復元元はmanifestの `base_commit` で、`git show <base_commit>:<old>` が元データを返す。元promptは既存の記録以外から復元・創作しない。過去レビューのパスは当時の記録として残す。

| 種別 | 正本配置 | 状態・対応 |
|---|---|---|
| 敵 | `assets/images/enemies/Mxxx.png`、`raw/Mxxx[-alpha].png` | monsters.mdの既存ID。M001も同じroot。既存の採用／採否待ちを継承し、新品質規約を満たすとは判定しない |
| 召喚獣 | `assets/images/summons/Sxxx.png`、`raw/Sxxx.png` | S002〜S007の6種のみ現存。S001は未生成、S008は同じ存在の設計だが現存画像なし。架空のファイルを作らない |
| 人物 | `assets/images/characters/Cxxx/{masters,poses,walk,raw}/Cxxx-<suffix>.png` | 下表のC管理ID。旧人名prefixをIDへ置換し、年齢・衣装・pose・方向・コマを全て保持 |
| MAP（旧素材・現存のみ） | `assets/images/fields/legacy/Exx[-variant].png` | 33MAP＋12旧差分。新規生成先ではない。寺町再作成候補の代わりに採用するものではない |
| legacy mask | `assets/images/fields/legacy/masks/Exx-*.png` | JSON・生成補助は `verification/fields/legacy-masks/`。旧接続を変更しない検証専用 |
| 汎用フィールド検証（現存のみ） | `assets/images/fields/verification/VFIELDxxx.png`、`masks/VFIELDxxx-*.png` | 新規作成しない。VFIELD001=overview、002=wide-road、003=narrow-lane、004=connector。MAP対応は推測しない |
| 外観参照 | `assets/images/fields/reference/<kebab-case>.{png,webp}` | 外観参照専用（平置き・小文字英数とハイフンのみ）。mapの「実行時参照」には使わない |
| 戦闘背景 | `assets/images/battle-backgrounds/BGxxx.png`（現存の旧候補BG007〜009のみ `candidates/` に残る） | 下表。検証設定は `verification/battles/` |
| 図解 | `assets/images/diagrams/DIAG001.png`、`DIAG002.png` | 旧topology overview／atlas。MAP背景に使わない |
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
| BG002 | bg-b.png | 既存検証素材、採用に昇格しない |
| BG003 | bg-c.png | 既存検証素材、採用に昇格しない |
| BG004 | stage-a.png | 既存検証素材、採用に昇格しない |
| BG005 | stage-b.png | 既存採用舞台。stage-b.json参照を維持 |
| BG006 | stage-c.png | 既存stage-c検証素材 |
| BG007 | teramachi-outdoor-diorama-1920x1080-candidate.png | 画素審査passのみ。完全prompt・参照・live検証未記録でblocked。参照保持 |
| BG008 | stage-e-1920x1080-candidate.png | 画素審査passのみ。完全prompt・参照・live検証未記録でblocked。参照保持 |
| BG009 | stage-f-miniature-1920x1080-candidate.png | 画素審査passのみ。完全prompt・参照・live検証未記録でblocked。参照保持 |

M001の旧640px透過画像は移動で品質再承認しない。今後の再生成は敵スキルの45°・4グリッド契約を使い、既存画像をそのまま新規約passと扱わない。

削除した147ファイルは再作成必須の背景44、対応するrebuild専用mask/config82、pre-sync重複10、失敗または更新中の未審査戦闘候補11。未審査候補の削除理由を画素不合格と捏造しない。削除でワークツリーから約203.3MiBを除去するが、Git履歴には復元可能な原本が残る。

検証は `uv run python3 scripts/verify_asset_layout.py` と `ruby scripts/verify_map_ledger.rb`。画像byte hash、全移動先一意性、ID形式、旧path消失、JSONの実在参照を確認する。実HTTPの設定→画像読込は `uv run python3 -m unittest discover -s tests -v` で確認する。配信rootはリポジトリrootのままで、name-name側へ渡すURLは `/verification/fields/*.field.json` または `/verification/battles/stage-{b,c}.json` に更新する。
