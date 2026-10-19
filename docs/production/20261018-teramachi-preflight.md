# 寺町建物群の制作前入力（2026-10-18）

状態: **BLOCKED / 未生成**。runtimeのready判定ではない。#51の16枚全再作成（1920×1080）に先立ち、最初の対象を **共通外観参照1枚** とする。E11最終背景、室内、maskはまだ生成しない。

根拠: [#51](https://github.com/kako-jun/sit-by-me/issues/51)、[#60](https://github.com/kako-jun/sit-by-me/issues/60)。着手前記録は [#51コメント](https://github.com/kako-jun/sit-by-me/issues/51#issuecomment-6243857457)、[#60コメント](https://github.com/kako-jun/sit-by-me/issues/60#issuecomment-6243857707)。

## Issue #60原文（旧配置の記述を含む。要約ではなく入力へ添付）

```text
ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。

E11 境内（外部）
  └─ door-main → F01 本堂
                    ├─ door-east / 渡り廊下 → E12 住居
                    └─ door-west / 廊下 → F02 幼稚園・遊戯室

- `E12.door-playroom ↔ F02.door-west` の住居↔幼稚園直結を廃止する。
- F01が住居と幼稚園の双方へ向かう屋内の中心・分岐になる。
- E11から住居・幼稚園へ屋外を経由する新規doorは作らない。
```

## 原文行束

以下は記載元の原文行。概要からの再構成をしない。更新時には5ファイルとの逐語一致を再検査する。map-topologyは (1) 接続行（入ってくる接続E04→E11を含む）、(2) 寺町地形不変条件（L565-568）、(3) 屋外・屋内の接続表の行（L575-580）の3ブロックを含む。`SOURCE` で始まる行は出典ラベルであり、原文ではない。それ以外の行が現行ファイルと逐語一致する。

```text
SOURCE docs/map-asset-registry.md
| E01 | `assets/images/fields/legacy/E01.png` | 寺町 | retired-replacement-required |
| E11 | `assets/images/fields/legacy/E11.png` | 寺町 | retired-replacement-required |
| E12 | `assets/images/fields/legacy/E12.png` | 寺町 | retired-replacement-required |
| F01 | `teramachi-main-hall-interior` | 寺町 | ドア接続・時期・室内通路 |
| F02 | `teramachi-kindergarten-hall` | 寺町 | ドア接続・舞台と通路 |
SOURCE docs/map-specifications.md
| E01 kindergarten | 幼稚園前半〜終幕 | 本堂の裏で雪遊びをする私立幼稚園の園庭（屋外） | 段丘上。bottom→E05.top（正門）、door-west→E11.door-kindergarten（境内の右隣の通用門） | F02は同じ幼稚園の屋内。E01↔F02の直結doorは未契約のため描かない |
| E11 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→E04、door-main→F01、door-kindergarten→E01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。E01は境内の右隣。住居／遊戯室への屋外doorなし |
| E12 residence | 全時期 | 庫裏の台所と幼馴染の部屋（屋内） | door-hall→中央F01のdoor-west。F02直結なし | #60/#51。本堂の西（左）。台所は火事イベントの場所 |
| F01 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→E11、door-west→E12.door-hall、door-east→F02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
| F02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→F01.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。E12直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。E01と同じ幼稚園で、園庭直結は未契約 |
SOURCE docs/map-topology.md
| E01.bottom | E05.top | edge | 幼稚園正門から南の主路（E05）へ出る。#51の決定（園庭は境内の右隣・入口のそば）による。旧E01.right→E02.leftは廃止。E02.leftは住居裏の勝手口の細道E10.rightへ続く通路（ループ化で行き止まりなし） |
| E01.door-west | E11.door-kindergarten | door | 境内（E11）の右（東）隣の園庭へ入る通用門。扉の位置・形はTBD |
| E04.top | E11.bottom | edge | 山門から境内へ |
| E11.door-main | F01.door-south | door | 本堂内部 |
| F01.door-west | E12.door-hall | door | 本堂から西（境内から北を見て左）の庫裏（住居）への渡り廊下 |
| F01.door-east | F02.door-west | door | 本堂から東（境内から北を見て右）の幼稚園への屋内廊下。F02側は本堂側（西）から入るので既存IDのwestと整合。扉の位置・廊下長はTBD |
| `E01.door-west` | `E11.door-kindergarten` | 園庭の西側（境内側）通用門。境内の右（東）脇の同じ門へ入る。園庭主路（E01.bottom→E05.top）とは分離する。 |
| `E11.door-main` | `F01.door-south` | 境内から本堂へ。段差を主路にせず、扉前に回転余地を残す。 |
| `F01.door-west` | `E12.door-hall` | 本堂から西（左）の庫裏へ渡る廊下。畳廊下の方位と扉位置を一致させる。扉位置TBD。 |
| `F01.door-east` | `F02.door-west` | 中央の本堂から東（右）の幼稚園へ屋内廊下で移動。F02は本堂側（西面）から入る。扉位置・廊下長TBD。舞台袖は画面内終端。 |
SOURCE docs/map-topology.md 寺町地形不変条件（L565-568）
- **主路との整合（組み替えの要点）**: 主路 E02→E03→E04→E05→E06 は西→東のまま変えない。E11はE04の真上（境内）、E01はその右（東）隣でE05の真上に置く。E01の正門は南の主路（E01.bottom↔E05.top）。旧E01.right↔E02.leftは廃止し、E02.leftは住居裏の細道E10.rightへ続く（E02→E03→E10→E02のループ）。
- **境内（`temple-grounds` / E11）**: 山門（南）から本堂（北）へ石畳。境内から見て左（西）に住居側、右（東）に幼稚園側の建物が続く。屋外から住居・幼稚園へのdoorは作らない（屋内でF01経由）。
- **幼稚園（E01園庭／F02遊戯室）**: 園庭E01は境内E11の右（東）隣で寺の入口のそば。E11↔E01は境内東脇の通用門（door）。F02は本堂F01の東（右）の屋内。E01↔F02の直結は未契約。
- **庫裏（E12）**: 本堂の西（左）。渡り廊下F01.door-west↔E12.door-hall。幼稚園職員室への廊下は#60で廃止（住居↔幼稚園は直結しない）。
SOURCE docs/map-topology.md 6.2 屋外・屋内の接続表の行（L575-580。見出し・区切り行は省く）
| E04.top | E11.bottom | 辺（縦の石畳） | 山門から境内へ |
| E11.door-main | F01.door-south | ドア（本堂の正面） | 境内から本堂 |
| F01.door-west | E12.door-hall | ドア（渡り廊下） | 本堂（中央）から西の住居。内部どうし |
| F01.door-east | F02.door-west | ドア（屋内廊下） | 本堂から東の幼稚園・遊戯室 |
| E11.door-kindergarten | E01.door-west | ドア（通用門） | 境内の東脇から右隣の園庭へ。扉位置TBD |
| E01.bottom | E05.top | 辺 | 園庭の正門から主路E05へ |
SOURCE docs/map-contract-checklist.md
| E01 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E01.png`; mask未記録 | 園庭の既存画像におけるE05(bottom)/E11(door-west)の実端、幼稚園期のtraversalを採寸する。E02との接続は#51で廃止 |
| E11 | recreate-required-1920x1080 | R006,R011,R024 | 旧境内画像は参照専用。新背景・mask未作成 | #60の屋外境内。E04端、E01.door-west通用門（境内の右＝東側）、F01正面扉、池・墓地のblocked域を記録。E12/F02屋外doorなし。共通外観参照未通過 |
| E12 | recreate-required-1920x1080 | R006,R011,R021,R024 | 旧庫裏画像は参照専用。新背景・mask未作成 | #60/#51の西（本堂から見て左）の屋内住居。F01.door-west↔door-hallのみ。内部廊下の扉位置、幅・段差・回転域、火事時遮断範囲がTBD。F02直結なし |
| F01 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。E11南、E12西、F02東の扉位置、畳・仏具と主路、段差・幅・回転域を記録する |
| F02 | recreate-required-1920x1080 | R021,R024 | 旧遊戯室画像は参照専用。新背景・mask未作成 | #60/#51の東（右）の屋内幼稚園。F01.door-east↔F02.door-west（本堂側＝西から入る）の扉位置・廊下長、舞台袖・椅子・主路の分離、段差・幅・回転域を記録する。E12直結なし |
SOURCE docs/teramachi-rebuild-candidates.md
| E01 | `E01-teramachi-kindergarten-rebuild-candidate.png` | bottom→E05.top、door-west→E11 | 屋外園庭（境内の右＝東隣）。通用門は園庭主路と分離 | recreate-required-1920x1080 |
| E11 | `E11-temple-grounds-rebuild-v4-candidate.png` | bottom→E04、door-main→F01、door-kindergarten→E01.door-west | 屋外境内。住居・遊戯室への屋外doorなし | recreate-required-1920x1080 |
| E12 | `E12-temple-residence-rebuild-v3-candidate.png` | door-hall→F01.door-west | 屋内庫裏。本堂の西（左）。F02直結なし | recreate-required-1920x1080 |
| F01 | `F01-temple-main-hall-rebuild-v2-candidate.png` | door-south→E11、door-west→E12.door-hall、door-east→F02.door-west | 中央の屋内本堂。扉前の段差なし・回転余地 | recreate-required-1920x1080 |
| F02 | `F02-kindergarten-playroom-rebuild-candidate.png` | door-west→F01.door-east | 本堂の東（右）の屋内遊戯室。扉位置TBD。舞台袖は画面内終端 | recreate-required-1920x1080 |
```

## 建築不変表

| 原文／正本 | 検査する範囲 |
|---|---|
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| E11 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| E01の正本行「私立幼稚園の園庭（屋外）」／F02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。E01を室内にしない。未契約の園庭直結doorを足さない |
| F01.door-west ↔ E12.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| F01.door-east ↔ F02.door-west | 東の幼稚園まで屋内で連続（F02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| E11から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はF01へ。住居・遊戯室の外部入口を発明しない |

## 参照入力と失敗記録

- 材料の既存見本: `assets/images/fields/legacy/E04.png`。建物配置の正本には使わない。
- #68で失敗したrebuild画像を削除した。生成時の現存参照は `assets/images/fields/legacy/E01.png`、`E11.png`、`E12.png`（同じディレクトリ）を題材・工作材料の補助として入力し、#60と衝突する配置・旧扉・比率を継承しない。F01/F02に現存する旧完成画像はない。削除画像を必須添付にしない。
- 削除済み旧 `teramachi-temple-compound-master-plan-v2-connected.png` は屋根の切断・室内露出、分離した量塊／外部通路に見える失敗例。**外観共通参照として不合格**。名前のconnectedを建築成立の証拠にしない。生成入力の配置正本として使わない。削除対象・SHA-256・元commit・失敗理由は [移行manifest](20261018-asset-migration.json) に記録した。失敗画像自体を恒久保持しない。
- Ref R006/R011/R024: `docs/map-reference-research.md` の地域・土塀・地理資料。特定寺院の平面や室内を保証しない。
- Ref R021: 後のruntimeの幅・回転域換算用。外観参照の建物寸法を決める根拠には使わない。

## 最初の1枚への具体的入力案（実行前ドラフト）

```text
対象: 寺町共通外観参照。E11/E12/F01/F02/E01の同じ建物群を確認する1枚。
納品: 1920×1080 PNG、16:9、非透過。北＝上、鉛直下向き角80°以上85°以下。
添付: 本文のIssue #60原文、5ファイルの原文行束、建築不変表を省略せず添付する。注意: #60原文のdoor-east/west記述は旧配置（door-east→E12住居、door-west→F02幼稚園）。現行（F01.door-west→E12住居、F01.door-east→F02幼稚園）は原文行束を優先する。
西の住居—中央の本堂—東の幼稚園（境内から北を見て左から右）。園庭E01は境内E11の右（東）隣。移動は同一建物内の屋内廊下だけ。
外観は屋根と外壁を保持する。室内、家具、断面、屋根の切欠きを見せない。
別棟、外部渡り廊下、屋外通路、住居と幼稚園の直接接続を追加しない。
E01は幼稚園の屋外園庭、E11は屋外境内。未契約の出入口や道を追加しない。
材料: 土台5 mm foamboardと露出したcorrugated cardboard断面。
壁paper clayを爪楊枝で刻む。屋根corrugated cardboardをカッターで切る。
雪cotton battingを白いPVA接着剤で固定。柱wooden toothpick。
固定masking tapeと白いPVA接着剤。matte poster paintと平筆で着色。
土台断面、段ボール切断面、テープ、PVA接着剤、綿繊維から3種類以上が原寸で判別できること。
人物・読める文字・空・地平線なし。
この参照は外観の順序・包含関係だけを検証する。
廊下の形、建物寸法、扉ピクセル座標、mask幅、runtime linksをこの絵から確定しない。
```

## 外観参照の保存先と検査手順

- 保存先: `.claude/skills/sit-field-background/SKILL.md` 手順4が案内する `assets/images/fields/` 配下の `reference/`（参照専用）を使う。現時点で `assets/images/fields/reference/` は実在しない（`legacy/` のみ）。ディレクトリは生成時に作る。具体的なファイル名は要確認。 `reference/` は外観参照専用で、mapの「実行時参照」には使わない（`scripts/verify_asset_layout.py` は `fields/reference/<kebab-case>.png` のみ許可）。
- 実寸計測: 返却原本を保存後、`identify -format '%wx%h\n' <file>`（または `file <file>`）で1920×1080であることを確認する。不一致ならリサイズで通さず不合格として記録する。
- ハッシュ記録: `sha256sum <file>` を実行し、完全prompt・参照一覧・測定結果とともに記録する。
- legacy参照3枚（`legacy/E01.png`、`E11.png`、`E12.png`）は1536×1024であり、参照入力としては可だが、1920×1080の合格根拠にはならない。

## 残るTBDと生成可否

| 項目 | 共通外観参照 | 最終MAP／mask |
|---|---|---|
| 中央F01・西E12・東F02、屋内限定、直結廃止 | #60で確定。追加の配置決定を求めない | 同じ事実を継承 |
| 屋根形状・外壁外形・園庭／境内との具体配置 | スキルの外観参照スコープ内で順序・包含関係だけを検証する。候補の造形を新たな建築契約と見なさない。runtime配置の採寸は後工程 | 参照通過後に対象行へ必要な配置を契約 |
| F02.door-westの実扉位置、各廊下幅／曲がり／段差・回転域 | 描かず検証対象外。runtime TBDだけを理由に外観参照全体を止めない | TBD。既存IDを勝手に改名しない |
| E01/E11の接続端、屋外主路／池／墓地、E12火事遮断域 | 描画で新規確定しない | TBD。個別MAPの原文・参照・mask契約が必要 |
| 利用する実ツールの1920×1080出力指定・出力検査 | promptに1920×1080を明記して1回だけ直接生成できる。APIにsize引数がなくても不可能とは判定しない。実出力を計測し不一致なら後工程へ進めない。リサイズで通過させない | 同じゲート |
| 原文束・スキルの独立事前レビュー | 未通過。通過後に共通外観参照1枚へ進む | 外観参照通過までBLOCKED |

現時点は準備成果。#68の素材整理と独立事前レビューが通過してから、共通外観参照を1枚だけ生成・実寸検査・独立画像レビューする。決定済みの建築順序を再質問する必要はない。最終16枚は全て再作成待ちであり、旧pass・旧maskでreadyにしない。
