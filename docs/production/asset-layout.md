# 素材ID配置（#68、2026-10-18）

本制作の画像正本は `assets/images/`。配置変更は採用判定ではない。

**置き場所の規則（パターン・種別・用途・許可リスト理由）の正本は台帳 [ファイル配置.yaml](../ledger/ファイル配置.yaml)**（検査は `scripts/verify_asset_layout.py`（画像ID規則）と `scripts/verify_index_reachable.rb`（全ファイルが配置規則に一致・INDEX から到達））。下の表は人向けの解説で、パターンは配置IDで表を引く。全体の入口は [INDEX](../INDEX.md)。

## 保存運用（#68決定、2026-10-19）

- **サンプル・候補の置き場を作らない**。`candidates/`、版suffix、`verification/` 配下の検証画像置き場は作らない。生成画像は、ゲームで使う正本パス（上表のID別パス）へ**直接上書き保存**する。
- 使うならコミットするだけ、使わないなら git でリバート（`git restore <path>`、未追跡の新規ファイルは削除）。**使う可能性のあるテイクは、次を生成する前にコミットする**（未コミットの新規ファイルは上書きで消える）。`git add` は名指し。
- **採用状態は置き場でなく台帳のstatusで管理する**（[map-asset-registry](../map-asset-registry.md)・各台帳）。正本パスにファイルがあることは、採用も審査通過も意味しない。
- **加工前原本（`raw/`）は保管しない**。人物・敵・召喚獣とも、切り出し・縮小・トリム前の元絵は残さず、来歴（prompt・測定値・判定）をIssueかレビュー文書に記録する。過去分の復元は git 履歴から（`git show 1bb09d0:<path>`、記録は `20261018-asset-migration.json` の `pruned_path`）。
- **不採用・失敗画像は残さない**。追跡済みなら `git restore <path>`、未追跡の新規ファイルなら即削除。`candidates/`・`legacy/`・版suffix・サンプル置き場は新運用では作らず、残さない前提とする。
- 参照用に残す画像（`fields/reference/`、外観参照専用。#105で許可済み）は、役割が分かる名前（kebab-case）で保存する。形式は **非可逆WebP（品質85）** を許可する（`magick <元PNG> -quality 85 <名>.webp`。実寸は縮小しない）。人物・敵・召喚獣・戦闘背景も同じ非可逆WebP（品質85、アルファ保持、実寸不変）が正本（#68 PR-W）。MAP（fields/legacy・masks）はMAP改名PR（PR-M）でWebP化するまでPNG、brandはPNGのまま。原寸の元画像は参照として残さない。
- 保存済み: `assets/images/fields/reference/teramachi-common-exterior-reference.webp`（非可逆WebP品質85、1672×940、430,536 bytes、sha256 `c596781d351fce35d71b1b31c8db8964e39b2623fde558b44f92cd4723da3175`。元PNG sha256 `7082a759e364a4731d18ba20908034a1f89317c4e6599cd96bee1d6703e77663`）。用途は**順序・包含関係の確認のみ**。池・墓地・鐘楼・井戸・像・遊具・築地塀・通用門などの位置・寸法・扉位置・廊下の形は確定させない。独立画像レビュー合格済み（[#51コメント](https://github.com/kako-jun/sit-by-me/issues/51)参照）。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-upper-torso-bdy02-adopted.webp`（BDY-02 上半身・胴体上段の基準状態、新版（首1本・左右は本人から見る。2段階生成。旧v3は取り消して差し替え）。非可逆WebP品質85、実寸1672×941・リサイズなし、218,296 bytes、sha256 `21b1bf75cc2742de8c9904f3d588639fb5647bb4fa1544c1fe78008ddd93e06b`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [採用記録](20261022-bdy02-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-left-leg-1-bdy09-adopted.webp`（BDY-09 左足通路1・付け根側の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、270,378 bytes、sha256 `3ff693ab1b735e14f53a401e2c9e8e97543d700feb15386c2e35e5b4160a85b2`、新プール（人体関連）の作り直し版・旧版は削除。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-lower-torso-bdy03-adopted.webp`（BDY-03 下半身・胴体下段・4本合流の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、226,386 bytes、sha256 `22724fc3a41f13e91a9a0bcaacb0f771d3d2ed9b69863d8e722a96f036f520dc`、新プール導入前の装飾計画の版を kako-jun が目視採用。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-mouth-bdy01-adopted.webp`（BDY-01（口）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、267,372 bytes、sha256 `5331efc4c98cb024aa854e0fd8c235179e0adfbf907ad97511e57c1245409441`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-left-arm-1-bdy05-adopted.webp`（BDY-05（左手通路1・付け根側）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、212,068 bytes、sha256 `e735fd28fd1d99b8935db4f0eb392447870b0c39e014e2465f452a5c5404f317`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-left-arm-2-bdy06-adopted.webp`（BDY-06（左手通路2・末端）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、322,122 bytes、sha256 `612a4e1a899b896ced85799afa34f5cb5962394816f59b1ac312cc8390ab5272`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-right-arm-1-bdy07-adopted.webp`（BDY-07（右手通路1・付け根側）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、316,554 bytes、sha256 `41e0c9cd768b4508ec589c1def2d399c1f1d87c8f9f7211796cfb4888f2af7ef`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-right-arm-2-bdy08-adopted.webp`（BDY-08（右手通路2・末端）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、261,072 bytes、sha256 `d69af93e9150e9357019bea407804252d07e76be017fce08c42e4a9435821cd4`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-left-leg-2-bdy10-adopted.webp`（BDY-10（左足通路2・中間）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、249,814 bytes、sha256 `caabd723d724d8b1baa1366dfd04514ad2d131a391f4a12b59a838fe065f66be`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-left-leg-3-bdy11-adopted.webp`（BDY-11（左足通路3・末端）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、340,390 bytes、sha256 `c498110a52afc0d4eb2bdeddd716f9dc879872ffb40e3c832cfafeed77e8f2d9`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-right-leg-1-bdy12-adopted.webp`（BDY-12（右足通路1・付け根側）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、304,990 bytes、sha256 `adc110d58f80dfc131b38568f5e361eeffed62b2e830cd32debb6f4a9ff43ccf`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-right-leg-2-bdy13-adopted.webp`（BDY-13（右足通路2・中間）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×940・リサイズなし、349,056 bytes、sha256 `9293c0284a14edc20b29844a1a304c6003c975d4e2d10b39e83113fd97783d85`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-right-leg-3-bdy14-adopted.webp`（BDY-14（右足通路3・末端）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、269,066 bytes、sha256 `ef44dfb132af74e73192d5eaefbe4959fd5c0c73abbd4aba40c0e88514ab6911`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-brain-maze-bdy04-adopted.webp`（BDY-04（頭・脳の迷路通路）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、245,358 bytes、sha256 `4f441b8cca1106f665c1670decd51008adf8b80e6f5ae485563eff61ae0f3982`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-stomach-bdy15-adopted.webp`（BDY-15（胃・J字の1袋）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、220,986 bytes、sha256 `16ce82a76c721a5638399993d2089ec9ee8bd7a23720c59465c1bea238a1c93a`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-heart-bdy16-adopted.webp`（BDY-16（心臓・4部屋の環）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、301,770 bytes、sha256 `19b4bc72d609719991036633ebaec98cdcb746da37d9093318344eac593ff2ce`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- 保存済み（採用・#142 2026-10-22）: `assets/images/fields/reference/body-lungs-bdy17-adopted.webp`（BDY-17（肺・5部屋の外周の環。案A）の基準状態。様式参照なし・装飾込み1回生成。非可逆WebP品質85、実寸1672×941・リサイズなし、194,058 bytes、sha256 `dc1c67d1c156565ca19ec006d38de13a484a601064aa5cecbbec80e9702633a4`。PNG原本は残さない）。マスク作成済み・第2回red-team済み・blocked維持・runtime未切替。来歴は [体内MAP採用記録](20261022-body-maps-adoption.md)。
- `raw/`・`verification/`（検証JSON・VFIELD・prototype/legacy-masks）・BG002〜004・BG006〜009（candidates/ ごと）・DIAG は #68 の追従PRで削除済み。復元は git 履歴から。

寺町15枚（TRM-02〜TRM-16。旧TRM-01は統合で廃止）の全再作成と全件通過後の一括切替（#51）は継続する。

全712ファイルの旧→新／削除、SHA-256、理由は [移行manifest](20261018-asset-migration.json)。全行の復元元はmanifestの `base_commit` で、`git show <base_commit>:<old>` が元データを返す。元promptは既存の記録以外から復元・創作しない。過去レビューのパスは当時の記録として残す。

| 種別 | 配置ID | 状態・対応 |
|---|---|---|
| 敵 | 配置ID `asset-enemies` | 実在パス例: `assets/images/enemies/Mxxx.webp`。monsters.mdの既存ID。M001も同じroot。既存の採用／採否待ちを継承し、新品質規約を満たすとは判定しない |
| 召喚獣 | 配置ID `asset-summons` | 実在パス例: `assets/images/summons/Sxxx.webp`。S002〜S007の6種のみ現存。S001は未生成、S008は同じ存在の設計だが現存画像なし。架空のファイルを作らない |
| 人物 | 配置ID `asset-characters` | 実在パス例: `assets/images/characters/Cxxx/{masters,poses,walk}/Cxxx-<suffix>.webp`。下表のC管理ID。旧人名prefixをIDへ置換し、年齢・衣装・pose・方向・コマを全て保持。幼稚園期の歩きは上下左右と斜め4方向を各3コマで保存（例: `C001-walk-downleft-1.webp`） |
| MAP（旧素材・現存のみ） | 配置ID `asset-field-legacy` | 実在パス例: `assets/images/fields/legacy/<MAP ID>[-variant].webp`（MAP IDは区域コード3字＋2桁連番。例 `TRM-03`。[対応表](20261019-map-id-renumber.json)）。33MAP＋12旧差分。非可逆WebP（品質85）。新規生成先ではない。寺町再作成候補の代わりに採用するものではない。PNGは置かない |
| legacy mask | 配置ID `asset-field-legacy-masks` | 実在パス例: `assets/images/fields/legacy/masks/<MAP ID>-*.webp`。旧接続を変更しない検証専用。**可逆WebP**（元PNGと画素が完全一致）。JSON・生成補助（make_masks.py）は削除済み |
| 外観参照 | 配置ID `asset-field-reference` | 実在パス例: `assets/images/fields/reference/<kebab-case>.webp`。外観参照専用（平置き・小文字英数とハイフンのみ）。mapの「実行時参照」には使わない |
| 体内マスク（runtime切替前） | 配置ID `asset-field-masks` | 実在パス例: `assets/images/fields/masks/BDY-NN-{mask,traversal-edit,mask-overlay}.webp`（17箇所×3=51ファイル）。`mask`・`traversal-edit` は**可逆WebP（VP8L）**、`mask-overlay` は確認用の**非可逆WebP**。体内17MAPのマスク（#142）。台帳は blocked 維持で runtime 未切替 |
| 斜め視点マスク（runtime切替前） | 配置ID `asset-field-masks` | 実在パス例: `assets/images/fields/masks/TRM-02-{mask,traversal-edit,mask-overlay}.webp`。寺町の斜め視点（#144）。形式は体内マスクと同じ（mask・edit は可逆WebP、overlay は非可逆）。入力JSON・結果は `docs/production/oblique-masks/`。台帳は blocked 維持（ready にしない） |
| 戦闘背景 | 配置ID `asset-battle-backgrounds` | 実在パス例: `assets/images/battle-backgrounds/BGxxx.webp`（現存はBG001・BG005のみ。BG002〜004・006〜009は削除済みで、復元は git 履歴 `1bb09d0` から。戦闘背景の新規作成は別件）。下表 |
| フィールド感情吹き出し | 配置ID `asset-field-emotion` | 実在パス例: `assets/images/effects/field-emotion/field-emotion-{exclaim,question,dots}.png`。256x256 透過PNG（#170、[registry](../field-emotion-registry.md)）。配置は暫定（#139 と整合時に再検討） |
| 人物共通の採用素材 | 配置ID `asset-shared-adopted` | 実在パス例: `assets/images/characters/shared/anonymous-elder-woman.webp`。透過切り抜き WebP。`-v数字` で終わる名は不可（候補は `shared/candidates/`） |
| ブランド | 配置ID `asset-brand` | 実在パス例: `assets/images/brand/logo.svg`（正本）、`logo.png`（SVG派生、WebP化しない）。暫定の文字ロゴ（SIT BY ME）。ゲームIDではない。のち差し替え予定 |

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
